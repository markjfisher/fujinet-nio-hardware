# R3 component selection status

This is a circuit BOM review, not an orderable manufacturing BOM. Assigned
library footprints do not by themselves qualify a purchasable part.

| References | Selection | Status / remaining work |
| --- | --- | --- |
| U8 | TPS259630DDAR | Implemented; pin map and PowerPAD footprint inspected; thermal copper and fault transients remain |
| U9 | LM66100DCKR | Implemented; DCK six-pin map checked; reverse-blocking connection follows TI |
| D3 | TPD2E2U06DCKR | Implemented; three-pin DCK map checked; CC shunt ESD only |
| R100–R104 | 24.9k, 10k, 37.4k, 10k, 681 ohm; 0.1% | Tolerance used in limits; final manufacturer series/TCR required |
| C100–C102 | 1uF/25V X7R, 10nF/25V C0G, 1uF/10V X7R | Values implemented; final MPN and effective capacitance required |
| J40 | WING TAT ED86BGFBK, owner-identified fitted part | Preferred horizontal sidecar reference; tail forming/contact mapping/case fit unresolved, footprint deliberately unassigned |
| L1 | Coilcraft XAL4020-222MEC candidate | Manufacturer 2.2uH part identified; not yet assigned to CAD pending complete buck qualification |
| J1 | GCT USB4105-GF-A candidate | Manufacturer drawing located; pad map/stake variant and enclosure position still to reconcile |
| J30 | Hirose DM3 family under review | Need selected switch/shield contact numbering, not just mechanical similarity |
| Remaining ICs/passives | Inherited R2 circuit selections | Package and orderable BOM audit remains; existing footprint fields are provisional |

[Coilcraft's manufacturer table](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal40xx/)
identifies XAL4020-222MEC as 2.2uH, 38.7 milliohm maximum DCR at 25°C,
5.6A typical saturation current (30% inductance drop) and 4.0A reference RMS
current for 20°C rise. These are not guaranteed in-circuit temperature ratings.
The searched library contains `Inductor_SMD:L_Coilcraft_XAL4020-XXX`.
Do not substitute an assumed XAL4030-222 part: the table's 2.2uH device is XAL4020.
The [GCT drawing](https://gct.co/files/drawings/usb4105.pdf) is the source for
USB socket qualification. Neither candidate is a purchasing instruction.

Next BOM work: effective buck input/output capacitance at applied voltage;
inductor ripple and saturation over temperature; RP core regulator reference
layout; exact IC packages and USB/microSD contact maps; switch/header mechanics.
All must be reconciled before complete PCB import and placement.
