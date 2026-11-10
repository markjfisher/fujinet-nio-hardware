# R4 placement readiness — 2026-11-10

**Ready for constrained placement preparation.** All PCB positions, locks,
groups, nets and geometry remain byte-for-byte unchanged. No routing or
placement generator ran. Only Q5's schematic symbol was repaired.

| Requirement | Decision / evidence | Remaining action |
|---|---|---|
| Exact hold-up parts | Panasonic parts and recommended lands below | Apply the two footprint changes during incremental placement preparation |
| Preserve placement | 203 footprints, 63 individually locked; 42 groups, all unlocked | Classification is advisory; no unlocks performed |
| Group staged circuitry | 11 proposed clusters cover all 52 staged footprints | Regroup and place deliberately, respecting existing fixed areas |
| Resolve Q5 warning | Direct standard NPN B/E/C symbol with unchanged device and connectivity | Complete: ERC warning removed |

## Bulk capacitors selected

| Reference / rail | Exact Panasonic MPN | Ratings | Required KiCad footprint |
|---|---|---|---|
| C113 / 3V3_BUS | **6SVPC100M** | 100 µF ±20%, 6.3 V; ESR ≤30 mΩ at 100 kHz/20°C; B6, Ø5.0 × 5.9 mm | `Capacitor_SMD:CP_Elec_5x5.9` |
| C117 / main 3V3 | **6SVPC220M** | 220 µF ±20%, 6.3 V; ESR ≤27 mΩ at 100 kHz/20°C; C6, Ø6.3 × 5.9 mm | `Capacitor_SMD:CP_Elec_6.3x5.9` |

Both are polarized polymer parts. Pin 1 is positive; pin 2 is ground.
Allow 6.0 mm maximum seated height plus enclosure clearance. Initial minimum
capacitances are 80/176 µF, meeting Phase 1 assumptions. Manufacturer ripple
ratings are respectively 1.97/2.32 A at 100 kHz/105°C.

Native footprint read-back matches Panasonic's land recommendations exactly:
B6: two 3.0 × 1.6 mm pads at x=±2.2 mm (1.4 mm gap, 7.4 mm outside span);
C6: two 3.5 × 1.6 mm pads at x=±2.8 mm (2.1 mm gap, 9.1 mm outside span).
**Both current `CP_Elec_6.3x5.8` assignments must change**; it is oversized
for C113 and has the wrong pad gap/height identity for C117. These changes
are specified here, not yet applied to the PCB or schematic footprint fields.
The selected procurement BOM is [bulk-capacitors.csv](bulk-capacitors.csv).

