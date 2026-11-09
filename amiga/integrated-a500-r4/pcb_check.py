"""Independent native PCB/schematic parity, contact geometry, and placement checks."""
from pathlib import Path
import json,math,subprocess,collections,xml.etree.ElementTree as E
import pcbnew as k
ROOT=Path(__file__).resolve().parent;P=ROOT/'integrated-a500-r4.kicad_pcb';R=ROOT/'review'
mechanical=json.loads((ROOT/'mechanical.json').read_text())
b=k.LoadBoard(str(P));fs={f.GetReference():f for f in b.GetFootprints()}
plan={c['reference']:c for c in json.loads((ROOT/'circuit.json').read_text())['components'] if not c['reference'].startswith('#')}
assert set(fs)==set(plan)|{'H1','H2','H3','H4'},set(fs)^set(plan)
t=E.parse(R/'netlist.xml');expected={(n.get('ref'),n.get('pin')):net.get('name') for net in t.findall('./nets/net') for n in net.findall('node')}
checked=0
for ref,c in plan.items():
 f=fs[ref];assert str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName())==c['footprint'],ref
 for pin,net in c['pins'].items():
  pads=[p for p in f.Pads() if p.GetNumber()==pin];assert pads,(ref,pin)
  assert all(str(p.GetNetname())==expected[ref,pin] for p in pads),(ref,pin)
  checked+=1
 # No assigned copper net on an explicitly NC pin may join a functional net.
 for p in f.Pads():
  number=p.GetNumber()
  if number and number not in c['pins']:
   assert not p.GetNetname() or str(p.GetNetname()).startswith('unconnected-'),(ref,number,p.GetNetname())
f=fs['J40'];assert len(list(f.Pads()))==86
for pad in f.Pads():
 n=int(pad.GetNumber());i=(n-1)//2
 assert abs(k.ToMM(pad.GetPosition().x)-99.666)<1e-5
 assert abs(k.ToMM(pad.GetPosition().y)-(8.66+i*2.54))<1e-5
 assert set(pad.GetLayerSet().Seq())==({k.F_Cu,k.F_Mask} if n%2 else {k.B_Cu,k.B_Mask})
 assert abs(k.ToMM(pad.GetSize().x)-9.5)<1e-5 and abs(k.ToMM(pad.GetSize().y)-1.65)<1e-5
 assert not pad.IsOnLayer(k.F_Paste) and not pad.IsOnLayer(k.B_Paste)
for item in json.loads((ROOT/'reference/rp-core-footprints.json').read_text())['records']:
 f=fs[item['reference']];x,y=item['fixed'];dx,dy=mechanical['reference_cell_translation_mm'];x+=dx;y+=dy
 assert math.hypot(k.ToMM(f.GetPosition().x)-x,k.ToMM(f.GetPosition().y)-y)<1e-5,item
 assert abs((f.GetOrientationDegrees()-item['rotation'])%360)<1e-5,item
local=[]
for m in json.loads((R/'bypass-placement.json').read_text())['moves']:
 c=fs[m['reference']];u=fs[m['load']];cp=c.GetPosition()
 distance=min(math.hypot(k.ToMM(cp.x-p.GetPosition().x),k.ToMM(cp.y-p.GetPosition().y)) for p in u.Pads() if str(p.GetNetname())=='/3V3')
 assert distance<5.01,(m,distance)
 local.append(distance)
# A full 18 mm band is clear of non-socket parts on both faces, including
# mounting hardware courtyards. Solder lands belonging to J40 are intentional.
zones=[z for z in b.Zones() if z.GetZoneName()=='A500 connector component clearance']
assert len(zones)==1
z=zones[0]
assert z.GetIsRuleArea() and z.GetDoNotAllowFootprints()
assert set(z.GetLayerSet().Seq())=={k.F_Cu,k.B_Cu}
assert not z.GetDoNotAllowTracks() and not z.GetDoNotAllowVias() and not z.GetDoNotAllowZoneFills()
rightmost=-1e9
for ref,f in fs.items():
 if ref=='J40':continue
 items=[g for g in f.GraphicalItems() if g.GetLayer() in [k.F_CrtYd,k.B_CrtYd]]+list(f.Pads())
 edge=max(k.ToMM(g.GetBoundingBox().GetRight()) for g in items)
 assert edge<=mechanical['component_limit_x_mm']+1e-5,(ref,edge)
 rightmost=max(rightmost,edge)
