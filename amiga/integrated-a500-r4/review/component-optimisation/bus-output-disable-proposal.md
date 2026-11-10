# A500 R4 — final USB-power requirement and bus-output protection

2026-11-10 revision 3. **USB main-power requirement decided by the user.**
TPS2121 and dual-source main power are rejected. No CAD changes in this revision.
The bus-disable circuit below remains a candidate, with one specific unresolved
host-safety issue documented below; it is not an implementation-ready design.

## Final power requirement

| Requirement | Implementation decision | Evidence / check |
|---|---|---|
| Normal R4 operation | USB power is required. Retain J1 → U8 TPS259630DDAR → U9 LM66100DCKR → U4 TPS22917DBVR → U5 TPS62130RGTR and main 3V3. | Existing schematic and R3 power allocation. No TPS2121 or source-selection circuitry. |
| USB-powered, Amiga off | Both processors and flashing/debug facilities operate from USB. All host-facing outputs remain disconnected. | Bus permission must depend on valid host power separately from USB availability. |
| Amiga-powered, USB off | No RP2350, ESP32 or main-3V3 power from the expansion connector. | No power OR connection, main-regulator input connection or alternate main-rail feed from Amiga 5 V. |
| Permitted host consumption | Raw Amiga 5 V is sensed through a high-impedance divider. A small current-limited host-interface rail is permitted only to keep the output-disable stage operational as USB/main power fails. | All host-interface and sense consumption counts against the same 300 mA allowance. |
| USB qualification | Keep the existing ≥1.5 A advertised-current requirement. Retain FUSB303B and AON supply; U7 remains a separate AON-domain device. | A default-current USB host port is not assumed capable of powering this board. U7 Schmitt replacement and its bypass remain within the scoped conditioning work. |
| Bus permission | Require valid Amiga power, valid relevant board rails, host reset released, RUN mode, BUS_ARM, BUS_READY and existing cycle/BERR interlocks. | USB presence alone must never enable a host output. |

The existing [USB power review](../../../integrated-a500-r3/power-review.md)
allocates 1.2 A at 3.3 V and estimates 1.166 A USB input under its stated
loss/efficiency assumptions. Consolidation does not justify lowering that
allocation without evidence.

