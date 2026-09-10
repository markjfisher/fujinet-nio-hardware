# Passive Amiga Zorro-II breakout — revision A

Open [kicad/zorro-breakout.kicad_pro](kicad/zorro-breakout.kicad_pro) in KiCad 10.
The schematic and PCB use project-local symbol and footprint libraries; no
downloaded library is required. All 100 physical edge contacts are exposed.
There are **no active components, buffers, level shifters, termination,
regulators, memory or AutoConfig logic**, and no development-module footprint.

This is a **review design, not a hardware-tested or released product**.
Read [reference-review.md](docs/reference-review.md) for the pin-map corrections
and mechanical findings, and [fabrication notes](fabrication/README.md) before
using the fabrication outputs. Nothing has been ordered or manufactured.

The follow-up [mechanical cross-check](docs/mechanical-cross-check.md) measures
VA2000, RIPPLE-IDE, AmigaSID and the EATX socket against this board and
Commodore drawings. It retains the fabrication hold: insertion/contact
envelope, bevel depth/land and mask registration allowance remain unresolved.

## Files

* `kicad/`: editable schematic, four-layer PCB, project and local libraries.
* `data/pin-map.csv`: independently transcribed/reviewed Appendix K pin map.
* `data/verification.csv`: each physical contact → net → footprint pad →
  every matching header/test-point pad, including shared grounds and +5V.
* `data/bom.csv`: passive assembly parts. Headers may be omitted for direct
  probe access or replaced with compatible 2.54 mm sockets.
* `review/`: schematic PDF, PCB views, ERC/DRC reports and consistency result.
* `fabrication/`: copper, mask, silk and outline Gerbers; Excellon drill file,
  drill map and fabrication instructions.
* `scripts/`: reproducible generation, routing import, verification and export.
* `routing/`: Specctra input/session retained to reproduce routed copper.

## Finding signals

View the **component side**, insertion edge down: pin 100 is at the left end,
pin 2 at the right. **Pin 1 is on the reverse, directly opposite pin 2.**
The board does not have a key that prevents reversed insertion. Verify your
A500-to-Zorro-II adapter's orientation before insertion. An A500's native
86-pin expansion connector is not this 100-pin connector.

| Header | Group | Rows, top to bottom |
|---|---|---|
| J2 | ADDRESS | A1–A23, GND |
| J3 | DATA | D0–D15, GND |
| J4 | BUS CONTROL | /AS, /UDS, /LDS, READ, /DTACK, /OVR, XRDY, /RESET, /HLT, /BERR, FC0, FC1, FC2, DOE, /BUSRST, GND |
| J5 | AUTOCONFIG / SLOT CONTROL | /SLAVE, /CFGIN, /CFGOUT, GND |
| J6 | INTERRUPTS | /INT2, /INT6, GND |
| J7 | DMA / ARBITRATION | /OWN, /BR, /BGACK, /BG, /GBG, GND |
| J8 | CLOCKS | /C3, CDAC, /C1, E, 7M, GND |
| J9 | POWER | +5V, +5V, GND, GND, GND, GND |
| J10 | RESERVED / LEGACY | Reserved 40, 42, 44, 96; legacy /VPA 48, /VMA 51; NC 97, 98; SenseZ3 91; GND |
| TP1 / TP2 / TP3 | Auxiliary POWER | -5V / +12V / -12V, respectively |

**On two-column headers, both pins in each horizontal pair carry the SAME
signal. They are not signal-and-ground pairs.** J4/J5/J6/J8 provide duplicate
access for a development connection and a logic analyser. The rectangular
pad is header pin 1; pairs are numbered 1/2, 3/4, etc. The numbers next to
signal names on the board are **Zorro contact numbers**, not header indices.
J9 similarly provides four +5V pins and eight ground pins.

Important corrections to the starting map: **28=A7, 29=A1**; 96 is Reserved
with a legacy /EINT1 alias. Pin 91 is **not** connected to the PCB ground
plane: only a Zorro-II backplane grounds it. See the reference review for all
aliases and the reason to distinguish physical names from Zorro-II names.

## Connecting and probing

**DO NOT CONNECT DIRECTLY TO 3.3V LOGIC WITHOUT CHECKING ELECTRICAL
COMPATIBILITY.** This applies to the Core2350B/RP2350B board, an ESP32-S3 and
the logic analyser itself. This breakout makes no electrical conversion or
protection. Provide the required external interface before attaching logic.

Power the Amiga off before inserting/removing the card or moving jumpers.
Check board orientation, shorts between supply rails and ground, and
continuity through the adapter before powering up. Do not feed a USB module's
5V supply back into the Amiga's +5V rail. The auxiliary rails are test-only;
their presence and current budget depend on the host/adapter.

Keep probe and jumper leads short and use a nearby labelled GND. Prefer
high-impedance, low-capacitance inputs; each attached probe/board adds bus
loading. The internal GND plane helps return paths but does not certify bus
timing or signal integrity. The routed stubs and external wiring must be
evaluated on the intended machine. This is not a ribbon-cable extension bus.
No rail output current rating has been established by a thermal test.

The card does not respond to AutoConfig, drive /SLAVE, request DMA, assert
an interrupt, or drive any clock/control signal by itself. **/CFGIN and
/CFGOUT are separate nets.** Inserting this passive board can interrupt
configuration of cards farther down the chain. For passive-only use with
downstream cards, an external jumper from J5.3 (/CFGIN) to J5.5 (/CFGOUT)
passes the chain through. Fit it only with power off and no external circuit
driving either line; remove it before testing external AutoConfig logic.
No jumper is fitted or implied by the design.

Reserved and NC contacts are brought out for completeness, not permission to
drive them. NC 97/98 can carry signals in Zorro-III operation. /VPA and /VMA
are legacy functions unavailable in A3000 Zorro-II cycles. SenseZ3 may float
on a Zorro-III backplane; this board deliberately adds no pull-up.

The board is 180 mm wide, 100 mm above the connector shoulder, with a
129.26 mm tongue provisionally projecting 7.62 mm. Insertion depth,
contact-to-tip offset, shoulder profile and bevel still require authoritative
confirmation; **the current outline is not approved for manufacture**.
It omits an enclosure bracket and
full-length card guide tabs; support the board and attached leads during
bench use. Case/adapter fit and physical insertion have not been tested.

## Reproducing checks

From this directory in the workspace:

```sh
export NIO_WORKSPACE=/home/markf/dev/nio/fujinet-nio-workspace
source "$NIO_WORKSPACE/scripts/env.sh"
python scripts/check.py
```

The check exports fresh schematic connectivity, runs the independent mapping
and geometry assertions (including five negative cases), then KiCad ERC and
DRC with schematic parity. It does not regenerate or reroute the board.
Reports include warnings and fail on any unresolved violation; no DRC/ERC
exclusions are added by this project.

To reproduce the CAD **overwriting generated design files**, run
`python scripts/generate.py`, followed by `python scripts/import-routing.py`
and the check above. Reuse the stored routing session only while connector
placement, nets and mechanics are unchanged. `generate.py` explicitly resets
the PCB to its placement/fan-out state; it must not be used to update text on
a manually edited board without preserving those edits first.

Routing uses local Freerouting 2.4.1 via DSN/SES. It is not needed for opening,
checking or exporting the finished project. See `routing/README.md` for the
exact command. `python scripts/export.py` rebuilds review/fabrication outputs
after the checks pass. No export script contacts a board manufacturer.
