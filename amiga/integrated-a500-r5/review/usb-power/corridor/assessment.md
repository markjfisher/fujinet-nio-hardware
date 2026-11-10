# Focused USB routing-corridor assessment

**Placement-feasibility pass: no component movement is necessary.** The reviewed
candidate PCB is byte-identical to `99bb7cf1`; U5/L1/C8/C117 and the entire RP
cell, including proposed ground-via locations, are preserved. No routing or
mux placement was performed. [Annotated corridor view](assessment.png).

| Check | Finding / constraint for routing |
| --- | --- |
| Actual RP flash path | J1 A6/B6 → D2 1/6 → U1.3; U1.4 → R22.2 → R22.1 → U20.67 (D+). J1 A7/B7 → D2 3/4 → U1.7; U1.6 → R23.2 → R23.1 → U20.66 (D−). The arrows across U1 and each resistor represent device paths, not same-net copper. |
| Other USB branches | PC_DP/DM also terminate at U2.3/7. U1/U2 pins 2/8 share LINK_DP/DM for Run. Keep both muxes together, with short PC branches; this is not a single inline switch. |
| Connector escape | J1's data pads alternate DM/DP/DM/DP along y=81.25–82.75 mm. Duplicate-pin joining requires a local layer crossover. The copper-edge gap from J1 to D2 is 0.9325 mm; there is room for conventional small escape vias, subject to final pad/via DRC. Preserve D2's short ground return. |
| D2 onward | A clear 1.0 mm-wide planning neck at x=6.2–7.2 runs north to y≈76, then east above C3/U3. It avoids their actual courtyards and proposed ground vias. This is a corridor allowance, not an impedance-derived pair width. |
| Future mux bay | Keep x=18–34, y=70–79 mm available for U1/U2, C1/C2 and local fan-out. Each actual DGS footprint courtyard is 6.29 × 3.59 mm; two packages and their bypasses fit within this 16 × 9 mm allowance with escape space. Exact placement is deferred. |
| RP approach | A 2 mm-wide corridor at x=23–25 runs north beside the RP/flash cell, then across y=36.5–38.5 and south through x=40.4–43.4 toward R22/R23's north-facing pads at y=47.575. This avoids flash, crystal, RP regulator and their ground-via reservations. The already-reviewed resistor-to-RP escape remains subject to routing validation. |
| Buck separation | The checked envelopes, including the mux bay, stay **at least 13.325 mm** from the bounding envelope of the actual BUCK_SW pads. There is no reason to pass through U5/L1/C8/C117 or their input/output current loops. This measures existing pad geometry, not future copper/EMI performance. |

**Layer and power-path requirements:** use F.Cu over uninterrupted L2 ground for
the long USB corridor. Keep the U8→U9→U4→U5 load-current path south of it and
main 3V3 distribution outside the reserved USB band. At J1, VBUS joining may
use the other signal layer on the connector side of D2 rather than crossing
the USB escape on F.Cu. CC/control crossings and D2.5's VBUS_PROTECTED reference
feed should also use local vias/another signal layer as needed; D2.5 is not a
through-path for board load current. Preserve the ground reference at any USB
layer transition. These are routing constraints, not claims that copper has
already been verified.

The actual TS3USB30EDGSR VSSOP pinout puts D+ and D− on opposite package sides;
the mux bay therefore includes room for fan-out around the body and potentially
local signal vias. TI recommends short, matched pairs, minimal vias, continuous
reference planes and separation from switching circuitry; the corridor follows
that guidance. Final impedance, skew, branch lengths, layer transitions and
routed length still need checking against the selected stackup and
[TI's layout guidance, §8.4](https://www.ti.com/lit/ds/symlink/ts3usb30e.pdf).
D2's data-through pin pairs and supply/ground pins were also checked against
[ST's USBLC6-2SC6 pinout](https://www.st.com/resource/en/datasheet/usblc6-2.pdf).

[check.py](check.py) performs read-only native pad-net assertions, footprint
courtyard intersection checks and proposed-via checks, then annotates the
existing KiCad plot. [checks.json](checks.json) records the geometry and PCB
hash. It neither places components nor creates tracks. Unchanged CAD means
the existing ERC/DRC results remain applicable; they were not rerun.

**Conclusion:** the power placement does not obstruct a practical USB path.
Reserve the illustrated space when placing the muxes and later clusters.
Approval remains with the user; no candidate transfer has occurred.
