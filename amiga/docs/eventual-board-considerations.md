# Eventual Board Considerations

For the current prototype, separate USB connections to the RP2350 and ESP32-S3 development boards are fine and convenient for flashing.

For the eventual integrated board, where both devices will be bare SMD parts rather than dev boards, programming and recovery access should be designed in deliberately.

## RP2350 programming/debug access

Provide:

- Native USB connection to the RP2350 USB D+/D− pins.
- A way to enter BOOTSEL/UF2 mode.
- Accessible RESET/RUN control.
- SWD access for recovery/debugging:
  - SWDIO
  - SWCLK
  - GND
  - 3V3
  - optionally RUN

Even if normal firmware updates are done over USB, SWD pads/header should still be present as a recovery path.

## ESP32-S3 programming/debug access

Provide:

- Native USB D+/D− connection for flashing/debugging.
- EN/RESET access.
- GPIO0/BOOT access so the ROM bootloader can always be entered.
- Optional JTAG/debug pads.

The ESP32-S3 USB Serial/JTAG capability should make USB flashing/debugging straightforward without needing a separate USB-to-UART bridge.

## USB connector strategy

For the prototype:

```text
USB -> RP2350 dev board
USB -> ESP32-S3 dev board
```

For the final board, possible designs include:

```text
USB-C #1 -> RP2350
USB-C #2 -> ESP32-S3
```

This is simple, but probably unnecessary on a finished product.

A cleaner final arrangement would likely be:

```text
Single external USB-C connector
        |
        +--> normal device power/data path
```

with separate internal/test pads for programming, debugging and recovery.

If a shared USB connector is intended to program both processors, some deliberate switching, muxing, hub, or boot-routing design will be required.

## RP2350 ↔ ESP32-S3 interconnect pin-budget gate

**Do not freeze a schematic or PCB layout until this has been resolved.**

The currently working RP2350 ↔ ESP32-S3 SPI wiring is a two-development-board
laboratory fixture, not an eventual-board pin assignment.  Its RP2350 pins
GP2–GP7 are used for SCLK, MOSI, MISO, CS, `READY`, and `DATA_AVAILABLE`.
In the currently proposed Zorro-facing mapping, GP2–GP7 are already assigned
to Amiga address lines A2–A7.  They cannot be copied to the integrated board
or electrically shared with the Zorro bus.

Before selecting the production link ABI or finalising RP2350 bus routing:

- Make a complete RP2350 GPIO budget, including Zorro address/data/control,
  reset/debug, and all interprocessor signals.
- Reserve dedicated, electrically isolated pins for the selected RP2350 ↔
  ESP32-S3 transport.  SPI needs SCLK, MOSI, MISO, and CS; the feasibility
  fixture also uses two ESP-to-RP flow-control signals (`READY` and
  `DATA_AVAILABLE`).
- Decide, from the link-feasibility evidence, whether the production protocol
  can safely reduce or replace those flow-control wires.  Do not assume that
  it can.
- Record the chosen pinout, reset/boot ownership, and any intentional mux or
  isolation circuitry in the schematic review before layout.

The pin scarcity is a design decision to resolve, not evidence that SPI has
already been ruled in or out.  A direct shared connection to Zorro address or
data nets is not an acceptable shortcut.

### Current-map observation

The Core2350B mapping under review assigns GP0–GP46 to Zorro or board-level
signals; GP47 is the only visibly uncommitted GPIO/test point.  GP2–GP7 are
not spare: they carry A2–A7.  The integrated bare-RP2350 schematic may make
different choices (for example, it need not retain a development-board
`LOWBAT` signal), but it must not claim spare GPIOs without a reviewed,
signal-by-signal budget.  As drawn, there are not enough dedicated RP GPIOs
for the six-wire SPI feasibility fixture.

### Candidate solutions

1. **Recommended baseline: internal USB link.**  Use RP2350 USB in host mode
   and ESP32-S3 USB-OTG in device mode, connected by D+, D−, VBUS and GND.
   The ESP exposes a CDC-ACM or vendor-bulk packet endpoint; the RP is the
   sole host.  This consumes the chips' dedicated USB pads rather than the
   exhausted RP GPIO budget, and USB supplies framing, flow control and
   integrity handling.  It does require an explicit programming/recovery
   design: that USB port cannot at the same time be the PC-facing port for
   either chip.  Retain RP SWD/RUN and ESP EN/GPIO0/USB service pads, and
   choose a USB switch or an intentional service connector if PC flashing is
   required through one external connector.

