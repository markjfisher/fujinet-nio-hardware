"""Independent KiCad export/ERC and candidate connectivity checks; no CAD edits."""
import csv
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REVIEW = ROOT / 'review'
SCH = ROOT / 'integrated-r0.kicad_sch'


def run(*args):
    subprocess.run(args, check=True, cwd=ROOT)


def main():
    REVIEW.mkdir(exist_ok=True)
    run('kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml',
        '-o', str(REVIEW / 'netlist.xml'), str(SCH))
    run('kicad-cli', 'sch', 'erc', '--exit-code-violations', '--format', 'json',
        '-o', str(REVIEW / 'erc.json'), str(SCH))
    tree = ET.parse(REVIEW / 'netlist.xml')
    actual = {}
    for net in tree.findall('./nets/net'):
        for node in net.findall('node'):
            key = (node.get('ref'), node.get('pin'))
            assert key not in actual, f'Duplicate pin: {key}'
            actual[key] = net.get('name').removeprefix('/')
    expected = json.loads((ROOT / 'expected-pins.json').read_text())['pins']
    checked = 0
    for ref, pins in expected.items():
        if ref.startswith('#'):
            continue  # KiCad power flags are not physical components.
        for pin, name in pins.items():
            assert actual.get((ref, pin)) == name, (ref, pin, name, actual.get((ref, pin)))
            checked += 1

    # Evaluate the switch topology using independently exported pad nets.
    # TS3USB30E: /OE high isolates; S low chooses pins 2/8, high pins 3/7.
    modes = []
    for rp, esp, wanted in [(0, 0, {'RP', 'ESP'}), (1, 0, {'PC', 'RP'}),
                            (0, 1, {'PC', 'ESP'}), (1, 1, set())]:
        for polarity, common, p1, p2 in [('DP', '4', '2', '3'), ('DM', '6', '8', '7')]:
            graph = {}
            for ref, select, disable in [('U1', rp, esp), ('U2', esp, rp)]:
                if disable:
                    continue
                a, b = actual[ref, common], actual[ref, p2 if select else p1]
                graph.setdefault(a, set()).add(b)
                graph.setdefault(b, set()).add(a)
            pairs = set()
            for a in ['PC', 'RP', 'ESP']:
                seen, todo = set(), [a + '_' + polarity]
                while todo:
                    node = todo.pop()
                    if node not in seen:
                        seen.add(node)
                        todo.extend(graph.get(node, set()) - seen)
                for b in ['PC', 'RP', 'ESP']:
                    if b != a and b + '_' + polarity in seen:
                        pairs.add(tuple(sorted((a, b))))
            required = {tuple(sorted(wanted))} if wanted else set()
            assert pairs == required, (rp, esp, polarity, pairs, required)
        modes.append({'flash_rp': rp, 'flash_esp': esp, 'connected': sorted(wanted)})

    rows = list(csv.DictReader((ROOT / 'rp2350-pin-allocation.csv').open()))
    assert {int(r['package_pad']) for r in rows} == set(range(1, 82))
    gpios = [r for r in rows if r['signal'].startswith('GPIO')]
    assert len(gpios) == 48
    assert len({r['candidate_net'] for r in gpios}) == 48
    for i in range(2, 8):
        assert next(r for r in gpios if r['signal'] == f'GPIO{i}')['candidate_net'] == f'Z_A{i}'
    assert all('SPI' not in r['candidate_net'] for r in gpios)
    run('kicad-cli', 'sch', 'export', 'pdf', '-o', str(REVIEW / 'schematic.pdf'), str(SCH))
    run('kicad-cli', 'sch', 'export', 'svg', '-o', str(REVIEW) + '/', str(SCH))
    # Normalize whitespace in the review export only; never rewrite CAD files.
    svg = REVIEW / 'integrated-r0.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    result = {'scope': 'USB/power/recovery sheet and proposed RP allocation; not whole board',
              'checked_physical_pin_assignments': checked, 'switch_modes': modes,
              'rp_package_pads': len(rows), 'rp_gpio_count': len(gpios),
              'erc_violations': 0, 'pcb': 'not implemented; no DRC/parity claim'}
    (REVIEW / 'checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
