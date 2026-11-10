# FujiNet A500 R5 — placement review candidate

Open [integrated-a500-r5.kicad_pro](integrated-a500-r5.kicad_pro).
Electrical baseline: authoritative R4 at hardware commit `46e0bb7a`, **not** the
CadMust trial. R4 was copied without regenerating the board or schematic.

[R5_PLACEMENT_GUIDE.md](R5_PLACEMENT_GUIDE.md) is the standing acceptance specification.
[RP pad-level review](review/pad-refinement/report.md) and
[RP2350 close-up with pad nets](review/pad-refinement/pad-nets.png) were approved
as milestone 1 at `8c00c072`. Preserve that geometry and its proposed ground vias;
regulator copper, crystal routing and USB pair escape still require validation.
The [initial milestone report](review/milestone-1/report.md) is retained as historical evidence.

The root PCB now contains the approved RP and USB/power cells; the power
placement was transferred through MCP in `1e8f0634`. The accepted
[USB corridor assessment](review/usb-power/corridor/assessment.md) remains a
placement constraint.

The **USB mux cell** is ready for visual review:
[report](review/usb-mux/report.md),
[open candidate project](review/usb-mux/candidate/integrated-a500-r5.kicad_pro),
[pad-net close-up](review/usb-mux/pad-nets.png), and
[context view](review/usb-mux/context.png).
Only the separate candidate adds U1/U2, C1/C2 and R1/R2. Do not transfer it or
place another cluster before approval. No routing or fabrication readiness is implied.
