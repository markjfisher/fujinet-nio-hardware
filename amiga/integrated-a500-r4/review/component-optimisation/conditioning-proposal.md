# Phase 1 input-conditioning review — proposal only

2026-11-10. Baseline: `3464c256`, with the previous stop report at `a4e8f988`.
No CAD, placement, routing, project settings or firmware changes.

**Recommendation:** use explicit non-inverting Schmitt buffers at slow-signal
boundaries; retain the reviewed fast AND/inverter consolidation. Replace the
AON inverter with a Schmitt inverter. Do not attempt to fix the supervisor
outputs with much stronger pull-ups. The concrete edge-conditioning candidate
below would make the Phase 1 subtotal **172 fitted components**, not 162.

**This is not yet an implementation-ready electrical sign-off.** The audit also
finds that the present buck PG signal does not guarantee safe shutdown or
brownout. The proposed Schmitt changes resolve the identified input-edge
architecture issue, but cannot make that power-state guarantee. Section 6
identifies the missing guard requirements; its parts must be qualified before
approving the complete corrective schematic. No new physical experiment is
needed to establish these datasheet findings.

## 1. Evidence, scope and requirements

Fresh KiCad XML export: 188 fitted components. All physical component pin/net
assignments in `circuit.json` match the saved schematic; four virtual power
flags are omitted by the native exporter. The obsolete `gates` shorthand was
not used. Read-only MCP guidance and symbol search succeeded. Supporting
`conditioning-resistors.csv` records every resistor and its disposition;
`conditioning-calculations.json` contains the bounded RC calculations.

| Requirement | Proposed treatment | Validation state |
|---|---|---|
| Slow inputs must not enter ordinary CMOS directly | Explicit Schmitt boundaries, including firmware high-Z handoff | Pin maps below; not implemented |
| Preserve active-low resets and fail-low arm/requests | Non-inverting buffers; keep input-side biases and open-drain controls | Boolean polarity checked |
| Keep AON separate from main | U7 remains AON; added local buffers use main 3V3 | No new cross-rail pull-ups |
| Preserve fast XRDY path | No new stage on address or /AS paths | Existing conditional allocations retained |
| Safe brownout and partial power | Independent power-valid shutdown qualification required | **Not closed by PG/Schmitt alone** |
| Preserve board | No CAD writes; byte hashes and Git diff checked | Unchanged |

## 2. What the datasheets actually require

Do not equate the 50 pF switching-test load with an input-capacitance maximum.
Do not interpolate a typical threshold plot into a guaranteed limit.

| Exact device | Relevant requirement / limitation |
|---|---|
| TI SN74LVC11A | Recommended-condition Δt/Δv max 10 ns/V; no supply qualifier on that row. At 3.0–3.6 V, VIH=2.0 V and VIL=0.8 V. Standard CMOS, −40…125°C. CI=4.9 pF is typical, not max. [S1] |
| TI SN74LVC1G11, SN74LVC1G04, SN74LVC1G08, SN74LVC1G74 | Relevant 3.3 V ±0.3 V transition limit is 10 ns/V. DFF clock inputs are not exempt; the phrase about level-triggering does not override recommended conditions. [S2] |
| TI SN74LVC541A, Rev O; SN74LVC04A, Rev T | The reviewed recommended-condition tables do **not** publish a numeric input-slew limit. The 541 text nevertheless warns about slow standard-CMOS inputs. Do not report a part-specific 10 ns/V guarantee that is absent from these tables. Use 10 ns/V as a conservative project screening rule only. [S3] |
| TI TS3USB30E | No numeric control-input slew limit or Schmitt guarantee in the reviewed table; control VIH≥1.3 V, VIL≤0.5 V at 3–3.6 V. Treat resistor-release control edges explicitly. [S4] |
| Nexperia 74LVC1G74, 74LVC1G08, 74LVC541A | Advertise Schmitt action, **but still specify 10 ns/V** at the relevant supply. Rejected as a slow-edge cure by manufacturer substitution alone. [S5] |
| Nexperia 74LVC3G17 | Explicit Schmitt transfer characteristics, no input-transition restriction in recommended conditions, 1.65–5.5 V supply, 5.5 V-tolerant inputs and Ioff. Recommended candidate. [S6] |
| TI SN74LVC1G14 | Explicit Schmitt inverter, no recommended input-slew restriction, Ioff; recommended U7 replacement. [S7] |

