# FujiNet A500 R4 — pre-routing component optimisation review

2026-11-10. **Analysis/proposal only; no schematic, PCB or project settings changed.**

Recommendation: consolidate the main-domain Boolean logic first, selectively use isolated resistor arrays, and retain the distributed bus buffers and safety interfaces for the first revision. Target **154 fitted components instead of 188**, subject to the validation gates below. This includes two additional bypass capacitors, not indiscriminate capacitor removal. The target is fewer placements and simpler circuit organisation; a smaller PCB or lower BOM cost is not yet demonstrated.

## Evidence and limits

- Exported all nine sheets of the **saved** schematic with KiCad 10, rather than trusting the previous PDF or generator. The fresh netlist has 188 physical components and matches all 864 recorded functional pin assignments. Inspected the exported RP and interlock sheets visually and read all components/nets. Independently compared all 864 functional pad assignments and all 188 component values between fresh schematic and saved PCB. Read the saved board with native pcbnew for positions, sides and package counts.
- The schematic/project files were already modified at task start; PCB matches the latest saved placement revision. Preserved the working tree as found. `preservation.json` records SHA-256 before/after for every R4 schematic, PCB and project file.
- `circuit.json`'s **components/pins** agree with the netlist, but its old **gates** shorthand is stale: U63 actually produces SAFE_BASE, U71/U75 use DATA_VALID, U80 produces WAIT_SINK, and U81 drives XRDY, not DTACK. This review uses the actual saved connections. J40 also has a harmless value-label alias: the saved schematic and board say “A500 FEMALE mating socket”, while the plan names ED86BGFBK. Any later generator change must fix that metadata separately; never regenerate from the obsolete shorthand.
- [Full BOM](bom.csv), [35-device logic inventory](logic-inventory.md), [all 49 resistors](resistors.csv), [all 72 capacitors](capacitors.csv) include actual nets and positions. Capacitor ownership below is an engineering assignment, not something connectivity on a shared power net proves.
- **Verified** means checked against the saved netlist or cited manufacturer document. **Conditional proposal** means a concrete, pin-mapped alternative requiring implementation checks. **Deferred** means not included in the recommended count. No proposed replacement has been routed or measured.
- Existing native-check record: zero schematic/PCB parity findings, six retained DRC findings, 499 unconnected items and zero tracks. Those are prior baseline results, not a fabrication pass. This review did not rerun mutating build/placement scripts or use ERC as evidence of electrical equivalence.

## Requirements for the review

| Requirement | Decision | Evidence/check | Still open |
|---|---|---|---|
| Preserve host isolation | Keep 5 V-tolerant/Ioff bus receivers and open-drain host outputs | Actual pin nets; device datasheets | Supply-ramp/backfeed analysis and prototype waveforms |
| Preserve hardware wait/read safety | Preserve equations, independent byte enables and both asynchronous-clear state elements | Gate maps below; existing bus contract | New timing, pulse/recovery, hazards and OE races |
| Reduce assembly count | Consolidate gates within the main 3V3 domain; two isolated arrays | Explicit package and capacitor arithmetic | Supplier price, assembly yield, routing comparison |
| Keep necessary bypassing | One local bypass per replacement logic package; retain processor and regulator-specific capacitors | Manufacturer power guidance | Effective capacitance, pin-level placement, loop geometry |
| Four-layer layout | Continuous L2 ground; short reference-backed critical paths | Native geometry and manufacturer layout guidance | Fabricator stackup, USB impedance and enclosure qualification |

## 1. Current BOM

| Category | Fitted packages |
|---|---:|
| U-designated IC/module packages | 47 |
| Of those, 74-series | 35 |
| Resistors, all discrete | 49 |
| Capacitors | 72 |
| MOSFETs | 4 |
| Protection diode/ESD packages | 2 |
| Connectors/headers | 7 |
| Pushbuttons | 4 |
| Inductors | 2 |
| Crystal | 1 |
| **Total fitted schematic components** | **188** |
| Board-only mounting-hole footprints | 4 |
| **Total PCB footprints** | **192** |

The 47 U packages comprise 46 IC packages plus the ESP module; the module's internal parts are not separately counted. This is not yet an orderable BOM: most passives have values and generic footprints, not manufacturer part numbers or complete dielectric/tolerance/rating selections. The requested complete 74-series inventory is in [logic-inventory.md](logic-inventory.md), one row per reference, including used gates/channels, supplies, signal domains, connected signals and consolidation disposition.

