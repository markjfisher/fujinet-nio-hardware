#!/usr/bin/env python3
"""Apply the approved A-5 prototype mechanics without regenerating/rerouting.

Also used by generate.py so explicit regeneration retains the release geometry.
"""
import hashlib
import json
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]


def v(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


def electrical_digest(board):
    """Independent of pad width, outline, mask and zone fill/serialization."""
    pads = sorted((fp.GetReference(), pad.GetNumber(), pad.GetNetname(),
                   pad.GetPosition().x, pad.GetPosition().y,
                   pad.GetLayerSet().FmtHex())
                  for fp in board.GetFootprints() for pad in fp.Pads())
    tracks = []
    for i in range(len(board.Tracks())):
        t = board.Tracks()[i].Cast()
        tracks.append((t.GetClass(), t.GetNetname(), t.GetStart().x,
                       t.GetStart().y, t.GetEnd().x, t.GetEnd().y,
                       int(t.GetLayer()), t.GetWidth(p.F_Cu) if isinstance(t, p.PCB_VIA) else t.GetWidth(),
                       t.GetDrillValue() if isinstance(t, p.PCB_VIA) else 0))
    return hashlib.sha256(json.dumps([pads, sorted(tracks)]).encode()).hexdigest()


def apply(board):
    drawings = [board.Drawings()[i].Cast() for i in range(len(board.Drawings()))]
    for d in drawings:
        if d.GetLayer() == p.Edge_Cuts:
            board.Remove(d)
    # Clockwise closed outline. Arc midpoints define concave R1.5 roots.
    segments = [((20,20),(200,20)), ((200,20),(200,120)),
                ((200,120),(170.76,120)),
                ((169.26,121.5),(169.26,126.12)),
                ((169.26,126.12),(167.76,127.62)),
                ((167.76,127.62),(41.5,127.62)),
                ((41.5,127.62),(40,126.12)),
                ((40,126.12),(40,121.5)),
                ((38.5,120),(20,120)), ((20,120),(20,20))]
    for a, b in segments:
        s = p.PCB_SHAPE(board)
        s.SetShape(p.SHAPE_T_SEGMENT)
        s.SetStart(v(*a)); s.SetEnd(v(*b))
        s.SetLayer(p.Edge_Cuts); s.SetWidth(p.FromMM(.05)); board.Add(s)
    for a, mid, b in [((170.76,120),(169.699339828,120.439339828),(169.26,121.5)),
                      ((40,121.5),(39.560660172,120.439339828),(38.5,120))]:
        s = p.PCB_SHAPE(board)
        s.SetShape(p.SHAPE_T_ARC)
        s.SetArcGeometry(v(*a), v(*mid), v(*b))
        s.SetLayer(p.Edge_Cuts); s.SetWidth(p.FromMM(.05)); board.Add(s)
    fp = next(f for f in board.GetFootprints() if f.GetReference() == 'J1')
    # Edge fingers intentionally share one mask window (not soldered pads).
    fp.SetAllowSolderMaskBridges(True)
    for pad in fp.Pads():
        pad.SetSize(v(1.6,5))
    graphics = [fp.GraphicalItems()[i].Cast() for i in range(len(fp.GraphicalItems()))]
    for g in graphics:
        if g.GetLayer() in (p.F_Mask, p.B_Mask):
            fp.Remove(g)
    for layer in (p.F_Mask, p.B_Mask):
        s = p.PCB_SHAPE(fp)
        s.SetShape(p.SHAPE_T_RECT)
        s.SetStart(v(38,120)); s.SetEnd(v(171.26,128.12))
        s.SetFillMode(p.FILL_T_FILLED_SHAPE); s.SetWidth(0)
        s.SetLayer(layer); fp.Add(s)
    return fp


if __name__ == '__main__':
    path = ROOT / 'kicad/zorro-breakout.kicad_pcb'
    board = p.LoadBoard(str(path))
    before = electrical_digest(board)
    fp = apply(board)
    assert electrical_digest(board) == before, 'Electrical routing/mapping changed'
    copy = p.FOOTPRINT(fp); copy.SetPosition(v(0,0)); copy.SetReference('REF**')
    for pad in copy.Pads():
        pad.SetNetCode(0)
    p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP).FootprintSave(
        str(ROOT / 'kicad/ZorroBreakout.pretty'), copy)
    p.SaveBoard(str(path), board)
    assert electrical_digest(p.LoadBoard(str(path))) == before
    print('Preserved electrical digest:', before)
