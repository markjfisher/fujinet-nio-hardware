"""Read-only native-geometry reference-label placement; never hides a reference.

All reference text uses 0.9 mm height, 0.15 mm strokes and horizontal reading.
Nearby legal candidates avoid component bodies, pads, silk graphics and labels.
The regular logic cells prefer a shared baseline for IC and bypass references.
"""
from pathlib import Path
import json,math,pcbnew as k
ROOT=Path(__file__).resolve().parent;b=k.LoadBoard(str(ROOT/'integrated-a500-r4.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()};plan=json.loads((ROOT/'review/cluster-plan.json').read_text())
def xy(item):return k.ToMM(item.GetPosition().x),k.ToMM(item.GetPosition().y)
def bb(item):
 q=item.GetBoundingBox();return [k.ToMM(q.GetX()),k.ToMM(q.GetY()),k.ToMM(q.GetRight()),k.ToMM(q.GetBottom())]
def overlaps(a,z,g=.12):return a[0]<z[2]+g and a[2]>z[0]-g and a[1]<z[3]+g and a[3]>z[1]-g
def body(f):
 layer=k.F_Fab if f.GetReference()=='U30' else (k.B_CrtYd if f.GetLayer()==k.B_Cu else k.F_CrtYd)
 items=[s for s in f.GraphicalItems() if s.GetLayer()==layer and hasattr(s,'GetShape')]+list(f.Pads())
 qs=[bb(x) for x in items]
 return [min(q[0] for q in qs),min(q[1] for q in qs),max(q[2] for q in qs),max(q[3] for q in qs)]
obstacles={k.F_Cu:[],k.B_Cu:[]};bodies={r:body(f) for r,f in fs.items()}
for f in fs.values():
 side=f.GetLayer();obstacles[side].append(bodies[f.GetReference()])
 for pad in f.Pads():
  for side in obstacles:
   if pad.IsOnLayer(side):obstacles[side].append(bb(pad))
 for g in f.GraphicalItems():
  if g.GetLayer()==k.F_SilkS:obstacles[k.F_Cu].append(bb(g))
  if g.GetLayer()==k.B_SilkS:obstacles[k.B_Cu].append(bb(g))
for g in b.GetDrawings():
 if g.GetLayer()==k.F_SilkS:obstacles[k.F_Cu].append(bb(g))
 if g.GetLayer()==k.B_SilkS:obstacles[k.B_Cu].append(bb(g))
original={ref:(xy(f.Reference()),k.ToMM(f.Reference().GetTextSize().x),k.ToMM(f.Reference().GetTextThickness()),f.Reference().IsVisible(),f.Reference().GetTextAngle().AsDegrees()) for ref,f in fs.items()}
preferred={}
for ic,cap in plan['bypass_loads'].items():
 x,y=xy(fs[ic]);cx,cy=xy(fs[cap]);preferred[ic]=(x,y-2.9);preferred[cap]=(cx,y-2.9)
options={};offsets={}
for ref,f in fs.items():
 field=f.Reference();field.SetVisible(True);field.SetTextSize(k.VECTOR2I(k.FromMM(.9),k.FromMM(.9)));field.SetTextThickness(k.FromMM(.15));field.SetTextAngle(k.EDA_ANGLE(0,k.DEGREES_T))
 px,py=xy(field);q=bb(field);off=(q[0]-px,q[1]-py,q[2]-px,q[3]-py);offsets[ref]=off
 bx0,by0,bx1,by1=bodies[ref];cx,cy=(bx0+bx1)/2,(by0+by1)/2
 candidates=[]
 if ref in preferred:candidates.append((*preferred[ref],-10))
 for radius in [.25,.75,1.25,1.75,2.25,3.25,4.25,5.25,6.25]:
  for shift in [0,-1.5,1.5,-3,3]:
   cost=radius+abs(shift)*.4
   candidates.extend([(cx+shift,by0-radius-off[3],cost),(cx+shift,by1+radius-off[1],cost+.05),
    (bx0-radius-off[2],cy+shift,cost+.1),(bx1+radius-off[0],cy+shift,cost+.1)])
 legal=[]
 for x,y,cost in candidates:
  rect=(x+off[0],y+off[1],x+off[2],y+off[3])
  if rect[0]<-5.85 or rect[1]<3.65 or rect[2]>104.85 or rect[3]>120.35:continue
  if any(overlaps(rect,z) for z in obstacles[f.GetLayer()]):continue
  legal.append((cost,round(x,4),round(y,4),rect))
 options[ref]=sorted(legal)
 assert legal,('no nearby label candidate',ref)
placed={k.F_Cu:[],k.B_Cu:[]};out=[];failed=[]
# Constrained tiny parts first. Stable reference tie break keeps runs deterministic.
for ref in sorted(options,key=lambda r:(0 if any(v[0]<0 for v in options[r]) else 1,len(options[r]),r)):
 f=fs[ref];side=f.GetLayer()
 choices=[v for v in options[ref] if not any(overlaps(v[3],z,.15) for z in placed[side])]
 if not choices:failed.append(ref);continue
 cost,x,y,rect=choices[0];placed[side].append(rect)
 out.append({'reference':ref,'x_mm':x,'y_mm':y,'visible':True,'silk_size_mm':.9,'silk_thickness_mm':.15,'angle_deg':0,'silk_layer':'B.Silkscreen' if side==k.B_Cu else 'F.Silkscreen'})
assert not failed,('label assignment could not be completed',failed)
updates=[v for v in out if math.hypot(original[v['reference']][0][0]-v['x_mm'],original[v['reference']][0][1]-v['y_mm'])>.0001 or original[v['reference']][1:]!=(.9,.15,True,0.0)]
(ROOT/'review/label-plan.json').write_text(json.dumps({'labels':out,'updates':updates,'hidden':[],'font_mm':.9,'stroke_mm':.15},indent=2)+'\n')
print('Planned',len(out),'visible reference labels at one size; none hidden')
