"""Read-only corridor envelopes, net assertions and native-plot annotation. No routing/placement."""
import pcbnew as k,json,hashlib,math,re
from pathlib import Path
o=Path(__file__).resolve().parent;r=o.parent;bpath=r/'candidate/integrated-a500-r5.kicad_pcb';raw=bpath.read_bytes();b=k.LoadBoard(str(bpath));fs={f.GetReference():f for f in b.GetFootprints()}
boxes={'D2 north escape':(6.2,76,7.2,83.45),'Across to mux bay':(6.2,75.7,18.5,76.7),'Future U1/U2 + C1/C2 bay':(18,70,34,79),'West RP corridor':(23,37,25,70.5),'North of flash':(23,36.5,43.4,38.5),'R22/R23 approach':(40.4,37.5,43.4,46.4)}
results={}
for n,(l,t,rr,bt)in boxes.items():
 hits=[]
 for f in b.GetFootprints():
  q=f.GetCourtyard(k.F_CrtYd).BBox();fl,ft,fr,fb=q.GetX()/1e6,q.GetY()/1e6,q.GetRight()/1e6,q.GetBottom()/1e6
  if min(rr,fr)>max(l,fl)and min(bt,fb)>max(t,ft):hits.append(f.GetReference())
 assert not hits,(n,hits)
 results[n]={'xyxy_mm':[l,t,rr,bt],'courtyard_collisions':hits}
# Verify each electrically contiguous section; device channels are NOT copper shorts.
def pad(ref,num):return next(p for p in fs[ref].Pads()if p.GetNumber()==str(num))
chains=[ [('J1','A6'),('J1','B6'),('D2',1),('D2',6),('U1',3),('U2',3)], [('J1','A7'),('J1','B7'),('D2',3),('D2',4),('U1',7),('U2',7)], [('U1',4),('R22',2)], [('U1',6),('R23',2)], [('R22',1),('U20',67)], [('R23',1),('U20',66)], [('U1',2),('U2',2)], [('U1',8),('U2',8)] ]
netchecks=[]
for chain in chains:
 nets={pad(ref,n).GetNetname()for ref,n in chain};assert len(nets)==1
 netchecks.append({'net':next(iter(nets)),'pads':[ref+'.'+str(n)for ref,n in chain]})
# All proposed GND via discs remain outside the unobstructed corridor envelopes.
for path in [r/'verification.json',r.parents[1]/'review/pad-refinement/pad-checks.json']:
 data=json.loads(path.read_text())
 for v in data['prospective_ground_vias']:
  x,y=v['via_xy_mm']
  for name,(l,t,rr,bt)in boxes.items():
   assert math.hypot(max(l-x,0,x-rr),max(t-y,0,y-bt))>=.3,(name,v)
# Separation from a conservative bounding box containing all existing SW pads.
sw=[p.GetBoundingBox()for f in b.GetFootprints()for p in f.Pads()if p.GetNetname().endswith('/BUCK_SW')]
swbox=(min(q.GetX()for q in sw)/1e6,min(q.GetY()for q in sw)/1e6,max(q.GetRight()for q in sw)/1e6,max(q.GetBottom()for q in sw)/1e6)
def gap(a,z):return math.hypot(max(a[0]-z[2],z[0]-a[2],0),max(a[1]-z[3],z[1]-a[3],0))
sep=min(gap(rect,swbox)for rect in boxes.values());assert sep>13
assert len(b.GetTracks())==0 and bpath.read_bytes()==raw
result={'pcb_sha256':hashlib.sha256(raw).hexdigest(),'cad_unchanged':True,'corridor_envelopes':results,'net_sections':netchecks,'buck_sw_pad_envelope_mm':swbox,'minimum_corridor_to_sw_envelope_mm':sep,'muxes_still_staged':True,'new_tracks_or_vias':0,'limitations':'Envelopes, not routes. Mux bay is a future placement constraint; connector/mux fanouts and impedance remain routing validation.'}
(o/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
# Annotate the existing native plot; no new board graphic or rule area.
s=(r/'native.svg').read_text();layers=[]
for n,(l,t,rr,bt)in boxes.items():
 color='#ffa85c' if 'bay' in n and 'Future' in n else '#40e9f1';layers.append(f'<rect x="{l+6}" y="{t-3.5}" width="{rr-l}" height="{bt-t}" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-width=".12" stroke-dasharray=".5 .3"/>')
for text,x,y in [('Future mux bay (not placed)',18,68.8),('USB corridor - not routed',20,34.5),('To R22 / R23',40,35),('Local connector crossover',-3,89.5)]:
 layers.append(f'<text x="{x+6}" y="{y-3.5}" font-family="sans-serif" font-size=".65" fill="#40e9f1" stroke="none">{text}</text>')
s=s.replace('</svg>','<g>'+''.join(layers)+'</g></svg>');s=re.sub(r'width="[^"]+mm" height="[^"]+mm" viewBox="[^"]+"','width="63mm" height="72mm" viewBox="0 30 63 72"',s,count=1);(o/'assessment.svg').write_text(s)
print('PASS: empty corridors, net chains and via reservations; SW separation',sep,'mm; no CAD edits')
