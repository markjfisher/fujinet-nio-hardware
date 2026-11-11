"""Provisional top-access envelopes: read-only geometric check, not enclosure certification."""
import pcbnew as k,json,math
from pathlib import Path
o=Path(__file__).resolve().parent;b=k.LoadBoard(str(o/'candidate/integrated-a500-r5.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()}
def rect(f):
 q=f.GetCourtyard(k.F_CrtYd).BBox();return[q.GetX()/1e6,q.GetY()/1e6,q.GetRight()/1e6,q.GetBottom()/1e6]
def hit(a,b):return min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1])
envelopes={'J31':[25.5,6.5,40.66,11.5],'J20':[46.5,6.5,61.66,11.5],'J2':[3,107,15,118],'J60':[16,110,24.54,116]}
for ref,a in envelopes.items():
 for name,f in fs.items():
  if name!=ref:assert not hit(a,rect(f)),(ref,name,rect(f))
buttons={}
for ref in ['SW1','SW2','SW3','SW4']:
 f=fs[ref];x,y=f.GetPosition().x/1e6+3.25,f.GetPosition().y/1e6+2.25
 assert x-5>=-6 and x+5<=105 and y-5>=3.5 and y+5<=120.5
 for name,g in fs.items():
  if name==ref:continue
  l,t,r,bt=rect(g);assert math.hypot(max(l-x,0,x-r),max(t-y,0,y-bt))>=5,(ref,name)
 buttons[ref]={'actuator_center_mm':[x,y],'top_access_radius_mm':5}
(o/'access-envelopes.json').write_text(json.dumps({'status':'provisional; actual plug/shunt/actuator and enclosure dimensions unverified','header_access_rectangles_mm':envelopes,'button_access':buttons},indent=2)+'\n');print('PASS provisional top-access envelopes clear other component courtyards')
