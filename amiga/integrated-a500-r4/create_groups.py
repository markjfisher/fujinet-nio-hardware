"""Native API fills two MCP gaps: PCB groups and changing an existing part's side."""
from pathlib import Path
import json,pcbnew as k
ROOT=Path(__file__).resolve().parent;P=ROOT/'integrated-a500-r4.kicad_pcb';b=k.LoadBoard(str(P));fs={f.GetReference():f for f in b.GetFootprints()}
plan=json.loads((ROOT/'review/cluster-plan.json').read_text())
extra=json.loads((ROOT/'cluster-groups.json').read_text())
for record in plan['groups']:record['members']+=extra['extend'].get(record['name'],[])
plan['groups']+=extra['groups']
for ref in plan['backside']:
 f=fs[ref]
 if f.GetLayer()!=k.B_Cu:f.Flip(f.GetPosition(),k.FLIP_DIRECTION_TOP_BOTTOM)
existing={g.GetName():g for g in b.Groups() if g.GetName().startswith('FN:')}
seen=set()
for record in plan['groups']:
 name='FN: '+record['name']
 if name in existing:
  group=existing.pop(name)
  for item in list(group.GetItems()):group.RemoveItem(item)
 else:
  group=k.PCB_GROUP(b);group.SetName(name);b.Add(group)
 for ref in record['members']:
  assert ref not in seen,ref
  group.AddItem(fs[ref]);seen.add(ref)
assert not existing,('unexpected candidate groups',list(existing))
k.SaveBoard(str(P),b)
(ROOT/'review/group-checks.json').write_text(json.dumps({'groups':plan['groups'],'grouped_components':len(seen),'ungrouped':sorted(set(fs)-seen)},indent=2)+'\n')
print('Saved',len(plan['groups']),'native groups;',len(seen),'grouped components; SD bypass on back')
