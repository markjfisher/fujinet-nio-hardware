"""Read-only probe: /usr/bin/python3 read_only_probe.py CHECKOUT BOARD OUTPUT_DIR.
Never calls annealer, apply, or board save; selection flags change only in memory.
"""
import types,sys,hashlib,json
from pathlib import Path
import pcbnew as k
src=Path(sys.argv[1]).resolve();pkg=types.ModuleType('plugin');pkg.__path__=[str(src/'plugin')];sys.modules['plugin']=pkg
from plugin.board_model import extract_board_model
from plugin.constraints import parse_constraints, movable_selection, restrict_to_selection, partial_groups, constrained_refs
p=Path(sys.argv[2]).resolve();before=hashlib.sha256(p.read_bytes()).hexdigest();b=k.LoadBoard(str(p));m=extract_board_model(b)
assert len(m.footprints)==203
native_groups={g.GetName():sorted(i.GetReference() for i in g.GetItems() if isinstance(i,k.FOOTPRINT)) for g in b.Groups()}
expected={n:rs for n,rs in native_groups.items() if len(rs)>=2};actual={g.name:sorted(m.footprints[i].reference for i in g.member_indices) for g in m.component_groups};assert actual==expected
fs={f.GetReference():f for f in b.GetFootprints()}; mf={f.reference:f for f in m.footprints}
assert all(mf[r].locked==f.IsLocked() for r,f in fs.items())
results={}
for label,selected in [('none',set()),('single',{'C113'}),('partial_group',{'U61'}),('complete_group',set(native_groups['FN: Power and firmware permission']))]:
 for r,f in fs.items():f.SetSelected() if r in selected else f.ClearSelected()
 x=extract_board_model(b,selected_only=True);movable=[x.footprints[i].reference for i in x.moveable_indices]
 assert all(x.footprints[i].reference in selected for i in x.moveable_indices)
 if label in ['none','partial_group']:assert not movable
 if label=='single':assert movable==['C113']
 if label=='complete_group':assert len(movable)==1
 results[label]={'selected':sorted(selected),'movable_representatives':movable,'partial_groups':partial_groups(x,selected)}
example={'meta':{'schema_version':2,'board_dimensions_mm':[(m.outline_xmax-m.outline_xmin)/1e6,(m.outline_ymax-m.outline_ymin)/1e6]},'component_groups':[],'net_priorities':{},'placement_constraints':{'fixed_positions':[{'ref':r,'x_mm':(f.x-m.outline_xmin)/1e6,'y_mm':(f.y-m.outline_ymin)/1e6} for r,f in sorted(mf.items())]},'design_notes':['PRESERVATION SNAPSHOT: all parts fixed, including outside-board staging; not an optimisation recipe.']}
c=parse_constraints(example);assert not c.warnings
restricted,skips=restrict_to_selection(c,{'C113'},model=m);assert [x['ref'] for x in restricted.placement['fixed_positions']]==['C113']
assert movable_selection({'U20'},{'U20'},{'U20'})=={'U20'}
assert hashlib.sha256(p.read_bytes()).hexdigest()==before
r={'source_commit':'bbed16824a806e6ba787b96d3915233462db9bd2','kicad_version':k.Version(),'pcb_sha256_unchanged':before,'footprints':len(m.footprints),'native_groups':len(native_groups),'extracted_multimember_groups':len(actual),'group_memberships_match':True,'outline_bbox_mm':[m.outline_xmin/1e6,m.outline_ymin/1e6,m.outline_xmax/1e6,m.outline_ymax/1e6],'outline_vertices':len(m.outline_polygon or []),'keepouts':len(m.keepouts),'selection_tests':results,'schema_parse':'PASS','no_optimizer_or_writeback_called':True}
(Path(sys.argv[3])/'compatibility.json').write_text(json.dumps(r,indent=2)+'\n');(Path(sys.argv[3])/'preservation.constraints.json').write_text(json.dumps(example,indent=2)+'\n');print(json.dumps(r,indent=2))
