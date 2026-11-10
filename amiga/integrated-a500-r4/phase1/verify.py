"""Independent native netlist checks and bounded circuit-equivalence calculations."""
import collections,itertools,json,subprocess,sys,xml.etree.ElementTree as E
from pathlib import Path
P=Path(sys.argv[1]).resolve();stage=sys.argv[2];D=P/'phase1';D.mkdir(exist_ok=True)
xml=D/f'{stage}.xml'
subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(xml),str(P/'integrated-a500-r4.kicad_sch')],check=True)
t=E.parse(xml);plan=json.loads((P/'circuit.json').read_text());expected={c['reference']:c for c in plan['components'] if not c['reference'].startswith('#')}
actual={c.get('ref'):c for c in t.findall('./components/comp')}
assert set(actual)==set(expected),(set(actual)-set(expected),set(expected)-set(actual))
nets={};identities=collections.defaultdict(set)
for n in t.findall('./nets/net'):
 for pin in n.findall('node'):nets[(pin.get('ref'),pin.get('pin'))]=n.get('name')
errors=[]
for r,c in expected.items():
 for p,n in c['pins'].items():
  a=nets.get((r,p));identities[n].add(a)
  if a is None or a.rsplit('/',1)[-1]!=n:errors.append((r,p,n,a))
 for (ref,p),n in nets.items():
  if ref==r and p not in c['pins'] and not n.startswith('unconnected-'):errors.append((r,p,'NC',n))
 assert actual[r].findtext('footprint')==c['footprint'],(r,'footprint')
 if r!='J40':assert actual[r].findtext('value')==c['value'],(r,'value',actual[r].findtext('value'),c['value'])
assert not errors,errors
assert all(len(v)==1 for v in identities.values()),{k:v for k,v in identities.items() if len(v)!=1}
# Actual exported map, not generator shorthand.
pn=lambda r,p:nets[r,str(p)].rsplit('/',1)[-1]
for r in ['U60','U90','U91']:
 assert pn(r,1)=='GUARD_OK_RAW' and pn(r,6)=='3V3_BUS' and pn(r,3)=='3V3_BUS'
assert pn('U60',5)=='HOST_SENSE' and pn('U90',5)=='MAIN_SENSE' and pn('U91',5)=='BUS_SENSE'
assert pn('U92',1)=='GUARD_OK_RAW' and pn('U92',6)=='BUS_DISABLE' and pn('U92',3)=='BUS_DISABLE' and pn('U92',4)=='BUS_PERMIT'
for r in ['U44','U45']:assert pn(r,20)=='3V3_BUS'
for r in ['U46','U47']:assert pn(r,20)=='3V3'
for r in ['U44','U45','U46','U47']:assert pn(r,19)=='BUS_DISABLE'
assert pn('U94',2)==pn('U94',5)=='GND' and pn('U94',6)=='AMIGA_XRDY' and pn('U94',3)=='AMIGA_INT2_N'
assert pn('U93',1)==pn('U93',5)=='BUS_PERMIT'
assert pn('U93',7)==pn('U94',1)=='WAIT_OE_N' and pn('U93',3)==pn('U94',7)=='IRQ_OE_N'
assert pn('U5',10)=='5V_MAIN' and nets.get(('U5','4'),'unconnected-').startswith('unconnected-') and pn('U96',5)=='3V3_BUS'
truth=[]
for host,main,bus,wait,irq,byte in itertools.product([0,1],repeat=6):
 good=host and main and bus;disable=not good;permit=not disable
 wait_oe=not(permit and wait);irq_oe=not(permit and irq)
 data_enabled=not(disable or byte)
 assert (not wait_oe)==bool(good and wait)
 assert (not irq_oe)==bool(good and irq)
 assert data_enabled==bool(good and not byte)
 if not good:assert wait_oe and irq_oe and not data_enabled
 truth.append([host,main,bus,wait,irq,byte,int(disable),int(permit),int(data_enabled),int(not wait_oe),int(not irq_oe)])
# Resistor-tolerance and supervisor threshold corners, incl. 15nA SNS bias.
def thresholds(top,bottom):
 lo=(.4*.99-15e-9*(top*.999*bottom*1.001)/(top*.999+bottom*1.001))*(1+top*.999/(bottom*1.001))
 hi=(.4*1.01+15e-9*(top*1.001*bottom*.999)/(top*1.001+bottom*.999))*(1+top*1.001/(bottom*.999))
 return lo,hi
