#!/usr/bin/env python3
"""
ZMK Local Build Script using Docker
Reads build.yaml and builds selected configuration using Docker
"""

import yaml
import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path


def load_build_config(workspace_path):
    """Load and parse the build.yaml configuration file."""
    config_file = workspace_path / "build.yaml"
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('include', [])
    except FileNotFoundError:
        print(f"Error: {config_file} not found!")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing {config_file}: {e}")
        sys.exit(1)


def display_build_options(builds):
    """Display available build configurations."""
    print("\n=== Available Build Configurations ===\n")
    for idx, build in enumerate(builds, 1):
        board = build.get('board', 'N/A')
        shield = build.get('shield', 'N/A')
        snippet = build.get('snippet', '')
        cmake_args = build.get('cmake-args', '')

        print(f"{idx}. {shield} ({board})")
        if snippet:
            print(f"   └─ Snippet: {snippet}")
        if cmake_args:
            print(f"   └─ CMake args: {cmake_args}")
        print()


def get_user_choice(max_choice):
    """Get user's build selection."""
    while True:
        try:
            choice = input(f"Select build configuration (1-{max_choice}) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                print("Exiting...")
                sys.exit(0)
            choice_num = int(choice)
            if 1 <= choice_num <= max_choice:
                return choice_num - 1  # Convert to 0-indexed
            else:
                print(f"Please enter a number between 1 and {max_choice}")
        except ValueError:
            print("Invalid input. Please enter a number.")


def clean_west_workspace(west_workspace_path: Path):
    """Delete the local west workspace contents so dependencies will be re-fetched."""
    if not west_workspace_path.exists():
        return

    # Remove entirely to ensure hidden files like .west/ are cleared.
    shutil.rmtree(west_workspace_path, ignore_errors=True)
    west_workspace_path.mkdir(parents=True, exist_ok=True)


def clean_artifacts(artifacts_path: Path):
    """Delete local build artifacts under manual_build/artifacts/."""
    if not artifacts_path.exists():
        return
    shutil.rmtree(artifacts_path, ignore_errors=True)
    artifacts_path.mkdir(parents=True, exist_ok=True)


def build_docker_command(build_config, workspace_path):
    """Construct the Docker build command."""
    board = build_config.get('board')
    shield = build_config.get('shield')
    snippet = build_config.get('snippet')
    cmake_args = build_config.get('cmake-args')

    # Sanitize shield name for build directory (replace spaces and underscores with hyphens)
    shield_dir = shield.replace(' ', '-').replace('_', '-')
    build_dir = f"manual_build/artifacts/{shield_dir}"

    # Keep west-managed checkouts out of the repo root by using a dedicated west workspace directory
    # under manual_build/ (gitignored). We mount:
    # - /repo      -> the git repo (source-of-truth for config + custom shields module)
    # - /workspace -> the west workspace (contains zephyr/zmk/modules checkouts)
    # - /out       -> build output/artifacts directory
    west_workspace_host = workspace_path / "manual_build" / "west-workspace"
    artifacts_host = workspace_path / "manual_build" / "artifacts"

    build_dir_in_container = f"/out/{shield_dir}"

    # Base Docker command
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{workspace_path}:/repo",
        "-v", f"{west_workspace_host}:/workspace",
        "-v", f"{artifacts_host}:/out",
        "-w", "/workspace",
        "zmkfirmware/zmk-build-arm:stable",
        "sh", "-c"
    ]

    # Build the west commands
    west_commands = []
    west_commands.append('mkdir -p /workspace /out')
    # Be explicit about where we operate; west init/update/build must run from the workspace root.
    west_commands.append('cd /workspace')
    # Copy config into the workspace so west init -l can initialize *here*.
    # (If the local manifest repo is outside the workspace, west may initialize in the manifest dir.)
    west_commands.append('rm -rf /workspace/config && cp -R /repo/config /workspace/config')

    # Copy this repo's custom shields as a proper module inside the workspace (avoid name collision
    # with the zephyr checkout at /workspace/zephyr).
    west_commands.append('rm -rf /workspace/zmk-config-charybdis && mkdir -p /workspace/zmk-config-charybdis/zephyr')
    west_commands.append('if [ -d /repo/boards ]; then cp -R /repo/boards /workspace/zmk-config-charybdis/; fi')
    west_commands.append('if [ -d /repo/dts ]; then cp -R /repo/dts /workspace/zmk-config-charybdis/; fi')
    west_commands.append('if [ -f /repo/zephyr/module.yml ]; then cp /repo/zephyr/module.yml /workspace/zmk-config-charybdis/zephyr/module.yml; fi')

    # Init the west workspace at /workspace, using the copied local manifest repo at /workspace/config.
    west_commands.append('[ -d .west ] || west init -l /workspace/config')
    # Fetch dependencies only when missing (first run or after --clean).
    west_commands.append('cd /workspace')
    west_commands.append('if [ ! -d zmk ]; then west update; fi')
    west_commands.append('west zephyr-export')

    # Construct west build command (quote build_dir in case shield name has spaces)
    # Use --pristine to automatically clean build directory (prevents board mismatch errors)
    build_cmd_parts = [
        f'west build -s zmk/app -d "{build_dir_in_container}" -b {board} --pristine'
    ]

    # Add snippet if present (BEFORE the -- separator, as a west flag)
    if snippet:
        build_cmd_parts.append(f'-S "{snippet}"')

    # Add the CMake separator
    build_cmd_parts.append("--")

    # Add config directory so ZMK can find custom shields
    build_cmd_parts.append(f"-DZMK_CONFIG=/workspace/config")

    # If this repo has been refactored to the new module-based layout (no config/boards),
    # expose the repo root as an extra Zephyr module so boards/shields are discovered.
    # (Inside the container, the repo is mounted at /repo)
    if (workspace_path / "zephyr" / "module.yml").exists():
        build_cmd_parts.append(f"-DZMK_EXTRA_MODULES=/workspace/zmk-config-charybdis")

    # Add shield (quoted to handle shields with spaces like "prospector_dongle prospector_adapter")
    build_cmd_parts.append(f'-DSHIELD="{shield}"')

    # Add cmake args if present
    if cmake_args:
        build_cmd_parts.append(cmake_args)

    west_commands.append(" ".join(build_cmd_parts))

    # Combine all commands
    full_command = " && ".join(west_commands)
    docker_cmd.append(full_command)

    return docker_cmd, build_dir


