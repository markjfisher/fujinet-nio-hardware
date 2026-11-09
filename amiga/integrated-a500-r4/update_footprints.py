"""Apply plan footprint properties through MCP without rebuilding the circuit."""
import asyncio,json,os
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
ROOT=Path(__file__).resolve().parent
async def main():
 p=json.loads((ROOT/'circuit.json').read_text())
 env=dict(os.environ,KICAD_SYMBOL_DIR=f'/usr/share/kicad/symbols:{ROOT.parents[1]}/kicad/libraries')
 async with Client(StdioTransport(command=str(ROOT.parents[1]/'tools/kicad/launch'),args=[],env=env),timeout=120) as c:
  for page in sorted({x['page'] for x in p['components']}):
   path=str(ROOT/(page+'.kicad_sch'))
   await c.call_tool('schematic',{'operation':'load','schematic_path':path})
   for x in p['components']:
    if x['page']!=page:continue
    d=(await c.call_tool('schematic',{'operation':'bulk_update_components','criteria':{'reference_pattern':'^'+x['reference']+'$'},'updates':{'footprint':x['footprint']}})).data
    if not isinstance(d,dict) or d.get('updated')!=1:raise RuntimeError(d)
   await c.call_tool('schematic',{'operation':'save','schematic_path':path})
   print(page,flush=True)
if __name__=='__main__':asyncio.run(main())
