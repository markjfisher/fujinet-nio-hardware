"""MCP restoration of exact native net names and explicit candidate DFM limits."""
import asyncio,json,xml.etree.ElementTree as E
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
ROOT=Path(__file__).resolve().parent
async def main():
 async with Client(StdioTransport(command=str(ROOT.parents[1]/'tools/kicad/launch'),args=[]),timeout=120) as c:
  async def call(op,**kw):
   r=await c.call_tool('pcb',dict(operation=op,pcb_path=str(ROOT/'integrated-a500-r4.kicad_pcb'),**kw));d=r.data
   if not isinstance(d,dict):d=json.loads(r.content[0].text)
   if d.get('error') or d.get('status')=='error':raise RuntimeError(d)
   return d
  t=E.parse(ROOT/'review/netlist.xml')
  nc=[{'reference':n.get('ref'),'pad':n.get('pin'),'net':net.get('name').replace('/', '{slash}')}
      for net in t.findall('./nets/net') if net.get('name').startswith('unconnected-')
      for n in net.findall('node')]
  d=await call('bulk_assign_pad_nets',assignments=nc)
  assert d.get('error_count',0)==0,d
  for ref,y in [('H2',3.475),('H3',120.525)]:
   await call('move_footprint',reference=ref,x_mm=90,y_mm=y)
  await call('move_footprint',reference='J60',x_mm=28,y_mm=115,rotation_deg=0)
  for ref,x,y in [('U62',35,22),('U67',35,30),('U68',45,22),('U71',45,30)]:
   await call('move_footprint',reference=ref,x_mm=x,y_mm=y)
  await call('set_design_rules',min_clearance_mm=.125,min_track_width_mm=.125,
    min_via_diameter_mm=.45,min_via_drill_mm=.2,min_hole_to_hole_mm=.25,
    min_through_hole_diameter_mm=.2,min_copper_edge_clearance_mm=.5)
  await call('set_net_class',class_name='Default',nets=[],clearance_mm=.125,track_width_mm=.2,via_diameter_mm=.45,via_drill_mm=.2)
  listing=await call('list_silkscreen')
  if 'NOT FOR FABRICATION' not in json.dumps(listing):
   await call('add_text',text='FujiNet A500 R4 - PLACEMENT REVIEW',x_mm=48,y_mm=102,text_size_mm=1.2)
   await call('add_text',text='NOT FOR FABRICATION',x_mm=48,y_mm=105,text_size_mm=1.2)
  await call('auto_fix_silkscreen')
  d=(await c.call_tool('audit',{'operation':'all','pcb_path':str(ROOT/'integrated-a500-r4.kicad_pcb')})).data
  (ROOT/'review/pcb-audit.json').write_text(json.dumps(d,indent=2)+'\n')
  print('MCP net restoration, rules, and silk complete')
if __name__=='__main__':asyncio.run(main())
