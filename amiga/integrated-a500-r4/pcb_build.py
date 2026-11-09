"""MCP constructs and places the R4 PCB; native checks follow separately.

The pipeline's pending_approval return is an internal placement review point.
It is deliberately used to prevent premature routing of critical circuitry.
"""
import asyncio,json,os
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
ROOT=Path(__file__).resolve().parent
HW=ROOT.parents[1]
async def main():
    # MCP's library resolver has no project fp-lib-table support. Supply a
    # per-process library root; never install into the user's shared library.
    app=ROOT/'tool-library-root'
    base=app/'Contents/SharedSupport/footprints';base.mkdir(parents=True,exist_ok=True)
    link=base/'candidate.pretty'
    if not link.exists():link.symlink_to(ROOT/'candidate.pretty',target_is_directory=True)
    env=dict(os.environ,KICAD_APP_PATH=str(app))
    hints={
      'J40':{'fixed':[105,62],'rotation':0},
      'U20':{'fixed':[60,60],'rotation':0},
      'U30':{'fixed':[7,30],'rotation':90},
      'J1':{'fixed':[3,82],'rotation':270},
      'J30':{'fixed':[9.32,62.32],'rotation':90},
      'J2':{'fixed':[12,110],'rotation':0},
      'J60':{'fixed':[88,117],'rotation':90},
      'J20':{'fixed':[54,8],'rotation':90},
      'J31':{'fixed':[32,8],'rotation':90},
      'U1':{'fixed':[29,76],'rotation':0},
      'U2':{'fixed':[39,76],'rotation':0},
      'U3':{'fixed':[14,72],'rotation':0},
      'U8':{'fixed':[14,92],'rotation':0},
      'U9':{'fixed':[25,92],'rotation':0},
      'U5':{'fixed':[36,94],'rotation':0},
    }
    for i in range(4):hints[f'SW{i+1}']={'fixed':[48+10*i,115],'rotation':0}
    for i in range(8):hints[f'U{40+i}']={'fixed':[85,20+12*i],'rotation':0}
    # Critical regulator footprints/positions follow the official RP2350B R4
    # cell. The tool handles all remaining placement around these constraints.
    for item in json.loads((ROOT/'reference/rp-core-footprints.json').read_text())['records']:
        hints[item['reference']]={'fixed':item['fixed'],'rotation':item['rotation']%360}
    rp_positions={
      'U21':(53,45,0), 'C20':(56,40,0), 'R20':(50,40,90),
      'Y20':(60,74,0), 'R21':(60.2,69.5,90),
      'C21':(57,72,90), 'C22':(63,72,90),
      'R22':(58,53,90), 'R23':(60,53,90),
      'C26':(52,57.8,0), 'C27':(52,62,0),
      'C28':(56.5,68,90), 'C29':(58.4,68,90),
      'C30':(68,64,0), 'C31':(68,60,0),
      'C32':(68,56,0), 'C33':(71.5,57.5,0),
      'C34':(61,48,90), 'C35':(58.5,49.5,90),
      'C36':(56,52,90), 'C37':(52,60,0),
      'C38':(62.5,68,90), 'C39':(70.5,61.5,0),
    }
    for ref,(x,y,a) in rp_positions.items():hints[ref]={'fixed':[x,y],'rotation':a}
    # Dedicated buffer bypass capacitors; avoid treating every 3V3 capacitor
    # as interchangeable across the whole board during graph placement.
    for i in range(8):hints[f'C{50+i}']={'fixed':[90.5,17.1+12*i],'rotation':90}
    (ROOT/'placement-hints.json').write_text(json.dumps(hints,indent=2)+'\n')
    async with Client(StdioTransport(command=str(HW/'tools/kicad/launch'),args=[],env=env),timeout=240) as c:
        result=await c.call_tool('build_pcb_from_schematic',{
          'project_path':str(ROOT/'integrated-a500-r4.kicad_pro'),
          'board_width_mm':105,'board_height_mm':124,
          'approved':False,'export_gerbers':False,'add_mounting_holes':True,
          'placement_hints':hints})
        d=result.data
        if not isinstance(d,dict):d=json.loads(result.content[0].text)
        (ROOT/'review/placement-result.json').write_text(json.dumps(d,indent=2)+'\n')
        print(json.dumps({k:v for k,v in d.items() if k not in ['steps','proposal']},indent=2))
        if d.get('error'):raise RuntimeError(d['error'])
if __name__=='__main__':asyncio.run(main())
