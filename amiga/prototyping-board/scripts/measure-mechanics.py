#!/usr/bin/env python3
"""Read-only KiCad connector evidence; never saves or converts the source board.

Usage: python scripts/measure-mechanics.py BOARD REFERENCE
Dimensions are mm in board coordinates, not inferred from a rendered image.
Mask graphics supplement pad expansion: a blanket opening overrides mask dams.
"""
import argparse
import hashlib
import json
from pathlib import Path

import pcbnew as p


def mm(value):
    return round(p.ToMM(value), 6)


def xy(value):
    return [mm(value.x), mm(value.y)]


def shape(item):
    result = {'kind': item.GetShapeStr(), 'layer': item.GetLayerName(),
              'start': xy(item.GetStart()), 'end': xy(item.GetEnd()),
              'stroke': mm(item.GetWidth())}
    if item.GetShape() == p.SHAPE_T_ARC:
        result.update(center=xy(item.GetCenter()), radius=mm(item.GetRadius()))
    if item.GetShape() == p.SHAPE_T_POLY:
        poly = item.GetPolyShape()
        result['outlines'] = [
            [xy(poly.COutline(i).CPoint(j)) for j in range(poly.COutline(i).PointCount())]
            for i in range(poly.OutlineCount())]
    return result


def measure(path, reference):
    board = p.LoadBoard(str(path))
    fp = next(f for f in board.GetFootprints() if f.GetReference() == reference)
    pads = list(fp.Pads())
    result = {'source_name': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'reference': reference, 'value': fp.GetValue(),
              'footprint_library_item': str(fp.GetFPID().GetLibItemName()),
              'pcb_thickness': mm(board.GetDesignSettings().GetBoardThickness()),
              'footprint_position': xy(fp.GetPosition()),
              'footprint_rotation_deg': fp.GetOrientationDegrees(),
              'pads': [], 'board_edge': [], 'board_mask_graphics': [], 'connector_graphics': []}
    for pad in sorted(pads, key=lambda x: int(x.GetNumber())):
        result['pads'].append({'number': pad.GetNumber(), 'position': xy(pad.GetPosition()),
                               'size': xy(pad.GetSize()), 'rotation_deg': pad.GetOrientationDegrees(),
                               'shape_enum': int(pad.GetShape()), 'layers': pad.GetLayerSet().FmtHex(),
                               'front_copper': pad.IsOnLayer(p.F_Cu),
                               'back_copper': pad.IsOnLayer(p.B_Cu),
                               'mask_expansion': mm(pad.GetSolderMaskExpansion(p.F_Mask if pad.IsOnLayer(p.F_Cu) else p.B_Mask))})
    for i in range(len(board.Drawings())):
        item = board.Drawings()[i].Cast()
        if isinstance(item, p.PCB_SHAPE) and item.GetLayer() == p.Edge_Cuts:
            result['board_edge'].append(shape(item))
        if isinstance(item, p.PCB_SHAPE) and item.GetLayer() in [p.F_Mask, p.B_Mask]:
            result['board_mask_graphics'].append(shape(item))
    for i in range(len(fp.GraphicalItems())):
        item = fp.GraphicalItems()[i].Cast()
        if isinstance(item, p.PCB_SHAPE) and item.GetLayer() in [p.F_Mask, p.B_Mask, p.Edge_Cuts]:
            result['connector_graphics'].append(shape(item))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('board', type=Path)
    parser.add_argument('reference')
    args = parser.parse_args()
    print(json.dumps(measure(args.board, args.reference), indent=2))
