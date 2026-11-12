# FujiNet A500 — requirements and implementation rationale

**Shareable requirements baseline, 2026-11-12.** Describes the integrated R5
design through `16fc4b17`. Requirements below describe intended behaviour;
implementation means present in the design, not electrically qualified hardware.
R5 has approved placement but is unrouted and is not fabrication-ready.

This document consolidates the current decisions scattered through the design
reviews. It separates required behaviour from our RP2350/discrete-logic solution
so another implementation, including an FPGA, can be compared fairly. It adds
no new circuit requirements. Earlier revision reports remain historical evidence;
their old component references and “pending review” notices are not current status.

## Product and functional division

The board is a FujiNet networking/storage peripheral for a stock Amiga A500,
connecting directly to its 86-contact expansion edge. It is a horizontal sidecar
extending left of the machine, not an upright card or a development-board carrier.
The purchased A500-to-Zorro-II adapter and passive breakout are bench equipment,
not parts of the final product.

```text
A500 86-pin bus
    ↕
5 V-compatible receivers / separately enabled data drivers
    ↕                  ↑ hardware qualification and output disable
RP2350B + PIO          address/cycle logic, latches, rail supervision
    ↕ dedicated USB host/device link
ESP32-S3 module
    ├── Wi-Fi / FujiNet networking and application services
    ├── microSD storage
    └── NET and DISK indicators

External USB-C → protected power → main 3V3 / processors / PWR indicator
              → selectable PC flashing path to either processor
Amiga 5 V → current-limited host-interface rail + host-power sensing
```

The RP handles the local, time-sensitive bus interface. ESP networking or card
latency must not determine how long an Amiga bus cycle lasts. Higher-level
requests are transferred through local buffering/mailbox handling and the
interprocessor link. PIO is our chosen deterministic execution mechanism; it
is not itself a requirement that an FPGA implementation must reproduce.

## Requirements mapped to R5