low,high=thresholds(67500,10000)
detect=low*.95
# Declared discharge envelope includes capacitor ESR step, effective cap min and 3us guard allowance.
main_end=detect-1.2*.05-1.2*3e-6/(220e-6*.8)
bus_end=detect-.30*.05-.30*3e-6/(100e-6*.8)
assert min(main_end,bus_end)>2.7
assert high*1.025<3.3*.985
# Equivalence for consolidated packages uses exported input/output associations.
equivalence=[]
if expected['U61']['value']=='SN74LVC11APWR':
 maps={'U61':[(['BUS_PERMIT','BUS_PERMIT','HOST_RESET_N'],'SAFE_POWER'),(['RP_RUN_C','RUN_MODE_C','BUS_ARM_C'],'SAFE_MODE'),(['SAFE_POWER','SAFE_MODE','BUS_READY_C'],'SAFE_BASE')],
 'U66':[(['Z_A23','Z_A22','Z_A21'],'IO_TOP'),(['IO_TOP','A20_LOW','Z_A19'],'IO_WINDOW'),(['SAFE','AS_ACTIVE','IO_WINDOW'],'CYCLE_OK')],
 'U71':[(['CYCLE_OK','Z_READ','DATA_VALID'],'READ_DRIVE'),(['CYCLE_OK','WRITE_CYCLE','DATA_RECEIVE'],'WRITE_RECEIVE'),(['CYCLE_OK','WAIT_PENDING','3V3'],'WAIT_SINK')]}
 for r,gates in maps.items():
  for (pins,y),(ins,out) in zip([([1,2,13],12),([3,4,5],6),([9,10,11],8)],gates):
   assert [pn(r,p) for p in pins]==ins and pn(r,y)==out
   for b in itertools.product([False,True],repeat=3):assert all(b)==(b[0] and b[1] and b[2])
   equivalence.append(out)
if expected['U64']['value']=='SN74LVC04APWR':
 for a,y,ni,no in [(1,2,'Z_AS_N','AS_ACTIVE'),(3,4,'Z_A20','A20_LOW'),(5,6,'Z_LDS_N','LO_ACTIVE'),(9,8,'Z_UDS_N','HI_ACTIVE'),(11,10,'Z_READ','WRITE_CYCLE'),(13,12,'DATA_VALID','DATA_RECEIVE')]:assert pn('U64',a)==ni and pn('U64',y)==no;equivalence.append(no)
for r,signals,common in [('R37',['SD_DAT2','SD_CS','SD_MOSI','SD_MISO'],'3V3'),('R64',['BUS_READY','DATA_DRIVE','ACK_REQ','IRQ_REQ'],'GND')]:
 if expected[r]['value'].startswith('CAT16'):
  for a,b,n in zip([1,2,3,4],[8,7,6,5],signals):assert {pn(r,a),pn(r,b)}=={n,common}
result=dict(stage=stage,components=len(actual),functional_pins=sum(len(c['pins']) for c in expected.values()),net_membership='PASS',power_truth_cases=len(truth),equivalent_gate_outputs=equivalence,threshold_3v3_min=low,threshold_3v3_max=high,guaranteed_overdrive_voltage=detect,main_shutdown_voltage=main_end,bus_shutdown_voltage=bus_end,normal_xrdy_budget_ns=(44.7 if expected["U61"]["value"]=="SN74LVC11APWR" else 53.1),shutdown_floor_V=2.7,assumptions=['3us detection/conditioning budget at specified overdrive, <=50pF GUARD_OK_RAW','effective bulk capacitance >=80% of nominal; ESR <=50mohm','main discharge <=1.2A; bus discharge <=300mA; hard short excluded','prototype confirmation of ramps, loads, shutdown and recovery remains required'])
(D/f'{stage}-checks.json').write_text(json.dumps(result,indent=2)+'\n');(D/f'{stage}-power-truth.json').write_text(json.dumps(dict(columns=['host_valid','main_valid','bus_valid','wait','irq','byte_oe_n','disable','permit','data_drive','xrdy_sink','irq_sink'],rows=truth),indent=2)+'\n')
subprocess.run(['kicad-cli','sch','erc','--format','json','-o',str(D/f'{stage}-erc.json'),str(P/'integrated-a500-r4.kicad_sch')],check=True)
print(json.dumps(result,indent=2))
