"""Native rule area: MCP add_zone exposes copper pours, not component keepouts.

The whole-band check excepts J40. This rule area covers the remaining gap up
to J40's existing courtyard; bus copper and vias are deliberately allowed.
"""
from pathlib import Path
import json,pcbnew as k
ROOT=Path(__file__).resolve().parent
P=ROOT/'integrated-a500-r4.kicad_pcb';b=k.LoadBoard(str(P));m=json.loads((ROOT/'mechanical.json').read_text());o=m['outline']
name='A500 connector component clearance'
for z in list(b.Zones()):
 if z.GetZoneName()==name:b.Remove(z)
z=k.ZONE(b);z.SetZoneName(name);z.SetIsRuleArea(True)
layers=k.LSET();layers.AddLayer(k.F_Cu);layers.AddLayer(k.B_Cu);z.SetLayerSet(layers)
z.SetDoNotAllowFootprints(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(False);z.SetDoNotAllowZoneFills(False)
x=m['component_limit_x_mm'];y=o['y_mm'];bottom=y+o['height_mm']
poly=z.Outline();poly.NewOutline()
for px,py in [(x,y),(94.5,y),(94.5,bottom),(x,bottom)]:poly.Append(k.FromMM(px),k.FromMM(py))
b.Add(z);k.SaveBoard(str(P),b)
print('Component-only keepout recorded on both faces; connector copper allowed')
