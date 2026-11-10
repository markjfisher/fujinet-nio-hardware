# Phase 1 implementation completed — 2026-11-10

Protection and I1/I2/R-A/R-B are implemented in native KiCad and committed
separately. USB remains mandatory for main power. No TPS2121 was installed.
See [implemented power protection](bus-output-disable-proposal.md) for exact
supervisor connections, limits and prototype tests.

| Stage | Exact modification | Fitted count |
|---|---|---:|
| Checkpoint | Original R4 | 188 |
| Protection | Three MIC2790H monitors, limited host-interface rail, output overrides, hold-up and required conditioning; includes U7/U5 bypasses | 227 |
| I1 | U61/U62/U63 → U61; U66/U67/U68 → U66; U71/U76/U80 → U71, all SN74LVC11APWR. Keep C70/C75/C80; remove six redundant package bypasses | 215 |
| I2 | U64/U65/U69/U70/U74/U75 → U64 SN74LVC04APWR. Keep C73; remove five redundant package bypasses. U7 stays separate on AON | 205 |
| R-A | R37–R40 → R37 CAT16-4702F4LF, four isolated 47 kΩ 1% elements | 202 |
| R-B | R64–R67 → R64 CAT16-1002F4LF, four isolated 10 kΩ 1% elements | **199** |

Final inventory: **45 ICs, 54 resistor packages, 78 capacitors, 22 other fitted
parts**. PCB has **203 footprints**, including four mounting holes.
Consolidations remove 28 packages from the protected intermediate design.
Protection adds 39 versus the original baseline, so the net change is +11.
The earlier 162 target is superseded by the approved electrical corrections.

## Package maps and equivalence

SN74LVC11A: VCC14/GND7; gates (1,2,13)→12, (3,4,5)→6,
(9,10,11)→8, preserving each original gate's inputs in pin1/3/6 order.
SN74LVC04A: VCC14/GND7; old U64/65/69/70/74/75 map respectively to
1→2, 3→4, 5→6, 9→8, 11→10, 13→12. All gates are used.
Both packages remain on main 3V3; output-enable safety does not depend on
undefined powered-down outputs. The separate hardware guard overrides them.

Both CAT16 F4 arrays use isolated pairs **1–8, 2–7, 3–6, 4–5**.
R37 maps SD_DAT2/SD_CS/SD_MOSI/SD_MISO to their individual main-3V3 pull-ups;
R41 is retained. R64 maps BUS_READY/DATA_DRIVE/ACK_REQ/IRQ_REQ to their
individual ground biases. There is no internal common terminal. The CAT
concave array footprint is used. Worst static element dissipation at 3.3 V
is 1.1 mW (10 kΩ), comfortably below the documented element rating.

## Verification results

- Each stage: native KiCad XML export compared **every functional pin**, exact
  part value/footprint and cross-sheet net identity with the intended circuit.
  Replacement gate associations and every resistor-array element pass.
- Each stage: all **64 guard validity/request/byte-enable combinations** pass.
  This is logical verification, not an analogue power-ramp simulation.
- Native ERC: **32 findings**: 30 retained undriven-input findings, the retained
  U9 open-collector-to-ground/power-output modelling error, and a new Q5
  library-copy mismatch warning. Q5 pin1/base, pin2/emitter and pin3/collector
  were checked explicitly. No ERC exclusions were added; ERC is not clean.
- Each stage: native PCB DRC reports **6 retained violations, 499 unconnected
  items and zero schematic-parity errors**. The PCB remains unrouted; those
  counts are tool findings, not a claim that every unrouted edge was counted.
- Normal XRDY path: **44.7 ns worst-case allocated address path** and 42.5 ns
  AS path versus 60 ns; includes the new request gate/output driver and 10 ns
  board allowance. Selected LVC11A/04A delays are 4.1/6 ns at the specified
  3.0–3.6 V conditions. Existing firmware setup constraints remain required.
- Bounded shutdown calculation: main ≥2.829 V, bus ≥2.883 V at disable,
  above 2.7 V. See the protection document for load, ESR, overdrive, response
  and capacitance assumptions; these need prototype confirmation.
- Native final preservation comparison: outline unchanged; every surviving
  footprint retains position/rotation/side/lock/UUID except the seven explicitly
  repackaged references. Existing connector, bus-buffer and critical processor/
  power placements are preserved. Zero tracks were added.
- Schematic PDF, guard/control renders and the PCB/staging render were visually
  inspected. Matching net labels connect the schematic blocks electrically.
  The schematic is readable at zoom but still needs editorial grouping work;
  no polished placement or completed routing is claimed.

Evidence is in [../../phase1](../../phase1/), including per-stage XML, ERC,
DRC, pin-map/truth checks and PCB-preservation records. The current schematic
is [../schematic.pdf](../schematic.pdf). The [board/staging preview](../../phase1/board-and-staging.png)
shows why components are outside the outline: they await deliberate placement.
Older review inventories and placement pictures describe the baseline.

## Remaining work before layout/fabrication approval

Place the new supervisor/hold-up/output-disable cluster locally to its loads,
keep GUARD_OK_RAW short (≤50 pF total), and place each surviving bypass beside
its new package. Keep regulator feedback/switching loops and RP/ESP support
clusters constrained. Select exact bulk capacitor procurement parts meeting
minimum effective capacitance and maximum ESR over temperature; footprints
remain provisional. Then perform the scoped shutdown, inrush, thermal and
bus-timing prototype checks in the protection document. No routing or global
placement optimisation was performed in this phase.

## Source and commit record

- Checkpoint: `13bd46e0`; migration/verification tooling: `89c8a638`.
- Protection: `c2313a37`.
- I1: `03fe1e5b`.
- I2: `c2c86764`; R-A: `6d3c12ee`; R-B: `4e6379e5`.

Manufacturer basis: [TI SN74LVC11A](https://www.ti.com/lit/ds/symlink/sn74lvc11a.pdf),
[TI SN74LVC04A](https://www.ti.com/lit/ds/symlink/sn74lvc04a.pdf), and
[Bourns CAT/CAY](https://www.bourns.com/pdfs/CATCAY.pdf), plus the supervisor,
Schmitt and buffer datasheets linked in the protection document.
