"""Geometry-based local bypass placement constraints; read-only native KiCad.

Outputs MCP moves, never CAD. Each capacitor is assigned to its actual load,
not to the global 3V3 centroid. Candidate locations must clear pad/body bounds.
The final KiCad DRC remains authoritative.
"""
from pathlib import Path
import json,math,pcbnew as k
ROOT=Path(__file__).resolve().parent
b=k.LoadBoard(str(ROOT/'integrated-a500-r4.kicad_pcb'))
fs={f.GetReference():f for f in b.GetFootprints()}
pairs={f'C{70+i}':f'U{61+i}' for i in range(23)}
pairs.update(C60='U60',C93='U84',C94='U85',C95='U86')
def mm(p):return k.ToMM(p.x),k.ToMM(p.y)
def bbox(f):
 items=[x for x in f.GraphicalItems() if x.GetLayer()==k.F_CrtYd]
 if not items:items=list(f.Pads())
 boxes=[i.GetBoundingBox() for i in items]
 return (min(k.ToMM(x.GetX()) for x in boxes),min(k.ToMM(x.GetY()) for x in boxes),max(k.ToMM(x.GetRight()) for x in boxes),max(k.ToMM(x.GetBottom()) for x in boxes))
def overlap(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
occupied={r:bbox(f) for r,f in fs.items() if r not in pairs}
moves=[];unplaced=[]
for cap,ic in pairs.items():
 f=fs[ic];power=[mm(p.GetPosition()) for p in f.Pads() if str(p.GetNetname())=='/3V3'];assert power,ic
 capf=fs[cap];cx,cy=mm(capf.GetPosition());bb=bbox(capf);ox0,oy0,ox1,oy1=bb[0]-cx,bb[1]-cy,bb[2]-cx,bb[3]-cy
 options=[]
 for px,py in power:
  for radius in [2,2.5,3,3.5,4,4.5,5]:
   for angle in range(0,360,15):
    x=round(px+radius*math.cos(math.radians(angle)),3);y=round(py+radius*math.sin(math.radians(angle)),3)
    q=(x+ox0-.15,y+oy0-.15,x+ox1+.15,y+oy1+.15)
    if q[0]<.5 or q[1]<.5 or q[2]>104.5 or q[3]>123.5:continue
    if any(overlap(q,z) for z in occupied.values()):continue
    options.append((radius+.001*math.hypot(x-cx,y-cy),x,y,q))
 if not options:
  unplaced.append({'cap':cap,'ic':ic});occupied[cap]=bb;continue
 _,x,y,q=min(options);occupied[cap]=q
 moves.append({'reference':cap,'x_mm':x,'y_mm':y,'load':ic,'max_power_pad_center_distance_mm':5})
out={'moves':moves,'unplaced':unplaced};(ROOT/'review/bypass-placement.json').write_text(json.dumps(out,indent=2)+'\n');print('Local bypass locations',len(moves),'unplaced',unplaced)
assert not unplaced
