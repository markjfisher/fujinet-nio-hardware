#!/usr/bin/env python3
"""Import the checked-in Specctra session into the generated placement board."""
from pathlib import Path
import argparse
import hashlib
import runpy
import json
import subprocess
import tempfile
import pcbnew as p
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--pcb',type=Path,default=root/'kicad/zorro-breakout.kicad_pcb')
ap.add_argument('--session',type=Path,default=root/'routing/zorro-breakout.ses')
ap.add_argument('--ground-pours',action='store_true')
ap.add_argument('--completion',type=Path)
args=ap.parse_args()
path=args.pcb
completion=args.completion
if completion is None and args.session.resolve()==(root/'routing/zorro-breakout.ses').resolve():
    completion=root/'routing/two-layer-completion.json'
data_completion=json.loads(completion.read_text()) if completion and completion.exists() else None
if data_completion:
    assert hashlib.sha256(args.session.read_bytes()).hexdigest()==data_completion['source_session_sha256'], 'Completion belongs to a different routing session'
b=p.LoadBoard(str(path))
if not p.ImportSpecctraSES(b,str(args.session)):
    raise SystemExit('Specctra session import failed')
if args.ground_pours or b.GetCopperLayerCount()==2:
    assert b.GetCopperLayerCount()==2
    for z in list(b.Zones()):
        if not z.GetIsRuleArea(): b.Remove(z); z.thisown=False
    ground=next(n for n in b.GetNetsByNetcode().values() if n.GetNetname()=='GND')
    for layer in (p.F_Cu,p.B_Cu):
        zone=p.ZONE(b); zone.SetLayer(layer); zone.SetNet(ground)
        zone.SetLocalClearance(p.FromMM(.25));zone.SetThermalReliefGap(p.FromMM(.25))
        zone.SetThermalReliefSpokeWidth(p.FromMM(.5))
        zone.SetMinThickness(p.FromMM(.25))
        zone.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
        zone.Outline().NewOutline()
        for x,y in [(21,21),(199,21),(199,118),(21,118)]:
            zone.Outline().Append(p.FromMM(x),p.FromMM(y))
        b.Add(zone)
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(path),b)
# The autorouter can leave pre-fanout vias and dead-end track stubs. Remove
# ONLY objects KiCad itself identifies as dangling, checking after each pass.
count=0
with tempfile.TemporaryDirectory(prefix='zorro-drc-') as tmp:
    report=Path(tmp)/'drc.json'
    for attempt in range(10):
        subprocess.run(['kicad-cli','pcb','drc',str(path),'--format','json','--severity-all','--output',str(report)],check=True)
        data=json.loads(report.read_text())
        ids={item['uuid'] for violation in data['violations'] if violation['type'] in ['via_dangling','track_dangling'] for item in violation['items']}
        if not ids: break
        removed=0
        for t in [b.Tracks()[i].Cast() for i in range(len(b.Tracks()))]:
            if t.m_Uuid.AsString() in ids:
                if not isinstance(t,p.PCB_TRACK): raise RuntimeError('DRC requested removal of a non-track item')
                b.Remove(t); t.thisown=False; removed+=1
        if removed!=len(ids): raise RuntimeError('Could not resolve all redundant copper objects')
        count+=removed
        p.ZONE_FILLER(b).Fill(b.Zones())
        p.SaveBoard(str(path),b)
    else: raise RuntimeError('Copper cleanup did not converge')
if data_completion:
    digest=runpy.run_path(str(root/'scripts/routing-metrics.py'))['placement_digest']
    assert digest(b)==data_completion['placement_sha256'], 'Completion placement/mapping mismatch'
    layers=(p.F_Cu,p.B_Cu)
    def point(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
    for route in data_completion['routes']:
        net=next(n for n in b.GetNetsByNetcode().values() if n.GetNetname()==route['net'])
        for a,c in zip(route['points'],route['points'][1:]):
            if a[0]!=c[0]:
                assert a[1:]==c[1:]
                t=p.PCB_VIA(b);t.SetPosition(point(*a[1:]));t.SetWidth(p.FromMM(.65))
                t.SetDrill(p.FromMM(.3));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(*layers)
            else:
                t=p.PCB_TRACK(b);t.SetStart(point(*a[1:]));t.SetEnd(point(*c[1:]))
                t.SetLayer(layers[a[0]]);t.SetWidth(p.FromMM(route['width']))
            t.SetNet(net);b.Add(t)
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
print(f'Imported routing, removed {count} redundant copper objects, and filled GND copper.')
