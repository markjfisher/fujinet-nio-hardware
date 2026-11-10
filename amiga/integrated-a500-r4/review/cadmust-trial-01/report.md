# First selected-group placement trial — review only

2026-11-10; authoritative baseline `9a6e75a2`. **No transfer to the authoritative PCB.**

The best courtyard/keep-out-valid optimiser result is [the candidate PCB](best/integrated-a500-r4.kicad_pcb).
Open its adjacent project to retain libraries and design rules. [Visual comparison](comparison.png):
left = MCP local seed; right = CadMust result. Native KiCad plots: [before](before.svg), [after](after.svg).
This is a useful connection-length trial, **not a placement ready for transfer**: silkscreen collisions remain.

| Requirement | Implementation / evidence | Result |
|---|---|---|
| Scoped complete groups | U61/C70/R3/R63; U66/C75; U71/C80; U64/C73 | Four rigid groups, ten footprints |
| Local geometry through MCP | Explicit move_footprint calls; 0° TSSOPs; bypass centres +5.6 mm X, −1.95 mm Y from IC | VCC-side local bypass; capacitor pad 1 faces pin 14 |
| Preserve all other parts | selected_only=True export, no unlock or constraint templates | All 193 unselected footprint trees identical, including text, pads and properties |
| Independent hard acceptance checks | Native courtyard bounding boxes versus all parts, physical board outline, antenna rectangle and connector corridor | Zero selected overlaps, off-board parts or forbidden-region intersections |
| Preservation | Parsed full native footprint/group/board comparison plus independent pad UUID/net checks | All locks, 42 groups, standalone graphics/text, rules/zones and nets preserved; zero tracks |

## Measured comparison

| Metric | Local seed | Best trial |
|---|---:|---:|
| Total HPWL, mm | 15148.98 | 14084.14 |
| HPWL of nets touching selected parts, mm | 3288.54 | 2223.70 |
| Selected courtyard overlaps / keep-out breaches | 0 / 0 | 0 / 0 |
| CadMust whole-model overlap proxy | 38 | 38 |
| Native DRC violations, excluding unrouted connections | 11 | 19 |
| Unconnected items / schematic parity errors | 499 / 0 | 499 / 0 |

Overall HPWL improves **7.03%**; selected-incident HPWL improves **32.38%**.
HPWL is a bounding-box wire-length estimate, not routed length or a timing result.
Both stages use identical net exclusions: `/GND`, `/VBUS_C`, `/VBUS_PROTECTED`.
Fixed staged protection components still influence connection lengths; their eventual placement may change the preferred result.
The 38 whole-model overlaps are the upstream proxy, not native DRC courtyard violations, and do not implicate these selected parts.

Native DRC confirms no courtyard overlaps or new copper-clearance violations. Six original findings
remain (four J1 hole clearances and two U30 silk/edge findings). Local-seed labels add five findings;
optimised labels add thirteen. These involve selected labels and selected parts landing underneath
preserved labels near the RP2350 (notably C23/C24/C30/C32). All unselected text is unchanged.
Visual inspection confirms the denser processor-side placement and these label collisions.
Do not approve this candidate as a finished silkscreen layout. A subsequent constrained trial should
reserve those text envelopes or explicitly authorize local label tidying before transfer.

## Method and compatibility

CadMust-Neo `bbed16824a806e6ba787b96d3915233462db9bd2`, KiCad 10.0.7.
MCP guidance and actual move responses succeeded. Existing groups were already correct, so no
membership edits were necessary. MCP lacks selection-setting/group editing operations; this limitation
was reported before a **read-only** native selection export. No custom placement algorithm or direct
PCB coordinate edits were used. Upstream batch_runner performed optimisation and upstream apply_model
performed native write-back with `--respect-board-locks`; the GUI/global silkscreen pass was bypassed.

Run: `--profile default --seed 42 --pad-clearance on --offboard reject`, no scatter or unlock.
Only four representatives are movable; their complete groups follow rigidly. Read-back shows maximum
intra-group distance drift 0.000128 mm from upstream integer rotation rounding (well below 0.001 mm).
The first discarded run exposed a 0.05 mm bypass courtyard overlap in the seed; MCP corrected each
capacitor's offset from 5.3 to 5.6 mm before the recorded trial. This is why independent DRC matters.

The read-only model adapter includes the exact antenna rectangle x=−26.75…−5.75/y=6…54 mm
and full connector clearance x=87…105/y=3.5…120.5 mm. Acceptance separately rejects selected
courtyard intersections with either rectangle; the cost function is not the acceptance gate.
J40 and the antenna module themselves remain fixed exceptions. Existing unrelated staging/boundary
and footprint-envelope audit findings remain untouched, not silently treated as clean.

The upstream batch CLI emitted a headless action-plugin registration assertion diagnostic but completed
successfully. Write-back used package loading without GUI registration; all 203 UUIDs matched, zero
side mismatches or flips. This demonstrates this headless path, not GUI undo compatibility.

## Evidence and next decision

- [Semantic/geometry/HPWL results](verification.json), [net and authority checks](extra-checks.json).
- [Native seed DRC](seed-drc.json), [native candidate DRC](best-drc.json), [ERC](erc.json): 31 unchanged findings.
- MCP audit(all) and MCP DRC independently ran; native parity is zero. MCP audit also reports existing
  broad envelope/staging issues; native DRC is the exact courtyard/clearance authority.
- [Baseline hashes](authority-hashes.json): every authoritative CAD file remains byte-identical.
- `export_model.py` is read-only extraction; `check.py` is read-only validation (takes upstream checkout
  path). Pickles are locally generated trial models, not scripts that place footprints. The exported
  seed and best projects are disposable copies. No routing, manufacturing export or transfer occurred.

**Recommendation:** retain this as the first trial, review the improved group locations, and authorize a
small follow-up addressing the identified silkscreen envelopes before any transfer. Do not globally
move processors, power clusters, buffers or staged protection to accommodate this result.
