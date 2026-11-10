# R5 milestone 1 — floorplan and RP2350 visual review

**Ready for visual review; stop here.** [Overview](overview.png) · [Close-up](rp-cluster.png).
Open [R5](../../integrated-a500-r5.kicad_pro). Standing criteria:
[R5_PLACEMENT_GUIDE.md](../../R5_PLACEMENT_GUIDE.md); future agents are directed there by R5 AGENTS.md.

| Requirement | Implementation | Verification / remaining limit |
|---|---|---|
| Independent electrical baseline | Copy of authoritative R4, not its CadMust candidate | All R4 hashes unchanged; schematics byte-identical; native parity zero. Project metadata automatically renamed R4→R5; rules unchanged |
| Mechanical datums | Outline, J40 position/orientation/pads and footprint retained; H1–H4 retained and locked | Native comparison passes; no new connector/mating geometry. Physical enclosure fit still inherits R4's measured-adapter assumptions |
| Clean floorplan | Discarded all 42 R4 placement groups and nonmechanical locks; staged 167 remaining parts in separated 50 mm cells | No obsolete group reused; only J40/H1–H4 and the 31-member RP cell on-board |
| Usable central RP anchor | U20 at (42,60) mm; cell spans approximately x26–55/y36–76 | Clearance to buffer corridor; no unrelated circuitry consumes the RP escape space |
| Reserved functional areas | Buffer corridor x72–87/y12–110; connector clearance x87–105; left ESP/SD/USB areas and top/bottom service regions | Buffer and antenna native rule areas plus independent rectangle checks. J40 is the intentional connector-region exception |
| Four layers and RF clearance | Existing four-layer stack retained; fixed antenna exclusion x−26.75…−5.75/y6…54 on all copper layers | Footprint's own antenna rule moves with staged U30; fixed reservation remains at the planned edge. Final module placement must satisfy both manufacturer geometry and this reservation |
| Orderly, readable RP cell | Pin-owned bypass rows; 0.6 mm references, 0.09 mm stroke; no hidden references | Native DRC: zero courtyard/copper/silkscreen overlap findings. Text-height rule conflict explicitly retained below |

## Ownership and placement rationale

All support parts are accounted for. The 31 members form one new, unlocked group,
`R5: RP2350 support cell - visual review pending`. Group membership preserves the
reviewed cell for later movement; approval/locking is not implied. J20 SWD, buttons,
USB switches and the host reset/guard ICs remain staged for their own milestones.

| Members | Actual owner / critical path | Placement rationale |
|---|---|---|
| U20,L20,C23,C24,C25,R24 | RP internal regulator: LX63→L20→DVDD65; VIN64/C24; AVDD61/C23 fed through R24 | Exact imported Raspberry Pi relative geometry and rotations checked, including L20's swapped pad mapping/winding orientation. R24 belongs to AVDD filtering, not USB |
| C26,C27,C28,C29,C30,C31,C32 | IOVDD pins 5,15,24,29,41,50,60 respectively | Perimeter rows, power pad toward corresponding edge; room beyond ground pads for short ground vias |
| C33,C34,C35,C36 | ADC59, USB/OTP68, QSPI69, IOVDD76 | Right/north supply sites; northern capacitors face south toward their own pins, labels consistently beside each vertical cell |
| C37,C38,C39 | DVDD pins 10,51,32 | C39 is the larger 4.7 µF at the distant south DVDD site; C25 supplies the fourth site at65. C39 moved close to pin32 while retaining pad clearance |
| U21,C20,R20,R13 | Flash: VCC8/C20; CS1 shares RP75/BOOT; R20 pull-up, R13 BOOT-to-switch series path | Flash northwest of RP QSPI pins70–75; bypass at VCC side, bias/BOOT parts at CS side. Preserve all six QSPI signals and ground return access |
| Y20,R21,C21,C22 | RP XIN30→Y20.1/C21; XOUT31→R21→Y20.3/C22; Y20.2/.4 ground | Quiet south corridor; load capacitors immediately beside crystal signal pads; R21 on output path rather than beside its label |
| R22,R23 | U20 USB_DP67→R22.1, R22.2→RP_DP; USB_DM66→R23.1, R23.2→RP_DM | Source-side pads face east toward MCU. Deliberately staggered around the fixed regulator cell; DP pad-centre separation ~1.2 mm, DM ~6.2 mm. Route the short escapes first and join as a pair northwest of the cell; no pair geometry has yet been claimed |
| R10 | 3V3→RP_RUN35 pull-up | South/east beside reset escape; remote reset/guard drivers remain staged |

[Measured capacitor ownership](capacitor-ownership.json) verifies each supply net against its
specific RP pin. Ordinary bypass pad-centre distances are approximately 1.8–3.7 mm;
these are geometric measurements, not routed inductance or loop-length guarantees.
Ground vias, a continuous ground reference, minimal switch copper and the precise regulator
return geometry are mandatory at routing. No tracks, vias or plane fills were added here.
Crystal/flash connections have reserved space; routing must keep them short and away from LX.

Manufacturer basis: Raspberry Pi [Hardware design with RP2350, §§2–5](https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf),
release 3, and the existing [licensed reference mapping](../../reference/rp-core-footprints.json).
The regulator is orientation-sensitive: retain the specified Abracon winding orientation and
reference capacitor/filter topology. Placement alone does not reproduce its copper or validate
regulator transient behaviour. The existing reference-land/assembly qualification remains open.

## Checks and known findings

- 203 footprints / 199 fitted electrical components; 31 in RP cell, five mechanical anchors,
  167 staged. All footprint UUIDs, pad UUIDs, nets, local pad geometry, library identities and
  schematic associations preserved. Outline and mechanical pad positions unchanged. Zero tracks.
- [Read-only verifier](verify.py) and [results](verification.json): pass. It also independently
  checks reference-cell offsets and all RP courtyards against other footprints and reserved regions.
- [Native DRC with schematic parity](drc.json): **zero parity errors**, 499 unrouted connections;
  **four inherited J1 hole-clearance errors** and **199 text-height warnings**. No courtyard,
  copper-clearance or silkscreen-overlap findings. No exclusions were added.
- The guide explicitly requests 0.6 mm references; the inherited manufacturing rule requires
  0.8 mm. Both remain intact. Resolve fabrication capability/text size before manufacturing;
  this is a documented review exception, not a clean manufacturing DRC claim.
- [ERC](erc.json): 31 existing findings, unchanged electrical design.
- MCP audit(all): zero footprint/silkscreen overlaps. Its 172 boundary/keep-out reports are
  staged parts and preserved mechanical/antenna/connector-envelope cases; they are not
  silently counted as a board-wide pass. Independent RP acceptance checks exclude none of its parts.
- Overview and close-up inspected. Functional areas and RP ownership are visible; no next cluster placed.

## Tool use and milestone gate

All footprint moves, rotations and reference edits used kicad-mcp. No CadMust run,
custom placement optimiser, coordinate-file editing or board regeneration. Narrow native KiCad
fallback handled unsupported group deletion/creation, lock changes and rule-area/planning graphics.
The first group-removal call crashed in the Python/native binding; retaining group handles and
explicitly managing removed-object ownership allowed a successful save/read-back. No R4 data was lost.

The guide requires: **“finish and review one cluster before moving to the next.”**
This candidate now stops at that gate. Approve or request changes to the floorplan/RP cell before
USB/power, ESP/SD, buffers or host-protection placement. Actual enclosure fit and routed electrical
performance are not established by this placement review.
