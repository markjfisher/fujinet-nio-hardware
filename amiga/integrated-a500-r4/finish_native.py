"""Native KiCad API fills MCP gaps: hierarchy IDs, library IDs and layer count.

No routing is created. Native net renaming also works around the MCP returning
"Net TX_HI_N not found" for a net present in native read-back.
"""
from pathlib import Path
import json,xml.etree.ElementTree as E
import pcbnew as k
ROOT=Path(__file__).resolve().parent
p=ROOT/'integrated-a500-r4.kicad_pcb';b=k.LoadBoard(str(p))
t=E.parse(ROOT/'review/netlist.xml');plan={c['reference']:c for c in json.loads((ROOT/'circuit.json').read_text())['components']}
components={c.get('ref'):c for c in t.findall('./components/comp')}
expected={(n.get('ref'),n.get('pin')):net.get('name') for net in t.findall('./nets/net') for n in net.findall('node')}
renames={}
for f in b.GetFootprints():
 ref=f.GetReference()
 if ref not in components:
  assert ref in ['H1','H2','H3','H4'],ref
  f.SetBoardOnly(True)
  continue
 c=components[ref];fid=c.findtext('footprint');lib,name=fid.split(':',1);f.SetFPID(k.LIB_ID(lib,name))
 f.SetPath(k.KIID_PATH(c.find('sheetpath').get('tstamps')+c.findtext('tstamps')))
 for field in ['Datasheet','Description']:
  f.GetField(field).SetText(c.findtext("./fields/field[@name='"+field+"']") or '')
 for pad in f.Pads():
  key=(ref,pad.GetNumber())
  if key not in expected or pad.GetNumber() not in plan[ref]['pins']:continue
  old=str(pad.GetNetname());new=expected[key]
  assert old, key
  if old in renames:assert renames[old]==new,(key,renames[old],new)
  renames[old]=new
for net in list(b.GetNetInfo().NetsByName().values()):
 old=str(net.GetNetname())
 if old in renames:net.SetNetname(renames[old])
b.SetCopperLayerCount(4)
layers=k.LSET.AllCuMask(4);layers.AddLayerSet(k.LSET.AllNonCuMask());b.SetEnabledLayers(layers)
# Preserve the module antenna restriction on every copper layer. The two-layer
# constructor had narrowed the library's all-copper keepout to F/B only.
for zone in next(f for f in b.GetFootprints() if f.GetReference()=='U30').Zones():
 if zone.GetIsRuleArea():zone.SetLayerSet(k.LSET.AllCuMask())
# Lock engineering anchors. Generic autofix does not honour these locks in the
# pinned MCP, and must not be used on this candidate.
for f in b.GetFootprints():
 if f.GetReference() in json.loads((ROOT/'placement-hints.json').read_text()):f.SetLocked(True)
k.SaveBoard(str(p),b)
(ROOT/'review/net-renames.json').write_text(json.dumps(renames,indent=2)+'\n')
print('Native hierarchy/library IDs restored; four copper layers, unrouted.')
