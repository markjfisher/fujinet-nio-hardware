# Zorro-II mechanical cross-check — updated 2026-09-11

**NOT FABRICATION-READY.** No PCB, footprint, copper, schematic or pin-map
changes were made. Pitch, finger width, nominal thickness and nominal tongue
width are supported. The complete stepped insertion profile is not established
by these references; their conflicting dimensions have not been averaged.
The EDAC follow-up below establishes nominal seating/contact datums, but
does **not** remove the fabrication hold. This follow-up changes this report
only; electrical mapping, routing and all CAD remain unchanged.
The **WingTAT follow-up** below now identifies the actual mating socket and
supersedes EDAC/TE as the connector-specific evidence. It supplies a readable
bevel recommendation, but does not yet remove the fabrication hold.

## Measurements

All values are **mm**, except angles. Measurements use copper-pad boundaries
and the **centreline of Edge.Cuts**, not the drawn line's outer stroke.
Setback means distance from the finger's insertion-end copper to the planar
board tip, **before beveling**. Projection means tip to a physical shoulder;
it is not finger length or the height of a mask opening. `—` means not specified
or not recoverable; `N/A` means the feature does not exist on that board.

| Feature | Breakout now | VA2000 | RIPPLE-IDE A5 | AmigaSID rev 2 | A2000 EATX R3.1 | Commodore evidence |
|---|---|---|---|---|---|---|
| PCB thickness | 1.6 | 1.6 CAD | 1.6 CAD + ordering notes | 1.6 CAD/stack | 1.6 **motherboard** | No legible thickness callout in inspected A-5 |
| Contact pitch; extreme span | 2.54; 124.46 | 2.54; 124.46 | 2.54; 124.46 | 2.54; 124.46 | 2.54; 124.46 **socket tails** | A-5: 49 × 2.54 = 124.46; HRM p. 428 corroborates span |
| Finger width × length | 1.524 × 5 | 1.524 × 5 | 1.524 × 6.754 | 1.524 × 10 | N/A, socket pads 1.31 ×1.31 | Detail insufficiently legible for numeric transcription |
| Finger-to-tip setback | 1 | 0.040 | 0.955241–0.955245¹ | 0.1016 | N/A | — |
| Tongue / insertion-region width | 129.26 | 127, entire card width | 129.235206 between side flats | 130.048, entire card width | N/A | **129.26 ±0.1**, A-5 and HRM p. 428 |
| Tongue projection | 7.62 | N/A: no shoulders | N/A: no shoulders | N/A: no shoulders | N/A | Not established for Zorro-II by the legible dimensions² |
| Shoulder / corner geometry | Square roots and tip corners | No shoulders; square corners | No shoulders; tip corners R≈1.27 | No shoulders; square corners | N/A | A-5 shows **R1.5** shoulder detail; other detail not fully legible |
| Bevel | Unspecified, release held | No numeric callout found | **45°** ordering instruction; depth/land absent | No numeric callout found | N/A on motherboard; see TE evidence below | Bevel shown on A-5; complete numeric callout unreadable |
| Mask expansion per finger edge | 0; separate 1.524 × 5 openings | +0.2; 1.924 × 5.4 openings | 0 on pads **plus blanket opening**³ | 0; 1.524 × 10 openings | +0.05 on socket pads, not card fingers | No mask clearance specification found |

¹ RIPPLE's nominally horizontal tip differs by 0.000004 mm between endpoints.
This is stored CAD precision, not a manufacturing tolerance. Do not round the
0.955245 setback to 1.000 and call them identical.

² A-6 explicitly gives 7.62 for the **video card**, not the 100-pin Zorro card.
The 7.62 near the top of A-5 is a mounting-hole offset, not tongue projection.
HRM pp. 427–430 describe Zorro-III form factors; p. 391 directs Zorro-II
designers to the A500/A2000 TRM. Zorro-II/III share the connector, but neither
a scaled picture nor an unrelated dimension supplies the missing detail.

³ RIPPLE's front/back mask polygons span x=80.895…212.975,
y=108.520445…117.410445, with 0.1-wide boundary stroke. Their geometric
rectangle is 132.08 ×8.89, extending beyond the board tip. This removes
inter-finger mask dams. It is not equivalent to zero-expansion isolated pads.

