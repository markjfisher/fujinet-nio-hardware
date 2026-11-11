# R5 service placement — visual review pending

The approved control-logic candidate is transferred to authoritative R5. The
new service candidate is separate at `candidate/integrated-a500-r5.kicad_pro`.
Only J2/J20/J31/J60 and SW1–SW4 were placed; no routing or global optimisation.
All eight service positions are **provisional pending enclosure review**.

| Requirement | Implementation | Evidence/check | Remaining decision |
|---|---|---|---|
| Preserve approved board | Eight selected footprints; 195 unchanged, including all existing groups/locks | `verify.py`, native DRC/parity | None for transfer |
| Debug access | J31 UART and J20 SWD in an aligned top-edge row, pin 1 left | Pad-net readback; header access rectangles | Plug height, cable bend and lid access |
| Recovery access | RP RESET/BOOT and ESP RESET/BOOT in two aligned bottom-edge pairs | 11 mm centre spacing within pairs, 14 mm between pairs; 10 mm diameter top-access disks clear other courtyards | Button height, actuator travel, enclosure openings |
| Physical mode/arm access | J2 at bottom-left, J60 between mode selection and buttons | Shunt/finger envelopes clear nearby footprints | Shunt grip and cover design |
| Readability | 0.6 mm references, separate 1 mm functional captions | Native and MCP silk checks; visual close-ups | Final fabricator text capability |

## Review images and geometry

- `context.png`: complete board, all footprints now on-board in this candidate.
- `headers-pad-nets.png`: UART/SWD row.
- `controls-pad-nets.png`: mode, arm and recovery controls.
- `placement.json`, `pin-nets.json`, `pad-nets.csv`: exact positions and actual nets.
- `access-envelopes.json`: **planning envelopes**, not connector specifications.
  They are checked against component courtyards by `access-check.py`. No CAD
  keep-out or copper geometry was added for these provisional access envelopes.

J31 pin 1 is (28, 9) mm; J20 pin 1 is (49, 9) mm. Both are rotated 90° so
pins increase left-to-right. Their centres are 5.5 mm inside the top edge.
They remain vertical headers: access is from above, not an assumed side-entry
plug. Allow a removable lid/service hatch, connector body height and cable bend
space without intruding into the ESP antenna exclusion.

SW1–SW4 actuator centres are (30.25, 114.25), (41.25, 114.25),
(55.25, 114.25), (66.25, 114.25) mm. The common actuator row is 6.25 mm
inside the bottom edge. Ten-millimetre top-access disks fit without touching
other component courtyards; this does not guarantee comfortable operation for
all fingers or a particular enclosure actuator. Final side-wall thickness,
plunger diameter, button height/travel and assembly tolerances must be checked
against selected physical parts. The 6 mm switch footprints are unchanged.

J2 pin 1 is (6, 110) mm. J60 pin 1 is (19, 113) mm, its two pins horizontal.
Both need top access for fitting/removing shunts. They are deliberately separate
from the recovery buttons. No board extension was necessary. J40, the mounting
holes, antenna/card access and all existing approved placement remain unchanged.

## Service pinout / operation labels

| Part | Actual pin order or function |
|---|---|
| J31, left-to-right 1–5 | GND, ESP_TXD0, ESP_RXD0, ESP_EN, ESP_BOOT_N; 3.3 V signals |
| J20, left-to-right 1–5 | 3V3 reference, RP_SWDIO, GND, RP_SWCLK, RP_RUN; reference is not an external board-power input |
| J2, horizontal pairs top-to-bottom | 1–2 RUN; 3–4 Flash RP; 5–6 Flash ESP; select one pair |
| J60 | 3V3 to BUS_ARM when fitted; normally open |
| SW1 / SW2 | Pull RP_RUN / RP_BOOT_PULL to GND |
| SW3 / SW4 | Pull ESP_EN / ESP_BOOT_N to GND |

Mode selection and bus arm are not power switches. Normal board power remains
USB. No electrical topology, footprint, pinout or safety mechanism changed.
Service lines must subsequently be routed clear of USB pairs and switching
nodes. Debug wiring length/return paths remain subject to routing validation;
use a short external SWD lead and validate debug operation on the prototype.

## Verification

- Root PCB equals the full approved control-logic candidate semantically.
- Candidate changes exactly eight footprints. All 195 other footprints match
  authoritative R5 exactly, including reference labels. Existing groups, locks,
  nets, IDs, mechanical geometry, schematics and project rules are preserved.
- Six provisional service groups added via native KiCad API after disclosing
  MCP's missing group operation. All placement and caption edits used MCP.
- Ten functional captions added; existing standalone drawings remain unchanged.
- Native KiCad 10 DRC: **zero new findings**, zero schematic parity issues.
  Baseline remains four J1 hole-clearance errors, 199 text-height warnings,
  intentional U30 library mismatch and 499 unconnected items. Not a clean
  fabrication DRC result. ERC unchanged at 31 baseline findings.
- MCP full audit: no service-footprint overlap or keep-out findings, no
  silk/pad or text/text overlap. Remaining reports are existing ESP/SD/coarse
  boundary findings; three listed footprint pairs explicitly say `overlap:false`.
- Independent checks preserve the buffer corridor, connector band, antenna
  exclusion, J30 access, USB corridors and all earlier proposed ground-via sites.
- Provisional access envelopes pass. Native plots visually inspected.
- Zero tracks/vias added. No authoritative service transfer has occurred.

Stop for visual approval. Enclosure acceptance is a separate later checkpoint;
these service groups may move as necessary for that work. Do not transfer this
candidate or begin routing until authorised.
