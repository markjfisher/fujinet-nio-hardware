# R3 engineering scope

R3 adds the protected input supply to the preserved R2 A500 circuit. It does
not change the 48-GPIO allocation or the XRDY/per-cycle-latch bus handshake.

- [Power review](power-review.md): new devices, limits, budget and remaining checks.
- [Connector selection](mechanical-selection.md): manufacturer dimensions and the unresolved mating orientation.
- [Bus review](bus-review.md): unchanged R2 handshake and firmware obligations.
- [R2 engineering](../integrated-a500-r2/engineering.md): processor, storage, USB modes and accepted evidence. Its SS34 power path is superseded here.

Correction to the R2 prose: the RP BOOT series resistor is **R13**, not R23.
The saved circuit always had R13 in that path; R23 is the RP USB D− resistor.
That was a documentation substitution error, not a schematic connection change.

The product remains a direct A500 sidecar with a female 86-contact socket;
A2000 is a separate future board. Cold USB mode changes and independent
physical BOOT/RESET remain mandatory. Legacy/default-current USB power remains
unsupported. The Amiga supply is sensed only, never used to power this board.

No PCB or fabrication release is claimed. The open gates are specific:
connector contact mapping/case envelope, overvoltage transient coordination,
current-downgrade timing, final capacitor/inductor BOM and PCB thermal/layout
checks. Existing bench USB and passive-capture evidence remains accepted.
