"""Incremental electrical edits, not a placement/board generator."""
import json,copy
from pathlib import Path
P=Path(__file__).resolve().parent.parent
base=json.loads((P/'phase1/baseline-plan.json').read_text())
C={c['reference']:c for c in base['components']}
stages=[]
def stage(name):
 s={'name':name,'remove':[],'add':[],'rewire':[],'update':[]};stages.append(s);return s
def rm(s,*refs):
 for r in refs:s['remove'].append(copy.deepcopy(C.pop(r)))
def add(s,r,lib,val,pins,fp,page='guard',position=None):
 c=dict(reference=r,lib_id=lib,value=val,pins={str(k):v for k,v in pins.items()},footprint=fp,page=page,position=position or [50+len(s['add'])%7*100,60+len(s['add'])//7*60],rotation=0)
 assert r not in C,r
 C[r]=c;s['add'].append(copy.deepcopy(c))
def rw(s,r,p,n):
 c=C[r];old=c['pins'].get(str(p));s['rewire'].append(dict(reference=r,page=c['page'],pin=str(p),old=old,new=n));c['pins'].pop(str(p),None) if n is None else c['pins'].__setitem__(str(p),n)

def upd(s,r,**kw):
 s['update'].append(dict(reference=r,page=C[r]['page'],**kw));C[r].update(kw)
def cap(s,r,n,v='100n 10V X7R',page='guard',fp='Capacitor_SMD:C_0603_1608Metric'):add(s,r,'Device:C_Polarized' if 'polymer' in v else 'Device:C',v,{1:n,2:'GND'},fp,page)
def res(s,r,a,b,v):add(s,r,'Device:R',v,{1:a,2:b},'Resistor_SMD:R_0603_1608Metric')
def schmitt(s,r,pairs):
 pins={8:'3V3',4:'GND'}
 for (a,y),(raw,out) in zip([(1,7),(3,5),(6,2)],pairs):pins[a]=raw;pins[y]=out
 add(s,r,'Phase1:74LVC3G17','74LVC3G17DC,125',pins,'Package_SO:VSSOP-8_2.3x2mm_P0.5mm')
s=stage('protection')
rm(s,'U60','R60','R61','R62','C60','R9','U81','U83','C90','C92')
add(s,'U95','Phase1:TPS2553','TPS2553DBVR',{1:'AMIGA_5V',2:'GND',3:'AMIGA_5V',5:'HOST_ILIM',6:'HOST_5V_LIMITED'},'Package_TO_SOT_SMD:SOT-23-6')
res(s,'R110','HOST_ILIM','GND','133k 1%');cap(s,'C110','AMIGA_5V')
add(s,'D4','Device:D_Schottky','SS14-13-F',{1:'HOST_LDO_IN',2:'HOST_5V_LIMITED'},'Diode_SMD:D_SMA')
add(s,'U96','Regulator_Linear:AP2112K-3.3','AP2112K-3.3TRG1',{1:'HOST_LDO_IN',2:'GND',3:'HOST_LDO_IN',5:'3V3_BUS'},'Package_TO_SOT_SMD:SOT-23-5')
cap(s,'C111','HOST_LDO_IN','1u 10V X7R');cap(s,'C112','3V3_BUS','1u 10V X7R')
cap(s,'C113','3V3_BUS','100u 6.3V polymer 20% ESR<=50m',fp='Capacitor_SMD:CP_Elec_6.3x5.8')
res(s,'R111','3V3_BUS','GND','4.7k 1%')
for r,sense,ct,top,bot,supply,ctref,byref in [('U60','HOST_SENSE','HOST_CT','R60','R61','AMIGA_5V','C114','C60'),('U90','MAIN_SENSE','MAIN_CT','R112','R113','3V3','C115','C118'),('U91','BUS_SENSE','BUS_CT','R114','R115','3V3_BUS','C116','C119')]:
 add(s,r,'Phase1:MIC2790H','MIC2790H-04VD6-TR',{1:'GUARD_OK_RAW',2:'GND',3:'3V3_BUS',4:ct,5:sense,6:'3V3_BUS'},'Package_TO_SOT_SMD:TSOT-23-6')
 res(s,top,supply,sense,'102k 0.1%' if r=='U60' else '67.5k 0.1%');res(s,bot,sense,'GND','10k 0.1%');cap(s,ctref,ct,'100p 25V C0G 5%');cap(s,byref,'3V3_BUS','1u 10V X7R')
res(s,'R116','3V3_BUS','GUARD_OK_RAW','10k 1%')
add(s,'U92','Phase1:SN74LVC2G14','SN74LVC2G14DBVR',{1:'GUARD_OK_RAW',6:'BUS_DISABLE',3:'BUS_DISABLE',4:'BUS_PERMIT',2:'GND',5:'3V3_BUS'},'Package_TO_SOT_SMD:SOT-23-6');cap(s,'C120','3V3_BUS')
res(s,'R117','3V3_BUS','BUS_DISABLE','100k 1%');res(s,'R122','BUS_PERMIT','GND','10k 1%')
add(s,'U93','Phase1:SN74LVC2G132','SN74LVC2G132DCUR',{1:'BUS_PERMIT',2:'WAIT_SINK',7:'WAIT_OE_N',5:'BUS_PERMIT',6:'IRQ_SINK',3:'IRQ_OE_N',4:'GND',8:'3V3_BUS'},'Package_SO:VSSOP-8_2.3x2mm_P0.5mm');cap(s,'C121','3V3_BUS')
add(s,'U94','Phase1:SN74LVC2G125','SN74LVC2G125DCUR',{1:'WAIT_OE_N',2:'GND',6:'AMIGA_XRDY',7:'IRQ_OE_N',5:'GND',3:'AMIGA_INT2_N',4:'GND',8:'3V3_BUS'},'Package_SO:VSSOP-8_2.3x2mm_P0.5mm');cap(s,'C122','3V3_BUS')
res(s,'R118','3V3_BUS','WAIT_OE_N','100k 1%');res(s,'R119','3V3_BUS','IRQ_OE_N','100k 1%')
add(s,'Q5','Transistor_BJT:MMBT3904','MMBT3904-7-F',{1:'GUARD_RESET_BASE',2:'GND',3:'RP_RUN'},'Package_TO_SOT_SMD:SOT-23')
res(s,'R120','BUS_DISABLE','GUARD_RESET_BASE','22k 1%');res(s,'R121','GUARD_RESET_BASE','GND','100k 1%')
cap(s,'C117','3V3','220u 6.3V polymer 20% ESR<=50m',fp='Capacitor_SMD:CP_Elec_6.3x5.8')
for r in ['U44','U45']:rw(s,r,20,'3V3_BUS')
for r in ['C54','C55']:rw(s,r,1,'3V3_BUS')
for r in ['U44','U45','U46','U47']:rw(s,r,19,'BUS_DISABLE')
rw(s,'U5',4,None);rw(s,'U61',1,'BUS_PERMIT');rw(s,'U61',3,'BUS_PERMIT')
# Condition only released safety/mode/request inputs in this implementation.
schmitt(s,'U97',[(x,x+'_C') for x in ['RP_RUN','RUN_MODE','BUS_ARM']]);cap(s,'C125','3V3')
schmitt(s,'U98',[(x,x+'_C') for x in ['BUS_READY','DATA_DRIVE','ACK_REQ']]);cap(s,'C126','3V3')
add(s,'U99','74xGxx:74LVC1G17','SN74LVC1G17DBVR',{2:'IRQ_REQ',4:'IRQ_REQ_C',3:'GND',5:'3V3'},'Package_TO_SOT_SMD:SOT-23-5');cap(s,'C127','3V3')
for p,n in [(1,'RP_RUN_C'),(3,'RUN_MODE_C'),(6,'BUS_ARM_C')]:rw(s,'U62',p,n)
rw(s,'U63',6,'BUS_READY_C');rw(s,'U84',1,'ACK_REQ_C');rw(s,'U86',1,'DATA_DRIVE_C');rw(s,'U82',2,'IRQ_REQ_C')
# Protect slow open-collector host reset / bus-error / receive-only DTACK inputs.
schmitt(s,'U100',[(x,x+'_C') for x in ['AMIGA_RESET_N','AMIGA_BERR_N','AMIGA_DTACK_N']]);cap(s,'C128','3V3')
for pin,net in [(6,'AMIGA_RESET_N_C'),(8,'AMIGA_BERR_N_C'),(7,'AMIGA_DTACK_N_C')]:rw(s,'U43',pin,net)
# Same five-pin layout and logic polarity, real Schmitt input for CC status.
upd(s,'U7',lib_id='74xGxx:74LVC1G14',value='SN74LVC1G14DBVR')
cap(s,'C123','3V3_AON',page='power');C['C123']['position']=[350,200];s['add'][-1]['position']=[350,200]
cap(s,'C124','5V_MAIN',page='power');C['C124']['position']=[350,250];s['add'][-1]['position']=[350,250]
# Stage snapshots are pin intent, independent of native CAD export.
add(s,'#FLG10','power:PWR_FLAG','PWR_FLAG',{1:'HOST_LDO_IN'},'',position=[750,60])
s['expected']=copy.deepcopy(list(C.values()))
s=stage('I1')
for r,olds,capkeep,caps in [('U61',['U61','U62','U63'],'C70',['C71','C72']),('U66',['U66','U67','U68'],'C75',['C76','C77']),('U71',['U71','U76','U80'],'C80',['C85','C89'])]:
 pins={14:'3V3',7:'GND'};pos={'U61':[550,120],'U66':[680,120],'U71':[550,260]}[r];page=C[r]['page']
 for old,(a,b,c,y) in zip(olds,[(1,2,13,12),(3,4,5,6),(9,10,11,8)]):
  p=C[old]['pins'];pins.update({a:p['1'],b:p['3'],c:p['6'],y:p['4']})
 rm(s,*olds,*caps);add(s,r,'Phase1:SN74LVC11A','SN74LVC11APWR',pins,'Package_SO:TSSOP-14_4.4x5mm_P0.65mm',page,pos)
s['expected']=copy.deepcopy(list(C.values()))
s=stage('I2');pins={14:'3V3',7:'GND'};pos=[680,260]
for r,a,y in [('U64',1,2),('U65',3,4),('U69',5,6),('U70',9,8),('U74',11,10),('U75',13,12)]:pins[a]=C[r]['pins']['2'];pins[y]=C[r]['pins']['4']
rm(s,'U64','U65','U69','U70','U74','U75','C74','C78','C79','C83','C84');add(s,'U64','Phase1:SN74LVC04A','SN74LVC04APWR',pins,'Package_SO:TSSOP-14_4.4x5mm_P0.65mm','control',pos)
s['expected']=copy.deepcopy(list(C.values()))
for name,refs,val in [('R-A',['R37','R38','R39','R40'],'CAT16-4702F4LF'),('R-B',['R64','R65','R66','R67'],'CAT16-1002F4LF')]:
 s=stage(name);pins={};pos=[550,120] if name=='R-A' else [680,400];page=C[refs[0]]['page']
 for r,a,b in zip(refs,[1,2,3,4],[8,7,6,5]):pins[a]=C[r]['pins']['1'];pins[b]=C[r]['pins']['2']
 rm(s,*refs);add(s,refs[0],'Device:R_Pack04',val,pins,'Resistor_SMD:R_Array_Concave_4x0603',page,pos);s['expected']=copy.deepcopy(list(C.values()))
(P/'phase1/stages.json').write_text(json.dumps(stages,indent=2)+'\n')
print([(s['name'],len(s['expected'])) for s in stages])
