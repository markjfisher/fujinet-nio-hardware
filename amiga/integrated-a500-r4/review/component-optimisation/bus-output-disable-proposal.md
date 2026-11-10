# A500 R4 — implemented USB power and bus-output protection

2026-11-10. Supersedes revision 3 and the rejected TPS2121 proposal. The user
approved independent 3V3_BUS supervision and incremental implementation.
Native schematic is authoritative; see ../../phase1/ for exported verification.

| Requirement | Implemented circuit | Qualification |
|---|---|---|
| USB powers the complete board | Existing J1/U8/U9/U4/U5 path retained; main 3V3 has no Amiga feed | Existing 1.2 A main-rail allocation; USB must advertise sufficient current |
| Limited host-interface supply | AMIGA_5V → U95 TPS2553DBVR → D4 SS14-13-F → U96 AP2112K-3.3TRG1 → 3V3_BUS | R110 133 kΩ 1%: 173.7–233.9 mA sustained limit; interface allocation ≤100 mA |
| Qualify every output-related rail | U60/U90/U91 MIC2790H-04VD6-TR sense host 5 V, main 3V3 and 3V3_BUS independently | All powered from held-up 3V3_BUS; open-drain resets share GUARD_OK_RAW |
| Hardware override | U92 SN74LVC2G14DBVR generates BUS_DISABLE and BUS_PERMIT | Slow reset release enters a Schmitt input; permit has a 10 kΩ ground bias |
| Disable data outputs | U44–U47 spare /OE pin 19 takes BUS_DISABLE | Existing byte enables remain; U44/U45 and C54/C55 move electrically to 3V3_BUS |
| Disable XRDY/IRQ | U93 SN74LVC2G132DCUR gates requests with BUS_PERMIT; U94 SN74LVC2G125DCUR drives GND or high impedance | Removes U81/U83 and their bypass capacitors; output never drives high |
| Reset on powered-host fault | Q5 MMBT3904-7-F sinks RP_RUN through open collector; 22 kΩ base drive, 100 kΩ base bias | Host-off leaves RP_RUN free for USB-only flashing |

## Exact supervisor and hold-up changes

MIC2790H pins: 1=/RESET, 2=GND, 3=/MR tied to its supply,
4=CT, 5=SNS, 6=3V3_BUS. Three **open-drain** outputs combine directly;
there is no push-pull output conflict and no cascade of reset-release timers.
R116=10 kΩ pulls GUARD_OK_RAW to 3V3_BUS. Each supervisor has a 1 µF local
bypass and 100 pF C0G ±5% CT capacitor (C114–116).

U60 divider R60/R61=102 kΩ/10 kΩ, both 0.1%, nominal trip 4.48 V.
U90 R112/R113 and U91 R114/R115=67.5 kΩ/10 kΩ, both 0.1%, nominal trip
3.10 V. Including 1% threshold, resistor tolerances and 15 nA bias gives
3.06265–3.13747 V. Release includes hysteresis and approximately
0.43–1.89 ms CT delay with capacitor tolerance; all three must release.
Unused U5 PG is explicitly NC; R9 is removed.

C113=100 µF on 3V3_BUS and C117=220 µF on main 3V3: polarized polymer,
6.3 V, ±20%, **effective capacitance ≥80% nominal and ESR ≤50 mΩ**.
C111/C112=1 µF at AP2112 input/output; C110=100 nF limiter input.
D4 isolates local stored energy from host collapse; R111=4.7 kΩ bleeds
3V3_BUS. The capacitor package is provisional: exact procurement parts,
ESR over temperature and effective capacitance must be locked before layout.

At the supervisor's specified 5% overdrive, minimum sense-equivalent voltage
is 2.90952 V. Allocate 3 µs for detection, shared reset discharge and output
disabling (MIC maximum 2.2 µs under its stated overdrive conditions;
GUARD_OK_RAW total capacitance ≤50 pF). With ESR step and capacitive discharge,
main 3V3 at ≤1.2 A remains ≥2.829 V and 3V3_BUS at ≤0.30 A remains ≥2.883 V.
The latter includes margin beyond the ≤100 mA normal interface allocation.
These exceed the **2.7 V shutdown floor**. They are bounded calculations,
not measured guarantees for an instantaneous hard short or arbitrary load.
Normal bus timing remains qualified at 3.0–3.6 V; a brownout can abort a cycle.

