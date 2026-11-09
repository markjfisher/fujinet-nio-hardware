# R2 engineering decisions and review boundary

2026-11-09. R2 supersedes the R1 bus handshake; R1 remains preserved.
This is a concrete A500 circuit candidate. It is not an electrical
sign-off, a layout or a manufacturing release. R0 remains the saved historical
USB/power proposal; this document supersedes its host-form-factor assumptions.

## Product and connector

The first product plugs directly into the **A500's 86-contact expansion edge**
using a female mating connector. The bench used the manufactured PCBWay
100-contact passive breakout, a purchased A500-to-Zorro-II adapter and Dupont
wiring. Those are test infrastructure, not required parts of the final product.
An A2000 100-contact card is a separate future mechanical/electrical variant.

The repository's `Amiga_A500_Expansion_86` logical symbol is reused. Its
associated existing footprint is **male PCB edge fingers**, not a female socket
land pattern. J40 deliberately has no footprint. Do not inherit that footprint
when creating the PCB. The empty A500 template was not evidence of a validated
mating-socket design. TE [1-5530843-0](https://www.te.com/en/product-1-5530843-0.html)
is an 86-position, 2.54mm receptacle candidate, but its customer drawing,
orientation, case clearance, contact numbering and availability still require
mechanical selection. It is not an approved BOM item here.

A500 pin 12 is grounded; the buffer presents this as CFGIN low to RP GPIO43.
Pin 11 has no CFGOUT connection, and there is no A2000-style SLAVE contact.
Unused arbitration, clocks, /OVR and supply contacts are explicit NCs.
XRDY (18) and /BERR (46) are now connected; see the R2 handshake review.
No bus mastering, RAM replacement, expansion passthrough or accelerator is
implemented. Future accelerator work remains outside the first-board circuit.

## Processor circuits and complete allocation

RP2350B is bare silicon. U21 is a W25Q128JVSIQ 16MB QSPI flash; Y20 is the
recommended ABM8-272-T3 12MHz crystal with 15pF loads and 1k drive resistor.
USB has 27-ohm series resistors; SWDIO, SWCLK, RUN, GND and **reference-only**
3.3V are accessible. RP BOOT pulls QSPI_SS down through the existing 1k R23.
Do not add a second series 1k at the processor.

The core regulator has a 3.3uH AOTA-B201610S3R3-101-T inductor, input/output
4.7uF capacitors and the manufacturer's 33-ohm/4.7uF VREG_AVDD filter.
Its marked inductor orientation and reference placement are essential layout
constraints, not optional generic autorouter choices. IOVDD/analog/USB/QSPI
and the three DVDD pads have local decoupling allocations.

| RP GPIO | Signal / function |
| --- | --- |
| 0 | Buffered /AS |
| 1–23 | Buffered A1–A23 |
| 24–39 | D0–D15 via separately enabled receive/transmit buffers |
| 40, 41, 42 | /UDS, /LDS, READ |
| 43 | Buffered A500 CFGIN (grounded at host) |
| 44 | ACK_REQ completion pulse, external pull-down |
| 45 | IRQ_REQ, external pull-down; optional /INT2 sink |
| 46 | BUS_READY, external pull-down; firmware arming condition |
| 47 | DATA_DRIVE read-claim pulse, external pull-down |

The [81-pad CSV](rp2350-pin-allocation.csv) is checked against the native
export. GPIO45/46 differ from R0's CFGOUT_REQ/SLAVE_REQ proposal. Dedicated
pads carry USB, QSPI, RUN and SWD. Physical USB selection uses no GPIO.
There is no RP-to-ESP SPI: GP2–GP7 remain A2–A7 without sharing or multiplexing.
This is a new allocation, not a claim to reproduce the earlier breadboard map.

ESP uses a **surface-mount ESP32-S3-WROOM-1-N16R8 module**, not the bench
carrier. This deliberate first-board choice retains module flash, PSRAM,
crystal and RF matching. Bare ESP silicon would introduce unnecessary RF and
memory-layout work. GPIO35–37 are reserved for octal PSRAM and left unused.
USB uses GPIO19/20 with 22-ohm resistors; GPIO0 and EN join the physical recovery
circuit. GPIO45/46 have download-compatible low straps. GPIO9/10/11/12 serve
microSD MISO/CS/MOSI/CLK, with pull-ups and a clock series resistor. UART0,
BOOT and EN are exposed for service. The USB-only board's main-rail-valid
signal reaches GPIO21 at a safe 3.3V logic level; no ESP pin receives 5V.

## USB, power and recovery

R2 preserves the R0 USB topology: U1 routes RP, U2 routes ESP. Port 1 is the
private pair; port 2 is PC D+/D-. Flash RP disables ESP's mux and holds ESP
reset; Flash ESP does the reciprocal. Both flash selections asserted disable
both muxes and hold both processors reset. No mode shunt leaves the private
USB path selected but cannot arm the bus. Fit exactly one shunt.

**Cold transitions only:** unplug USB power, allow rails to discharge, select
Run/Flash RP/Flash ESP, then reconnect. The circuit has no hot-change reset
sequencer. Selecting Flash forces physical ROM boot independently of either
application. Separate BOOT and RESET buttons remain accessible.

External Type-C is always a **sink**, including Run. RP is host only on the
private internal data link; it never sources external VBUS. FUSB303B supplies
the CC Rd terminations; do not add parallel 5.1k resistors. Its GPIO OUT1 is
pulled up and inverted: no attachment/default current leaves main power off,
1.5A or 3A advertisement enables the load switch. The controller and inverter
use the small always-on 3.3V rail ahead of that switch.

Power path: USB VBUS -> SS34 reverse-blocking diode -> TPS22917 load switch ->
TPS62130 3.3V buck. TPS22917 CT is connected to VIN, with a discharge resistor
from VOUT to QOD. TPS62130 uses 312k/100k feedback (about 3.296V), 2.2uH
inductor and soft start. C7/C8 are now assigned larger 1206 packages, but actual
MPN/effective capacitance still needs selection; package size alone is not
capacitance qualification.

| 3.3V allocation | Peak budget |
| --- | ---: |
| ESP module | 600mA |
| RP, flash, core conversion | 200mA |
| SD | 200mA |
| Bus/control | 100mA |
| Margin | 100mA |
| Total | 1.2A / 3.96W |

Using the R0 conservative 4.5V input, 0.5V diode drop, 0.15V other loss and
85% buck efficiency gives approximately 1.21A input plus the small AON load.
This is a design allocation, not measured demand. Run needs a suitable USB-C
supply; flashing currently requires a **data-capable USB-C port advertising at
least 1.5A**. USB-A/default-current service is not supported by this circuit.

Amiga +5V is only sensed through a 100k/10k divider (about 45uA at 5V).
It is never joined to VBUS, 5V_MAIN or 3V3. Ground is shared. D1 and the load
switch block the intended reverse VBUS path. Local-powered bus drivers are
inhibited when the Amiga is off; their inputs do not have pull-ups to the
local supply on host nets. Ioff-rated devices address board-off/host-on
operation. This establishes the intended steady-state isolation, **not zero
leakage or instantaneous protection during every supply transient**.

Power review remains open: input fuse/overvoltage/CC protection, diode thermal
loss, capacitor DC-bias derating, inrush/current-limit worst cases, insufficient
power indication and FUSB303B GPIO reaction to a live Rp-current downgrade.
The data sheet gives a 10–20ms Rp-change interval, but this alone does not close
the entire power-disable response. No USB compliance or protected-input
release is claimed. These are design-review items, not a request to repeat the
accepted USB feasibility experiment.

## A500 bus circuit and firmware obligations

U40–U43 receive address/control signals. U44/U45 drive the two data bytes;
U46/U47 receive them. These are **SN74LVC541APWR at 3.3V**, represented by
pin-compatible generic 541 symbols. Do not fit 74LS541 or plain 74HC541.
LVC supplies TTL-compatible thresholds, 5V-tolerant inputs and Ioff protection.
Separate transmit/receive buffers avoid changing a transceiver DIR pin while
enabled. The cost is two additional packages compared with the R0 proposal.

TPS3808G01 watches divided host +5V: nominal falling threshold 4.455V, with
20ms reset-release delay when CT is open. SAFE is the AND of host power good,
local buck PG, host reset released, RP RUN released, Run mode, physical BUS
ARM and RP BUS_READY. Hardware gates additionally qualify /AS, address region,
READ, DATA_DRIVE and each byte strobe. All four byte OEs pull high by default;
requests and BUS_READY pull low. XRDY and /INT2 use Ioff-rated open-drain
LVC1G06 outputs, with pull-ups owned by the host, not local 3.3V. /BERR also
qualifies SAFE. /DTACK is an input only; the board never drives it.

Hardware qualifies the $E80000–$EFFFFF I/O region. R2 replaces the erroneous
R1 local-DTACK handshake with hardware XRDY holdoff. Firmware decodes exact
ownership and completes every qualified cycle, including unowned addresses
without driving their data. Two flip-flops discard stale completion/read-claim
levels between cycles. See [the detailed handshake and timing review](bus-review.md)
for the circuit, firmware sequencing and remaining physical qualification.
This first candidate has no expansion passthrough; multi-device coexistence
and accelerators are not qualified. Advertise a non-memory 64KiB I/O board.

The 65,536 static cases and 65,536 five-step latch sequences check logical
behaviour, not analog hazards, timing, metastability or firmware. Read/write
pin direction and minimum pulse/settling times remain firmware obligations.

## Accepted evidence and remaining layout work

The user clarified that the real Amiga captures were not committed. The two
provided screenshots show AutoConfig-triggered bus activity at the physical
breakout. Two analyzers demonstrated access to 32 channels. This is accepted
bring-up evidence; neither finding nonexistent CSVs nor writing a trace parser
is a prerequisite for this circuit. The screenshots do not qualify propagation
or release timing of buffers that were not present. Cross-analyzer timing would
need alignment only if a future measurement relies on it.

RP-host/ESP-device traffic, maximum-capacity packets, reset/fault recovery and
independent ROM flashing through the shared connector are accepted as recorded
in the firmware USB-host bench ledger. No corrupted firmware campaign or repeat
USB-feasibility test is requested.

Before PCB construction: close the electrical items above, select the mating
socket and envelope, finish footprint/BOM choices and cross-check packages,
then establish a four-layer stackup with a continuous ground plane. Apply the
ESP antenna keepout, RP core regulator reference placement, short local supply
loops and service-control access. Establish 90-ohm USB pair geometry from the
actual stackup. Generic autorouting is only for ordinary nets after critical
routes and mechanical constraints are protected and independently checked.

## Primary technical sources

- [Raspberry Pi hardware design guide](https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf), revision 2: core regulator/inductor orientation, crystal, flash, USB and decoupling.
- [RP2350 data sheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf): B package and dedicated pins.
- [ESP32-S3-WROOM module data sheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) and [schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html).
- [TI LVC541A](https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf), [LVC1G06](https://www.ti.com/lit/ds/symlink/sn74lvc1g06.pdf), [TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf).
- [onsemi FUSB303B](https://www.onsemi.com/download/data-sheet/pdf/fusb303b-d.pdf), GPIO table and Rp-change timing. Remaining USB/power sources are linked in [R0](../integrated-r0/proposal.md#manufacturer-references).
- [Commodore A500/A2000 technical reference scan](https://erikarn.github.io/amiga/docs/Amiga_500_Technical_Reference.pdf), 86-pin connector discussion, printed pages 87–99. The printed page 229 equations are **A2000 PAL equations**, not an A500 Gary specification.
- [Commodore expansion-connector table](https://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/node00FE.html), alongside the repository's reviewed [86/100-pin comparison](../docs/expansion-to-zorro-pin-map.md).
