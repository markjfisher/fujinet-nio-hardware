"""Set every reference explicitly through MCP; no auto-fix/hide fallback."""
import asyncio,json
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
ROOT=Path(__file__).resolve().parent
async def main():
 plan=json.loads((ROOT/'review/label-plan.json').read_text())
 async with Client(StdioTransport(command=str(ROOT.parents[1]/'tools/kicad/launch'),args=[]),timeout=120) as c:
  for label in plan.get('updates',plan['labels']):
   r=await c.call_tool('pcb',dict(operation='update_silkscreen',pcb_path=str(ROOT/'integrated-a500-r4.kicad_pcb'),silk_field='reference',**label));d=r.data
   if not isinstance(d,dict):d=json.loads(r.content[0].text)
   assert d.get('status')=='ok',d
 print('Applied',len(plan.get('updates',plan['labels'])),'changed reference labels; all references retained')
if __name__=='__main__':asyncio.run(main())
