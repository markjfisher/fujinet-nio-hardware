"""Read-only placement/net/clearance checks. Never writes CAD."""
import pcbnew as k,json,re,math,hashlib,collections,copy
from pathlib import Path
o=Path(__file__).resolve().parent;r=o.parents[1];p=o/'candidate/integrated-a500-r5.kicad_pcb';root=r/'integrated-a500-r5.kicad_pcb';approved=r/'review/esp-sd/candidate/integrated-a500-r5.kicad_pcb'
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

a,c,z=map(tree,[root,p,approved]);fa,fc,fz=map(fps,[a,c,z]);assert a==z,'Root transfer differs from approved ESP candidate'
refs=set(x['reference']for x in json.loads((o/'placement.json').read_text()));assert len(refs)==20;assert {ref for ref in fa if fa[ref]!=fc[ref]}==refs
normalized=copy.deepcopy(a)
for item in normalized:
 if isinstance(item,list)and item[0]=='zone'and ['name','"R5 reserved buffer corridor"']in item:
  ko=next(x for x in item if isinstance(x,list)and x[0]=='keepout');field=next(x for x in ko if isinstance(x,list)and x[0]=='footprints');assert field[1]=='not_allowed';field[1]='allowed'
assert [x for x in normalized if not isinstance(x,list)or x[0]not in ['footprint','group']]==[x for x in c if not isinstance(x,list)or x[0]not in ['footprint','group']]
assert all(g in c for g in a if isinstance(g,list)and g[0]=='group')
b=k.LoadBoard(str(p));old=k.LoadBoard(str(root));fs={f.GetReference():f for f in b.GetFootprints()}
def identity(f):return(f.m_Uuid.AsString(),f.GetValue(),f.GetFPIDAsString(),f.IsLocked(),f.GetPath().AsString(),sorted((p.m_Uuid.AsString(),p.GetNumber(),p.GetNetname(),p.GetFPRelativePosition().x,p.GetFPRelativePosition().y)for p in f.Pads()))
for f in old.GetFootprints():assert identity(f)==identity(fs[f.GetReference()])
assert len(b.GetTracks())==0 and len(fs)==203
for u in range(40,48):
 g=next(g for g in b.Groups()if g.GetName()=='R5: U%d buffer cell - visual review pending'%u)
 owned={'U'+str(u),'C'+str(u+10)}
 if u>=44:owned.add('R'+str({44:50,45:51,46:52,47:53}[u]))
 assert {item.GetReference()for item in g.GetItems()}==owned
for src in r.iterdir():
 if src.suffix in ['.kicad_sch','.kicad_pro','.kicad_sym']or src.name in ['fp-lib-table','sym-lib-table']:assert src.read_bytes()==(o/'candidate'/src.name).read_bytes()
def box(q):return(q.GetX()/1e6,q.GetY()/1e6,q.GetRight()/1e6,q.GetBottom()/1e6)
def overlap(a,b):return min(a[2],b[2])>max(a[0],b[0])and min(a[3],b[3])>max(a[1],b[1])
for f in fs.values():
 q=box(f.GetCourtyard(k.F_CrtYd).BBox())
 if f.GetReference()in refs:assert q[0]>=72 and q[2]<=87 and q[1]>=12 and q[3]<=110,(f.GetReference(),q)
 else:assert not overlap(q,(72,12,87,110)),f.GetReference()
 if f.GetReference()!='U30':assert not overlap(q,(-26.75,6,-5.75,54))
 if f.GetReference()!='J40':assert not overlap(q,(87,3.5,94.5,120.5)),f.GetReference()
 for pad in f.Pads():assert not overlap(box(pad.GetBoundingBox()),(-26.75,6,-5.75,54))
for name,v in json.loads((r/'review/usb-power/corridor/checks.json').read_text())['corridor_envelopes'].items():
 if name.startswith('Future'):continue
 for f in fs.values():assert not overlap(box(f.GetCourtyard(k.F_CrtYd).BBox()),v['xyxy_mm']),(name,f.GetReference())
