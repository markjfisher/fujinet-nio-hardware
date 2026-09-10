#!/usr/bin/env python3
"""Check the frozen mechanical-review evidence and extractor against live CAD.

This tests extraction/report arithmetic, not mating fit or fabrication readiness.
External source boards need not be installed: their hashed measurements are
retained in review/mechanics. A later intentional CAD change needs a new review.
"""
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'review/mechanics'
measure = runpy.run_path(str(ROOT / 'scripts/measure-mechanics.py'))['measure']


def close(actual, expected):
    assert abs(actual - expected) < 0.00001, (actual, expected)


def main():
    records = {path.stem: json.loads(path.read_text()) for path in EVIDENCE.glob('*.json')}
    assert set(records) == {'current', 'va2000', 'ripple', 'amigasid', 'eatx'}
    assert measure(ROOT / 'kicad/zorro-breakout.kicad_pcb', 'J1') == records['current']
    for line in (EVIDENCE / 'design-unchanged.sha256').read_text().splitlines():
        digest, relative = line.split(maxsplit=1)
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, relative
    for name, record in records.items():
        pads = record['pads']
        assert [int(p['number']) for p in pads] == list(range(1, 101))
        close(record['pcb_thickness'], 1.6)
        axis = 1 if name == 'eatx' else 0
        positions = sorted({p['position'][axis] for p in pads})
        assert len(positions) == 50
        close(positions[-1] - positions[0], 124.46)
        for a, b in zip(positions, positions[1:]):
            close(b - a, 2.54)
        if name != 'eatx':
            for pad in pads:
                assert pad['front_copper'] == (int(pad['number']) % 2 == 0)
                assert pad['back_copper'] == (int(pad['number']) % 2 == 1)
                close(pad['size'][0], 1.524)
    # Values independently checked in the published copper/outline Gerbers.
    expected = {
        'current': (127.62, 5, 1, 129.26, 0),
        'va2000': (139.573, 5, .040, 127, .2),
        'ripple': (116.28969, 6.754, .955245, 129.235206, 0),
        'amigasid': (134.89, 10, .1016, 130.048, 0),
    }
    for name, (tip, length, setback, width, mask) in expected.items():
        record = records[name]
        for pad in record['pads']:
            close(pad['size'][1], length)
            close(tip - pad['position'][1] - length / 2, setback)
            close(pad['mask_expansion'], mask)
        # Vertical side segments reaching the connector end, not the wider body.
        sides = {edge['start'][0] for edge in record['board_edge']
                 if edge['kind'] == 'Line' and edge['start'][0] == edge['end'][0]
                 and max(edge['start'][1], edge['end'][1]) > tip - 2}
        assert len(sides) == 2
        close(max(sides) - min(sides), width)
    assert {g['layer'] for g in records['ripple']['connector_graphics']} == {'F.Mask', 'B.Mask'}
    assert all(not r['board_mask_graphics'] for r in records.values())
    print('PASS: live extractor, five reference measurements, report arithmetic and unchanged design hashes.')


if __name__ == '__main__':
    main()
