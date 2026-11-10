"""Read-only selection exporter. No PCB mutation or placement calculation."""
import sys,types,pickle,json
from pathlib import Path
import pcbnew as k
pkg=types.ModuleType('plugin');pkg.__path__=['/tmp/cadmust-neo-review/plugin'];sys.modules['plugin']=pkg
from plugin.board_model import extract_board_model,KeepOut
selected={'U61','C70','R3','R63','U66','C75','U71','C80','U64','C73'}
b=k.LoadBoard(sys.argv[1])
for f in b.GetFootprints():
 f.SetSelected() if f.GetReference() in selected else f.ClearSelected()
m=extract_board_model(b,selected_only=True)
for box in [(-26.75,6,-5.75,54),(87,3.5,105,120.5)]:
 m.keepouts.append(KeepOut(*(int(v*1e6) for v in box)))
assert len(m.moveable_indices)==4
assert all(f.locked for f in m.footprints if f.reference not in selected)
Path(sys.argv[2]).write_bytes(pickle.dumps(m))
print('Selected complete groups:',[m.footprints[i].reference for i in m.moveable_indices])
