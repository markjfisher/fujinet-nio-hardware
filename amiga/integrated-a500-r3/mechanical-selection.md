# Direct A500 mating socket selection

The layout candidate is **Sullins ECC43DRAN**: PBT/phosphor bronze, 30 microinch
gold contact plating, 43 positions on each face, dual readout, right-angle
through-hole tails, no mounting ears. This is a manufacturer catalogue
configuration, not a claim of stock or confirmed A500 case fit.

Source: [Sullins manufacturer catalogue](https://www.sullinscorp.com/wp-content/uploads/2018/10/2019-CATALOG.pdf),
printed pages 50–51 (PDF pages 52–53). The right-angle cross-section was
visually inspected. The earlier TE candidate is not selected for layout.

| Property | Manufacturer dimension | Design consequence |
| --- | --- | --- |
| Contact pitch | 2.54mm | 43 contacts per face; span 106.68mm |
| Mating card | 1.57 +/-0.20mm | Check against actual A500 motherboard edge specification |
| Slot dimension B | 111.76 +/-0.20mm | Need clearance around the complete motherboard tongue |
| Housing dimension C | 116.21 +/-0.38mm | Reserve at least this body envelope at the case opening |
| Insertion depth | 6.73mm | Must reach full engagement before housing hits the case |
| Right-angle tail rows | 3.96mm | A generic 2.54mm-row header footprint is wrong |
| Tail length | 3.18mm | Through-hole assembly, not card-edge fingers |
| Minimum hole diameter | 1.09mm | Finished-hole requirement, not nominal drill-tool size |
| No mounting ears | N option | Avoid the H option's 131.45mm overall length; enclosure must support the sidecar |

The existing logical 86-contact symbol is reusable. The released male edge
footprint is not. Manufacturer A/B contact labels must be explicitly mapped
to Amiga odd/even contacts using a defined mating-face view. The catalogue
alone does not establish which face of the actual A500 motherboard is up at
the socket, nor the case opening/board-height relationship.

**J40 remains without a footprint until that mapping and envelope are checked.**
Do not assign a generic header or mirrored male footprint to make PCB import
appear complete. No new electronic experiment is required: the missing work
is mechanical drawing/reference reconciliation. Do not order a connector or
PCB on the strength of this catalogue selection alone.

## Identified bench adapter

On 2026-11-09 the owner identified the working bench adapter as
**A500-ZorroII-Edge v0.2, Matthias Heinrichs (Matze)**, purchased from
[this Etsy listing](https://www.etsy.com/uk/listing/1047879117/amiga-500-zorro-ii-slot-expander-a500).
This resolves the identity of the adapter used with the manufactured passive
breakout. It is the mechanical reference to investigate for the direct-A500
socket; it is not a required component of the final integrated board.

The seller links [the creator's a1k project thread](https://www.a1k.org/forum/index.php?threads/50215/).
That thread could not be read in this session (HTTP 403 on direct retrieval).
No source PCB file, socket manufacturer part number or dimensioned mounting
reference has yet been recovered from it. The listing identifies the board
and describes its side-port/pass-through arrangement; it does not establish
that its fitted socket is the proposed Sullins part.

Next reconcile the original socket footprint/contact mapping with the
manufacturer drawing and A500 case envelope. Keep ECC43DRAN provisional and
J40 unassigned until that comparison is possible. The adapter identification
does not change any circuit nets or invalidate the accepted bench results.

## PCBWay reference located

The owner supplied [this PCBWay project](https://www.pcbway.com/project/shareproject/Commodore_Amiga_500_Zorro_II_slot_adapter_board_A500_plus_expansion_eda5396e.html).
It credits Matze and lists `A-Zorro-Edge-2b.sch.pdf`, `gerbers.zip` and
`A-Zorro-Edge-2b.txt` (BOM), plus a linked DigiKey list. Download handlers require
login; direct retrieval of an advertised archive returned HTTP 403. The
DigiKey page did not expose its component rows in the accessible response.
No downloadable design contents have therefore been verified.

Both public top/bottom PCB renderings were downloaded and visually inspected.
They show opposing edge-contact regions and a central through-hole slot
connector. The low-resolution images suggest the A500 mating connector may
attach at an edge rather than use the provisional Sullins right-angle
through-hole pattern. This is an inference to resolve from the Gerbers and
BOM, not a confirmed socket type or a dimensioned footprint. Do not equate
the central Zorro slot footprint with the female A500 mating socket.

The schematic PDF, Gerber ZIP and BOM text are the useful next inputs. Inspect
connector pad numbering, mounting style and board outline before choosing
whether to retain or replace ECC43DRAN. The public project lists CC BY-NC-SA;
record provenance and review reuse terms before importing any third-party CAD.
No third-party CAD has been copied into the candidate, and no order/upload or
circuit change was performed in this reference review.

## Supplied schematic inspected

The owner provided `~/Downloads/A-Zorro-Edge-2b.sch_PCBWay Community.pdf`.
SHA-256: `b98e4c90fc96800524143247595f602047e43bb976550a2408eaffc5783b377f`. Text extraction and a rendered full-page
visual inspection were completed. The title is `A-Zorro-Edge-2b`, sheet 1/1,
with drawing date 15.11.2015 and print timestamp 29.06.2016.

| Reference | Explicit schematic name | Role |
| --- | --- | --- |
| CN1 | A500-EXPANSION-SLOT-SOLDER | 86-contact A500 mating socket |
| CN2 | A500-EXPANSION_EDGE | 86-contact pass-through male edge |
| CN3 | ZORROII_SLOT | 100-contact Zorro-II card slot |

An independent transcription of CN1's address/data, ground, +5V and used
control pin numbers was compared with R3 J40: **61 assignments agree**.
In particular XRDY=18, BERR=46, RESET=53, DTACK=66, R/W=68, LDS=70,
UDS=72 and AS=74. The remaining used J40 pin, 12, is CN1 CFIN; R3 grounds
that local configuration input for its direct single-board arrangement.
The adapter instead carries a configuration chain through its connectors;
that distinction is intentional, not a pin-number mismatch.

The connector name establishes which symbol represents the mating socket,
but is not an orderable MPN or dimensioned mounting specification. It supports
investigating the edge-solder mounting inference from the renderings; it does
not establish tail shape, row spacing, pad face assignment or case clearance.
Gerbers and BOM remain the next mechanical inputs. No candidate pin mapping
or connector footprint was changed on the basis of this schematic alone.

## Supplied Gerbers and BOM inspected

The owner provided `~/Downloads/gerbers_PCBWay Community/gerbers/` and
`~/Downloads/A-Zorro-Edge-2b_PCBWay Community.txt`. These are the matching
**A-Zorro-Edge-2b** reference artifacts: all layer/drill basenames agree,
CAM reports identify EAGLE 7.6.0 and the same design name, and the BOM's
CN1/CN2/CN3 references and device names agree with the supplied schematic.
The BOM was exported 29.06.2016; Gerber/drill reports were generated
25.01.2026. Matching identity is established, but the later CAM date means
we do not assume byte-for-byte equivalence to the original 2015 board.
Reference file hashes are in [the manifest](review/matze-reference-sha256.json).

The set includes top/bottom copper, mask, paste, silkscreen, GKO and an XLN
drill file plus CAM reports. Read-only parsing of the rectangular pad flashes
in GTL/GBL and GTP/GBP found identical coordinate sets: two regions each with
43 pads on each face, at 2.54mm pitch and 106.68mm first-to-last contact span.
The nominal rectangular copper aperture is approximately **1.650 x 9.500mm**.
Both ends also occur in the paste files; do not treat these reference paste
layers as a ready-to-use stencil prescription for our new board.

| BOM reference | Device | Custom EAGLE package |
| --- | --- | --- |
| CN1 | A500-EXPANSION-SLOT-SOLDER | LKONT_43-SLOT-SOLDER |
| CN2 | A500-EXPANSION_EDGE | LKONT_43 |
| CN3 | ZORROII_SLOT | SLOT_100 |

This supports the edge-solder socket interpretation and rules out copying a
central through-hole Zorro footprint as the A500 mating connector. The BOM
still does not specify a connector manufacturer/orderable MPN. Gerber pads
alone do not identify an available socket's tail geometry or establish its
contact numbering viewed from the mating face. The provisional Sullins
right-angle part is therefore not qualified by these files; its different
mounting pattern must not be substituted into this reference geometry.

These inputs resolve the missing-reference-file request. Remaining mechanical
work is to identify a compatible purchasable socket and reconcile its drawing,
contact-face mapping and case fit. No additional USB/bus experiment is needed
for that work. No reference CAD was imported or candidate circuit changed.
