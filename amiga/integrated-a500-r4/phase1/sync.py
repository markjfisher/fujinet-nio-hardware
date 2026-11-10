"""Incremental MCP footprint addition/net assignment; never regenerates the board."""
import asyncio,json,os,sys,subprocess,xml.etree.ElementTree as E
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
SRC=Path(__file__).resolve().parent;HW=SRC.parents[2];P=Path(sys.argv[1]).resolve();stage=sys.argv[2];pcb=P/'integrated-a500-r4.kicad_pcb'
async def main():
 subprocess.run(['/usr/bin/python3',str(SRC/'sync_native.py'),str(P),stage,'prepare'],check=True)
 plan=json.loads((P/'phase1'/f'{stage}-sync.json').read_text())
 async with Client(StdioTransport(command=str(HW/'tools/kicad/launch'),args=[]),timeout=180) as cli:
  async def call(op,**kw):
   r=await cli.call_tool('pcb',dict(operation=op,pcb_path=str(pcb),**kw));d=r.data
   if not isinstance(d,dict):d=json.loads(r.content[0].text)
   assert not d.get('error') and d.get('status')!='error',(op,d)
   return d
  for a in plan['add']:
   await call('place_footprint',**a)
   await call('update_silkscreen',reference=a['reference'],visible=True,silk_size_mm=.9,silk_thickness_mm=.15,angle_deg=0)
  t=E.parse(P/'phase1'/f'{stage}.xml')
  assignments=[dict(reference=n.get('ref'),pad=n.get('pin'),net=net.get('name').replace('/','{slash}')) for net in t.findall('./nets/net') for n in net.findall('node')]
  d=await call('bulk_assign_pad_nets',assignments=assignments);assert d.get('error_count',0)==0,d
 subprocess.run(['/usr/bin/python3',str(SRC/'sync_native.py'),str(P),stage,'finish'],check=True)
 subprocess.run(['kicad-cli','pcb','drc','--schematic-parity','--format','json','-o',str(P/'phase1'/f'{stage}-drc.json'),str(pcb)],check=True)
if __name__=='__main__':asyncio.run(main())
