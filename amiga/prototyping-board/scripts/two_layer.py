#!/usr/bin/env python3
"""Prepare a two-layer routing candidate, preserving the released placement.

Output directory is explicit; this does not replace the fabrication release.
"""
import argparse
import re
import shutil
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
POWER = {'+5V', '-5V', '+12V', '-12V', 'GND'}


def v(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


def track(b, net, start, end, layer):
    t = p.PCB_TRACK(b); t.SetStart(start); t.SetEnd(end); t.SetLayer(layer)
    t.SetNetCode(net.GetNetCode())
    t.SetWidth(p.FromMM(.6 if net.GetNetname() in POWER else .3)); b.Add(t)


def setup(b):
    """Replace copper only with the reviewed two-layer routing seeds."""
    for t in [b.Tracks()[i].Cast() for i in range(len(b.Tracks()))]:
        b.Remove(t); t.thisown = False
    for z in list(b.Zones()):
        b.Remove(z); z.thisown = False
    b.SetCopperLayerCount(2)
    for fp in b.GetFootprints():
        pads = list(fp.Pads())
        if fp.GetReference() == 'J1':
            for pad in pads:
                layer = p.F_Cu if pad.IsOnLayer(p.F_Cu) else p.B_Cu
                end = v(p.ToMM(pad.GetPosition().x), 118.5)
                track(b, pad, pad.GetPosition(), end, layer)
        else:
            # Preserve short direct duplicate-header links; no seed vias.
            for i, a in enumerate(pads):
                for c in pads[i+1:]:
                    if a.GetNetname() == c.GetNetname() and a.GetPosition().y == c.GetPosition().y:
                        track(b, a, a.GetPosition(), c.GetPosition(), p.F_Cu)
    # Keep every via out of the mating tongue, including router-created vias.
    keep = p.ZONE(b); keep.SetIsRuleArea(True)
    ls=p.LSET(); ls.AddLayer(p.F_Cu); ls.AddLayer(p.B_Cu); keep.SetLayerSet(ls)
    keep.SetDoNotAllowVias(True); keep.SetDoNotAllowTracks(False)
    keep.SetDoNotAllowPads(False); keep.SetDoNotAllowZoneFills(True)
    keep.Outline().NewOutline()
    for x,y in [(19,119.5),(201,119.5),(201,129),(19,129)]:
        keep.Outline().Append(p.FromMM(x),p.FromMM(y))
    b.Add(keep)


def export_dsn(b, dsn):
    p.ExportSpecctraDSN(b,str(dsn))
    text=dsn.read_text()
    text=text.replace('    (boundary\n', '''    (autoroute_settings
      (layer_rule F.Cu (active on) (preferred_direction vertical))
      (layer_rule B.Cu (active on) (preferred_direction horizontal))
    )
    (boundary
''')
    # Override width for supply/ground nets without reducing default clearance.
    match=re.search(r'    \(class kicad_default ([\s\S]*?)\n      \(circuit',text)
    assert match
    nets=match.group(1).split()
    rest=' '.join(n for n in nets if n not in POWER)
    text=text[:match.start(1)]+rest+text[match.end(1):]
    via=re.search(r'\(use_via ("[^"]+")\)',text).group(1)
    newclass=f'    (class power '+ ' '.join(sorted(POWER))+f' (circuit (use_via {via})) (rule (width 600) (clearance 200)))\n'
    text=text.replace('  )\n  (wiring\n',newclass+'  )\n  (wiring\n')
    assert '(via_keepout' in text, 'KiCad must export the tongue via keepout'
    dsn.write_text(text)


def prepare(source, output):
    output.mkdir(parents=True, exist_ok=True)
    b=p.LoadBoard(str(source)); setup(b)
    pcb=output/'zorro-breakout.kicad_pcb'; p.SaveBoard(str(pcb),b)
    for name in ('zorro-breakout.kicad_pro','zorro-breakout.kicad_sch','fp-lib-table'):
        if (output/name).resolve() != (ROOT/'kicad'/name).resolve():
            shutil.copyfile(ROOT/'kicad'/name,output/name)
    if output.resolve() != (ROOT/'kicad').resolve():
        shutil.copytree(ROOT/'kicad/ZorroBreakout.pretty',output/'ZorroBreakout.pretty',dirs_exist_ok=True)
    export_dsn(b,output/'zorro-breakout.dsn')
    print(pcb)


if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('output',type=Path)
    ap.add_argument('--source',type=Path,default=ROOT/'kicad/zorro-breakout.kicad_pcb')
    args=ap.parse_args(); prepare(args.source,args.output)
