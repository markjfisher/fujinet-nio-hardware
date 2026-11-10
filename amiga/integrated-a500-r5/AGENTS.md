# R5 standing placement specification

Read and follow [R5_PLACEMENT_GUIDE.md](R5_PLACEMENT_GUIDE.md) before every R5
placement task. Its per-cluster checklist and approval gates are acceptance
criteria. R4 remains unchanged; preserve the R4-derived electrical design.
The floorplan and refined RP2350 support cluster at `8c00c072` are approved as
milestone 1. Preserve their internal geometry and the proposed ground-via sites
in `review/pad-refinement/pad-checks.json`. Copper remains subject to routing
validation. The next USB/power cluster is a separate candidate in
`review/usb-power/candidate/`, pending visual approval. Do not transfer it or
place another functional cluster before that review.
