# R5 host-protection placement — visual review

**Candidate only; stop for approval before transfer.** The approved bus-buffer
cell is now authoritative; see [transfer record](../bus-buffers/acceptance.md).
This candidate places 42 host-protection/support components and preserves the
other 161 footprints. No routing, outline changes or global optimisation.

Open [KiCad candidate](candidate/integrated-a500-r5.kicad_pro).
Views: [power/supervision/override](supervision-pad-nets.png),
[reset and host-input conditioning](reset-pad-nets.png),
[bus hold-up](hold-up-pad-nets.png), [floorplan](context.png).
Pad-net annotations are read from native KiCad. Green rings are proposed vias,
not copper; the view scripts do not write CAD.

## Engineering requirements

| Requirement | Placement / check | Remaining routing or prototype validation |
|---|---|---|
| Limited host supply | U95 at (63,19), D4 at (56.5,19.95), U96 at (49,19). Actual pin flow runs right-to-left from host input through isolation diode and LDO. C110 at input, C111/C112 at LDO pins. | Keep raw host supply run direct to limiter; broad limited-supply and ground paths. Verify existing current-limit/startup assumptions on prototype. |
| Independent supervision | U60/U90/U91 at y=30, x=30/43/56; matching bypass, divider and CT layout. Each CT cap faces pin 4; each 1 µF bypass faces pin 6. | Route host sense from raw AMIGA_5V; main and bus sense from their load rails. Quiet divider/CT grounds, separate from load-current returns. |
| Hardware output disable | U92/R116/R117/R122 below the supervisors, to the right of the USB approach. U93/U94 adjacent with local OE pulls and bypasses. All original pin nets and domains retained. | Keep shared GUARD_OK_RAW compact, total capacitance ≤50 pF; direct BUS_DISABLE distribution to all four data buffers. Preserve the reviewed ≤3 µs shutdown allocation; actual copper and measurements must validate it. |
| Bus hold-up | C113 at (65,85), positive pad toward buffer column, R111 nearby. Local C54/C55 at output buffers remain unchanged. | Wide low-inductance 3V3_BUS distribution; reserve the clear strip between this cell and the buffer column. Bulk capacitance/ESR and loaded collapse remain existing prototype checks. |
| RP reset | Q5/R120/R121 near RP_RUN, with U97/C125 alongside. Q5 collector points toward U97 RP_RUN input. Approved R10/RP cluster untouched. | Route collector to RP_RUN and keep the base pull-down local. Other U97 mode/arm paths connect to later control placement. |
| Host input conditioning | U100/C128 just left of U43, using actual RESET/BERR/DTACK pin mapping. | Mixed pin directions require fan-out/layer transitions; do not bypass conditioning for a shorter route. |
| Mechanical and routing reserves | Existing outline, holes, J40, antenna/card access, all five USB corridors and the buffer corridor preserved. | This cluster fits now; remaining logic is not yet proven to fit. Propose a vertical extension if later routing/placement room is insufficient. No outline edit without approval. |

## Complete ownership

Nine local groups were created after checks:

| Group | Members |
|---|---|
| Host supply | U95, C110, R110, D4, U96, C111, C112 |
| Host supervisor | U60, C60, C114, R60, R61 |
| Main supervisor | U90, C118, C115, R112, R113 |
| Bus supervisor | U91, C119, C116, R114, R115 |
| Hardware disable | U92, C120, R116, R117, R122 |
| XRDY/IRQ guard | U93, U94, C121, C122, R118, R119 |
| Bus hold-up | C113, R111 |
| RP reset conditioning | Q5, R120, R121, U97, C125 |
| Host input conditioning | U100, C128 |

U98/U99, request/control logic, their bypasses, service headers and switches
remain staged. C117 and all prior approved supply/support geometry are retained.
No parts, values, power domains or electrical connections changed.

The existing parts were checked against manufacturer information:
[TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf) (input bypass and ILIM),
[AP2112](https://www.diodes.com/assets/Datasheets/AP2112.pdf) (SOT25 pinout and
local 1 µF input/output ceramics), and
[MIC2790](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MIC2790-1-3-Supervisor-with-High-Accuracy-Ultra-Fast-Propagation-Delay-and-Capacitor-Programmable-Reset-Delay-DS20007151.pdf)
(SNS, CT, VDD and open-drain H variant). The manufacturer's example layout is
not a drop-in geometry for this three-supervisor circuit. The implemented
[electrical contract](../../../integrated-a500-r4/review/component-optimisation/bus-output-disable-proposal.md)
remains unchanged, including its operating assumptions and prototype tests.

## Verification

- kicad-mcp performed every footprint move, rotation and reference edit. Native
  KiCad was used only for unsupported group transfer/creation and the previously
  approved buffer reservation setting. No placement generator ran.
- Exact full-board semantic equality for the approved buffer transfer. In the
  host candidate, exactly 42 footprint trees differ; all other footprints,
  existing groups, locks, identities, pin nets, outline and rule areas match.
  Schematic/project/library files are unchanged.
- Native DRC and MCP DRC: **zero new findings**. Baseline remains 4 J1
  hole-clearance errors, 199 text-height warnings, 1 intentional U30 footprint
  mismatch and 499 unrouted connections. Schematic parity: zero issues.
  ERC findings match all baseline sheets exactly (31 existing findings).
- MCP audit: no new footprint or silk/reference overlap. Its 12 existing
  coarse overlaps concern the ESP antenna bounding box/backside SD caps;
  57 keep-out/boundary reports include staged parts and accepted connector
  geometry. These are not presented as a globally clean audit.
- Eleven bypass-to-supply connections checked against actual nets: pad-centre
  distances 1.89–3.10 mm; the three supervisors are consistently 2.275 mm.
  Supply pads face the owning pins. All CT and bypass values remain unchanged.
- Twenty-six prospective 0.6/0.3 mm ground vias have ≥0.292 mm clearance to
  foreign pad bounding boxes; earlier approved prospective vias remain clear.
  They are provisional routing aids, not added vias. C113's proposed ground via
  is outside its solder pad; no via-in-pad assembly assumption is introduced.
- Native plots inspected at pad level and as a whole-board view. References
  remain 0.6 × 0.6 mm, stroke 0.09 mm. Final conductor geometry, plane continuity,
  reset capacitance and supply impedance are routing checks, not proven by DRC.

Evidence: [verification](verification.json), [pad nets](pin-nets.json),
[placement](placement.json), [groups](groups.json), [native DRC](drc.json),
[ERC](erc.json), [MCP audit](mcp-audit.json), [MCP DRC](mcp-drc-summary.json).
Stop for visual review. Do not transfer or place the next cluster yet.