Commodore specifies **300 mA total at +5 V from expansion pins 5 and 6**, with
no port current limiting. The manual's printed page 227 (PDF page 233) was
visually checked. At 85% assumed conversion efficiency, the existing 3.96 W
load allocation alone requires 932 mA at 5 V before path losses. This explains
the final USB requirement; it is no longer an unresolved architecture decision.
[Commodore manual scan](https://support.retrorewind.ca/media/commodore/amiga/commodore_a500-a2000_technical_reference_manual.pdf#page=233)

## Host-interface limiter candidate

For the proposed ≤100 mA interface allocation, use **TPS2553DBVR** ahead of
the SS14/AP2112 branch, never ahead of a main-rail feed. DBV pins: 1=raw
AMIGA_5V, 2=GND, 3=EN tied to raw AMIGA_5V, 4=/FAULT diagnostic only,
5=ILIM through **133 kΩ ±1%** to GND, 6=HOST_5V_LIMITED. Add a local 100 nF
input bypass. Keep the isolation diode and downstream capacitance.

TI Table 9-2 gives **173.7–233.9 mA** limiting for this resistor, leaving
headroom below the stock 300 mA allocation for device quiescent current and
the raw host-sense divider. This is a sustained current-limit envelope, not
an instantaneous peak-current ceiling. Startup charging and output-load
transients must be checked; /FAULT's deglitch delay is unsuitable as the only
fast bus-disable signal. This candidate is **not installed** and does not close
the rail-supervision issue below.
[TI TPS2553 datasheet, pin table and Table 9-2](https://www.ti.com/lit/ds/symlink/tps2553.pdf)

## Specific host-safety blocker before implementation

The saved guard monitors raw AMIGA_5V with MIC2790 and main 3V3 with MIC2793,
but supplies both supervisors and the host-facing drivers from **3V3_BUS**.
It does not sense that local rail. A local overload/current-limited ramp or
LDO dropout can lower 3V3_BUS while both sensed rails remain valid. Neither
SNS comparator is then required to assert reset. Connecting VDD to a rail is
not equivalent to supervising that rail at the bus's qualified voltage.

Microchip specifies valid supervisor operation down to 1.5 V, not a 3.1 V
local-VDD brownout trip. The SN74LVC541A supports operation down to 1.65 V,
but the reviewed bus timing is specified at 3.0–3.6 V, and its Ioff test at
VCC=0 does not guarantee high impedance throughout an intermediate-voltage
collapse. Thus a still-enabled interface could miss bus turnaround or enter
an unspecified state and contend with a host driver. This is a credible
possible host-damage mechanism, not an observed failure or a claim that every
brownout causes damage.
[Microchip MIC2790/1/3, electrical limits and functional description](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MIC2790-1-3-Supervisor-with-High-Accuracy-Ultra-Fast-Propagation-Delay-and-Capacitor-Programmable-Reset-Delay-DS20007151.pdf)
[TI SN74LVC541A operating, timing and Ioff limits](https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf)

Required narrow correction: independently qualify **3V3_BUS** and force the
same data-OE and XRDY/IRQ overrides on its undervoltage, with enough local
hold-up for the shutdown response. A further MIC2790-family monitor is a
candidate, but its precise reset combining and full shutdown bound have not
been verified. Do not simply wire push-pull reset outputs together or treat
the published typical /MR delay as a guaranteed maximum. Do not implement the
previous two-monitor candidate unchanged. No new general architecture audit
or repeat USB feasibility experiment is requested.

## Existing bus-disable candidate — requires the correction above

The host-derived rail is justified solely by keeping host output control alive
when USB power fails. It must sit behind the host input limiter. During USB-only
operation this small host-facing stage is intentionally unpowered/high impedance;
both processors remain usable. Host absence must not hold RP_RUN low. Any
supervisor /MR tie must use its own valid supply domain, not leave the previous
main-3V3 tie connected to an unpowered host-domain supervisor.

| Circuit change | Exact implementation |
|---|---|
| Add `3V3_BUS` | Current-limited Amiga 5 V → **SS14-13-F** isolation diode → **AP2112K-3.3TRG1**. EN tied to its input; 1 µF input/output ceramics, 47 µF output reservoir and 4.7 kΩ output bleeder. This rail supplies only the host-facing output buffers and supervisor circuitry. |
| Retain data buffers U44/U45 | Move their VCC and local bypasses to `3V3_BUS`. Preserve their existing byte-enable inputs. Connect their spare `/OE` pins **19** to `BUS_DISABLE` instead of ground. Apply the same override to U46/U47 pin 19, keeping those receivers on main 3V3. |
| Replace host supervisor U60 | **MIC2790L-04VD6-TR**, powered from `3V3_BUS`. Reuse the host-sense divider, changing R60 to **102 kΩ, 0.1%**, retaining R61 **10 kΩ, 0.1%**: approximately **4.48 V** threshold. Its push-pull `/RESET` becomes `HOST_PG`; remove R62. Add 100 pF C0G timing capacitor and use 1 µF local bypass. |
| Add main-supply supervisor | **MIC2793LH-04VMT-TR**, powered from `3V3_BUS`. Sense main 3V3 through **67.5 kΩ / 10 kΩ, 0.1%**: approximately **3.10 V** threshold. EN tied high; `/MR` connected to `HOST_PG`; CTH **100 pF C0G**, bypass **1 µF**. Its active-high RESET drives `BUS_DISABLE`; complementary `/RESET` supplies `BUS_PERMIT`. Add 100 kΩ pull-up on `BUS_DISABLE`. |
| Replace U81/U83 output stages | **SN74LVC2G132DCUR** generates `NAND(BUS_PERMIT, WAIT_SINK)` and `NAND(BUS_PERMIT, IRQ_SINK)`. These drive the two `/OE` inputs of **SN74LVC2G125DCUR**. Tie both buffer data inputs to ground; outputs connect to XRDY and `/INT2`. Thus each output can **sink low or disconnect; never drive high**. Both packages use `3V3_BUS`, individual 100 nF bypasses and 100 kΩ `/OE` pull-ups. |
| Force processor reset during a fault | `BUS_DISABLE` drives an **MMBT3904-7-F** through 22 kΩ; emitter grounded, collector connected to existing RP_RUN reset node, with 100 kΩ base-emitter pull-down. Existing buttons and flash controls remain connected. |
| Remove dependence on buck PG | Use `BUS_PERMIT` in place of `3V3_PG` in the existing safety equation. Remove R9 and ground unused U5 PG. **Keep the existing TPS62130**—changing to its A variant is unnecessary here. |
| Provide shutdown margin | Add **100 µF, ≥6.3 V, ±20%, ESR ≤50 mΩ** to main 3V3, retaining existing regulator capacitors. |

The MIC supervisors provide a documented **2.2 µs maximum sense-response delay
under their specified overdrive conditions**, plus delayed release. The selected
100 pF timing capacitors give approximately 1 ms nominal recovery delay per
supervisor. This is a component specification, not a measured end-to-end
shutdown result. [Microchip datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MIC2790-1-3-Supervisor-with-High-Accuracy-Ultra-Fast-Propagation-Delay-and-Capacitor-Programmable-Reset-Delay-DS20007151.pdf)

The **dual NAND already provides the Schmitt conditioning needed at this
guard's request inputs**. No extra Schmitt stage is needed on the push-pull
supervisor outputs. This replaces the earlier blanket five-buffer proposal
for this specific power-disable function; it does not claim to resolve every
other input-conditioning finding.
[NAND datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc2g132.pdf)

The revised XRDY allocation is approximately **44.7 ns against 60 ns**,
including the existing 10 ns interconnect allowance, under the original load
assumptions. Arithmetic: 36.5 − 4.5 + 7.0 + 5.7 = 44.7 ns, replacing the
original open-drain inverter delay with NAND plus buffer-enable delay. This
is a design allocation, not measured timing compliance.
[Output-buffer timing](https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf)

## Operating assumptions

- Stock A500; no live connector insertion.
- Interface load ≤100 mA; main-rail discharge load ≤1.2 A.
- Ordinary supply loss and brownout are the intended operating envelope.
  A hard short collapsing a rail instantaneously is outside this sequencing
  guarantee.
- A fault may abort a bus transaction; transaction preservation during a
  power failure is not promised.

## Essential validation before active attachment

1. Verify power-up, USB removal and both supply brownouts: all host outputs
   disconnect before their controlling circuitry leaves its valid operating
   range.
2. Verify recovery cannot re-enable outputs until supervisor delays expire and
   firmware deliberately reasserts BUS_READY.
3. Verify USB-only operation permits independent processor flashing/debug and
   produces no host backfeed. With Amiga power only, processors and main 3V3
   remain off and all host outputs disconnect. With both present, USB powers
   the processors; host power only supplies the limited interface stage.
5. Exercise a controlled local 3V3_BUS sag with raw Amiga 5 V and main 3V3
   still valid; verify the corrected guard releases outputs before the
   interface leaves its qualified range. This is a newly identified circuit
   acceptance condition, not an instruction to test an unprotected host.
4. Measure XRDY assertion and sink voltage with representative host loads.

These focused tests are acceptance gates for the proposed implementation,
not a request to repeat the accepted USB feasibility experiments or start
another general audit. Schematic implementation, native connectivity checks,
ERC and incremental PCB synchronisation remain subject to approval. Preserve
the existing PCB; do not regenerate its placement or route globally.

## Implementation status

The final USB requirement supersedes revision 2's dual-source proposal and
closes its current-budget decision. The local-interface-rail supervision gap
is the only new stop condition recorded here. Protection implementation and
I1/I2/R-A/R-B remain unimplemented; no component-count reduction is claimed.
The existing PCB, schematic and placement remain unchanged. Continue with
schematic-first edits and independent checks once this specific guard gap is
closed; preserve the PCB and synchronise incrementally. No routing or ordering.

Verification this revision: manufacturer limiter table and supervisor/driver
limits read; final USB requirement checked against the unchanged power chain;
local documentation link checked and `git diff --check` passed. No CAD test is
claimed for a documentation-only change.
