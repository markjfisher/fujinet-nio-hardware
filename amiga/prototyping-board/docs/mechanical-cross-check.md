# Zorro-II mechanical cross-check

Updated 2026-09-11. **FABRICATION-READY — PROTOTYPE SPIN ONLY.**

Scope: the current breakout mating with **WingTAT ED100BGFBK,
[LCSC C5173320][socket]**. This report records measured CAD, Commodore
dimensions and connector recommendations separately. The approved A-5 outline, 1.6 mm finger width and continuous mask windows
are implemented. Electrical mapping, pad positions and routed tracks/vias
are unchanged. Fabrication outputs are regenerated for PCBWay.

## Controlling evidence

- [Commodore TRM Figure A-5](a5.png): user-supplied clear scan, including
  detail X and the through-thickness bevel view. Dimensions are read directly,
  not scaled from pixels.
- [WingTAT EDxxxBGFBK drawing][drawing]: revision A, sheet 1/1, 100-position
  variant. This is the identified mating connector.
- [HRM third edition][hrm], printed p. 391, directs Zorro-II mechanical
  designers to the A500/A2000 TRM. Printed pp. 427–430 provide Zorro-III
  form-factor corroboration, not a replacement for A-5.
- Three operating-card projects supply CAD/Gerber comparisons; EATX supplies
  motherboard socket-footprint evidence only. Source revisions are below.

All dimensions are **mm**, except angles. CAD outline measurements use the
**centreline of Edge.Cuts**. Setback is insertion-end copper to the planar
board tip before beveling. Projection is shoulder datum to tip. Neither
finger length nor mask-opening height is a projection measurement.

## Card comparison

| Feature | Breakout now | Commodore A-5 | VA2000 | RIPPLE-IDE A5 | AmigaSID rev 2 | A2000 EATX R3.1 |
|---|---|---|---|---|---|---|
| PCB thickness | 1.6 | Not dimensioned on supplied page | 1.6 CAD | 1.6 CAD + ordering notes | 1.6 CAD/stack | 1.6 motherboard |
| Pitch; extreme contact-centre span | 2.54; 124.46 | 2.54; 124.46 | 2.54; 124.46 | 2.54; 124.46 | 2.54; 124.46 | 2.54; 124.46 socket tails |
| Finger width × length | 1.6 ×5 | Width 1.6; length not separately dimensioned | 1.524 ×5 | 1.524 ×6.754 | 1.524 ×10 | N/A; socket pads 1.31 ×1.31 |
| Finger-to-tip setback | 1 | Not separately dimensioned as a copper setback | 0.040 | 0.955241–0.955245 | 0.1016 | N/A |
| Tongue / insertion-region width | 129.26 | 129.26 ±0.1 | 127, whole card | 129.235206 between side flats | 130.048, whole card | N/A |
| Shoulder-to-tip projection | 7.62 | **7.62**, detail X | No shoulders | No shoulders | No shoulders | N/A |
| Shoulder roots | R1.5 | **R1.5** | No shoulders | No shoulders | No shoulders | N/A |
| Planar tip corners | 1.5 ×45° | **1.5 ×45°** chamfer | Square | R≈1.27 | Square | N/A |
| Through-thickness bevel | 0.5 ×45° per face; fabrication instructions | **0.5 ×45° BEVEL** | No numeric callout found | 45° ordering instruction; depth absent | No numeric callout found | N/A |
| Mask expansion per finger edge | 0 on pads plus continuous window | Not specified | +0.2; isolated openings | 0 on pads plus blanket opening | 0; isolated openings | +0.05 on socket pads only |

The **1.5 ×45° planar corner chamfer and 0.5 ×45° thickness bevel are
different features**. A-5's projection is dimensioned in detail X; the 7.62
at the main drawing's top right is a separate mounting-hole offset.

A-5 detail X also specifies **2.5** from an outer contact centre to the
tongue side. Its main width/span dimensions imply centred end margins of
`(129.26 − 124.46) / 2 = 2.40`. The current centred layout has 2.40.
These nominal values differ; no unstated tolerance is assigned to reconcile
them. The user-approved explicit width/span and existing centring control.
The 2.40/2.50 detail discrepancy creates no demonstrated fit conflict and is
not a release blocker; contacts are not shifted to impose the generic detail.

RIPPLE's tiny setback range is stored CAD precision, not a manufacturing
tolerance. Its front/back mask polygons span
x=80.895…212.975, y=108.520445…117.410445, with 0.1-wide boundary stroke:
a geometric 132.08 ×8.89 rectangle extending beyond the tip and removing
inter-finger mask dams. This is not equivalent to isolated zero-expansion pads.

## Actual mating connector

Printed WingTAT values; explicit tolerances take precedence over its title block.

