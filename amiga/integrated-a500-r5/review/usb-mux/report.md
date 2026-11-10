# R5 USB mux placement — visual review pending

The approved USB/power placement is now authoritative: **`1e8f0634`**.
MCP transferred the 36 footprint transforms and exact reference properties;
independent comparison confirms all 203 footprint trees match the approved
power candidate. Native KiCad transferred group membership because MCP has no
group operation. Existing locks, RP geometry and unrelated footprints survived.

The next six-component cell is in a separate
[candidate project](candidate/integrated-a500-r5.kicad_pro), not the root PCB.
See the [pad-net close-up](pad-nets.png), [context view](context.png) and
[whole-board view](overview.png). Green rings are proposed ground vias only.

| Requirement | Placement and check | Routing work remaining |
| --- | --- | --- |
| Keep within reserved mux bay | All six courtyards lie within x=18–34, y=70–79 mm | Fine fan-out within the bay |
| Preserve USB corridor | All five non-bay corridor envelopes remain free of footprint courtyards | Pair width/gap, skew and transitions |
| Matching local cells | U2 at (22,75.5), U1 at (30,75.5), both 0°; C2/C1 above, R2/R1 below | Keep branches short |
| Pin-specific bypassing | C1/C2 supply pads face the approach to U1/U2 pin 10; both pad distances 2.37 mm; local ground access reserved | Short supply connection and return to plane |
| Preserve reviewed layout | All 197 unselected footprint trees unchanged from authoritative PCB | No changes authorised to RP or power cell |
| Readability | 0.6 mm references, 0.09 mm strokes; no native or MCP overlaps | Fabrication text-size acceptance |

**Owned parts:** U1/U2 = TS3USB30EDGSR; C1/C2 = 100 nF bypasses;
R1/R2 = 10 kΩ mode pull-downs. R1 biases FLASH_RP (U1.1 and U2.9);
R2 biases FLASH_ESP (U2.1 and U1.9). They sit below the corresponding select
input's IC, leaving the north bypass area clear. R3 belongs to RUN_MODE;
Q1/Q3 and other boot/reset controls remain staged for their own cell.

The actual DGS pinout has PC_DP at pin 3, PC_DM at pin 7, common D+/D− at
4/6 and LINK_DP/DM at 2/8. U2 is on the connector/ESP side; U1 on the RP side.
Their courtyards have a 1.71 mm horizontal gap, with additional room above and
below for the shared PC and LINK nets. The long RP pair can leave toward the
accepted western/northern corridor. Neither mux is treated as a flow-through
package: opposite-side D+/D− fan-out and any local layer crossings still need
routing validation. Keep the PC branch junction local to the pair of muxes,
avoid bypass routing across USB, and maintain a continuous ground reference,
following [TI §8.4](https://www.ti.com/lit/ds/symlink/ts3usb30e.pdf).

Four new proposed ground-via sites have 0.6 mm diameter / 0.3 mm drill. The
smallest conservative clearance to foreign pad copper is 0.178 mm, above the
existing 0.125 mm minimum; final routing DRC must validate actual vias. All
previous RP and USB/power via reservations remain clear. No vias were added.

**Verification:**

- Native DRC/parity checked on both the authoritative power transfer and mux
  candidate: zero parity errors, no new violations. Exact violation identities
  match the approved baseline: four J1 hole-clearance errors and 199 text-height
  warnings; 499 expected unrouted connections.
- Native ERC: the same 31 findings as the approved design, no new findings.
- MCP audit: no footprint or silkscreen overlaps. Its 131 boundary reports are
  125 intentionally staged footprints plus the six inherited connector/hole
  envelope reports.
- 203 footprints / 199 fitted components retained. Zero tracks or vias added.
  Schematics, values, footprint identities, nets, locks, board graphics and
  rules preserved. Native grouping adds only the six-member mux group.
- [verify.py](verify.py) is read-only and checks the transfer, preservation,
  corridor envelopes, bay containment and proposed via access.
  [verification.json](verification.json) records results and file hashes.

All placement and reference changes used MCP. No CadMust-Neo or routing ran.
**Stop for visual approval before transfer or another cluster.**