| ID | Requirement and reason | R5 implementation | Evidence / qualification remaining |
|---|---|---|---|
| R1 | Direct, mechanically supported A500 connection; keep keyboard access clear. | J40, WING TAT ED86BGFBK-based horizontal socket assembly; approximately 111 × 117 mm PCB, mounting holes and enclosure clearances. | [Connector geometry](../integrated-a500-r4/implementation.md#a500-connector), [86-pin map](expansion-to-zorro-pin-map.md). Tail forming, mating height and enclosure fit still need physical qualification. |
| R2 | Deterministic peripheral access using address, data and byte strobes; support discovery/configuration and packet/register transactions. | U20 bare RP2350B, PIO-oriented bus firmware contract, A1–A23, D0–D15, AS, UDS/LDS and read/write signals. Hardware selects the coarse E80000–EFFFFF window; firmware distinguishes owned accesses. | [Pin allocation](../integrated-a500-r4/rp2350-pin-allocation.csv), [bus contract](../integrated-a500-r2/bus-review.md). Final R5 firmware and active bus timing remain to be validated. |
| R3 | Correct A500 acknowledgement, including fast wait assertion, without contending with motherboard DTACK. | Hardware asserts XRDY; the A500 generates DTACK, which this board only receives. U84 completion latch releases the wait; hardware assertion does not wait for firmware. | [Handshake rationale](../integrated-a500-r2/bus-review.md). Updated [Phase 1 budget](../integrated-a500-r4/review/component-optimisation/phase1-status.md): 44.7 ns allocated address path against 60 ns, not a measured result. |
| R4 | Drive only the correct read byte lanes, never drive write cycles, and reject stale requests across cycles. | U86 read-claim latch, U84 completion latch, byte qualification and separate TX/RX enables. Reset, BERR, mode, arm and firmware readiness qualify operation. | [Bus contract](../integrated-a500-r2/bus-review.md). Firmware must observe data setup/hold and fresh request edges; hardware cannot correct an incorrect RP GPIO direction. |
| R5 | Interface modern 3.3 V circuitry to the 5 V host and isolate inactive drivers. | Eight SN74LVC541A packages U40–U47: four address/control receivers and two TX/RX pairs for the 16-bit data bus; specified input tolerance, output enables and partial-power behaviour. | [Buffer functions and pin nets](../integrated-a500-r5/review/bus-buffers/report.md). Actual host loading, thresholds, turnaround and signal integrity need routed/prototype checks. These are not eight independent application functions. |
| R6 | Release data, XRDY and IRQ during invalid power, reset or unsafe operation, independently of application firmware. | Three MIC2790H supervisors monitor host 5 V, main 3V3 and 3V3_BUS. U92 produces BUS_DISABLE/BUS_PERMIT; data-buffer OE override and U93/U94 low-or-high-impedance XRDY/IRQ outputs enforce permission. Hold-up capacitors preserve the shutdown interval. | [Implemented protection and power-state table](../integrated-a500-r4/review/component-optimisation/bus-output-disable-proposal.md). Bounded 3 µs shutdown calculation requires ramp/brownout/load measurements; it is not a guarantee against arbitrary hard shorts. |
| R7 | Released, slow or noisy control edges must not feed unsuitable standard CMOS inputs. | Schmitt conditioning of reset, mode/arm, firmware requests and selected host controls; biases establish defaults. Separate domains retain separate conditioning where required. | Same [protection record](../integrated-a500-r4/review/component-optimisation/bus-output-disable-proposal.md). Preserve polarity, threshold and timing assumptions during routing. |
| R8 | Supply processors independently of the Amiga; avoid backfeeding either power source or an unpowered host. | USB-C powers the main regulator and processors. Amiga 5 V supplies only sensing and a small limited interface rail: TPS2553 → isolation diode → AP2112 → 3V3_BUS. No TPS2121 dual-source main supply. | [Power limits](../integrated-a500-r4/review/component-optimisation/bus-output-disable-proposal.md): 300 mA host allowance, ≤100 mA interface allocation, 173.7–233.9 mA sustained limiter range. Main 3V3 allocation was 1.2 A before the LED allowance; confirm combined load/inrush/thermal behaviour. |
| R9 | Safe USB-C power admission and protected local rails. | CC/current-advertisement detection, input protection/current limiting, reverse blocking, buck conversion, bulk storage and per-pin bypassing. Normal operation requires a suitable USB source advertising at least 1.5 A. | [Power design review](../integrated-a500-r3/power-review.md), later protection updates above. A generic PC port is not automatically a sufficient source for full-load operation. |
| R10 | Reliable RP↔ESP packet transport without sharing pins with the Amiga bus. | RP dedicated USB host ↔ ESP USB device. All 48 RP GPIOs have assignments; dedicated USB/QSPI/SWD pins avoid the old SPI/address-pin conflict. | [Pin allocation](../integrated-a500-r4/rp2350-pin-allocation.csv), [link rationale and accepted bench evidence](eventual-board-considerations.md#rp2350--esp32-s3-interconnect-pin-budget-gate). Link/recovery feasibility is demonstrated; integrated switch/PCB behaviour still needs validation. |
| R11 | Flash either processor through one USB-C connector and recover without either application working. | U1/U2 TS3USB30E muxes; physical J2 Run / Flash RP / Flash ESP selection; independent RP and ESP BOOT/RESET switches SW1–SW4. Run connects RP↔ESP and isolates PC data; flash connects PC to the selected processor and isolates its peer. | [Mux topology](../integrated-a500-r5/review/usb-mux/report.md), [service controls](../integrated-a500-r5/review/service/report.md). Normal communication stops during flashing; validate assembled switching and mode transitions. |
| R12 | Provide networking/application processing and removable local storage independently of bus timing. | U30 ESP32-S3-WROOM-1-N16R8 module with integrated RF/memory support; J30 microSD in SPI mode, pull-ups, series/support parts and local decoupling. | [ESP/SD access constraints](../integrated-a500-r5/review/esp-sd/acceptance.md), [front-side decoupling acceptance](../integrated-a500-r5/review/front-sd/acceptance.md). Firmware services and media formats are separate deliverables; an SD socket does not establish hard-drive emulation. |
| R13 | Provide debugging and deliberate bus enable during bring-up. | J20 RP SWD/RUN with voltage reference, J31 ESP UART/EN/BOOT, and normally open J60 BUS_ARM. Physical reset/boot access supplements software updates. | [Service pinout](../integrated-a500-r5/review/service/report.md). SWD reference is not a board-power input; enclosure/cable access remains provisional. |
| R14 | Show power, network and disk status on the PCB or enclosure. | PWR from main 3V3; NET from ESP GPIO4; DISK from GPIO5. Each has a 1 kΩ limiter and an alternative onboard LED or polarized external-LED header, using no extra GPIO. | [Indicator design](../integrated-a500-r5/review/indicators/report.md), [assembly variants](../integrated-a500-r5/review/indicators/assembly.csv). Fit one LED option per channel. PWR is rail presence, not bus permission. NET/DISK semantics require firmware; allow an additional conservative 11 mA on main 3V3. |
| R15 | Manufacturable, serviceable layout with adequate signal returns and mechanical access. | Four-layer starting design with continuous ground reference; constrained regulator/crystal/USB/decoupling geometry, antenna exclusion and card-access envelope. All 214 footprints are now front-side. | [Placement specification](../integrated-a500-r5/R5_PLACEMENT_GUIDE.md), [single-sided population acceptance](../integrated-a500-r5/review/front-sd/acceptance.md). Routing, stackup, assembly and enclosure validation remain; through-hole soldering still involves the underside. |

## Why the board has many parts — and what an FPGA could replace

The visible component count includes support circuitry, not just processing.
The bare RP requires external flash, a crystal, regulator components and bypasses
for its supply pins. The ESP module already integrates much of its equivalent
support. Our discrete control design needs gates, two cycle latches, input
conditioning and a bypass capacitor per IC package. Buffers span many parallel
host signals. Three separate supply-valid conditions and their shutdown hold-up
also account for components. USB recovery, service access and enclosure LED
options add functions beyond a minimal bus interface.

The consolidation review already replaced nine single AND gates with three
triple-gate packages, six main-domain inverters with one hex inverter, and two
sets of four resistors with isolated arrays. These substitutions removed 28
packages from the protected intermediate design; see the
[implementation record](../integrated-a500-r4/review/component-optimisation/phase1-status.md).
Required local bypassing was retained.

An FPGA can potentially absorb the RP's bus state machine, address decoding,
byte qualification, request latches and much of the discrete Boolean logic.
It may also use a different interprocessor transport. That is a valid alternative
architecture, not a requirement to retain these exact chips or the USB topology.
The externally observable bus behaviour and recovery requirements still matter.

An FPGA does not by itself establish 5 V tolerance, safe outputs while unpowered
or unconfigured, power supervision, current limiting, RF/networking, storage or
mechanical access. Those functions may be integrated elsewhere in that design;
compare its actual devices, power/configuration states and included features
rather than assuming either design is better from part count alone.

**214 is a footprint count, not a fitted BOM count:** it includes four mounting
holes and alternative LED/header positions. Some positions are intentionally DNP.

## Limits and evidence status

R5 is a peripheral, not a CPU accelerator, Fast RAM board, RTG adapter, bus master
or expansion passthrough. The optional accelerator discussion in the older
overview is future architecture, not a claim that R5 implements its header or
capabilities. A future A2000 Zorro-II version needs its own connector/control
review; it is not merely the same 86-pin mapping on a larger card.

The current coarse address window and no-passthrough assumption restrict
multi-board coexistence. The firmware must promptly release unowned cycles and
must never wait for USB/ESP while holding an Amiga bus cycle. A bounded service
path and watchdog are required: the present discrete circuit has no autonomous
XRDY timeout, so a hung RP is not covered by a claim of universal automatic
recovery. See the [firmware obligations](../integrated-a500-r2/bus-review.md#firmware-contract-for-this-candidate).

Bench evidence establishes passive signal capture and internal USB communication,
packet capacity, recovery and manual ROM flashing feasibility. Netlist/parity,
truth-table and placement checks establish properties of the saved design.
Neither proves the active integrated board's analogue timing or fault behaviour.
The board still needs critical routing, return-path and impedance validation,
resolution of retained manufacturing-rule findings, enclosure qualification,
and the targeted power/bus/USB prototype checks. Network and future SD-backed
hard-drive functionality depend on matching firmware and Amiga driver support;
the DISK LED is provision for that functionality, not evidence it is delivered.

For the actual circuit, open the [authoritative R5 project](../integrated-a500-r5/integrated-a500-r5.kicad_pro).
For source evidence behind component choices, follow the manufacturer references
in the linked engineering reviews. This document summarizes those reviewed
decisions rather than presenting a new component qualification.
