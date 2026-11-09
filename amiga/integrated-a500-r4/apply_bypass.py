"""Apply geometry-derived capacitor locations through the supported MCP tool."""
import asyncio,json
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
ROOT=Path(__file__).resolve().parent
async def main():
 plan=json.loads((ROOT/'review/bypass-placement.json').read_text());assert not plan['unplaced']
 async with Client(StdioTransport(command=str(ROOT.parents[1]/'tools/kicad/launch'),args=[]),timeout=120) as c:
  for move in plan['moves']:
   args={k:move[k] for k in ['reference','x_mm','y_mm']}
   d=(await c.call_tool('pcb',dict(operation='move_footprint',pcb_path=str(ROOT/'integrated-a500-r4.kicad_pcb'),**args))).data
   assert d.get('status')=='ok',d
  await c.call_tool('pcb',{'operation':'auto_fix_silkscreen','pcb_path':str(ROOT/'integrated-a500-r4.kicad_pcb')})
  for ref,x,y in [('C102',17.8,97.8),('C5',17.4,77.6),('U78',87.74,113.2),('Q3',33.4,80.7),('C7',41.2,100.5)]:
   await c.call_tool('pcb',{'operation':'update_silkscreen','pcb_path':str(ROOT/'integrated-a500-r4.kicad_pcb'),'reference':ref,'silk_field':'reference','x_mm':x,'y_mm':y,'silk_size_mm':.8})
  d=(await c.call_tool('audit',{'operation':'all','pcb_path':str(ROOT/'integrated-a500-r4.kicad_pcb')})).data
  (ROOT/'review/pcb-audit.json').write_text(json.dumps(d,indent=2)+'\n')
 print('27 local bypass placements applied through MCP')
if __name__=='__main__':asyncio.run(main())