| Item | Drawing value | Confidence / qualification |
|---|---|---|
| Pitch; extreme span A | 2.54 ±0.05; 124.46 ±0.20 | High |
| Slot length B | 129.84 ±0.30 | High |
| Mouth-to-floor depth | 9.00 ±0.10 | High reading; not required insertion depth |
| Recommended card thickness | 1.57 ±0.15 | High |
| Recommended card width B | 129.84 ±0.20 | High; not the Commodore tongue width |
| Recommended fingers | Width 1.60; gaps 0.94; tip-to-bottom 1.54; tip-to-top 8.00 ±0.20 | High |
| Recommended card bevel | Both faces: 20.0° to board face; axial extent 1.54; remaining tip land 0.45 | High |
| General tolerances | Two-decimal dimensions ±0.10; one-decimal angles ±0.5° | High |

The second “Recommended Card Layout” is host-board drilling, not a mating
finger pattern. No contact-height datum, minimum wipe, shouldered-card seating
instruction or solder-mask clearance is specified.

### Fit calculations and limits

- **Width:** using Commodore's maximum tongue width and the socket's minimum
  slot length gives total longitudinal clearance
  `129.54 − 129.36 = 0.18`. This does not qualify root-radius interference
  or contact alignment.
- **Depth:** if the shoulder datum bears on the socket mouth, a 7.62 projection
  leaves a nominal `9.00 − 7.62 = 1.38` gap above the floor. Bottoming is
  not established as necessary. This calculation alone proves neither good
  engagement nor incompatibility; root/housing interaction also matters.
- **Copper:** the recommended interval is z=1.54…8.00, nominal length 6.46,
  versus current z=1.00…6.00, length 5. The drawing does not locate the
  contact patch, so static coverage and wipe cannot be calculated reliably.
- **Bevel:** on a nominal 1.6 board, a symmetric 0.5 ×45° Commodore bevel
  implies a remaining tip land of `1.6 − 2 ×0.5 = 0.6` and starts 0.5
  from the tip. Current copper would nominally clear it by 0.5.
  WingTAT's recommended axial extent instead reaches 0.54 into current
  copper. These are distinct profiles, not interchangeable requirements.
  Fabrication tolerances and finish termination still need approval.

## Prototype release disposition

Confidence distinguishes a readable dimension from demonstrated compatibility.

| Feature | Released disposition | Confidence / validation |
|---|---|---|
| Thickness | 1.6 nominal, order requirement ±0.10 finished | Within WingTAT recommendation; confirm requested tolerance in normal PCBWay CAM review |
| Pitch/span | 2.54 /124.46 unchanged | High; all sources agree |
| Tongue width | 129.26 ±0.1 | High; A-5 controls |
| End margin | Centred 2.40 | No demonstrated conflict with explicit outline; not a hold |
| Projection | 7.62 | High A-5 confidence; seating/wipe are prototype validation |
| Roots/corners | R1.5; planar 1.5 ×45° | Implemented and checked |
| Finger width | 1.6 | A-5 and WingTAT agree; implemented |
| Finger length/setback | Retain 5 /1 | Prototype choice; witness-mark/continuity validation required |
| Thickness bevel | 0.5 ×45° per face; 0.6 centre land REF at 1.6 thickness | A-5 controls; no independent 0.5 land constraint |
| Mask | Continuous F.Mask/B.Mask windows to the board edge, x=38…171.26, y=120…128.12 | Matches PCBWay exposure guidance; inspect manufactured mask |
| Finish | Selective hard gold over nickel | Required by fabrication instructions; inspect supplied finish |

The larger root geometry can determine actual shoulder seating against the
socket housing; the simple 1.38 floor-gap calculation is not a tolerance
stack or proof of the seated position. No demonstrated dimensional
incompatibility has been found. The socket's different recommended bevel and
absent wipe-envelope dimensions are recorded risks, not prototype-release
blockers under the user's approved A-5 control policy.

PCBWay publishes 45° machining, whole-region mask exposure and hard-gold
processing. Its edge-connector help page specifies ±5° and ±5 mil
(±0.127 mm) chamfer-height process tolerances; the capability matrix separately
lists ±0.15 mm normal bevel-depth capability. Neither alters the A-5 nominal
dimensions. Detailed manufacturing requirements, sources and the derived
land calculation are in [fabrication instructions](../fabrication/README.md).
Standard board-thickness tolerance must not silently replace the specified
±0.10 finished requirement. Supplier CAM confirmation is normal order review,
not evidence that the unbuilt prototype has been physically qualified.

