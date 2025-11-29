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
./build.py -s "nice_dongle"

# Build by board and shield (exact match)
./build.py -b nice_nano_v2 -s "nice_dongle dongle_display"

# List available configurations
./build.py -l

# Show help
./build.py -h
```

## Example Output

```
╔════════════════════════════════════════════╗
║   ZMK Local Build Script (Docker)          ║
╚════════════════════════════════════════════╝

=== Available Build Configurations ===

1. charybdis_left (nice_nano_v2)

2. charybdis_right_standalone (nice_nano_v2)
   └─ Snippet: studio-rpc-usb-uart
   └─ CMake args: -DCONFIG_ZMK_STUDIO=y

3. charybdis_right_dongle (nice_nano_v2)

4. prospector_dongle prospector_adapter (seeeduino_xiao_ble)
   └─ Snippet: studio-rpc-usb-uart
   └─ CMake args: -DCONFIG_ZMK_STUDIO=y

5. nice_dongle dongle_display (nice_nano_v2)
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
- `manual_build/artifacts/charybdis-right-dongle/zephyr/zmk.uf2`
- `manual_build/artifacts/prospector-dongle-prospector-adapter/zephyr/zmk.uf2`
- `manual_build/artifacts/nice-dongle-dongle-display/zephyr/zmk.uf2`
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

To customize the display, edit `config/boards/shields/charybdis/nice_dongle.conf`:
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
Check that your `build.yaml` is properly formatted and all shield definitions exist in the `config/boards/shields/` directory.

