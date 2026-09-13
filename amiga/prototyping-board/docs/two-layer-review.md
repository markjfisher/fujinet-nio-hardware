# Two-layer prototype conversion

2026-09-11. **The two-layer board is the fabrication release candidate.**
Mechanical release conditions, WingTAT socket and hard-gold requirements
remain in [fabrication instructions](../fabrication/README.md).

## Was four-layer construction necessary?

No circuit-level requirement was found. This passive board has no active
components, controlled-impedance specification, or dedicated supply-plane
requirement. The four-layer board used In1.Cu as GND and In2.Cu for 337
signal/power track segments, totalling 3,998.549 mm. Those tracks could not
simply be deleted: the conversion required a complete reroute.

Four layers did provide a real benefit: an uninterrupted inner GND plane.
Two layers trade that benefit for lower fabrication complexity, not identical
signal-integrity performance. This assessment was reported before CAD changes.

## Measured comparison

Baseline: hardware repository commit
`7d2c536cdc554b39942488d1791c985eb286db0b`.
Machine-readable [four-layer](../review/layer-comparison/four-layer.json) and
[two-layer](../review/layer-comparison/two-layer.json) measurements include
source PCB hashes and per-net via counts/minimum widths.

| Property | Four-layer release | Two-layer candidate |
|---|---|---|
| Overall dimensions | 180 ×107.62 mm | Unchanged |
| Body above shoulder | 180 ×100 mm | Unchanged |
| A-5 tongue, roots, corners, bevel | Approved prototype geometry | Unchanged |
| Finished thickness | 1.6 mm nominal | 1.6 mm nominal; current release accepts standard ±10% |
| Copper layers | F.Cu, In1.Cu, In2.Cu, B.Cu | F.Cu and B.Cu only |
| Via count | 158 | **136**, 22 fewer (13.9%) |
| Track segments | 907 | 1,061, about 17% more |
| Total track length | 9,048.987 mm | 9,386.749 mm, **3.7% more** |
| Minimum routed signal width | 0.30 mm | 0.30 mm |
| Minimum routed power/GND width | 0.30 mm | **0.60 mm** |
| Design clearance | 0.20 mm | Unchanged; pours use 0.25 mm |
| Filled GND area | In1: 16,627.57 mm² | Front: 12,784.22; back: 12,265.20 mm² |
| ERC | 0 violations | 0 violations |
| DRC | 0 violations, 0 unconnected, 0 parity issues | Same |

Lengths count track centre-lines, not current paths through pours. Segment
count is a routing-complexity proxy, not a count of connections. Total copper
area on two sides is not a substitute for a continuous reference plane.

All 230 physical pads retain their positions, dimensions, orientation/layers,
net assignments and drill sizes. This preserves the 100 card-edge contacts,
header grouping and duplicate access points. Board silkscreen and all
schematic/mapping files are unchanged. The pad/placement SHA256 is identical:
`2b50b0156b9286cdf3ca5ca85dda12a1ade08a2852a383d0d97b9590baa579f2`.

## Routing and return-path assessment

- Straight connector escape tracks, orthogonal/45° routing, standard through
  vias and the existing header positions are retained. No narrower tracks or
  smaller clearances were needed. Wider rails improve the routed power/GND
  connections; this is not a thermal/current-rating claim.
- Solid GND pours occupy both faces within x=21…199, y=21…118, outside the
  gold-finger region. Unconnected islands are removed. GND vias and existing
  plated GND header holes join the two faces; all ground contacts pass DRC
  connectivity checks. No extra vias were scattered simply to increase count.
- The router left GND, BERR and INT2 incomplete. Reviewed completion paths
  resolve them without jumpers or mapping changes. BERR has two vias; INT2 is
  the local complexity hotspot with eight versus three previously. This is
  disclosed rather than describing every signal as a direct single-layer run.
- Pours are interrupted by signal bundles, particularly near the lower fan-out
  and header banks. Return currents can detour around these slots and between
  faces. The two-layer board is **not** equivalent to the old continuous
  reference plane; DRC cannot establish ringing, crosstalk or timing margins.
- For this passive bench prototype, the modest length increase and fewer
  total vias present no demonstrated material functional downside requiring
  retention of four layers. That is an engineering prototype decision, not
  measured signal-integrity qualification. Keep probe leads short, use nearby
  GND access and support the board. Check clocks/control edges and host
  stability with the intended probes/cables before relying on measurements.
  Reassess the stackup before adding active interfaces or long cable loads.

## PCBWay cost implications

Two copper layers remove two foils and multilayer processing. Lower base-board
cost is expected, but **no matched four-/two-layer quote is available**.
[PCBWay's quote form](https://www.pcbway.com/orderonline.aspx) separately
offers layer-count and finish options. The board's dimensions, selective hard
gold, bevel and outline still contribute to cost. On 2026-09-13 the user
reported an initial $70 quote rising to $746 after CAM review; PCBWay's
engineer identified our tight finished-thickness requirement as requiring
the advanced line and offered ±10%. The current fabrication instructions
accept that standard tolerance at 1.6 mm nominal. The revised price is not
yet confirmed; a return to $70 is not guaranteed. See the
[mechanical cross-check](mechanical-cross-check.md) for the resulting
thickness-range/socket-fit validation item.

## Verification and reproducibility

`scripts/check.py` passes the mechanical/placement tests, all 100 pin mappings,
five negative mapping cases, ERC and full DRC with schematic parity. No rule
severity was relaxed and no DRC exclusions were added. Existing J1-only mask
bridge permission continues to model its approved continuous mask window.

`scripts/generate.py` now prepares two-layer routing seeds. The checked-in
DSN/SES plus `routing/two-layer-completion.json` reproduce the routed board;
the completion file is bound to the SES hash and verified placement. Import
removes only KiCad-reported dangling copper, replays the completion and fills
both GND pours. The exploratory path search is not a build dependency.
Generation, import and checks were also exercised in a separate scratch copy.
The regenerated board's measured routing, placement and filled-copper metrics
match the release board exactly. A separate comparison against the baseline
PCB confirms unchanged outline and silkscreen drawing geometry/content.

Fabrication exports include only two copper layers. Obsolete inner-layer
Gerbers/SVGs are retained under `review/layer-comparison/four-layer-exports/`,
outside the current fabrication package. `fabrication/SHA256SUMS` covers the
current outputs and fabrication instructions.

**Release: FABRICATION-READY — TWO-LAYER PROTOTYPE CANDIDATE.** Physical
socket seating/wipe, continuity/isolation and host/probe-load validation
remain the prototype acceptance tasks; production qualification is not claimed.
