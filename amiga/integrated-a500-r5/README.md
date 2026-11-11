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

The root PCB now contains the approved RP, USB/power, USB mux and ESP32/microSD cells; the power
placement was transferred through MCP in `1e8f0634`. The accepted
[USB corridor assessment](review/usb-power/corridor/assessment.md) remains a
placement constraint.

The approved mux placement was transferred in `57eccde7`, preserving all other
footprints and existing groups. Its shared PC/LINK nets, differential-pair fan-out
and continuous ground reference remain routing requirements.

The ESP32/microSD placement was approved and transferred on 2026-11-11. Retain
its [antenna and J30 enclosure/finger-access requirements](review/esp-sd/acceptance.md)
and the intentional U30 silk/library warning.

The **bus-buffer cluster** is ready for visual review:
[report](review/bus-buffers/report.md),
[open candidate project](review/bus-buffers/candidate/integrated-a500-r5.kicad_pro),
[address/control pad nets](review/bus-buffers/address-pad-nets.png),
[data pad nets](review/bus-buffers/data-pad-nets.png), and
[floorplan](review/bus-buffers/context.png).
Only the separate candidate contains these 20 placed components. Do not transfer
it or place another cluster before approval. No routing or fabrication readiness
is implied.
