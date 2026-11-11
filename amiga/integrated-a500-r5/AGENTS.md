# R5 standing placement specification

Read and follow [R5_PLACEMENT_GUIDE.md](R5_PLACEMENT_GUIDE.md) before every R5
placement task. Its per-cluster checklist and approval gates are acceptance
criteria. R4 remains unchanged; preserve the R4-derived electrical design.
The floorplan and refined RP2350 support cluster at `8c00c072` are approved as
milestone 1. Preserve their internal geometry and the proposed ground-via sites
in `review/pad-refinement/pad-checks.json`. Copper remains subject to routing
validation. USB/power and its corridor assessment are approved and the power
placement was transferred to the root PCB in `1e8f0634`. The approved USB mux
cell was transferred in `57eccde7`. ESP32/microSD is approved and transferred to
the root PCB; retain its explicit antenna exclusion check and intentional U30
silkscreen/library exception. Follow `review/esp-sd/acceptance.md` for the J30
enclosure opening, push-push travel and finger-access validation requirement.
The bus-buffer cell is approved and transferred to the root PCB. Retain its
explicit buffer-corridor ownership checks and proposed ground vias.
The host-protection cell is approved and transferred to the root PCB. Preserve
its internal geometry and ground-via sites; entire groups can be reconsidered
later for routing. See `review/host-protection/acceptance.md`.
The outline can be extended above/below only after an explicit proposal and
approval; do not crowd later circuitry to fit. J40 remains mechanically fixed.

For subsequent placement, preserve the planning corridors and paired
mux allowance in `review/usb-power/corridor/assessment.md`. These are reviewed
feasibility envelopes, not routed copper or final impedance geometry.

The control-logic placement is approved and transferred to the root PCB.
Preserve its reviewed geometry, groups and prospective ground-via locations.
See `review/control-logic/acceptance.md`.

The service-header/button candidate in `review/service/candidate/` is pending
visual approval. Do not transfer it yet. All service positions are provisional
pending enclosure review; retain its access-envelope planning requirements.

The indicator candidate in `review/indicators/candidate/` adds PWR/NET/DISK
(GPIO4/5 on ESP32) on top of the still-pending service candidate. Neither has
been transferred. Review `review/indicators/report.md` and its FIT/DNP assembly
matrix before accepting; each channel uses onboard OR wired LED, not both.
