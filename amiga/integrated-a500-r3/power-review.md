# R3 protected USB input review

R3 replaces the SS34 power diode with an electronic fuse followed by an ideal
diode. Both the always-on controller supply and main processor supply are
behind these devices. The power source remains USB-C only; Amiga +5V is only
sensed through the existing divider. No RP GPIO changes are required.

| Requirement | Implementation | Evidence | Remaining check |
| --- | --- | --- | --- |
| Limit overload current | U8 TPS259630DDAR, R104=681 ohm 0.1% | Native pins and tolerance calculation | 5V fault transients and thermal layout |
| Reject excessive input voltage | U8 OVLO 37.4k/10k 0.1% divider | 5.533–5.796V rising threshold including leakage | Fast-step overshoot against 6V absolute maximum |
| Reject low input at startup | U8 UVLO 24.9k/10k 0.1% divider | 4.110–4.266V rising threshold | Brownout/system reset response |
| Block reverse VBUS current | U9 LM66100DCKR, CE tied to output | Manufacturer reverse-blocking connection | Transient reverse charge and all powered-off paths |
| Qualify available source current | Existing FUSB303B OUT1/inverter/TPS22917 | Main rail stays off at default current | Live current downgrade timing |
| Protect CC against ESD | D3 TPD2E2U06DCKR, CC1/CC2 to GND | Manufacturer pin table, 5.5V working voltage | Connector placement and system ESD test |
| Data ESD return | D2 VBUS reference moved behind input protection | Native complete-net comparison | Layout and powered-off injection review |

## Selected parts and connections

[TPS2596 data sheet](https://www.ti.com/lit/ds/symlink/tps2596.pdf): U8 is the
**TPS259630** adjustable-OVLO, thermal-latch-off variant. A 10nF C0G capacitor
sets a nominal 4.2mV/us ramp (about 1.19ms to 5V). Thermal overload latches off;
unplug USB to reset it. Short-circuit current response is not instantaneous.
The output is VBUS_LIMITED. Its 1uF local capacitor feeds U9.

[LM66100 data sheet](https://www.ti.com/lit/ds/symlink/lm66100.pdf): U9 VIN is
VBUS_LIMITED, VOUT and CE are VBUS_PROTECTED, GND is ground, unused ST is
connected to ground as TI directs, and NC is unconnected. This replaces D1;
it is not an additional source. The device's 1.5A continuous-current rating
constrains the upstream current limit. Its maximum reverse leakage is finite;
do not describe this as zero leakage.

U8's 8 leads plus thermal pad match the installed TPS2596xx symbol. The
TI_SO-PowerPAD-8 footprint uses pad 9 for the exposed ground pad, a 2.41x3.10mm
copper area and 1.27mm lead pitch. TI's package drawing and separate exposed-pad
drawing were visually checked; thermal via/paste implementation remains a PCB
step. U9 uses the searched SOT-363_SC-70-6 footprint and TI's DCK pin table.

[D3 data sheet](https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf): DCK pins 1/2
connect to CC1/CC2, pin 3 to ground. These are shunt ESD channels, not extra Rd
resistors. FUSB303B retains its internal Rd. This 5V-only design makes no claim
to withstand sustained higher-voltage injection onto CC or USB data.

## Current and thermal allocation

The unchanged 3.3V allocation is 1.2A: ESP 600mA, RP/flash 200mA, SD 200mA,
bus/control 100mA, spare margin 100mA. At 85% assumed buck efficiency this needs
4.659W input. Use 4.5V at the receptacle and 85°C maximum power-device junction
for this calculation. Worst-case resistances used are 115.3mohm eFuse,
125mohm ideal diode, 140mohm main switch, plus 40mohm interconnect allowance.
Solving the constant-power load with those losses, then adding 5mA for AON
and controller overhead, gives **1.166A input**.

TI's broad +/-10.4% limit envelope plus the 0.1% programming resistor gives
**1.197–1.478A**. This leaves about **31mA** above the already margin-inclusive
budget and stays below 1.5A after upstream quiescent/divider allowance. The
margin is small; do not silently add loads. The calculation is in power_check.py
and verifies actual component values and nets from KiCad, not just a separate
spreadsheet. Its maximum-junction assumption is part of the result.

Initial ambient target is 0–40°C. At approximately 1.17A, the small load-switch
and ideal-diode packages each dissipate roughly 0.17–0.19W. TI's reference
thermal resistances imply roughly 32–35°C rise, below the 85°C budget at 40°C
ambient. This estimate is conditional on actual copper and enclosure cooling;
verify it on the PCB. It is not a guaranteed thermal rating.

## Voltage and transient boundaries

The final OVLO divider allows the normal 4.5–5.5V input interval. Its
calculated rising trip is 5.533–5.796V, below the downstream 6V absolute maximum.
This is a fault cutoff, not a claim that the downstream devices operate normally
above their 5.5V recommended range. The earlier 34.8k candidate would reject
some valid USB sources and was discarded before this revision was accepted.
No PD voltage negotiation is implemented.

Static OVLO thresholds do not bound overshoot from a fast faulty supply step.
The eFuse data sheet gives a typical cutoff response, not a complete worst-case
protection proof for our capacitance/source impedance. Do not claim every
9/12/20V fault is safe. Input surge/ESD coordination still needs review before
layout release. Current limiting plus thermal shutdown also needs startup and
short-circuit assessment with the final capacitor BOM.

The FUSB303B data sheet specifies 10–20ms Rp-change detection. The
[TPS22917 data sheet](https://www.ti.com/lit/ds/symlink/tps22917.pdf) lists 10us
typical turn-off. These support the chosen direct hardware disable path, but
adding a maximum to a typical is not a guaranteed system bound. A live-source
current downgrade remains a focused final-circuit qualification, not a repeat
of the accepted RP/ESP USB feasibility tests.

Large ceramic capacitors and both inductors still need final manufacturer
parts and effective-capacitance/saturation verification. No nominal package
size is being treated as proof of DC-bias performance. The previously examined
Murata GRM31CR61A226KE19 parts were not selected as a current BOM recommendation.