No card comparison establishes that its exact measured revision was tested
with this socket. VA2000, RIPPLE and AmigaSID document operating hardware,
but their shoulderless outlines do not validate this stepped geometry.
RIPPLE's library F.Fab guide (129.54 width, 7.400 projection, R1.241 roots)
is not its manufactured Edge.Cuts outline and is not copied as such.

EATX is a motherboard: its socket footprints have 5.08 tail-row spacing and
0.8 drilled holes. Its unused ZorroCardEdge library footprint is not a
manufactured daughter-card reference. Socket-tail dimensions are not card
finger dimensions.

## Source revisions and reproducibility

Historical pre-release measurements, pad coordinates, outlines and source-file hashes:
[review/mechanics](../review/mechanics/).

| Source/revision | Measured board and manufacturing cross-check |
|---|---|
| [VA2000 a512aabb][va] | `kicad/amiga-gfxcard.kicad_pcb`, CON-Z21; `gerbers/amiga-gfxcard-*` copper, mask and outline |
| [RIPPLE a87ed5c9][ripple] | `Kicad/RIPPLE.kicad_pcb`, CN1; `Gerbers/RIPPLE-*`; README ordering notes |
| [AmigaSID dab5f880][sid] | `Hardware/AmigaSID.kicad_pcb`, CON1; `Hardware/jlcpcb/gerber/GERBER-AmigaSID.zip` |
| [EATX dfde4574][eatx] | `2000EATX-KiCAD-R31/2000ATX.kicad_pcb`, CN601; `PCB.md` |

Gerbers corroborate measured copper, mask and planar outlines, not bevels.
RIPPLE's plotting origin is (82.305, 116.27689); account for translation
and Gerber Y reversal. Setback arithmetic:
current 127.62−(124.12+2.5)=1;
VA 139.573−(137.033+2.5)=0.040;
RIPPLE 116.28969−(111.957445+3.377)=0.955245;
SID 134.89−(129.7884+5)=0.1016.

Source SHA256:

- Local A-5 scan:
  `44288a8ac8fe7a9859f9220aa6337786ed5a9ce916d5c0f07a694905029fa1be`.
- WingTAT PDF:
  `c1ea539601b0ea821a9cdbd0b26ef051f1474a121ecf388562e0d5f95b0c9a9f`.

Checks from the prototyping-board directory, after sourcing the workspace
environment:

```sh
python scripts/test-mechanics.py
python scripts/check.py
python scripts/export.py
(cd fabrication && sha256sum -c SHA256SUMS)
git diff --check
```

Mechanical assertions, 100-contact mapping and five negative cases passed.
ERC: **0 violations**. DRC: **0 violations, 0 unconnected items, 0 parity
issues**. No global rule relaxations or per-violation exclusions were added.
J1 alone has KiCad's intentional solder-mask-bridge flag for the continuous
window. KiCad's Python binding emits enum-choice diagnostics but checks finish
successfully.

The pre-change electrical digest is
`67610cbc42d6f03976cf59b8a909f560a1fe18d3ae8fde59059cf2d786920dec`;
tests protect net assignments, pad positions and routed track/via geometry.
Schematic and mapping-file hashes remain unchanged. The historical
`current.json` and `design-unchanged.sha256` describe the original review PCB,
not the new mechanical release; the tests explicitly distinguish them.
Current fabrication outputs and their instructions have their own SHA256SUMS.

## Release decision

**FABRICATION-READY — PROTOTYPE SPIN ONLY.** The user-approved A-5 geometry
is implemented, checked and compatible with the identified nominal socket
dimensions and requested PCBWay process. No demonstrated incompatibility
requires holding this prototype for additional wipe documentation.

Prototype acceptance must establish actual seating/root clearance, contact
witness marks, all-contact continuity/isolation, mask/bevel quality and host
operation. These are listed in the fabrication instructions. This is not
production qualification or a guarantee of compatibility with every Zorro
socket. Nothing was ordered.

[va]: https://github.com/mntmn/amiga2000-gfxcard/tree/a512aabb95d28c2b844760b6c8536440c317a4c6
[ripple]: https://github.com/LIV2/RIPPLE-IDE/tree/a87ed5c9e8ecc55eed080cf1763fcd71e5b707a9
[sid]: https://github.com/call286/AmigaSID/tree/dab5f880e6e925596db0910db8779e43bc5f790d
[eatx]: https://github.com/jasonsbeer/Amiga-2000-EATX/tree/dfde4574396919e9cc51f5079ef054e4de3b9a07
[hrm]: https://www.ikod.se/wp-content/uploads/2020/08/Amiga_Hardware_Reference_Manual_3rd_Edition.pdf
[socket]: https://www.lcsc.com/product-detail/C5173320.html
[drawing]: https://datasheet.lcsc.com/datasheet/pdf/71aee04542fa26ea605dbae05f1ac670.pdf?productCode=C5173320
