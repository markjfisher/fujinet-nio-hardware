# R5 ESP32 / microSD placement review

Status: **candidate only, awaiting visual approval**. The approved six-part mux
cell has been transferred to the authoritative PCB. No ESP/SD placement has
been transferred, and no routing or global optimisation was performed.

Open [candidate project](candidate/integrated-a500-r5.kicad_pro).
Review [front pad nets](pad-nets.png), [back pad nets](back-pad-nets.png), and
[floorplan](context.png). Back view is flipped to look at the component side.
Green rings are proposed ground vias, not copper; grey outlines/text are planning
annotations on Dwgs.User, not silkscreen. The drawings are native KiCad plots
with read-only pad-net annotations. Render and verification scripts never edit CAD.

## Placement decisions

| Requirement | Candidate implementation |
|---|---|
| ESP32 module and antenna | U30 at (1,30), 90 degrees; antenna overhangs the left edge. All-layer exclusion x=-26.75..-5.75, y=6..54 is retained for copper, pads, tracks and vias. Other footprints are independently excluded. |
| Module supply | C41 100 nF and C40 10 uF below module pin 2, supply pads facing the module; respective pad-centre distances 1.98/3.18 mm. Local ground-via access retained. |
| USB pair | R31 DM and R30 DP below module pins 13/14, parallel and equally oriented. Escape heads toward U2 around the right of the SD socket. Preserve pair order, matched fan-out, continuous ground and the accepted mux corridors. |
| Boot/reset | R11/C10/Q1 form the EN support cell; R12/Q4 serve BOOT. Q1 FLASH_RP and Q4 FLASH_ESP connections remain unchanged. Switches and J31 remain staged. |
| Straps and VBUS sense | R32/R33 beside their actual STRAP45/46 pins. R34/R35 beside ESP_VBUS_VALID. No circuitry or values changed. |
| SD clock | R36 next to U30 pin 20, with its SD_CLK_CARD pad pointing toward the socket routing space. |
| SD socket | J30 at (3.2,60.5), -90 degrees, opens left. Ejected-card F.Fab envelope starts y=54.575, clearing the antenna exclusion by 0.575 mm. Keep its external approach unobstructed. |
| SD pull-ups and supply | R37 isolated array and R41 adjacent to the socket signal bank. C43 100 nF / C42 10 uF remain on B.Cu, supply pads facing socket pin 4; distances 1.30/2.80 mm. Use short supply vias and local ground vias. |
| Readability and assembly | References 0.6 mm / 0.09 mm, coherent rows and local ownership. Native courtyard and silkscreen checks plus front/back visual inspection completed. |

Complete changed set (20): U30, J30, C40–C43, R30–R37, R41,
R11, R12, C10, Q1, Q4. R38–R40 no longer exist after consolidation.
ESP support and SD support have separate review-pending KiCad groups.

The module includes its flash/PSRAM/crystal; no external support was added.
Module antenna placement follows the
[Espressif module layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html#positioning-a-module-on-a-base-board)
and [module datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf).
The Hirose DM3AT-SF-PEJM5 is a **push-push** socket; see the
[manufacturer product/drawing page](https://www.hirose.com/en/product/p/CL0609-0031-0-00).
Card clearance here is checked against the installed footprint's ejection artwork;
final enclosure access and antenna performance remain prototype validations.

## Tool boundary and local footprint exception

All footprint positions, rotations and reference edits used kicad-mcp. Its
missing group-edit operation required a disclosed native KiCad grouping step.
Existing group membership and all locks were preserved.

The blanket antenna **footprint** prohibition incorrectly rejected U30's own
antenna overhang. A disclosed native edit permits footprint bodies in that board
rule area while retaining every copper/pad/track/via prohibition. `verify.py`
independently rejects every other footprint and every pad in the exclusion.
Future placement tasks must retain that explicit check.

U30's two crossing silk segments were clipped at x=-5.75; the wholly off-board
segment was moved to F.Fab. This narrowly scoped native edit leaves one intentional
`lib_footprint_mismatch` warning. FPID, pads, courtyard and electrical identity
are unchanged. Do not blindly update this footprint from the library and restore
the off-board silk.

## Verification

| Check | Result |
|---|---|
| Approved mux transfer | Exactly U1/U2/C1/C2/R1/R2 changed; 197 other footprints and all existing groups/non-footprint objects preserved. All 203 footprint trees match the approved candidate. |
| ESP/SD isolation | Exactly 20 footprints changed; 183 unchanged, including the approved RP, mux and power cells. All identities, pad nets, locks and existing groups preserved. |
| Native DRC / parity | Zero parity issues. Four existing J1 hole-clearance errors, 199 existing text-height warnings, 499 unrouted connections. Only new finding: the intentional U30 footprint mismatch warning. No new clearance/courtyard/silkscreen errors. |
| ERC | All sheets' findings exactly match mux baseline: 31 existing findings. Schematic/project/library files unchanged. |
| Corridors / antenna | Five non-bay USB corridor envelopes clear. All pads and other footprints outside antenna exclusion; card ejection envelope clear. |
| Ground access | Eight prospective 0.6/0.3 mm vias checked; minimum foreign-pad clearance 0.20 mm. All earlier approved proposed via sites still clear. No actual vias added. |
| MCP audit | No silk/reference overlaps. 12 bounding-box overlap reports arise from U30's extended antenna courtyard bounding box and the backside C42/C43 projection beneath J30; native polygon/layer checks pass. 119 coarse keep-out/boundary reports include staged footprints, connector envelopes and these bounding-box cases. Not represented as a clean MCP audit. |

Evidence: [verification](verification.json), [check summary](check-summary.json),
[native DRC](drc.json), [ERC](erc.json), [MCP audit](mcp-audit.json),
[transfer preservation](transfer.json). The board still has zero tracks/vias.

Routing must establish actual 90-ohm USB geometry, length balance, shared PC/LINK
fan-out without long stubs, a continuous ground reference, and short supply/return
loops. These are placement feasibility results, not routed electrical validation.
Stop here for visual review before any candidate transfer or another cluster.