# J30 envelope and U30 contents are byte-for-byte semantic footprint matches.
assert fc['J30']==fz['J30'] and fc['U30']==fz['U30']
sites=[];metrics=[];pinrows=[]
def pad(ref,n):return next(p for p in fs[ref].Pads()if p.GetNumber()==str(n))
for u in range(40,48):
 ref='U'+str(u);cap='C'+str(u+10);f=fs[ref];y=f.GetPosition().y/1e6;rx=f.GetOrientationDegrees()==180
 assert pad(ref,20).GetNetname()==pad(cap,1).GetNetname()==('/3V3_BUS'if u in [44,45]else '/3V3');assert pad(cap,2).GetNetname()==pad(ref,10).GetNetname()=='/GND'
 dist=math.hypot(pad(ref,20).GetPosition().x-pad(cap,1).GetPosition().x,pad(ref,20).GetPosition().y-pad(cap,1).GetPosition().y)/1e6;assert abs(dist-1.6)<1e-5;metrics.append({'ic':ref,'bypass':cap,'supply':pad(ref,20).GetNetname(),'supply_pad_distance_mm':dist})
 sites.extend([{'reference':cap,'via_xy_mm':[75.9 if rx else 84.1,y+(6.075 if rx else -6.075)]},{'reference':ref+' pin10','via_xy_mm':[84.4 if rx else 75.6,y+(-2.925 if rx else 2.925)]}])
 if u>=44:
  res='R'+str({44:50,45:51,46:52,47:53}[u]);assert pad(res,2).GetNetname()==pad(ref,1).GetNetname();assert pad(res,1).GetNetname()=='/3V3';assert pad(ref,19).GetNetname()=='/BUS_DISABLE'
 for pp in f.Pads():pinrows.append({'ref':ref,'pin':pp.GetNumber(),'net':pp.GetNetname(),'xy_mm':[pp.GetPosition().x/1e6,pp.GetPosition().y/1e6]})
existing=[]
for path in [r/'review/esp-sd/verification.json',r/'review/usb-power/verification.json',r/'review/pad-refinement/pad-checks.json',r/'review/usb-mux/verification.json']:existing+=json.loads(path.read_text())['prospective_ground_vias']
for s in sites+existing:
 x,y=s['via_xy_mm'];clear=[]
 for f in fs.values():
  for pp in f.Pads():
   if pp.GetNetname()=='/GND' or not pp.GetNumber():continue
   l,t,rr,bt=box(pp.GetBoundingBox());clear.append(math.hypot(max(l-x,0,x-rr),max(t-y,0,y-bt))-.3)
 minimum=min(clear);assert minimum>=.125,(s,minimum)
 if s in sites:s.update(diameter_mm=.6,drill_mm=.3,minimum_foreign_pad_clearance_mm=minimum)
for i,s in enumerate(sites+existing):
 for t in (sites+existing)[:i]:assert math.dist(s['via_xy_mm'],t['via_xy_mm'])>=.85
baseline=json.loads((r/'review/esp-sd/drc.json').read_text());transfer=json.loads((o/'transfer-drc.json').read_text());drc=json.loads((o/'drc.json').read_text());assert baseline['violations']==transfer['violations'];key=lambda v:(v['type'],tuple(sorted(i['uuid']for i in v['items'])));assert collections.Counter(map(key,baseline['violations']))==collections.Counter(map(key,drc['violations']));assert drc['schematic_parity']==transfer['schematic_parity']==[]
erc=json.loads((o/'erc.json').read_text());assert erc['sheets']==json.loads((r/'review/esp-sd/erc.json').read_text())['sheets']
result={'authoritative_matches_entire_approved_esp_candidate':True,'changed_references':sorted(refs),'unchanged_footprints':183,'identities_nets_locks_and_existing_groups_preserved':True,'antenna_and_card_access_preserved':True,'connector_and_USB_corridors_clear':True,'buffer_corridor_ownership_verified':True,'previous_ground_via_sites_preserved':True,'prospective_ground_vias':sites,'bypass_pin_mapping':metrics,'new_native_drc_findings':0,'erc_unchanged':True,'schematic_parity':0,'tracks_and_vias':0,'root_sha256':hashlib.sha256(root.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(p.read_bytes()).hexdigest()};(o/'verification.json').write_text(json.dumps(result,indent=2)+'\n');(o/'pin-nets.json').write_text(json.dumps(pinrows,indent=2)+'\n');print('PASS: transfer, 20 selected /183 preserved, domains, corridors, vias, DRC/ERC/parity')
