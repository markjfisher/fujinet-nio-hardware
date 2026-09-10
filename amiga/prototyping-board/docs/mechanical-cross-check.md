# Zorro-II mechanical cross-check — 2026-09-10

**NOT FABRICATION-READY.** No PCB, footprint, copper, schematic or pin-map
changes were made. Pitch, finger width, nominal thickness and nominal tongue
width are supported. The complete stepped insertion profile is not established
by these references; their conflicting dimensions have not been averaged.

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

| Feature | Recommended disposition/value | Confidence; unresolved discrepancy |
|---|---|---|
| Thickness | Retain 1.6 nominal | High nominal: three cards agree. Finished-thickness tolerance must fit the mating connector, not just the CAD field. |
| Pitch/span | Retain 2.54 / 124.46 | High: Commodore, all cards and socket agree. |
| Finger width | Retain 1.524 | High across three cards. EATX's unused card-edge library is not contrary manufactured evidence. |
| Finger length and setback | Retain review geometry only; no replacement pair selected | Low for the **combined** 5-long / 1-setback / stepped-outline geometry. VA's 5-long fingers start 0.040 from the tip; RIPPLE and SID use longer fingers. Verify the seated contact/wipe envelope before selecting a pair. |
| Tongue width | Retain 129.26, fabrication tolerance ±0.1 | High: Commodore is controlling; RIPPLE fits this interval. VA's 127 and SID's 130.048 are out-of-interval alternatives, not new tolerances. |
| Projection/shoulders | No released value yet; R1.5 is the sourced Commodore root detail | Low for the complete profile. TE gives a typical 7.62 **minimum**, not validation of a 7.62 nominal, square-root outline at all tolerances. |
| Bevel | 45° is supported; depth/remaining land not released | Medium for angle (RIPPLE + TE). TE's typical 0.38 ×45° is conditional evidence, not a verified Commodore callout. |
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

1. **Seated insertion/contact envelope:** confirm projection and shoulder
   profile against a legible 100-pin Commodore detail or identified compatible
   mating socket, including tolerances; establish that the selected finger
   length/setback covers its contact/wipe envelope. None of the three card
   outlines validates the breakout's stepped combination.
2. **Bevel manufacturing callout:** confirm the applicable depth/remaining
   land and tolerances at 45°. A conditional TE typical drawing is available,
   but the Commodore detail and the actual A500 adapter remain unconfirmed.
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