Sources: Panasonic [100 µF](https://industrial.panasonic.com/ww/products/pt/os-con/models/6SVPC100M),
[220 µF](https://industrial.panasonic.com/ww/products/pt/os-con/models/6SVPC220M),
[SVPC datasheet, pp.1–2](https://industrial.panasonic.com/cdbs/www-data/pdf/AAB8000/AAB8000C256.pdf),
[recommended lands](https://industrial.panasonic.com/cdbs/www-data/pdf/AAB8000/AAB8000COL10.pdf).
Both selected rows are current, not marked NRFND in the reviewed table.
DigiKey lists active cut-tape ordering: [P16606CT-ND](https://www.digikey.co.uk/en/products/detail/panasonic-industry/6SVPC100M/4204938)
and [P16609CT-ND](https://www.digikey.co.uk/en/products/detail/panasonic-industry/6SVPC220M/4204941).
Stock was listed during this review; no order/reservation was made.

The ESR limits above are **not guaranteed full-temperature transient ESR**.
Keep the existing ≤50 mΩ/effective-capacitance prototype qualification in the
shutdown test plan. Endurance allows a further ±20% capacitance change from
initial: using 64% nominal and the same 50 mΩ/3 µs/load assumptions still gives
approximately 2.825 V main and 2.880 V bus, above 2.7 V. This sensitivity check
does not substitute for temperature, startup or regulator-stability testing.
Retain the AP2112 and buck's local ceramic capacitors; bulk capacitors supplement them.

## What stays fixed, and what may move later

| Class | Members / rule |
|---|---|
| Mechanically fixed | J40 A500 socket, board outline and right-edge x=87–105 mm component-free band; J1 USB and J30 SD access; H1–H4 mounting geometry. Holes are currently unlocked but must still be treated as fixed. |
| Electrically constrained | U20/RP regulator/reference cell, crystal, QSPI, U30/antenna keep-out and local supply; U5 switching loop and feedback; USB switches/protection/power path; U40–U47 bus-buffer corridor and local bypasses. Keep these existing anchors and relative geometry. Any future movement needs a specific electrical/layout justification. |
| Provisionally locked | J2/J20/J31/J60 and SW1–SW4: current service/recovery positions are retained, but may be reconsidered with enclosure/access requirements. Their present locks are not manufacturing datums. |
| Movable within constraints | Staged logic/arrays and ordinary passive support may be placed with their owning functional cluster. Unlocked does not mean unconstrained: bypasses stay at supply pins, pull-ups/biases with their nets, crystal/switching loops remain compact. |

[footprint-constraints.csv](footprint-constraints.csv) classifies every footprint,
including its current lock and coordinates. [group-constraints.json](group-constraints.json)
classifies all 42 groups and records exact membership. A group's classification
does not override a mechanically fixed member. No group is currently locked.

The old U60/U61/U62/U64/U66/U71 groups and SD-pullup group have incomplete or
obsolete memberships after consolidation. U7 and U5 groups also need their new
bypasses added. Rebuild those memberships in the next placement stage; do not
move a misleadingly named legacy group as though it still contains its IC.

## Proposed placement regions

These are planning envelopes in existing board millimetres, **not collision-cleared
coordinates**. They may overlap existing support parts that will need deliberate
local adjustment. Keep the continuous ground plane and antenna keep-out intact.

| Functional cluster | Suggested region / priority |
|---|---|
| U95/D4/U96 host limiter and LDO | Upper-right interior, x59–73/y14–25; near host 5 V entry. Local input/output ceramics and ILIM resistor. |
| U60/U90/U91/U92 supervisor/Schmitt cluster | x55–73/y27–40; compact shared reset, CT and divider grounds; total GUARD_OK_RAW capacitance ≤50 pF. Route sense lines from protected load rails. |
| U93/U94 output override plus C113 | x66–74/y66–96, beside host-output buffer corridor; C113 close to U44/U45 power distribution, U94 near XRDY/IRQ paths. Direct BUS_DISABLE routes. |
| C117 main hold-up | x39–48/y88–100, on regulator output distribution; keep away from L1 switch node and feedback loop. |
| Q5/U97 reset and control conditioning | x35–43/y60–72 near RP_RUN/recovery circuitry. |
| U98/U99/R64 request conditioning | x30–45/y46–60 near request flip-flops and source pins. |
| U100 host-input conditioning | x68–74/y48–57 immediately upstream of U43. |
| U61/U66/U71/U64 consolidated logic | Vacated upper rows x20–54/y14–40; arrange by signal flow, with C70/C75/C80/C73 beside their new packages. |
| R37 SD array | x12–21/y50–65 near SD routing and R41. |
| C123 / C124 | At U7 VCC / U5 AVIN respectively; these are local bypass additions, not part of a distant guard cluster. |

Full member lists and placement rules are in [proposed-clusters.json](proposed-clusters.json).
Reserve the host rail/guard/driver power-return paths before placing ordinary
logic. Keep USB pair geometry and uninterrupted return paths as explicit routing
constraints; neither a group nor an autorouter proves these.

## Q5 repair and checks

Q5 remains **MMBT3904-7-F, SOT-23**, with pin1=base, pin2=emitter,
pin3=collector. Its inherited `Transistor_BJT:MMBT3904` library alias was replaced
by direct `Transistor_BJT:Q_NPN_BEC`, whose pin geometry/electrical types match.
The exact purchasing value is retained; the datasheet field now refers to Diodes.
The MCP's in-place lib_id setter is unsupported, so the narrow change used the
KiCad schematic object serializer, followed by native KiCad read-back and
format normalization (which produces a larger textual diff than the electrical change). Hidden
footprint properties were preserved after visual inspection caught a serializer
visibility difference. No ERC exclusions were added.

Native full-net comparison: unchanged. All schematic component positions and
UUIDs: unchanged. PCB SHA-256 and bytes: unchanged, preserving every group/lock.
Count remains 199 fitted components / 203 footprints. ERC is **31 existing
findings**, with Q5's mismatch gone. Native DRC/parity: **6 existing violations,
499 unconnected items, zero parity errors**. This remains an unrouted candidate.
Updated schematic PDF was rendered and inspected. Evidence is beside this report.
