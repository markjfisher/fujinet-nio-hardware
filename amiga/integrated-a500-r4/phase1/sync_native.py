"""Native KiCad API for MCP gaps: removal, UUID binding and exact net read-back."""
import sys,json,xml.etree.ElementTree as E
from pathlib import Path
import pcbnew as k
P=Path(sys.argv[1]).resolve();stage=sys.argv[2];mode=sys.argv[3];pcb=P/'integrated-a500-r4.kicad_pcb';D=P/'phase1'
t=E.parse(D/f'{stage}.xml');comps={c.get('ref'):c for c in t.findall('./components/comp')};b=k.LoadBoard(str(pcb))
fs={f.GetReference():f for f in b.GetFootprints()}
def signature(f):return dict(position=[f.GetPosition().x,f.GetPosition().y],angle=f.GetOrientationDegrees(),side=f.GetLayer(),uuid=f.m_Uuid.AsString(),locked=f.IsLocked())
if mode=='prepare':
 before={r:signature(f) for r,f in fs.items()};adds=[];removed=[]
 for r,f in fs.items():
  if r not in comps and r not in ['H1','H2','H3','H4'] or r in comps and str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName())!=comps[r].findtext('footprint'):
   for g in b.Groups():
    if f in list(g.GetItems()):g.RemoveItem(f)
   b.Remove(f);removed.append(r)
 for r,c in comps.items():
  if r not in fs or r in removed:
   fid=c.findtext('footprint');lib,fp=fid.split(':',1)
   # Staging area outside the fixed outline; never globally reposition existing parts.
   used=len(adds);x=125+(used%8)*12;y=10+(used//8)*12
   # Keep separate-stage additions apart from the protection staging group.
   y+= {'protection':0,'I1':100,'I2':120,'R-A':140,'R-B':160}[stage]
   adds.append(dict(reference=r,value=c.findtext('value'),library=lib,footprint_name=fp,x_mm=x,y_mm=y,rotation_deg=0,check_keepouts=False))
 k.SaveBoard(str(pcb),b)
 (D/f'{stage}-sync.json').write_text(json.dumps(dict(before=before,removed=removed,add=adds),indent=2)+'\n')
 print('Incremental sync:',len(removed),'removed/replaced,',len(adds),'added')
else:
 expected={(n.get('ref'),n.get('pin')):(net.get('name').replace('/','{slash}') if net.get('name').startswith('unconnected-') else net.get('name')) for net in t.findall('./nets/net') for n in net.findall('node')}
 records=json.loads((D/f'{stage}-sync.json').read_text());changed=[]
 for f in b.GetFootprints():
  r=f.GetReference()
  if r not in comps:assert r in ['H1','H2','H3','H4'];continue
  c=comps[r];f.SetValue(c.findtext('value'));f.SetPath(k.KIID_PATH(c.find('sheetpath').get('tstamps')+c.findtext('tstamps')))
  f.SetFPID(k.LIB_ID(*c.findtext('footprint').split(':',1)))
  for field in ['Datasheet','Description']:f.GetField(field).SetText(c.findtext("./fields/field[@name='"+field+"']") or '')
  for pad in f.Pads():
   n=expected.get((r,pad.GetNumber()))
   if n and str(pad.GetNetname())!=n:
    target=b.FindNet(n)
    if target is None or target.GetNetCode()<0:target=k.NETINFO_ITEM(b,n);b.Add(target)
    pad.SetNet(target);changed.append([r,pad.GetNumber(),n])
   elif not n:pad.SetNetCode(0)
 k.SaveBoard(str(pcb),b);b=k.LoadBoard(str(pcb));fs={f.GetReference():f for f in b.GetFootprints()}
 assert set(fs)==set(comps)|{'H1','H2','H3','H4'}
 for r,f in fs.items():
  if r in records['before'] and r not in records['removed']:assert signature(f)==records['before'][r],('placement changed',r)
  if r not in comps:continue
  for pad in f.Pads():
   n=expected.get((r,pad.GetNumber()))
   assert (str(pad.GetNetname())==n if n else not pad.GetNetname()),(r,pad.GetNumber(),n,pad.GetNetname())
 assert len(list(b.GetTracks()))==0
 records.update(footprints=len(fs),native_net_repairs=changed,parity='PASS',unchanged_footprints_preserved=True,tracks=0)
 (D/f'{stage}-sync.json').write_text(json.dumps(records,indent=2)+'\n')
 print('Native read-back PASS:',len(fs),'footprints;',len(changed),'canonical net-name repairs; existing placement preserved')
