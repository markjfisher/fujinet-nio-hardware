# Integrated R0 circuit proposal

2026-11-09. **Candidate, not a released board or fabrication package.**

The implemented schematic is the USB/power/recovery circuit. J3 and J4 are
temporary integration boundaries, not a proposal to connect development boards
with long USB leads. The processor support circuits, buffered Zorro interface
and edge connector are not yet implemented in this candidate. The following
table distinguishes decisions from completed CAD. No PCB has been generated.

| ID | Requirement | Chosen implementation | Evidence / check | Remaining decision |
| --- | --- | --- | --- | --- |
| U1 | Run / Flash RP / Flash ESP through one USB-C | Two TS3USB30EDGSR muxes, independently enabled; physical three-position shunt selector | Saved schematic; exported net membership and four-state switch truth table | Enclosed, keyed selector mechanics |
| U2 | Recovery independent of either application | Separate BOOT and RESET buttons; selector forces selected BOOT and holds peer reset | Q1–Q4 and SW1–SW4; accepted physical ROM-entry evidence | Integrate RP QSPI and ESP GPIO0/EN at the processor sheets |
| P1 | Defined power, current and CC | USB-C sink only; FUSB303B requires advertised 1.5 A or 3 A; TPS22917 feeds 3.3 V buck | Manufacturer pin tables; rail budget below | Confirm GPIO current-change response and tolerances in detailed power review |
| P2 | No host or Amiga back-power | No Amiga supply input; series diode and reverse-blocking load switch; bus Ioff and hardware OE interlock | Schematic rail separation; proposed bus equations below | Implement and check bus interlock before any active attachment |
| G1 | Complete RP budget without SPI/address overlap | RP2350B, 48 GPIO assigned below; native USB pads; physical controls use no GPIO | `rp2350-pin-allocation.csv`, 81 package pads accounted for | Reconcile original active schematic when located; this is a revised proposal |
| Z1 | Safe bus operation and local cycle service | LVC receive/data buffers, independent byte OEs, open-drain response; PIO services local mailbox | Existing C5/C7/C8 functional evidence only; timing ledger below | Actual 32-channel trace locations and numerical timing closure |
| M1 | Preserve connector and route critical nets deliberately | Reuse reviewed passive connector geometry in a new four-layer project; continuous ground plane | Existing passive mechanical review | Freeze circuit, component packages, stackup and USB geometry before placement |

## USB paths and physical controls

U1 common pins 4/6 join RP D+/D−; U2 common pins 4/6 join ESP D+/D−.
Both switches' port 1 pins 2/8 join the private LINK pair. Both port 2 pins 3/7
join the PC pair. U1 S=FLASH_RP and /OE=FLASH_ESP; U2 S=FLASH_ESP and
/OE=FLASH_RP. These are **active-high flash selections**, pulled down by 10k.
No processor owns selection, and no SPI or READY/DATA_AVAILABLE wire exists.

| J2 shunt | FLASH_RP | FLASH_ESP | Data connection | Reset / boot |
| --- | --- | --- | --- | --- |
| 1–2: Run | 0 | 0 | RP ↔ ESP; PC isolated | Both normal; RUN_MODE enables bus interlock |
| 3–4: Flash RP | 1 | 0 | PC ↔ RP; ESP isolated | ESP held reset; RP BOOTSEL forced |
| 5–6: Flash ESP | 0 | 1 | PC ↔ ESP; RP isolated | RP held reset; ESP GPIO0 forced low |
| Both flash shunts, invalid | 1 | 1 | Both muxes disabled | Both processors held reset |

No shunt leaves the private USB path selected but RUN_MODE low, so the future
Zorro drivers must remain disabled. Fit exactly one shunt. More than one shunt
is not a supported operating mode. A physical selector could replace this
header after its contact truth table and footprint are checked.

