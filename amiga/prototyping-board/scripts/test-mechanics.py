#!/usr/bin/env python3
"""Check the frozen mechanical-review evidence and extractor against live CAD.

This tests extraction/report arithmetic, not mating fit or fabrication readiness.
External source boards need not be installed: their hashed measurements are
retained in review/mechanics. A later intentional CAD change needs a new review.
"""
import hashlib
import argparse
import json
from pathlib import Path
import runpy
import pcbnew as p
from mechanics import electrical_digest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'review/mechanics'
measure = runpy.run_path(str(ROOT / 'scripts/measure-mechanics.py'))['measure']
placement_digest = runpy.run_path(str(ROOT / 'scripts/routing-metrics.py'))['placement_digest']


def close(actual, expected):
    assert abs(actual - expected) < 0.00001, (actual, expected)


def main(pcb_path=ROOT / 'kicad/zorro-breakout.kicad_pcb'):
    records = {path.stem: json.loads(path.read_text()) for path in EVIDENCE.glob('*.json')}
    assert set(records) == {'current', 'va2000', 'ripple', 'amigasid', 'eatx'}
    # current.json and design-unchanged.sha256 preserve the PRE-release review.
    # Intentional mechanical changes do not rewrite the historical evidence.
    live = measure(pcb_path, 'J1')
    board = p.LoadBoard(str(pcb_path))
    assert placement_digest(board) == '2b50b0156b9286cdf3ca5ca85dda12a1ade08a2852a383d0d97b9590baa579f2', 'Verified pads/placement/mapping changed'
    if board.GetCopperLayerCount()==4:
        assert electrical_digest(board) == '67610cbc42d6f03976cf59b8a909f560a1fe18d3ae8fde59059cf2d786920dec'
    else:
        assert board.GetCopperLayerCount()==2
        ground=[z for z in board.Zones() if not z.GetIsRuleArea()]
        assert len(ground)==2 and {z.GetLayer() for z in ground}=={p.F_Cu,p.B_Cu}
        assert all(z.GetNetname()=='GND' and z.GetFilledArea()>0 for z in ground)
        assert all(z.GetIslandRemovalMode()==p.ISLAND_REMOVAL_MODE_ALWAYS for z in ground)
        for i in range(len(board.Tracks())):
            t=board.Tracks()[i].Cast()
            if not isinstance(t,p.PCB_VIA):
                assert t.GetLayer() in (p.F_Cu,p.B_Cu)
                assert p.ToMM(t.GetWidth()) >= (.6 if t.GetNetname() in {'GND','+5V','-5V','+12V','-12V'} else .3)-1e-6
    for a, b in zip(live['pads'], records['current']['pads']):
        assert a == dict(b, size=[1.6, 5.0]), 'Only finger width may change'
    arcs = [s for s in live['board_edge'] if s['kind'] == 'Arc']
    assert len(arcs) == 2
    for arc in arcs:
        close(arc['radius'], 1.5)
    assert {tuple(a['center']) for a in arcs} == {(38.5,121.5),(170.76,121.5)}
    lines = {(tuple(s['start']),tuple(s['end'])) for s in live['board_edge'] if s['kind'] == 'Line'}
    assert len(lines) == 10
    for segment in [((169.26,126.12),(167.76,127.62)),
                    ((41.5,127.62),(40,126.12)),
                    ((167.76,127.62),(41.5,127.62)),
                    ((40,126.12),(40,121.5)),
                    ((169.26,121.5),(169.26,126.12))]:
        assert segment in lines
    assert not live['board_mask_graphics']
    assert len(live['connector_graphics']) == 2
    assert {s['layer'] for s in live['connector_graphics']} == {'F.Mask','B.Mask'}
    fp = next(f for f in board.GetFootprints() if f.GetReference() == 'J1')
    assert fp.AllowSolderMaskBridges()
    assert all(not f.AllowSolderMaskBridges() for f in board.GetFootprints() if f.GetReference() != 'J1')
    for i in range(len(fp.GraphicalItems())):
        g = fp.GraphicalItems()[i].Cast()
        if isinstance(g,p.PCB_SHAPE) and g.GetLayer() in (p.F_Mask,p.B_Mask):
            assert g.GetShape() == p.SHAPE_T_RECT
            assert g.GetFillMode() == p.FILL_T_FILLED_SHAPE
            assert [round(p.ToMM(g.GetStart().x),6),round(p.ToMM(g.GetStart().y),6)] == [38,120]
            assert [round(p.ToMM(g.GetEnd().x),6),round(p.ToMM(g.GetEnd().y),6)] == [171.26,128.12]
    for line in (EVIDENCE / 'design-unchanged.sha256').read_text().splitlines():
        digest, relative = line.split(maxsplit=1)
        if relative == 'kicad/zorro-breakout.kicad_pcb':
            continue  # Electrical digest above protects the changed PCB.
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
    print('PASS: A-5 outline, fingers, continuous mask, fixed placement/mapping, routing constraints and five historical datasets.')


if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--pcb',type=Path,default=ROOT/'kicad/zorro-breakout.kicad_pcb')
    main(ap.parse_args().pcb)
