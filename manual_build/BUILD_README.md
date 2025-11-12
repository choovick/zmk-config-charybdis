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

Simply run the build script:

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

5. settings_reset (nice_nano_v2)

6. settings_reset (seeeduino_xiao_ble)

Select build configuration (1-6) or 'q' to quit:
```

## Output Location

Built firmware files will be in:
- `manual_build/artifacts/charybdis-left/zephyr/zmk.uf2`
- `manual_build/artifacts/charybdis-right-standalone/zephyr/zmk.uf2`
- `manual_build/artifacts/charybdis-right-dongle/zephyr/zmk.uf2`
- `manual_build/artifacts/prospector-dongle-prospector-adapter/zephyr/zmk.uf2`
- `manual_build/artifacts/settings-reset/zephyr/zmk.uf2`

Additionally, firmware is automatically copied to:
- `manual_build/artifacts/output/*.uf2` with clean names

All build artifacts (including downloaded ZMK source, Zephyr, modules, etc.) are contained within the `manual_build/` directory to keep your repository clean.

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

