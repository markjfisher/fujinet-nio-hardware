"""MCP applies reviewed circuit-cell placements. Never runs generic autofix."""
import asyncio,json,sys
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
ROOT=Path(__file__).resolve().parent
async def main():
 plan=json.loads((ROOT/'review'/(sys.argv[1] if len(sys.argv)>1 else 'cluster-plan.json')).read_text())
 async with Client(StdioTransport(command=str(ROOT.parents[1]/'tools/kicad/launch'),args=[]),timeout=120) as c:
  for move in plan['moves']:
   r=await c.call_tool('pcb',dict(operation='move_footprint',pcb_path=str(ROOT/'integrated-a500-r4.kicad_pcb'),**move))
   d=r.data
   if not isinstance(d,dict):d=json.loads(r.content[0].text)
   if d.get('status')!='ok':raise RuntimeError(d)
 print('Applied',len(plan['moves']),'MCP component moves')
if __name__=='__main__':asyncio.run(main())