**Cold mode changes only:** unplug USB, wait for 3.3 V to discharge, move the
shunt, then reconnect. Do not promise hot switching: a running RP host must
not be switched onto PC D+/D− before reset. The first board uses this explicit
power-off transition procedure; a hot-change reset sequencer is not implemented.
For recovery, select the desired Flash position and power up; alternatively
hold its BOOT button while pressing and releasing RESET. Restore Run with USB
unplugged. The peer's application is irrelevant to both ROM entry paths.

RP_BOOT_N at J3.5 goes to QSPI_SS. R13 is the 1k isolation resistor in its
pull-down path; do not put another 1k in series by accident. RP_RUN is the
dedicated RUN pad. ESP_BOOT_N joins GPIO0; ESP_EN joins CHIP_PU/EN. ESP GPIO46
must retain its download-compatible strap. Use 27Ω series resistors at RP USB
pads and the Espressif-recommended 22Ω starting values at ESP pads, not at these
temporary interface symbols. Retain accessible RP SWDIO/SWCLK/RUN/GND and
3.3 V **reference-only** pads; ESP UART0/EN/GPIO0/GND remain service pads.

The external connector is always a Type-C power sink, including Run when the
RP is the **internal** USB host. Never change CC to source just because RP's
internal controller is a host. No hub and no external VBUS-source FET are needed.
The ESP is self-powered by the board's 3.3 V rail. Its internal-link VBUS-valid
condition follows main power; GPIO21 is reserved for a gated VBUS-valid signal
in the ESP sheet. Never connect 5 V directly to an ESP GPIO. A detached PC
cannot leave this USB-only board powered. Do not add an auxiliary/debug power
feed without revisiting both data and VBUS isolation.

## Power and backfeed

Path: J1 VBUS → SS34 D1 → VBUS_PROTECTED → TPS22917 U4 → 5V_MAIN →
TPS62130 U5 → 3V3. AP2112K supplies only 3V3_AON for the CC controller and
inverter ahead of U4. U3 is GPIO-mode, sink-only: PORT has a 100k pulldown,
ADDR floats, EN is grounded, VBUS_DET has the specified 887k series resistor.
The controller supplies the two CC Rd terminations; **do not add external
5.1k resistors in parallel**. OUT1 low means at least 1.5 A and is inverted
to enable U4. No firmware participates in granting main power.

U4's 1nF CT capacitor joins **VIN**, not ground. Its 1k QOD resistor provides
controlled discharge. C7 is behind the slew-controlled switch. R7/R8 set the
buck to approximately 3.296 V from its 0.8 V reference; DEF and FSW are low,
SS is 3.3nF, L1 starts at 2.2µH with saturation rating at least 4 A. The 22µF
output capacitor needs its effective capacitance checked at bias; its current
0603 assignment is provisional and is **not an approved procurement choice**.
Add local processor decoupling and the RP core regulator network separately.

| 3.3 V load | Reserved peak current |
| --- | ---: |
| ESP32-S3, RF and memory | 600 mA |
| RP2350B, flash and core conversion | 200 mA |
| microSD | 200 mA |
| Bus buffers, control and indicators | 100 mA |
| Design margin | 100 mA |
| **Total design allocation** | **1200 mA / 3.96 W** |

These are allocations, not measured consumption. Assuming 4.5 V at J1,
0.5 V diode drop, 0.15 V switch/wiring loss and 85% buck efficiency gives
3.96/(3.85×0.85) = **1.21 A**, plus the small AON load. This fits a 1.5 A
advertisement with about 0.28 A reserve. Verify actual transient demand,
diode thermal loss and worst-case regulator efficiency before freezing parts.
No accelerator load is included. Do not power one from this budget.

This choice intentionally requires a data-capable USB-C PC/hub port advertising
at least 1.5 A for flashing. Legacy USB-A/default-current ports leave the main
rail off; they are not silently assumed to provide the running-board current.
An indication for insufficient power is still to be added. Supporting legacy
ports would require a separately budgeted service-power mode or auxiliary
power input; neither is implied by this candidate.