### Electrical boundaries

All logic operates at nominal 3.3 V. U7 alone uses `3V3_AON`; all other 74-series packages use switched `3V3`. U40–U43 translate raw host inputs into the internal domain. U44/U45 drive host data, U46/U47 receive it. U81/U83 sink host XRDY and /INT2; neither may be replaced by a push-pull inverter. No local /DTACK driver exists.

The fitted [SN74LVC541A](https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf) accepts inputs to 5.5 V, has Ioff and independent active-low OE pins. At 3 V supply, its loaded output guarantees include VOH ≥2.2 V at −24 mA (≥2.4 V at −12 mA) and VOL ≤0.55 V at 24 mA. These are TTL-compatible levels, **not 5 V CMOS highs**. Host receiver thresholds, actual fanout and current must remain checked; “5 V tolerant” describes permitted input voltage, not 5 V output drive. Retain the existing eight buffers for the initial proposal.

No gate is guaranteed to behave as valid logic throughout an arbitrarily slow or interrupted supply ramp. Ioff is a VCC=0 guarantee, not a brownout-state guarantee. Preserve host-power sensing, main-power-good qualification, RUN/reset, BUS_ARM, BUS_READY, BERR shutdown and OE pull-ups. USB-powered/Amiga-off operation must leave every host-facing driver disabled or released. Amiga-powered/USB-off operation must not feed the dead board through its bus pins.

## 2. Ranked IC proposals

Counts include the removed packages' dedicated 100 nF bypasses and one retained/reassigned bypass per new package. No capacitor is shared between separate ICs to obtain the saving.

| ID / priority | Original devices | Exact proposed replacement | Use | IC reduction | Bypass reduction | Benefit / risk / effort | Recommendation |
|---|---|---|---|---:|---:|---|---|
| I1 / 1 | U61,U62,U63; U66,U67,U68; U71,U76,U80 | **3 × TI SN74LVC11APWR**, TSSOP-14 | Three triple-AND packages, all 9 gates used | 6 | 6 | High / medium / medium | Main proposal; group by function, not existing grid rows |
| I2 / 2 | U64,U65,U69,U70,U74,U75 | **TI SN74LVC04APWR**, TSSOP-14 | All 6 inverters | 5 | 5 | High / medium / medium | Main proposal; floorplan between address decode and byte logic |
| I3 / 3 | U72,U73,U77,U78 | **TI SN74LVC00APWR**, TSSOP-14 | All 4 NAND gates; tied-high third inputs disappear | 3 | 3 | High / medium / medium | Conditional on main-domain power-off audit and OE timing |
| I4 / 4 | U84,U86 | **TI SN74LVC74APWR**, TSSOP-14 | Both positive-edge DFFs; independent clocks/clears preserved | 1 | 1 | Medium / medium-high / medium | Conditional; do not treat as a pin-compatible swap |
| I5 / 5 | U81,U83 | **TI SN74LVC2G06DBVR**, SOT-23-6 | Both open-drain inverters | 1 | 1 | Low-medium / medium / low-medium | Optional after connector-side routing comparison |
| I6 / 6 | U82,U85 | **TI SN74LVC08APWR**, TSSOP-14 | 2 of 4 AND gates | 1 | 1 | Low / medium / medium | Prefer existing singles: SAFE and IRQ locations differ; two spare gates and larger body |

**Keep U7 separate:** combining it with switched-domain inverters would defeat power qualification. Keep U79 single: one OR gate does not justify a quad OR package. Keep the bus buffers initially: they are already multi-channel, distributed interfaces with meaningful direction/byte boundaries.

The conditional main proposal is I1–I4, not automatic permission to install all six options. If I3/I4's power-off conditions cannot be established, retain their existing parts; the lower-risk subtotal is given below.

### Proposed gate-to-pin assignments

Provisional new references here are `LA`, `LB`, `LC`, `LI`, `LN`, `LF`, `LO`, `LG`; these do not rename anything in the CAD. All use `3V3` and GND. The following mappings are complete enough for schematic implementation, with a separate library-symbol/pad audit still required.

