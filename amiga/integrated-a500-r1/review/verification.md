# R1 verification — 2026-11-09

Result: **saved circuit connectivity/static-logic checks pass; electrical and
mechanical release remains open.** No PCB or fabrication claim.

Commands, after `source scripts/env.sh`:

```sh
repos/fujinet-nio-hardware/.local-tools/kicad/venv/bin/python \
  repos/fujinet-nio-hardware/tools/kicad/apply-compat.py
repos/fujinet-nio-hardware/.local-tools/kicad/venv/bin/python \
  repos/fujinet-nio-hardware/amiga/integrated-a500-r1/build.py
python repos/fujinet-nio-hardware/amiga/integrated-a500-r1/check.py
```

The final independent native KiCad 10.0.7 read-back contains 171 physical
components. Exact membership checks pass for **803 physical pin assignments
on 183 nets**, including all cross-sheet connections and all 81 RP2350B pads.
The test rejects accidental net merges as well as missing connections.
RP GP2–GP7 remain A2–A7; GPIO45/46 are IRQ_REQ/BUS_READY.

Static evaluation from exported IC pins passed 32,768 interlock combinations,
32 high-address patterns and eight USB mode/polarity cases. This does not
replace propagation-delay/analog/startup analysis, firmware or active-board
measurements. Required firmware sequencing is recorded in engineering.md.

Native ERC reports **30 pin_not_driven findings**, retained in erc.json.
Every finding is at J40: A1–A23, /AS, /UDS, /LDS, READ, /RESET, /DTACK and
/INT2. The existing connector symbol declares these as inputs; the actual
motherboard address/control drivers and wired-signal pull-ups are outside
this schematic. The check rejects any other ERC finding. No ERC exclusions
were added, and this is explicitly **not a zero-ERC pass**. Correctly modeling
external host drivers/pull-ups remains distinct from proving the circuit.

All eight native PDF pages were rendered and visually inspected. They contain
the overview, power, USB/recovery, RP, ESP/storage, address and data buffers,
and interlock logic. No blank processor page or off-page content remains.
Functional grouping and explicit local capacitor/divider wires improve the R0
presentation, but substantial label-based wiring remains; a final schematic
presentation pass is still due before layout. Named power connections are
real nets, not unconnected capacitors.

Live configured MCP read-back of rp.kicad_sch succeeded: 32 placed symbols
(including power flags), 237 wires and 48 junctions. MCP reports modified=true
on load; no save was issued during that read-only inspection. Fresh MCP
construction processes used the configured launcher and successfully queried
libraries. The native export, rather than MCP counts, is the connectivity
acceptance evidence.

The tools' private-property formatter patch was tested against the actual
RP2350B and Crystal_GND24 library definitions: parse/format/parse equality
passes, and native KiCad now loads and exports both in the full candidate.
Patch application is hash-guarded and idempotent; setup shell syntax passes.
Tool limitations/workarounds are recorded in tools/kicad/README.md.

Preservation check passed against hardware setup baseline acaea6b3:

```sh
git -C repos/fujinet-nio-hardware diff --exit-code acaea6b3 -- \
  amiga/prototyping-board kicad/libraries
```

Neither the manufactured passive breakout nor its custom connector library was
rewritten. R0 CAD is untouched. No board DRC/parity was run because R1 has no
PCB. No hardware experiment, firmware flashing, fabrication upload or order
was performed. Workspace submodule pins remain unchanged.
