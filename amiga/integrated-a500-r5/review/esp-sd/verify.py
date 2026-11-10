"""Read-only comparison and corridor/via verification; never writes CAD."""
import pcbnew as k,json,re,math,hashlib
from pathlib import Path
o=Path(__file__).resolve().parent;r=o.parents[1];root=r/'integrated-a500-r5.kicad_pcb';p=o/'candidate/integrated-a500-r5.kicad_pcb';approved=r/'review/usb-mux/candidate/integrated-a500-r5.kicad_pcb'
def tree(p):
 ts=iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',p.read_text()))
 def read(t):
  if t=='(':
   a=[]
   for t in ts:
    if t==')':return a
    a.append(read(t))
  try:return float(t)
  except:return t
 return read(next(ts))
def fps(t):return {next(c[2].strip('"')for c in f if isinstance(c,list)and c[:2]==['property','"Reference"']):f for f in t if isinstance(f,list)and f[0]=='footprint'}
a,c,z=map(tree,[root,p,approved]);fa,fc,fz=map(fps,[a,c,z]);assert fa==fz,'Approved transfer mismatch'
refs=set('U30 J30 C40 C41 C42 C43 R30 R31 R32 R33 R34 R35 R36 R37 R41 R11 R12 C10 Q1 Q4'.split());assert {ref for ref in fa if fa[ref]!=fc[ref]}==refs
import copy
normalized=copy.deepcopy(a)
for item in normalized:
 if isinstance(item,list) and item[0]=='zone' and ['name','"R5 antenna all-layer exclusion"'] in item:
  ko=next(x for x in item if isinstance(x,list)and x[0]=='keepout');field=next(x for x in ko if isinstance(x,list)and x[0]=='footprints');assert field[1]=='not_allowed';field[1]='allowed'
assert [x for x in normalized if not isinstance(x,list)or x[0]not in ['footprint','group']]==[x for x in c if not isinstance(x,list)or x[0]not in ['footprint','group']]
b=k.LoadBoard(str(p));old=k.LoadBoard(str(root));fs={f.GetReference():f for f in b.GetFootprints()}
def identity(f):return(f.m_Uuid.AsString(),f.GetValue(),f.GetFPIDAsString(),f.IsLocked(),f.GetPath().AsString(),sorted((p.m_Uuid.AsString(),p.GetNumber(),p.GetNetname(),p.GetFPRelativePosition().x,p.GetFPRelativePosition().y)for p in f.Pads()))
for f in old.GetFootprints():assert identity(f)==identity(fs[f.GetReference()])
assert len(b.GetTracks())==0 and len(fs)==203
corr=json.loads((r/'review/usb-power/corridor/checks.json').read_text())['corridor_envelopes']
for name,v in corr.items():
 if name.startswith('Future'):continue
 l,t,rr,bt=v['xyxy_mm']
 for f in fs.values():
  q=f.GetCourtyard(k.F_CrtYd).BBox();assert not(min(rr,q.GetRight()/1e6)>max(l,q.GetX()/1e6)and min(bt,q.GetBottom()/1e6)>max(t,q.GetY()/1e6)),(name,f.GetReference())
# Antenna footprint prohibition is replaced with this explicit exception for U30 only.
for f in fs.values():
 q=f.GetCourtyard(k.F_CrtYd).BBox()
 if f.GetReference()!='U30':assert not(q.GetX()/1e6 < -5.75 and q.GetRight()/1e6 > -26.75 and q.GetY()/1e6 <54 and q.GetBottom()/1e6>6),f.GetReference()
 for pad in f.Pads():
  q=pad.GetBoundingBox();assert not(q.GetX()/1e6 < -5.75 and q.GetRight()/1e6 > -26.75 and q.GetY()/1e6<54 and q.GetBottom()/1e6>6),(f.GetReference(),pad.GetNumber())
# Card ejection artwork stays below the antenna exclusion; keep its left approach open.
for item in fs['J30'].GraphicalItems():
 if item.GetLayer()==k.F_Fab and hasattr(item,'GetStart'):
  a1,b1=item.GetStart(),item.GetEnd()
  if min(a1.x,b1.x)<k.FromMM(-6):assert min(a1.y,b1.y)/1e6>=54.575-1e-6
sites=[{'reference':ref,'via_xy_mm':xy}for ref,xy in [('C41',[-3,43.3]),('C40',[-.5,43.3]),('C10',[4.5,43.3]),('C42',[14.7,57.5]),('C43',[14.7,60]),('U30 pin1',[-4.26,40.1]),('U30 pin40',[-4.26,19.9]),('J30 shield',[12.7,65.4])]]
existing=[]
for path in [r/'review/usb-power/verification.json',r/'review/pad-refinement/pad-checks.json',r/'review/usb-mux/verification.json']:existing+=json.loads(path.read_text())['prospective_ground_vias']
for s in sites+existing:
 x,y=s['via_xy_mm'];clear=[]
 for f in fs.values():
  for pad in f.Pads():
   if pad.GetNetname()=='/GND' or not pad.GetNumber():continue
   q=pad.GetBoundingBox();clear.append(math.hypot(max(q.GetX()/1e6-x,0,x-q.GetRight()/1e6),max(q.GetY()/1e6-y,0,y-q.GetBottom()/1e6))-.3)
 minimum=min(clear);assert minimum>=.125,(s,minimum)
 if s in sites:s.update(diameter_mm=.6,drill_mm=.3,minimum_foreign_pad_clearance_mm=minimum)
for i,s in enumerate(sites+existing):
 for t in (sites+existing)[:i]:assert math.dist(s['via_xy_mm'],t['via_xy_mm'])>=.85
metrics=[]
for cap,ic,pin in [('C40','U30','2'),('C41','U30','2'),('C42','J30','4'),('C43','J30','4')]:
 cp=next(p for p in fs[cap].Pads()if p.GetNumber()=='1');ip=next(p for p in fs[ic].Pads()if p.GetNumber()==pin);assert cp.GetNetname()==ip.GetNetname()=='/3V3';metrics.append({'from':cap+'.1','to':ic+'.'+pin,'distance_mm':math.hypot(cp.GetPosition().x-ip.GetPosition().x,cp.GetPosition().y-ip.GetPosition().y)/1e6})
for src in r.iterdir():
 if src.suffix in ['.kicad_sch','.kicad_pro','.kicad_sym']or src.name in ['fp-lib-table','sym-lib-table']:assert src.read_bytes()==(o/'candidate'/src.name).read_bytes()
assert all(g in c for g in a if isinstance(g,list)and g[0]=='group')
result={'transfer_all_203_footprints_equal_approved_mux_candidate':True,'changed_references':sorted(refs),'unchanged_footprints':183,'all_corridors_clear':True,'antenna_exclusion_independently_checked':True,'card_eject_clearance_to_antenna_mm':.575,'identities_nets_locks_preserved':True,'existing_ground_via_sites_preserved':True,'tracks_and_vias':0,'prospective_ground_vias':sites,'decoupler_pad_distances':metrics,'authoritative_sha256':hashlib.sha256(root.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(p.read_bytes()).hexdigest()};(o/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
