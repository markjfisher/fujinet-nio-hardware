#!/usr/bin/env python3
"""Import the checked-in Specctra session into the generated placement board."""
from pathlib import Path
import json
import subprocess
import tempfile
import pcbnew as p
root=Path(__file__).resolve().parents[1]
path=root/'kicad/zorro-breakout.kicad_pcb'
b=p.LoadBoard(str(path))
if not p.ImportSpecctraSES(b,str(root/'routing/zorro-breakout.ses')):
    raise SystemExit('Specctra session import failed')
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
print(f'Imported routing, removed {count} redundant copper objects, and filled the ground plane.')
