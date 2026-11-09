# Direct A500 integrated candidate R2

**Circuit review candidate. Not ready for active attachment or manufacture.**
R2 corrects the A500 bus handshake from R1. The motherboard generates
/DTACK; this board pulls XRDY low to insert a wait and releases it when ready.
Per-cycle latches prevent stale completion/read-drive requests carrying into
the next transfer. /BERR disables the bus outputs. No extra RP GPIO is used.

Open the [eight-page schematic PDF](review/schematic.pdf),
[handshake and timing review](bus-review.md), and [engineering decisions](engineering.md).
Native project: [integrated-a500-r2.kicad_pro](integrated-a500-r2.kicad_pro).
R1, R0, the manufactured passive breakout and custom libraries are preserved.

| Requirement | Implementation | Check | Open |
| --- | --- | --- | --- |
| Direct A500 connection | 86-contact female socket, no adapter | Native connector net mapping | Socket MPN, orientation and footprint |
| Correct A500 acknowledgement | Hardware XRDY wait; no DTACK driver | Commodore pp.91,94; saved netlist | Loaded timing and active qualification |
| Per-cycle isolation | Completion/read-claim latches; BERR interlock | 65,536 static cases + 65,536 sequences | PIO sequencing, watchdog, analog transitions |
| RP pin budget | Same 48 GPIO and 81 package pads | Native complete pin membership | Implement this map in firmware |
| USB and independent recovery | Two muxes; physical mode and BOOT/RESET | Eight path checks; accepted bench evidence | Cold-transition circuit qualification |
| Explicit power | USB-C >=1.5A; isolated host supply monitor | Existing budget and rail checks | Input protection, CC response, derating |
| PCB | Four-layer design planned | No PCB claim | Socket, BOM and electrical closure first |

## Verification and reproduction

After `source scripts/env.sh`, run:

```sh
repos/fujinet-nio-hardware/.local-tools/kicad/venv/bin/python \
  repos/fujinet-nio-hardware/amiga/integrated-a500-r2/build.py
python repos/fujinet-nio-hardware/amiga/integrated-a500-r2/check.py
```

Construction uses the MCP launcher; the public schematic API only finishes
page metadata and explicit no-connects. `check.py` independently exports through
native KiCad and checks whole-net membership, processor pins, bus logic and
USB paths. [Verification](review/verification.md) records the limitations.

There are **32 retained ERC findings** for external-host drivers/pull-ups;
this is not zero ERC. No PCB exists, so DRC, schematic parity and USB geometry
are not checked. No new physical experiment or fabrication order is requested.
