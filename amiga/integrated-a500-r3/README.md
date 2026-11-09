# Direct A500 candidate R3 — protected input supply

**Circuit review candidate; not an electrical or manufacturing release.**
R3 adds an electronic fuse, reverse-blocking ideal diode and CC ESD protection
to the preserved R2 circuit. The 48-GPIO allocation and A500 XRDY handshake
are unchanged.

Open the [nine-page schematic](review/schematic.pdf),
[power review](power-review.md), [connector selection](mechanical-selection.md)
and [component selection status](component-selection.md).
The native project is [integrated-a500-r3.kicad_pro](integrated-a500-r3.kicad_pro).
The [engineering index](engineering.md) identifies inherited decisions and
remaining gates. R0/R1/R2 and released passive hardware are untouched.

| Requirement | R3 implementation | Check | Open |
| --- | --- | --- | --- |
| Overload / overvoltage | TPS259630, programmed current and voltage thresholds | Native pin/value checks; tolerance corners | Fast fault transients / startup |
| Reverse VBUS isolation | LM66100, CE tied to output | Manufacturer pin map and full net membership | Transient backfeed qualification |
| CC ESD | TPD2E2U06 shunt channels | Pin table, normal voltage rating | System ESD / layout |
| Current budget | 1.2A at 3.3V, USB-C >=1.5A | Calculated 1.166A input; minimum limit 1.197A | Thermal and efficiency assumptions |
| A500 socket | ECC43DRAN catalogue candidate | Pitch, mating thickness, tail rows and housing dimensions | Contact orientation and case envelope |
| PCB preparation | Existing circuit and package review | No substitute male-edge footprint | Final BOM and mechanical constraints before placement |

Run after `source scripts/env.sh`:

```sh
python repos/fujinet-nio-hardware/amiga/integrated-a500-r3/check.py
python repos/fujinet-nio-hardware/amiga/integrated-a500-r3/power_check.py
```

Rebuild with the pinned tool-venv Python and this directory's `build.py`.
Construction uses the MCP; native KiCad independently exports nets, ERC and PDF.
See [verification](review/verification.md). The 33 retained ERC findings are
reviewed model/grounded-status cases, not a clean ERC result. No PCB exists,
so DRC and schematic/PCB parity are not checked. No order or upload is in scope.
