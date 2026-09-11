# Reference review — before layout

Reviewed 2026-09-10. The supplied PROTOTYPING-SPEC.txt remains unchanged.

Follow-up: [mechanical-cross-check.md](mechanical-cross-check.md) contains
actual CAD/Gerber measurements from all four requested projects, manufacturer
follow-through for the EATX socket, and the current release decision. It
supersedes the preliminary mechanical assessment below where more specific.

## Pin-map discrepancies and decisions

The printed **Amiga Hardware Reference Manual, Third Edition**, Appendix K,
pp. 437–439, was inspected as page images (PDF pages 451–453). OCR is not
reliable for the subscripts: in particular it reads A7 as A1.

* **28 = A7; 29 = A1.** The starting specification reverses these. Use the
  printed table, corroborated by the Appendix K HTML transcription.
* The table continues onto **p. 439** for pins 83–100; pp. 437–438 alone
  cannot verify all 100 contacts.
* **96 = Reserved**, legacy /EINT1, like reserved pins 40, 42 and 44. Expose
  each separately, with no pull-up, grounding, or shared reserved net.
* **48 = legacy /VPA**, physical /MTACK; **51 = legacy /VMA**, physical /DS0.
  Those 6800-interface functions are unsupported on A3000 Zorro-II cycles
  (Appendix K, Changes from the A2000 Bus). These are isolated legacy points,
  not ordinary supported Zorro-II handshake signals.
* **53 = /RST**, physical /RESET: retain the familiar /RESET breakout label.
* **92 = E7M**, physical 7M: label 7M, retain the logical alias in the CSV.
* **91 = SenseZ3**, grounded by a Zorro-II **backplane**, floating on a
  Zorro-III backplane (p. 412). Route independently to a labelled sense point;
  do not short it to the PCB ground plane. This preserves its physical
  function when used in A3000/A4000 systems.
* **97/98 = NC in Zorro-II**, physical /FCS and /DS1. Expose as separate NC
  points; they can carry Zorro-III signals in a Zorro-III system.
* Slot-index suffix N is omitted in user labels (/SLAVE, /CFGIN, /CFGOUT,
  /BR, /BG); there is only one slot on this board.

## Mechanics and orientation

Appendix K p. 391 directs Zorro-II designers to the **A500/A2000 Technical
Reference Manual**; pp. 427–430 themselves show Zorro-III mechanics. TRM
Figure A-5 was inspected
in the second scan below (PDF p. 280, left-hand drawing). The first scan
omits A-5 and A-6, so its A-7 86-pin drawing must not be substituted.

Verified: 50 positions per face, 2.54 mm pitch, 124.46 mm between extreme
contact centres, **129.26 ±0.1 mm tongue width**, and even-numbered contacts
on the **component side**, pin 100 at left and pin 2 at right when the
insertion edge is down. Pin 1 is opposite pin 2 on the reverse. No key notch
divides the Zorro tongue. The full-card envelope is 337.19 ×114.5 mm above
the connector shoulder; this project uses a shorter, lower board without an
ISA/video extension or case bracket. Case support is not supplied.

The implemented prototype mechanics use the clear local [A-5 scan](a5.png):
7.62 projection, R1.5 roots, 1.5 ×45° planar corner chamfers, 1.6-wide
fingers and a 0.5 ×45° bevel on each face. The 1.6 nominal finished board
implies a 0.6 nominal centre land (reference only). Finger length 5 and tip
setback 1 remain explicit prototype choices; all contact positions and
electrical routing are unchanged.

The intended socket is WingTAT ED100BGFBK / LCSC C5173320. The release
targets PCBWay with continuous mask openings and selective hard gold.
Full measurements, sources and evidence limits are in
[mechanical-cross-check.md](mechanical-cross-check.md); machining and
process tolerances are in [fabrication instructions](../fabrication/README.md).

**FABRICATION-READY — PROTOTYPE SPIN ONLY.** Actual seating, contact witness
marks, continuity/isolation and host behaviour remain physical validation
items. The missing manufacturer wipe envelope is not a prototype release
hold. No hardware has been tested and nothing has been ordered.

## Sources

* [AHRM third-edition scan](https://www.ikod.se/wp-content/uploads/2020/08/Amiga_Hardware_Reference_Manual_3rd_Edition.pdf)
  SHA256 `edcf9528eccb1f6143d9d8854ad7eb09756abe59f5722e4c6b964f4ff844d2ba`.
* [Appendix K transcription](https://www.theflatnet.de/pub/cbm/amiga/AmigaDevDocs/hard_k.html)
  — cross-check only; printed pages take precedence.
* [A500/A2000 TRM, including A-5 at PDF p. 280](https://erikarn.github.io/amiga/docs/Amiga_500_Technical_Reference.pdf)
  SHA256 `61b55a0d1cd01614fa40fca05b5e879458ac0735b178539749ed4d3c303ebd08`.
* [Other TRM scan, missing A-5](https://amiga.net.au/files/Tech_Amiga/Commodore_A500-A2000_Technical_Reference_Manual.pdf).
* [MNT VA2000 connector](https://github.com/mntmn/amiga2000-gfxcard/blob/a512aabb95d28c2b844760b6c8536440c317a4c6/kicad/zorro2.pretty/zorro2card.kicad_mod)
  and [PCB](https://github.com/mntmn/amiga2000-gfxcard/blob/a512aabb95d28c2b844760b6c8536440c317a4c6/kicad/amiga-gfxcard.kicad_pcb).
  Mechanical measurement cross-check only; no VA2000 circuit is incorporated.
