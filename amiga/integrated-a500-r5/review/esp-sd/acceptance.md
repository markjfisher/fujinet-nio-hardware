# ESP32/microSD placement acceptance and transfer

Approved by the user on 2026-11-11, conditional on retaining antenna and card
access. Twenty reviewed footprint positions, rotations and reference placements
were transferred through kicad-mcp to authoritative R5. Native KiCad carried over
only the already-reviewed U30 silk geometry, antenna rule-area footprint setting
and two groups, because MCP lacks those operations. No new U30 footprint change
was made to suppress its intentional library-mismatch warning.

Read-back confirms the entire authoritative PCB's parsed contents equal the
approved `review/esp-sd/candidate/integrated-a500-r5.kicad_pcb`, including all
203 footprints, groups and rule areas. Existing RP2350, USB, power and mux
geometry is retained. Native DRC findings exactly equal the accepted candidate:
4 J1 hole-clearance errors, 199 text-height warnings, 1 intentional U30 footprint
mismatch warning, 499 unrouted connections, zero schematic parity issues.
See [transfer DRC](../bus-buffers/transfer-drc.json) and
[preservation verification](../bus-buffers/verification.json).

## Standing mechanical requirement: J30 access

J30 opens to the left. Retain its position, orientation and insertion/ejection
artwork. The ejected-card envelope is x=-10.525..-5.125, y=54.575..65.575 mm;
its upper edge is 0.575 mm below the antenna exclusion. This small separation
is **not a validated finger-access allowance**.

The enclosure must provide an unobstructed opening for a card to be inserted
fully, pressed to latch/release the push-push mechanism, and gripped after
ejection. Wall thickness, recess depth, bevels, finger access and manufacturing
tolerances must be checked using the actual socket/card and a mechanical mock-up
before enclosure release. Do not accept a slot that clears the card outline but
prevents pressing or removing it. No aperture or finger-clearance dimension is
claimed validated by this PCB-only review.

Retain U30's all-layer antenna exclusion x=-26.75..-5.75, y=6..54 mm and external
antenna overhang. Future enclosure walls, fasteners and conductive features must
respect the antenna requirements. Keep the explicit footprint/pad exclusion
check from `review/esp-sd/verify.py`; U30's own body is the sole footprint exception.
Later routing still needs to preserve the documented USB corridors and returns.