The original stop report's 0.8–2.0 V calculation is a useful diagnostic, not a
manufacturer-defined rise-time measurement procedure. The Δt/Δv rows do not
define those endpoints. Here both 10–90% time and threshold-region traversal
are calculated, with local slope also considered. Slow RC cases fail by a
large margin under either screening interpretation. Switching-test input edges
of approximately 2.5 ns are test conditions, not permission to quote the same
delay measured from an arbitrary point on a slow RC ramp. [S1,S8]

## 3. Full slow/released-signal audit

| Signal(s) | Actual source / receiver | Finding and proposed disposition |
|---|---|---|
| HOST_PG | U60.1 open drain, R62 10k → U61.1 | Schmitt before LA.A; keep 10k. U60 explicitly recommends 10k–1M pull-up. |
| 3V3_PG | U5.4 open drain, R9 10k → U61.3 | Schmitt before LA.A; separate PG truth-table defect in §6. |
| RP_RUN | R10 10k, Q2 drain, SW1, J20.5 → U20.35/U62.1 | Split raw wired-reset node from driven RP_RUN; buffer both RP and safety-logic destinations. Keep debug/reset sinks on raw side. |
| CC_LOW_CURRENT | U3.7 OUT1 open drain, R6 10k → U7.2 | Replace U7 with SN74LVC1G14DBVR on AON; unchanged inversion. OUT1 high-Z at unattached/default current means POWER_ALLOW low after valid AON operation. [S9] |
| RUN_MODE, BUS_ARM | J2/J60 removable links; R3/R63 10k down → U62 | Condition release as well as assertion. Schmitt is not debounce: change mode/arm with bus inactive and processors held/reset; hot insertion remains unqualified. |
| BUS_READY | RP output / high-Z on reset, R64 10k down → U63.6 | Buffer; retained fail-low raw bias. |
| DATA_DRIVE, ACK_REQ | RP outputs / high-Z on reset, R65/R66 10k down → U86/U84 clocks | Buffer both clock inputs; retain distinct clocks and clears. Slow falling edges still matter even though only rising edges capture data. |
| IRQ_REQ | RP output / high-Z, R67 10k down → U82.2 | Buffer; keep U82 equation and U83 open-drain output. |
| FLASH_RP, FLASH_ESP | J2 and R1/R2 10k down → U1/U2 controls and Q gates | Condition controls to USB switches. Keep MOS gates on raw nodes to avoid placing their gate capacitance on the clean logic output. Same static mode table; no hot-switching claim. |
| AMIGA_RESET_N, AMIGA_BERR_N, AMIGA_DTACK_N | External host control nets → U43.6/.8/.7 | Treat as potentially resistor-released; no known host pull-up/load maximum supplied. Add non-inverting Schmitt stages **before** these U43 inputs. DTACK remains receive-only, including its presently unused receiver output. No board pull-up to 3V3. |
| TX_LO_N, TX_HI_N, RX_LO_N, RX_HI_N | Push-pull U72/U73/U77/U78 plus R50–53 10k → buffer OEs | Driven fast when main domain valid. Pull-ups do not prove safe OE during undefined supply ramps; address in power guard, not with extra Schmitt buffers on every OE. |
| ESP_EN | R11 10k/C10 1µF, Q1, SW3, J31.4 → module EN | Deliberate RC reset. Espressif recommends this topology; retain. It is not an LVC logic input and must not be subjected to the LVC 10 ns/V rule. Validate ≥50µs reset-low and rail-stabilisation timing. [S10] |
| ESP_BOOT_N | R12 10k, Q4, SW4/J31.5 → GPIO0 | Static boot strap, keep; must settle before EN release. No numerical GPIO slew guarantee established here. Avoid boot-button changes during strap sampling. |
| RP_BOOT_N / RP_BOOT_PULL | R20 10k, R13 1k, Q3/SW2 → flash /CS and RP QSPI_SS | Bidirectional-use boot/active-QSPI node: **do not insert a one-way buffer**. Keep passive boot circuit; release with clocks quiescent and allow settling before flash traffic. Flash /CS must track VCC during power-up; detailed boot/power-up timing remains a validation item. [S11] |
| SD_DAT2, SD_CS, SD_MOSI, SD_MISO, SD_DAT1 | R37–41 47k plus card/ESP drivers | Pulls define idle/startup; active SPI edges are push-pull. Arrays preserve these separate nets. ESP/card reset, removal and idle states are not high-speed edge sources. Retain pulls and power-up/command sequencing; do not claim LVC slew compliance for card internals. |
| ESP_STRAP45/46, ESP_VBUS_VALID | R32/33 down; R34/35 divider from main 3V3 | Straps/static supply indication, not ordinary external LVC inputs. ESP_VBUS_VALID is **main-rail-derived**, not raw USB VBUS sensing. Keep and document this meaning. |
| EFUSE_FAULT_N | U8 open drain, R105 to AON | No receiving CMOS input in saved circuit; no conditioning needed presently. |
| HOST_SENSE, BUCK_FB, CC_VBUS_DET, EFUSE_UVLO/OVLO/ILM, CC_PORT | Analog sense/threshold/configuration resistors | Excluded from digital edge limit; retain intended analog hysteresis/filtering and ratings. |
| SOFT_START, BUCK_SS, EFUSE_DVDT | C6/C9/C101 timing nodes | Analog ramps, not digital CMOS input defects. |
| Z_D0–15 and other tri-state bus/boot nets | RP and U46/U47 handoff; U44/U45 input stages remain connected | No external data-bus biases in saved circuit. Idle validity depends on RP pulls/firmware and host bus behaviour; OE disabling does not disconnect input transistors. **Additional bus-idle validation needed**, not cured by control Schmitt buffers. |

