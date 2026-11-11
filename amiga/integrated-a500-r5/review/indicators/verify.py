"""Read-only validation of the indicator candidate; never changes CAD."""
import re,json,copy,math,hashlib,collections,xml.etree.ElementTree as E
from pathlib import Path
import pcbnew as k
p=Path(__file__).resolve().parent;r=p.parents[1];base=r/'review/service/candidate';cand=p/'candidate'
# Reuse only pure read-only parsing helpers from the earlier review.
s=(r/'review/service/verify.py').read_text();exec(s[s.index('def tree'):s.index('\na,c,z=')])
a=tree(base/'integrated-a500-r5.kicad_pcb');b=tree(cand/'integrated-a500-r5.kicad_pcb');fa,fb=fps(a),fps(b)
refs={x['reference']for x in json.loads((p/'placement.json').read_text())}
assert len(refs)==11 and len(fb)==214 and set(fb)-set(fa)==refs
for ref in fa:
 if ref!='U30':assert fa[ref]==fb[ref],ref
# U30's only edits are the two formerly unused GPIO pad nets.
u=copy.deepcopy(fb['U30']);oldpads={next(v[1]for v in x if isinstance(v,list)and v[0]=='uuid'):x for x in fa['U30']if isinstance(x,list)and x[0]=='pad'}
changed=[]
for pad in u:
 if not isinstance(pad,list)or pad[0]!='pad':continue
 uid=next(v[1]for v in pad if isinstance(v,list)and v[0]=='uuid');op=oldpads[uid]
 if pad!=op:
  assert pad[1]in ['"4"','"5"'];assert [v for v in pad if not isinstance(v,list)or v[0]!='net']==[v for v in op if not isinstance(v,list)or v[0]!='net']
  changed.append(pad[1]);pad[:]=copy.deepcopy(op)
assert sorted(changed)==['"4"','"5"'] and u==fa['U30']
for x in a:
 if isinstance(x,list)and x[0]in ['footprint','net']:continue
 assert x in b, str(x)[:120]
for f in base.iterdir():
 if f.suffix in ['.kicad_sch','.kicad_pro','.kicad_sym']or f.name in ['fp-lib-table','sym-lib-table']:
  if f.name!='esp.kicad_sch':assert f.read_bytes()==(cand/f.name).read_bytes(),f.name

def nets(path):return {(x.get('ref'),x.get('pin')):n.get('name')for n in E.parse(path).findall('./nets/net')for x in n.findall('node')}
old=nets(p/'baseline.xml');new=nets(p/'netlist.xml')
for pair,n in old.items():
 if pair in [('U30','4'),('U30','5')]:assert n.startswith('unconnected-')
 else:assert new[pair]==n,(pair,n,new.get(pair))
expected={}
for i,name in enumerate(['PWR','NET','DISK']):
 an='/ESP32-S3 module and microSD/LED_'+name+'_A';sig='/3V3'if i==0 else '/ESP32-S3 module and microSD/LED_'+name+'_GPIO'
 expected.update({(f'R{130+i}','1'):sig,(f'R{130+i}','2'):an,(f'D{130+i}','2'):an,(f'D{130+i}','1'):'/GND',(f'J{130+i}','1'):an,(f'J{130+i}','2'):'/GND'})
 if i:expected.update({(f'R{132+i}','1'):sig,(f'R{132+i}','2'):'/GND',('U30',str(3+i)):sig})
assert all(new[pair]==n for pair,n in expected.items())
board=k.LoadBoard(str(cand/'integrated-a500-r5.kicad_pcb'));fs={f.GetReference():f for f in board.GetFootprints()}
for f in fs.values():
 for pad in f.Pads():
  if (f.GetReference(),pad.GetNumber())in new:assert pad.GetNetname().replace('{slash}','/')==new[f.GetReference(),pad.GetNumber()]
