"""Read-only first-milestone acceptance checks; native pcbnew + XML netlists."""
import pcbnew as k,json,hashlib,math,xml.etree.ElementTree as E
from pathlib import Path
r5=Path(__file__).resolve().parents[2];r4=r5.parent/'integrated-a500-r4';out=Path(__file__).parent
refs={'U20','U21','L20','Y20','R10','R13',*[f'R{i}' for i in range(20,25)],*[f'C{i}' for i in range(20,40)]};fixed={'J40','H1','H2','H3','H4'}
a=k.LoadBoard(str(r4/'integrated-a500-r4.kicad_pcb'));b=k.LoadBoard(str(r5/'integrated-a500-r5.kicad_pcb'))
fs=[{f.GetReference():f for f in q.GetFootprints()} for q in [a,b]]
assert set(fs[0])==set(fs[1]) and len(fs[1])==203
for r,f in fs[0].items():
 g=fs[1][r]
 assert (f.m_Uuid.AsString(),f.GetValue(),f.GetFPIDAsString(),f.GetPath().AsString(),f.GetLayer())==(g.m_Uuid.AsString(),g.GetValue(),g.GetFPIDAsString(),g.GetPath().AsString(),g.GetLayer()),r
 def pads(fp):
  return sorted((p.m_Uuid.AsString(),p.GetNumber(),p.GetNetname(),p.GetFPRelativePosition().x,p.GetFPRelativePosition().y,p.GetSize().x,p.GetSize().y,p.GetDrillSize().x,p.GetDrillSize().y) for p in fp.Pads())
 assert pads(f)==pads(g),r
 if r in fixed:assert (f.GetPosition(),f.GetOrientationDegrees())==(g.GetPosition(),g.GetOrientationDegrees())
 if r not in refs|fixed:assert g.GetPosition().x>120e6,r
 assert g.Reference().IsVisible()
 assert g.Reference().GetTextSize()==k.VECTOR2I(600000,600000)
 assert g.Reference().GetTextThickness()==90000
 assert g.IsLocked()==(r in fixed)
def outline(board):return sorted((s.GetShape(),s.GetStart().x,s.GetStart().y,s.GetEnd().x,s.GetEnd().y,s.GetWidth()) for s in board.GetDrawings() if s.GetLayer()==k.Edge_Cuts)
assert outline(a)==outline(b);assert a.GetCopperLayerCount()==b.GetCopperLayerCount()==4
assert len(a.GetTracks())==len(b.GetTracks())==0
for name,digest in json.loads((out/'r4-hashes.json').read_text()).items():assert hashlib.sha256((r4/name).read_bytes()).hexdigest()==digest,name
for p in r4.glob('*.kicad_sch'):
 assert p.read_bytes()==(r5/p.name.replace('integrated-a500-r4','integrated-a500-r5')).read_bytes()
pa=json.loads((r4/'integrated-a500-r4.kicad_pro').read_text().replace('integrated-a500-r4','integrated-a500-r5'));pb=json.loads((r5/'integrated-a500-r5.kicad_pro').read_text());assert pa==pb
# Conservative physical acceptance, independent of any placement cost.
def box(f):
 c=f.GetCourtyard(k.F_CrtYd);q=c.BBox() if c.OutlineCount() else f.GetBoundingBox(False,False)
 return (q.GetX()/1e6,q.GetY()/1e6,q.GetRight()/1e6,q.GetBottom()/1e6)
def hit(a,b):return min(a[2],b[2])>max(a[0],b[0])+1e-5 and min(a[3],b[3])>max(a[1],b[1])+1e-5
bb={r:box(f) for r,f in fs[1].items()};overlaps=sorted(set(tuple(sorted([r,s])) for r in refs for s in bb if r!=s and hit(bb[r],bb[s])))
# Reference cell uses irregular courtyards; native DRC remains the exact check.
assert not overlaps,overlaps
for r in refs:
 q=bb[r];assert q[0]>=-6 and q[1]>=3.5 and q[2]<=72 and q[3]<=106,r
 for z in [(-26.75,6,-5.75,54),(87,3.5,105,120.5),(72,12,87,110)]:assert not hit(q,z),r
# Regulator cell matches the licensed reference offsets, not obsolete general R4 placement.
anchor=fs[1]['U20'].GetPosition();source=json.loads((r5/'reference/rp-core-footprints.json').read_text())
for x in source['records']:
 f=fs[1][x['reference']];p=f.GetPosition();assert abs(p.x/1e6-anchor.x/1e6-(x['fixed'][0]-60))<1e-5;assert abs(p.y/1e6-anchor.y/1e6-(x['fixed'][1]-60))<1e-5;assert f.GetOrientationDegrees()==x['rotation']
capmap={'C26':5,'C27':15,'C28':24,'C29':29,'C30':41,'C31':50,'C32':60,'C33':59,'C34':68,'C35':69,'C36':76,'C37':10,'C38':51,'C39':32,'C23':61,'C24':64,'C25':65}
ownership=[]
for c,pin in capmap.items():
 cp=next(p for p in fs[1][c].Pads() if p.GetNumber()=='1');up=next(p for p in fs[1]['U20'].Pads() if p.GetNumber()==str(pin));assert cp.GetNetname()==up.GetNetname()
 ownership.append({'capacitor':c,'u20_pin':pin,'net':cp.GetNetname(),'pad_centre_distance_mm':math.hypot(cp.GetPosition().x-up.GetPosition().x,cp.GetPosition().y-up.GetPosition().y)/1e6})
(out/'capacitor-ownership.json').write_text(json.dumps(ownership,indent=2))
result={'r4_all_hashes_unchanged':True,'schematics_byte_identical_project_only_renamed':True,'all_footprint_and_pad_ids_nets_local_geometry_preserved':True,'mechanical_datums_preserved':True,'four_copper_layers':True,'tracks':0,'footprints':203,'rp_cluster':sorted(refs),'staged_count':len(set(fs[1])-refs-fixed),'locked_mechanical_refs':sorted(fixed),'selected_courtyard_intersections':overlaps,'reserved_regions_pass':True,'regulator_reference_geometry_pass':True,'all_reference_text_standard_and_visible':True,'groups':[g.GetName() for g in b.Groups()]}
(out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
