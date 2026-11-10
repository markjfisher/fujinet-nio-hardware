"""Read-only placement verification against the approved root R5 PCB. No CAD edits."""
import pcbnew as k,json,math,re,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2];o=r/'review/usb-power';a=r/'integrated-a500-r5.kicad_pcb';p=o/'candidate/integrated-a500-r5.kicad_pcb';b=k.LoadBoard(str(p));old=k.LoadBoard(str(a));fs={f.GetReference():f for f in b.GetFootprints()};before={f.GetReference():f for f in old.GetFootprints()}
refs=set('J1 D2 D3 U3 C3 R4 R5 R6 U6 C4 C5 U7 C123 U8 U9 C100 C101 C102 R100 R101 R102 R103 R104 R105 U4 C6 R14 U5 L1 C7 C8 C9 C124 R7 R8 C117'.split())
def tree(path):
 ts=iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',Path(path).read_text()))
 def read(t):
  if t=='(':
   result=[]
   for t in ts:
    if t==')':return result
    result.append(read(t))
  try:return float(t)
  except:return t
 return read(next(ts))
def footprints(t):return {next(c[2].strip('"') for c in f if isinstance(c,list)and c[:2]==['property','"Reference"']):f for f in t if isinstance(f,list)and f[0]=='footprint'}
ta,tb=tree(a),tree(p);fa,fb=footprints(ta),footprints(tb);changed={ref for ref in fa if fa[ref]!=fb[ref]};assert changed==refs,changed^refs
assert [x for x in ta if not isinstance(x,list)or x[0]not in ['footprint','group']]==[x for x in tb if not isinstance(x,list)or x[0]not in ['footprint','group']]
def ids(f):return (f.m_Uuid.AsString(),f.GetValue(),f.GetFPIDAsString(),f.GetPath().AsString(),f.IsLocked(),f.GetLayer(),sorted((p.m_Uuid.AsString(),p.GetNumber(),p.GetNetname(),p.GetFPRelativePosition().x,p.GetFPRelativePosition().y,p.GetSize().x,p.GetSize().y)for p in f.Pads()))
assert len(fs)==203
for ref in fs:assert ids(fs[ref])==ids(before[ref]),ref
assert len(b.GetTracks())==0
for ref in refs:
 f=fs[ref];assert f.Reference().IsVisible();assert f.Reference().GetTextSize()==k.VECTOR2I(k.FromMM(.6),k.FromMM(.6));assert f.Reference().GetTextThickness()==k.FromMM(.09)
 box=f.GetCourtyard(k.F_CrtYd).BBox();assert box.GetRight()/1e6<72
 assert box.GetY()/1e6>73 and box.GetBottom()/1e6<108
 if ref!='J1':assert box.GetX()/1e6>-6
# Grounds have explicit reserved via sites. These annotations create no copper.
sites={'C3':(10.6,78.5),'C4':(13.8,87.3),'C5':(20.2,87.3),'C123':(25.2,89.8),'C100':(7,100.475),'C101':(.0,94.4),'C102':(14,94.2),'C7':(28.1,96.8),'C8':(30.5,98),'C9':(26.1,89),'C124':(26.5,91.8),'C117':(49.8,96),'D2':(2,82),'D3':(5.8,78),'U8':(4.3,92),'U9':(15.2,97.4),'U6':(14.9,86.5),'U7':(18.8,90.95),'U4':(18.8,95)}
rp=json.loads((r/'review/pad-refinement/pad-checks.json').read_text())['prospective_ground_vias']
def checksite(x,y):
 distances=[]
 for f in b.GetFootprints():
  for pad in f.Pads():
   if pad.GetNetname()=='/GND' or not pad.GetNumber():continue
   q=pad.GetBoundingBox();dx=max(q.GetX()/1e6-x,0,x-q.GetRight()/1e6);dy=max(q.GetY()/1e6-y,0,y-q.GetBottom()/1e6);distances.append((math.hypot(dx,dy)-.3,f.GetReference()+'.'+pad.GetNumber()))
 return min(distances)
checks=[]
for ref,(x,y) in sites.items():
 clearance,nearest=checksite(x,y);gnds=[pad for pad in fs[ref].Pads()if pad.GetNetname()=='/GND'];assert gnds,ref
 dist=min(math.dist((x,y),(pad.GetPosition().x/1e6,pad.GetPosition().y/1e6))for pad in gnds)
 checks.append({'reference':ref,'via_xy_mm':[x,y],'diameter_mm':.6,'drill_mm':.3,'minimum_foreign_pad_clearance_mm':clearance,'nearest_foreign_pad':nearest,'distance_to_gnd_pad_centre_mm':dist})
 if clearance<.2:print('FAIL VIA',ref,clearance,nearest)
for site in rp:assert checksite(*site['via_xy_mm'])[0]>=.125
for x in checks:assert x['minimum_foreign_pad_clearance_mm']>=.2,x
for i,x in enumerate(checks):
 for y in checks[:i]:assert math.dist(x['via_xy_mm'],y['via_xy_mm'])>=.85
# Candidate has exact schematic/library/project copies; no connectivity changes.
for src in r.iterdir():
 if src.suffix in ['.kicad_sch','.kicad_pro','.kicad_sym']or src.name in ['fp-lib-table','sym-lib-table']:assert src.read_bytes()==(o/'candidate'/src.name).read_bytes(),src
# Numeric critical-net distances are placement estimates, not routed lengths.
def pad(ref,n):return next(p for p in fs[ref].Pads()if p.GetNumber()==str(n))
metrics=[]
for a1,n1,a2,n2 in [('C7',1,'U5',12),('C124',1,'U5',10),('U5',1,'L1',1),('L1',2,'C8',1),('U5',14,'C8',1),('R7',2,'U5',5),('C9',1,'U5',9),('C100',1,'U8',4),('U8',5,'C102',1),('C102',1,'U9',1),('C123',1,'U7',5)]:
 x,y=pad(a1,n1),pad(a2,n2);assert x.GetNetname()==y.GetNetname();metrics.append({'from':a1+'.'+str(n1),'to':a2+'.'+str(n2),'net':x.GetNetname(),'straight_line_mm':math.hypot(x.GetPosition().x-y.GetPosition().x,x.GetPosition().y-y.GetPosition().y)/1e6})
result={'baseline_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changed_references':sorted(refs),'unchanged_footprints':len(fs)-len(refs),'identities_nets_locks_preserved':True,'rp_geometry_and_proposed_vias_preserved':True,'mechanical_datums_and_board_graphics_unchanged':True,'schematics_and_project_rules_unchanged':True,'tracks_and_vias':len(b.GetTracks()),'groups':{g.GetName():len(g.GetItems())for g in b.Groups()},'critical_pad_distances':metrics,'prospective_ground_vias':checks}
(o/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(refs),'moved;',len(fs)-len(refs),'unchanged;',len(checks),'GND-via sites; RP preserved')
