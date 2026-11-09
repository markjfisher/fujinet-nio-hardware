# R4 verification — 2026-11-09

## Result and limits

**Pass for saved circuit connectivity, PCB parity and the stated placement
constraints. Not a routed board, clean DRC result or fabrication release.**
All work is in the new R4 candidate. Released hardware and earlier candidates
are unchanged; no push, order, fabrication export or submodule pin change.

| Independent check | Result |
| --- | --- |
| Physical inventory | 188 circuit components and four board-only mounting holes |
| Exact functional net membership | 864 pin assignments, 195 complete nets |
| RP allocation | 81 package pads, 48 unique GPIO functions; no SPI/address collision |
| Logic tests | 65,536 static cases; 65,536 latch sequences; 32 address patterns; eight USB selections |
| Native schematic/PCB parity | **0 findings** |
| A500 lands | All 86 checked for face, numbering, position, dimensions and no paste |
| RP reference cell | Six footprints and relative positions checked; no reference copper imported |
| Control bypass capacitors | 27 paired to their loads; maximum center-to-power-pad distance 3.111 mm |
| Native ERC | 33 retained, unchanged electrical/model findings |
| Native DRC | Four USB connector hole-clearance findings; two antenna-overhang silk findings |
| Unconnected PCB items | **499**, expected at this unrouted stage; not waived |
| Routing | 0 tracks; four copper layers enabled, impedance stackup not selected |

The ERC findings remain the 32 external-host model cases and manufacturer-
directed grounded LM66100 ST connection documented in R3. No exclusions were
added. Project-local library registration resolved the seven temporary missing-
library findings. Native checking is independent of the MCP's return status.

The conditional power calculation remains 1.166A input, with calculated current
limit 1.197–1.478A. This is not a thermal, hot-plug, current-downgrade or fault-
transient measurement. See the inherited R3 power review and `power-checks.json`.

## Tool gaps caught and corrected

- The pipeline strips hierarchy-leading slashes from net names and library
  nicknames from footprint identifiers; it omits schematic paths and NC net
  assignments. Native read-back caught these. Public pcbnew restores identifiers
  and paths; MCP assigns explicit NC nets, including KiCad's `{slash}` escaping
  for three FUSB303B pin names.
- MCP `rename_net` returned “not found” for `TX_HI_N`, although native read-back
  showed that net. Native `NETINFO_ITEM.SetNetname` supplies this narrow fallback.
- Loading/updating the custom A500 symbol without the custom symbol search path
  lost its definition. The affected candidate sheet was restored from R3,
  updated through a correctly configured fresh MCP process and rechecked.
  `update_footprints.py` now supplies that environment. Earlier projects were
  never changed.
- Negative placement-hint angles are ignored by this MCP. Reference angles are
  normalized modulo 360 before submission and checked after saving.
- Enabling four copper layers does not automatically expand the two-layer
  constructor's antenna keepout. Native API restores the library's all-copper
  layer set. It is not sufficient to inspect the front-layer preview alone.
- The placer treats shared supply capacitors as graph neighbours of many chips.
  RP/buffer constraints and geometry-derived control bypass placements prevent
  relying on that result for decoupling.
- MCP does not construct custom footprint pads, set hierarchy IDs or register
  project libraries. Native pcbnew handles footprint/board gaps; the pinned
  kiutils LibTable serializer writes project library configuration only. No
  KiCad CAD S-expressions were hand-generated or patched.

Generic placement autofix is unsuitable here: source inspection shows that it
can move locked components. It was not applied to this board. The tool's broad
courtyard audit also treats the ESP's antenna/body bounding box as one region,
so it reports apparent overlaps that native KiCad does not classify as physical
courtyard conflicts. The full MCP audit is retained, not substituted for DRC.

## Commands and visual inspection

After `source scripts/env.sh`, run system Python on `check.py`,
`power_check.py`, and `pcb_check.py`. Construction and placement use the pinned
MCP launcher; the README records the build order. `pcb_check.py` invokes native
`kicad-cli pcb drc --schematic-parity` with an absolute board path and exports
`placement.svg`. Earlier relative-path CLI calls hit a KiCad assertion; they
are not used as final evidence.

The native top-layer preview was rendered and inspected: A500 lands run down
the right edge, USB-C and microSD face left, ESP antenna overhangs the left
edge, RP is central, bus buffers face the socket, recovery controls are at the
bottom and debug headers are at the top. Mounting holes were moved clear of
the socket and the bus-arm jumper. Final power/USB routing and assembly access
are not established by this view. The sparse schematic uses labeled nets;
its native netlist, not apparent drawing proximity, establishes connection.

## Remaining layout work

