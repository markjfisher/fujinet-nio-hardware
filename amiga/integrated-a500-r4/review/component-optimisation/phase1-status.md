# Phase 1: stopped at pre-substitution electrical verification

Follow-up: the approved wider audit is recorded in
[conditioning-proposal.md](conditioning-proposal.md), with resistor inventory,
RC calculations and CAD preservation evidence. No substitutions have yet been
implemented; that proposal also identifies an unresolved power-state guard.

Checkpoint: `3464c256` (baseline content `de42fbbd`). No schematic or PCB
changes have been made. I1, I2, R-A, R-B and the bypass additions remain
unimplemented. No placement generator, routing or PCB synchronisation was run.

## Blocking finding: I1 power-good input edge rate

A fresh native KiCad XML netlist export confirms:

| Signal | Driver | Pull-up | Existing receiver | Proposed receiver |
|---|---|---|---|---|
| HOST_PG | U60 TPS3808G01DBVR RESET, pin 1 | R62, 10 kΩ to 3V3 | U61 pin 1 | LA pin 1 |
| 3V3_PG | U5 TPS62130RGTR PG, pin 4 | R9, 10 kΩ to 3V3 | U61 pin 3 | LA pin 2 |

Both manufacturer datasheets specify open-drain outputs. The proposed
SN74LVC11A has standard CMOS inputs, a maximum input transition rate of
10 ns/V, and typical input capacitance of 4.9 pF. Its standard-CMOS-input
section warns about excess current and oscillation with slow edges and
recommends Schmitt conditioning for slow/noisy signals.

For an ideal 3.3 V pull-up, using only typical receiver capacitance:

`RC = 10 kΩ × 4.9 pF = 49 ns`

`t(0.8 V → 2.0 V) = RC × ln((3.3−0.8)/(3.3−2.0)) = 32.0 ns`

This is about 26.7 ns/V across the input threshold region, exceeding
10 ns/V even before PCB and driver capacitance. This calculation is an
engineering estimate, not a measured waveform or guaranteed worst-case
model. It is sufficient to prevent claiming datasheet compliance.

The original SN74LVC1G11 also specifies 10 ns/V at 3.3 V. This is a gap in
the baseline review as well as a verification blocker for the replacement;
retaining U61 alone does not establish a compliant circuit. Boolean
equivalence and fast propagation-delay sums do not resolve slow input edges.
This affects power/recovery interlocks, not a request to repeat accepted USB
experiments. No actual unintended bus drive has been demonstrated.

## Proposed resolution requiring scope approval

Extend the electrical review to power-good/reset/mode input conditioning.
Evaluate Schmitt conditioning or stronger pull-ups against driver sink
ratings, maximum credible capacitance, power sequencing and propagation
delay. Include RP_RUN, another resistor-released input, in that check.
Select exact parts/values and validate the revised circuit before applying
I1. Do not silently waive the edge requirement or force the 162-component
target if a safe circuit needs additional parts.

## Verification and counts

- MCP usage guidance and read-only library searches responded successfully.
- Fresh native `kicad-cli sch export netlist --format kicadxml` succeeded;
  it reports 188 components and confirms the connections above.
- No substitutions were made; post-substitution equivalence, ERC, DRC and
  schematic/PCB parity checks therefore have not been performed.
- Current count remains 188 fitted components (47 U, 49 R, 72 C, 20 other),
  with 192 PCB footprints including four mounting holes. Target 162 is not
  achieved.
- Mechanical placement, bus buffers, critical power cells and CAD files
  remain unchanged. Checkpoint and this status report are separate commits.

## Manufacturer evidence

- [TI SN74LVC11A](https://www.ti.com/lit/ds/symlink/sn74lvc11a.pdf):
  recommended operating conditions, electrical characteristics and standard
  CMOS input discussion.
- [TI SN74LVC1G11](https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf):
  recommended operating conditions.
- [TI TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf): open-drain RESET.
- [TI TPS62130](https://www.ti.com/lit/ds/symlink/tps62130.pdf): open-drain PG.
