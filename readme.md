# ZMK CONFIG FOR THE CHARYBDIS 4X6 WIRELESS SPLIT KEYBOARD ZEPHYR 4.1

This configuration supports two modes:

- **Standalone Mode**: Right keyboard acts as central, connects directly to host
- **Dongle Mode**: Dedicated dongle with display acts as central, both keyboards connect to it

## Table of Contents

- [ZMK CONFIG FOR THE CHARYBDIS 4X6 WIRELESS SPLIT KEYBOARD ZEPHYR 4.1](#zmk-config-for-the-charybdis-4x6-wireless-split-keyboard-zephyr-41)
  - [Table of Contents](#table-of-contents)
  - [BOM](#bom)
    - [Additional Components for Dongle Mode](#additional-components-for-dongle-mode)
      - [Option 1: Prospector Dongle (Seeeduino XIAO BLE)](#option-1-prospector-dongle-seeeduino-xiao-ble)
      - [Option 2: Nice!Nano Dongle (Nice!Nano v2)](#option-2-nicenano-dongle-nicenano-v2)
      - [Option 3: ZDSE Prospector Dongle (Seeeduino XIAO BLE)](#option-3-zdse-prospector-dongle-seeeduino-xiao-ble)
  - [Tester Pro Micro Shield](#tester-pro-micro-shield)
  - [Repository Structure](#repository-structure)
    - [Key Files Explained](#key-files-explained)
      - [Shared Configuration Files (Consolidated)](#shared-configuration-files-consolidated)
      - [Shield-Specific Files](#shield-specific-files)
  - [Operating Modes](#operating-modes)
    - [Standalone Mode](#standalone-mode)
    - [Dongle Mode](#dongle-mode)
    - [Dongle Display Features](#dongle-display-features)
      - [Prospector Dongle (Seeeduino XIAO BLE)](#prospector-dongle-seeeduino-xiao-ble)
      - [ZDSE Prospector Dongle (Seeeduino XIAO BLE)](#zdse-prospector-dongle-seeeduino-xiao-ble)
      - [Nice!Nano Dongle (Nice!Nano v2)](#nicenano-dongle-nicenano-v2)
  - [West.yml Configuration](#westyml-configuration)
    - [Remotes Section](#remotes-section)
    - [Projects Section](#projects-section)
    - [Self Section](#self-section)
  - [Keymap](#keymap)
  - [RGB LED Configuration](#rgb-led-configuration)
    - [RGB Shield Variants](#rgb-led-configuration)
    - [RGB Off/On Reliability](#rgb-offon-reliability)
    - [Change LED Data Pin](#change-led-data-pin)
    - [Change LED Count Per Side](#change-led-count-per-side)
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
    - [Flashing (Standalone Mode)](#flashing-standalone-mode)
      - [Flashing checklist (reset settings first)](#flashing-checklist-reset-settings-first)
    - [Flashing (Dongle Mode)](#flashing-dongle-mode)
      - [First time or changing modes: reset settings first](#first-time-or-changing-modes-reset-settings-first)
    - [Tester Pro Micro (GPIO Testing)](#tester-pro-micro-gpio-testing)
      - [For testing a Pro Micro-compatible board](#for-testing-a-pro-micro-compatible-board)

## BOM

See the full [Bill of Materials](/docs/bom/readme.md) for electronics, PCBs, fabrication files (ready-to-upload gerbers for PCBWay/JLCPCB), and 3D print files.

RGB parts (SK6812 LEDs, 1uF capacitors, and 330 Ohm resistors) are documented there as **optional**.

### Additional Components for Dongle Mode

#### Option 1: Prospector Dongle (Seeeduino XIAO BLE)

- 1x Seeeduino XIAO BLE (nRF52840) - Dongle central
- 1x [Prospector Display Module](https://github.com/carrefinho/prospector) - Custom OLED display

#### Option 2: Nice!Nano Dongle (Nice!Nano v2)

- 1x Nice!Nano v2 (nRF52840) - Dongle central
- 1x OLED Display (SSD1306, I2C) - Generic OLED module
  - **128x32** (0.91" OLED) - Use `dongle_nice_32` shield
  - **128x64** (0.96" OLED) - Use `dongle_nice_64` shield
- Uses [zmk-dongle-display](https://github.com/englmaxi/zmk-dongle-display) module

#### Option 3: ZDSE Prospector Dongle (Seeeduino XIAO BLE)

- 1x Seeeduino XIAO BLE (nRF52840) - Dongle central
- 1x [Prospector Display Module](https://github.com/carrefinho/prospector) - Custom IPS LCD display
- Uses [zmk-dongle-screen-engine](https://github.com/hitsmaxft/zmk-dongle-screen-engine) with the [Neon Cat theme](https://github.com/hitsmaxft/zdse-themes/tree/main/themes/neon-cat)
- Alternative firmware for Prospector hardware with animated RGB565 themes

![Wireless Keyboard](/docs/picture/wireless-charybdis.png)

## Tester Pro Micro Shield

This repository includes a **ZMK Tester Shield** (`tester_pro_micro`) for troubleshooting and testing Pro Micro-compatible boards (Nice!Nano, Seeeduino XIAO, etc.). The tester shield maps all 18 available GPIO pins (D0-D10, D14-D16, D18-D21) to virtual "keys" that output "PIN X" when triggered, helping you verify all GPIO pins are working correctly before assembling your keyboard.

**How to use:**

1. Flash `tester_pro_micro-nice_nano-zmk.uf2` to your controller (see [Building Firmware](#building-firmware))
2. Connect the board via USB to your computer
3. Open a text editor
4. Connect a switch or wire from any GPIO pin to GND and trigger it
5. The board will output "PIN X" where X is the pin number (e.g., "PIN 14")

The tester runs in USB-only mode (no BLE) and includes two physical layouts for ZMK Studio visualization.

## Repository Structure

```text
zmk-config-charybdis/
├── CMakeLists.txt                   # Module CMake entry (adds custom app sources)
├── boards/                          # Module-based shields (Zephyr 4.1+ recommended layout)
│   └── shields/
│       ├── charybdis/               # Charybdis shield configuration
│       │   ├── charybdis.dtsi                        # Common device tree (keyboard layout, kscan)
│       │   ├── charybdis_layers.h                    # Shared layer definitions
│       │   ├── charybdis_trackball_processors.dtsi   # Shared trackball processing config
│       │   ├── charybdis_rgb.dtsi                    # Shared RGB underglow/per-key LED config
│       │   ├── charybdis_right_common.dtsi           # Shared right keyboard hardware config
│       │   ├── charybdis_left.conf                   # Left side Kconfig options (left-specific only)
│       │   ├── charybdis_left.overlay                # Left side device tree overlay
│       │   ├── charybdis_left_rgb.conf               # Left RGB variant Kconfig (comment only)
│       │   ├── charybdis_left_rgb.overlay            # Left RGB variant (base overlay + LED strip)
│       │   ├── charybdis_right_standalone.conf       # Right side Kconfig (standalone mode)
│       │   ├── charybdis_right_standalone.overlay    # Right side overlay (standalone mode)
│       │   ├── charybdis_right_standalone_rgb.conf   # Symlink → charybdis_right_standalone.conf
│       │   ├── charybdis_right_standalone_rgb.overlay # Right standalone RGB variant (+ LED strip)
│       │   ├── dongle_charybdis_right.conf           # Symlink → charybdis_right_standalone.conf
│       │   ├── dongle_charybdis_right.overlay        # Right side overlay (dongle mode)
│       │   ├── dongle_charybdis_right_rgb.conf       # Symlink → charybdis_right_standalone.conf
│       │   ├── dongle_charybdis_right_rgb.overlay    # Right dongle-mode RGB variant (+ LED strip)
│       │   ├── dongle_common.dtsi                    # Base shared dongle config (all variants)
│       │   ├── dongle_nice_common.dtsi               # Nice!Nano platform common config
│       │   ├── dongle_prospector_common.dtsi         # Prospector platform common config
│       │   ├── dongle_prospector.conf                # Prospector dongle Kconfig options
│       │   ├── dongle_prospector.overlay             # Prospector dongle device tree overlay
│       │   ├── dongle_zdse_prospector.conf           # ZDSE Prospector dongle Kconfig (Neon Cat theme)
│       │   ├── dongle_zdse_prospector.overlay        # ZDSE Prospector display hardware overlay
│       │   ├── dongle_nice_32.conf                   # Nice!Nano dongle 32px Kconfig options
│       │   ├── dongle_nice_32.overlay                # Nice!Nano dongle 32px device tree overlay
│       │   ├── dongle_nice_64.conf                   # Nice!Nano dongle 64px Kconfig options
│       │   ├── dongle_nice_64.overlay                # Nice!Nano dongle 64px device tree overlay
│       │   ├── Kconfig.defconfig                     # Shield Kconfig definitions
│       │   └── Kconfig.shield                        # Shield Kconfig options
│       └── tester_pro_micro/         # Pro Micro GPIO tester shield
│           ├── Kconfig.shield                        # Shield identifier
│           ├── Kconfig.defconfig                     # Shield defaults (USB-only, no BLE)
│           ├── tester_pro_micro.zmk.yml              # Shield metadata
│           ├── tester_pro_micro.overlay              # GPIO pin definitions (18 pins)
│           ├── tester_pro_micro.keymap               # Pin test macros
│           └── tester_pro_micro-layouts.dtsi         # Physical layouts (pinout + single row)
├── dts/                             # Local devicetree extensions
│   └── bindings/
│       └── behaviors/
│           └── zmk,behavior-rgb-local.yaml           # Custom RGB behavior binding
├── config/                          # Main ZMK configuration directory (keymap + west manifest)
│   ├── charybdis.conf               # Global ZMK configuration
│   ├── charybdis.keymap             # Keymap definition file
│   ├── charybdis.zmk.yml            # ZMK build configuration
│   ├── info.json                    # Repository metadata
│   └── west.yml                     # West manifest (see West.yml section below)
├── manual_build/                    # Local build scripts
│   ├── build.py                     # Interactive build script
│   └── BUILD_README.md              # Build instructions
├── src/                             # Local ZMK module source extensions
│   └── behaviors/
│       └── behavior_rgb_local.c     # Event-source RGB behavior for split/dongle mode
├── docs/                            # Documentation
│   ├── bom/                         # Bill of Materials
│   │   ├── stl/                     # 3D Print files
│   │   │   ├── charybdis_left_base.stl
│   │   │   ├── charybdis_left_button.stl
│   │   │   ├── charybdis_left_case.stl
│   │   │   ├── scylla_right_base.stl
│   │   │   ├── scylla_right_button.stl
│   │   │   └── scylla_right_case.stl
│   │   └── readme.md
│   ├── keymap/                      # Keymap documentation
│   │   ├── config.yaml              # Keymap drawer configuration
│   │   ├── keymap.yaml              # Base keymap definition
│   │   ├── keymap.svg               # Generated: Visual keymap (created by render.sh)
│   │   └── render.sh                # Script to parse keymap and generate SVG
│   └── picture/                     # Images
│       ├── wireless-charybdis.png
│       ├── charybdis-rgb-underglow.jpg
│       └── led-power-switch-mod.jpg
├── build.yaml                       # GitHub Actions build configuration
├── zephyr/
│   └── module.yml                   # Zephyr module marker (board_root, dts_root, cmake)
└── readme.md                        # This file
```

### Key Files Explained

#### Shared Configuration Files (Consolidated)

- **`charybdis_layers.h`**: Layer definitions (BASE, POINTER, LOWER, RAISE, SYMBOLS, SCROLL, SNIPING) used across all shields
- **`charybdis_trackball_processors.dtsi`**: Shared trackball input processing configurations (snipe/scroll/move modes)
- **`charybdis_rgb.dtsi`**: Shared RGB LED bus/device configuration (SPI, LED strip node, `zmk,underglow` chosen node)
- **`charybdis_right_common.dtsi`**: Common hardware config for both right keyboard variants (GPIO, SPI, trackball device)
- **`dongle_charybdis_right.conf`**: Symlink to `charybdis_right_standalone.conf` (identical hardware config)
- **`src/behaviors/behavior_rgb_local.c`**: Custom RGB behavior using event-source locality so RGB controls execute on the half that generated the key event (useful in dongle/split mode)
- **`dts/bindings/behaviors/zmk,behavior-rgb-local.yaml`**: Devicetree binding for the custom RGB behavior
- **`CMakeLists.txt`**: Registers the custom behavior source into the ZMK `app` target
- **`zephyr/module.yml`**: Exposes board/dts roots and CMake entry for this module

#### Shield-Specific Files

- **`config/charybdis.keymap`**: Defines all key layers, behaviors, and bindings
- **`boards/shields/charybdis/charybdis.dtsi`**: Shared device tree definitions (keyboard matrix, kscan, physical layout)
- **`charybdis_left.overlay`**: Left side configuration (same for both modes)
- **`charybdis_right_standalone.overlay`**: Right side for **standalone mode** (processes trackball locally)
- **`dongle_charybdis_right.overlay`**: Right side for **dongle mode** (forwards trackball to dongle)
- **`*_rgb.overlay` variants**: Thin wrappers that include the base overlay plus `charybdis_rgb.dtsi` (LED strip on spi3). Use these when the optional RGB LEDs are installed - see [RGB LED Configuration](#rgb-led-configuration)
- **`dongle_common.dtsi`**: Base shared configuration for all dongle variants (matrix, input split, physical layout)
- **`dongle_nice_common.dtsi`**: Nice!Nano platform-specific common config (KSCAN, I2C)
- **`dongle_prospector_common.dtsi`**: Prospector platform-specific common config (KSCAN)
- **`dongle_prospector.overlay`**: Prospector dongle configuration (receives trackball from right peripheral)
- **`dongle_zdse_prospector.overlay`**: ZDSE Prospector dongle - hardware-only ST7789V display + PWM backlight shield for `dongle_screen_host` (receives trackball from right peripheral)
- **`dongle_nice_32.overlay`**: Nice!Nano dongle with 128x32 OLED display
- **`dongle_nice_64.overlay`**: Nice!Nano dongle with 128x64 OLED display
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
- **Dongle Options**:
  - **Prospector**: Seeeduino XIAO BLE with custom Prospector display module
  - **Nice!Nano**: Nice!Nano v2 with generic OLED (I2C)
    - **128x32 OLED** (0.91") - Use `dongle_nice_32` shield
    - **128x64 OLED** (0.96") - Use `dongle_nice_64` shield
- **Connection**: Left → Dongle ← Right, Dongle → Host Computer
- **Pairing Order**: Pair left keyboard first, then right keyboard for correct battery display
- **Power**: USB powered (no sleep mode needed)

### Dongle Display Features

#### Prospector Dongle (Seeeduino XIAO BLE)

- Active layer indicator with layer names
- Split battery status for both peripherals
- Peripheral connection status indicators
- Caps Word indicator
- Fixed brightness (50%) without ambient light sensor

#### ZDSE Prospector Dongle (Seeeduino XIAO BLE)

- **Display**: Prospector 1.69" IPS LCD (ST7789V, 240x280 RGB565)
- **Firmware**: [zmk-dongle-screen-engine](https://github.com/hitsmaxft/zmk-dongle-screen-engine) (ZDSE) with the [Neon Cat theme](https://github.com/hitsmaxft/zdse-themes/tree/main/themes/neon-cat)
- **Theme**: Synthwave pixel HUD with time-driven character, water shimmer, equalizer, keyboard status, and modifier feedback
- **Battery**: Split battery status for both peripherals
- **WPM**: Words Per Minute driven animation/equalizer
- **Brightness**: Fixed at 50% (`CONFIG_ZMK_DONGLE_SCREEN_BRIGHTNESS`), no ambient light sensor
- **Trackball**: Full trackball forwarding supported (unlike the retired YADS option)
- **Touch**: Not available - the Prospector has no touch controller, so theme gestures are inactive

#### Nice!Nano Dongle (Nice!Nano v2)

Two variants are available based on OLED display size:

**128x32 OLED (dongle_nice_32):**

- **Display**: 128x32 OLED (SSD1306) via I2C (0.91" module)
- **Active layer name** with center alignment and scrolling support
- **Peripheral battery levels** (left + right keyboards)
- **HID indicators** (CAPS, NUM, SCROLL lock)
- **Output status** (USB/BLE connection)
- **Active modifiers display** (Shift, Ctrl, Alt, GUI)
- **Display timeout**: 5 minutes (configurable)
- **Optimized for 32px height**: Bongo cat disabled, modifiers optional

**128x64 OLED (dongle_nice_64):**

- **Display**: 128x64 OLED (SSD1306) via I2C (0.96" module)
- **Active layer name** with center alignment and scrolling support
- **Peripheral battery levels** (left + right keyboards)
- **HID indicators** (CAPS, NUM, SCROLL lock)
- **Output status** (USB/BLE connection)
- **Active modifiers display** (Shift, Ctrl, Alt, GUI)
- **Bongo cat** enabled (more vertical space available)
- **Display timeout**: 5 minutes (configurable)

**Wiring (Nice!Nano to OLED):**

- VCC → 3.3V
- GND → GND
- SDA → Pin 2
- SCL → Pin 3

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
  - name: englmaxi
    url-base: https://github.com/englmaxi
  - name: hitsmaxft
    url-base: https://github.com/hitsmaxft
```

- **`zmkfirmware`**: The main ZMK firmware repository, containing the core ZMK application code
- **`badjeff`**: Repository containing the PMW3610 trackball driver used for the Charybdis trackball. See [zmk-pmw3610-driver](https://github.com/badjeff/zmk-pmw3610-driver) for full configuration options.
- **`carrefinho`**: Repository containing the Prospector display module for the dongle. See [prospector-zmk-module](https://github.com/carrefinho/prospector-zmk-module) for display configuration options.
- **`englmaxi`**: Repository containing the OLED dongle display module. See [zmk-dongle-display](https://github.com/englmaxi/zmk-dongle-display).
- **`hitsmaxft`**: Repository containing the ZDSE screen engine and themes. See [zmk-dongle-screen-engine](https://github.com/hitsmaxft/zmk-dongle-screen-engine) and [zdse-themes](https://github.com/hitsmaxft/zdse-themes).

### Projects Section

```yaml
projects:
  - name: zmk
    remote: zmkfirmware
    revision: main
    import: app/west.yml
  - name: zmk-pmw3610-driver
    remote: badjeff
    revision: zmk-0.4
  - name: prospector-zmk-module
    remote: carrefinho
    revision: core/zephyr-4-1
  - name: zmk-dongle-display
    remote: englmaxi
    revision: main
  - name: zmk-dongle-screen-engine
    remote: hitsmaxft
    revision: v1.4.1
    path: modules/zmk-dongle-screen-engine
  - name: zdse-themes
    remote: hitsmaxft
    revision: v1.0.0
    path: modules/zdse-themes
```

- **`zmk`**:
  - **Purpose**: Main ZMK firmware application
  - **Source**: `zmkfirmware` remote
  - **Version**: `main` branch
  - **Import**: Includes additional dependencies from `app/west.yml` in the ZMK repository

- **`zmk-pmw3610-driver`**:
  - **Purpose**: PMW3610 trackball sensor driver for ZMK
  - **Source**: `badjeff` remote
  - **Version**: `zmk-0.4` branch (PMW3610-alt compatible + Zephyr 4.1 updates)
  - **Note**: This driver provides device tree bindings and driver code for the PMW3610 trackball sensor used on the Charybdis right side

- **`prospector-zmk-module`**:
  - **Purpose**: Custom OLED display module for Seeeduino XIAO BLE dongle with ZMK Studio support
  - **Source**: `carrefinho` remote
  - **Version**: `core/zephyr-4-1` branch
  - **Note**: Provides the `prospector_adapter` shield for dongle mode, includes widgets for layer display, battery status, and connection indicators

- **`zmk-dongle-display`**:
  - **Purpose**: Generic OLED display module for Nice!Nano dongle (128x32/128x64 displays)
  - **Source**: `englmaxi` remote
  - **Version**: `main` branch
  - **Note**: Provides the `dongle_display` shield for generic I2C OLED displays (SSD1306). Supports both 128x32 and 128x64 displays with configurable widgets. Use `dongle_nice_32` shield for 32px displays or `dongle_nice_64` shield for 64px displays.

- **`zmk-dongle-screen-engine`**:
  - **Purpose**: ZDSE (ZMK Dongle Screen Engine) - display-agnostic theme host with RGB565 rendering for ZMK dongles
  - **Source**: `hitsmaxft` remote
  - **Version**: `v1.1.2` tag (pinned release matching zdse-themes v1.0.0 Theme ABI 1.1)
  - **Note**: Provides the `dongle_screen_host` shield which owns the status screen. Renders animated themes directly to the ST7789V display without LVGL widgets

- **`zdse-themes`**:
  - **Purpose**: Theme modules for ZDSE - this build uses the Neon Cat theme (synthwave pixel HUD)
  - **Source**: `hitsmaxft` remote
  - **Version**: `v1.0.0` tag (pinned release)
  - **Note**: Themes compile only when explicitly enabled (e.g. `CONFIG_ZDSE_NEON_CAT_THEME=y` in `dongle_zdse_prospector.conf`)

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

## RGB LED Configuration

RGB underglow is **opt-in via shield variants**. The base keyboard shields assume no LED hardware; the `_rgb` variants add the WS2812/SK6812 strip (spi3 MOSI on `P1.13`, nice!nano `D15`):

![Charybdis with RGB underglow installed](/docs/picture/charybdis-rgb-underglow.jpg)

| Base shield (no LEDs) | RGB variant | Side / mode |
|---|---|---|
| `charybdis_left` | `charybdis_left_rgb` | Left (both modes) |
| `charybdis_right_standalone` | `charybdis_right_standalone_rgb` | Right, standalone central |
| `dongle_charybdis_right` | `dongle_charybdis_right_rgb` | Right, dongle-mode peripheral |

Each `_rgb` overlay just includes the base overlay plus `charybdis_rgb.dtsi`; `SPI`/`LED_STRIP`/`ZMK_RGB_UNDERGLOW` defaults are gated on the `_rgb` shields in [`Kconfig.defconfig`](/boards/shields/charybdis/Kconfig.defconfig). Flash the `_rgb` firmware to **both** halves when LEDs are installed.

With an `_rgb` build, underglow starts on at boot in the rainbow (spectrum) effect at 25% brightness (see [`config/charybdis.conf`](/config/charybdis.conf)). RGB keys on the raise layer (`RGB_ON/OFF/BRI/BRD/EFF/HUI`) work from either half and stay in sync via the custom `rgb_loc` behavior — including when a dongle without LEDs is the central.

> [!WARNING]
> **Software "off" is not power off (right/trackball side).** On the right half, the LED strip's power rail is shared with the trackball, and the nice!nano has no dedicated power-management pin for the LEDs. ZMK's hard power cut (`EXT_POWER`) would also kill the trackball — which is why this repo sets `CONFIG_ZMK_RGB_UNDERGLOW_EXT_POWER=n` (see [RGB Off/On Reliability](#rgb-offon-reliability)). The consequence: `RGB_OFF` only stops the data signal, and WS2812/SK6812 LEDs keep drawing significant idle current per LED (driver IC quiescent current) even when fully "off", noticeably shortening battery life.
>
> If battery life matters, the recommended mod is a **physical switch on the LED power wire** — between the controller and the strip only, not the shared rail, so the trackball keeps running while the LEDs are hard-powered off.
>
> ![Slide switch wired into the LED power line on the PCB](/docs/picture/led-power-switch-mod.jpg)

### RGB Off/On Reliability

If LEDs turn off but do not turn back on reliably with `RGB_ON` (until reset), set:

- [`config/charybdis.conf`](/config/charybdis.conf)

```kconfig
CONFIG_ZMK_RGB_UNDERGLOW_EXT_POWER=n
```

This decouples RGB commands from external power rail control.  
With this set to `n`, `RGB_ON/OFF` controls underglow state only, which is more reliable on some builds/hardware combinations.

Quick behavior summary:

- `CONFIG_ZMK_RGB_UNDERGLOW_EXT_POWER=y` (ZMK upstream default): `RGB_ON/OFF` can also toggle external power for LEDs. This can save more battery, but some setups may fail to re-enable LEDs cleanly until reset.
- `CONFIG_ZMK_RGB_UNDERGLOW_EXT_POWER=n` (current setting in this repo): `RGB_ON/OFF` only changes underglow state/effect in software. This is usually more reliable for turning LEDs back on, with a small battery tradeoff compared to hard power-cut behavior.

### Change LED Data Pin

To change the RGB LED data pin, edit:

- [`boards/shields/charybdis/charybdis_rgb.dtsi`](/boards/shields/charybdis/charybdis_rgb.dtsi)

Find these lines and update the `NRF_PSEL(SPIM_MOSI, <port>, <pin>)` value:

```dts
spi3_default: spi3_default {
    group1 {
        psels = <NRF_PSEL(SPIM_MOSI, 1, 13)>;
    };
};
```

```dts
spi3_sleep: spi3_sleep {
    group1 {
        psels = <NRF_PSEL(SPIM_MOSI, 1, 13)>;
        low-power-enable;
    };
};
```

Current default is Pro Micro `D15` on nice!nano v2 (`P1.13`).

### Change LED Count Per Side

The per-side LED count is set in the `_rgb` variant overlays where the shared RGB include is used:

- Left side: [`boards/shields/charybdis/charybdis_left_rgb.overlay`](/boards/shields/charybdis/charybdis_left_rgb.overlay)  
  `#define CHARYBDIS_RGB_CHAIN_LENGTH 29`
- Right side: [`boards/shields/charybdis/charybdis_right_standalone_rgb.overlay`](/boards/shields/charybdis/charybdis_right_standalone_rgb.overlay) and [`boards/shields/charybdis/dongle_charybdis_right_rgb.overlay`](/boards/shields/charybdis/dongle_charybdis_right_rgb.overlay)  
  `#define CHARYBDIS_RGB_CHAIN_LENGTH 27`

## Trackball Sensitivity Configuration

The trackball sensitivity can be adjusted at both hardware and software levels.

### Hardware Sensor Sensitivity (CPI/DPI)

The PMW3610 trackball sensor CPI (Counts Per Inch) is configured in [`boards/shields/charybdis/charybdis_right_common.dtsi`](/boards/shields/charybdis/charybdis_right_common.dtsi):

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

Software scaling is configured per layer in [`boards/shields/charybdis/charybdis_trackball_processors.dtsi`](/boards/shields/charybdis/charybdis_trackball_processors.dtsi). The trackball has three different modes with independent sensitivity settings:

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

The physical layout for ZMK Studio is defined in [`boards/shields/charybdis/charybdis.dtsi`](/boards/shields/charybdis/charybdis.dtsi) in the `charybdis_6col_layout` section. This defines the physical key positions, sizes, and rotations needed for the visual representation in ZMK Studio.

### Enabling/Disabling ZMK Studio

ZMK Studio support is enabled by default via the build configuration in [`build.yaml`](/build.yaml).

**Standalone mode** - Right keyboard has ZMK Studio:

```yaml
- board: nice_nano
  shield: charybdis_right_standalone
  snippet: studio-rpc-usb-uart
  cmake-args: -DCONFIG_ZMK_STUDIO=y
```

**Dongle mode** - Multiple dongles have ZMK Studio:

**Prospector dongle:**

```yaml
- board: xiao_ble
  shield: dongle_prospector prospector_adapter
  snippet: studio-rpc-usb-uart
  cmake-args: -DCONFIG_ZMK_STUDIO=y
```

**Nice!Nano dongles (both 32px and 64px):**

```yaml
- board: nice_nano
  shield: dongle_nice_32 dongle_display  # or dongle_nice_64
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

- `charybdis_left-nice_nano-zmk.uf2`
- `charybdis_left_rgb-nice_nano-zmk.uf2`
- `charybdis_right_standalone-nice_nano-zmk.uf2`
- `charybdis_right_standalone_rgb-nice_nano-zmk.uf2`
- `dongle_charybdis_right-nice_nano-zmk.uf2`
- `dongle_charybdis_right_rgb-nice_nano-zmk.uf2`
- `dongle_prospector prospector_adapter-xiao_ble-zmk.uf2`
- `dongle_zdse_prospector dongle_screen_host-xiao_ble-zmk.uf2`
- `dongle_nice_32 dongle_display-nice_nano-zmk.uf2`
- `dongle_nice_64 dongle_display-nice_nano-zmk.uf2`
- `tester_pro_micro-nice_nano-zmk.uf2`
- `settings_reset-nice_nano-zmk.uf2`
- `settings_reset-xiao_ble-zmk.uf2`

### Local Build (Manual)

For local building using Docker, see [`manual_build/BUILD_README.md`](/manual_build/BUILD_README.md) for detailed instructions.

The interactive build script provides options for:

1. **charybdis_left** - Left keyboard (works with both modes)
2. **charybdis_left_rgb** - Left keyboard with RGB underglow
3. **charybdis_right_standalone** - Right keyboard for standalone mode (Nice!Nano)
4. **charybdis_right_standalone_rgb** - Right keyboard for standalone mode with RGB underglow
5. **dongle_charybdis_right** - Right keyboard for dongle mode (Nice!Nano)
6. **dongle_charybdis_right_rgb** - Right keyboard for dongle mode with RGB underglow
7. **dongle_prospector prospector_adapter** - Dongle with Prospector display (XIAO BLE)
8. **dongle_zdse_prospector dongle_screen_host** - Dongle with ZDSE Neon Cat theme (XIAO BLE)
9. **dongle_nice_32 dongle_display** - Nice!Nano dongle with 128x32 OLED
10. **dongle_nice_64 dongle_display** - Nice!Nano dongle with 128x64 OLED
11. **tester_pro_micro** - GPIO pin tester for Pro Micro-compatible boards
12. **settings_reset** - Reset stored settings

Note: Local builds use a dedicated workspace under `manual_build/west-workspace/` and should behave the same as CI. If a specific configuration fails locally, prefer building in GitHub Actions and then iterate locally once the dependency/workspace is stable.

Built firmware files are automatically copied to `manual_build/artifacts/output/` with descriptive names.

## Flashing Firmware

### How to Flash

1. Double-press the reset button on the board to enter bootloader mode
2. The board will appear as a USB drive
3. Copy the appropriate `.uf2` file to the USB drive
4. The board will automatically flash and restart

### Flashing (Standalone Mode)

#### Flashing checklist (reset settings first)

1. Flash `settings_reset-nice_nano-zmk.uf2` to **both** keyboards
2. Flash `charybdis_left-nice_nano-zmk.uf2` to the left keyboard (or `charybdis_left_rgb-nice_nano-zmk.uf2` if RGB LEDs are installed)
3. Flash `charybdis_right_standalone-nice_nano-zmk.uf2` to the right keyboard (or `charybdis_right_standalone_rgb-nice_nano-zmk.uf2` if RGB LEDs are installed)
4. The keyboards will automatically pair with each other

### Flashing (Dongle Mode)

#### First time or changing modes: reset settings first

1. **Flash settings reset and dongle firmware** (choose your dongle type):

   a) **Prospector Dongle (Seeeduino XIAO BLE)**:
      - Flash `settings_reset-nice_nano-zmk.uf2` to **both** keyboards
      - Flash `settings_reset-xiao_ble-zmk.uf2` to the **dongle**
      - Flash `dongle_prospector prospector_adapter-xiao_ble-zmk.uf2` to the dongle

   b) **ZDSE Prospector Dongle (Seeeduino XIAO BLE)**:
      - Flash `settings_reset-nice_nano-zmk.uf2` to **both** keyboards
      - Flash `settings_reset-xiao_ble-zmk.uf2` to the **dongle**
      - Flash `dongle_zdse_prospector dongle_screen_host-xiao_ble-zmk.uf2` to the dongle

   c) **Nice!Nano Dongle (Nice!Nano v2)**
      - Flash `settings_reset-nice_nano-zmk.uf2` to **all three** devices (left, right, dongle)
      - Flash the appropriate dongle firmware to the dongle:
        - **128x32 OLED**: `dongle_nice_32 dongle_display-nice_nano-zmk.uf2`
        - **128x64 OLED**: `dongle_nice_64 dongle_display-nice_nano-zmk.uf2`
      - Connect OLED display to dongle via I2C (SDA→Pin 2, SCL→Pin 3)

2. Flash `charybdis_left-nice_nano-zmk.uf2` to the left keyboard (or `charybdis_left_rgb-nice_nano-zmk.uf2` if RGB LEDs are installed)
3. Flash `dongle_charybdis_right-nice_nano-zmk.uf2` to the right keyboard (or `dongle_charybdis_right_rgb-nice_nano-zmk.uf2` if RGB LEDs are installed)
4. **Important**: Pair the left keyboard to the dongle first, then pair the right keyboard (paring occurs when reset firmware is flashed prior to main firmware). Just ensure to follow two previous steps in order (left first, then right) and the battery status will display correctly on the dongle.

### Tester Pro Micro (GPIO Testing)

#### For testing a Pro Micro-compatible board

1. Flash `tester_pro_micro-nice_nano-zmk.uf2` (or your board variant) to the controller
2. Connect the board via USB to your computer
3. Open a text editor or terminal
4. Connect a switch or wire from any GPIO pin to GND and trigger it
5. The board will output "PIN X" where X is the pin number (e.g., "PIN 14")
6. Test all pins you want to verify

**Note**: The tester firmware disables Bluetooth and runs in USB-only mode for simplicity.