All remaining resistor groups are power dividers, discharge, crystal damping,
USB/SD series terminations or already covered above. All remaining internal
gate inputs are driven push-pull or tied to a rail during valid operation.
Supply-tied inputs are not guaranteed logic during supply ramp; that is a
power-valid problem, not a reason to add a buffer to every rail tie.

## 4. Conservative RC bounds and lower-pull-up alternatives

These are **design-envelope calculations**, not fabricated guaranteed maxima.
The board is unrouted; several ICs specify only typical capacitance and the
existing 2N7002 value lacks a manufacturer-specific capacitance bound. No
honest unconditional worst-case rise time can be extracted from this BOM yet.

Use qualified 10k ±1%, ≤100ppm/°C resistors; allow another 1% temperature
variation: Rmax=10.2k. For local open-drain/logic nodes allocate 50pF total:
10pF receiver allowance, 10pF source, 20pF trace/pads, 10pF probe. This is
deliberately larger than a typical 3.5–4.9pF input. For RP raw reset allocate
200pF including MOS drain, both device/header loads and service wiring.
External host nodes have no proved maximum; evaluate a 200pF example but do
not label that a measured or guaranteed host load.

At VCCmin=3.0V and 10µA adverse leakage, Vfinal=2.898V:

| R nominal / total C | RC max | 10–90% time | 0.8→2.0V rise | 2.0→0.8V fall, zero leakage |
|---|---:|---:|---:|---:|
| 10k / 50pF | 510ns | 1.121µs | 433ns | 467ns |
| 10k / 200pF | 2.04µs | 4.482µs | 1.731µs | 1.869µs |
| 1k / 50pF | 51ns | 112ns | 40.5ns | 46.7ns |

The 10–90% time is relative to the final RC amplitude; threshold traversal
includes leakage. A resistor-released falling edge is exponential too. With
50pF, the local slope at 2V on a 3V rising edge requires roughly R≤200Ω to
reach 10ns/V even ignoring leakage. That demands up to ~18mA at 3.6V:
incompatible with the supervisor's 1mA VOL test guarantee and buck PG's 2mA
guarantee. Even 1k cannot close the 50pF case. [S12,S13]

Keep 10k at R6/R9/R10/R62 and 10k fail-low biases; keep the approved 10k
isolated request array. Schmitt conditioning removes reliance on a fast raw
RC edge. It does **not** remove leakage/DC-level, latency or input-noise limits.
Enforce clean output loads ≤50pF, preferably ≤20pF; raw reset service wiring
must remain inside its declared envelope. No extra RC debounce capacitors are
proposed on bus or request clocks.