2. **Keep SPI by redesigning the Zorro front end.**  Put Zorro capture,
   buffering and address/decode work in a small CPLD/FPGA or dedicated bus
   interface with the necessary 5 V-tolerant buffers.  Present the RP2350
   with a narrower local FIFO/register interface, freeing RP GPIOs for a
   dedicated SPI link.  This is the robust SPI route, but it is a real board
   architecture change with extra silicon and verification work; it is not a
   late pin swap.

3. **Use a lower-pin-count serial transport only after measurement.**  A
   point-to-point UART uses TX/RX; I²C uses two wires.  Either could fit if
   the final GPIO budget releases two pins, with packet framing, sequence
   numbers and backpressure implemented in the protocol.  They are not
   substitutes for the demonstrated SPI throughput/recovery properties until
   tested at required packet rates.  A three-wire/no-CS SPI variant is also
   only viable if the chosen ESP slave implementation has a reliable framing
   and recovery mechanism without chip select.

4. **Do not time-multiplex Zorro nets with the ESP link as the default
   solution.**  Bus switches and strict idle-window arbitration may be
   theoretically possible, but they add contention, timing and missed-cycle
   risks to a real-time bus interface.  Consider them only if a complete bus
   isolation/capture design proves it, effectively converging on option 2.

**Decision recommendation:** make the internal USB link the next architecture
spike and keep USB service/recovery pads.  In parallel, perform a final-board
GPIO audit.  If production requirements demand SPI rather than USB, choose
the Zorro-front-end redesign deliberately; do not expect the present direct
GPIO map to grow the required pins.

## Independent recovery

It may be useful for one processor to control the other's reset/boot pins, for example:

```text
RP2350 -> ESP32-S3 EN / GPIO0
```

or vice versa.

However, independent physical recovery access should still exist.

Do not create a design where broken firmware on one processor prevents the other processor from being reflashed.

Suggested service/test access:

```text
RP2350:
    3V3
    GND
    SWDIO
    SWCLK
    RUN

ESP32-S3:
    3V3
    GND
    EN
    GPIO0
    USB D+
    USB D-
```

These could be unpopulated headers, pogo/test pads, Tag-Connect-style footprints, or another compact service interface.

## Physical board requirements

The eventual board will likely need:

- Rear-accessible USB-C connector.
- Accessible microSD card slot.
- A small number of user-accessible buttons for ESP32 firmware functionality.
- ESP32 BOOT/RESET functionality where appropriate.
- RP2350 BOOTSEL/RESET access, potentially hidden or service-only.
- Programming/debug pads for both processors.
- A recovery route that does not depend on either processor already running valid firmware.

## Power

The final RP2350/ESP32-S3 board should only need a suitable 5 V USB supply, with the PCB generating the required local 3.3 V rails.

The A500-Zorro adapter's auxiliary floppy-power input is therefore not necessary for the prototype or necessarily for the final design.

The final board can instead use its own USB-C power input, which also has the advantage that the RP2350 and ESP32-S3 can remain powered while the Amiga itself is power-cycled.

That behaviour may be useful during development and may also simplify firmware/update/recovery behaviour in the finished device.

---

## Optional Accelerator Capability

The eventual FujiNet board should leave room for a future optional accelerator module without making acceleration a requirement of the first production revision.

The preferred approach is to expose a dedicated high-speed accelerator header/interface rather than designing a specific Raspberry Pi model directly into the base board.

Conceptually:

```text
A500 expansion bus
        |
        v
+----------------------+
| FujiNet base board   |
|                      |
| RP2350 / bus logic   |
| ESP32-S3             |
| storage/networking   |
+----------+-----------+
           |
           | accelerator header
           |
           v
+----------------------+
| Optional accelerator |
|                      |
| Raspberry Pi 3A+     |
| or future equivalent |
|                      |
| Emu68 / 68k runtime  |
+----------------------+
```

The base board should remain fully functional with no accelerator fitted.

### Goals

The optional accelerator capability could eventually provide:

- 68k CPU acceleration/emulation.
- Fast RAM.
- Possible FPU functionality through the emulated CPU environment.
- Potential future RTG or other Pi-assisted hardware features.
- Tight integration with FujiNet storage, including the planned `fujinet-hd.device`.
- A combined external expansion experience similar in spirit to historical devices such as the GVP A530:
  - CPU acceleration.
  - Mass storage.
  - Additional system capability in one external unit.

### Division of responsibility

The Raspberry Pi should not be responsible for hard real-time Amiga bus timing.

A more appropriate division is:

```text
Amiga bus
   |
   v
RP2350 / CPLD / FPGA
   |
   | deterministic bus handling
   | arbitration
   | timing-sensitive interface
   |
   v
fast local interface
   |
   v
Raspberry Pi
   |
   | 68k emulation
   | Fast RAM services
   | accelerator functions
   | possible RTG / future expansion
```

The ESP32-S3 remains responsible for FujiNet networking/storage/application functionality.

