"""Independent native KiCad connectivity, ERC and hardware-logic checks. No CAD edits."""
import csv
import itertools
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
REVIEW=ROOT/'review'
SCH=ROOT/'integrated-a500-r3.kicad_sch'
def run(*args):subprocess.run(args,check=True,cwd=ROOT,capture_output=True,text=True)
def main():
 plan=json.loads((ROOT/'circuit.json').read_text())
 run('kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(REVIEW/'netlist.xml'),str(SCH))
 run('kicad-cli','sch','erc','--format','json','-o',str(REVIEW/'erc.json'),str(SCH))
 tree=ET.parse(REVIEW/'netlist.xml');actual={};nets={}
 for n in tree.findall('./nets/net'):
  nets[n.get('name')]={(p.get('ref'),p.get('pin')) for p in n.findall('node')}
  for key in nets[n.get('name')]:
   assert key not in actual,key
   actual[key]=n.get('name')
 expected=defaultdict(set)
 for c in plan['components']:
  if c['reference'].startswith('#'):continue
  for pin,n in c['pins'].items():expected[n].add((c['reference'],pin))
 # Whole-net membership, not merely labels or a count of parts. This catches
 # accidental shorts, disconnected hierarchy and duplicated local net names.
 for name,pins in expected.items():
  connected={actual.get(k) for k in pins}
  assert len(connected)==1 and None not in connected,(name,connected,pins)
  net=connected.pop()
  assert net.rsplit('/',1)[-1]==name,(name,net)
  assert nets[net]==pins,(name,'unexpected/missing members',nets[net]^pins)
 a={key:net.rsplit('/',1)[-1] for key,net in actual.items()}
 assert {p for r,p in actual if r=='U20'}=={str(i) for i in range(1,82)}
 assert len({a['U20',str(i)] for i in range(1,82)})==len(set(next(c for c in plan['components'] if c['reference']=='U20')['pins'].values()))
 assert [a['U20',str(i)] for i in [79,80,1,2,3,4]]==[f'Z_A{i}' for i in range(2,8)]
 assert a['U20','56']=='IRQ_REQ' and a['U20','57']=='BUS_READY'
 assert a['U20','66']=='RP_USB_DM' and a['U20','67']=='RP_USB_DP'
 # Logic evaluation uses IC pin membership exported by KiCad and the
 # manufacturer's pin functions. It does not use the proposed gate-net list.
 order=[f'U{i}' for i in range(61,64)]+['U85']+[f'U{i}' for i in range(64,84)]
 kinds={c['reference']:c['lib_id'].split('74LVC1G')[-1] for c in plan['components'] if c['reference'] in order}
 def evaluate(inputs):
  v=dict(inputs,**{'3V3':1,'GND':0})
  for r in order:
   k=kinds[r];ps=['1','3','6'] if k in ('10','11') else (['1','2'] if k in ('08','32') else ['2'])
   b=[v[a[r,p]] for p in ps]
   out=(not b[0]) if k in ('04','06') else ((not all(b)) if k=='10' else (any(b) if k=='32' else all(b)))
   v[a[r,'4']]=int(out)
  return v
 safe_inputs=['HOST_PG','3V3_PG','HOST_RESET_N','RP_RUN','RUN_MODE','BUS_ARM','BUS_READY','HOST_BERR_N']
 cases=0
 for safe_bits in itertools.product([0,1],repeat=8):
  for as_n,rd,drive,lds,uds,ack,irq,window in itertools.product([0,1],repeat=8):
   x=dict(zip(safe_inputs,safe_bits))
   x.update(Z_AS_N=as_n,Z_READ=rd,DATA_VALID=drive,Z_LDS_N=lds,Z_UDS_N=uds,WAIT_PENDING=not ack,IRQ_REQ=irq,
            Z_A23=window,Z_A22=1,Z_A21=1,Z_A20=0,Z_A19=1)
   v=evaluate(x);safe=all(safe_bits);cycle=safe and not as_n and window
   assert v['TX_LO_N']==int(not(cycle and rd and drive and not lds))
   assert v['TX_HI_N']==int(not(cycle and rd and drive and not uds))
   assert v['RX_LO_N']==int(not(cycle and not rd and not drive and not lds))
   assert v['RX_HI_N']==int(not(cycle and not rd and not drive and not uds))
   assert v['AMIGA_XRDY']==int(not(cycle and not ack))
   assert v['AMIGA_INT2_N']==int(not(safe and irq))
   assert not(v['TX_LO_N']==0 and v['RX_LO_N']==0)
   assert not(v['TX_HI_N']==0 and v['RX_HI_N']==0)
   cases+=1
 # No board output may drive DTACK. The existing receive buffer is observation only.
 assert expected['AMIGA_DTACK_N']=={('J40','66'),('U43','7')}
 # Manufacturer pin functions: CLK1 D2 /Q3 GND4 Q5 /CLR6 /PRE7 VCC8.
 # Evaluate asynchronous clear and positive edges from saved net membership.
 def latch_step(ref, values, q, previous_clock):
  assert a[ref,'7']=='3V3' and a[ref,'8']=='3V3' and a[ref,'4']=='GND'
  clk=values[a[ref,'1']]
  if not values[a[ref,'6']]:q=0
  elif clk and not previous_clock:q=values[a[ref,'2']]
  return q,clk
 sequential_cases=0
 for ref,clock,pin in [('U84','ACK_REQ','3'),('U86','DATA_DRIVE','5')]:
  assert a[ref,'6']=='CYCLE_OK'
  assert a[ref,pin]==('WAIT_PENDING' if ref=='U84' else 'DATA_VALID')
  # Exhaust five-step sequences of cycle qualification, request and lane state.
  # Includes requests stuck high over back-to-back cycles and asynchronous aborts.
  for events in itertools.product(range(8),repeat=5):
   q=previous=0;reference_q=0;last_request=0
   for e in events:
    cycle,request,lane=(e>>2)&1,(e>>1)&1,e&1
    v={'3V3':1,'CYCLE_OK':cycle,'ANY_LANE':lane,clock:request}
    q,previous=latch_step(ref,v,q,previous)
    if not cycle:reference_q=0
    elif request and not last_request:reference_q=lane if ref=='U84' else 1
    assert q==reference_q
    last_request=request
   sequential_cases+=1
 # Exhaust the five high address bits independently of the safety-state loop.
 for bits in itertools.product([0,1],repeat=5):
  x.update(dict(zip(['Z_A23','Z_A22','Z_A21','Z_A20','Z_A19'],bits)))
  assert evaluate(x)['IO_WINDOW']==int(bits==(1,1,1,0,1))
 # USB paths, both polarities, all physical flash selections.
 for rp,esp,wanted in [(0,0,{('ESP','RP')}),(1,0,{('PC','RP')}),(0,1,{('ESP','PC')}),(1,1,set())]:
  for polarity,common,p1,p2 in [('DP','4','2','3'),('DM','6','8','7')]:
   graph=defaultdict(set)
   for r,sel,oe in [('U1',rp,esp),('U2',esp,rp)]:
    if oe:continue
    u,w=a[r,common],a[r,p2 if sel else p1];graph[u].add(w);graph[w].add(u)
   pairs=set()
   for src in ['PC','RP','ESP']:
    seen=set();todo=[src+'_'+polarity]
    while todo:
     node=todo.pop()
     if node not in seen:seen.add(node);todo.extend(graph[node]-seen)
    for dst in ['PC','RP','ESP']:
     if dst!=src and dst+'_'+polarity in seen:pairs.add(tuple(sorted((src,dst))))
   assert pairs==wanted,(rp,esp,polarity,pairs)
 # ERC findings are retained, not excluded or called a clean pass. Restrict the
 # known model limitation to external A500 inputs and off-sheet pull-ups.
 erc=json.loads((REVIEW/'erc.json').read_text())
 violations=[v for s in erc['sheets'] for v in s['violations']]
 allowed={18,19,46,53,66,68,70,72,74,29,27,26,24,21,23,28,30,32,34,36,38,39,41,43,45,47,52,54,56,58,57,59}
 import re
 found=set()
 grounded_status=0
 for v in violations:
  if v['type']=='pin_to_pin':
   # TI explicitly directs grounding unused LM66100 ST. The old host symbol
   # declares GND a power output, so KiCad flags this valid grounded OD output.
   descriptions=[i['description'] for i in v['items']]
   assert any(s.startswith('Symbol U9 Pin 5 ') for s in descriptions),v
   assert any(s.startswith('Symbol J40 Pin 1 ') for s in descriptions),v
   grounded_status+=1
   continue
  assert v['type']=='pin_not_driven',v
  assert len(v['items'])==1,v
  m=re.match(r'Symbol J40 Pin (\d+) ',v['items'][0]['description']);assert m,v
  found.add(int(m[1]))
 assert found==allowed,(found,allowed)
 assert grounded_status==1
 run('kicad-cli','sch','export','pdf','-o',str(REVIEW/'schematic.pdf'),str(SCH))
 rows=list(csv.DictReader((ROOT.parent/'integrated-r0/rp2350-pin-allocation.csv').open()))
 for r in rows:
  r['candidate_net']=a['U20',r['package_pad']]
  if r['package_pad']=='55':r['function']='completion pulse; rising edge releases XRDY for this cycle; external pulldown'
  if r['package_pad']=='58':r['function']='read-claim pulse; per-cycle latch; external pulldown'
  if r['package_pad']=='59':r['function']='analog supply; local decoupling'
  if r['package_pad']=='61':r['function']='regulator analog supply; 33-ohm/4.7uF filter'
 with (ROOT/'rp2350-pin-allocation.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator="\n");w.writeheader();w.writerows(rows)
 result=dict(scope='A500 R3 circuit candidate; NOT electrical/layout release',components=len(tree.findall('./components/comp')),
  checked_physical_pin_assignments=sum(map(len,expected.values())),exact_nets=len(expected),rp_package_pads=81,
  bus_logic_cases=cases,sequential_cases=sequential_cases,address_decode_cases=32,usb_cases=8,erc_findings_retained=len(violations),
  erc_status='32 external A500 model findings plus manufacturer-directed grounded ST; no exclusions; not zero ERC',
  pcb='not implemented; DRC and parity not applicable')
 (REVIEW/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
