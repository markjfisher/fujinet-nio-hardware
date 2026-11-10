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

The root PCB remains that approved baseline, with 167 footprints staged.

The **USB input/protection and power-conversion placement candidate** is ready
for visual review: [report](review/usb-power/report.md),
[open candidate project](review/usb-power/candidate/integrated-a500-r5.kicad_pro),
[overview](review/usb-power/overview.png), and
[pad-net close-up](review/usb-power/pad-nets.png).
Only this separate candidate has the next 36 components placed. Do not transfer
it or proceed to ESP/SD or routing before approval. No fabrication readiness is implied.
