# A500 R4 — dual-source power and bus-output disable proposal

2026-11-10 revision 2. **Proposed; implementation blocked by the stock A500 power budget. Not implemented.**

This records the circuit proposed in the conversation. Saving this document
does not authorize CAD changes. It narrows the earlier
[conditioning review](conditioning-proposal.md) to one implementation for
power-state bus-output disabling. The existing schematic and PCB remain
unchanged.

## Corrected requirements and one proposed power topology

USB is optional for normal operation. Amiga +5 V must power the processors,
SD card and interface; USB must independently power the processors and all
flashing/debugging functions when the host is off. With both available, use
qualified USB power preferentially. Source selection never grants bus-drive
permission. This supersedes the USB-only assumption in the earlier proposal
and the existing R3 power review; CAD still represents that earlier circuit.

**Concrete incompatibility:** the existing load allocation exceeds the documented
stock A500 expansion-port allowance. The topology below is the selected direction,
but it is not an electrically approved implementation at the present load.

| Requirement | Proposed schematic connection | Evidence / outstanding constraint |
|---|---|---|
| Dual source with reverse blocking | Add **TPS2121RUXR**. IN1 pin 7 receives qualified USB; IN2 pin 2 receives current-limited Amiga +5 V. OUT pins 1/8 become `5V_MAIN`, feeding existing U5 **TPS62130RGTR**. GND pin 12 to ground. | TI documents independent reverse-current blocking and automatic source selection. No direct connection between sources. |
| USB priority | CP2 pin 3 to GND; PR1 pin 6 from IN1 through 100 kΩ / 100 kΩ (1%) divider. At 4.5 V IN1, PR1 is at least 2.23 V, above the 1.10 V maximum priority threshold. | VREF mode selects valid IN1 regardless of relative input voltage. This is not the fast-comparator mode; uninterrupted transfer is not promised. |
| Reuse USB protection and qualification | Retain J1 → U8 TPS259630DDAR → U9 LM66100DCKR → U4 TPS22917DBVR; reconnect U4 output to mux IN1 instead of directly powering U5. Retain the protected upstream U6/FUSB303B supply, so USB qualification can cold-start independently. | Existing CC permission controls **only the USB branch**, never the common main supply. Keep U9 for upstream/AON reverse isolation. |
| Qualify USB current | Retain FUSB303B OUT1 and replace U7 with pin-compatible **SN74LVC1G14DBVR**, with local 100 nF bypass. Rename POWER_ALLOW to USB_POWER_ALLOW. Retain the 10 kΩ OUT1 pull-up. | Open-drain CC indication needs Schmitt conditioning. Complete-board USB operation requires a source advertising at least 1.5 A; a default-current computer port is not sufficient under the present allocation. |
| Protect the Amiga input | J40 pins 5/6 → dedicated input current limiter → mux IN2. Feed any host-only interface supply from the same limited branch; raw Amiga sense remains high impedance. | All host draw, including bypass paths, must fit **300 mA total**. A fuse alone is not a precise current limiter. Exact limiter/value selection is deliberately blocked by the incompatible operating load. |
| Mux auxiliary components | Local input/output ceramics, SS ramp capacitor and ILM programming resistor are required; retain U5 support circuitry and proposed local AVIN bypass. ST may be grounded if unused. | Final SS/ILM values depend on the resolved load and startup allowance. TPS2121's 80 kΩ setting spans 1–2 A and cannot protect a 300 mA host allocation. Do not reuse it as the sole host limiter. |
| Host-off isolation | Keep bus permission dependent on raw Amiga power, valid main 3V3, host reset and existing hardware/firmware readiness. USB selection or mux ST is never BUS_PERMIT. | Host-facing outputs must remain high impedance during USB-only flashing, even though the processors run. |

This retains the existing USB protection rather than adding another alternative
architecture. The USB-only AON rail serves USB detection; normal Amiga operation
must not depend on that rail. U4's discharge connection remains on its own USB
branch, not the common mux output. Recalculate USB current/thermal margins with
the additional mux resistance before implementation: the old 31 mA margin is
not transferable. Keep data-ESD references on the protected USB branch.

