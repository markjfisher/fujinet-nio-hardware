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