D1 blocks a sustained reverse path into J1; U4 also has reverse-current
blocking. Real parts have leakage and reverse-blocking activation transients:
this is not a claim of zero current under every fault. There is no electrical
join between Amiga +5V and any board supply. Amiga +5V is used only for a
high-impedance host-power monitor in the proposed bus circuit. Ground is common.
USBLC6 protects the PC pair; final CC/VBUS protection, input fuse/overvoltage
protection and connector MPN remain detailed-design items. The candidate must
not be treated as a finished protected power input just because ERC passes.

FUSB303B was selected over TUSB320 after reviewing the latter's attachment-only
GPIO current indication. FUSB303B specifies Rp-change detection at 10–20 ms.
The exact GPIO downgrade behavior must be confirmed from the full device state
machine or manufacturer before power sign-off. Do not infer it solely from an
interrupt-register bit or treat this candidate as USB compliance certification.

## RP2350B allocation and Zorro circuit decision

The CSV lists every GPIO and every dedicated pad. Its intended assignment is:
GP0=/AS; GP1–23=A1–23; GP24–39=D0–15; GP40=/UDS; GP41=/LDS; GP42=READ;
GP43=/CFGIN; GP44=ACK_REQ; GP45=CFGOUT_REQ; GP46=SLAVE_REQ; GP47=DATA_DRIVE.
Thus GP2–7 remain address inputs. USB uses pads 66/67. Physical selection,
VBUS qualification, BOOT, reset and SWD need no GPIO. There are no spare GPIOs.
This deliberately revised map must not be represented as the unlocated earlier
Core2350B map. It is not compatible with the W1 synthetic fixture mapping.

First-board bus proposal: four SN74LVC541A receive buffers for 23 address bits,
strobes, READ, /CFGIN and reset observations; two SN74LVC245A data transceivers,
one per byte lane. All run at 3.3 V, accept 5 V inputs, and specify Ioff for
the board-off/Amiga-on case. Their TTL input threshold is the reason for this
choice. **Do not substitute SN74LVC8T245 with its bus side powered at 5 V
without checking VIH:** a nominal 5 V translator does not automatically accept
the Amiga's guaranteed TTL high level. A 3.3 V LVC output must be checked against
the actual Zorro loading and receiver VIH; no analog margin is claimed here.

Bus-side pulls must reference Amiga power, never always-on board power. No
board pull-up is permitted on a bus signal while the Amiga is off. Receive
buffers cannot drive the bus. Data OE defaults high with 10k to local 3.3 V;
DATA_DRIVE, ACK_REQ, CFGOUT_REQ and SLAVE_REQ have explicit external pulldowns.
Bus arming is a physical normally-open service jumper, independent of RP GPIO.

Implement the following in discrete hardware, not an ARM task:

* SAFE = host-power-good AND local-power-good AND host-reset-released AND
  RP-RUN-released AND RUN_MODE AND physical BUS_ARM.
* DRIVE_LO = SAFE AND DATA_DRIVE AND READ AND !/AS AND !/LDS.
* DRIVE_HI = SAFE AND DATA_DRIVE AND READ AND !/AS AND !/UDS.
* Enable the selected data lane only while its corresponding DRIVE is true;
  direction changes occur while both OEs are high. Receive during qualified
  writes, without enabling an RP-to-bus output. Treat turn-around as a separate
  sequenced operation, not merely DIR=READ with continuously asserted OE.
* /DTACK uses an open-drain sink qualified by SAFE, ACK_REQ, active /AS and an
  active lane. /SLAVE and /CFGOUT need their separately reviewed Zorro timing
  and electrical semantics; do not simply tie /SLAVE to /DTACK.

Use an always-local-powered comparator/supervisor watching divided Amiga +5V
to inhibit outputs below its valid range and while host power ramps. Reset
also inhibits OE directly. A firmware output stuck high must still be cut off
by /AS, the lane strobe, host reset or power loss. The comparator threshold,
hysteresis, maximum disable delay and gate implementation are not frozen until
the existing timing evidence is located. This is the principal remaining bus
circuit decision; it does not invalidate the accepted USB feasibility.

