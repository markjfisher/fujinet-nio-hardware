"""Independent native PCB/schematic parity, contact geometry, and placement checks."""
from pathlib import Path
import json,math,subprocess,collections,xml.etree.ElementTree as E
import pcbnew as k
ROOT=Path(__file__).resolve().parent;P=ROOT/'integrated-a500-r4.kicad_pcb';R=ROOT/'review'
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
 f=fs[item['reference']];x,y=item['fixed']
 assert math.hypot(k.ToMM(f.GetPosition().x)-x,k.ToMM(f.GetPosition().y)-y)<1e-5,item
 assert abs((f.GetOrientationDegrees()-item['rotation'])%360)<1e-5,item
local=[]
for m in json.loads((R/'bypass-placement.json').read_text())['moves']:
 c=fs[m['reference']];u=fs[m['load']];cp=c.GetPosition()
 distance=min(math.hypot(k.ToMM(cp.x-p.GetPosition().x),k.ToMM(cp.y-p.GetPosition().y)) for p in u.Pads() if str(p.GetNetname())=='/3V3')
 assert distance<5.01,(m,distance)
 local.append(distance)
assert b.GetCopperLayerCount()==4
subprocess.run(['kicad-cli','pcb','drc','--schematic-parity','--format','json','-o',str(R/'drc.json'),str(P)],check=True,capture_output=True)
drc=json.loads((R/'drc.json').read_text());assert not drc['schematic_parity'],drc['schematic_parity'][:2]
subprocess.run(['kicad-cli','pcb','export','svg','--mode-single','--exclude-drawing-sheet','--layers','F.Cu,F.Silkscreen,Edge.Cuts','--page-size-mode','2','--output',str(R/'placement.svg'),str(P)],check=True,capture_output=True)
svg=R/'placement.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
result={'status':'PASS for connectivity and documented placement constraints; not routing or fabrication',
 'physical_components':len(plan),'mounting_holes':4,'checked_functional_pin_assignments':checked,
 'schematic_parity_findings':len(drc['schematic_parity']),'socket_contacts_checked':86,
 'rp_reference_footprints_and_positions_checked':6,'local_control_bypass_caps_checked':len(local),
 'maximum_control_cap_center_to_power_pad_mm':round(max(local),3),'copper_layers':4,
 'tracks':len(b.GetTracks()),'drc_violations_retained':dict(collections.Counter(x['type'] for x in drc['violations'])),
 'unconnected_items':len(drc['unconnected_items']),'stackup_and_usb_geometry':'not qualified'}
(R/'pcb-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
