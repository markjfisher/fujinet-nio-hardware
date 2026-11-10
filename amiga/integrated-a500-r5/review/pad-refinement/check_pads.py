import pcbnew as k,json,math,hashlib,re,sys
from pathlib import Path
r=Path(__file__).resolve().parents[2];out=r/'review/pad-refinement';a=k.LoadBoard(str(out/'before.kicad_pcb'));b=k.LoadBoard(str(r/'integrated-a500-r5.kicad_pcb'));fs=[{f.GetReference():f for f in z.GetFootprints()} for z in [a,b]]
def tree(path):
 ts=iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',Path(path).read_text()))
 def read(t):
  if t=='(':
   r=[]
   for t in ts:
    if t==')':return r
    r.append(read(t))
  try:return float(t)
  except:return t
 return read(next(ts))
def ft(t):return {next(c[2].strip('"') for c in f if isinstance(c,list) and c[:2]==['property','"Reference"']):f for f in t if isinstance(f,list) and f[0]=='footprint'}
ta=tree(str(out/'before.kicad_pcb'));tb=tree(r/'integrated-a500-r5.kicad_pcb');fa,fb=ft(ta),ft(tb)
changed=[x for x in fa if fa[x]!=fb[x]]
allowed={'R22','R23','U21','C20','R20','R13','C34','C35','C36','C28','C29','C39','R21','C30','C31','C38','C33','C32','C26','C37','C27','R24','C25','C23'}
assert set(changed)<=allowed
assert [x for x in ta if not isinstance(x,list) or x[0]!='footprint']==[x for x in tb if not isinstance(x,list) or x[0]!='footprint']
for ref in fs[0]:
 f,g=fs[0][ref],fs[1][ref]
 def ids(z):return (z.m_Uuid.AsString(),z.GetFPIDAsString(),z.GetValue(),z.GetPath().AsString(),z.IsLocked(),z.GetLayer(),sorted((p.m_Uuid.AsString(),p.GetNumber(),p.GetNetname(),p.GetFPRelativePosition().x,p.GetFPRelativePosition().y,p.GetSize().x,p.GetSize().y) for p in z.Pads()))
 assert ids(f)==ids(g),ref
for ref in ['U20','L20','R24','C23','C24','C25']:
 f,g=fs[0][ref],fs[1][ref];assert f.GetPosition()==g.GetPosition() and f.GetOrientationDegrees()==g.GetOrientationDegrees(),ref

def pad(f,n):return next(p for p in f.Pads() if p.GetNumber()==str(n))
def xy(p):return (p.GetPosition().x/1e6,p.GetPosition().y/1e6)
def dist(p,q):return math.dist(xy(p),xy(q))
usbs=[];flash=[]
for d in fs:
 lengths=[dist(pad(d['U20'],pn),pad(d[ref],1)) for ref,pn in [('R22',67),('R23',66)]];usbs.append({'dp_mm':lengths[0],'dm_mm':lengths[1],'difference_mm':abs(lengths[0]-lengths[1])})
 pairs=[(1,75),(2,74),(3,73),(5,72),(6,71),(7,70)];flash.append({str(i):dist(pad(d['U21'],i),pad(d['U20'],j)) for i,j in pairs})
# Confirm every reference regulator pad against actual manufacturer's downloadable cell.
src=Path(sys.argv[1]);refboard=k.LoadBoard(str(src));reference=[]
for original,ours in [('L1','L20'),('C6','C24'),('C7','C25'),('C9','C23'),('R3','R24')]:
 f=refboard.FindFootprintByReference(original);g=fs[1][ours]
 for p in f.Pads():
  n=p.GetNumber();target=str(3-int(n)) if ours=='L20' else n;q=pad(g,target);x,y=xy(p);xx,yy=xy(q);assert abs(xx-(x-57))<1e-5 and abs(yy-(y-41.45))<1e-5
  reference.append({'source':original+'.'+n,'source_net':p.GetNetname(),'r5':ours+'.'+target,'r5_net':q.GetNetname(),'pad_translation_mm':[-57,-41.45]})
# Concrete future GND-via sites. No board mutation, via creation, or routing.
sites={'C20':(31.5,39.6),'C23':(47.7,54.25),'C24':(46.3,54.1),'C25':(46.3,52.9)}
for c,y in [('C26',57.8),('C37',59.8),('C27',61.8)]:sites[c]=(32.8,y)
for c,y in [('C32',55.4),('C33',57.5),('C38',59.6),('C31',61.7),('C30',63.8)]:sites[c]=(51.7,y)
for c,x in [('C28',39.4),('C29',41.4),('C39',43.8)]:sites[c]=(x,69.7)
for c,x in [('C34',42),('C35',40),('C36',38)]:sites[c]=(x,50.75)
checks=[]
for ref,(x,y) in sites.items():
 candidates=[]
 for f in b.GetFootprints():
  for p in f.Pads():
   if p.GetNetname()=='/GND':continue
   q=p.GetBoundingBox();left,right=q.GetX()/1e6,q.GetRight()/1e6;top,bottom=q.GetY()/1e6,q.GetBottom()/1e6
   dx=max(left-x,0,x-right);dy=max(top-y,0,y-bottom)
   candidates.append((math.hypot(dx,dy)-0.3,f.GetReference()+'.'+p.GetNumber()))
 minimum,nearest=min(candidates);checks.append({'capacitor':ref,'via_xy_mm':[x,y],'diameter_mm':0.6,'drill_mm':0.3,'minimum_foreign_pad_clearance_mm':minimum,'nearest_foreign_pad':nearest,'distance_to_gnd_pad_centre_mm':math.dist((x,y),xy(pad(fs[1][ref],2)))})
 assert minimum>=0.125,(ref,minimum,nearest)
for i,u in enumerate(checks):
 for v in checks[:i]:assert math.dist(u['via_xy_mm'],v['via_xy_mm'])>=0.85
# South row exact bbox gaps, using full pad rectangles conservatively.
rows=[]
for ref,pn in [('C28',24),('C29',29),('C39',32)]:
 f=fs[1][ref];q=f.GetCourtyard(k.F_CrtYd).BBox();u=fs[1]['U20'].GetCourtyard(k.F_CrtYd).BBox()
 cp=pad(f,1);up=pad(fs[1]['U20'],pn);assert cp.GetNetname()==up.GetNetname()
 rows.append({'capacitor':ref,'pin':pn,'courtyard_gap_to_u20_mm':(q.GetY()-u.GetBottom())/1e6,'supply_pad_centre_distance_mm':dist(cp,up),'north_copper_to_u20_south_pad_edges_mm':(cp.GetBoundingBox().GetY()-up.GetBoundingBox().GetBottom())/1e6})
result={'modified_refs':changed,'unselected_objects_and_floorplan_unchanged':True,'u20_and_regulator_positions_unchanged':True,'ids_nets_locks_groups_preserved':True,'tracks':len(b.GetTracks()),'usb_before':usbs[0],'usb_after':usbs[1],'flash_before_pad_distances_mm':flash[0],'flash_after_pad_distances_mm':flash[1],'south_row':rows,'regulator_reference_source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'regulator_pad_mapping':reference,'prospective_ground_vias':checks}
(out/'pad-checks.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['regulator_pad_mapping','prospective_ground_vias']},indent=2))
