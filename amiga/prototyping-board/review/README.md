# Revision A design review

The project is electrically complete as a passive breakout: 100 physical
contacts, 83 nets, 130 breakout header/test-point pads, all 14 mandatory
duplicate signals. The source specification has not been edited.

See the follow-up [mechanical cross-check](../docs/mechanical-cross-check.md)
and `mechanics/` measurements for the current mechanical release holds. That
review leaves CAD and pin mapping unchanged; hashes are retained in
`mechanics/design-unchanged.sha256`.

## Verification run

From `repos/fujinet-nio-hardware/amiga/prototyping-board`:

```sh
export NIO_WORKSPACE=/home/markf/dev/nio/fujinet-nio-workspace
source "$NIO_WORKSPACE/scripts/env.sh"
python scripts/check.py
python scripts/export.py
```

KiCad version: **10.0.5**. The export command runs the checks again before
producing outputs. These commands cover the only modified repository,
`fujinet-nio-hardware`; no firmware/library/Amiga emulator tests apply.

| Check | Result |
|---|---|
| CSV / actual schematic netlist / PCB / verification CSV | PASS, 100 contacts |
| Required duplicate access | PASS, 14 signals |
| Passive symbol pins and isolated special contacts | PASS |
| Finger dimensions, face assignment, header grid, outline | PASS |
| Ground plane reserved; no vias/inner tracks in mating tongue | PASS |
| Deliberately corrupted CSV, schematic, PCB and table | All 5 rejected |
| ERC | 0 errors, 0 warnings |
| DRC, including warnings | 0 violations |
| Unconnected copper items | 0 |
| Schematic/PCB parity | 0 issues |

`erc.rpt`, `drc.rpt`, `drc.json` and `consistency.json` are machine-generated
evidence. No intentional ERC/DRC violation or project exclusion was required.
KiCad's default disabled checks are listed in its ERC report; the project
does not change those defaults.

The distribution's `pcbnew` Python module emits three `PROPERTY_ENUM` startup
assert messages, and can emit a SWIG object-destructor diagnostic during
regeneration. These are binding diagnostics, not ERC/DRC findings. The
generated CAD is independently loaded and checked by `kicad-cli`.

## Visual review and limits

`layout-front.svg` and `layout-back.svg` show actual plotted silk, mask
openings and the board edge. The reverse view is mirrored for viewing from
the back; manufacturing files are **not mirrored**. `schematic.pdf` contains
the entire named-net circuit; `copper/` contains separate copper layer views.
The SVGs are vector drawings and retain detail when zoomed or printed.

The layout groups all nine requested categories, labels reserved/NC points
explicitly, shows component-side orientation, supplies distributed grounds,
and places the required copyright and 3.3V compatibility warning on silk.
There is no module footprint or path from an auxiliary rail to one.

**Unresolved mechanical issue:** the available original A-5 bevel callout is
too faint for an authoritative angle/depth transcription. Fabrication is
held on that detail and on final insertion depth, contact-to-tip offset and
shoulder profile: the current square-shouldered, 7.62 mm projection is
provisional. Do not substitute guessed connector dimensions. The
129.26 mm tongue width, contact pitch/span and face orientation are sourced
in `docs/reference-review.md`. A500 adapter and real-slot fit, contact finish,
current/thermal capacity, signal integrity and bus loading have not been
tested on hardware. DRC/continuity does not establish those properties.

This is therefore a reviewable design package, not a fabrication release or
a claim that a powered prototype has passed Amiga hardware acceptance.
