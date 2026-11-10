"""Review-only annotation of native KiCad SVG. Does not write any CAD file."""
import pcbnew as k,json,re,html,csv
from pathlib import Path
r=Path(__file__).resolve().parents[2];out=r/'review/pad-refinement';b=k.LoadBoard(str(r/'integrated-a500-r5.kicad_pcb'));raw=(out/'native.svg').read_text();raw='\n'.join(s.rstrip() for s in raw.splitlines())+'\n';(out/'native.svg').write_text(raw)
refs=set(json.loads((r/'review/milestone-1/verification.json').read_text())['rp_cluster']);labels=[];rows=[]
for f in b.GetFootprints():
 if f.GetReference() not in refs:continue
 seen=set()
 for p in f.Pads():
  key=p.GetNumber()
  if key in seen:continue
  seen.add(key);x,y=p.GetPosition().x/1e6+6,p.GetPosition().y/1e6-3.5
  net=p.GetNetname();short=net.rsplit('/',1)[-1];text=p.GetNumber()+':'+short
  rows.append([f.GetReference(),p.GetNumber(),net,p.GetPosition().x/1e6,p.GetPosition().y/1e6])
  if f.GetReference()=='U20' and p.GetNumber()=='81':continue
  q=p.GetBoundingBox();w,h=q.GetWidth()/1e6,q.GetHeight()/1e6
  angle=-90 if h>w else 0
  length=max(w,h)*0.86;size=min(min(w,h)*0.45,length/(max(len(text),1)*0.62),0.16)
  labels.append(f'<text transform="translate({x} {y}) rotate({angle})" text-anchor="middle" dominant-baseline="central" font-family="DejaVu Sans Mono" font-size="{size}" fill="#ffffff" stroke="none">{html.escape(text)}</text>')
checks=json.loads((out/'pad-checks.json').read_text())
for v in checks['prospective_ground_vias']:
 x,y=v['via_xy_mm'];x+=6;y-=3.5
 labels.append(f'<circle cx="{x}" cy="{y}" r="0.3" fill="none" stroke="#4fffc3" stroke-width="0.04" stroke-dasharray="0.08 0.04"/><circle cx="{x}" cy="{y}" r="0.15" fill="none" stroke="#4fffc3" stroke-width="0.03"/>')
labels.append('<text x="31" y="74" font-family="sans-serif" font-size="0.4" fill="#4fffc3">Green rings: proposed GND vias only; no copper added</text>')
annotated=raw.replace('</svg>','<g>'+''.join(labels)+'</g></svg>')
for name,box,w,h in [('pad-nets','30 35 32 40',32,40),('north-pad-nets','31 39 26 20',26,20),('south-pad-nets','39 59 21 17',21,17)]:
 s=re.sub(r'width="[^"]+mm" height="[^"]+mm" viewBox="[^"]+"',f'width="{w}mm" height="{h}mm" viewBox="{box}"',annotated,count=1);(out/(name+'.svg')).write_text(s)
with (out/'pad-nets.csv').open('w') as f:
 writer=csv.writer(f,lineterminator="\n");writer.writerow(['reference','pad','full_net','x_mm','y_mm']);writer.writerows(rows)
