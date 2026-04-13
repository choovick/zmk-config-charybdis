# BOM

## Electronics

| Part name                                   | Amount  |
| ------------------------------------------- | ------- |
| Perixx Trackball 34mm                       | 1       |
| Nice!Nano v2 or NRF52840 Compatible Board   | 2       |
| BAT54C KL3 Diodes                           | 24      |
| 1N4148W Diodes                              | 8       |
| Reset Button 4x4x1.5                        | 2       |
| PMW3610 Module                              | 1       |
| Power Switch 1P2T SPDT Vertical H2.0mm      | 2       |
| 3.175mm Ceramic Bearing Balls (For BTU Mod) | 3       |
| 26 AWG Cable Single Core                    | 5 Meter |
| MX Switches (To your liking)                | 56      |
| JST PH 2.0 Cable And Jack Power Connector   | 2 Pairs |
| Heated Screw Insert, M3xD5x5                | 5       |
| Heated Screw Insert, M4xD6x5                | 16      |
| M3 8mm Torx Screw                           | 5       |
| M4 8mm Torx Screw                           | 16      |
| Li-Po Battery 801350 500mAh-150mAh          | 2       |
| Square Hole IC Sockets 24 pin wide          | 2       |

### Optional RGB Parts (SK6812 Per-Key)

If you want RGB lighting, add the following optional parts (based on BastardKB's original `electronics_bom.md`):

| Part name                      | Amount (4x6) | Notes                  |
| ----------------------------- | ------------ | ---------------------- |
| SK6812 Mini-E LEDs            | 58           | Optional RGB LEDs      |
| Capacitor, 1uF, size 1206     | 4            | Optional, for RGB data/power stability |
| Resistor, 330 Ohms, size 1206 | 4            | Optional, series resistor for RGB data path |
| Wires (28 AWG recommended)    | As needed    | Optional, black/red/color |
| Ribbon cables Flexstrip       | 6            | Optional, if used by your assembly approach |

## PCB

| Part name            | Amount | Link                                                      |
| -------------------- | ------ | --------------------------------------------------------- |
| Flex PCBs            | 2      | <https://github.com/Bastardkb/Scylla-PCB-Plate>           |
| Flex PCB Right Thumb | 1      | <https://github.com/Bastardkb/Charybdis-PCB-thumbs>       |
| Flex PCB Left Thumb  | 1      | <https://github.com/Bastardkb/Scylla-PCB-thumb-cluster>   |
| PMW3610 Breakout     | 1      | <https://github.com/Bastardkb/charybdis-pmw3610-breakout> |
| Nice!Nano Holder     | 1      | <https://github.com/victorlucachi/Elite-C-holder>         |

## Fabrication files

Pre-created zip files are available for convenient upload to [PCBWay](https://www.pcbway.com/) or [JLCPCB](https://jlcpcb.com/).

### PCB Gerber Files

| File                                                                     | Description                   |
| ------------------------------------------------------------------------ | ----------------------------- |
| [pcb-scylla-flex.zip](./fabrication/pcb-scylla-flex.zip)                 | Main flex PCBs (left & right) |
| [pcb-chary-thumbs.zip](./fabrication/pcb-chary-thumbs.zip)               | Charybdis right thumb cluster |
| [pcb-scylla-thumb.zip](./fabrication/pcb-scylla-thumb.zip)               | Scylla left thumb cluster     |
| [pcb-shield-nice-nano-v2.zip](./fabrication/pcb-shield-nice-nano-v2.zip) | Nice!Nano holder shield       |

### PMW3610 Breakout Board (with Assembly)

The PMW3610 breakout board files include BOM and component placement files for PCB assembly service:

| File                                                                                 | Description                         |
| ------------------------------------------------------------------------------------ | ----------------------------------- |
| [pcm-pmw3610-adapter.zip](./fabrication/pcm-pmw3610-adapter.zip)                     | Gerber files                        |
| [pcm-pmw3610-adapter-bom.csv](./fabrication/pcm-pmw3610-adapter-bom.csv)             | Bill of Materials for assembly      |
| [pcm-pmw3610-adapter-positions.csv](./fabrication/pcm-pmw3610-adapter-positions.csv) | Component placement (centroid) file |

> **PCBWay Shared Project:** A pre-configured order for the PMW3610 breakout board is available at [Charybdis PMW3610 Breakout Board](https://www.pcbway.com/project/shareproject/Charybdis_PMW3610_Breakout_Board_722a6b85.html). See the project description for assembly instructions (assembly is on the **bottom side** only).
>
> ⚠️ **Warning:** This pre-configured order has not been tested yet. There might be some back and forth with the PCB manufacturer to clarify couple of things.

## 3D Prints

| Part name                          | Amount | Link                                                                                                        |
| ---------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------- |
| Scylla Right case                  | 1      | [Scylla Right Case (High USB)](./stl/scylla_right_case.stl)                                                 |
| Charybdis Left case                | 1      | [Charybdis Left Case (High USB)](./stl/charybdis_left_case.stl)                                             |
| Scylla Right plate                 | 1      | [Scylla Right Plate (Slider Switch)](./stl/scylla_right_base.stl)                                           |
| Charybdis Left plate               | 1      | [Charybdis Left Plate (Slider Switch)](./stl/charybdis_left_base.stl)                                       |
| Scylla Right Button                | 1      | [Scylla Right Button](./stl/scylla_right_button.stl)                                                        |
| Charybdis Left Button              | 1      | [Charybdis Left Button](./stl/charybdis_left_button.stl)                                                    |
| [alternative] Original Right Case  | 1      | <https://github.com/Bastardkb/Charybdis/blob/main/files/4x6/MK2/charybdis_v4_247_right.stl>                 |
| [alternative] Original Left Case   | 1      | <https://github.com/Bastardkb/Scylla/blob/main/files/MK2/scylla_v3_36.stl>                                  |
| [alternative] Original Right Plate | 1      | <https://github.com/Bastardkb/Charybdis/blob/main/files/4x6/MK2/charybdis_v4_247_plate_R.stl>               |
| [alternative] Original Left Plate  | 1      | <https://github.com/Bastardkb/Scylla/blob/main/files/MK2/scylla_v3_36_plate_left.stl>                       |
| Adapter - top                      | 1      | <https://github.com/Bastardkb/Charybdis/blob/main/files/4x6/adapter_v4_v4_top.stl>                          |
| Adapter - bottom                   | 1      | <https://github.com/Bastardkb/Charybdis/blob/main/files/mods/btu/adapter_btu_bottom_v32.stl>                |
| Adapter - ball                     | 1      | <https://github.com/Bastardkb/Charybdis/blob/main/files/mods/static-bearing/printable_btu_3.175mm_ball.stl> |

> **Note:** The case files above have the USB connector cutout raised to accommodate microcontroller sockets (headers). The plate files are modified for slider power switches.
