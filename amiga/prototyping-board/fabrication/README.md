# Fabrication instructions — revision A, two-layer prototype release

**FABRICATION-READY — PROTOTYPE SPIN ONLY.** Target fabricator: **PCBWay**.
Mating socket: **WingTAT ED100BGFBK / LCSC C5173320**.
Commodore A-5 controls the mating-card outline and bevel.
Physical fit and operation remain subject to prototype validation.

## Board and stack

- **Two copper layers, top/bottom only**; FR-4; **1.6 mm nominal finished
  board thickness with standard ±10% tolerance (1.44–1.76 mm) accepted**.
  Use PCBWay's standard thickness process. No tighter thickness tolerance,
  thickness sorting or advanced-line thickness control is required.
- Nominal 35 µm copper per layer. Stack: **F.Cu / FR-4 / B.Cu**.
  Solid GND pours on both faces stop above the tongue; remove unconnected
  islands. No internal copper layers or controlled impedance are specified.
- Body: 180 ×100 above the shoulder, overall height 107.62.
- Tongue: **129.26 ±0.1 width; 7.62 projection; R1.5 concave roots;
  1.5 ×45° planar tip-corner chamfers**. Follow Edge.Cuts, not a rectangular
  bounding box. The 2.40 nominal end margins follow the explicit tongue
  width and 124.46 contact span; do not move contacts to impose 2.50.
- Fingers: 50 per face, **2.54 pitch; 1.6 ×5 copper; 1.00 tip setback**.
  Even contacts on component face; odd on reverse. Do not mirror Gerbers.
  Length/setback are retained prototype choices, not separate A-5 dimensions.
- Routed signals 0.30; power/GND routes 0.60 minimum; absolute design
  minimum 0.25; clearance 0.20; via 0.65 / drill 0.30;
  header pads 1.70 / plated holes 1.00. Copper-to-outline minimum 0.50.
  No vias, drilled holes or ground pours in the tongue/bevel region.

## Bevel: controlling dimensions and process tolerances

**Machine both faces of the insertion edge: 0.5 mm ×45° per face.**
These A-5 dimensions control. With 1.6 nominal finished thickness, the
remaining centre land is **0.6 mm REF**, calculated as 1.6 −2×0.5.
**Do not independently constrain the land to 0.5 mm.**
The thickness bevel is distinct from the planar 1.5 ×45° corner chamfers.

PCBWay's [edge-connector guidance][edge] publishes machining tolerances of
**±5° angle and ±5 mil (±0.127 mm) chamfer height**. These are process
tolerances, not alternative nominal bevel dimensions or a tolerance assigned
to the reference land. Its [capability matrix][cap] separately lists bevel
depth ±0.15 mm in the normal capability band. Request the help-centre
±0.127 mm height tolerance; any process deviation is subject to CAM review.
Nominal copper starts 0.50 mm beyond the bevel. Even 0.627 axial machining
extent leaves 0.373 nominal clearance to copper before outline/registration
variation. Reject machining that reaches finger copper or leaves a knife edge.

The [gold-finger parameter table][gold] lists a 0.5 land alongside a 0.5
depth for a 1.6 board. Do not copy those as three independent exact constraints.
Use the A-5 callout above. The outline Gerber encodes planar routing only;
**these instructions must accompany it** to define the thickness bevel.

## Gold and mask

- **Selective electroplated hard gold over nickel on all 100 fingers**;
  target 30 µin gold over 120–150 µin nickel (within PCBWay's published
  gold-finger capability). ENIG may be used elsewhere. No HASL, tin or
  immersion-gold substitution on mating contacts.
- F.Mask and B.Mask each contain a **continuous filled opening**, extending
  across the complete tongue to/beyond the routed edge: board coordinates
  x=38…171.26, y=120…128.12. This follows PCBWay's
  [full-edge-connector exposure guidance][mask].
  No inter-finger mask dams; no mask, silk or paste on the contact region.
- J1 alone permits intentional solder-mask bridges in KiCad. This models
  the continuous window, not a waived copper short or global DRC exclusion.
- Smooth, burr-free mating edge. No tabs, tooling holes, plating-bus remnants
  or conductive debris may remain there. The fabricator supplies its plating
  process/panel plan and removes temporary plating connections, preserving
  every final net and all isolation requirements.
- No stencil is required; this assembly is through-hole only.

## Package and verification

Submit this file with the regenerated `gerbers/` and `drill/` outputs.
`SHA256SUMS` covers machine outputs and this instruction file. All layers
share one absolute millimetre origin. Review outputs include ERC/DRC,
schematic, layout and copper views.

Mechanical assertions, 100-contact mapping with five negative cases, ERC,
DRC and schematic parity must pass before export. Pad geometry/positions and electrical mapping are protected by a frozen
placement digest; tracks/vias were intentionally rerouted for two layers.
The original comparison datasets remain historical evidence. See the
[two-layer review](../docs/two-layer-review.md) for metrics and return-path limits.

## Prototype validation — not missing-documentation release holds

1. With power off, inspect board thickness, plating, bevel and mask; verify
   seating in the actual socket without forcing. Check root/housing clearance.
   Record finished thickness at the fingers. The accepted fabrication range
   reaches 1.76 mm, 0.04 mm above WingTAT's recommended 1.72 mm upper limit;
   socket fit across the full fabrication range has not been established.
   This is a prototype validation item, not a tighter supplier thickness limit.
   A floor gap is not itself a failed fit; do not deepen the tongue to bottom it.
2. Check all 100 contacts for continuity and neighbouring/opposite-contact
   isolation using `data/verification.csv`, including rails, reserved/NC,
   SenseZ3 and /CFGIN versus /CFGOUT.
3. Inspect contact witness marks and repeat continuity while gently moving the
   supported board. Record actual engagement/wipe and any intermittency.
   The WingTAT drawing does not specify a wipe envelope; prototype acceptance
   must establish adequate engagement with the retained 5 mm fingers.
4. Test host operation only after passive continuity checks. Support the
   bracketless board and leads. Loading, timing, thermal/current capacity,
   durability and other Amiga sockets are not qualified by this release.
   Signal bundles interrupt the two-layer ground pours; use short probe leads
   and check clock/control waveforms and host stability with the intended load.

[edge]: https://www.pcbway.com/helpcenter/ordering_parameter_instruction/Edge_Connector.html
[cap]: https://www.pcbway.com/capabilities.html
[gold]: https://www.pcbway.com/pcb_prototype/PCB_Gold_fingers.html
[mask]: https://www.pcbway.com/helpcenter/soldermask_issues/Soldermask_opening_for_Gold_fingers.html
