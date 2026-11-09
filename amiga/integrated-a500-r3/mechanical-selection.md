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
