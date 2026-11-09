# Integrated Amiga board candidate R0

Start with [the circuit proposal and requirements](proposal.md).
Open [the candidate project](integrated-r0.kicad_pro) in KiCad 10, or review
[the schematic PDF](review/schematic.pdf).

This is an implemented **USB/power/recovery subcircuit**, with temporary RP/ESP
integration boundaries. It is not a complete integrated board or fabrication
release. [Verification and remaining work](review/verification.md) distinguish
the passing checks from the unimplemented processor and Zorro circuitry.

[RP2350 package allocation](rp2350-pin-allocation.csv) accounts for all 81 pads
and all 48 GPIOs, including separate ACK and SLAVE requests. It is a revised
candidate allocation, not a transcription of the earlier Core2350B drawing.

To refresh independent netlist, ERC, connectivity checks and review exports:

```sh
source "$NIO_WORKSPACE/scripts/env.sh"
python "$NIO_WORKSPACE/repos/fujinet-nio-hardware/amiga/integrated-r0/check.py"
```

The check does not generate or edit CAD. There is no PCB to route yet.