## 5. Concrete conditioning candidate

Provisional names below are not existing CAD references.

| Change | Exact part / value | Connection proposal | Added fitted count |
|---|---|---|---:|
| U7 | TI **SN74LVC1G14DBVR** | 2=CC_LOW_CURRENT, 4=POWER_ALLOW, 3=GND, 5=3V3_AON, 1=NC; retain planned local 100nF addition | 0 beyond approved subtotal |
| SA | Nexperia **74LVC3G17DC,125** | 1→7 HOST_PG→HOST_PG_C; 3→5 3V3_PG→3V3_PG_C; 6→2 RP_RESET_RAW→RP_RUN | +2 with bypass |
| SB | Same | 1→7 RUN_MODE_RAW→RUN_MODE; 3→5 BUS_ARM_RAW→BUS_ARM; 6→2 BUS_READY_RAW→BUS_READY | +2 |
| SC | Same | 1→7 DATA_DRIVE_RAW→DATA_DRIVE; 3→5 ACK_REQ_RAW→ACK_REQ; 6→2 IRQ_REQ_RAW→IRQ_REQ | +2 |
| SD | Same | 1→7 FLASH_RP_RAW→FLASH_RP_SWITCH; 3→5 FLASH_ESP_RAW→FLASH_ESP_SWITCH; pin6=GND, output2=NC | +2 |
| SE | Same | 1→7 AMIGA_RESET_N→U43.6; 3→5 AMIGA_BERR_N→U43.8; 6→2 AMIGA_DTACK_N→U43.7; outputs get new local net names | +2 |

SA–SE pin8=main3V3, pin4=GND, each with its own 100nF X7R 0603,
≥10V, ±10% bypass. The capacitor manufacturer part number is not yet
qualified; this is a value/rating specification, not an orderable passive BOM.
Use three-gate packages locally instead of distributing one central package's
outputs across the board. One unused gate in SD is preferable to forcing a
different-domain signal into it. All pull resistors remain on the **raw** side;
RP GPIOs drive raw request nets, never the buffer outputs. J20.5, Q2 and SW1
remain open-drain/contact controls of RP_RESET_RAW. No push-pull contention is
introduced on the reset node.

S6 specifies pin mapping, 7.1ns maximum delay at 3.0–3.6V/50pF through125°C,
and ±2µA Ioff at VCC=0. Its threshold limits are given at discrete supply
points, not as a guaranteed interpolated 3.3V curve. Local inputs reach their
own supply rail; host conditioned inputs are intended for 5V pull-up levels,
not an assumed 2.4V minimum push-pull source. Confirm host low/high margins
and overshoot at the connector. Do not silently use these parts as arbitrary
TTL-to-CMOS translators on every address/data line.

### Timing and reset effects

- Boolean equations and polarity are unchanged after inputs settle. SA/SB
  add one stage to safety qualification. SC adds one stage to request paths.
- I1/I2 address→XRDY remains **36.5ns including the existing 10ns allowance**;
  /AS→XRDY remains **34.3ns**, assuming stable SAFE, cleared latch and qualified
  bus edges. No Schmitt stage is added to those paths.
- For fast, specified test edges, request delay is 1.0–7.1ns. A 20ns pulse can
  shrink to 13.9ns, still above the existing 2.7ns latch requirement. Retain
  the ≥100ns DATA_DRIVE-to-ACK interval and ≥60ns /AS-to-DATA_DRIVE rule.
- The existing 50ns /AS-inactive requirement is unchanged by these buffers:
  asynchronous-clear paths stay in the original fast logic. Reset/arming
  release must additionally wait for raw RC settling and firmware readiness.
- SE adds a 7.1ns *fast-edge* allocation to host RESET/BERR paths. Slow raw
  release latency depends on actual host pull-up and capacitance. Do not add
  7.1ns to an arbitrary slow-input threshold crossing and call that a
  guaranteed maximum; the published timing test uses ≤2.5ns input edges.
- No new filter delays reset assertion intentionally. Button bounce can still
  reset repeatedly; Schmitt hysteresis is not debouncing or a pulse stretcher.
