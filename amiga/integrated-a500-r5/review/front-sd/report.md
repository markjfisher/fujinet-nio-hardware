# R5 front-side microSD decoupling candidate

**Approved and transferred to authoritative R5. No routing.**

See [acceptance.md](acceptance.md) for transfer verification.

The approved LED/service candidate was transferred separately in `7f37d2f4`.
Its 214 footprint records, labels and groups match the reviewed candidate;
the approved ESP schematic is byte-identical. This candidate starts there.

## Placement

| Part | Value | Before | Candidate F.Cu centre / angle | Purpose |
|---|---|---|---|---|
| C43 | 100 nF | B.Cu (13, 60), 0° | (13.4, 59.2), 90° | Local J30 VDD bypass |
| C42 | 10 µF, 10 V | B.Cu (13, 57.5), 0° | (13.4, 55.5), 90° | Local microSD bulk reservoir |

Coordinates are millimetres. Same footprints, values, pad numbers and nets.
Both supply pads face south; ground pads face north. C43.1 at
(13.4, 59.975) is directly aligned with J30.4 at (10.925, 59.975):
2.475 mm centre-to-centre, with no layer transition required for this connection.
Capacitor and socket courtyards have 0.56 mm separation. The two capacitor
courtyards have 0.65 mm vertical separation; C43 clears R37's courtyard by
0.73 mm horizontally. References remain readable with no reported silk overlaps.

During routing, keep J30 VDD–C43 short and direct. Feed C42 and this local
supply node through a suitably wide branch/3V3 plane connection, with space
east of the capacitors for the branch; do not force the supply through a
thin, serial chain of capacitor pads. C42's supply pad is approximately
4.45 mm from J30 VDD in a straight line, so the bulk branch is longer than
the bypass branch. Actual copper and transient behaviour remain routing/
prototype validation items, not established by placement alone.

Reserve 0.6 mm diameter / 0.3 mm drill ground vias at:

- C42: (13.4, 53.8), 0.925 mm from its GND pad centre.
- C43: (13.4, 57.5), 0.925 mm from its GND pad centre.

Their conservative clearance to foreign pad bounding boxes is 0.606 mm and
0.475 mm respectively, exceeding 0.125 mm. These replace only the old C42/C43
prospective via sites in `review/esp-sd/verification.json`; every other approved
prospective ground-via site is preserved. No actual vias were added.

## Verification and assembly

- All 214 footprints are on F.Cu; **no backside component placement remains**.
  Through-hole headers/connectors still need their normal underside soldering;
  this means one-sided component population, not eliminating underside solder work.
- All other 212 footprint records are unchanged. All footprint/pad identities,
  net assignments, locks, groups, board drawings, keep-outs and mechanical geometry
  are preserved. All schematic/project/library files are byte-identical.
- J30 insertion/ejection envelope and U30 antenna exclusion remain clear.
  Existing enclosure/finger-access validation requirements still apply.
- Native KiCad DRC with schematic parity: **zero parity issues** and no new
  non-text-height findings. Remaining reported findings: four existing J1 hole
  clearances, 199 text-height warnings, the intentional U30 library mismatch,
  and 499 unrouted connections. Text-height and unrouted reports are capped;
  the two capacitor references move into the capped text-warning listing without
  changing their 0.6 mm font size or introducing a new rule violation category.
- MCP DRC also ran successfully. MCP audit reports no silk/pad or text overlaps.
  Its new U30/C42 bounding-box overlap is a false positive from U30's concave
  courtyard: C42 is east of the antenna and south of the module body. The exact
  courtyard regions were checked separately. Other reported boundary/keep-out
  items concern unchanged approved geometry; no rules were suppressed.
- `verify.py` independently checks every pad net against the approved schematic
  netlist, all unchanged geometry and identities, all groups, local courtyards,
  excluded regions, prospective via access and native DRC/parity.

MCP performed capacitor movement, rotation and reference placement. Its interface
does not expose footprint flipping; the disclosed native KiCad `Flip` API was
used solely for the two B.Cu-to-F.Cu changes. The PCB was not regenerated.

Open `candidate/integrated-a500-r5.kicad_pro` for review.
`closeup.png` is the native KiCad front-layer plot; `pad-closeup.png` adds pad-net
annotations and cyan prospective ground-via markers, which are not PCB objects.

**C42/C43 transfer completed following user approval.**
