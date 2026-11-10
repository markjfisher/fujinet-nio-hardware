# A500 R4 — concrete bus-output disable proposal

2026-11-10. **Proposed; awaiting user approval. Not implemented.**

This records the circuit proposed in the conversation. Saving this document
does not authorize CAD changes. It narrows the earlier
[conditioning review](conditioning-proposal.md) to one implementation for
power-state bus-output disabling. The existing schematic and PCB remain
unchanged.

## Proposed circuit

Use a separately powered bus-output stage with a hardware supervisor override.
The Amiga powers this small interface section; USB continues powering the
processors. The interface can therefore release the bus when processor power
fails.

| Circuit change | Exact implementation |
|---|---|
| Add `3V3_BUS` | Amiga 5 V → **SS14-13-F** isolation diode → **AP2112K-3.3TRG1**. EN tied to its input; 1 µF input/output ceramics, 47 µF output reservoir and 4.7 kΩ output bleeder. This rail supplies only the host-facing output buffers and supervisor circuitry. |
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
3. Verify USB-only operation produces no host backfeed, and Amiga-only
   operation keeps outputs disconnected.
4. Measure XRDY assertion and sink voltage with representative host loads.

These focused tests are acceptance gates for the proposed implementation,
not a request to repeat the accepted USB feasibility experiments or start
another general audit. Schematic implementation, native connectivity checks,
ERC and incremental PCB synchronisation remain subject to approval. Preserve
the existing PCB; do not regenerate its placement or route globally.

**Decision pending:** approve this circuit for implementation, or provide
specific corrections. No fabrication ordering is included.
