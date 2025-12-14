# Local Build Instructions

This repository includes a Python script to build ZMK firmware locally using Docker.

## Prerequisites

1. **Docker** - Install Docker Desktop for macOS

   ```bash
   brew install --cask docker
   ```

2. **Python 3** and **PyYAML**

   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

### Interactive Mode

Simply run the build script without arguments:

```bash
./build.py
# or
python3 build.py
```

The script will:

1. Read the `build.yaml` configuration
2. Display available build options
3. Ask you to select which configuration to build
4. Run Docker to build the firmware
5. Output the `.uf2` file location

### Command-Line Mode

For faster builds, you can specify the configuration directly:

```bash
# Build by number (from the list)
./build.py -n 1

# Build by shield name (partial match)
./build.py -s "dongle_nice"

# Build by board and shield (exact match)
./build.py -b nice_nano_v2 -s "dongle_nice dongle_display"

# List available configurations
./build.py -l

# Show help
./build.py -h
```

### Dependency caching (avoid re-downloading)

The script keeps a persistent west workspace in:

- `manual_build/west-workspace/`

This directory is gitignored and contains the checked out dependencies (`zephyr/`, `zmk/`, `modules/`, etc.),
so subsequent builds do **not** re-download everything.

Useful flags:

- `--clean` (alias: `--clean-deps`): deletes **both**:
  - `manual_build/west-workspace/` (dependencies; forces a fresh `west update`)
  - `manual_build/artifacts/` (build outputs)

### How it works (repo stays clean)

This script keeps your git repo clean by using a **separate west workspace** under:

- `manual_build/west-workspace/`

Inside the Docker container it mounts:

- `/repo`: your git repository (read-only source-of-truth for `config/`, `boards/`, `dts/`, and `zephyr/module.yml`)
- `/workspace`: the west workspace (contains `.west/`, `zephyr/`, `zmk/`, `modules/`, etc.)
- `/out`: build outputs (written to `manual_build/artifacts/`)

Each build, it copies:

- `/repo/config` → `/workspace/config` (so `west init -l` initializes in the workspace)
- `/repo/boards`, `/repo/dts`, `/repo/zephyr/module.yml` → `/workspace/zmk-config-charybdis/` (as a proper Zephyr module)

Then it runs:

- `west init -l /workspace/config` (only if needed)
- `west update` (only if dependencies are missing, e.g. first build or after `--clean`)
- `west build ... -DZMK_CONFIG=/workspace/config -DZMK_EXTRA_MODULES=/workspace/zmk-config-charybdis`

## Example Output

```text
╔════════════════════════════════════════════╗
║   ZMK Local Build Script (Docker)          ║
╚════════════════════════════════════════════╝

=== Available Build Configurations ===

1. charybdis_left (nice_nano_v2)

2. charybdis_right_standalone (nice_nano_v2)
   └─ Snippet: studio-rpc-usb-uart
   └─ CMake args: -DCONFIG_ZMK_STUDIO=y

3. dongle_charybdis_right (nice_nano_v2)

4. dongle_prospector prospector_adapter (seeeduino_xiao_ble)
   └─ Snippet: studio-rpc-usb-uart
   └─ CMake args: -DCONFIG_ZMK_STUDIO=y

5. dongle_nice dongle_display (nice_nano_v2)
   └─ Snippet: studio-rpc-usb-uart
   └─ CMake args: -DCONFIG_ZMK_STUDIO=y

6. settings_reset (nice_nano_v2)

7. settings_reset (seeeduino_xiao_ble)

Select build configuration (1-6) or 'q' to quit:
```

## Output Location

Built firmware files will be in:

- `manual_build/artifacts/charybdis-left/zephyr/zmk.uf2`
- `manual_build/artifacts/charybdis-right-standalone/zephyr/zmk.uf2`
- `manual_build/artifacts/dongle-charybdis-right/zephyr/zmk.uf2`
- `manual_build/artifacts/dongle-prospector-prospector-adapter/zephyr/zmk.uf2`
- `manual_build/artifacts/dongle-nice-dongle-display/zephyr/zmk.uf2`
- `manual_build/artifacts/settings-reset/zephyr/zmk.uf2`

Additionally, firmware is automatically copied to:

- `manual_build/artifacts/output/*.uf2` with clean names

All build artifacts (including downloaded ZMK source, Zephyr, modules, etc.) are contained within the `manual_build/` directory to keep your repository clean.

## Nice!Nano Dongle with OLED Display

The build configuration now includes a nice!nano-based dongle with a 128x32 OLED display. This uses the `zmk-dongle-display` module to provide:

- Active HID indicators (CLCK, NLCK, SLCK)
- Highest layer name
- Output status
- Peripheral battery levels
- Optional: Dongle battery level
- Optional: WPM meter

The 128x32 OLED configuration automatically disables the bongo cat and modifier widgets to fit the smaller display. The display uses I2C connected to the nice!nano's pro_micro_i2c bus.

To customize the display, edit the shield config under `boards/shields/charybdis/` (e.g. `dongle_nice_64.conf`):

- Enable WPM: `CONFIG_ZMK_DONGLE_DISPLAY_WPM=y`
- Change layer alignment: `CONFIG_ZMK_DONGLE_DISPLAY_LAYER_TEXT_ALIGN="left"` (or "center", "right")
- Use macOS modifiers: `CONFIG_ZMK_DONGLE_DISPLAY_MAC_MODIFIERS=y`

## Flashing

1. Connect your board via USB
2. Put it in bootloader mode (double-tap reset button)
3. Copy the appropriate `.uf2` file to the USB drive that appears
4. The board will automatically reboot with the new firmware

## Troubleshooting

### Docker permission issues

If you get permission errors, make sure Docker Desktop is running.

### PyYAML not found

Install dependencies:

```bash
pip3 install -r requirements.txt
```

### Build failures

Check that your `build.yaml` is properly formatted and that your shields exist under `boards/shields/` (module-based layout).
