"""Apply measured envelope and fixture moves through MCP, preserving circuit."""
import asyncio,json
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
ROOT=Path(__file__).resolve().parent
async def main():
 m=json.loads((ROOT/'mechanical.json').read_text());moves=json.loads((ROOT/'review/mechanical-moves.json').read_text())['moves']
 async with Client(StdioTransport(command=str(ROOT.parents[1]/'tools/kicad/launch'),args=[]),timeout=120) as c:
  async def call(op,**kw):
   r=await c.call_tool('pcb',dict(operation=op,pcb_path=str(ROOT/'integrated-a500-r4.kicad_pcb'),**kw));d=r.data
   if not isinstance(d,dict):d=json.loads(r.content[0].text)
   if d.get('error') or d.get('status')=='error':raise RuntimeError(d)
   return d
  await call('set_outline',**m['outline'])
  for move in moves:await call('move_footprint',**move)
  for text,y in [('FujiNet A500 R4 - PLACEMENT REVIEW',102),('NOT FOR FABRICATION',105)]:
   await call('edit_text',text=text,x_mm=42,y_mm=y)
  # The footprint itself is excepted by the native whole-band constraint.
  for ref,x,y in [('C7',35.2,100.5),('C5',11.4,77.6),('H1',18,12)]:
   await call('update_silkscreen',reference=ref,silk_field='reference',x_mm=x,y_mm=y,silk_size_mm=.8)
  audit=(await c.call_tool('audit',{'operation':'all','pcb_path':str(ROOT/'integrated-a500-r4.kicad_pcb')})).data
  (ROOT/'review/pcb-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 print('MCP mechanical fit applied')
if __name__=='__main__':asyncio.run(main())
