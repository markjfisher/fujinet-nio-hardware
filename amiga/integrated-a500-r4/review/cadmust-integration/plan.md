# R4 CadMust-Neo integration — review checkpoint

Reviewed upstream **bbed16824a806e6ba787b96d3915233462db9bd2** on 2026-11-10.
No optimiser, annealer, automatic silkscreen placement or placement write-back
was executed. The checkout was inspected in /tmp; no plugin was installed.

## Completed changes

- `926c32b6`: C113 → Panasonic **6SVPC100M**, `CP_Elec_5x5.9`;
  C117 → **6SVPC220M**, `CP_Elec_6.3x5.9`. Schematic properties updated through
  MCP; native pcbnew filled the MCP's missing in-place footprint-replacement
  operation. Centres, rotations, sides, locks, footprint/pad UUIDs, schematic
  paths and pin nets retained. Part values now include exact MPNs.
- `5cfeb117`: repaired nine existing groups, preserving all 42 group UUIDs and
  lock states. U61's combined permission group now includes C70/R3/R63;
  U66+C75, U71+C80 and U64+C73 restored. Old U62 group repurposed for R64;
  U60/C60/R60/R61 reunited with C114; R37 returned to SD pullups with R41;
  C123 added to U7's group and C124 to U5's. Surviving footprints never moved.
- Full native pin/net verification passes. ERC: 31 existing findings; DRC:
  6 existing violations, 499 unconnected items, **zero parity errors**.
  Still 199 fitted components, 203 footprints, 63 locked footprints, zero tracks.
  Footprint rendering inspected; [capacitor preview](caps.png).

Current inventories: [footprints and classifications](current-footprint-constraints.csv),
[repaired groups and staging warnings](current-groups.json). Readiness-region
proposals remain planning envelopes, not collision-cleared constraints.

## Constraint-file format actually implemented

