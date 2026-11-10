# R5 standing placement specification

Read and follow [R5_PLACEMENT_GUIDE.md](R5_PLACEMENT_GUIDE.md) before every R5
placement task. Its per-cluster checklist and approval gates are acceptance
criteria. R4 remains unchanged; preserve the R4-derived electrical design.
The floorplan and refined RP2350 support cluster at `8c00c072` are approved as
milestone 1. Preserve their internal geometry and the proposed ground-via sites
in `review/pad-refinement/pad-checks.json`. Copper remains subject to routing
validation. USB/power and its corridor assessment are approved and the power
placement was transferred to the root PCB in `1e8f0634`. The approved USB mux
cell was transferred in `57eccde7`. ESP32/microSD is now a separate candidate in
`review/esp-sd/candidate/`, pending visual approval. Do not transfer it or place
another cluster before that review. Retain its explicit antenna exclusion check
and documented local U30 silkscreen exception if accepted.

For subsequent placement, preserve the planning corridors and paired
mux allowance in `review/usb-power/corridor/assessment.md`. These are reviewed
feasibility envelopes, not routed copper or final impedance geometry.
