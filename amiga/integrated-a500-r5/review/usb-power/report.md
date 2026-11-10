# R5 milestone 2 — USB input/protection and power placement

**Visual review pending. No routing.** The user approved RP milestone 1 at
`8c00c072`; the authoritative root PCB remains byte-for-byte unchanged.
Open [the candidate project](candidate/integrated-a500-r5.kicad_pro) to review
this next cluster. All 36 footprint moves, rotations and reference edits used
kicad-mcp. Native KiCad was used only for grouping (unsupported by MCP),
independent read-back, checks and plotting. No generator or optimiser ran.

- [Whole-board overview](overview.png)
- [Complete cluster with actual pad nets](pad-nets.png)
- [USB/protection detail](input-pad-nets.png)
- [Buck detail](buck-pad-nets.png)

These are native KiCad plots with a read-only pad-net overlay, not GUI captures.
Green rings denote **proposed** 0.6/0.3 mm ground-via sites, not added copper.
The inherited board-title silkscreen still says RP cluster review; board graphics
were preserved. Grey floorplan boxes are planning reservations, not electrical
keepouts. The power cell extends into available space to their right/below.

| Requirement | Placement / evidence | Remaining validation |
| --- | --- | --- |
| Preserve approved RP cell | All 31 RP footprint trees, labels, nets and locks unchanged; existing proposed via sites remain clear | RP copper, crystal and USB pair routing |
| Accessible USB input | J1 faces left at (-3,82), -90°, matching its R4 edge position; D2/D3 close to connector | Enclosure aperture and plug envelope |
| Follow power path | J1 → U8 → U9 → U4 → U5/L1; U6/U3/U7 qualification branch remains separate | Wide power copper and thermal performance |
| Buck reference topology | U5 rotated 180°; input capacitors left, L1 right, C8 below, feedback/SS above | Actual loop area, Kelvin sensing, return copper |
| Legible local geometry | Consistent 0.6 mm text/0.09 mm strokes; native and MCP checks find no new label/footprint overlaps | Fabricator acceptance of text size |
| Preserve wider floorplan | Outline, J40, holes, rule areas and all 167 unselected footprints unchanged | Later clusters remain staged |

## Ownership and electrical intent

Four KiCad groups describe the complete placed cell; all existing footprint
locks are preserved. The RP group's name records its approval; membership and
all RP footprint properties are unchanged.

| Group | Components | Pad-level placement intent |
| --- | --- | --- |
| USB connector and ESD | J1, D2, D3 | D2 presents PC_DP/PC_DM on its connector-facing side; D3 protects CC1/CC2 before U3. Ground-via access is reserved at both protectors. The later data-mux route must escape toward the open area above/right, away from the buck. |
| CC qualification and AON | U3, C3, R4–R6, U6, C4/C5, U7, C123 | C3 serves U3.12; C4/C5 face U6 input/output pins; C123 serves U7.5. R4/R5 are aligned below their owning U3 inputs. U7 feeds U4 POWER_ALLOW. |
| eFuse and reverse blocking | U8/U9, C100–C102, R100–R105 | C100 at U8 IN; C101 by dVdt; R100/R101 UVLO on the left; R102/R103 OVLO and R104 ILM on the right. C102 bridges the U8-output/U9-input region. R105 is the fault pull-up. |
| Main switch and buck | U4, C6, R14, U5, L1, C7–C9, C124, R7/R8, C117 | C6 connects SS to VBUS_PROTECTED, **not ground**; R14 is discharge support. C7/C124 serve PVIN/AVIN, C9 SS, R7/R8 FB, C8 the local output, C117 main-rail bulk/hold-up. |

No values, footprints or connections changed. C117 remains the previously
approved 6SVPC220M/CP_Elec_6.3x5.9; it supplements C8 and does not replace the
ceramic switching-loop capacitor. U1/U2, ESP/SD, bus buffers and host guard
remain staged. C113 remains with the future bus-supply protection cell.

## Manufacturer layout evidence and routing constraints

The buck placement follows the topology of TI's
[TPS62130 datasheet §11, Figure 11-1](https://www.ti.com/lit/ds/symlink/tps62130.pdf),
using the actual saved pad nets. C7/C124 sit at the input side, L1 keeps SW local,
and C8 returns beside PGND. R7/R8 and C9 occupy the quiet side. At routing,
connect AGND/PGND directly to the exposed-pad ground and plane; sense VOS and
FB at C8's output using quiet paths separate from load-current copper. Preserve
space around the existing thermal-hole footprint. Placement alone does not
establish the regulator's current-loop area or stability.

Input support placement follows
[TPS2596 §11](https://www.ti.com/lit/ds/symlink/tps2596.pdf): local input bypass,
short current-carrying paths, nearby dVdt/current-limit/divider components,
and ground-plane attachment. U8 needs exposed-pad ground copper and thermal
stitching during routing; the reserved external ground via is not its complete
thermal design. U9's nearby C102 and open output corridor follow
[LM66100 §11](https://www.ti.com/lit/ds/symlink/lm66100.pdf).

Measured pad-centre separations are placement estimates, **not routed lengths**:
C7→U5 PVIN 2.55 mm; C124→AVIN 2.28 mm; U5 SW1→L1 3.66 mm;
L1→C8 3.20 mm; VOS→C8 5.14 mm. C100→U8 IN is 2.17 mm and
C102→U9 IN is 2.16 mm. Complete endpoints/nets are in
[verification.json](verification.json) and [pad-nets.csv](pad-nets.csv).

Nineteen proposed ground-via locations pass a conservative foreign-pad bounding
box clearance check at ≥0.2 mm, with ≥0.85 mm between proposed via centres.
All previously approved RP via sites remain clear. These sites reserve access;
they do not prescribe the final number of power/thermal/ESD ground vias.
Keep a continuous ground reference, avoid spreading SW copper, and provide
adequate main-rail copper from C8/C117 to the later processor/guard circuitry.

## Verification

- **203 footprints / 199 fitted components**, unchanged; 36 moved from staging,
  131 remain staged in the candidate. Zero added tracks or vias.
- Full unselected-footprint comparison: **167 unchanged**, including pad-level
  RP geometry, all labels, identities, locks and local footprint geometry.
- Native DRC with schematic parity: **0 parity errors, no new violations**.
  The exact violation type/severity/item UUID set matches milestone 1:
  4 existing J1 hole-clearance errors and 199 existing text-height warnings.
  There are 499 expected unrouted connections. No new clearance, courtyard,
  solder-mask or silkscreen violations.
- Native ERC: **31**, identical to the authoritative baseline: 30 pin-not-driven
  findings and the existing U9 ST-to-ground pin-type finding. No new warnings.
- MCP audit: no footprint, pad-label or label-label overlaps. Its 137 boundary
  reports consist of 131 intentionally staged footprints plus J1's deliberate
  shell overhang and the inherited J40/H4 envelope/rule reports. No selected
  component enters the antenna, bus-buffer or connector-clearance regions.
- Candidate schematics, library tables and project rules are byte-identical
  copies. `../kicad` is a relative symlink to the existing hardware libraries,
  preserving the original library-table resolution from the deeper directory.
- [verify.py](verify.py) independently checks preservation, nets, geometry,
  candidate copies and proposed via access; [render.py](render.py) only
  annotates native plots. Neither constructs nor edits PCB placement.

**Stop here for visual approval.** Transfer to the root R5 board and the next
ESP/SD placement remain pending. Fabrication is outside this milestone.