- U7 has a 6.5ns full-temperature fast-edge limit; CC negotiation is not in the
  60ns bus path. Current downgrades still need the existing shutdown response
  reviewed across controller, switch and discharge delays.

### Alternatives rejected or deferred

| Alternative | Decision |
|---|---|
| Reduce all pull-ups to 1k or below | Reject: cannot meet conservative RC bound and supervisor/PG sink limits together. |
| Replace LA with **SN74HCS11PWR** | Attractive zero-extra-package option, unlimited input transition time. Defer: positive clamps/no specified Ioff, and no guaranteed 3.3V delay row; 2V/4.5V limits cannot be silently interpolated. It also does not solve IRQ/clock/USB inputs. [S14] |
| Substitute Nexperia ordinary LVC gates/FFs | Reject as sole cure: their explicit transition limits remain despite Schmitt-action prose. |
| Use TI **SN74LVC1G97DBVR** as U82's Schmitt AND | Electrically plausible, but with SC already needed for both clock inputs, using its third channel keeps U82 and avoids a package/pin-map change without increasing count. |
| Lower all resistors / add RC filtering | Does not fix undefined supply operation; added RC on request clocks harms timing. |

## 6. Power-up, shutdown and brownout: unresolved safety findings

The board's source is **USB VBUS**. AMIGA_5V is sensed through R60/R61;
it is not an alternative main-power input. “AON” means upstream of the main
load switch, not battery-backed or present without USB.

| Condition | Result of audit |
|---|---|
| Valid USB, Amiga off | U60 senses absent host voltage; after valid supervisor operation HOST_PG low prevents SAFE. Conditioning preserves this. Host receivers themselves can float with the host off; disable/idle-input behaviour still needs a firm constraint. |
| Amiga on, USB absent, rails fully zero | No power OR path from Amiga. Retain 5.5V-tolerant/Ioff bus interfaces. New SE has specified power-off isolation. U60 SENSE is rated independently to 6.5V, but its unpowered leakage/backfeed must not be inferred solely from that voltage rating. |
| USB default-current / not attached | OUT1 released → pull-up → U7 inverter low → main switch off once AON valid. U7 Schmitt preserves the truth table. Below AON's valid operating range its output is not guaranteed. |
| Main starts while AON valid | Disarm/request raw pulls remain low; firmware may arm only after power and reset qualification and idle bus. No deterministic DFF power-up Q is assumed. |
| Main undervoltage, EN shutdown, thermal shutdown | **TPS62130 PG is high-Z**, potentially read high by R9 while the rail decays. Even normal falling PG threshold is 87–94% of target, so it may not trip until about2.87V for a nominal3.3V rail—below the 3.0V timing corner. |
| USB removal / both domains decay | Ioff at exactly0V does not prove high-Z throughout intermediate supply voltages. Shared-rail OEs and AON inverter cannot supply a guaranteed shutdown sequence on their own. |
| External SWD/UART attached to unpowered board | Service interfaces have no blanket power-off isolation guarantee. Require high-Z/open-drain service behaviour while target off; externally powered push-pull UART/boot/reset drives remain unqualified. |

**Recommended buck correction:** change U5 to **TPS62130ARGTR**, the A variant
with PG asserted low during EN/UVLO/thermal shutdown while VIN remains present.
This uses the same RGT pinout and costs no added package. It is a correction to
the PG truth table, **not a complete brownout solution**: its percentage
threshold and loss-of-VIN limitation remain. Preserve the regulator cell and
verify the variant against the same power design. [S13]

**Additional guard needed before safety sign-off:** independently monitor main
3V3 above its qualified minimum, hold RP reset/disarm until valid, directly
inhibit the spare OE inputs on U44–U47, and force both host open-drain sinks
released before their driving logic becomes undefined. Guard must remain valid
through AON/main decay and not back-power either domain. An OE-only guard is
insufficient for XRDY/IRQ.

Do **not** rubber-stamp a **TPS3808G33DBVR** as that complete guard. It is an
exact candidate for delayed reset qualification, but the reviewed SENSE-to-
RESET delay is only typical (20µs), and its low-voltage guarantees do not
establish the required whole-board turn-off sequence. For illustration,
22µF at1.2A loses0.1V in only1.83µs; capacitance derating makes that shorter.
The final guard needs a guaranteed detection/shutdown bound, an explicit
hold-up/discharge envelope and host-sink isolation. This review has **not**
qualified an exact complete guard circuit and therefore does not authorize
implementing the Schmitt proposal as if all power-state concerns were closed.

