"""Read-only geometric planner for circuit-defined cells; outputs MCP moves.

Power and ground are not used to infer functional ownership. The manifest
explicitly pairs each bypass capacitor with its load. Reserved RP/flash and
USB regions keep the logic placer out of the critical analogue/USB layout.
"""
from pathlib import Path
import json,math,pcbnew as k
ROOT=Path(__file__).resolve().parent;b=k.LoadBoard(str(ROOT/'integrated-a500-r4.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()}
def xy(f):return k.ToMM(f.GetPosition().x),k.ToMM(f.GetPosition().y)
def bbox(f):
 layer=k.F_Fab if f.GetReference()=='U30' else k.F_CrtYd
 items=[s for s in f.GraphicalItems() if s.GetLayer()==layer]+list(f.Pads())
 if not items:items=list(f.Pads())
 boxes=[s.GetBoundingBox() for s in items]
 return [min(k.ToMM(s.GetX()) for s in boxes),min(k.ToMM(s.GetY()) for s in boxes),max(k.ToMM(s.GetRight()) for s in boxes),max(k.ToMM(s.GetBottom()) for s in boxes)]
def moved(ref,x,y):
 ox,oy=xy(fs[ref]);bb=bbox(fs[ref]);return [bb[0]+x-ox,bb[1]+y-oy,bb[2]+x-ox,bb[3]+y-oy]
def overlap(a,z,gap=.25):return a[0]<z[2]+gap and a[2]>z[0]-gap and a[1]<z[3]+gap and a[3]>z[1]-gap
pairs={f'U{61+i}':f'C{70+i}' for i in range(23)};pairs.update(U60='C60',U84='C93',U85='C94',U86='C95')
extras={'U60':['R60','R61','R62'],'U62':['R63','R3'],'U63':['R64'],'U84':['R66'],'U86':['R65'],'U82':['R67']}
bypass={'C1':('U1','10'),'C2':('U2','10'),'C3':('U3','12'),'C40':('U30','2'),'C41':('U30','2'),'C42':('J30','4'),'C43':('J30','4')}
esp_moves={'Q4':(11.2,17.67),'R12':(11.2,13.5),'R30':(10.5,42),'R31':(14,42),'R33':(17,33),'C10':(.5,44)}
sd_moves={f'R{37+i}':(16.5,55.5+3*i) for i in range(5)}
rp_moves={'R13':(47,38)}
movers=set(rp_moves)|set(esp_moves)|set(sd_moves)|set(pairs)|set(pairs.values())|{r for rs in extras.values() for r in rs}|set(bypass)
occupied={r:bbox(f) for r,f in fs.items() if r not in movers}
moves=[];groups=[];placements={}
def legal(boxes,guard=True):
 for bb in boxes.values():
  if bb[0]<-5.5 or bb[1]<4 or bb[2]>87 or bb[3]>120: return False
  if any(overlap(bb,z) for z in occupied.values()):return False
  if guard and overlap(bb,[42,38,70,78],0):return False
 vals=list(boxes.values())
 return not any(overlap(a,z,.1) for i,a in enumerate(vals) for z in vals[i+1:])
def save_group(name,coords):
 for ref,(x,y) in coords.items():
  occupied[ref]=moved(ref,x,y);placements[ref]=(x,y)
  moves.append({'reference':ref,'x_mm':round(x,4),'y_mm':round(y,4)})
 groups.append({'name':name,'members':list(coords)})
for name,coords in [('RP boot bias',rp_moves),('ESP recovery and USB',esp_moves),('SD pullups',sd_moves)]:
 assert legal({r:moved(r,*pos) for r,pos in coords.items()},guard=False),name
 save_group(name,coords)
order=['U61','U62','U63','U85','U64','U65','U66','U67','U68','U69','U70','U79','U84','U86','U71','U72','U73','U74','U75','U76','U77','U78','U80','U81','U82','U83','U60']
# Repeated local cell: IC + bypass at its supply side, with bias parts below.
# Native geometry rejects occupied cells rather than squeezing parts together.
slots=[(22+9*i,16+9*j) for j in range(3) for i in range(6)]
slots += [(22+9*i,43+9*j) for j in range(4) for i in range(2)]
slots += [(48+9*i,85+9*j) for j in range(2) for i in range(3)]
for ic in order:
 chosen=None
 options=[(52,94)]+slots if ic=='U60' else slots
 for x,y in options:
  coords={ic:(x,y),pairs[ic]:(x+4.1,y-.95)}
  for i,ref in enumerate(extras.get(ic,[])):
   coords[ref]=(x+4.1,y+2.2+2.3*i) if i<2 else (x,y+4.5)
  if legal({r:moved(r,*pos) for r,pos in coords.items()}):chosen=coords;break
 if chosen is None:raise RuntimeError('No legal cell for '+ic)
 save_group('Logic '+ic,chosen)
# Place the previously global-power-centroid capacitors near actual power pads.
# Smallest decouplers go first; bulky reservoirs follow.
distances=[]
for cap in ['C1','C2','C3','C41','C40']:
 ic,pin=bypass[cap];pad=next(p for p in fs[ic].Pads() if p.GetNumber()==pin);px,py=k.ToMM(pad.GetPosition().x),k.ToMM(pad.GetPosition().y)
 choices=[]
 for radius in [1.5+i*.5 for i in range(24)]:
  for angle in range(0,360,15):
   x=px+radius*math.cos(math.radians(angle));y=py+radius*math.sin(math.radians(angle))
   if legal({cap:moved(cap,x,y)},guard=False):choices.append((radius,round(x,4),round(y,4)))
  if choices:break
 if not choices:raise RuntimeError('No bypass location for '+cap)
 distance,x,y=min(choices);save_group('Bypass '+cap+' for '+ic,{cap:(x,y)})
 distances.append({'capacitor':cap,'load':ic,'power_pin':pin,'center_to_power_pad_mm':distance})
# SD supply decoupling fits directly behind the socket power pad on B.Cu.
# The MCP move operation has no side-change operation: native API flips only
# these two footprints after moves; final DRC validates the two-sided result.
for cap,x,y in [('C43',-3,62.8),('C42',.5,64.5)]:
 save_group('Bypass '+cap+' for J30',{cap:(x,y)})
 distances.append({'capacitor':cap,'load':'J30','power_pin':'4','center_to_power_pad_mm':round(math.hypot(x+4.405,y-62.845),3),'side':'B.Cu'})
# Include fixed critical cells as selectable groups without moving them.
groups += [
 {'name':'RP regulator reference cell','members':['U20','L20','R24','C23','C24','C25']},
 {'name':'RP crystal','members':['Y20','R21','C21','C22']},
 {'name':'RP QSPI flash','members':['U21','R20','C20','R13']},
 {'name':'USB switch RP','members':['U1','C1']},
 {'name':'USB switch ESP','members':['U2','C2']},
 {'name':'USB CC detection','members':['U3','C3']},
 {'name':'ESP local supply','members':['U30','C40','C41']},
 {'name':'microSD local supply','members':['J30','C42','C43']}]
groups=[g for g in groups if not g['name'].startswith('Bypass ') and g['name']!='RP boot bias']
for i in range(8):groups.append({'name':f'Bus buffer U{40+i}','members':[f'U{40+i}',f'C{50+i}']})
result={'moves':moves,'groups':groups,'bypass_loads':pairs,'local_power_distances':distances,'backside':['C42','C43']}
(ROOT/'review/cluster-plan.json').write_text(json.dumps(result,indent=2)+'\n')
print('Planned',len(moves),'moves in',len(groups),'groups');print(json.dumps(distances,indent=2))
