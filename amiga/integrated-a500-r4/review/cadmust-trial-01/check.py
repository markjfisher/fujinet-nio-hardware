"""Read-only independent preservation/geometry/HPWL verification."""
import sys,types,pickle,json,re,hashlib
from pathlib import Path
import pcbnew as k
root=Path(__file__).resolve().parent
selected={'U61','C70','R3','R63','U66','C75','U71','C80','U64','C73'}
def tree(p):
 ts=iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',p.read_text()))
 def read(t):
  if t=='(':
   r=[]
   for t in ts:
    if t==')':return r
    r.append(read(t))
  try:return float(t)
  except:return t
 return read(next(ts))
def fps(t):return {next(c[2] for c in f if isinstance(c,list) and c[:2]==['property','"Reference"']):f for f in t if isinstance(f,list) and f[0]=='footprint'}
def groups(t):return sorted([x for x in t if isinstance(x,list) and x[0]=='group'],key=str)
def bbox(f):
 p=f.GetCourtyard(k.F_CrtYd)
 r=p.BBox() if p.OutlineCount() else f.GetBoundingBox(False,False)
 return [r.GetX()/1e6,r.GetY()/1e6,r.GetRight()/1e6,r.GetBottom()/1e6]
def hit(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-5 and min(a[3],b[3])-max(a[1],b[1])>1e-5
out={}
t0=tree(root/'baseline/integrated-a500-r4.kicad_pcb'); f0=fps(t0)
for label in ['seed','best']:
 p=root/label/'integrated-a500-r4.kicad_pcb';t=tree(p);fs=fps(t); b=k.LoadBoard(str(p)); ff={f.GetReference():f for f in b.GetFootprints()}
 changed=[r for r in f0 if fs[r]!=f0[r] and r.strip('"') not in selected]
 assert not changed,changed
 assert groups(t)==groups(t0)
 assert [x for x in t if isinstance(x,list) and x[0] not in ['footprint','generator_version']]==[x for x in t0 if isinstance(x,list) and x[0] not in ['footprint','generator_version']]
 boxes={r:bbox(f) for r,f in ff.items()}
 overlaps=sorted(set(tuple(sorted([r,s])) for r in selected for s in boxes if s!=r and hit(boxes[r],boxes[s])))
 forbidden=[(-26.75,6,-5.75,54),(87,3.5,105,120.5)]
 keep=[r for r in selected if any(hit(boxes[r],z) for z in forbidden)]
 off=[r for r in selected if boxes[r][0]<-6 or boxes[r][1]<3.5 or boxes[r][2]>105 or boxes[r][3]>120.5]
 locks={r:f.IsLocked() for r,f in ff.items()};orig=k.LoadBoard(str(root/'baseline/integrated-a500-r4.kicad_pcb'))
 assert locks=={f.GetReference():f.IsLocked() for f in orig.GetFootprints()}
 out[label]={'unselected_full_footprint_changes':changed,'all_groups_locks_board_graphics_zones_unchanged':True,'selected_courtyard_overlaps':overlaps,'selected_keepout_violations':keep,'selected_offboard':off,'positions':{r:[ff[r].GetPosition().x/1e6,ff[r].GetPosition().y/1e6,ff[r].GetOrientationDegrees()] for r in sorted(selected)},'tracks':len(b.GetTracks())}
pkg=types.ModuleType('plugin');pkg.__path__=[str(Path(sys.argv[1]).resolve()/'plugin')];sys.modules['plugin']=pkg
for label,name in [('seed','seed.pkl'),('best','post.pkl')]:
 m=pickle.loads((root/name).read_bytes());total=local=0
 for n in m.nets.values():
  # Same exclusions as the completed optimiser run for both stages.
  if n.net_name in ['/GND','/VBUS_C','/VBUS_PROTECTED'] or n.is_excluded or len(n.pad_refs)<2:continue
  pts=[m.footprints[fi].pads[pi].abs_position(m.footprints[fi].x,m.footprints[fi].y,m.footprints[fi].angle_deg) for fi,pi in n.pad_refs]
  h=max(x for x,y in pts)-min(x for x,y in pts)+max(y for x,y in pts)-min(y for x,y in pts)
  total+=h
  if any(m.footprints[fi].reference in selected for fi,pi in n.pad_refs):local+=h
 out[label]['comparable_total_hpwl_mm']=total/1e6;out[label]['selected_incident_hpwl_mm']=local/1e6
(root/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
