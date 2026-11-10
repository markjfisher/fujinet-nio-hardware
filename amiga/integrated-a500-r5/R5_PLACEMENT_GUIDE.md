# FujiNet A500 R5 — PCB Placement Guide

**Status:** Standing placement standard. Applies to every R5 placement task.  
**Scope:** Physical PCB layout only; the verified R4-derived electrical design remains authoritative unless a separate schematic change is approved.

## 1. Design intent and priorities

Build a board that is **electrically sound, routable, mechanically compatible, orderly, and readable**. Minimise estimated wirelength only after satisfying those requirements. A better HPWL score does not justify crowding, unclear component ownership, or poor routing access.

Priority order: (1) electrical and mechanical requirements, (2) local current loops and signal/return paths, (3) routing space and functional flow, (4) repeatable alignment and orientation, (5) clear references, (6) global HPWL.

## 2. R5 baseline and floorplan

- R5 is a separate KiCad project. **Do not modify R4.** Preserve schematic connectivity, component identities, footprints, net assignments, design rules, and valid UUID associations.
- Retain the board outline, mounting-hole geometry, and **J40's exact position, orientation, and mating height**. Verify case and connector clearance.
- Treat all other R4 positions, locks, and groups as **untrusted placement**, not as constraints. Stage those footprints neatly outside the board in the R5 working copy, retaining their identity and connectivity. Do not automatically reuse obsolete groups.
- Place **U20 (RP2350) approximately centrally within the usable component area**, with room on all sides for its pin-specific support parts and routing. Central does not mean the exact geometric centre if that compromises the layout.
- Reserve an uninterrupted, adequately wide **bus-buffer corridor beside J40 on the right** for U40–U47 and their local bypasses. Do not allow the RP cluster or unrelated logic to consume this corridor.
- Reserve mechanical/access regions for USB, microSD, antenna, service headers and buttons. The ESP32 antenna needs the manufacturer-specified all-layer copper/placement keep-out.
- Assume a four-layer board with a continuous ground plane; do not assume planes eliminate the need for short local return paths.

## 3. Place in dependency order

1. Mechanical datums and reserved regions (J40, holes, enclosure, connectors and antenna).
2. RP2350 **U20 and its complete support cell**: internal regulator, pin-specific decoupling, QSPI flash, crystal, USB resistors and relevant bias parts.
3. USB input/protection and power conversion, then ESP32 and SD.
4. Amiga-facing bus buffers and their local decoupling, using a repeatable layout pattern.
5. Host-interface power guard, supervisors, output-disable logic and associated hold-up components.
6. Remaining control logic, pull networks, headers and service components.

**Approval gate:** finish and review one cluster before moving to the next. Do not place all components in one pass.

## 4. Internal optimisation of every cluster

- Identify the anchor IC, all owned support parts, their exact nets/pins, and any placement-sensitive connections **before moving them**.
- Orient and place to minimise *critical* trace length, current-loop area, stubs, crossings and return-path discontinuities. Leave practical trace/via escape routes and assembly clearance.
- For decouplers, map each capacitor to a specific supply pin or supply-pin cluster. Prefer the supply pad facing its IC pin **when that improves the full supply-and-ground loop**; provide a short ground via to the plane. Do not enforce one universal capacitor rotation.
- For switching regulators, use the manufacturer/reference-layout topology for input/output capacitors, inductor, switching node, feedback and ground. For the RP2350, follow the Raspberry Pi reference layout, including inductor orientation. Keep crystal and QSPI connections short and appropriately arranged.
- Place series resistors such as RP USB R22/R23 **in their actual signal paths**, close to the intended source/receiver as required; keep the USB pair orderly. Place R24 with its actual owning circuit, not wherever a label fits.
- Align repeated capacitors/resistors consistently (grid, spacing, rotation, and label side) **when electrically equivalent**. Repeated buffer-plus-bypass cells should use the same reviewed template unless a real routing constraint requires an exception.
- A group is not accepted until its internal geometry is electrically sensible, legible and locally checked. Only then create/update its KiCad group. Treat approved sensitive clusters as rigid; other clusters may be moved as units later.

## 5. Readability and alignment rules

- Reference designators must be **unambiguous**: each label must clearly belong to one footprint, not sit over another component or between two candidates.
- Initial reference text standard: **0.6 × 0.6 mm, stroke 0.09 mm**, subject to fabrication capability. Use consistent text orientation and placement relative to similar footprints.
- No reference overlaps with another label, component body, pad, or protected region. Check against neighbouring **fixed and staged** components, not just selected ones.
- Keep related ICs and passives in visually coherent rows/columns where this does not compromise the electrical design. Avoid arbitrary angles, irregular gaps, isolated/dangling support parts, and unexplained inconsistencies.
- Maintain visible separation between functional clusters and leave room for routing. Do not fix a crowded placement by merely hiding its labels.
- Check both native KiCad DRC and a zoomed visual view. A courtyard-only pass is insufficient.

## 6. Tool boundaries and preservation

- **Astra:** choose electrically justified placement, define group ownership/constraints, verify and report.
- **kicad-mcp:** preferred interface for footprint movement, rotation and supported grouping operations. If an operation is unsupported, explain the gap before using a narrowly scoped native KiCad alternative.
- **CadMust-Neo:** optional *later* optimisation of already reviewed movable clusters. Run on a disposable copy, constrain selection, and independently check antenna/connector clearance, labels, unchanged footprints and DRC. Never accept solely on HPWL.
- No custom placement optimiser, stale coordinate generator, whole-board regeneration, or unapproved routing.
- Preserve the authoritative project until the candidate is reviewed. For any approved transfer, verify unchanged schematic nets, footprint identities, mechanical datums, and unselected objects.

## 7. Acceptance checklist for each cluster

- [ ] Every support part accounted for; pin/net ownership explained.
- [ ] Power, ground, timing and critical routing paths make physical sense.
- [ ] Capacitor/series-resistor orientation is intentional; manufacturer layout followed where applicable.
- [ ] Courtyards, mechanical clearance, antenna/connector keep-outs and routing access pass.
- [ ] Similar cells are consistently oriented/aligned; no dangling components.
- [ ] Reference labels are legible, non-overlapping and unambiguously owned.
- [ ] Native DRC and schematic/PCB parity checked; new findings identified separately from baseline.
- [ ] Close-up and floorplan images supplied for human review **before proceeding**.

## 8. First R5 milestone

Create an independent R5 working project; retain J40, outline and holes; stage all other components off-board; reserve the right-side buffer corridor; then **place only the RP2350 cluster** with the rules above. Return an overview, legible close-up, and short placement rationale. **Stop for approval.**