## Recommendations and confidence

Confidence concerns applicability to this breakout, not accuracy of reading
the CAD. An exact CAD value is not proof of a universal Zorro requirement.
The EDAC-based contact and projection assessments in this table are historical;
use the WingTAT follow-up and final release decision for the identified socket.

| Feature | Recommended disposition/value | Confidence; unresolved discrepancy |
|---|---|---|
| Thickness | Retain 1.6 nominal | High nominal: three cards agree. Finished-thickness tolerance must fit the mating connector, not just the CAD field. |
| Pitch/span | Retain 2.54 / 124.46 | High: Commodore, all cards and socket agree. |
| Finger width | Retain 1.524 | High across three cards. EATX's unused card-edge library is not contrary manufactured evidence. |
| Finger length and setback | Retain review geometry only; no replacement pair selected | Medium for nominal EDAC contact-point coverage (see follow-up); low for guaranteed wipe/engagement over tolerances. VA's 5-long fingers start 0.040 from the tip; RIPPLE and SID use longer fingers. |
| Tongue width | Retain 129.26, fabrication tolerance ±0.1 | High: Commodore is controlling; RIPPLE fits this interval. VA's 127 and SID's 130.048 are out-of-interval alternatives, not new tolerances. |
| Projection/shoulders | No released value yet; R1.5 is the sourced Commodore root detail | EDAC's 8.38 slot is deeper than the current 7.62 projection. TE gives a typical 7.62 **minimum** for its family. Neither releases this profile for every intended socket. |
| Bevel | Actual-socket WingTAT recommendation below supersedes the earlier 45° candidate; CAD/fabrication integration held | High drawing confidence; differs from RIPPLE + TE, and must not be combined with their dimensions. |
| Mask | No universal numeric margin selected | Conflicting implementations: +0.2 isolated, zero isolated, and blanket opening. Obtain registration allowance for the selected contact/wipe envelope; do not average them. |

## Evidence qualifications that affect the decision

**Library versus manufactured outline.** RIPPLE's library `F.Fab` guide has
a 129.54-wide tongue, 7.400 projection, R1.241 roots and R1.27 tip corners.
These follow directly from x=−2.54…127 and y=−3.027…4.373. They are **not
Edge.Cuts**, and are not present as shoulders in the shipped board/Gerbers.
Consequently, copying that guide would not copy RIPPLE's tested outline.

EATX is a motherboard. Its five 100-pin Zorro socket footprints have 2.54
longitudinal pitch, 5.08 row spacing and 0.8 drilled holes. The footprint's
inherited name mentions Samtec HLE, but the shopping list specifies
**A121376-ND**, identified as [TE 5645235-3][socket-id]. Do not infer the mating part
from that library name. The 5.08 CAD tail-row spacing also differs from TE's
4.85 drawing value; neither is the card's 2.54 contact pitch, and neither
establishes daughter-card geometry. Its separate, **unused** `ZorroCardEdge.kicad_mod`
has 1.78 ×7.62 pads and a 129.286-wide `F.Fab` box; it is not an EATX
daughter-card manufacturing reference.

