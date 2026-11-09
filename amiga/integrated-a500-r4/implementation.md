# R4 implementation evidence

## A500 connector

The fitted part is the owner's **WING TAT ED86BGFBK**. The
[Wing Tat ED family drawing](https://assets.ebee.com/datasheet/ED18BGFBK/166525.pdf)
includes the 86-contact variant: 2.54 mm pitch, 106.68 mm contact span,
115.51 mm overall width, 5.08 mm stock tail-row spacing and 3.8 mm tail length.
The family drawing identifies a straight DIP connector. A horizontal
edge-solder assembly therefore needs formed tails; an unmodified stock socket
is not being represented as a ready-made straddle-mount part.

The decisive assembly footprint is `LKONT_43-SLOT-SOLDER` in Matze's
[original Eagle library](https://gitlab.com/MHeinrichs/Amiga-EagleCAD-library),
commit `f0a859e277bc0c632d10967e9951d1f7e595259f`. It has odd contacts 1–85
on the top face and even contacts 2–86 on the bottom. Centers span
−53.34 to +53.34 mm at 2.54 mm pitch. Lands are 1.65 × 9.5 mm; their centers
are 5.334 mm inside the board edge. These dimensions agree with the supplied
A-Zorro-Edge-2b Gerbers. The native check asserts every contact's number,
face, position, dimensions and absence of solder-paste apertures.

The custom footprint records factual land geometry, not a copy of the whole
Eagle library. The board edge is local x=0; the sidecar is at negative x.
Placement is (105,62) mm, so the connector occupies the right side of the
111 × 117 mm board. Socket plastic and the Amiga case extend beyond this PCB
outline; the outline is not an enclosure drawing. Tail forming, insertion
clearance, vertical board position, underside clearance and enclosure supports
remain mechanical qualification items. The manufacturer's 1.57 ±0.15 mm card
thickness refers to the mating edge, not automatically to the sidecar PCB.

## Owner-measured mechanical refinement

The owner measured approximately 117 mm along the connector on the working
adapter and 18 mm from its right PCB edge before components. The original R4
outline was 124 mm long; it added 3.5 mm at each end. The revised rectangle
removes those end margins while preserving the socket position and pad pitch.
All electronics move 6 mm away from the Amiga, keeping their relative placement
and yielding a 111 × 117 mm envelope. Mounting holes and recovery switches are
repositioned inside that envelope. The upper-left support is inset to clear the
ESP module/antenna courtyard; the housing should use the saved mounting pattern. The extra 6 mm of depth preserves usable
circuit area while establishing the component-free connector band.

The saved outline is x=-6..105, y=3.5..120.5 mm. No component courtyard, pad or
mounting hardware courtyard except J40 extends right of x=87 mm. A component
keepout covers the gap from x=87 to x=94.5 on both faces; J40's own courtyard
occupies the remainder. Tracks and planes remain permitted there because the
bus must reach the socket. The native check verifies the entire 18 mm band,
including the part not covered by the keepout due to J40's exception.

These are approximate owner measurements, not a qualified mating drawing.
The 18 mm datum is assumed to be the PCB edge, not the socket's outer mating
face. The original adapter's plus-shaped outline is not copied: a rectangle is
the current candidate, with the enclosure providing support and case clearance.
No exact square, completed enclosure fit or additional physical test is implied.

## Raspberry Pi reference cell

Six footprints and relative placements come from the official
[RP2350B minimal reference ZIP](https://pip.raspberrypi.com/documents/RP-010329-CA),
`RPI-RP2350B-MINIMAL_R4-S1_public`. Source board SHA256:
`4f937c8a16cc62e7d69ba1a5b9f824aa83fb418d498ce65399447fdd99754170`.
The [MIT notice](reference/Raspberry-Pi-LICENSE.txt) is retained.
The [mapping](reference/rp-core-footprints.json) is machine-readable.

| Reference design | This board | Treatment |
| --- | --- | --- |
| U1 | U20 | RP2350B QFN-80 plus ground pad 81 and thermal holes |
| L1 | L20 | AOTA-B201610S3R3-101-T; footprint pad numbers exchanged so the original LX/DVDD physical orientation is preserved |
| C6 / C7 | C24 / C25 | Regulator input/output, Murata GRM155R60J475ME47D from the reference BOM |
| C9 | C23 | Analog regulator supply, same reference capacitor |
| R3 | R24 | 33 ohm, Yageo RC0402FR-0733RL from the reference BOM |

The reference inductor lands are 0.7 × 1.7 mm at centers ±0.7 mm.
[Abracon's drawing](https://abracon.com/datasheets/AOTA-B201610S3R3-101-T.pdf)
shows a different recommended pattern (1.0 × 1.6 mm lands, 1.0 mm gap).
This candidate deliberately follows Raspberry Pi's tightly arranged regulator
cell. That choice still needs assembly review; it is not a claim that the two
patterns are identical. No reference copper has been copied, so reference
placement alone does not establish an equivalent regulator loop or ground return.

## Other footprint decisions

J1 uses `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`, associated
with the [GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf).
Its shield identifier SH agrees with the schematic. The native checker retains
four 0.1944 mm copper-to-NPTH clearances against the current 0.25 mm design
rule; package/DFM reconciliation is required rather than hiding those findings.

J30 uses Hirose DM3AT-SF-PEJM5 and KiCad's matching footprint; pins 9/10 are
unused detection contacts, explicitly marked NC, and SH is grounded.
See the [Hirose catalogue](https://www.hirose.com/product/download/?distributor=mouser&lang=en&num=DM3AT-SF-PEJM5&type=catalogue)
and [manufacturer explanation of reel suffixes](https://support.hirose.com/en/support/solutions/articles/68000029780-what-is-the-difference-between-dm3at-sf-pejm5-and-dm3at-sf-pejm5-40-).
The AT socket is push-push; a library description is not authoritative for its
mechanism. L1 uses the XAL4020 footprint and the previously reviewed 2.2uH
Coilcraft part. Buttons and headers remain generic candidate packages.

A matching pad number establishes connectivity, not package qualification.
The remaining IC package audit includes the FUSB303B's very small QFN land
pattern; matching a generic library outline is insufficient. Effective buck
capacitance, full orderable passive BOM, soldering process and enclosure
access also remain open.

## Layout continuation

The next work is critical layout: reconcile the USB connector hole clearance,
finish the buck input/output/return placement, select a concrete four-layer
stackup and route the RP regulator plus USB paths with explicit return paths
and pair geometry. Then use the MCP router for ordinary nets, verifying that
it preserves critical copper. Four enabled copper layers do not define a
controlled-impedance stackup; there is no 90-ohm claim for this candidate.

No new physical USB feasibility test is needed. The existing passive captures
establish bus visibility, not active-buffer timing. Active timing/PIO and fault
qualification belong to the assembled prototype stage, not to a replay of
breadboard acceptance before drawing the board.

## Circuit clusters and readable references

The first automated placement left 34 reference fields hidden and used four
font sizes. Some supply capacitors were also assigned unsuitable positions.
The saved revision replaces that result with explicit IC/capacitor associations,
regular control cells and all references at 0.9 mm with 0.15 mm strokes. The
planner reserves IC/capacitor label baselines before placing surrounding labels.
It checks text bounding boxes against pads, bodies and other labels without
hiding or shrinking references to make them fit.

MCP applies component positions, orientations and reference-field changes.
Its current API does not expose native group creation or flipping an existing
footprint; `create_groups.py` uses public pcbnew APIs for those two operations.
There are 54 named groups with 183 components. C42/C43 use B.Cu beneath the SD
socket vicinity; its library component keepouts are front-only. Underside
assembly and enclosure clearance must include these two capacitors.

The buck cell follows the topology/orientation guidance in
[TI TPS62130 datasheet §11, Figure 11-1](https://www.ti.com/lit/ds/symlink/tps62130.pdf):
input capacitance beside VIN, inductor beside SW, output capacitance beside the
inductor/regulator and feedback components away from SW. The eventual routing
must join AGND/PGND/exposed-pad ground, keep switching loops short, and give VOS
its own connection to the output capacitor. Placement alone does not satisfy
these requirements. C4/C5 also sit beside the always-on regulator. The native
checker verifies the thirteen power-cell placements and orientations.