Mux authority: [TI TPS2121 datasheet](https://www.ti.com/lit/ds/symlink/tps2121.pdf),
pin table, electrical characteristics and Table 9-3. Reverse blocking permits
finite leakage and switching transients; it is not a zero-current guarantee.
CC authority: [onsemi FUSB303B datasheet](https://www.onsemi.com/pdf/datasheet/fusb303b-d.pdf).
Conditioner: [TI SN74LVC1G14](https://www.ti.com/lit/ds/symlink/sn74lvc1g14.pdf).

## Verified current-budget blocker

Commodore's **A500/A2000 Technical Reference Manual**, printed page **227**
(PDF page 233), specifies **300 mA from expansion pins 5 and 6 combined** and
states that this port has **no current limiting**. The downloaded page was
rendered and visually checked, not inferred from a third-party connector table.
[Commodore manual scan](https://support.retrorewind.ca/media/commodore/amiga/commodore_a500-a2000_technical_reference_manual.pdf#page=233)

The [existing allocation](../../../integrated-a500-r3/power-review.md) is
3.3 V × 1.2 A = **3.96 W**: ESP 600 mA, RP/flash 200 mA, SD 200 mA,
bus/control 100 mA and margin 100 mA. These are allocations, not measured
simultaneous consumption. At the existing assumed 85% regulator efficiency:

- Required input before path losses: **4.66 W**, or **932 mA at 5 V**
  (**1.035 A at 4.5 V**), plus control/interface overhead.
- Stock port allocation: **1.50 W at 5 V**; at 85% efficiency, at most
  **386 mA at 3.3 V**, before path losses and host-interface overhead.
- Even at impossible 100% conversion efficiency, the present 3.96 W allocation
  exceeds the port's 1.50 W allowance. A more efficient mux cannot close this gap.

A host limiter must have a worst-case upper limit, including tolerance and all
bypass draw, no greater than 300 mA. Under the current allocation that limiter
would prevent reliable startup or cause brownout. Setting it near 1 A instead
would violate the documented stock-host budget. A stronger external Amiga PSU
alone does not establish a higher rating for the motherboard/connector path.

**Required decision before detailed implementation:** establish a reduced
complete-board operating budget that fits 300 mA at the host connector, or
explicitly change the supported-host assumption to an electrically qualified
higher-current A500 power path. No such qualification or reduced-load evidence
currently exists. Do not silently substitute mandatory USB power: that would
contradict the corrected requirement. This is the specific reason to stop;
no unrelated audit is requested.

## Retained bus-disable circuit, subject to the power-budget decision

The separately powered output stage below remains the proposed safety mechanism.
Its host-derived rail must sit behind the host input limiter and its current
counts toward the same 300 mA allowance. During USB-only operation this small
host-facing stage is intentionally unpowered/high impedance; both processors
and their flashing/debug functions must still operate. Host absence must not
hold RP_RUN low: the reset clamp must act on a powered host-side fault, while
existing physical boot/reset controls remain usable without the Amiga.

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
   produces no host backfeed. Verify Amiga-only normal operation within the
   agreed host current limit. With both present, verify USB priority and
   transfer on unplugging either source; outputs remain disabled during any
   resulting brownout until hardware and firmware readiness return.
4. Measure XRDY assertion and sink voltage with representative host loads.

These focused tests are acceptance gates for the proposed implementation,
not a request to repeat the accepted USB feasibility experiments or start
another general audit. Schematic implementation, native connectivity checks,
ERC and incremental PCB synchronisation remain subject to approval. Preserve
the existing PCB; do not regenerate its placement or route globally.

**Decision pending:** resolve the documented host-current incompatibility before
approving implementation. No CAD, placement, routing or fabrication ordering is
authorized by this document.

Documentation validation: source page visually inspected; budget arithmetic and
relative documentation link checked; `git diff --check` passed. This revision
changes only this Markdown proposal, not the schematic, PCB or submodule pins.
