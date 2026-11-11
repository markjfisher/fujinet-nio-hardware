# R5 PWR / NET / DISK — visual review candidate

Open `candidate/integrated-a500-r5.kicad_pro`. Review `closeup.png`, `context.png`
and `schematic-closeup.png`. **Nothing transferred to authoritative R5.**
This candidate starts from the pending service-placement candidate and retains
its geometry; that does not imply approval of the service placement. No routing.

| Requirement | Implementation | Evidence / remaining check |
|---|---|---|
| PWR | Main USB-powered 3V3 → R130 → LED anode; cathode to GND | Actual whole-net readback; indicates rail presence, not power-good or bus permission |
| NET | GPIO4 / U30 pad 4 → R131 → LED | Previously NC; active high; firmware assignment required |
| DISK | GPIO5 / U30 pad 5 → R132 → LED | Previously NC; independent output for future disk activity |
| Onboard or case LED | D130–D132 OR J130–J132 with wired LED; one shared resistor/channel | Alternative assemblies in `assembly.csv`; never populate/use both LED loads in one channel |
| Reset state | R133/R134 = 100k GPIO-to-GND | Holds inputs low while high-impedance; firmware initializes output LOW before enabling it |
| Preserve layout | 11 added footprints; all 203 existing positions/locks/groups untouched | 202 existing footprints exact; U30 changes only pad 4/5 net assignments |

## GPIO and component selection

Actual R5 netlist: module **ESP32-S3-WROOM-1-N16R8**. Pads 4 and 5 were explicitly
unused; they map to GPIO4/5. Existing SD uses GPIO9–12, USB uses 19/20,
VBUS-valid uses 21, service UART uses 43/44; straps and debug connections remain
unchanged. GPIO4/5 are not strapping pins, memory pins or the fixed USB pins.
The N16R8 memory reservation of GPIO35–37 is avoided. No combined NET/DISK
indicator is necessary. This is a hardware allocation; firmware was not changed.

[Espressif module datasheet v1.8](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf),
pin definitions, module variants, boot configuration and DC characteristics,
supports this allocation. Its 40 mA source-current entry is **typical** at the
stated 3.3 V / drive-strength conditions, not a universal guaranteed maximum.
Our resistor bounds even a shorted LED branch to under 3.64 mA at 3.6 V.

Exact orderable parts are in `assembly.csv`:

