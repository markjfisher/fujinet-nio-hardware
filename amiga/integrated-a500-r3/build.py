"""Construct this candidate through the selected MCP; never edits released CAD.

Public kicad-sch-api fills only MCP gaps: no-connect markers,
page metadata. No S-expression construction or patching.
Run with tools/kicad's pinned Python after sourcing workspace scripts/env.sh.
"""
import asyncio, json, os, math, sys
from pathlib import Path
from collections import defaultdict
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from kicad_sch_api import Schematic
ROOT=Path(__file__).resolve().parent
HW=ROOT.parents[1]
PAGES=['input','power','usb','rp','esp','address','data','control']
TITLES=['Protected USB input','USB-C power and qualification','USB routing and physical recovery','RP2350B and support','ESP32-S3 module and microSD','A500 socket and input buffers','Independent byte-lane data buffers','Hardware bus interlocks']
async def main():
 plan=json.loads((ROOT/'circuit.json').read_text()); log=[]; extras={}
 env=dict(os.environ,KICAD_SYMBOL_DIR=f'/usr/share/kicad/symbols:{HW}/kicad/libraries')
 os.environ.update({'KICAD_SYMBOL_DIR':env['KICAD_SYMBOL_DIR']})
 netpages=defaultdict(set)
 for c in plan['components']:
  for n in c['pins'].values():netpages[n].add(c['page'])
 cross={n for n,p in netpages.items() if len(p)>1}
 async with Client(StdioTransport(command=str(HW/'tools/kicad/launch'),args=[],env=env),timeout=120) as client:
  async def call(op,**args):
   r=await client.call_tool('schematic',dict(operation=op,**args));d=r.data
   if not isinstance(d,dict):d=json.loads(r.content[0].text)
   if d.get('error') or d.get('status')=='error':raise RuntimeError((op,args,d))
   log.append({'operation':op,'result':d});return d
  await client.call_tool('get_usage_guidance',{'operation':'strategy'})
  # Read-only search verifies this process's library discovery too.
  r=await client.call_tool('library',{'operation':'search','query':'Amiga_A500','kind':'symbol','type':'symbol','limit':2})
  log.append({'library_check':str(r.data)})
  for page,title in zip(PAGES,TITLES):
   if '--root-only' in sys.argv:
    extras[page]=([],sorted({n for c in plan['components'] if c['page']==page for n in c['pins'].values()} & cross),title)
    continue
   print('Constructing',page,flush=True)
   await call('create',name=page)
   nc=[];glob=[];seen=set();pins={};ends={};placed=[]
   for c in [c for c in plan['components'] if c['page']==page]:
    args={k:c[k] for k in ['lib_id','reference','value','position','footprint']}
    await call('add_component',**args)
    if c['rotation']:
     result=await call('bulk_update_components',criteria={'reference_pattern':'^'+c['reference']+'$'},updates={'rotation':c['rotation']})
     assert result['updated']==1, result
    pp=await call('list_component_pins',reference=c['reference']);assert pp['pins'],c
    for p in pp['pins']:
     n=c['pins'].get(p['number']);xy=[p['x'],p['y']];key=(c['reference'],p['number']);pins[key]=xy
     if n is None:nc.append(xy);continue
     # Pin direction from relative position, corrected using library pin orientation.
     # MCP exposes exact transformed positions; the API is read-only here.
     from kicad_sch_api.library.cache import get_symbol_cache
     sym=get_symbol_cache().get_symbol(c['lib_id'])
     sp=next(p0 for p0 in sym.pins if p0.number==p['number'])
     angle=(sp.rotation+c['rotation'])%360
     dx,dy={0:(-1,0),90:(0,1),180:(1,0),270:(0,-1)}[angle]
     length=20.32 if dx<0 else 5.08
     end=[round(xy[0]+dx*length,3),round(xy[1]+dy*length,3)]
     await call('add_wire',start_pos=xy,end_pos=end)
     rotation=90 if dy else 0
     await call('add_label',text=n,position=end,rotation=rotation,size=0.889)
     ends[key]=end
    placed.append(c)
   for r,p,r2,p2 in plan.get('connections',[]):
    refs={c['reference']:c for c in placed}
    if r in refs and r2 in refs:
     assert refs[r]['pins'][p]==refs[r2]['pins'][p2]
     await call('add_wire_between_pins',comp1_ref=r,pin1=p,comp2_ref=r2,pin2=p2)
   # Local physical wires join nearby collinear passive pins on the same net.
   # These clarify supply/return rails and resistor dividers without hidden joins.
   ps=[(c['reference'],p,n) for c in placed if c['lib_id'] in ['Device:R','Device:C'] for p,n in c['pins'].items()]
   done=set()
   for i,(r,p,n) in enumerate(ps):
    a=ends[r,p]
    for r2,p2,n2 in ps[i+1:]:
     b=ends[r2,p2]
     if n!=n2 or r==r2:continue
     dist=abs(a[0]-b[0])+abs(a[1]-b[1])
     if 0<dist<=35.56 and (a[0]==b[0] or a[1]==b[1]):
      # Don't run through another component's body: horizontal rails only.
      if a[1]!=b[1]:continue
      key=tuple(sorted((tuple(a),tuple(b))))
      if key in done:continue
      await call('add_wire',start_pos=a,end_pos=b);done.add(key)
      await call('add_junction',position=a);await call('add_junction',position=b)
   # Use MCP-supported hierarchical ports: the API global-label method does not serialize.
   ports=sorted({n for c in placed for n in c['pins'].values()} & cross)
   for i,n in enumerate(ports):
    pt=[449.58,30.48+i*3.81];end=[459.74,pt[1]]
    await call('add_hierarchical_label',text=n,position=pt,shape='bidirectional',size=0.889)
    await call('add_wire',start_pos=pt,end_pos=end)
    await call('add_label',text=n,position=end,size=0.889)
   for nt in plan['notes'].get(page,[]):
    await call('add_text',text=nt['text'],position=[223.52,nt['position'][1]],size=1.27)
   await call('save',schematic_path=str(ROOT/f'{page}.kicad_sch'))
   extras[page]=(nc,ports,title)
  await call('create',name='integrated-a500-r3')
  await call('add_text',text='FujiNet A500 integrated R3 - circuit review; NOT fabrication release',position=[420,15.24],size=2.54)
  for i,(page,title) in enumerate(zip(PAGES,TITLES)):
   x=50.8+(i%4)*198.12;y=40.64+(i//4)*269.24
   ports=extras[page][1];height=max(50.8,12.7+len(ports)*3.81)
   sheet=await call('add_sheet',name=title,filename=f'{page}.kicad_sch',position=[x,y],sheet_size=[132.08,height])
   for j,n in enumerate(ports):
    offset=7.62+j*3.81
    await call('add_sheet_pin',sheet_uuid=sheet['sheet_uuid'],name=n,pin_type='bidirectional',edge='left',position_along_edge=height-offset)
    pt=[x,y+offset];end=[x-30.48,y+offset]
    await call('add_wire',start_pos=pt,end_pos=end)
    await call('add_label',text=n,position=end,size=0.889)
  await call('save',schematic_path=str(ROOT/'integrated-a500-r3.kicad_sch'))
 # Single writer handoff: MCP process has exited before API finishing operations.
 for page,(nc,ports,title) in ([] if '--root-only' in sys.argv else extras.items()):
  s=Schematic.load(str(ROOT/f'{page}.kicad_sch'))
  for pos in nc:s.no_connects.add(position=tuple(pos))
  s.set_paper_size('A2');s.set_title_block(title=title,date='2026-11-09',rev='R3 candidate',company='FujiNet NIO')
  s.save()
 s=Schematic.load(str(ROOT/'integrated-a500-r3.kicad_sch'));s.set_paper_size('A1');s.set_title_block(title='FujiNet direct A500 integrated candidate',date='2026-11-09',rev='R3 candidate');s.save()
 (ROOT/'integrated-a500-r3.kicad_pro').write_text('{}\n')
 (ROOT/'review/build-log.json').write_text(json.dumps({'calls':len(log),'results':log},indent=2)+'\n')
 print(f'CAD construction complete: {len(plan["components"])} components; {len(log)} calls',flush=True)
if __name__=='__main__':asyncio.run(main())
