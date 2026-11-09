# A500 R4 — first physical placement candidate

R4 turns the protected R3 circuit into a **111 × 117 mm horizontal sidecar
placement**, with the female A500 socket at the right edge and an 18 mm
component-free band behind that edge (the socket solder lands are excepted). It is a new project;
released passive hardware and R0–R3 remain unchanged.

Open the [board preview](review/placement.png), [native project](integrated-a500-r4.kicad_pro)
or [nine-page schematic](review/schematic.pdf). The PCB contains all 188 physical
components and four mounting holes. **It has no routed copper yet.** Separate
pads in the preview are component lands, not completed connections. Matching
schematic labels are electrically connected: native checks verify 864 functional
pin assignments on 195 complete nets, and schematic/PCB parity is zero.

| Requirement | Implementation | Evidence/check | Remaining decision or check |
| --- | --- | --- | --- |
| Direct horizontal A500 attachment | ED86BGFBK assembly footprint at right edge; board extends left | Original Matze Eagle package and supplied Gerbers; native check of all 86 pads | Tail-forming process, socket/body and case fit |
| Run / Flash RP / Flash ESP | Shared USB-C, two analog switches, cold mode jumper | Eight control combinations; exact native nets | Coupled USB routing and switched-circuit qualification |
| Independent recovery | Four physical BOOT/RESET buttons; RP SWD and ESP UART headers | Complete pin allocation and PCB pad coverage | Final button/header height and enclosure access |
| Power and Amiga-off isolation | USB-C >=1.5A source; protected input, reverse blocking; Amiga 5V sensed only | [Power calculation and assumptions](../integrated-a500-r3/power-review.md); 1.166A conditional input budget | Buck layout, effective capacitance, thermal/fault/current-downgrade behaviour |
| RP pins and bus safety | All 48 GPIO allocated; dedicated USB/QSPI/debug; LVC buffers and hardware interlocks | [Pin table](rp2350-pin-allocation.csv); 65,536 static and 65,536 sequential cases | PIO deadlines, propagation delay and active-bus validation |
| RP regulator placement | Six reference footprints and relative positions from Raspberry Pi's R4 design | Native geometric/net checks; source hash and MIT notice retained | Copper, ground return and regulator qualification |
| Physical layout | Four copper layers enabled; local bus/control bypass capacitors; antenna keepout on all copper | Native parity, DRC, pad mapping and visual inspection | Stackup, critical routing, ordinary routing, final BOM and DFM |

The electrical decisions remain in the [R3 power review](../integrated-a500-r3/power-review.md),
[R2 engineering](../integrated-a500-r2/engineering.md) and
[bus review](../integrated-a500-r3/bus-review.md). R4 changes footprint assignments
and makes the unused microSD detection contacts explicit; it does not change
the bus protocol or consume additional RP GPIO. Existing USB demonstrations
and passive logic-analyzer observations remain accepted.

See [mechanical/component evidence](implementation.md) and
[verification and outstanding findings](review/verification.md).
The circuit BOM is not yet an orderable manufacturing BOM. No fabrication
files, vendor upload, order, push or workspace submodule-pin change is included.

## Reproduction

Source the workspace `scripts/env.sh`. Run `build.py`, `pcb_build.py`,
`finish_mcp.py` and `apply_bypass.py` with the pinned
`repos/fujinet-nio-hardware/.local-tools/kicad/venv/bin/python`.
Run the native checking/geometry scripts with system Python:

1. `make_footprints.py` constructs the A500 footprint through pcbnew. The six
   checked-in RP footprints are already present. To refresh those, download the
   cited official reference ZIP and pass its extracted directory to
   `import_rp_footprints.py`.
2. Register the project-local library using
   `uv run --with kiutils==1.4.8 python register_library.py`.
   This writes library configuration only, using its LibTable serializer.
3. `build.py`, then `check.py`: MCP schematic construction and independent
   native netlist/ERC/PDF export. `update_footprints.py` is an optional incremental
   property update, not required after a fresh build.
4. `pcb_build.py`: MCP board construction and constrained placement. Its
   `pending_approval` status is an internal routing checkpoint, not a request
   for another user permission.
5. `finish_native.py`, then `finish_mcp.py`: repair the documented tool export
   gaps, establish DFM targets and make the placement adjustments.
6. `plan_bypass.py`, then `apply_bypass.py`: calculate legal local bypass
   positions and apply them through MCP.
7. `fit_mechanics.py`, then `apply_mechanics.py`, then `reserve_connector.py`
   applies the owner-measured envelope without regenerating the board.
8. `check.py`, `power_check.py`, `pcb_check.py`: independent final checks.
   `pcb_check.py` also exports the native placement SVG. Raster preview uses
   CairoSVG; no image generation or hand-edited CAD is involved.

The actual saved candidate is the review artifact. These scripts are not a
fabrication pipeline. Do not run whole-board generation after adding routes:
it replaces the board. Do not run generic placement autofix: this pinned MCP
implementation does not respect footprint locks.