## Required input conditioning retained within this implementation

U7 becomes SN74LVC1G14DBVR on 3V3_AON, with C123=100 nF.
C124=100 nF locally bypasses U5 AVIN on 5V_MAIN.
U97/U98/U100 are 74LVC3G17DC,125 with C125/C126/C128=100 nF:
respectively RP_RUN/RUN_MODE/BUS_ARM; BUS_READY/DATA_DRIVE/ACK_REQ;
and host RESET/BERR/receive-only DTACK. U99 SN74LVC1G17DBVR plus C127
conditions IRQ_REQ. These address previously identified released inputs;
address and AS assertion paths receive no extra Schmitt buffer.
The RP's physical RUN pin and independent boot/reset controls remain intact.

## Power-state behaviour

| Host | Main USB rail | Local bus rail | Hardware result |
|---|---|---|---|
| Off | On | Off | Host-facing drivers unpowered; Ioff-rated paths, permit biased low; USB flashing available |
| On | Off/brownout | Valid | Main supervisor asserts; data disabled, XRDY/IRQ high impedance, RP reset held |
| Falling/brownout | On | Held up | Host supervisor asserts before local output logic loses qualification |
| On | On | Brownout | New U91 asserts the same override; local hold-up supplies its response interval |
| Valid | Valid | Valid | Permission only after supervisor release; existing reset/mode/firmware/cycle interlocks still apply |

The stock A500 allows 300 mA total on its expansion +5 V pins. Limiter maximum
plus sense/quiescent currents fits that allowance; it does not establish an
instantaneous peak ceiling. No main CPU current is taken from the host.
The USB main load allocation remains unchanged.

## Essential prototype validation

1. Scope all three rails, GUARD_OK_RAW, BUS_DISABLE, representative data OE,
   XRDY and IRQ during slow ramps, brownouts and removal of either source.
   Verify actual capacitance/load envelope and ≤3 µs shutdown at the specified
   overdrive; measure output high impedance before the 2.7 V floor.
2. Check host-limiter startup/current/thermal behaviour, local-rail discharge,
   no backfeed, and USB startup/inrush with the added 220 µF.
3. Check reset release, firmware re-arm, byte turnaround and XRDY assertion
   against the 60 ns contract. Retain DATA_DRIVE→ACK ≥100 ns and AS→DATA ≥60 ns.
   Conditioning adds up to 7.1 ns to the affected request/control paths.

Placement/routing, exact bulk-capacitor selection and these measurements are
required before fabrication approval. They do not require repeating accepted
USB communication/ROM flashing feasibility experiments.

## Manufacturer evidence

- [Microchip MIC2790/1/3](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MIC2790-1-3-Supervisor-with-High-Accuracy-Ultra-Fast-Propagation-Delay-and-Capacitor-Programmable-Reset-Delay-DS20007151.pdf): open-drain order code, pinout, thresholds, bias, response conditions and CT timing.
- [TI TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf): Table 9-2 current limit and startup behaviour.
- [Diodes AP2112](https://www.diodes.com/assets/Datasheets/AP2112.pdf): accuracy, bypass/stability and discharge behaviour.
- [TI SN74LVC2G14](https://www.ti.com/lit/ds/symlink/sn74lvc2g14.pdf), [SN74LVC2G132](https://www.ti.com/lit/ds/symlink/sn74lvc2g132.pdf), [SN74LVC2G125](https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf): pin maps, Schmitt inputs where specified, partial-power limits and delays.
- [TI SN74LVC541A](https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf): output-enable truth table, 2.7 V electrical limits and Ioff.
- [Nexperia 74LVC3G17](https://assets.nexperia.com/documents/data-sheet/74LVC3G17.pdf): Schmitt inputs, 5 V tolerance, Ioff and 7.1 ns maximum at 3.0–3.6 V/50 pF/full temperature.
- [Commodore manual, printed page 227](https://support.retrorewind.ca/media/commodore/amiga/commodore_a500-a2000_technical_reference_manual.pdf#page=233): expansion-port current allowance.
