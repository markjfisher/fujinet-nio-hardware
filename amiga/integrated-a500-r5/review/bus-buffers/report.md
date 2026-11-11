# R5 bus-buffer placement — visual review candidate

The approved ESP32/microSD cell is now in authoritative R5; see its
[acceptance and mechanical-access requirements](../esp-sd/acceptance.md).
The **bus-buffer cell is candidate-only**. Open the
[candidate project](candidate/integrated-a500-r5.kicad_pro), then review
[address/control pad nets](address-pad-nets.png),
[data pad nets](data-pad-nets.png) and [floorplan](context.png).
Green rings are proposed ground-via locations, not routed copper.

## Engineering requirements and implementation

| Requirement | Implementation and evidence | Remaining validation |
|---|---|---|
| Correct bus flow | U40–U43 and U46/U47 at 180 degrees: Amiga inputs face right/J40; local outputs face left. U44/U45 at 0 degrees: local inputs left, host outputs right. Actual pads/nets checked. | Final fan-out and layer transitions; no pin swapping performed. |
| Local bypassing | C50–C57 each 100 nF, F.Cu, supply pad facing owning IC pin 20; every supply-pad centre distance is 1.60 mm. Ground-via space checked at capacitor and IC pin 10. | Short, wide supply/return copper into continuous ground plane. |
| Preserve safe control | R50–R53 remain 10 kΩ from main 3V3 to the associated pin-1 OE; signal pad faces OE, 1.55 mm pad-centre distance. BUS_DISABLE remains on pin 19 of all four data buffers. | Route control lines without shared noisy returns; preserve approved disable timing. |
| Separate power domains | U44/U45 and C54/C55 use 3V3_BUS; other buffers/bypasses use main 3V3. OE pull-ups remain on main 3V3 exactly as reviewed. | Keep 3V3_BUS distribution distinct; host protection stays staged for the next cluster. |
| Mechanical and routing room | All 20 footprints fit x=72..87, y=12..110 buffer corridor. J40 clearance x=87..94.5 and all existing USB corridors untouched. | Connector-side escape requires F/B layer access; this is not a routed proof. |
| Consistent cells | Repeated receive cells at 11 mm pitch; adjacent TX/RX pairs per data byte, with support parts outside the pair. All references 0.6 mm / 0.09 mm, horizontal, clear of pads. | Visual approval. |

The existing SN74LVC541APWR PW/TSSOP-20 assignment was checked against
[TI datasheet SCAS298O, pin table and sections 8.3–8.4](https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf).
Pin 20 is VCC, pin 10 GND, and pins 1/19 are active-low enables. TI calls for
local bypassing, short ground returns and an unbroken ground reference. This
task changes neither component selection nor the reviewed power-state circuit.

## Ownership and positions

All IC centres are x=80 mm. The vertical sequence follows address/control then
high-byte and low-byte data. High-byte precedes low-byte because J40's high data
pins start above the low data pins. Shared-byte connections still require
fan-out; adjacency does not remove every crossing.

| IC | Centre y / angle | Function | Bypass | Local OE pull-up |
|---|---|---|---|---|
| U40 | 25 / 180° | A1–A8 receive | C50 | None; both OEs grounded |
| U41 | 36 / 180° | A9–A16 receive | C51 | None; both OEs grounded |
| U42 | 47 / 180° | A17–A23 and AS receive | C52 | None; both OEs grounded |
| U43 | 58 / 180° | UDS/LDS/READ, conditioned RESET/DTACK/BERR inputs | C53 | None; both OEs grounded |
| U45 | 73 / 0° | D8–D15 transmit | C55 | R51, TX_HI_N |
| U47 | 81 / 180° | D8–D15 receive | C57 | R53, RX_HI_N |
| U44 | 95 / 0° | D0–D7 transmit | C54 | R50, TX_LO_N |
| U46 | 103 / 180° | D0–D7 receive | C56 | R52, RX_LO_N |

U43 retains the exact existing grounded inputs and no-connect outputs; the
conditioned host signals come from the protection circuitry, not direct raw
J40 connections. [Pin inventory](pin-nets.json) is authoritative for each pad.

## Verification and tool boundaries

- Twenty selected footprints changed; 183 others are semantically identical to
  authoritative R5, including U30 and J30, all approved RP/power/USB/mux geometry,
  mechanical datums, footprint UUIDs, pads/nets, locks and existing groups.
- Eight buffer groups were added after local checks using native KiCad. MCP lacks
  group editing. All footprint/reference edits used kicad-mcp; no CAD generator
  or custom placement script was used.
- The empty-floorplan `R5 reserved buffer corridor` footprint prohibition was
  released in the candidate through native KiCad, since MCP cannot edit rule
  areas. Its outline is unchanged. The verifier requires every selected buffer
  footprint to fit inside, and excludes every unrelated footprint. This is an
  ownership reservation, not an electrical copper keep-out. Antenna and connector
  rule areas remain unchanged.
- Native DRC and MCP DRC: **no new findings** compared with the approved ESP
  baseline. Retained findings: 4 J1 hole-clearance errors, 199 text-height warnings,
  1 intentional U30 library mismatch, 499 unrouted connections. Zero parity issues.
  ERC sheets exactly match the baseline (31 existing findings).
- MCP audit reports no selected-cell overlap or silk/reference overlap. Its
  12 existing coarse overlap reports concern the accepted ESP antenna bounding
  box and backside SD caps; 99 boundary/keep-out reports include staged parts
  and existing connector/antenna geometry. Native polygon checks are unchanged.
- Sixteen proposed 0.6/0.3 mm ground vias have at least 0.618 mm clearance to
  foreign pad bounding boxes. All previously reviewed proposed via sites remain
  available. No vias, tracks or zones of routed copper were added.
- Native front renders were visually inspected with actual pad-net overlays.
  Schematic/project/library files are unchanged. `verify.py` and `render.py` are
  read-only CAD consumers, not placement generators.

Evidence: [verification](verification.json), [native DRC](drc.json), [ERC](erc.json),
[MCP audit](mcp-audit.json), [MCP DRC summary](mcp-drc-summary.json),
[exact placement record](placement.json).

Stop for visual review before transfer or placement of the host-protection cell.
No routing or global optimisation has been performed.
