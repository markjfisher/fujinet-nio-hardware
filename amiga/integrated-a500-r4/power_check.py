"""Power allocation/corner calculations and native pin-map assertions."""
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent

def main():
    tree = ET.parse(ROOT / 'review/netlist.xml')
    pins = {(p.get('ref'), p.get('pin')): n.get('name').rsplit('/', 1)[-1]
            for n in tree.findall('./nets/net') for p in n.findall('node')}
    for ref, expected in {
        'U8': {'1':'GND','2':'EFUSE_DVDT','3':'EFUSE_UVLO','4':'VBUS_C',
               '5':'VBUS_LIMITED','6':'EFUSE_FAULT_N','7':'EFUSE_ILM','8':'EFUSE_OVLO','9':'GND'},
        'U9': {'1':'VBUS_LIMITED','2':'GND','3':'VBUS_PROTECTED','5':'GND','6':'VBUS_PROTECTED'},
        'U4': {'1':'VBUS_PROTECTED','2':'GND','3':'POWER_ALLOW','4':'SOFT_START','5':'DISCHARGE','6':'5V_MAIN'},
    }.items():
        for pin, net in expected.items():
            assert pins[ref, pin] == net, (ref, pin, net)
    assert not any(r == 'D1' for r, p in pins)
    assert pins['D2','5'] == 'VBUS_PROTECTED'
    assert [pins['D3',str(i)] for i in [1,2,3]] == ['CC1','CC2','GND']
    values = {c.get('ref'): c.findtext('value') for c in tree.findall('./components/comp')}
    for ref, value in {'R100':'24.9k 0.1%','R101':'10k 0.1%',
                       'R102':'37.4k 0.1%','R103':'10k 0.1%',
                       'R104':'681R 0.1%','C101':'10n 25V C0G'}.items():
        assert values[ref] == value
    # Datasheet-wide current-limit accuracy envelope, plus resistor tolerance.
    limit_min = (0.0112 + 903 / (681 * 1.001)) * (1 - 0.104)
    limit_max = (0.0112 + 903 / (681 * 0.999)) * (1 + 0.104)
    # 85C junction maxima: eFuse .1153, ideal diode .125, load switch .140;
    # add .040 ohm allowance for copper, vias and contacts after the receptacle.
    resistance = 0.1153 + 0.125 + 0.140 + 0.040
    power_in = 3.3 * 1.2 / 0.85
    load_current = (4.5 - math.sqrt(4.5**2 - 4 * resistance * power_in)) / (2 * resistance)
    # Conservative AON/controller/divider allowance, including upstream eFuse IQ.
    current = load_current + 0.005
    assert current < limit_min
    assert limit_max + 0.001 < 1.5
    def divider_range(top, bottom, lo, hi):
        return [lo * (1 + top * .999 / (bottom * 1.001)) - 1e-7 * top * 1.001,
                hi * (1 + top * 1.001 / (bottom * .999)) + 1e-7 * top * 1.001]
    ov = divider_range(37400, 10000, 1.17, 1.22)
    uv = divider_range(24900, 10000, 1.18, 1.22)
    assert ov[0] > 5.5 and ov[1] < 6.0
    assert uv[1] < 4.5
    result = dict(current_limit_A=[limit_min, limit_max], input_budget_A=current,
                  current_margin_A=limit_min-current, ovlo_rising_V=ov,
                  uvlo_rising_V=uv, assessed_input_range_V=[4.5,5.5],
                  assumed_max_junction_C=85, assumed_buck_efficiency=.85,
                  efuse_nominal_ramp_ms=5/(42000/10000),
                  status='allocation checks pass; not transient/thermal or USB compliance qualification')
    (ROOT/'review/power-checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
