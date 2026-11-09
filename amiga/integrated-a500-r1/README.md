# Direct A500 integrated candidate R1

**Circuit review candidate, not ready for manufacture or attachment to an Amiga.**
This advances R0 from a USB/power fragment to a complete set of processor,
storage and bus-interface circuits. Electrical release and PCB layout remain
unfinished. The manufactured passive breakout and R0 baseline are preserved.

Open [the eight-page schematic PDF](review/schematic.pdf), then
[the engineering decisions and remaining checks](engineering.md).
The KiCad project is [integrated-a500-r1.kicad_pro](integrated-a500-r1.kicad_pro).
The overview page joins seven functional sheets through named hierarchical
connections; PDF page order is assigned by KiCad and can change on rebuild.

| Requirement | R1 implementation | Evidence/check | Still open |
| --- | --- | --- | --- |
| Direct A500 connection | 86-contact female socket; existing logical pin map | All connector-to-buffer nets checked | Actual socket MPN, mating orientation and mechanical footprint |
| Optional A2000 product | Separate future 100-contact card variant | Host differences documented | A2000-specific CFGOUT/SLAVE and mechanics; not implemented here |
| Shared USB / recovery | R0 two-mux circuit; physical mode, independent BOOT/RESET | Four switch states, both polarities; accepted bench recovery | Switching-circuit prototype qualification; cold changes only |
| Processors and storage | RP2350B + 16MB flash + crystal/core supply; ESP SMD N16R8 module + microSD | Native saved pin/net check; manufacturer references | Package/BOM and layout review |
| Complete RP allocation | 81 pads; 48 GPIO; native USB/SWD; no interprocessor SPI | GP2–GP7 remain A2–A7 | Firmware must adopt this exact map |
| Safe bus enables | Eight LVC541 buffers, discrete interlocks, host monitor, open-drain ACK/IRQ | Exhaustive static logic checks against native netlist | Timing/analog margins and startup/shutdown transients |
| Explicit power | USB-C sink, >=1.5A advertisement, 1.2A 3.3V allocation | Rail separation, regulator circuits, budget | Protection, derating and CC downgrade sign-off; legacy USB-A unsupported |

The small capacitors are local supply reservoirs and noise filters; the
resistors set voltage levels, default states and signal termination. Matching
net labels are electrical connections even without a long drawn wire. Supply
banks and selected local circuits now have explicit connecting wires. Physical
PCB placement must put each decoupling capacitor beside its device's supply
pin; schematic proximity alone does not establish that.

## Verification

From the workspace, with KiCad 10 available:

```sh
source scripts/env.sh
python repos/fujinet-nio-hardware/amiga/integrated-a500-r1/check.py
```

`check.py` exports the saved design through native KiCad, checks **whole-net
membership** (including hierarchy and unintended shorts), every RP package
pad, all USB modes and the bus interlocks. It retains the actual ERC report.
There are **30 `pin_not_driven` ERC findings**, all at the external A500
connector: its existing symbol models address/control lines as inputs, and
host-side drivers/pull-ups are outside this schematic. These are reviewed
model limitations, not a zero-ERC result. No findings are suppressed.
See [checks.json](review/checks.json) and [verification.md](review/verification.md).

No PCB exists yet, so PCB DRC, schematic/PCB parity, USB impedance, antenna
clearance and mechanical fit are **not checked**. No fabrication package or
order has been produced.

## Editing and reproduction

`circuit.json` records the intended components, pin membership and schematic
layout. `build.py` constructs this candidate using the selected MCP through
its repository launcher. It overwrites **only this candidate**, never R0 or the
passive breakout. Run it with the pinned tool venv Python, then run `check.py`.
Read the tool compatibility notes before rebuilding; no concurrent writer or
unsaved KiCad editor may target these files.

The next release gate is to close the power and host-interface electrical
review, select/check the female socket, finish the schematic presentation and
BOM, then create a constrained four-layer PCB candidate. The existing traces
and USB demonstrations do not need to be repeated to reach that gate.