- D130/D131: [Kingbright APT1608SGC](https://www.kingbrightusa.com/images/catalog/spec/apt1608sgc.pdf), green, 1.6 × 0.8 mm.
- D132: [Kingbright APT1608SYCK](https://www.kingbrightusa.com/images/catalog/spec/apt1608syck.pdf), yellow, same package.
- R130–R132: [YAGEO RC0603FR-071KL](https://www.yageogroup.com/component-documentation/download/specsheet/RC0603FR-071KL), 1k, 1%, 0.1 W.
- R133/R134: [YAGEO RC0603FR-07100KL](https://www.yageogroup.com/component-documentation/download/specsheet/RC0603FR-07100KL), 100k, 1%, 0.1 W.
- J130–J132: [Würth 61300211121](https://www.we-online.com/components/products/datasheet/61300211121.pdf), vertical 2-pin, 2.54 mm pitch.

LED and resistor 0603 footprint body/terminal sizes match the selected packages;
LED pad 1 is cathode, pad 2 anode. Header pitch/body match the 5.08 × 2.54 mm
part. KiCad's 1.0 mm drill lies within the header drawing's 1.10 ±0.15 mm hole
recommendation; include finished-hole tolerance in fabrication checks. Header
height is about 8.54 mm above PCB before adding a mating housing/cable.

At 3.3 V, nominal LED current is approximately 1–2 mA, dependent on actual Vf.
The quoted green/yellow Vf values are characterized at 20 mA, so brightness at
this lower current is a **prototype check**, particularly through a light pipe.
At a conservative 3.6 V and 990 ohms, current is bounded by 3.64 mA even with
zero LED drop, and resistor power by 13.1 mW. Allow **11 mA extra main-rail load**
for all three branches plus pull-downs; typical load should be considerably less.
No Amiga-power or bus-enable circuitry is changed.

## Assembly and enclosure

Choose independently per channel:

1. **PCB LED:** fit the resistor and D13x; leave J13x unpopulated.
2. **Case LED:** fit the resistor and J13x; omit D13x. Connect a passive two-lead
   low-Vf indicator: header pin 1 `+` to anode, pin 2 `-` to cathode/GND.

All alternative footprints stay in the design/netlist. The KiCad BOM without a
variant filter is **not an assembly instruction**; use the FIT/DNP matrix.
Do not fit both loads: they are electrically parallel after one resistor and
would share current unpredictably. No extra GPIO, driver or cable resistor is
needed for a suitable passive LED. Do not connect powered LED modules or apply
external voltage. Use low-current green/yellow/red LEDs compatible with 3.3 V;
blue/white or built-in-resistor panel indicators are not assumed compatible.

Three columns on 5.5 mm centres occupy the upper-left area, outside the antenna
exclusion. Each has header, LED and series resistor; resistor pad 2 aligns with
the LED anode. R133/R134 are a matched pair beside U30's local support area.
Existing approved references are untouched. A/K and +/- markings are explicit.

The 4 × 7 mm top-access envelope per header clears the exact concave U30
courtyard and other components. This is a provisional allowance, not a specified
mating connector. Confirm cable housing/grip, strain relief, header height,
light-pipe clearance and lid geometry during enclosure work. Keep LED leads
short, inside the enclosure, and clear of the antenna, SD access and USB paths.
No board extension was required. Header pad copper also clears the retained
legacy mounting-hole keep-out; its footprint box can still trigger MCP's coarse
keep-out check. No rule area was changed to hide that report.

## Validation and limitations

- Independent netlist comparison preserves every pre-existing connected pin;
  only two unused ESP pads become outputs. All PCB pads match the exported
  netlist, including every LED polarity and external connector connection.
- Native ERC remains at 31 baseline findings; schematic/PCB parity is zero.
- Native DRC has no new clearance, courtyard, silk-overlap or parity findings.
  Four existing J1 hole-clearance errors and intentional U30 library mismatch
  remain. **Eleven new 0.6 mm references** inherit the standing guide's conflict
  with the project's 0.8 mm minimum. They are additional text-height warnings,
  not a clean DRC pass. No exclusions or design rules were changed.
- KiCad reports 199 text-height warnings and 499 unconnected items at its report
  limits. These capped totals must not be used to claim unchanged complete
  finding sets or a complete ratsnest count. `verify.py` compares non-text
  findings and independently checks all actual pad/net memberships.
- MCP audit has no text/pad or text/text overlap. Its U30 overlap reports use a
  bounding rectangle spanning the antenna and module; exact native concave
  courtyard checks pass. Remaining pre-existing coarse reports are retained.
- USB/buffer/connector corridors, antenna exclusion, card access, all prior
  proposed ground-via sites, existing service geometry and groups are preserved.
- 214 PCB footprints (203 + 11); normal assembly adds eight PCB components,
  with the other three option footprints DNP. Case LEDs are off-board items.
- MCP performed schematic construction, wires/labels, new PCB placement and net
  assignments. Supported APIs filled disclosed tool gaps only: two NC removals,
  schematic field/text placement, footprint library/UUID binding and groups.
  No direct S-expression editing, regeneration, routing or global optimisation.

Prototype checks: verify LED polarity/brightness and current in each assembly,
confirm NET/DISK remain off at reset and follow firmware activity, and validate
cable/LED access with the enclosure. Disk semantics and LED pulse stretching are
future firmware work. PWR can be checked independently of firmware.

**Stop for visual approval before transferring this candidate.**
