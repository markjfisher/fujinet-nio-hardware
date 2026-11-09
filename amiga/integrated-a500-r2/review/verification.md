# R2 verification — 2026-11-09

The configured MCP responded successfully to guidance, symbol/footprint
searches and read-only inspection of the passive breakout (13 components,
230 wires). No save was issued for that project. Fresh construction used the
same repository launcher with the existing KiCad-10 compatibility patch.

Native KiCad exported and checked 177 physical components, 831 connected
physical pin assignments and 189 exact nets, including all 81 RP pads.
Checks reject unintended extra members as well as missing connections.
/DTACK has exactly two members: J40.66 and receiver U43.7, with no board driver.

Saved-netlist evaluation passed 65,536 static bus combinations, 32 address
patterns and eight USB mode/polarity combinations. The two new flip-flops were
checked over 65,536 five-step sequences covering asynchronous clear, qualified
completion, held requests and back-to-back cycles. These are digital functional
checks, not timing, analog, firmware or hardware qualification.

Native ERC retains **32 pin_not_driven findings** at J40: the previous 30
external-host driver/pull-up model findings plus XRDY and /BERR. No exclusions
were added. The check rejects any other finding; this is not zero ERC.

All eight native PDF pages were rendered and visually inspected. The new
latches, BERR input, XRDY sink and sheet ports are present and within the page.
Matching labels establish electrical connections; the schematic still needs
a final presentation pass before layout. PDF order is assigned by KiCad.

Commands after `source scripts/env.sh`:

```sh
repos/fujinet-nio-hardware/.local-tools/kicad/venv/bin/python \
  repos/fujinet-nio-hardware/amiga/integrated-a500-r2/build.py
python repos/fujinet-nio-hardware/amiga/integrated-a500-r2/check.py
pdftoppm -scale-to 1600 -png \
  repos/fujinet-nio-hardware/amiga/integrated-a500-r2/review/schematic.pdf \
  /tmp/a500-r2-review
```

The [bus review](../bus-review.md) documents manufacturer delay maxima and the
provisional 44.9ns assertion allocation against Commodore's 60ns limit. Actual
loading, edges, firmware sequencing and host revision timing remain open.
Power protection, CC downgrade handling, the female socket and BOM remain open.
No PCB exists: DRC, schematic/PCB parity and USB pair geometry are not checked.

Released passive CAD, its libraries and R0/R1 candidates are preserved. No
physical test, firmware flash, fabrication upload/order or push was performed.
Workspace submodule pins remain unchanged.