[constraints.py](https://github.com/remiblokker/CadMust-Neo/blob/bbed16824a806e6ba787b96d3915233462db9bd2/plugin/constraints.py)
reads JSON (v1/v2 conventions). Required top-level keys:
`meta`, `component_groups`, `net_priorities`, `placement_constraints`.
`meta.schema_version` is descriptive; the parser does not enforce a version gate.

| Field | Actual behaviour / intended use |
|---|---|
| `meta.board_dimensions_mm: [w,h]` | Size sanity warning only. |
| `placement_constraints.fixed_positions: [{ref,x_mm,y_mm}]` | Sets position and locks in the model. No explicit angle field; retain current orientation and side. |
| `component_groups: [{id,members,max_span_mm}]` | Soft cohesion penalty; **not a hard maximum distance**. Without max_span or template it does not bind the parts. |
| Group `template: {anchor,relative_positions:{REF:{dx_mm,dy_mm}}}` | Establishes relative offsets in the anchor frame and a rigid group. Applying a template itself can relocate parts. Use only after reviewing local geometry. |
| `zone_preferences: [{ref,zone}]` | Soft preference among a 3×3 grid (`top-left`, `center`, etc.); cannot enforce our exact mm rectangles. |
| `edge_locked: [{ref,edge,...}]` | Snaps/slides along an edge; **not a fixed connector position**. Do not use for J40/J1/J30. |
| `keep_out_zones: [{ref,clearance_mm,layers,...}]` | Component-relative clearance ring or v2 antenna object, not arbitrary board rectangles. |
| `back_side: [{ref}]` | Can flip parts on application. Omit for initial integration. |
| `net_priorities: {critical:{nets:[...],weight:N},...}` | HPWL weights/exclusions. Use exact exported net names. A weighted excluded power net remains excluded. |
| `signal_classes`, `design_notes`, provenance | Ignored by the placement engine; cannot enforce timing, USB impedance or return paths. |

Coordinates are **relative to the extracted outline bounding-box minimum**, not
KiCad absolute coordinates. This board extracts as (-6.05, 3.45)–(105.05,120.55)
mm, including edge stroke: `x_json=x_kicad+6.05`, `y_json=y_kicad−3.45`.
Do not substitute the nominal -6/3.5 outline centreline origin.
[preservation.constraints.json](preservation.constraints.json) is parser-validated
and fixes **every** present footprint, including staging; it is an auditable
coordinate baseline, **not an optimisation recipe**.

## Representation plan

| Readiness classification | CadMust representation and control |
|---|---|
| Mechanical fixed: J40/J1/J30, H1–H4, outline | Explicit fixed_positions at the current coordinates; omit from selection. Preserve side/angle and verify against the baseline afterwards. Holes need this even though their KiCad lock flag is currently false. |
| Electrical anchors: RP reference cell/crystal/QSPI, ESP/antenna, buck, USB path, U40–U47 corridor | Initially freeze **every member** at its current position, including unlocked support parts. Keep existing group relationships. Do not name these as movable cohesion/zone targets. |
| Provisional service headers/buttons | Frozen in the first pass. Only a later explicit selection/enclosure decision releases them. |
| Approved movable logic and passive clusters | First arrange each local circuit with MCP/manual KiCad. Then select the **complete native group** for rigid-body optimisation, or use reviewed JSON templates. Groups spanning staging and the board are not usable rigid templates yet. |
| Host-protection parts | Use the eleven readiness clusters as engineering planning units, not one giant rigid group. Seed limiter/LDO, monitor/Schmitt and output/hold-up cells separately; establish bypass/CT/divider locality before allowing whole-cell movement. Soft cohesion may guide a candidate but cannot enforce ≤50 pF GUARD_OK_RAW or shutdown delay. |

All 52 staged footprints remain where they were. Future local cluster seeding
is a separate placement operation requiring review. Repairing group membership
has intentionally not guessed new coordinates or grouped all staged parts.

## Selection and KiCad 10 compatibility

[GUI selection handling](https://github.com/remiblokker/CadMust-Neo/blob/bbed16824a806e6ba787b96d3915233462db9bd2/plugin/cadmust_neo_action.py#L688)
restricts positional constraints to selected parts. A partly selected native
KiCad group remains immobile. However, references named by a constraint file
can have their model locks cleared, even if KiCad says locked; when selection
is off this can expand to other members of their native group. Native lock
flags are preserved on write-back, so a locked-looking part may have moved.
Use a strict selection whitelist, explicit fixed positions for protected parts,
and before/after verification of **all unselected references**. Avoid `--unlock all`.

README claims KiCad 9.x/9.0.7 testing. Source includes KiCad 10's two-argument
outline API and 9+ flip enum handling. A **read-only KiCad 10.0.7 probe passed**:
203 footprints, all 40 multi-member groups matched (two singleton groups are
not modelled as rigid groups), four outline vertices and one board-level
placement keep-out. Empty selection moves nothing; C113-only is eligible;
U61 alone is frozen; its complete group has one movable representative.
JSON parsing and selection restriction also pass. No annealing or write-back
was involved. This establishes extraction/helper compatibility, **not tested
GUI/undo or optimisation-result compatibility**. See [compatibility.json](compatibility.json).

Two specific integration safeguards are required before the first run:

1. **Keep-outs:** extraction reads board-level footprint-forbidden rule areas,
   not U30's embedded footprint antenna rule area. That area exists at
   x=-26.75…-5.75/y=6…54 mm. Materialise its exact geometry in the temporary
   model/board adapter or supply a verified explicit antenna constraint; do not
   rely on automatic pad-free inference. The imported connector keep-out is
   only x87…94.5 mm; our full x87…105 component-clearance contract (J40 excepted)
   still needs an independent body-clearance check. Copper/return-plane
   restrictions remain KiCad routing constraints, not placement guarantees.
2. **GUI side effects:** the action calls silkscreen placement for all visible
   references after optimisation, with no selected-only filter. Its rejection
   restore records only footprint reference/XY/angle, not reference-text
   positions or side flips. Therefore use a disposable candidate and transfer
   only reviewed selected footprint transforms, preserving all other text,
   locks, sides, groups and geometry. Do not rely on the GUI Reject button as
   a complete rollback. No such run/transfer is authorised or performed here.

Next reviewed step: prepare local cluster geometry and a run-specific selection
plus constraint file; dry-check keep-outs and protected footprints; then approve
an isolated selection-only trial. Native netlist/parity, DRC, mechanical checks,
visual inspection and timing/USB/power review remain acceptance gates regardless
of the optimiser's score.