This keeps the hard real-time bus work separate from the higher-level processor emulation.

### Accelerator module choice

A Raspberry Pi 3A+ class device is a reasonable initial target:

- Compact.
- Relatively low power.
- Already proven in PiStorm-style applications.
- Sufficiently powerful for substantial 68k acceleration.

A Pi 4 or Pi 5 could potentially be supported later, but the base-board interface should not depend on a particular Raspberry Pi generation or mechanical form factor.

The accelerator interface should therefore be treated as a stable board-to-board contract rather than as a direct "Pi socket".

### Signals to preserve

The base board should avoid discarding signals that could be needed for future bus-master or accelerator functionality.

At minimum, consideration should be given to exposing the following through the accelerator interface:

```text
Address:
    A1..A23

Data:
    D0..D15

Bus control:
    /AS
    /UDS
    /LDS
    R/W
    /DTACK

Bus arbitration:
    /BR
    /BG
    /BGACK

System control:
    /RESET
    /HALT

Clock/timing:
    relevant 7 MHz / CPU / bus clocks

Power:
    +5V
    +3V3 where useful
    GND
```

The exact required signal set should be determined before committing the final header pinout.

### Bus-master capability

An external accelerator is fundamentally different from an ordinary Zorro peripheral.

A PiStorm-style CPU replacement normally sits directly on the 68000 bus in place of the original processor.

An accelerator connected through the A500 expansion interface would instead coexist with the motherboard 68000 and therefore needs a deliberate mechanism for obtaining ownership of the bus.

The design should preserve the signals required for proper bus arbitration:

```text
accelerator requests bus
        |
        v
       /BR
        |
        v
68000 grants bus
        |
        v
       /BG
        |
        v
accelerator acknowledges ownership
        |
        v
     /BGACK
```

This should be treated as future architectural work rather than assumed to work merely because the A500 expansion connector exposes much of the 68000 bus.

### Physical interface

The accelerator interface should preferably be:

- A compact board-to-board or mezzanine header.
- Mechanically keyed if practical.
- Documented as a stable internal hardware interface.
- Located so an accelerator daughterboard can fit inside a future enclosure.
- Capable of carrying the required bus signals with sensible ground distribution.
- Designed with enough signal-integrity margin for the expected bus/interface speed.

Avoid using a loose Dupont-style header for the final design.

Possible implementation choices could include:

- dual-row board-to-board connector,
- mezzanine connector,
- high-density pin header,
- another mechanically robust internal connector.

The exact connector should be selected only after the required signal count and expected interface speed are known.

### Independent base-board operation

The accelerator must remain optional.

With no accelerator installed:

```text
A500
 |
 +--> FujiNet RP2350
 |
 +--> ESP32-S3
 |
 +--> SD / networking / fujinet-hd.device
```

With an accelerator installed:

```text
A500
 |
 +--> FujiNet bus interface
          |
          +--> ESP32-S3 / FujiNet services
          |
          +--> accelerator module
                  |
                  +--> Raspberry Pi / Emu68
```

No core FujiNet functionality should depend on the accelerator module being present.

### Power considerations

The accelerator connector should account for the potentially significant current requirements of a Raspberry Pi class device.

The final design should not assume that the A500 expansion port alone should supply that load.

A likely arrangement is:

```text
external USB-C 5V supply
        |
        +--> FujiNet base board
        |
        +--> RP2350
        |
        +--> ESP32-S3
        |
        +--> optional accelerator module
```

Power sequencing and back-powering must be considered carefully, particularly because the FujiNet/accelerator hardware may remain powered while the Amiga itself is switched off or power-cycled.

The design should ensure that powered external logic cannot unintentionally feed current back into an unpowered Amiga through bus signal pins.

### Future investigation

Before committing the production-board accelerator header, investigate:

- Exact A500 expansion-bus arbitration behaviour.
- Whether `/BR`, `/BG`, `/BGACK`, `/HALT`, and `/RESET` are sufficient for the intended accelerator architecture.
- Electrical buffering or level translation required between the Amiga bus and modern 3.3 V logic.
- Whether an RP2350 is sufficient as the deterministic bus front-end or whether a CPLD/FPGA should be added.
- Suitable high-speed communication mechanism between bus front-end and Raspberry Pi.
- Compatibility possibilities with Emu68.
- Whether existing PiStorm software can sensibly be adapted or whether a FujiNet-specific accelerator architecture is preferable.
- Power sequencing and unpowered-bus isolation.
- Mechanical space and cooling requirements.
- Whether Fast RAM and other accelerator resources should appear as native Zorro resources, CPU-local resources, or a combination.

The first production board does not need to implement acceleration, but it should avoid making future acceleration unnecessarily difficult.
