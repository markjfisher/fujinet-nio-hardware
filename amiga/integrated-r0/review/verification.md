# Candidate verification — 2026-11-09

Scope: a reviewable first-board proposal, complete proposed RP package
allocation, and implemented USB/power/recovery **subcircuit**. The integrated
processor and Zorro sheets are unfinished. No PCB or fabrication acceptance.

## Tool availability and preservation

The configured `fujinet_kicad` MCP was discovered in the live tool catalogue.
`get_usage_guidance(operation="strategy")`, library searches, project listing,
and `schematic(load/info)` on the passive breakout returned successful results.
The passive read reported 13 components and 230 wires. Its in-memory `modified`
flag was true after load; no save was issued against it. A subsequent
`git diff --exit-code HEAD -- amiga/prototyping-board` returned zero.
The read-only PCB load also returned success: 13 footprints and 1,197 track
items. The same preservation check passed afterward.

Two early analysis calls used unsupported/missing arguments and the BOM query
found no exported BOM. These did not establish inspection; the subsequent
successful schematic load/info did. No registration/startup repair was needed.

All component construction, net-label attachment and schematic wiring used the
configured MCP, serialized against a new candidate. Its collision query found
zero collisions before the final label-layout adjustment. Independent KiCad
netlist checks were run again after that adjustment.

The router does not expose page-size or no-connect-marker operations. Those two
operations used the installed `kicad_sch_api` public `set_paper_size`,
`set_title_block` and `no_connects.add` methods after saving, followed by MCP
reload. No KiCad S-expression generation or patching was used. The six NC
markers are USB SBU1/SBU2 and unused FUSB303B outputs/address-mode selection;
they are deliberate circuit choices, not ERC exclusions.

**Tool limitation found:** after reloading this candidate, MCP
`list_component_pins(U1)` returned success with an empty pin list for the
inherited TS3USB30EDGSR symbol, although native KiCad exported all ten pins.
Do not use that empty response as proof that the component has no pins.
Further pin-position operations should use the actual library definition or
freshly instantiated state and independently verify their saved result.

## Checks run

From the workspace root:

```sh
source scripts/env.sh
python repos/fujinet-nio-hardware/amiga/integrated-r0/check.py
git -C repos/fujinet-nio-hardware diff --exit-code HEAD -- amiga/prototyping-board
```

Result: **170 physical pin assignments match independent KiCad XML export;
four USB selector states pass on both polarities; KiCad 10.0.7 ERC reports
zero errors and zero warnings.** The CSV accounts for 81 package pads and 48
unique GPIO assignments. GP2–7 carry A2–7 and none carries an interprocessor
SPI signal. See `checks.json`, `erc.json` and `netlist.xml`.

The TS3USB30E DGS, FUSB303B, TPS22917 and TPS62130 pin maps were compared with
manufacturer pin-function tables. RP2350B mapping was compared with Figure 3
and the supply descriptions in the downloaded Raspberry Pi datasheet, printed
pages 16–17 and 400–401. PDF SHA256:
`a638d6780da919162660691bfa02c6dcf7c2a0b6e9f18e2d7519c80b664a2e39`.
The temporary copy is `/tmp/rp2350-datasheet.pdf`; the manufacturer's link in
the proposal is the durable source. Ground pad 81 is the library's exposed-pad
number for the datasheet's central GND pad.

Native PDF and SVG exports were inspected as rasterized pages. That review
found left-facing pin labels overlapping symbols; their stubs were extended
through the MCP and the result rendered again. Circuit groups and polarity
labels are now distinguishable. Remaining drawing cleanup includes passive
field orientation and sheet density; it is not a release-quality drawing.

Power flags identify real downstream supply nets after passive series elements
(GND input, diode-protected input and buck output after L1). They do not assert
that the electrical power design is qualified. The QOD resistor separates the
discharge terminal from the output power pin and deliberately slows discharge.

## What has not passed

* Whole-board connectivity, processor decoupling/flash/RF design and Zorro gate
  implementation: not present in this subcircuit.
* Final capacitor/inductor/connector MPN and footprint review: incomplete.
* Dynamic CC allowance reduction, power protection/thermal/inrush sign-off:
  open; see the proposal's explicit constraints.
* Actual 32-channel Amiga evidence and the old active pin-map schematic:
  not located. Existing synthetic captures were found and indexed, not
  substituted for those measurements.
* PCB placement, routing, DRC, audit and schematic parity: not run because no
  candidate PCB exists. No generic routing pass would establish USB impedance.

No physical USB tests were repeated, no corrupted images were requested, no
fabrication order was prepared, and no released board was regenerated.
