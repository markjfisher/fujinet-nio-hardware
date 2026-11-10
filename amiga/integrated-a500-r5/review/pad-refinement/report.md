# R5 milestone 1 — pad-level refinement for approval

[Full close-up with pad nets](pad-nets.png) · [Zoomable SVG](pad-nets.svg) ·
[North / USB / regulator detail](north-pad-nets.png) · [Southern row](south-pad-nets.png).
These are native KiCad plots with a read-back annotation layer, not GUI screenshots.
White text is `pad:net` (hierarchical prefix omitted); [CSV](pad-nets.csv) retains full names.
Green rings mark **proposed**, clearance-checked ground-via sites; no vias or tracks exist.

The R5 guide remains the acceptance specification. U20 remains at (42,60), 0°.
All other clusters, staging, mechanical datums, reserved regions, locks and group memberships
are unchanged. Only 18 RP support footprints moved; six more received label-only changes.
All placement and label edits used kicad-mcp. R4 is untouched.

| Focus | Change / result | Acceptance evidence |
|---|---|---|
| R22/R23 USB | Parallel 90° packages at (41,48.4)/(42.8,48.4), source pads south, outgoing pads north | DP/DM pad-centre distances now 6.35/5.96 mm; mismatch 0.39 mm, previously 1.16/6.15 mm with 4.99 mm mismatch. This increases total direct distance to obtain a coherent, balanced escape |
| Regulator | L20/R24/C23/C24/C25 physical geometry unchanged | Every pad compared against Raspberry Pi's downloadable minimal-board regulator cell; exact translation, including the intentional L20 numbering reversal. Labels clarified without moving this circuit |
| Flash | U21 moves from (35,45) to (34,48); C20/R20/R13 follow their own supply/CS pins | All six direct QSPI pad distances improve; sum 72.28→62.90 mm (13.0%). No intrusion into regulator, USB or reserved floorplan areas |
| Southern bypass row | C28/C29/C39 at common y=68, 270°; x=39.4/41.4/43.8 | Each courtyard is 1.47 mm from U20; copper edge setback 1.475 mm. C28→24 and C29→29 line up directly; C39→32 retains a modest lateral offset to leave crystal escape space |
| Other bypass rows | Right row x=50, 2.1 mm pitch; north row y=52.4 with consistent vertical orientation | Pin ownership individually checked. Left row retained: its existing setbacks and clearances passed. Ground pads face outward; none of the capacitors was assigned by visual proximity alone |
| Ground-via space | 18 sites for C20, C23–C39 checked at 0.6 mm diameter / 0.3 mm drill | Conservative foreign-pad bounding-box clearance ≥0.325 mm, versus 0.125 mm board clearance; pairwise via separation checked. Coordinates in pad-checks.json. No via or route was added |
| References | Matched USB labels, consistent capacitor-row references, revised regulator labels | Zero native silk-over-copper, silk overlap or courtyard-overlap findings; close-ups visually inspected |

## Regulator net evidence

The actual saved pads are:

- L20.1 = RP_LX, right at (45.7,51.35); L20.2 = RP_DVDD, left at (44.3,51.35).
- R24.1 = 3V3; R24.2 = RP_VREG_AVDD, feeding C23.1 and U20.61.
- C23.2, C24.2 and C25.2 = GND.
- C24.1 = 3V3 / U20.64; C25.1 = RP_DVDD / U20.65.

Compared with [Raspberry Pi's actual Minimal KiCad download](https://datasheets.raspberrypi.com/rp2350/Minimal-KiCAD.zip):
`RPI-RP2350A-MINIMAL_R4-S1.kicad_pcb`, SHA256
`cde2b7e54bf25b443972b8b31214f7880428c40be70d9df9dbd3d0a41fc50b86`.
Its common regulator cell matches ours under translation (−57,−41.45) mm relative to the
LX connection. Source L1.1/DVDD maps to our L20.2; source L1.2/LX maps to L20.1.
All other capacitor/filter pad numbers and power roles match directly. The RP2350B
anchor offsets also match the existing licensed B reference mapping. Thus physical winding
orientation and capacitor/filter arrangement survive the numbering change.

The [Raspberry Pi hardware guide §§2 and 5](https://pip-assets.raspberrypi.com/categories/1214-rp2350/documents/RP-008280-DS-1-hardware-design-with-rp2350.pdf)
explains the orientation-sensitive regulator layout and USB series termination. Reference
placement does not establish reference copper: the switch node, returns, thermal grounding
and copper exclusions must still follow that layout during the separately approved routing stage.

## Routing intent and limits

The USB pair has an available approach on the west side of the regulator, between the
northern supply capacitors and L20, then fans to the two south-facing resistor pads.
Keep both lines on the same continuous reference plane, avoid the LX copper, and match
actual escape lengths during routing. The measured 0.39 mm is **straight-line placement
imbalance**, not a routed length or impedance result. The proposed ground vias leave this
approach available; they are planning evidence, not copper already accepted by DRC.

C28→U20.24 and C29→U20.29 now have 2.325 mm pad-centre separations; C39→U20.32
is 2.616 mm. The gap between C29 and C39 is left for XIN/XOUT escape. R21 moves to
(46.4,70), with unchanged nets, to keep clear of that row's ground-via sites. Crystal and
load-capacitor positions are unchanged. [Capacitor ownership](capacitor-ownership.json)
records every actual pin/net assignment and distance.

## Validation and stop gate

- [Preservation check](verification.json) and [pad checks](pad-checks.json) pass. Full parsed
  board comparison confirms unselected footprints/text, board graphics, rules, regions and groups
  unchanged; every footprint/pad UUID, net, local geometry and lock retained. Zero tracks/vias.
- Native [DRC/parity](drc.json): no new findings; zero parity errors. Remain: four inherited J1
  hole-clearance errors, 199 existing 0.6 mm versus 0.8 mm text-height warnings, 499 unconnected items.
- MCP audit(all) reports zero footprint/silkscreen overlaps; its 172 staging/boundary reports
  remain. MCP DRC agrees with native counts. No schematic change; prior ERC findings remain applicable.
- Native rendered views inspected. Green circles are review annotations only and are absent in KiCad.
- Reproduce: `verify.py`; `check_pads.py PATH_TO_EXTRACTED_REFERENCE_PCB`; `annotate_plot.py`
  after a fresh KiCad `native.svg` export. These scripts only inspect or render, never place components.

**Stopped for approval.** This refines milestone 1; it does not approve routing or placement of another cluster.