**Manufacturer follow-through.** [TE's 5645235-3 drawing][te-drawing]
(C1) specifies 2.54 pitch, 124.46 extreme span, a 7.49-deep socket and
acceptance of 1.37–1.78-thick cards. Its **1.52 ×45° callout describes the
connector housing**, not the PCB bevel. The associated
[application specification 114-13018, rev C][te-app], Figure 4, p. 6,
shows a *typical* shouldered daughter card with 7.62 minimum projection,
0.38 ×45° bevel on both faces and 1.57 ±0.20 thickness. It also uses a
different pad pattern; §3.7 requires the specific connector drawing to
control the daughter card. This is useful corroboration for the EATX socket,
not permission to import every typical dimension into the original Amiga
slot/A500 adapter design. The actual adapter socket is not identified here.

**Working status is bounded.** RIPPLE states tested/working; AmigaSID reports
operation on an A500 with a Zorro-II adapter and NanoSwinSID. VA2000's project
documents operating hardware. These are author reports, not measurements of
physical samples of the exact downloaded revisions. EATX identifies R3.1 as
production. None supplies an as-built bevel-depth inspection record.

## EDAC 395-100-520-202 follow-up (historical comparison)

Inspected the [part-specific EDAC drawing][edac-part], issue 1,
2017-05-16, both sheets, and the [345/395 family ordering/mechanical
guide][edac-family], all three pages. Section A-A and the family's dual-row
section agree. Values below are **printed nominal dimensions**, not measured
from illustration scale. The part drawing supplies no explicit tolerance for
slot depth/contact height; do not import the family's A–E length tolerances.

| Item | Connector-derived evidence | Confidence / limit |
|---|---|---|
| Slot mouth to floor | 0.330 in (8.38 mm) | High nominal, both drawings; not a minimum insertion instruction |
| Contact point above slot floor | 0.160 in (4.06 mm) | High datum reading; **not** 4.06 below the mouth, and not a specified wipe length |
| Accepted card thickness | 0.054–0.070 in (1.37–1.78 mm) | High, family section; current 1.6 nominal is inside |
| Recommended daughter-board contact area | Family p. 2 labels the full-width finger portion 0.350 in (8.89 mm), width 0.055 in (1.40 mm) | High drawing reading; 8.89 is **not a shoulder-to-tip projection callout**. Current 5 mm fingers do not reproduce this recommendation |
| Bevel | No PCB through-thickness bevel angle/depth/land specified in these documents | Unresolved; drawn planar corner clips cannot supply a bevel specification |
| Solder mask | No mating-pad mask expansion, registration tolerance or mask-free wipe envelope specified | Unresolved; drawing hatching is not a mask-layer definition |

### Nominal fit/contact calculation — inference, not acceptance

Use `z` measured upward from the PCB tip. With a flat card bottomed against
the slot floor, the nominal contact point is `z = 4.06`. Its depth below the
socket mouth is `8.38 − 4.06 = 4.32`. If the breakout's square shoulders stop
on the mouth at 7.62 insertion, the tip remains `8.38 − 7.62 = 0.76` above
the floor and the contact point is `z = 7.62 − 4.32 = 3.30`.

This assumes aligned, rigid nominal geometry, shoulder bearing on the mouth,
and the section's contact datum; it omits tolerances and contact-beam movement.
It establishes neither permission to operate partly seated nor required
normal force. **Do not lengthen the tongue automatically to 8.38 or 8.89.**
The actual A500 adapter socket is still unidentified, and EDAC's 8.38 floor
depth differs from the previously inspected TE socket's 7.49.

| Existing card | Copper interval `z`, from earlier CAD/Gerber measurements | Contains nominal EDAC bottomed point 4.06? |
|---|---|---|
| Breakout | 1.000…6.000 | Yes; also contains the conditional shoulder-stopped point 3.30 |
| VA2000 | 0.040…5.040 | Yes |
| RIPPLE | approximately 0.955245…7.709245 | Yes |
| AmigaSID | 0.1016…10.1016 | Yes |

This improves confidence in **static nominal coverage**, not guaranteed wipe.
In a fixed-point sliding model, the breakout provides `3.30 − 1 = 2.30` mm
of travel over copper before shoulder stop, versus `4.06 − 1 = 3.06` if
bottomed. These are calculated travel distances, **not EDAC minimum-wipe
ratings**. Initial contact, deflection, contact-patch extent, lateral
misalignment and tolerance limits are unspecified. The other cards' lack of
shoulders does not prove that the breakout's partial seating is acceptable;
their reported working status does not identify an EDAC 395 test socket.

Neither a nominal point inside copper nor those travel calculations qualify
the zero-expansion mask openings. VA's +0.2 margin, RIPPLE's blanket opening
and AmigaSID's zero margin remain differing implementations. Likewise,
RIPPLE's 45° instruction and TE's typical 0.38 ×45° do not become EDAC
requirements. No new bevel or mask value is selected.

**Result:** EDAC resolves the nominal socket/contact datums, but leaves
partial-seating acceptability, tolerance-qualified contact/wipe coverage,
bevel and mask process requirements unresolved. **NOT FABRICATION-READY.**

Source integrity: part PDF SHA256
`0384f67a1704274b4f7b254c9e0ad28875bf2c4b1b7ae60d97406b56787957a2`;
family PDF SHA256
`2f5ab5d6977298b7f48897a83db9bb8e95164720aea358619687f4ba9bb9188a`.
The part PDF was obtained from EDAC's own file host and matches the initially
located distributor mirror byte-for-byte. No physical sample was measured.
Follow-up verification: `python scripts/test-mechanics.py`, the unchanged
design SHA256 check and `git diff --check` passed. The nominal calculations
above were checked against the retained pad coordinates using decimal
arithmetic. ERC/DRC were not rerun for this documentation-only follow-up;
the previously checked CAD is byte-for-byte unchanged.

## WingTAT actual-socket follow-up — 2026-09-11

User identifies [LCSC C5173320][wingtat-product] as the actual socket:
**WingTAT ED100BGFBK**. Its linked [EDxxxBGFBK drawing][wingtat-drawing],
revision A, sheet 1/1, is legible. EDAC is now comparison evidence only;
its contact-position calculation is **not applicable evidence for WingTAT**.

### Printed values (mm)

| Drawing location | Value | Confidence |
|---|---|---|
| 100-position row; socket top view | Pitch 2.54 ±0.05; A 124.46 ±0.20; slot length B 129.84 ±0.30 | High |
| Socket section, upper centre | Mouth-to-floor 9.00; title-block two-decimal tolerance ±0.10 | High reading; not an insertion instruction |
| Recommended card, lower left | Thickness 1.57 ±0.15; width B 129.84 ±0.20; fingers 1.60 wide, gaps 0.94 | High |
| Same card face view | Tip-to-finger-top 8.00 ±0.20; tip-to-finger-bottom 1.54 | High; no shoulder datum |
| Card section, lower centre | Both-face bevel 20.0° to board face, axial extent 1.54, remaining tip land 0.45 | High |
| Title block | Unqualified two-decimal dimensions ±0.10; one-decimal angles ±0.5° | High; explicit tolerances override |

Contact height/wipe, permissible partial seating, shoulder profile and mask
clearance are **not specified**, rather than unreadable. The second
“Recommended Card Layout” is the socket's host-board drilling, not fingers.

### Comparison and disposition

Current thickness 1.6 is nominally compatible; the finished-board tolerance
still needs specifying. Retain the Commodore tongue width, not the wider
WingTAT card recommendation. Calculated total slot clearance at the proposed
Commodore maximum width is `129.54 − 129.36 = 0.18`; this is longitudinal
clearance only, not a shoulder or lateral-contact qualification.

Assuming shoulders bear at the socket mouth, the current 7.62 projection
stops the tip **1.38 nominally short of the floor** (`9.00 − 7.62`). That
does not prove failure, but neither establishes permissible seating. Do not
change projection to the slot depth without qualifying the shoulder shape.

The recommended copper interval is **z=1.54…8.00**, calculated length 6.46,
versus the breakout's **z=1.00…6.00**, length 5. Neither the VA2000's equal
length nor the longer RIPPLE/SID fingers validates this combination in the
identified socket. None of their recorded evidence identifies this exact
mating part. Without a contact datum, the previous EDAC point-coverage and
wipe calculations cannot be repeated for WingTAT.

The bevel drawing resolves the missing **socket-specific nominal bevel**.
It does not support retaining the earlier 45° candidate. Applying its axial
extent unchanged would reach 0.54 into the current copper interval
(`1.54 − 1.00`), so this cannot be treated as a fabrication-note-only change.
The board maker must resolve which bevel dimensions control across finished
thickness tolerance and how copper/finish terminate. No dimensions are
averaged, and no CAD is changed pending review.

The isolated zero-expansion mask openings remain unqualified. A blanket
opening is supported as a working-card precedent by RIPPLE, but its precise
extent and the selected fabricator's registration allowance still need
approval for this board. Connector drawing shading is not a mask definition.

### Assets for human cross-check

These are existing local assets, not new independent sources:

| Asset | What to inspect / limitation |
|---|---|
| `/tmp/zorro-reference.JbSlda/fingers-detail.png` | Best focused A-5 crop: faded vertical dimension left of fingers, lower-left tip/chamfer leader, and bevel annotation above the lower sectional view. Full numeric transcription remains unreliable. |
| `/tmp/zorro-reference.JbSlda/a5.png` | Upright complete A-5; detail at right provides context for the crop. |
| `/tmp/zorro-reference.JbSlda/detail.png` | Full scanned spread: A-5 on left, A-6 on right. A-5 is rotated/faint. |
| `/tmp/zorro-reference.JbSlda/scan5-a5.png` | Despite filename, this is **A-6 video card**, not the 100-pin A-5. Do not use its 7.62 as the missing Zorro dimension. |
| `/tmp/zorro-wingtat.zWCKfj/EDxxxBGFBK.pdf` | New exact-socket source, one page; readable. Check upper-centre socket section and lower-centre card bevel. |
| `/tmp/zorro-wingtat.zWCKfj/drawing-large.png` and `card-section.png` | High-resolution rendering and bevel crop for inspection; readable, not additional evidence. |
| `/tmp/edac-mechanics.WibJ0C/part-edac.pdf`, `family.pdf` | Earlier readable EDAC sources, not the selected socket; missing bevel/mask requirements cannot be recovered by magnifying them. |
| `/tmp/zorro-mechanics.kjTyKu/te-application.pdf` | Readable Figure 4, printed p. 6: earlier **typical TE** bevel, not a WingTAT requirement. |

WingTAT PDF SHA256:
`c1ea539601b0ea821a9cdbd0b26ef051f1474a121ecf388562e0d5f95b0c9a9f`.
Temporary assets are inspection aids; the source URL and hash above identify
the drawing independently of their retention.

Follow-up verification: after sourcing the workspace environment,
`python scripts/test-mechanics.py`,
`sha256sum -c review/mechanics/design-unchanged.sha256` and `git diff --check`
passed. The measurement test emitted KiCad enum-choice assertion diagnostics
but completed successfully. This follow-up edits documentation only; PCB,
schematic and mapping hashes are unchanged. ERC/DRC were not rerun because
no CAD changed; earlier results above are historical, not a new run.

## Reproduction and source revisions

Raw read-only measurements, including all 100 pad coordinates, outline
segments/arcs and source-file SHA256, are in [review/mechanics](../review/mechanics/).
The extractor does not save/convert the source boards. Example, with each
repository checked out at the revision below:

```sh
export NIO_WORKSPACE=/home/markf/dev/nio/fujinet-nio-workspace
source "$NIO_WORKSPACE/scripts/env.sh"
python scripts/measure-mechanics.py kicad/zorro-breakout.kicad_pcb J1
python scripts/measure-mechanics.py /path/to/RIPPLE-IDE/Kicad/RIPPLE.kicad_pcb CN1
python scripts/test-mechanics.py
python scripts/check.py
sha256sum -c review/mechanics/design-unchanged.sha256
```

Verification completed with KiCad 10.0.5: measurement tests passed for all
five datasets; all 100 contacts and 14 duplicate signals passed the existing
checker, including five negative cases. ERC: **0 violations**. DRC:
**0 violations, 0 unconnected items, 0 parity issues**. The hash check passed
after DRC: PCB, schematic and both mapping CSVs are byte-for-byte unchanged.
No geometry or manufacturing outputs were regenerated. These checks validate
stored geometry and connectivity, not mechanical compatibility.

| Source/revision | Measured board and manufacturing cross-check |
|---|---|
| [VA2000 a512aabb][va] | `kicad/amiga-gfxcard.kicad_pcb`, CON-Z21; `gerbers/amiga-gfxcard-{F_Cu,B_Cu,F_Mask,B_Mask,Edge_Cuts}.gbr` |
| [RIPPLE a87ed5c9][ripple] | `Kicad/RIPPLE.kicad_pcb`, CN1; `Gerbers/RIPPLE-*` copper/masks/outline; README ordering notes |
| [AmigaSID dab5f880][sid] | `Hardware/AmigaSID.kicad_pcb`, CON1; `Hardware/jlcpcb/gerber/GERBER-AmigaSID.zip` copper/masks/outline |
| [EATX dfde4574][eatx] | `2000EATX-KiCAD-R31/2000ATX.kicad_pcb`, CN601; `BOM/A2000EATX-REV31-ShoppingList.csv`, `PCB.md` |

Card Gerbers confirm the tabulated copper, mask and planar outlines. RIPPLE
uses an auxiliary plotting origin: (82.305, 116.27689) in PCB coordinates;
account for that translation and Gerber Y reversal before comparing values.
Setback calculations: current 127.62−(124.12+2.5)=1;
VA 139.573−(137.033+2.5)=0.040;
RIPPLE 116.28969−(111.957445+3.377)=0.955245;
SID 134.89−(129.7884+5)=0.1016. Bevels are not encoded by these planar Gerbers.

Commodore sources: [HRM third edition][hrm], printed pp. 391, 427–430;
[TRM A-5][trm], PDF p. 280 left drawing. Hashes are in
[reference-review.md](reference-review.md). EATX's bundled TRM was also
checked: PDF p. 243 is partial A-4 and p. 244 is A-6, not a clearer A-5.
TE drawing SHA256: `17d170c80c59168e7105ea549a254bf7fedf5cdbe16cf4c8e9b9c63bb4e569a9`;
application PDF: `64ee09e3122c0e99fe57f16eacccc04bb014b2287ca881ee16ad8193e1e8d80b`.

## Release decision

**NOT FABRICATION-READY.** Exactly these mechanical release items remain:

1. **Seated insertion/contact envelope:** qualify the current stepped
   outline, or a supported replacement, for WingTAT ED100BGFBK. Establish
   permissible seating, contact/wipe coverage and tolerances. The socket is
   now identified, but its drawing does not supply the needed contact datum
   or partial-seating acceptance. None of the three reference cards validates
   this stepped combination in that socket.
2. **Bevel/copper manufacturing integration:** reconcile WingTAT's now-readable
   bevel recommendation with finger setback/length, finished thickness and
   fabrication tolerances; approve a consistent manufacturing callout.
   Do not retain 45° by default or bevel into existing copper without review.
3. **Mask registration allowance:** specify/approve openings that keep mask
   off the required contact/wipe area at manufacturing tolerances. The current
   zero-expansion, isolated openings are measured, not process-qualified.

Then update the mechanical CAD/fabrication notes as supported and rerun the
checks/exports. No electrical redesign is required by this review. Nothing
was ordered. Hardware operation and production-process approval are not
implied by electrical DRC.

[va]: https://github.com/mntmn/amiga2000-gfxcard/tree/a512aabb95d28c2b844760b6c8536440c317a4c6
[ripple]: https://github.com/LIV2/RIPPLE-IDE/tree/a87ed5c9e8ecc55eed080cf1763fcd71e5b707a9
[sid]: https://github.com/call286/AmigaSID/tree/dab5f880e6e925596db0910db8779e43bc5f790d
[eatx]: https://github.com/jasonsbeer/Amiga-2000-EATX/tree/dfde4574396919e9cc51f5079ef054e4de3b9a07
[hrm]: https://www.ikod.se/wp-content/uploads/2020/08/Amiga_Hardware_Reference_Manual_3rd_Edition.pdf
[trm]: https://erikarn.github.io/amiga/docs/Amiga_500_Technical_Reference.pdf
[te-drawing]: https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=5645235&DocType=Customer+Drawing&PartCntxt=5645235-3
[te-app]: https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=114-13018&DocType=Specification+Or+Standard&PartCntxt=5645235-3
[socket-id]: https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/5645235-3/1122009
[edac-part]: https://files.edac.net/edac/content/395/395-100-520-202%20-%20EDAC%20Card%20Edge%20Connector.PDF
[edac-family]: https://files.edac.net/edac/content/series/og/English/EDAC%20345%20395%20Series%20Card%20Edge%20Connectors%20English%20Ordering%20Guide.pdf
[wingtat-product]: https://www.lcsc.com/product-detail/C5173320.html
[wingtat-drawing]: https://datasheet.lcsc.com/datasheet/pdf/71aee04542fa26ea605dbae05f1ac670.pdf?productCode=C5173320
