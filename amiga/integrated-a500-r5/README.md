# FujiNet A500 R5 — placement review candidate

Start with [board requirements and functional-block rationale](../docs/a500-board-requirements.md)
for a shareable explanation of what this board does and why its circuitry exists.

Open [integrated-a500-r5.kicad_pro](integrated-a500-r5.kicad_pro).
Electrical baseline: authoritative R4 at hardware commit `46e0bb7a`, **not** the
CadMust trial. R4 was copied without regenerating the board or schematic.

[R5_PLACEMENT_GUIDE.md](R5_PLACEMENT_GUIDE.md) is the standing acceptance specification.
[RP pad-level review](review/pad-refinement/report.md) and
[RP2350 close-up with pad nets](review/pad-refinement/pad-nets.png) were approved
as milestone 1 at `8c00c072`. Preserve that geometry and its proposed ground vias;
regulator copper, crystal routing and USB pair escape still require validation.
The [initial milestone report](review/milestone-1/report.md) is retained as historical evidence.

The root PCB now contains the approved RP, USB/power, USB mux, ESP32/microSD and bus-buffer cells; the power
placement was transferred through MCP in `1e8f0634`. The accepted
[USB corridor assessment](review/usb-power/corridor/assessment.md) remains a
placement constraint.

The approved mux placement was transferred in `57eccde7`, preserving all other
footprints and existing groups. Its shared PC/LINK nets, differential-pair fan-out
and continuous ground reference remain routing requirements.

The ESP32/microSD placement was approved and transferred on 2026-11-11. Retain
its [antenna and J30 enclosure/finger-access requirements](review/esp-sd/acceptance.md)
and the intentional U30 silk/library warning.

The [bus-buffer placement is accepted and transferred](review/bus-buffers/acceptance.md).

The host-protection, control-logic, service and indicator placements are now
approved and transferred to authoritative R5. All 214 footprints are front-side
following the accepted C42/C43 transfer. See the
[host-protection acceptance](review/host-protection/acceptance.md),
[control-logic acceptance](review/control-logic/acceptance.md),
[service/indicator transfer](review/indicators/transfer/acceptance.md) and
[single-sided population acceptance](review/front-sd/acceptance.md).
Earlier candidate reports are retained as historical review evidence.

No routing or fabrication readiness is implied. Service/header positions and
enclosure access still need mechanical validation.

The current outline is not an absolute limit. Propose a modest extension above
or below if later circuitry needs room; user approval is required before editing
the outline. Preserve J40's exact geometry and mating position.