SLAVE_REQ is independent of ACK_REQ so their assertion times can differ.
Moving bus arming to a physical interlock preserves all address pins and leaves
the 48-GPIO budget complete. The output requests remain pulled down during
reset and boot. This allocation does not establish the numerical timing needed
to freeze layout.

Mailbox cycles finish locally from RP SRAM/PIO state. USB completion becomes
status observed by later Amiga accesses; never hold a Zorro cycle until an ESP
response. Byte writes must merge only the selected lane; word accesses require
both strobes. The packet transport remains the accepted USB PacketLink with
capacity negotiation and no automatic replay after unknown completion.

## Evidence and physical layout boundary

The passive breakout was read through the live MCP (13 components, 230 wires)
without saving it. Its reviewed 100-contact map and connector geometry remain
the source for a later candidate PCB. Native file inventories, including ignored
files, and the workspace/hardware/firmware/core2350-test/DIEGO-500 repositories
were checked. The actual earlier active schematic and 32-channel captures have
not been located. The separate local `kicad-test/test-fujinet` file contains only
an A500 connector and is not that schematic.

The available [synthetic ledger](../../../fujinet-nio/bridges/rp2350-zorro/docs/feasibility/bench-evidence.md)
indexes C0–C9 at 1 MHz. C5 supports functional qualified writes; C7/C8 support
preloaded replies and direction sequencing. None establishes analog release
time or real Zorro setup/hold margin. The [USB ledger](../../../fujinet-nio/bridges/rp2350-zorro/lab/usb-host/VERIFICATION.md)
supports proceeding with the internal link and ROM recovery. No tests were
repeated and no corrupted firmware is requested. The next evidence action is
to locate existing captures, not commission a replacement experiment.

Plan four layers: components/signals, uninterrupted ground, power/slow signals,
signals. Preserve the released edge-contact geometry but copy it only into the
new project. Keep the ESP RF antenna at the board boundary with the module's
specified all-layer keepout, or use the bare-chip RF reference design if bare
silicon is retained. ESP package/module selection is still open; the bench's
WROOM-1 N16R8 is evidence, not an automatic final BOM decision.

Require 90Ω differential USB geometry from the chosen fabricator stackup,
short symmetric switch paths, adjacent ground return, and controlled stubs at
the PC fan-out. Constrain the private and PC pairs before ordinary routing.
Do not send the USB pairs through generic autorouting and call them qualified.
No placement, routing, PCB DRC, schematic/PCB parity or manufacturing approval
is claimed for this schematic-only candidate.

## Manufacturer references

* [TI TS3USB30E](https://www.ti.com/lit/ds/symlink/ts3usb30e.pdf): DGS pinout,
  enable/select truth table, Ioff, operating range and layout guidance.
* [onsemi FUSB303B](https://www.onsemi.com/download/data-sheet/pdf/fusb303b-d.pdf):
  GPIO sink configuration, OUT1/OUT2 current decoding, VBUS detection and timing.
* [TI TPS22917](https://www.ti.com/lit/ds/symlink/tps22917.pdf): pin table,
  VIN-referenced CT, QOD, reverse blocking and its limits.
* [TI TPS62130](https://www.ti.com/lit/ds/symlink/tps62130.pdf): feedback,
  soft-start, compensation/component selection and power layout.
* [TI LVC245A](https://www.ti.com/lit/ds/symlink/sn74lvc245a.pdf) and
  [LVC541A](https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf): input thresholds,
  5 V tolerance, Ioff and switching limits.
* [Raspberry Pi RP2350 resources](https://pip.raspberrypi.com/categories/1214-rp2350):
  package allocation, bare-chip hardware reference and recovery design.
* [Espressif schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html):
  supply provision, USB pins/resistors, strapping and reset requirements.
