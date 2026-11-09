"""Candidate power-cell floorplan following TPS62130 datasheet section 11.2.

Native geometry checks before MCP moves. This is not a routed/qualified
switching loop: the reference requires dedicated VOS sensing and ground paths.
"""
from pathlib import Path
import json,pcbnew as k
ROOT=Path(__file__).resolve().parent;b=k.LoadBoard(str(ROOT/'integrated-a500-r4.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()}
coords={'U5':(30,94,180),'L1':(36,94,270),'C7':(26,93.5,270),'C8':(33,98.2,180),
 'R7':(34.25,89.5,0),'R8':(30.75,89.5,0),'R9':(28,87,0),'C9':(26.5,89.5,0),
 'U4':(21,96.8,0),'C6':(20.5,100,0),'R14':(25,99.9,0),
 'C4':(2.5,75.3,180),'C5':(10.9,75.89,0)}
for ref,(x,y,a) in coords.items():
 f=fs[ref];f.SetOrientationDegrees(a);f.SetPosition(k.VECTOR2I(k.FromMM(x),k.FromMM(y)))
def bbox(f):
 items=[g for g in f.GraphicalItems() if g.GetLayer()==k.F_CrtYd]+list(f.Pads());qs=[i.GetBoundingBox() for i in items]
 return [min(k.ToMM(q.GetX()) for q in qs),min(k.ToMM(q.GetY()) for q in qs),max(k.ToMM(q.GetRight()) for q in qs),max(k.ToMM(q.GetBottom()) for q in qs)]
def overlap(a,z,g=.15):return a[0]<z[2]+g and a[2]>z[0]-g and a[1]<z[3]+g and a[3]>z[1]-g
issues=[]
for ref in coords:
 for other,f in fs.items():
  if ref==other or f.GetLayer()!=k.F_Cu:continue
  if overlap(bbox(fs[ref]),bbox(f)):issues.append((ref,other))
assert not issues,issues
moves=[{'reference':r,'x_mm':v[0],'y_mm':v[1],'rotation_deg':v[2]} for r,v in coords.items()]
(ROOT/'review/power-cell-plan.json').write_text(json.dumps({'moves':moves,'source':'https://www.ti.com/lit/ds/symlink/tps62130.pdf','section':'11.2, Figure 11-1; topology/orientation reference, not copied routing'},indent=2)+'\n')
print('Power-cell geometry:',len(moves),'placements, no courtyard conflicts')