def run_build(docker_cmd, shield_name):
    """Execute the Docker build command."""
    print(f"\n{'='*60}")
    print(f"Building: {shield_name}")
    print(f"{'='*60}\n")
    print(f"Running: {' '.join(docker_cmd[:7])}...")
    print(f"\nFull command string:\n{docker_cmd[-1]}\n")
    print()

    try:
        result = subprocess.run(docker_cmd, check=True)
        print(f"\n{'='*60}")
        print(f"✓ Build completed successfully!")
        print(f"{'='*60}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{'='*60}")
        print(f"✗ Build failed with error code {e.returncode}")
        print(f"{'='*60}\n")
        return False
    except KeyboardInterrupt:
        print("\n\nBuild interrupted by user.")
        sys.exit(1)


def copy_firmware_to_output(workspace_path, build_dir, shield_name, board_name):
    """Copy the built firmware to the output directory with a clean name."""
    # Create output directory if it doesn't exist
    output_dir = workspace_path / "manual_build" / "artifacts" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Source file
    source_file = workspace_path / build_dir / "zephyr" / "zmk.uf2"

    # Generate output filename: shield-board.uf2
    # Replace underscores with hyphens for consistency
    shield_clean = shield_name.replace('_', '-')
    board_clean = board_name.replace('_', '-')
    output_filename = f"{shield_clean}-{board_clean}.uf2"
    output_file = output_dir / output_filename

    # Copy the file
    try:
        if source_file.exists():
            shutil.copy2(source_file, output_file)
            print(f"✓ Firmware copied to: manual_build/artifacts/output/{output_filename}")
            return output_file
        else:
            print(f"Warning: Source file not found: {source_file}")
            return None
    except Exception as e:
        print(f"Error copying firmware: {e}")
        return None


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='ZMK Local Build Script using Docker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  ./build.py
  
  # Build by index number
  ./build.py -n 1
  
  # Build by shield name (partial match)
  ./build.py -s "nice_dongle"
  
  # Build by board and shield
  ./build.py -b nice_nano_v2 -s "nice_dongle dongle_display"
  
  # List available configurations
  ./build.py -l
        """
    )
    
    parser.add_argument('-n', '--number', type=int, metavar='N',
                        help='Build configuration number (1-based index)')
    parser.add_argument('-s', '--shield', type=str, metavar='SHIELD',
                        help='Shield name (or partial match)')
    parser.add_argument('-b', '--board', type=str, metavar='BOARD',
                        help='Board name (used with --shield for exact match)')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List available build configurations and exit')
    parser.add_argument('--clean', '--clean-deps', dest='clean_deps', action='store_true',
                        help='Delete the local west workspace (manual_build/west-workspace/) and re-download dependencies on the next build')
    
    return parser.parse_args()


def find_build_by_criteria(builds, shield=None, board=None):
    """Find a build configuration by shield and/or board name."""
    matches = []
    
    for idx, build in enumerate(builds):
        build_shield = build.get('shield', '')
        build_board = build.get('board', '')
        
        # Check if shield matches (partial or exact)
        shield_match = not shield or shield.lower() in build_shield.lower()
        
        # Check if board matches (exact)
        board_match = not board or board.lower() == build_board.lower()
        
        if shield_match and board_match:
            matches.append((idx, build))
    
    return matches


def main():
    """Main entry point."""
    # Get the absolute path of the workspace (parent of manual_build)
    workspace_path = Path(__file__).parent.parent.resolve()

    # Parse command-line arguments
    args = parse_arguments()

    print("╔════════════════════════════════════════════╗")
    print("║   ZMK Local Build Script (Docker)          ║")
    print("╚════════════════════════════════════════════╝")

    # Load build configurations
    builds = load_build_config(workspace_path)

    if not builds:
        print("Error: No build configurations found in build.yaml")
        sys.exit(1)

    # Handle list mode
    if args.list:
        display_build_options(builds)
        sys.exit(0)

    # Determine which build to use
    selected_build = None
    
    if args.number:
        # Build by number
        if 1 <= args.number <= len(builds):
            selected_build = builds[args.number - 1]
            print(f"\nSelected build #{args.number}")
        else:
            print(f"Error: Build number must be between 1 and {len(builds)}")
            sys.exit(1)
    
    elif args.shield or args.board:
        # Build by shield/board criteria
        matches = find_build_by_criteria(builds, args.shield, args.board)
        
        if not matches:
            print(f"Error: No build configuration found matching criteria:")
            if args.shield:
                print(f"  Shield: {args.shield}")
            if args.board:
                print(f"  Board: {args.board}")
            print("\nAvailable configurations:")
            display_build_options(builds)
            sys.exit(1)
        
        elif len(matches) == 1:
            idx, selected_build = matches[0]
            print(f"\nFound matching build #{idx + 1}:")
            print(f"  {selected_build.get('shield')} ({selected_build.get('board')})")
        
        else:
            print(f"\nMultiple builds match your criteria:")
            for idx, build in matches:
                print(f"  {idx + 1}. {build.get('shield')} ({build.get('board')})")
            print("\nPlease specify more precise criteria or use -n with the build number")
            sys.exit(1)
    
    else:
        # Interactive mode
        display_build_options(builds)
        choice = get_user_choice(len(builds))
        selected_build = builds[choice]

    # Ensure the west workspace dir exists on the host (bind-mounted into the container)
    west_workspace_path = workspace_path / "manual_build" / "west-workspace"
    west_workspace_path.mkdir(parents=True, exist_ok=True)

    artifacts_path = workspace_path / "manual_build" / "artifacts"
    artifacts_path.mkdir(parents=True, exist_ok=True)

    # Optional dependency cleanup happens on the host BEFORE running Docker.
    if args.clean_deps:
        print("\nCleaning dependency workspace: manual_build/west-workspace/", flush=True)
        clean_west_workspace(west_workspace_path)
        print("Dependency workspace cleaned.", flush=True)

        print("Cleaning build artifacts: manual_build/artifacts/", flush=True)
        clean_artifacts(artifacts_path)
        print("Build artifacts cleaned.\n", flush=True)

    # Build Docker command
    docker_cmd, build_dir = build_docker_command(selected_build, workspace_path)

    # Run the build
    shield_name = selected_build.get('shield')
    board_name = selected_build.get('board')
    success = run_build(docker_cmd, shield_name)

    if success:
        original_output = workspace_path / build_dir / "zephyr" / "zmk.uf2"
        print(f"\nOriginal output: {original_output}")

        # Copy to organized output directory
        output_file = copy_firmware_to_output(workspace_path, build_dir, shield_name, board_name)

        if output_file:
            print(f"\nTo flash: Copy the firmware to your board's USB drive")
            print(f"  File: {output_file.relative_to(workspace_path)}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