**I1 — three SN74LVC11APWR packages.** Each has VCC14/GND7; gate A inputs 1,2,13 → Y12; B inputs 3,4,5 → Y6; C inputs 9,10,11 → Y8. Pinout and 4.1 ns maximum at 3.3 V ±0.3 V, 50 pF, −40…125°C are from [TI §4/§5.6](https://www.ti.com/lit/ds/symlink/sn74lvc11a.pdf). Input tolerance is 5.5 V; Ioff is specified. No unused gates.

| New gate | Old | Input pin=net assignments | Output pin=net |
|---|---|---|---|
| LA.A | U61 | 1=HOST_PG, 2=3V3_PG, 13=HOST_RESET_N | 12=SAFE_POWER |
| LA.B | U62 | 3=RP_RUN, 4=RUN_MODE, 5=BUS_ARM | 6=SAFE_MODE |
| LA.C | U63 | 9=SAFE_POWER, 10=SAFE_MODE, 11=BUS_READY | 8=SAFE_BASE |
| LB.A | U66 | 1=Z_A23, 2=Z_A22, 13=Z_A21 | 12=IO_TOP |
| LB.B | U67 | 3=IO_TOP, 4=A20_LOW, 5=Z_A19 | 6=IO_WINDOW |
| LB.C | U68 | 9=SAFE, 10=AS_ACTIVE, 11=IO_WINDOW | 8=CYCLE_OK |
| LC.A | U71 | 1=CYCLE_OK, 2=Z_READ, 13=DATA_VALID | 12=READ_DRIVE |
| LC.B | U76 | 3=CYCLE_OK, 4=WRITE_CYCLE, 5=DATA_RECEIVE | 6=WRITE_RECEIVE |
| LC.C | U80 | 9=CYCLE_OK, 10=WAIT_PENDING, 11=3V3 | 8=WAIT_SINK |

Keep/reassign C70,C75,C80, one per package. Retire C71,C72,C76,C77,C85,C89 only with the associated old packages. The retained references are a bookkeeping proposal; place each at the new VCC pin.

**I2 — SN74LVC04APWR.** VCC14/GND7. U64: 1=Z_AS_N → 2=AS_ACTIVE; U65: 3=Z_A20 → 4=A20_LOW; U69: 5=Z_LDS_N → 6=LO_ACTIVE; U70: 9=Z_UDS_N → 8=HI_ACTIVE; U74: 11=Z_READ → 10=WRITE_CYCLE; U75: 13=DATA_VALID → 12=DATA_RECEIVE. Keep/reassign C73; retire C74,C78,C79,C83,C84. [TI §4/§6.8](https://www.ti.com/lit/ds/symlink/sn74lvc04a.pdf) gives 6 ns worst-case through 125°C at 3.3 V ±0.3 V, versus the current budget's 4.2 ns single inverter. It has 5.5 V-tolerant inputs and Ioff. Its common supply is suitable only for the six main-domain inverters; do not include U7.

**I3 — SN74LVC00APWR.** VCC14/GND7. U72: 1=READ_DRIVE,2=LO_ACTIVE →3=TX_LO_N; U73: 4=READ_DRIVE,5=HI_ACTIVE →6=TX_HI_N; U77: 9=WRITE_RECEIVE,10=LO_ACTIVE →8=RX_LO_N; U78: 12=WRITE_RECEIVE,13=HI_ACTIVE →11=RX_HI_N. The actual old third inputs are all hard-tied to 3V3, so 2-input NAND is Boolean-equivalent. Keep C81; retire C82,C86,C87. [TI §4/§5.9](https://www.ti.com/lit/ds/symlink/sn74lvc00a.pdf) gives 5.5 ns max at 3.3 V ±0.3 V through 125°C. Inputs tolerate 5.5 V, but the reviewed datasheet has **no Ioff parameter**: do not infer partial-power-down isolation from the family name. All connected inputs/outputs here are main-domain; prove that no externally powered path drives them during shutdown. Otherwise retain the singles or qualify a documented alternative.

**I4 — SN74LVC74APWR.** VCC14/GND7. First FF replaces U84: /CLR1=CYCLE_OK, D2=ANY_LANE, CLK3=ACK_REQ, /PRE4=3V3, Q5=NC, /Q6=WAIT_PENDING. Second replaces U86: /CLR13=CYCLE_OK, D12=3V3, CLK11=DATA_DRIVE, /PRE10=3V3, Q9=DATA_VALID, /Q8=NC. Keep C93; retire C95. [TI §4/§5.8/§5.11](https://www.ti.com/lit/ds/symlink/sn74lvc74a.pdf): 5.2 ns clock-to-output, 5.4 ns async-to-output maximum; ≥3.3 ns clock and clear pulses, 3 ns setup, 1 ns hold, 2 ns clear/preset recovery at 3.3 V ±0.3 V. Compared with the existing [single FF](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf), requirements change; POR does not supply a guaranteed initial Q. The reviewed dual datasheet does not specify Ioff. Both clocks must start low, clear must be asserted before arming, and all driving signals must remain main-domain. Never substitute the library's AUC part value for either LVC device.

**I5, optional — SN74LVC2G06DBVR.** VCC5/GND2; 1=WAIT_SINK →6=AMIGA_XRDY; 3=IRQ_SINK →4=AMIGA_INT2_N. Keep C90; retire C92. [TI §5/§6](https://www.ti.com/lit/ds/symlink/sn74lvc2g06.pdf) specifies 5.5 V-tolerant open-drain outputs, Ioff, and 3.9 ns worst-case propagation at 3.3 V through 125°C. Check both host pull-up loads, VOL/sink current and simultaneous package current. Do not add a board 3V3 pull-up to these host nets. Leave separate if reaching the widely separated connector contacts adds excessive XRDY load or awkward crossing.

**I6, optional — SN74LVC08APWR.** VCC14/GND7; 1=SAFE,2=IRQ_REQ →3=IRQ_SINK; 4=SAFE_BASE,5=HOST_BERR_N →6=SAFE. Tie unused inputs 9,10,12,13 to GND; outputs 8,11 NC. Keep C91; retire C94. [TI §4/§5.9](https://www.ti.com/lit/ds/symlink/sn74lvc08a.pdf) gives 5.5 ns maximum through 125°C at 3.3 V ±0.3 V, and 5.5 V input tolerance. No Ioff parameter in the reviewed datasheet. Benefit is small; prefer local singles unless floorplanning makes this an actual routing improvement.

The replacements drive **3.3 V logic**, not host-level highs. At 3 V supply the loaded guarantees differ: I1 and I4 specify VOH ≥2.2 V / VOL ≤0.55 V at 24 mA; the full-temperature I2/I3/I6 tables allow VOH down to 2.0 V / VOL up to 0.8 V at that load. Those latter values leave no useful margin against the receiving LVC 2.0 V / 0.8 V thresholds. Actual loads are logic inputs and bias resistors, not 24 mA loads: sum worst-case leakage, pull currents and dynamic capacitance, and choose a lower-current operating point with margin. Do not mistake per-pin drive capability for permission to switch every output at that current simultaneously. I5 has no driven high level: the host pull-up determines it. These are explicit electrical acceptance conditions for each proposal, not assumed equivalence.

Unused **inputs** must never float; unused **outputs** stay unconnected. NC pins designated by the manufacturer are not extra logic inputs. Do not repurpose spare gates into another power domain.

### Timing and state risk

The existing [A500 bus review](../../../integrated-a500-r3/bus-review.md) allocates 60 ns to XRDY assertion from valid address, with a provisional 10 ns interconnect/load allowance. For I1–I4 with the existing U81, the same stable-SAFE, already-cleared-latch assumptions give:

- Address chain: receiver 5.6 + four triple-AND stages ×4.1 + sink 4.5 = **26.5 ns**, or **36.5 ns** with the old 10 ns allowance.
- /AS chain: receiver 5.6 + hex inverter 6.0 + two AND stages ×4.1 + sink 4.5 = **24.3 ns**, or **34.3 ns** including the allowance.

These are recalculated **allocations, not a timing pass**. The existing captures establish bus visibility, not active timing. Package consolidation changes wire lengths, capacitive fanout, simultaneous switching and skew. Recalculate the SAFE/BERR/reset-disable path, DATA_VALID-to-OE path, read/write nonoverlap, /CLR recovery and XRDY release with extracted loads and actual voltage/temperature limits. Fast logical equivalence does not prove absence of glitches on multi-bit address transitions. Preserve the existing firmware ordering and bounded-service/watchdog obligations; no firmware change or new physical test is requested in this review.

### Larger buffers and other alternatives examined

[TI SN74LVC16244ADGGR](https://www.ti.com/lit/ds/symlink/sn74lvc16244a.pdf) can combine pairs of octal buffers into 16-bit TSSOP-48 packages: four independently enabled four-bit banks, 5.5 V inputs, Ioff and tri-state outputs. This is electrically plausible for U40+U41, U42+U43, U44+U45 and U46+U47, but **deferred, not recommended for the first optimisation**. It has four VCC pins per package: replacing eight one-VCC buffers with four such parts suggests 16 local bypasses instead of eight. Thus four fewer IC packages can mean **four more fitted components overall**. Finer pitch, escape routing, distributed connector contacts and package-current limits further weaken the case. No gate-to-pin migration is proposed for this deferred redesign.

An octal bidirectional 245 is not a direct replacement for each TX/RX pair: independent read/write enables become DIR+/OE logic, turnaround changes and power-off/host-drive contention need a new safety proof. CPLD/FPGA replacement would add programming, startup and verification scope; exclude it from this first-board consolidation. Avoid HC/HCT/AC/ABT substitutions based on matching gate numbers alone.

## 3. Resistor arrays

The complete resistor inventory lists both terminals of every resistor. Generic 0603 footprints do **not** establish a power rating or tolerance. For ordinary bias parts, specify 1% unless a justified alternative is approved; preserve every explicit 0.1%/1% requirement already recorded.

Use **isolated** arrays for the first revision. An isolated array contains separate resistors; any common connection is made explicitly in PCB copper. A common-terminal/bussed array internally joins one end: suitable only when every resistor truly shares the same rail. It must not join AON to main 3V3 or replace series resistors/dividers. A bussed five-resistor SD network is logically possible, but no specific compact, assembly-qualified bussed part is recommended here; the isolated four-plus-one arrangement has a clear pin/rail audit and uses all elements.

| ID / rank | Originals | Exact proposed part / wiring | Package reduction | Benefit / risk / effort | Decision |
|---|---|---|---:|---|---|
| R-A / 1 | R37–R40, each 47k; retain R41 | **Bourns CAT16-4702F4LF**, 4 isolated 47k ±1%; one end of each to 3V3, other ends SD_DAT2, SD_CS, SD_MOSI, SD_MISO respectively | 3 | Medium / low / low | Recommend, near J30; keep fifth 47k pull-up for SD_DAT1 |
| R-B / 2 | R64–R67, each 10k | **Bourns CAT16-1002F4LF**, 4 isolated 10k ±1%; BUS_READY, DATA_DRIVE, ACK_REQ, IRQ_REQ respectively to GND | 3 | Medium / low-medium / low | Recommend near RP pins 57,58,55,56; same bank, preserve fail-low bias |
| R-C / 3 | R50–R53, each 10k | Same **CAT16-1002F4LF**, isolated elements from main 3V3 to TX_LO_N,TX_HI_N,RX_LO_N,RX_HI_N | 3 | Medium / medium / medium | Deferred: present buffer column distributes OE pins over a long distance; retain local pull-ups unless buffers are reclustered |
| R-D / 4 | R32,R33, each 10k | **Bourns CAT16-103J2LF**, two isolated 10k ±5% to GND | 1 | Low / low-medium / low | Optional only; 5% is a deliberate tolerance choice, not a silent substitute; keep discrete in main estimate |

[Bourns CAT/CAY16 datasheet](https://www.bourns.com/pdfs/CATCAY.pdf) verifies the ordering codes, isolated circuits, 62.5 mW per element and 250 mW total at 70°C for F4, 50 V working limit, and temperature derating to 125°C. F4 is a 3.2 ×1.6 mm body with 0.8 mm terminal pitch; J2 is 1.6 ×1.6 mm, 125 mW total. Proposed elements dissipate at most **1.31 mW** for 10k ±1% at 3.6 V, or **0.279 mW** for 47k ±1%. Four-element totals remain below 5.3 mW. These are ample nominal margins; verify the final ambient derating and actual manufacturer land pattern. Procurement availability/prices have not been qualified.

Keep R1–R3/R63 local to their destinations or mode controls rather than creating a long central bias bus. Keep R6 on AON separate from main-rail pull-ups. Keep R10/R11/R12/R20 near their reset/boot destinations. Keep R34/R35 as the VBUS-valid divider, not an equal-valued pull network. Keep R5's high-value CC sense path, R7/R8 buck feedback, R60/R61 host threshold and R100–R104 e-fuse thresholds/current setting discrete with their specified tolerances. The 10k 0.1% parts R61/R101/R103 must **not** become elements of a 1% array.

Keep R22/R23 (27 Ω RP USB), R30/R31 (22 Ω ESP USB), R36 (33 Ω SD clock), R21 (crystal drive), R24 (regulator filter), R13 (boot isolation) and R14 (discharge) discrete. Series-resistor arrays might save one package but can add coupling or force poor source/pair placement; no measured routing benefit presently justifies that change. Do not add pull-ups to Amiga bus nets merely to fill spare array elements.

## 4. Capacitors and power — retain by function

The capacitance inventory includes **timing/filter/load** capacitors as well as bypass capacitors. The following covers all 72 references.

| References | Role / power pin assignment | Recommendation |
|---|---|---|
| C1,C2 | U1/U2 USB switch VCC10 | Retain 100 nF at each switch |
| C3 | U3 CC-controller VDD12, AON | Retain 100 nF locally; not shared with U7 |
| C4,C5 | U6 input pin1 and output pin5 | Retain 1 µF each, satisfy regulator stability/effective capacitance |
| C6 | U4 soft-start pin4 relative to input | Timing component, retain; not ground decoupling |
| C7,C8 | U5 PVIN11/12 input bulk and 3V3 output bulk | Retain 10/22 µF and qualified bias/ESR/ripple ratings |
| C9 | U5 SS/TR9 | Retain timing capacitor |
| C10 | ESP_EN RC with R11 | Retain reset timing; not supply bypass |
| C20 | U21 flash VCC8 | Retain 100 nF at package |
| C21,C22 | RP crystal load capacitors | Retain; validate against crystal CL and stray capacitance, not “15 pF by convention” |
| C23 | U20 VREG_AVDD61, after R24 | Retain 4.7 µF/filter/reference geometry |
| C24 | U20 VREG_VIN64 | Retain 4.7 µF in reference regulator cell |
| C25 | Regulator output / U20 DVDD65 | Retain 4.7 µF at output in reference cell |
| C26–C36 | Eleven 100 nF bypasses for eight IOVDD pins plus ADC, USB/OTP, QSPI supplies | Retain all; make pin ownership explicit below |
| C37,C38,C39 | Other three DVDD sites, two 100 nF plus one 4.7 µF | Retain; correct placement ownership before optimisation |
| C40,C41 | U30 module 3V3 pin2: 10 µF +100 nF | Retain at module input, short ground return |
| C42,C43 | J30 SD VDD4: 10 µF +100 nF | Retain at socket; investigate returning to top side after consolidation |
| C50–C57 | U40–U47 VCC20, one each | Retain eight 100 nF while these packages remain |
| C60 | U60 supervisor VDD6 | Retain local 100 nF |
| C70–C95 | U61–U86 respectively, one each | Only remove excess bypasses when their associated IC packages are replaced; I1–I4 reduce 26 sites to 11 |
| C100,C102 | U8 input and output bulk, also U9 input rail | Retain protection-path bulk; verify local input/output loops |
| C101 | U8 dVdt pin2 | Retain inrush timing capacitor; not bypass |

**Two additions are budgeted, not implemented:** a dedicated 100 nF at U7 VCC5 (nearest current AON capacitors are ~9.6 mm and ~5.0 mm away by component centres), and a local 100 nF at U5 AVIN10 following its reference application, in addition to the PVIN bulk. Final layout review may justify sharing an adequately local existing capacitor, but the count estimate does not depend on doing so. [TI TPS62130 application/layout guidance](https://www.ti.com/lit/ds/symlink/tps62130.pdf) distinguishes input/output loops, analog supply bypass, feedback and VOS sensing. Preserve direct AGND/PGND/exposed-pad ground, short high-current loops and a quiet VOS connection to output capacitance. Capacitance values alone do not prove stable operation.

### RP2350 pin ownership is more important than the count

Proposed explicit assignment: C26→IOVDD5, C27→15, C28→24, C29→29, C30→41, C31→50, C32→60, C33→ADC_AVDD59, C34→USB_OTP_VDD68, C35→QSPI_IOVDD69, C36→IOVDD76. All are 100 nF. This is a **proposed constraint map**, not a claim that the present routes or schematic establish physical ownership.

For DVDD, use C37→pin10, **C38→pin51 and C39 (4.7 µF)→pin32**, with C25 at the regulator/output site pin65. The current board instead puts C38 at the south and C39 to the right. Pin32 is the farthest of these supply sites from the regulator; swap their intended local roles in the later approved placement pass. The [RP2350 datasheet §6.1](https://pip-assets.raspberrypi.com/categories/1214-rp2350/documents/RP-008373-DS-2-rp2350-datasheet.pdf?disposition=inline) calls for larger capacitance at the distant DVDD site and local ADC/USB decoupling. Preserve the six already-imported reference footprints/relative positions; do not rearrange their tiny cell to make labels symmetrical.

The official hardware-design-guide download was inaccessible during this review; existing reference geometry and its recorded provenance were inspected, and current power requirements were checked in the accessible official RP2350 datasheet. Final sign-off still needs the reference-layout comparison, not merely this proposed pin map.

### ESP, power budget and manufacturing

U30 is a **module**, already containing flash, PSRAM, RF and its own internal bypassing. Do not duplicate the bare-chip external circuit or delete the module input bulk. Keep its supply capable of radio transients; Espressif calls for a supply of at least 500 mA and local bulk in its [hardware guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html). GPIO45/46 straps and EN timing remain explicit. Module pin2 bypass and antenna restrictions follow the [module datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf).

The inherited 1.166 A conditional USB input estimate and 1.197–1.478 A e-fuse limit are not recertified by reducing logic count. Quiescent current may decrease, but Cpd, load and switching activity matter; do not reduce the USB source requirement, fuse/current limit, regulator rating or bulk on that basis. Re-evaluate effective MLCC capacitance under DC bias, ESR, regulator stability, input hot-plug, CC current downgrade, discharge, reverse blocking, and thermal margins with selected orderable parts.

Only C42/C43 are presently on the back. Recovering top-side space for them could remove a second-side SMD assembly operation without removing any electrical component. This may be a more valuable manufacturing improvement than one extra IC consolidation. It remains a placement hypothesis, subject to the SD socket's top-side keepout and a short VDD/ground loop.

## 5. Expected count reduction — explicit scenarios

| Scenario | U packages | Resistor packages | Capacitors | Other fitted | Total fitted | PCB footprints incl. 4 holes | Reduction |
|---|---:|---:|---:|---:|---:|---:|---:|
| Current | 47 | 49 | 72 | 20 | 188 | 192 | — |
| I1+I2, R-A+R-B, plus two bypass additions | 36 | 43 | 63 | 20 | 162 | 166 | 26 (13.8%) |
| **Main target: I1–I4, R-A+R-B, plus two bypass additions** | **32** | **43** | **59** | **20** | **154** | **158** | **34 (18.1%)** |
| Main target plus I5 | 31 | 43 | 58 | 20 | 152 | 156 | 36 (19.1%) |
| Main target plus I5 and I6 | 30 | 43 | 57 | 20 | 150 | 154 | 38 (20.2%) |

The 43 resistor packages in the main target are 41 discretes +2 arrays, still implementing all 49 resistor elements. I1–I4 change 21 original logic packages into six, with fifteen fewer bypasses. Savings are not double-counted. Optional R-C would save three further packages, R-D one; neither is included above. Counts are conditional, not commitments to a new BOM.

**Do not equate fewer placements with less area.** Three TSSOP triple-gate packages occupy about 96 mm² of published lead-inclusive package envelope, versus about 73 mm² for nine SOT-23-6 envelopes, before bypasses/courtyards/routing. TSSOP makes inspection and repair easier than tiny QFN choices, but savings in labels, placements and bypass loops do not guarantee a smaller board. The 111×117 mm envelope is strongly connector/mechanically driven. Exact courtyard area, routability and assembly quote comparisons come after approved floorplanning; no monetary saving is claimed.

## 6. Placement-constraint strategy

Use four layers with L2 as a continuous reference ground. L1 carries components and critical signals; L3 carries power distribution and carefully limited secondary routing; L4 carries remaining signals referenced to appropriate ground copper. Avoid split returns under fast signals. Antenna and connector rule areas remain deliberate local exceptions, not invitations to fragment the ground plane. Final dielectric thickness/copper/stackup must precede a 90 Ω USB geometry calculation.

| Class | Components / constraint | Optimiser authority |
|---|---|---|
| Hard fixed mechanical | J40 position, orientation, both faces/pad numbers; 111×117 outline; H1–H4; 18 mm component-free strip except socket | None without explicit mechanical revision; check formed connector tails and housing separately |
| Edge/access constrained | J1 USB-C, J30 SD, U30 antenna, SW1–SW4, J2/J60 mode/arm, J20/J31 debug | May move only within approved edge/access zones; reserve plug/card/button/tool envelopes, not just courtyard |
| RF exclusion | U30 antenna overhang and manufacturer antenna region | No copper, routes or components in antenna exclusion on any layer; enclosure metal/plastic review; do not rotate module freely |
| Rigid RP regulator cell | U20,L20,C23,C24,C25,R24 reference relation | Preserve geometry and orientation as a cluster; derive regulator copper from reference; no generic autofix |
| Pin-constrained RP support | C26–C39 per the proposed pin map; Y20/R21/C21/C22; U21/C20; R22/R23 | Relative/local movement only; short power loops, crystal/QSPI/USB lengths and return paths dominate cosmetic alignment |
| Power-loop constrained | U5,L1,C7,C8,new AVIN bypass,R7,R8,C9; U8/C100–102/R100–104; U9; U4/C6/R14; U6/C4/C5 | Optimise each validated local cell as a group; constrain SW area, input/output loop, feedback/VOS, thermal ground and sense traces |
| USB topology constrained | J1,D2,U1,U2,R22/R23,R30/R31 plus CC D3/U3 | Preserve pair topology, ESD at entry, source series resistors and short switch branches; no long unused stubs or reference discontinuities |
| Bus flow constrained | J40 → receiver bank → LB/LI/LC/LF → byte-data buffers → J40 | Place from signal flow; constrain XRDY/AS/address path and OE/reset fanout; keep bus-facing stages near contacts, not a decorative column |
| Logic clusters | LA safe qualification; LB decode; LC lane/wait; LI inversion; LF state | Move within functional regions; gate reassignment within a package allowed only with checked pin-map update |
| Locally movable | Bias/pull arrays, corresponding bypasses, noncritical reset parts | Move with owning IC/connector, not toward a shared 3V3 centroid; no globally free decoupling capacitors |
| Freely movable presentation | Reference labels, documentation text outside restricted areas | Optimise last; cannot justify moving electrically critical components |

[Espressif layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html) supports an uninterrupted ground layer and antenna clearance. The existing keepout must also be checked against the final housing; a PCB-only keepout does not establish an RF-safe enclosure.

Acceptance metrics for an optimiser: unchanged pin-net membership and safety equations; no hard-region violations; short local supply/ground loops; timing-path wire/load limits; critical pair continuity; accessible connectors; a target of all-top SMD assembly; no new DRC conflicts; and actual routing feasibility. Group membership alone is not an electrical constraint. Native footprint locks alone are also insufficient for this MCP's generic autofix, which has previously ignored them. Do not run the old construction/placement scripts over a manually approved layout.

## 7. Recommended implementation order — only after approval

1. Freeze an analysed baseline and correct stale generator metadata in a new candidate. Resolve passive ratings/MPNs and the U7/U5 bypass and RP DVDD ownership findings before placement optimisation.
2. Implement R-A/R-B and I1, then I2. Re-run exact net comparisons, truth tables, safety-state tests, power-domain review and timing allocation after each circuit change. Do not re-use results for a different netlist.
3. Qualify I3/I4 specifically for main-domain shutdown behaviour, reset/clear recovery and byte-driver races; implement only after those conditions close. Otherwise use the 162-component staged target.
4. Keep U7/U79 and the eight bus buffers. Compare I5 only if connector-side placement supports it; normally retain U82/U85 rather than adopting I6.
5. Select the concrete four-layer stackup. Establish hard mechanical constraints and electrical clusters, explicitly assign each bypass to a power pin, then compare floorplans/routability and whether C42/C43 can move to the top.
6. Route/reference-review RP regulator, buck, crystal/QSPI, USB and fast bus control first; ordinary routing follows with critical copper preserved. Native ERC/DRC, net read-back and visual inspection are all required. Prototype timing/power tests belong after the resulting design exists; no repeat USB feasibility experiment is needed now.

**Review ends here. No replacement part, wiring, placement or routing has been implemented.**