assert not board.GetTracks()
def box(q):return(q.GetX()/1e6,q.GetY()/1e6,q.GetRight()/1e6,q.GetBottom()/1e6)
def overlap(a,b):return min(a[2],b[2])>max(a[0],b[0])and min(a[3],b[3])>max(a[1],b[1])
for ref in refs:
 f=fs[ref];q=box(f.GetCourtyard(k.F_CrtYd).BBox());assert q[0]>=-6 and q[2]<=87 and q[1]>=3.5 and q[3]<=120.5
 for ex in [(-26.75,6,-5.75,54),(72,12,87,110),(87,3.5,94.5,120.5)]:assert not overlap(q,ex),(ref,ex)
 for name,v in json.loads((r/'review/usb-power/corridor/checks.json').read_text())['corridor_envelopes'].items():
  if not name.startswith('Future'):assert not overlap(q,v['xyxy_mm']),(ref,name)
# Check prior planned ground-via sites against newly introduced foreign pads.
for folder,file in [('pad-refinement','pad-checks.json'),('usb-power','verification.json'),('usb-mux','verification.json'),('esp-sd','verification.json'),('bus-buffers','verification.json'),('host-protection','verification.json'),('control-logic','verification.json')]:
 for v in json.loads((r/'review'/folder/file).read_text())['prospective_ground_vias']:
  x,y=v['via_xy_mm']
  for ref in refs:
   for pad in fs[ref].Pads():
    if pad.GetNetname()=='/GND':continue
    l,t,rr,bt=box(pad.GetBoundingBox());assert math.hypot(max(l-x,0,x-rr),max(t-y,0,y-bt))-.3>=.125,(ref,v)
# Header cable housings: provisional 4 mm wide by 7 mm deep top access.
for i in range(3):
 ref=f'J{130+i}';x=-2+i*5.5;area=(x-2,5,x+2,12)
 for name,f in fs.items():
  if name==ref:continue
  if name=='U30':
   # Exact orthogonal concave courtyard decomposition, not its enclosing box.
   q=f.GetCourtyard(k.F_CrtYd).COutline(0);pts=[(q.CPoint(j).x/1e6,q.CPoint(j).y/1e6) for j in range(q.PointCount())]
   assert pts==[(-5.755,6.005),(-5.755,20.255),(14.445,20.255),(14.445,39.745),(-5.755,39.745),(-5.755,53.995),(-26.745,53.995),(-26.745,6.005)]
   assert not overlap(area,(-26.745,6.005,-5.755,53.995)) and not overlap(area,(-5.755,20.255,14.445,39.745))
  else:assert not overlap(area,box(f.GetCourtyard(k.F_CrtYd).BBox())),(ref,name)
key=lambda v:(v['type'],tuple(sorted(i['uuid']for i in v['items'])))
d=json.loads((p/'drc.json').read_text());bd=json.loads((r/'review/service/drc.json').read_text())
assert collections.Counter(key(v) for v in d['violations'] if v['type']!='text_height')==collections.Counter(key(v) for v in bd['violations'] if v['type']!='text_height')
assert not d['schematic_parity']
e=json.loads((p/'erc.json').read_text());be=json.loads((r/'review/service/erc.json').read_text());assert e['sheets']==be['sheets']
result=dict(footprints=214,new_footprints=sorted(refs),unchanged_existing_footprints=202,existing_U30_changes_only_GPIO4_GPIO5_nets=True,all_existing_placement_groups_locks_preserved=True,prior_via_sites_and_corridors_preserved=True,provisional_header_access_clear=True,all_netlist_pad_memberships_verified=True,ERC_unchanged=True,new_non_text_height_DRC_findings=0,new_06mm_reference_height_warnings=11,schematic_parity=0,tracks_vias=0,authoritative_sha256=hashlib.sha256((r/'integrated-a500-r5.kicad_pcb').read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256((cand/'integrated-a500-r5.kicad_pcb').read_bytes()).hexdigest())
(p/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: netlist, placement preservation, corridors/vias/access, ERC and DRC/parity')
