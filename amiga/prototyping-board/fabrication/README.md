# Fabrication instructions — revision A, REVIEW ONLY

**DO NOT ORDER FROM THIS PACKAGE YET.** No board has been ordered. The bevel
callout in the available A-5 scan is not legible enough to release to a
manufacturer. Confirm bevel depth/angle using a legible original drawing or
the selected mating connector manufacturer's specification. Do not let a
default online ordering option silently supply that missing dimension.
The current 7.62 mm tongue projection, 1 mm contact-to-tip offset and square
shoulders are provisional review geometry, not verified connector dimensions.
Confirm the insertion depth and shoulder-radius/profile as well as the bevel,
then update the outline/contact placement and rerun routing and checks as
needed. The supplied outline must not be released unchanged on the strength
of its electrical DRC pass.

## Board and stack

* Four copper layers; finished board thickness **1.6 mm**, including finishes.
* FR-4; nominal 35 µm copper per layer. Stack order is F.Cu / In1.Cu GND /
  In2.Cu / B.Cu. In1 is reserved for the ground plane; no signal tracks there.
  Specify a symmetric stack with thin outer dielectric spacing to the inner
  layers. Exact laminate stack and thickness tolerance require fabricator
  agreement; this design does not claim controlled impedance.
* Outer board: 180 ×100 mm above the shoulder; 107.62 mm overall height.
  Zorro tongue: **129.26 ±0.1 mm**, 7.62 mm projection, 124.46 mm extreme
  contact-centre span. See the mechanical review for source qualifications.
* Fingers: 50 per face, **2.54 mm pitch**, **1.524 ×5 mm copper contact area**.
  Even pads on component face; odd pads on reverse. Extreme right pair is
  2/1 viewed from the component face. Do not mirror Gerbers for manufacture.
* Nominal trace width 0.30 mm; minimum allowed 0.25 mm. Clearance 0.20 mm.
  Via diameter 0.65 mm / hole 0.30 mm. Header plated holes 1.00 mm with
  1.70 mm pads. Exact hole counts appear in `drill/report.txt`.
* Copper-to-outline clearance is 0.50 mm minimum. The fingers stop 1.00 mm
  short of the insertion edge. Keep all internal copper out of the tongue
  and bevel machining region. No via or drilled hole belongs in a finger.

## Contact finish and edge preparation

Use **selective hard gold over nickel on the mating contacts** for repeated
insertion/probing service. The rest of the board may use ENIG. Confirm gold
and nickel thickness, contact durability and the manufacturer's plating
process before release. Ordinary HASL or solder-tinned fingers are not an
acceptable substitution. The design intentionally has no solder-paste
apertures on the fingers; no stencil is required for this all-through-hole
assembly.

Chamfer/bevel both sides of the insertion edge only after the unresolved
Commodore/mating-connector dimension is confirmed. The final machining must
not remove the working gold contact area. The bare PCB edge must be smooth
and free of burrs. No breakaway tabs, mouse bites, tooling holes, panel rails,
plating-bus remnants or conductive debris may remain on the mating edge.
Any temporary electroplating connections must be fully removed so all 100
contacts retain the net assignments in the verification CSV.

F.Mask and B.Mask contain explicit openings for every mating contact.
Do not mask, silkscreen or apply solder paste over those contact surfaces.
The supplied Gerbers contain no manufacturing panel or plating bus; a
fabricator must provide its own process plan while preserving this finished
geometry. The outline Gerber describes planar routing only: **it cannot
encode an edge bevel or gold plating specification**.

## Package contents and acceptance

`gerbers/`: four copper layers, two masks, two silkscreens, Edge.Cuts and
Gerber job file. `drill/`: Excellon plated/non-plated files, map and report.
`SHA256SUMS` covers the machine fabrication outputs. Units are millimetres;
all layers use the same absolute origin. `review/` contains human-readable
views and electrical/design-rule reports.

Before any future manufacturing release, resolve the insertion profile, bevel and finished
connector fit, agree the stack/finish/tolerances with the manufacturer, and
review the CAM overlay at 1:1. This work does not authorize that release.
After fabrication, visually inspect the finger plating/bevel and test every
J1 contact against `data/verification.csv`, including isolation of opposite
contacts, supply rails, all reserved/NC nets, SenseZ3, and /CFGIN vs /CFGOUT.
Host-powered insertion, loading, timing, current capacity and case/adapter
fit are **not** validated by ERC or DRC.
