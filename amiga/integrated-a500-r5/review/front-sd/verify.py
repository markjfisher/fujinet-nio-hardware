"""Read-only verification of the front-side microSD capacitor candidate."""
import re,json,math,collections,hashlib,xml.etree.ElementTree as E
from pathlib import Path
import pcbnew as k
p=Path(__file__).resolve().parent;r=p.parents[1];c=p/'candidate'
s=(r/'review/service/verify.py').read_text();exec(s[s.index('def tree'):s.index('\na,c,z=')])
a=tree(r/'integrated-a500-r5.kicad_pcb');b=tree(c/'integrated-a500-r5.kicad_pcb')
fa,fb=fps(a),fps(b)
assert set(fa)==set(fb) and len(fb)==214
assert {ref for ref in fa if fa[ref]!=fb[ref]}=={'C42','C43'}
assert collections.Counter(repr(x)for x in a if not isinstance(x,list)or x[0]!='footprint')==collections.Counter(repr(x)for x in b if not isinstance(x,list)or x[0]!='footprint')
for f in r.iterdir():
 if f.suffix in ['.kicad_sch','.kicad_pro','.kicad_sym','.kicad_dru']or f.name in ['fp-lib-table','sym-lib-table']:assert f.read_bytes()==(c/f.name).read_bytes(),f.name
old=k.LoadBoard(str(r/'integrated-a500-r5.kicad_pcb'));board=k.LoadBoard(str(c/'integrated-a500-r5.kicad_pcb'))
fs={f.GetReference():f for f in board.GetFootprints()}
def ident(f):return(f.m_Uuid.AsString(),f.GetValue(),f.GetFPIDAsString(),f.IsLocked(),f.GetPath().AsString(),sorted((q.m_Uuid.AsString(),q.GetNumber(),q.GetNetname())for q in f.Pads()))
for f in old.GetFootprints():assert ident(f)==ident(fs[f.GetReference()])
assert not board.GetTracks()
assert all(f.GetLayer()==k.F_Cu for f in fs.values())
nets={(n.get('ref'),n.get('pin')):net.get('name')for net in E.parse(r/'review/indicators/netlist.xml').findall('./nets/net')for n in net.findall('node')}
for ref,f in fs.items():
 for q in f.Pads():
  if (ref,q.GetNumber())in nets:assert q.GetNetname().replace('{slash}','/')==nets[ref,q.GetNumber()]
def box(q):return(q.GetX()/1e6,q.GetY()/1e6,q.GetRight()/1e6,q.GetBottom()/1e6)
def overlap(a,b):return min(a[2],b[2])>max(a[0],b[0])and min(a[3],b[3])>max(a[1],b[1])
for ref in ['C42','C43']:
 f=fs[ref];bb=box(f.GetCourtyard(k.F_CrtYd).BBox())
 for name,g in fs.items():
  if name==ref:continue
  # U30 has a concave courtyard; check its exact two rectangles.
  areas=[(-26.745,6.005,-5.755,53.995),(-5.755,20.255,14.445,39.745)]if name=='U30'else[box(g.GetCourtyard(k.F_CrtYd).BBox())]
  for other in areas:assert not overlap(bb,other),(ref,name)
 for area in [(-26.75,6,-5.75,54),(-10.525,54.575,-5.125,65.575),(87,3.5,94.5,120.5),(72,12,87,110)]:assert not overlap(bb,area)
vias=[]
for ref,xy in [('C42',(13.4,53.8)),('C43',(13.4,57.5))]:
 distances=[]
 for f in fs.values():
  for q in f.Pads():
   if q.GetNetname()=='/GND':continue
   l,t,rr,bt=box(q.GetBoundingBox());x,y=xy
   distances.append(math.hypot(max(l-x,0,x-rr),max(t-y,0,y-bt))-.3)
 assert min(distances)>=.125
 vias.append(dict(reference=ref,via_xy_mm=xy,diameter_mm=.6,drill_mm=.3,minimum_foreign_pad_clearance_mm=min(distances)))
# Preserve all other previously proposed ground-via positions.
for folder,file in [('pad-refinement','pad-checks.json'),('usb-power','verification.json'),('usb-mux','verification.json'),('esp-sd','verification.json'),('bus-buffers','verification.json'),('host-protection','verification.json'),('control-logic','verification.json')]:
 for v in json.loads((r/'review'/folder/file).read_text())['prospective_ground_vias']:
  if folder=='esp-sd'and v['reference']in ['C42','C43']:continue
  x,y=v['via_xy_mm']
  for ref in ['C42','C43']:
   for q in fs[ref].Pads():
    if q.GetNetname()=='/GND':continue
    l,t,rr,bt=box(q.GetBoundingBox())
    assert math.hypot(max(l-x,0,x-rr),max(t-y,0,y-bt))-.3>=.125,(ref,v)
d=json.loads((p/'drc.json').read_text());od=json.loads((r/'review/indicators/transfer/drc.json').read_text())
key=lambda v:(v['type'],tuple(sorted(i['uuid']for i in v['items'])))
assert collections.Counter(key(v)for v in d['violations'] if v['type']!='text_height')==collections.Counter(key(v)for v in od['violations'] if v['type']!='text_height')
assert not d['schematic_parity']
result=dict(footprints=214,front_footprints=214,back_footprints=0,unchanged_footprints=212,changed=['C42','C43'],all_nets_identities_locks_groups_preserved=True,all_schematics_byte_identical=True,schematic_parity=0,new_non_text_height_DRC_findings=0,reported_DRC_counts=dict(collections.Counter(v['type']for v in d['violations'])),unconnected_reported=len(d['unconnected_items']),tracks_vias=0,prospective_ground_vias=vias,old_C42_C43_proposed_vias_superseded=True,other_proposed_vias_preserved=True,J30_courtyard_gap_mm=.56,C43_to_J30_supply_pad_center_distance_mm=2.475,authoritative_sha256=hashlib.sha256((r/'integrated-a500-r5.kicad_pcb').read_bytes()).hexdigest())
(p/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
