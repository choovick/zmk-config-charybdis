# ZMK CONFIG FOR THE CHARYBDIS 4X6 WIRELESS SPLIT KEYBOARD

This configuration supports two modes:
- **Standalone Mode**: Right keyboard acts as central, connects directly to host
- **Dongle Mode**: Dedicated dongle with display acts as central, both keyboards connect to it

## Table of Contents

- [ZMK CONFIG FOR THE CHARYBDIS 4X6 WIRELESS SPLIT KEYBOARD](#zmk-config-for-the-charybdis-4x6-wireless-split-keyboard)
  - [Table of Contents](#table-of-contents)
  - [BOM](#bom)
    - [Additional Components for Dongle Mode](#additional-components-for-dongle-mode)
  - [Tester Pro Micro Shield](#tester-pro-micro-shield)
  - [Repository Structure](#repository-structure)
    - [Key Files Explained](#key-files-explained)
      - [Shared Configuration Files (Consolidated)](#shared-configuration-files-consolidated)
      - [Shield-Specific Files](#shield-specific-files)
  - [Operating Modes](#operating-modes)
    - [Standalone Mode](#standalone-mode)
    - [Dongle Mode](#dongle-mode)
    - [Dongle Display Features (Prospector Module)](#dongle-display-features-prospector-module)
  - [West.yml Configuration](#westyml-configuration)
    - [Remotes Section](#remotes-section)
    - [Projects Section](#projects-section)
    - [Self Section](#self-section)
  - [Keymap](#keymap)
  - [Trackball Sensitivity Configuration](#trackball-sensitivity-configuration)
    - [Hardware Sensor Sensitivity (CPI/DPI)](#hardware-sensor-sensitivity-cpidpi)
    - [Software Scaling (Movement Speed)](#software-scaling-movement-speed)
    - [How Scaler Values Work](#how-scaler-values-work)
    - [Reference Documentation](#reference-documentation)
  - [ZMK Studio Support](#zmk-studio-support)
    - [Physical Layout Definition](#physical-layout-definition)
    - [Enabling/Disabling ZMK Studio](#enablingdisabling-zmk-studio)
    - [Studio Unlock](#studio-unlock)
  - [Building Firmware](#building-firmware)
    - [GitHub Actions (Automatic)](#github-actions-automatic)
    - [Local Build (Manual)](#local-build-manual)
  - [Flashing Firmware](#flashing-firmware)
    - [How to Flash](#how-to-flash)
    - [Standalone Mode](#standalone-mode-1)
    - [Dongle Mode](#dongle-mode-1)
    - [Tester Pro Micro (GPIO Testing)](#tester-pro-micro-gpio-testing)

## BOM

Here is the BOM for this project: [BOM Charybdis 4x6 Wireless](/docs/bom/readme.md)

### Additional Components for Dongle Mode
- 1x Seeeduino XIAO BLE (nRF52840) - Dongle central
- 1x [Prospector Display Module](https://github.com/carrefinho/prospector) - OLED display for dongle

![Wireless Keyboard](/docs/picture/wireless-charybdis.png)

## Tester Pro Micro Shield

This repository includes a **ZMK Tester Shield** (`tester_pro_micro`) for troubleshooting and testing Pro Micro-compatible boards (Nice!Nano, Seeeduino XIAO, etc.). The tester shield maps all 18 available GPIO pins (D0-D10, D14-D16, D18-D21) to virtual "keys" that output "PIN X" when triggered, helping you verify all GPIO pins are working correctly before assembling your keyboard.

**How to use:**
1. Flash `tester_pro_micro-nice_nano_v2-zmk.uf2` to your controller (see [Building Firmware](#building-firmware))
2. Connect the board via USB to your computer
3. Open a text editor
4. Connect a switch or wire from any GPIO pin to GND and trigger it
5. The board will output "PIN X" where X is the pin number (e.g., "PIN 14")

The tester runs in USB-only mode (no BLE) and includes two physical layouts for ZMK Studio visualization.

## Repository Structure

```
zmk-config-charybdis/
├── config/                          # Main ZMK configuration directory
│   ├── boards/                      # Shield board definitions
│   │   └── shields/
│   │       ├── charybdis/           # Charybdis shield configuration
│   │       │   ├── charybdis.dtsi                        # Common device tree (keyboard layout, kscan)
│   │       │   ├── charybdis_layers.h                    # Shared layer definitions
│   │       │   ├── charybdis_trackball_processors.dtsi   # Shared trackball processing config
│   │       │   ├── charybdis_right_common.dtsi           # Shared right keyboard hardware config
│   │       │   ├── charybdis_left.conf                   # Left side Kconfig options (empty)
│   │       │   ├── charybdis_left.overlay                # Left side device tree overlay
│   │       │   ├── charybdis_right_standalone.conf       # Right side Kconfig (standalone mode)
│   │       │   ├── charybdis_right_standalone.overlay    # Right side overlay (standalone mode)
│   │       │   ├── charybdis_right_dongle.conf           # Symlink → charybdis_right_standalone.conf
│   │       │   ├── charybdis_right_dongle.overlay        # Right side overlay (dongle mode)
│   │       │   ├── prospector_dongle.conf                # Prospector dongle Kconfig options
│   │       │   ├── prospector_dongle.overlay             # Prospector dongle device tree overlay
│   │       │   ├── Kconfig.defconfig                     # Shield Kconfig definitions
│   │       │   └── Kconfig.shield                        # Shield Kconfig options
│   │       └── tester_pro_micro/    # Pro Micro GPIO tester shield
│   │           ├── Kconfig.shield                        # Shield identifier
│   │           ├── Kconfig.defconfig                     # Shield defaults (USB-only, no BLE)
│   │           ├── tester_pro_micro.zmk.yml              # Shield metadata
│   │           ├── tester_pro_micro.overlay              # GPIO pin definitions (18 pins)
│   │           ├── tester_pro_micro.keymap               # Pin test macros
│   │           └── tester_pro_micro-layouts.dtsi         # Physical layouts (pinout + single row)
│   ├── charybdis.conf               # Global ZMK configuration
│   ├── charybdis.keymap             # Keymap definition file
│   ├── charybdis.zmk.yml            # ZMK build configuration
│   ├── info.json                    # Repository metadata
│   └── west.yml                     # West manifest (see West.yml section below)
├── manual_build/                    # Local build scripts
│   ├── build.py                     # Interactive build script
│   └── BUILD_README.md              # Build instructions
├── docs/                            # Documentation
│   ├── bom/                         # Bill of Materials
│   │   └── readme.md
│   ├── keymap/                      # Keymap documentation
│   │   ├── config.yaml              # Keymap drawer configuration
│   │   ├── keymap.yaml              # Base keymap definition
│   │   ├── keymap.svg               # Generated: Visual keymap (created by render.sh)
│   │   └── render.sh                # Script to parse keymap and generate SVG
│   └── picture/                     # Images
│       └── wireless-charybdis.png
├── build.yaml                       # GitHub Actions build configuration
└── readme.md                        # This file
```

### Key Files Explained

#### Shared Configuration Files (Consolidated)
- **`charybdis_layers.h`**: Layer definitions (BASE, POINTER, LOWER, RAISE, SYMBOLS, SCROLL, SNIPING) used across all shields
- **`charybdis_trackball_processors.dtsi`**: Shared trackball input processing configurations (snipe/scroll/move modes)
- **`charybdis_right_common.dtsi`**: Common hardware config for both right keyboard variants (GPIO, SPI, trackball device)
- **`charybdis_right_dongle.conf`**: Symlink to `charybdis_right_standalone.conf` (identical hardware config)

#### Shield-Specific Files
- **`config/charybdis.keymap`**: Defines all key layers, behaviors, and bindings
- **`config/charybdis.dtsi`**: Shared device tree definitions (keyboard matrix, kscan, physical layout)
- **`charybdis_left.overlay`**: Left side configuration (same for both modes)
- **`charybdis_right_standalone.overlay`**: Right side for **standalone mode** (processes trackball locally)
- **`charybdis_right_dongle.overlay`**: Right side for **dongle mode** (forwards trackball to dongle)
- **`prospector_dongle.overlay`**: Prospector dongle configuration (receives trackball from right peripheral)
- **`config/west.yml`**: Defines external dependencies (see West.yml section below)

## Operating Modes

### Standalone Mode
In standalone mode, the right keyboard acts as the central device:
- **Left keyboard**: Peripheral (Nice!Nano v2)
- **Right keyboard**: Central with trackball (Nice!Nano v2)
- **Connection**: Left → Right → Host Computer

### Dongle Mode
In dongle mode, a dedicated dongle acts as the central device with a display:
- **Left keyboard**: Peripheral (Nice!Nano v2)
- **Right keyboard**: Peripheral with trackball (Nice!Nano v2)
- **Dongle**: Central with Prospector OLED display (Seeeduino XIAO BLE)
- **Connection**: Left → Dongle ← Right, Dongle → Host Computer
- **Pairing Order**: Pair left keyboard first, then right keyboard for correct battery display

### Dongle Display Features (Prospector Module)
- Active layer indicator with layer names
- Split battery status for both peripherals
- Peripheral connection status indicators
- Caps Word indicator
- Fixed brightness (50%) without ambient light sensor

## West.yml Configuration

The `config/west.yml` file defines the ZMK firmware dependencies and external modules used in this configuration.

### Remotes Section

```yaml
remotes:
  - name: zmkfirmware
    url-base: https://github.com/zmkfirmware
  - name: badjeff
    url-base: https://github.com/badjeff
  - name: carrefinho
    url-base: https://github.com/carrefinho
```

- **`zmkfirmware`**: The main ZMK firmware repository, containing the core ZMK application code
- **`badjeff`**: Repository containing the PMW3610 trackball driver used for the Charybdis trackball. See [zmk-pmw3610-driver](https://github.com/badjeff/zmk-pmw3610-driver) for full configuration options.
- **`carrefinho`**: Repository containing the Prospector display module for the dongle. See [prospector-zmk-module](https://github.com/carrefinho/prospector-zmk-module) for display configuration options.

### Projects Section

```yaml
projects:
  - name: zmk
    remote: zmkfirmware
    revision: main
    import: app/west.yml
  - name: zmk-pmw3610-driver
    remote: badjeff
    revision: main
  - name: prospector-zmk-module
    remote: carrefinho
    revision: main
```

- **`zmk`**:
  - **Purpose**: Main ZMK firmware application
  - **Source**: `zmkfirmware` remote
  - **Version**: `main` branch
  - **Import**: Includes additional dependencies from `app/west.yml` in the ZMK repository

- **`zmk-pmw3610-driver`**:
  - **Purpose**: PMW3610 trackball sensor driver for ZMK
  - **Source**: `badjeff` remote
  - **Version**: `main` branch
  - **Note**: This driver provides device tree bindings and driver code for the PMW3610 trackball sensor used on the Charybdis right side

- **`prospector-zmk-module`**:
  - **Purpose**: OLED display module for dongle with ZMK Studio support
  - **Source**: `carrefinho` remote
  - **Version**: `main` branch
  - **Note**: Provides the `prospector_adapter` shield for dongle mode, includes widgets for layer display, battery status, and connection indicators

### Self Section

```yaml
self:
  path: config
```

- **`path: config`**: Tells west that this repository's configuration files are located in the `config/` directory

## Keymap

Can be updated at [/config/charybdis.keymap](/config/charybdis.keymap) and rendered with [render.sh](/docs/keymap/render.sh)

Generated with [Keymap Drawer](https://github.com/caksoylar/keymap-drawer-web/)

![Keymap](/docs/keymap/keymap.svg)

## Trackball Sensitivity Configuration

The trackball sensitivity can be adjusted at both hardware and software levels.

### Hardware Sensor Sensitivity (CPI/DPI)

The PMW3610 trackball sensor CPI (Counts Per Inch) is configured in [`config/boards/shields/charybdis/charybdis_right_common.dtsi`](/config/boards/shields/charybdis/charybdis_right_common.dtsi):

```dts
trackball: trackball@0 {
    compatible = "pixart,pmw3610";
    cpi = <800>;  // Change this value
    // ...
};
```

**Common CPI values:**
- `400` - Low sensitivity (more physical movement needed)
- `800` - Default, balanced sensitivity
- `1200` - High sensitivity
- `1600` - Very high sensitivity

### Software Scaling (Movement Speed)

Software scaling is configured per layer in [`config/boards/shields/charybdis/charybdis_trackball_processors.dtsi`](/config/boards/shields/charybdis/charybdis_trackball_processors.dtsi). The trackball has three different modes with independent sensitivity settings:

```dts
// Normal cursor movement (BASE and POINTER layers)
move {
    layers = <BASE POINTER>;
    input-processors = <&zip_xy_scaler 7 6>;  // multiplier divisor
};

// Precise movement (SNIPING layer)
snipe {
    layers = <SNIPING>;
    input-processors = <&zip_xy_scaler 1 3>;  // 1/3 speed for precision
};

// Scroll mode (SCROLL layer)
scroll {
    layers = <SCROLL>;
    input-processors = <&zip_xy_scaler 1 10>;  // Adjust scroll speed
};
```

### How Scaler Values Work

The scaler uses the formula: `output = (input × multiplier) / divisor`

**Examples:**
- `<&zip_xy_scaler 2 1>` - Doubles movement speed (input × 2 / 1)
- `<&zip_xy_scaler 1 2>` - Halves movement speed (input × 1 / 2)
- `<&zip_xy_scaler 7 6>` - Slightly faster than 1:1 (input × 7 / 6)

**To adjust sensitivity:**

| Goal | Change | Example |
|------|--------|---------|
| **Faster cursor** | Increase multiplier or decrease divisor | `7 6` → `8 6` or `7 5` |
| **Slower cursor** | Decrease multiplier or increase divisor | `7 6` → `6 6` or `7 7` |
| **Faster scroll** | Decrease divisor | `1 10` → `1 5` |
| **Slower scroll** | Increase divisor | `1 10` → `1 15` |

⚠️ **Important:** Use values ≤ 16 for both multiplier and divisor to avoid overflows.

### Reference Documentation

For more details on input processors, see:
- [ZMK Scaler Documentation](https://zmk.dev/docs/keymaps/input-processors/scaler)
- [PMW3610 Driver Configuration](https://github.com/badjeff/zmk-pmw3610-driver)

## ZMK Studio Support

This configuration includes support for [ZMK Studio](https://zmk.dev/docs/features/studio), which allows you to interactively configure and test your keyboard layout.

### Physical Layout Definition

The physical layout for ZMK Studio is defined in [`config/boards/shields/charybdis/charybdis.dtsi`](/config/boards/shields/charybdis/charybdis.dtsi) in the `charybdis_6col_layout` section. This defines the physical key positions, sizes, and rotations needed for the visual representation in ZMK Studio.

### Enabling/Disabling ZMK Studio

ZMK Studio support is enabled by default via the build configuration in [`build.yaml`](/build.yaml).

**Standalone mode** - Right keyboard has ZMK Studio:
```yaml
- board: nice_nano_v2
  shield: charybdis_right_standalone
  snippet: studio-rpc-usb-uart
  cmake-args: -DCONFIG_ZMK_STUDIO=y
```

**Dongle mode** - Prospector dongle has ZMK Studio:
```yaml
- board: seeeduino_xiao_ble
  shield: prospector_dongle prospector_adapter
  snippet: studio-rpc-usb-uart
  cmake-args: -DCONFIG_ZMK_STUDIO=y
```

To disable ZMK Studio support, comment out the `snippet` and `cmake-args` lines in the respective build configuration.

### Studio Unlock

To unlock ZMK Studio for configuration, press all three right thumb keys simultaneously:

- **RET** (Return/Enter)
- **SYMBOLS** (hold) / **SPACE** (tap)
- **RAISE** (hold) / **BSPC** (tap)

This combo is defined in [`config/charybdis.keymap`](/config/charybdis.keymap) as `combo_studio_unlock` using key positions 53, 54, and 55.

## Building Firmware

### GitHub Actions (Automatic)
Push changes to your repository and GitHub Actions will automatically build firmware for all configurations defined in [`build.yaml`](/build.yaml). Firmware files will be available in the Actions artifacts as a `firmware.zip` file containing:

- `charybdis_left-nice_nano_v2-zmk.uf2`
- `charybdis_right_standalone-nice_nano_v2-zmk.uf2`
- `charybdis_right_dongle-nice_nano_v2-zmk.uf2`
- `prospector_dongle prospector_adapter-seeeduino_xiao_ble-zmk.uf2`
- `tester_pro_micro-nice_nano_v2-zmk.uf2`
- `settings_reset-nice_nano_v2-zmk.uf2`
- `settings_reset-seeeduino_xiao_ble-zmk.uf2`

### Local Build (Manual)
For local building using Docker, see [`manual_build/BUILD_README.md`](/manual_build/BUILD_README.md) for detailed instructions.

The interactive build script provides options for:
1. **charybdis_left** - Left keyboard (works with both modes)
2. **charybdis_right_standalone** - Right keyboard for standalone mode (Nice!Nano v2)
3. **charybdis_right_dongle** - Right keyboard for dongle mode (Nice!Nano v2)
4. **prospector_dongle prospector_adapter** - Dongle with display (Seeeduino XIAO BLE)
5. **tester_pro_micro** - GPIO pin tester for Pro Micro-compatible boards
6. **settings_reset** - Reset stored settings

⚠️ **Known Issue:** Option 4 (prospector_dongle with prospector_adapter) currently fails in local builds due to module patching requirements. Options 1-3, 5, and 6 work correctly. **Use GitHub Actions for dongle builds** or consider using [act](https://github.com/nektos/act) to run the GitHub Actions workflow locally.

Built firmware files are automatically copied to `manual_build/artifacts/output/` with descriptive names.

## Flashing Firmware

### How to Flash
1. Double-press the reset button on the board to enter bootloader mode
2. The board will appear as a USB drive
3. Copy the appropriate `.uf2` file to the USB drive
4. The board will automatically flash and restart

### Standalone Mode
**First time or changing modes: Reset settings first**
1. Flash `settings_reset-nice_nano_v2-zmk.uf2` to **both** keyboards
2. Flash `charybdis_left-nice_nano_v2-zmk.uf2` to the left keyboard
3. Flash `charybdis_right_standalone-nice_nano_v2-zmk.uf2` to the right keyboard
4. The keyboards will automatically pair with each other

### Dongle Mode
**First time or changing modes: Reset settings first**
1. Flash `settings_reset-nice_nano_v2-zmk.uf2` to **both** keyboards
2. Flash `settings_reset-seeeduino_xiao_ble-zmk.uf2` to the **dongle**
3. Flash `prospector_dongle prospector_adapter-seeeduino_xiao_ble-zmk.uf2` to the dongle
4. Flash `charybdis_left-nice_nano_v2-zmk.uf2` to the left keyboard
5. Flash `charybdis_right_dongle-nice_nano_v2-zmk.uf2` to the right keyboard
6. **Important**: Pair the left keyboard to the dongle first, then pair the right keyboard

### Tester Pro Micro (GPIO Testing)
**For testing a Pro Micro-compatible board**
1. Flash `tester_pro_micro-nice_nano_v2-zmk.uf2` (or your board variant) to the controller
2. Connect the board via USB to your computer
3. Open a text editor or terminal
4. Connect a switch or wire from any GPIO pin to GND and trigger it
5. The board will output "PIN X" where X is the pin number (e.g., "PIN 14")
6. Test all pins you want to verify

**Note**: The tester firmware disables Bluetooth and runs in USB-only mode for simplicity.
