"""Annotate native KiCad plot with actual pad nets and proposed via sites; no CAD edits."""
import pcbnew as k,json,re,html,csv
from pathlib import Path
o=Path(__file__).resolve().parent;b=k.LoadBoard(str(o/'candidate/integrated-a500-r5.kicad_pcb'));checks=json.loads((o/'verification.json').read_text());refs=set(checks['changed_references']);raw=(o/'native.svg').read_text();raw='\n'.join(x.rstrip()for x in raw.splitlines())+'\n';(o/'native.svg').write_text(raw);labels=[];rows=[]
for f in b.GetFootprints():
 if f.GetReference()not in refs:continue
 seen=set();seen_positions=set()
 for p in f.Pads():
  key=p.GetNumber()
  if not key or key in seen:continue
  seen.add(key);x,y=p.GetPosition().x/1e6+6,p.GetPosition().y/1e6-3.5;net=p.GetNetname();short=net.rsplit('/',1)[-1];text=key+':'+short
  rows.append([f.GetReference(),key,net,x-6,y+3.5])
  if (x,y,net)in seen_positions:continue
  seen_positions.add((x,y,net));q=p.GetBoundingBox();w,h=q.GetWidth()/1e6,q.GetHeight()/1e6;angle=-90 if h>w else 0;size=min(min(w,h)*.45,max(w,h)*.86/(max(len(text),1)*.62),.16)
  labels.append(f'<text transform="translate({x} {y}) rotate({angle})" text-anchor="middle" dominant-baseline="central" font-family="DejaVu Sans Mono" font-size="{size}" fill="white" stroke="none">{html.escape(text)}</text>')
for v in checks['prospective_ground_vias']:
 x,y=v['via_xy_mm'];x+=6;y-=3.5;labels.append(f'<circle cx="{x}" cy="{y}" r=".3" fill="none" stroke="#4fffc3" stroke-width=".04" stroke-dasharray=".08 .04"/><circle cx="{x}" cy="{y}" r=".15" fill="none" stroke="#4fffc3" stroke-width=".03"/>')
annotated=raw.replace('</svg>','<g>'+''.join(labels)+'</g></svg>')
for name,box,w,h in [('irq-pad-nets','31 10 18 13',18,13),('qualifier-pad-nets','52 38 30 25',30,25),('latches-pad-nets','35 68 43 22',43,22),('enables-pad-nets','52 87 26 20',26,20),('context','0 0 111 117',111,117)]:
 s=re.sub(r'width="[^"]+mm" height="[^"]+mm" viewBox="[^"]+"',f'width="{w}mm" height="{h}mm" viewBox="{box}"',annotated,count=1);(o/(name+'.svg')).write_text(s)
with (o/'pad-nets.csv').open('w')as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['reference','pad','net','x_mm','y_mm']);w.writerows(rows)
