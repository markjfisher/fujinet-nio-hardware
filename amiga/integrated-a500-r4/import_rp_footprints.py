"""Extract six MIT-licensed reference footprints using native pcbnew.

Usage: python import_rp_footprints.py /path/to/unpacked/RPI-RP2350B-MINIMAL_R4-S1_public
MCP has no custom-footprint construction/import operation. No traces copied.
"""
import pcbnew as k,json,hashlib,shutil,sys
from pathlib import Path
r=Path(__file__).resolve().parent;s=Path(sys.argv[1]);b=k.LoadBoard(str(s/'RPI-RP2350B-MINIMAL_R4-S1.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()}; plugin=k.PCB_IO_MGR.FindPlugin(k.PCB_IO_MGR.KICAD_SEXP)
mp={'U1':'U20','L1':'L20','C6':'C24','C7':'C25','C9':'C23','R3':'R24'}
assert hashlib.sha256((s/'RPI-RP2350B-MINIMAL_R4-S1.kicad_pcb').read_bytes()).hexdigest()=='4f937c8a16cc62e7d69ba1a5b9f824aa83fb418d498ce65399447fdd99754170', 'Reference changed; review before importing'
records=[]
for old,new in mp.items():
 f=k.Cast_to_FOOTPRINT(fs[old].Duplicate(False));angle=f.GetOrientationDegrees();pos=f.GetPosition();xy=[k.ToMM(pos.x)-40,k.ToMM(pos.y)-40]
 f.SetOrientationDegrees(0);f.SetPosition(k.VECTOR2I(0,0));name='RP_Reference_'+old;f.SetFPID(k.LIB_ID('candidate',name));f.SetReference('REF**');f.SetValue(name)
 for p in f.Pads():
  p.SetNetCode(0)
  if old=='L1':p.SetNumber({'1':'2','2':'1'}[p.GetNumber()])
 plugin.FootprintSave(str(r/'candidate.pretty'),f)
 records.append({'source_reference':old,'reference':new,'footprint':'candidate:'+name,'fixed':xy,'rotation':angle,'pad_numbers_swapped':old=='L1'})
(r/'reference').mkdir(exist_ok=True);(r/'reference/Raspberry-Pi-LICENSE.txt').write_text((s/'LICENSE.txt').read_text())
out={'source':'https://pip.raspberrypi.com/documents/RP-010329-CA','source_board_sha256':hashlib.sha256((s/'RPI-RP2350B-MINIMAL_R4-S1.kicad_pcb').read_bytes()).hexdigest(),'records':records}
(r/'reference/rp-core-footprints.json').write_text(json.dumps(out,indent=2)+'\n')
d=json.loads((r/'circuit.json').read_text());by={c['reference']:c for c in d['components']}
for a in records:
 c=by[a['reference']];c['footprint']=a['footprint']
 if a['reference'] in ['C23','C24','C25']:c['manufacturer']='Murata';c['mpn']='GRM155R60J475ME47D'
 if a['reference']=='R24':c['manufacturer']='Yageo';c['mpn']='RC0402FR-0733RL'
(r/'circuit.json').write_text(json.dumps(d,indent=2)+'\n')
print(out)