points=[p for g in b.GetDrawings() if g.GetLayer()==k.Edge_Cuts for p in [g.GetStart(),g.GetEnd()]]
xs=[k.ToMM(p.x) for p in points];ys=[k.ToMM(p.y) for p in points];o=mechanical['outline']
assert [min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)]==[o['x_mm'],o['y_mm'],o['width_mm'],o['height_mm']]
# Every reference remains visible and consistently styled; no hidden-label
# workaround is accepted after the readability review.
for ref,f in fs.items():
 text=f.Reference()
 assert text.IsVisible(),('hidden reference',ref)
 assert abs(k.ToMM(text.GetTextSize().x)-.9)<1e-6 and abs(k.ToMM(text.GetTextSize().y)-.9)<1e-6,ref
 assert abs(k.ToMM(text.GetTextThickness())-.15)<1e-6,ref
 assert abs(text.GetTextAngle().AsDegrees())<1e-6,ref
 assert text.GetLayer()==(k.B_SilkS if f.GetLayer()==k.B_Cu else k.F_SilkS),ref
cluster=json.loads((R/'cluster-plan.json').read_text());power_distances=[]
for item in cluster['local_power_distances']:
 cap=fs[item['capacitor']];load=fs[item['load']];pad=next(p for p in load.Pads() if p.GetNumber()==item['power_pin'])
 distance=math.hypot(k.ToMM(cap.GetPosition().x-pad.GetPosition().x),k.ToMM(cap.GetPosition().y-pad.GetPosition().y))
 assert abs(distance-item['center_to_power_pad_mm'])<.002,item
 power_distances.append(dict(item,measured_mm=round(distance,3)))
assert {r for r,f in fs.items() if f.GetLayer()==k.B_Cu}=={'C42','C43'}
group_report=json.loads((R/'group-checks.json').read_text())
actual_groups={g.GetName():g for g in b.Groups()}
for record in group_report['groups']:
 g=actual_groups['FN: '+record['name']]
 assert {item.GetReference() for item in g.GetItems()}==set(record['members']),record
power_moves=json.loads((R/'power-cell-plan.json').read_text())['moves']
for move in power_moves:
 f=fs[move['reference']]
 assert math.hypot(k.ToMM(f.GetPosition().x)-move['x_mm'],k.ToMM(f.GetPosition().y)-move['y_mm'])<1e-5,move
 assert abs((f.GetOrientationDegrees()-move['rotation_deg']+180)%360-180)<1e-5,move
for move in json.loads((R/'tidy-plan.json').read_text())['moves']:
 f=fs[move['reference']]
 assert math.hypot(k.ToMM(f.GetPosition().x)-move['x_mm'],k.ToMM(f.GetPosition().y)-move['y_mm'])<1e-5,move
 if 'rotation_deg' in move:assert abs((f.GetOrientationDegrees()-move['rotation_deg']+180)%360-180)<1e-5,move
for ref in ['U69','U70','U74','U79']:
 assert {p.GetNumber() for p in fs[ref].Pads()}=={'1','2','3','4','5'},ref
assert b.GetCopperLayerCount()==4
subprocess.run(['kicad-cli','pcb','drc','--schematic-parity','--format','json','-o',str(R/'drc.json'),str(P)],check=True,capture_output=True)
drc=json.loads((R/'drc.json').read_text());assert not drc['schematic_parity'],drc['schematic_parity'][:2]
subprocess.run(['kicad-cli','pcb','export','svg','--mode-single','--exclude-drawing-sheet','--layers','F.Cu,F.Silkscreen,Edge.Cuts','--page-size-mode','2','--output',str(R/'placement.svg'),str(P)],check=True,capture_output=True)
subprocess.run(['kicad-cli','pcb','export','svg','--mode-single','--mirror','--exclude-drawing-sheet','--layers','B.Cu,B.Silkscreen,Edge.Cuts','--page-size-mode','2','--output',str(R/'placement-bottom.svg'),str(P)],check=True,capture_output=True)
back=R/'placement-bottom.svg';back.write_text('\n'.join(line.rstrip() for line in back.read_text().splitlines())+'\n')
svg=R/'placement.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
result={'status':'PASS for connectivity and documented placement constraints; not routing or fabrication',
 'physical_components':len(plan),'mounting_holes':4,'checked_functional_pin_assignments':checked,
 'schematic_parity_findings':len(drc['schematic_parity']),'socket_contacts_checked':86,
 'rp_reference_footprints_and_positions_checked':6,'local_control_bypass_caps_checked':len(local),
 'maximum_control_cap_center_to_power_pad_mm':round(max(local),3),'copper_layers':4,
 'outline_mm':[o['width_mm'],o['height_mm']],'component_free_band_mm':mechanical['component_free_depth_mm'],
 'rightmost_non_socket_courtyard_or_pad_x_mm':round(rightmost,3),
 'visible_reference_labels':len(fs),'reference_font_mm':.9,'native_component_groups':len(group_report['groups']),
 'grouped_components':group_report['grouped_components'],'local_supply_capacitors':power_distances,
 'backside_components':['C42','C43'],'power_cell_positions_checked':len(power_moves),
 'tracks':len(b.GetTracks()),'drc_violations_retained':dict(collections.Counter(x['type'] for x in drc['violations'])),
 'unconnected_items':len(drc['unconnected_items']),'stackup_and_usb_geometry':'not qualified'}
(R/'pcb-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
