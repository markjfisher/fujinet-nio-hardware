"""Apply one reviewed incremental stage via MCP. Never constructs a PCB."""
import asyncio,json,os,sys,collections,math
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from kicad_sch_api import Schematic
from kicad_sch_api.library.cache import get_symbol_cache
SRC=Path(__file__).resolve().parent.parent;HW=SRC.parents[1]
P=Path(sys.argv[1]).resolve();name=sys.argv[2]
SYMS=P/'phase1/tool-symbols';SYMS.mkdir(parents=True,exist_ok=True)
for directory in [Path('/usr/share/kicad/symbols'),HW/'kicad/libraries',SRC]:
 for f in directory.glob('*.kicad_sym'):
  target=SYMS/f.name
  if not target.exists():target.symlink_to(f.resolve())
os.environ['KICAD_SYMBOL_DIR']=str(SYMS)
stage=next(x for x in json.loads((SRC/'phase1/stages.json').read_text()) if x['name']==name)
expected={c['reference']:c for c in stage['expected']}
def xy(p):return (round(p.x,4),round(p.y,4))
def pinpos(c,pin):
 sp=next(p for p in get_symbol_cache().get_symbol(c['lib_id']).pins if p.number==pin)
 a=math.radians(c.get('rotation',0));x,y=sp.position.x,sp.position.y
 return (round(c['position'][0]+x*math.cos(a)-y*math.sin(a),4),round(c['position'][1]-x*math.sin(a)-y*math.cos(a),4))
