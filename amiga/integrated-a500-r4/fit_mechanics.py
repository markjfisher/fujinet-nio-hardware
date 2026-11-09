"""Geometry-derived MCP move plan for the owner's adapter measurements.

Read-only native KiCad; no CAD serialization. Re-runnable: derive translation
from U20's absolute target, then apply fixture positions absolutely.
"""
import json,pcbnew as k
from pathlib import Path
ROOT=Path(__file__).resolve().parent
b=k.LoadBoard(str(ROOT/'integrated-a500-r4.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()}
m=json.loads((ROOT/'mechanical.json').read_text());target_x=60+m['reference_cell_translation_mm'][0]
dx=target_x-k.ToMM(fs['U20'].GetPosition().x)
moves={}
for ref,f in fs.items():
 if ref=='J40':continue
 moves[ref]={'reference':ref,'x_mm':round(k.ToMM(f.GetPosition().x)+dx,6),'y_mm':round(k.ToMM(f.GetPosition().y),6)}
for ref,x,y in [('H1',18,7),('H2',83.5,7),('H3',83.5,117),('H4',-2.5,117)]+[(f'SW{i+1}',41.5+10*i,113) for i in range(4)]:
 moves[ref]={'reference':ref,'x_mm':x,'y_mm':y}
(ROOT/'review/mechanical-moves.json').write_text(json.dumps({'moves':list(moves.values())},indent=2)+'\n')
print('Mechanical move plan',len(moves),'footprints; electronics translation',dx,'mm')