Resolve USB-C land-to-NPTH clearance (0.1944 mm against the current 0.25 mm
rule), choose the concrete stackup, complete buck placement/thermal paths and
critical RP/USB routing, then use ordinary routing with preservation checks.
Keep antenna copper exclusion on all layers. Finish the package/MPN, capacitor
bias and mechanical-fit reviews. These are engineering tasks, not another
permission gate or a request to repeat the accepted USB experiments.

## Owner-measured envelope refinement

The revised outline is 111 × 117 mm. The owner's approximate 117 mm adapter
length replaces the initial 124 mm envelope. An 18 mm component-free strip is
measured inward from the right PCB edge; the socket lands are its intentional
exception. All other component pads and courtyards, including mounting hardware,
remain outside that strip. Native read-back checks the exact outline, the whole
strip and the two-sided component-only rule area. The maximum non-socket
courtyard/pad x coordinate is 86.975 mm against a limit of 87 mm.

Electronics translate left 6 mm as a group, preserving the RP reference cell,
local bypass relationships and all connections. Recovery switches move inward;
mounting holes fit the new outline, with H1 inset to clear the ESP courtyard.
Native parity remains zero, with the same six DRC findings and 499 unconnected
items. Updated native preview was visually inspected. Rectangular PCB shape is
a candidate envelope, not proof of enclosure or formed-tail fit.

## Circuit-cluster and label review

The revised placement restores 34 previously hidden references and replaces
four font sizes with visible 0.9 mm references / 0.15 mm strokes on all 192
footprints. Repeated IC/bypass cells share offsets and label baselines, including
C71/C76/C77/C80. Unrelated logic is moved out of the RP/flash region. The six
RP regulator reference placements remain unchanged. All references around U20,
including its tightly spaced north-side regulator parts, are now visible.

Named native PCB groups cover 183 components in 54 functional groups. The five
standalone connectors and four mounting holes are intentionally ungrouped.
Native read-back verifies every group membership, all reference styles and
visibility, seven local supply-capacitor relationships, and thirteen power-cell
positions/orientations. The buck output capacitor C8 is now in the power stage;
C4/C5 sit beside the always-on regulator. These checks verify saved geometry,
not routed loop inductance or transient performance.

C42/C43 are the only bottom-side components, beside the SD supply contact in
plan view. Native mirrored bottom and top previews were both rendered and
visually inspected. The bottom preview shows both labels clearly. Underside
component clearance is now part of the enclosure/assembly review.

Final native checks retain 864 functional assignments, zero schematic parity
findings, the same six DRC findings and 499 unrouted items. No new native
courtyard, pad-clearance or silkscreen-overlap findings appeared. No exclusions
were added. The board still contains zero tracks.

`cluster-mcp-audit.json` retains the separate MCP audit: 30 reported items,
including zero-area bounding-box contacts, the concave ESP courtyard's broad
bounding box, deliberate edge interfaces, and cross-side SD items. In particular,
MCP flags C42 against J30's keepout and C43 text against J30 pads without
respecting their opposite faces: native read-back confirms all five J30 keepout
zones are F.Cu-only while C42/C43 and their labels are on the back. Native DRC
reports none of those SD conflicts. This audit is not presented as clean or
used to override the retained native findings. Both audit and native DRC remain
necessary as routing proceeds.

## Follow-up visual review

Explicit label preferences replace generic free-space choices in the marked
areas. R3 is separated from R63; R32/R33/R36 use a regularly spaced column
with a reference immediately below each resistor. U3 is labelled beside its
QFN footprint, separately from C3. R53 aligns with R50–R52 and SW4's reference
is centered over its switch. RP support parts are spaced into clearer rows;
the six original RP regulator reference footprints retain their exact geometry.
The crystal capacitors remain beside Y20; their placement and the USB-series
resistor positions still require the critical-routing review.

`tidy-plan.json` records the component moves; `label-preferences.json` records
preferred label positions, checked against native geometry by the planner.
Native read-back checks the final moves and all five pads on each of
U69/U70/U74/U79. U69/U70/U74 are SN74LVC1G04DBVR inverters; U79 is an
SN74LVC1G32DBVR OR gate. TI specifies a five-pin DBV/SOT-23 package for both:
[1G04 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf),
[1G32 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g32.pdf).
The absent sixth pad is intentional; these are different packages from the
neighbouring six-pin devices.

Final follow-up verification: all 864 functional assignments and zero schematic
parity findings retained. Native DRC returns only the prior four hole-clearance
and two silk-edge findings; no additional findings remain. All 192 references
are visible at the uniform size. The regenerated top view was visually inspected
against the six marked areas. `tidy-mcp-audit.json` retains the separate 30-item
MCP audit with the same limitations described above. This remains an unrouted
placement candidate with 499 unconnected items.