async def main():
 # Public API gap: resize root sheet boxes before appending pins through MCP.
 rootfile=P/'integrated-a500-r4.kicad_sch';pre=Schematic.load(str(rootfile))
 for page in {c['page'] for c in expected.values()}:
  sh=pre.sheets.get_sheet_by_filename(page+'.kicad_sch')
  if sh:pre.sheets.update_sheet_size(sh['uuid'],(sh['size']['width'],max(250,sh['size']['height'])))
 pre.save()
 log=[];ncs=collections.defaultdict(list)
 env=dict(os.environ,KICAD_SYMBOL_DIR=str(SYMS))
 os.environ['KICAD_SYMBOL_DIR']=env['KICAD_SYMBOL_DIR']
 async with Client(StdioTransport(command=str(HW/'tools/kicad/launch'),args=[],env=env),timeout=120) as cli:
  async def call(op,**kw):
   r=await cli.call_tool('schematic',dict(operation=op,**kw));d=r.data
   if not isinstance(d,dict):d=json.loads(r.content[0].text)
   if d.get('status')=='error' or d.get('error'):raise RuntimeError((op,kw,d))
   log.append({'op':op,'args':kw,'result':d});return d
  await cli.call_tool('get_usage_guidance',{})
  # Library availability in this actual writer process, including custom symbols.
  for lib in sorted({c['lib_id'] for c in stage['add']}):
   r=await cli.call_tool('library',dict(operation='search',query=lib.split(':')[1],type='symbol',limit=100))
   d=r.data if isinstance(r.data,dict) else json.loads(r.content[0].text)
   assert any(x.get('lib_id')==lib for x in d.get('results',[])),(lib,d)
  pages={c['page'] for k in ['remove','add','rewire','update'] for c in stage[k]}
  # Root and all sheet ports are updated only for changed cross-sheet membership.
  nets=collections.defaultdict(set)
  for c in expected.values():
   for n in c['pins'].values():nets[n].add(c['page'])
  cross={n for n,v in nets.items() if len(v)>1}
  ports={page:sorted({n for c in expected.values() if c['page']==page for n in c['pins'].values()} & cross) for page in {c['page'] for c in expected.values()}}
  rootpath=P/'integrated-a500-r4.kicad_sch'
  root=Schematic.load(str(rootpath));root_changes={}
  for page,desired in ports.items():
   f=P/f'{page}.kicad_sch'
   current=Schematic.load(str(f)) if f.exists() else None
   existing={l.text for l in current.hierarchical_labels} if current else set()
   if set(desired)!=existing:pages.add(page);root_changes[page]=(existing,set(desired))
  for page in sorted(pages):
   f=P/f'{page}.kicad_sch'
   original=Schematic.load(str(f)) if f.exists() else None
   if original:await call('load',schematic_path=str(f))
   else:await call('create',name=page)
   wires=list(original.wires) if original else [];labels=list(original.labels) if original else []
   deletedw=set();deletedl=set()
   async def detach(point):
    for w in wires:
     if w.uuid in deletedw or point not in [xy(t) for t in w.points]:continue
     await call('remove_wire',wire_uuid=w.uuid);deletedw.add(w.uuid)
     for end in w.points:
      ep=xy(end)
      remaining=[a for a in wires if a.uuid not in deletedw and ep in [xy(t) for t in a.points]]
      if not remaining:
       for l in labels:
        if l.uuid not in deletedl and xy(l.position)==ep:
         await call('remove_label',label_uuid=l.uuid);deletedl.add(l.uuid)
   async def remove_component(r):
    c=next((c for c in stage['remove'] if c['reference']==r),expected.get(r))
    for sp in get_symbol_cache().get_symbol(c['lib_id']).pins:
     pos=pinpos(c,sp.number);await detach(pos);ncs[page].append(pos)
    await call('remove_component',reference=r)
   async def attach(c,pin,net):
    # MCP's loaded-symbol pin query omits common-unit pins in KiCad 10.
    # Use the library API transform and verify every connection natively.
    pos=list(pinpos(c,pin))
    sym=get_symbol_cache().get_symbol(c['lib_id']);sp=next(p for p in sym.pins if p.number==pin)
    angle=(sp.rotation+c.get('rotation',0))%360
    dx,dy={0:(-1,0),90:(0,1),180:(1,0),270:(0,-1)}[angle]
    end=[round(pos[0]+dx*5.08,4),round(pos[1]+dy*5.08,4)]
    await call('add_wire',start_pos=pos,end_pos=end)
    await call('add_label',text=net,position=end,rotation=90 if dy else 0,size=.889)
   async def add_component(c):
    await call('add_component',**{k:c[k] for k in ['lib_id','reference','value','position','footprint']})
    if c.get('rotation'):await call('bulk_update_components',criteria={'reference_pattern':'^'+c['reference']+'$'},updates={'rotation':c['rotation']})
    for pin,net in c['pins'].items():await attach(c,pin,net)
   for c in stage['remove']:
    if c['page']==page:await remove_component(c['reference'])
   for c in stage['update']:
    if c['page']==page:
     if 'lib_id' in c:await remove_component(c['reference']);await add_component(expected[c['reference']])
     else:
      d=await call('bulk_update_components',criteria={'reference_pattern':'^'+c['reference']+'$'},updates={k:v for k,v in c.items() if k not in ['page','reference']});assert d['updated']==1
   for c in stage['rewire']:
    if c['page']==page:
     pos=pinpos(expected[c['reference']],c['pin']);await detach(pos);ncs[page].append(pos)
     if c['new'] is not None:await attach(expected[c['reference']],c['pin'],c['new'])
   for c in stage['add']:
    if c['page']==page:await add_component(c)
   if page in root_changes:
    old,new=root_changes[page]
    if original:
     for l in original.hierarchical_labels:
      if l.text in old-new:await detach(xy(l.position))
    used_y=[l.position.y for l in original.hierarchical_labels] if original else []
    y=max(used_y,default=30.48)+7.62
    for n in sorted(new-old):
     pos=[800 if page=='guard' else 449.58,round(y,4)];end=[pos[0]+10.16,pos[1]]
     await call('add_hierarchical_label',text=n,position=pos,shape='bidirectional',size=.889)
     await call('add_wire',start_pos=pos,end_pos=end);await call('add_label',text=n,position=end,size=.889);y+=3.81
   await call('save',schematic_path=str(f));print('Saved',page,flush=True)
  await call('load',schematic_path=str(rootpath))
  for page,(old,new) in root_changes.items():
   sh=root.sheets.get_sheet_by_filename(page+'.kicad_sch')
   if sh:
    for pin in sh['pins']:
     if pin['name'] in old-new:
      pt=(round(pin['position']['x'],4),round(pin['position']['y'],4))
      for w in list(root.wires):
       if pt in [xy(x) for x in w.points]:
        await call('remove_wire',wire_uuid=w.uuid)
        for l in root.labels:
         if xy(l.position) in [xy(x) for x in w.points]:await call('remove_label',label_uuid=l.uuid)
    y=max((pin['position']['y'] for pin in sh['pins']),default=sh['position']['y'])+7.62
   else:
    d=await call('add_sheet',name='Host interface power guard',filename=page+'.kicad_sch',position=[50.8,590.55],sheet_size=[132.08,180]);sh=dict(uuid=d['sheet_uuid'],position=dict(x=50.8,y=590.55),size=dict(width=132.08,height=180),pins=[]);y=598.17
   # New pins are appended at bottom, not interspersed with existing root wiring.
   for n in sorted(new-old):
    offset=sh['size']['height']-(y-sh['position']['y'])
    await call('add_sheet_pin',sheet_uuid=sh['uuid'],name=n,pin_type='bidirectional',edge='left',position_along_edge=offset)
    pt=[sh['position']['x'],round(y,4)];end=[pt[0]-30.48,pt[1]]
    await call('add_wire',start_pos=pt,end_pos=end);await call('add_label',text=n,position=end,size=.889);y+=3.81
  await call('save',schematic_path=str(rootpath))
 # Single-writer handoff. MCP lacks remove-sheet-pin, remove-hierarchical-label,
 # no-connect and page-metadata operations; use the public schematic API only.
 for page in pages:
  f=P/f'{page}.kicad_sch';s=Schematic.load(str(f))
  # Rebuild only NC markers from actual placed positions (MCP snaps to grid).
  s.no_connects.clear()
  for c in expected.values():
   if c['page']!=page:continue
   obj=s.components.get(c['reference']);placed=dict(c,position=[obj.position.x,obj.position.y])
   for sp in get_symbol_cache().get_symbol(c['lib_id']).pins:
    if sp.number not in c['pins']:s.no_connects.add(position=pinpos(placed,sp.number))
  if page in root_changes:
   old,new=root_changes[page]
   for l in list(s.hierarchical_labels):
    if l.text in old-new:s.remove_hierarchical_label(l.uuid)
  s.set_paper_size('A1');s.save()
 root=Schematic.load(str(rootpath))
 for page,(old,new) in root_changes.items():
  sh=root.sheets.get_sheet_by_filename(page+'.kicad_sch')
  for pin in list(sh['pins']):
   if pin['name'] in old-new:root.sheets.remove_sheet_pin(sh['uuid'],pin['uuid'])
  height=max(pin['position']['y']-sh['position']['y'] for pin in sh['pins'])+7.62
  root.sheets.update_sheet_size(sh['uuid'],(sh['size']['width'],max(sh['size']['height'],height)))
 root.set_paper_size('A0');root.save()
 (P/'phase1').mkdir(exist_ok=True)
 (P/'phase1'/f'{name}-mcp.json').write_text(json.dumps({'calls':len(log),'operations':dict(collections.Counter(x['op'] for x in log))},indent=2)+'\n')
 plan=json.loads((P/'circuit.json').read_text());plan['components']=stage['expected'];plan.pop('gates',None);plan['generator_status']='Historical whole-board generators are obsolete; do not run. Phase1 uses incremental edits.'
 (P/'circuit.json').write_text(json.dumps(plan,indent=2)+'\n')
 print(name,'MCP edits complete:',len(log),'calls',flush=True)
if __name__=='__main__':asyncio.run(main())
