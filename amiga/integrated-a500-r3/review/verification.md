# R3 verification — 2026-11-09

## Scope and construction

New candidate only. R0/R1/R2, the manufactured passive breakout and shared
connector libraries are preserved. No PCB, fabrication output, vendor upload
or order was created. The connected MCP and fresh launcher processes returned
successful guidance and read-only library search responses. A read-only MCP
load/info of the passive breakout returned 13 components and 230 wires; it was
not saved. Git comparison confirms its files are unchanged. Construction used
3,539 serialized MCP calls, then the public schematic API for no-connect
markers and page metadata not supported by the selected MCP operations.
192 placed symbols comprise 188 physical components plus four power flags.

The pin-level intent is `circuit.json`; independent checks read the native
KiCad-exported netlist rather than trusting successful tool operations.

## Checks run

After sourcing workspace `scripts/env.sh`:

```sh
python repos/fujinet-nio-hardware/amiga/integrated-a500-r3/check.py
python repos/fujinet-nio-hardware/amiga/integrated-a500-r3/power_check.py
```

The first invokes native KiCad netlist export, ERC and PDF export. It checks
864 physical pin assignments with exact membership on all 195 nets, all 81
RP2350B package pads, 65,536 static interlock cases, 65,536 latch sequences,
32 address patterns and eight USB-control combinations. Truth-table coverage
is not propagation-delay or firmware-timing qualification.

The second checks saved power-device pin connections and programming values,
then tolerance corners: current limit 1.197–1.478A, OVLO 5.533–5.796V,
UVLO 4.110–4.266V. The conditional input budget is 1.166A; margin is 31mA.
See `power-checks.json` and ../power-review.md for assumptions and limits.

## Retained ERC findings

33 findings remain visible, with no exclusions:

- 32 inherited external-host model findings: the stand-alone A500 socket model
  cannot supply the motherboard's internal drivers/power knowledge.
- One pin-type conflict on LM66100 ST (U9.5), which TI explicitly permits to be
  grounded when unused. The exported net includes J40.1, modeled as a power
  output, so ERC reports open-drain to power-output. The check identifies the
  exact pins and requires that single additional finding.

The redundant VBUS_PROTECTED power flag was removed because U9's native power
output now drives that net; its duplicate-output error was fixed, not hidden.

## Visual review

All nine PDF sheets were rendered and inspected: hierarchy, input protection,
power qualification, USB recovery, RP support, ESP/storage, address buffers,
data buffers and bus interlocks. Power and RP sections were moved down to
keep long vertical labels inside the drawing border. Connected nets often use
matching labels instead of long drawn wires; this is electrically meaningful,
but the sparse presentation still needs editorial cleanup for easier reading.
Complete native net membership is the connectivity evidence, not visual
proximity of parts. Reviewed input-device package drawings are recorded in
the power review; socket dimensions are in the mechanical selection record.

## Unchecked release conditions

No PCB exists: placement, routing, impedance, DRC and schematic/PCB parity
are not checked. Final orderable BOM, capacitor DC-bias behaviour, socket
contact orientation and A500 case envelope remain open. Power fault overshoot,
source-current downgrade, thermal layout and active A500 bus timing require
final-circuit qualification. Existing USB bench feasibility and passive bus
capture evidence remain accepted; no repeat experiment is requested here.

Python AST parsing, local Markdown link checks and `git diff --check` passed.
Git comparisons preserve R0–R2 and all shared KiCad files against `658eb316`;
passive hardware and shared libraries are unchanged against `acaea6b3`. An
initial broader comparison against that older commit found only the existing
A500 template README clarification from earlier work, not a new CAD change.
