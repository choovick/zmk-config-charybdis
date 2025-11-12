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


def build_docker_command(build_config, workspace_path):
    """Construct the Docker build command."""
    board = build_config.get('board')
    shield = build_config.get('shield')
    snippet = build_config.get('snippet')
    cmake_args = build_config.get('cmake-args')

    # Sanitize shield name for build directory (replace spaces and underscores with hyphens)
    shield_dir = shield.replace(' ', '-').replace('_', '-')
    build_dir = f"manual_build/artifacts/{shield_dir}"

    # Base Docker command - mount repo root and work from /workspace
    # (west.yml requires workspace root to be parent of config/)
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{workspace_path}:/workspace",
        "-w", "/workspace",
        "zmkfirmware/zmk-build-arm:stable",
        "sh", "-c"
    ]

    # Build the west commands
    west_commands = []
    west_commands.append("[ -d .west ] || west init -l config/")
    west_commands.append("west update")
    west_commands.append("west zephyr-export")

    # Construct west build command (quote build_dir in case shield name has spaces)
    build_cmd_parts = [
        f'west build -s zmk/app -d "{build_dir}" -b {board}'
    ]

    # Add snippet if present (BEFORE the -- separator, as a west flag)
    if snippet:
        build_cmd_parts.append(f'-S "{snippet}"')

    # Add the CMake separator
    build_cmd_parts.append("--")

    # Add config directory so ZMK can find custom shields
    build_cmd_parts.append(f"-DZMK_CONFIG=/workspace/config")

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


def main():
    """Main entry point."""
    # Get the absolute path of the workspace (parent of manual_build)
    workspace_path = Path(__file__).parent.parent.resolve()

    print("╔════════════════════════════════════════════╗")
    print("║   ZMK Local Build Script (Docker)          ║")
    print("╚════════════════════════════════════════════╝")

    # Load build configurations
    builds = load_build_config(workspace_path)

    if not builds:
        print("Error: No build configurations found in build.yaml")
        sys.exit(1)

    # Display options
    display_build_options(builds)

    # Get user choice
    choice = get_user_choice(len(builds))
    selected_build = builds[choice]

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

