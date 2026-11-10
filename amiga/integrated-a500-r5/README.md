# FujiNet A500 R5 — placement review candidate

Open [integrated-a500-r5.kicad_pro](integrated-a500-r5.kicad_pro).
Electrical baseline: authoritative R4 at hardware commit `46e0bb7a`, **not** the
CadMust trial. R4 was copied without regenerating the board or schematic.

[R5_PLACEMENT_GUIDE.md](R5_PLACEMENT_GUIDE.md) is the standing acceptance specification.
[Milestone 1 report](review/milestone-1/report.md), [floorplan](review/milestone-1/overview.png),
and [RP2350 close-up](review/milestone-1/rp-cluster.png) are ready for visual review.

Only mechanical datums and the RP2350 support cell are on-board. The remaining
167 footprints are staged off-board. Do not place another cluster or route until
the milestone is reviewed. No fabrication readiness is implied.