Similarly, no claim is made that the current host-sense delay will release
outputs before every possible abrupt Amiga rail collapse. Resolve that
boundary and the data-bus idle bias contract as part of the corrective circuit
proposal, without rerunning USB feasibility tests.

## 7. BOM, placement and next approval boundary

| Scenario | Fitted components |
|---|---:|
| Current untouched CAD | 188 |
| Originally approved I1/I2/R-A/R-B plus two bypasses | 162 |
| Above plus five local triple Schmitt buffers and five bypasses; U7 and U5 replacements | **172 provisional subtotal** |
| Complete power-valid guard / any required bus-idle components | **Not yet determined; additional to172** |

The172 subtotal comprises41 U packages,43 resistor packages,68 capacitors and
20 other fitted parts;176 footprints including four mounting holes. It is not
a final safe-board target or an implemented BOM.

Place SA by reset/power qualification, SB by arm/ready logic, SC by latch
clocks, SD by USB switch controls, SE by U43. Each bypass is local to pin8.
Do not move bus buffers, connector/mechanics or either regulator cell. Do not
use a global placement generator. Schmitt outputs and unchanged critical
paths still require native net checks, ERC, incremental PCB sync, DRC and
visual review after implementation is approved.

Recommended order: close the power guard and idle-input contract first;
approve the complete corrective pin map; implement conditioning/reset/power
corrections in the schematic; then I1, I2, R-A and R-B as separate reversible
commits with per-stage verification. Stop here for review. This document is
not permission to modify CAD or to proceed to routing.

## Manufacturer sources

- S1 [TI SN74LVC11A](https://www.ti.com/lit/ds/symlink/sn74lvc11a.pdf), recommended conditions, electrical/switching tables and standard-CMOS discussion.
- S2 TI [1G11](https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf), [1G04](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf), [1G08](https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf), [1G74](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf).
- S3 TI [541A](https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf), [04A](https://www.ti.com/lit/ds/symlink/sn74lvc04a.pdf).
- S4 [TI TS3USB30E](https://www.ti.com/lit/ds/symlink/ts3usb30e.pdf).
- S5 Nexperia [1G74](https://assets.nexperia.com/documents/data-sheet/74LVC1G74.pdf), [1G08](https://assets.nexperia.com/documents/data-sheet/74LVC1G08.pdf), [541A](https://assets.nexperia.com/documents/data-sheet/74LVC541A.pdf), recommended-condition tables.
- S6 [Nexperia 74LVC3G17](https://assets.nexperia.com/documents/data-sheet/74LVC3G17.pdf), Rev15, pin table and sections10–12; [order code](https://www.nexperia.com/chemical-content/74LVC3G17DC.html).
- S7 [TI SN74LVC1G14](https://www.ti.com/lit/ds/symlink/sn74lvc1g14.pdf), RevAA.
- S8 [TI Implications of Slow or Floating CMOS Inputs](https://www.ti.com/lit/an/scba004e/scba004e.pdf).
- S9 [onsemi FUSB303B](https://www.onsemi.com/pdf/datasheet/fusb303b-d.pdf), Rev3, pin7 GPIO-mode table.
- S10 [Espressif schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html), power/reset section.
- S11 [Winbond W25Q128JV](https://www.winbond.com/resource-files/W25Q128JV%20RevI%2008232021%20Plus.pdf), power-up restrictions and AC test conditions; [RP2350 datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf), RUN and IO electrical characteristics. RP reference text was available locally at /tmp/rp2350-datasheet.txt; current download attempts were blocked, so no claim of newly retrieved revision.
- S12 [TI TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf), RevN, RESET pull-up guidance and tables6.5–6.6.
- S13 [TI TPS62130/TPS62130A](https://www.ti.com/lit/ds/symlink/tps62130.pdf), RevF, section8.3.3 and tables8-1/8-2.
- S14 [TI SN74HCS11](https://www.ti.com/lit/ds/symlink/sn74hcs11.pdf), RevC, clamps, unlimited input-slew row and switching table.
