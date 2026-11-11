# R5 control-logic placement — visual review pending

The authoritative PCB contains the approved host-protection transfer. This
candidate adds 35 remaining control components; it has **not** been transferred.
No routing, global optimisation, schematic changes or outline changes occurred.

Open `candidate/integrated-a500-r5.kicad_pro`. Review `context.png` and the
`qualifier-pad-nets.png`, `latches-pad-nets.png`, `enables-pad-nets.png` and
`irq-pad-nets.png` close-ups. Green circles indicate proposed ground vias,
not actual copper. Actual pad numbers/nets are overlaid on native KiCad plots;
`pad-nets.csv` provides readable full names.

## Placement decisions

| Cell | Placement rationale |
|---|---|
| U61/C70, U66/C75, U85/C94 | Safety qualification beneath supervisors; address/cycle gates beside address buffers. U66 rotated 180° so A19–A23 inputs face the bus side. |
| U64/C73 | Strobe/read/address inversion between RP and buffer corridor. Capacitor faces pin 14. |
| U98/C126/R64, U84/C93, U86/C95 | Request Schmitt conditioning beside its pull-down network and clocked latches. R64 signal pads face the logic; ground pads face the plane-access side. |
| U71/C80, U79/C88 | Read/write/wait and lane qualification south of RP; clear of the reviewed USB corridor and power cluster. |
| U73/C82, U72/C81, U78/C87, U77/C86 | Repeated high/low-byte transmit/receive enable cells toward the data buffers. Same IC/cap orientations and row/column spacing. |
| U99/C127, U82/C91 | IRQ conditioning beside the final IRQ gate, near the host-interface circuitry. |
| Q2, Q3, R3, R63 | Flash reset/boot control beside the corresponding RP region; mode/arm pull-downs near control circuitry with future service wiring access. |

All 15 bypass capacitors are checked against their actual IC supply pins on
main 3V3. Pin-to-cap distances and 15 proposed ground-via locations are recorded
in `verification.json`. These placements preserve supply and ground access;
final copper lengths/return loops remain routing acceptance work. No circuit
function, threshold, supply domain or timing contract was changed.

Local groups were created with native KiCad because MCP has no group-edit
operation; this limitation was disclosed before use. All placement and label
edits used MCP. Existing groups and locks are unchanged. The stale RP-only board
title was shortened to “FujiNet A500 R5”; it and the fabrication warning moved
to free lower-left space. These are the only changed standalone drawings.

## Verification

- 203 footprints: 35 placed here, **168 preserved exactly**, including all
  previously approved clusters, J40, mounting holes and staged service parts.
- Root PCB semantically matches the complete approved host-protection candidate.
- Footprint identities, pad nets, schematic hierarchy, locks and original groups
  preserved. Zero schematic/PCB parity issues; ERC unchanged (31 baseline findings).
- Native DRC: **zero new findings**. Existing 204 findings remain: four J1
  hole-clearance errors, 199 text-height warnings and intentional U30 library
  mismatch. 499 unconnected items are expected before routing. This is not a
  fabrication-ready DRC pass.
- MCP full audit: no silk-over-pad or text-to-text overlaps. Its remaining
  overlap/keep-out reports concern existing ESP/SD geometry, staged service
  footprints and coarse bounding boxes; three entries explicitly report
  `overlap:false`. None establish a new selected-footprint collision. Native
  courtyard checks and independent geometric checks pass.
- Buffer corridor, antenna exclusion, J30 access, connector band, USB routing
  envelopes and all previously proposed ground-via sites preserved.
- Header area (25–68, 4–13 mm) and button/service area (4–70, 108–120 mm)
  remain free of newly placed courtyards. No board extension is needed for this
  candidate. Detailed routing may still justify moving whole protection groups.
- Native plots visually inspected for pad-level topology, spacing and labels.
  No tracks or vias added.

`verify.py` and `render.py` are read-only checks/renderers, not placement generators.
`placement.json` records MCP edits for review; do not use it to overwrite later
manual PCB work. `groups.json` records ownership.

## Review gate

Approve this candidate before transferring it. Headers J2/J20/J31/J60 and
switches SW1–SW4 remain staged and require their own placement review. Actual
routing, USB pair geometry, switching copper and mechanical enclosure validation
remain subsequent work.
