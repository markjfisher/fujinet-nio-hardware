"""Project-local symbol library via kiutils serializer (MCP has no symbol editor)."""
from pathlib import Path
from kiutils.symbol import SymbolLib, Symbol, SymbolPin
from kiutils.items.syitems import SyRect
from kiutils.items.common import Property,Position,Effects,Font,Fill,Stroke
from kiutils.libraries import LibTable,Library
P=Path(__file__).resolve().parent.parent
specs={
'MIC2790H': [('1','~{RESET}','open_collector'),('2','GND','power_in'),('3','~{MR}','input'),('4','CTH','passive'),('5','SNS','input'),('6','VDD','power_in')],
'TPS2553': [('1','IN','power_in'),('2','GND','power_in'),('3','EN','input'),('4','~{FAULT}','open_collector'),('5','ILIM','passive'),('6','OUT','power_out')],
'SN74LVC2G14': [('1','1A','input'),('2','GND','power_in'),('3','2A','input'),('4','2Y','output'),('5','VCC','power_in'),('6','1Y','output')],
'SN74LVC2G132': [('1','1A','input'),('2','1B','input'),('3','2Y','output'),('4','GND','power_in'),('5','2A','input'),('6','2B','input'),('7','1Y','output'),('8','VCC','power_in')],
'SN74LVC2G125': [('1','~{1OE}','input'),('2','1A','input'),('3','2Y','tri_state'),('4','GND','power_in'),('5','2A','input'),('6','1Y','tri_state'),('7','~{2OE}','input'),('8','VCC','power_in')],
'74LVC3G17': [('1','1A','input'),('2','3Y','output'),('3','2A','input'),('4','GND','power_in'),('5','2Y','output'),('6','3A','input'),('7','1Y','output'),('8','VCC','power_in')],
'SN74LVC11A': [(str(n),name,typ) for n,name,typ in [(1,'1A','input'),(2,'1B','input'),(13,'1C','input'),(12,'1Y','output'),(3,'2A','input'),(4,'2B','input'),(5,'2C','input'),(6,'2Y','output'),(9,'3A','input'),(10,'3B','input'),(11,'3C','input'),(8,'3Y','output'),(7,'GND','power_in'),(14,'VCC','power_in')]],
'SN74LVC04A': [(str(n),f'{i}{k}',t) for i,a,y in [(1,1,2),(2,3,4),(3,5,6),(4,9,8),(5,11,10),(6,13,12)] for n,k,t in [(a,'A','input'),(y,'Y','output')]]+[('7','GND','power_in'),('14','VCC','power_in')],
}
lib=SymbolLib(generator='kiutils')
for name,pins in specs.items():
 sym=Symbol(entryName=name,inBom=True,onBoard=True,pinNamesOffset=.5)
 inp=[x for x in pins if x[2] not in ('output','tri_state','open_collector','power_out','power_in')]
 out=[x for x in pins if x[2] in ('output','tri_state','open_collector','power_out')]
 power=[x for x in pins if x[2]=='power_in']
 h=max(len(inp),len(out))*2.54+5.08
 sym.properties=[Property(key='Reference',value='U',position=Position(0,round(h/2+3.81,4),0),effects=Effects()),Property(key='Value',value=name,position=Position(0,round(h/2+1.27,4),0),effects=Effects())]
 body=Symbol(entryName=name,unitId=1,styleId=1)
 body.graphicItems=[SyRect(start=Position(-10.16,h/2),end=Position(10.16,-h/2),stroke=Stroke(width=.254,type='default'),fill=Fill(type='background'))]
 for side,items in [('left',inp),('right',out),('power',power)]:
  for i,(num,pn,typ) in enumerate(items):
   if side=='power': x=0; y=-h/2-5.08 if pn=='GND' else h/2+5.08;angle=90 if pn=='GND' else 270
   else:x=-15.24 if side=='left' else 15.24;y=h/2-3.81-i*2.54;angle=0 if side=='left' else 180
   body.pins.append(SymbolPin(electricalType=typ,position=Position(round(x,4),round(y,4),angle),length=5.08,name=pn,number=num,nameEffects=Effects(font=Font(height=.889,width=.889)),numberEffects=Effects(font=Font(height=.889,width=.889))))
 sym.units=[body];lib.symbols.append(sym)
lib.to_file(str(P/'Phase1.kicad_sym'))
LibTable(type='sym_lib_table',libs=[Library(name='Phase1',type='KiCad',uri='${KIPRJMOD}/Phase1.kicad_sym'),Library(name='fujinet-amiga',type='KiCad',uri='${KIPRJMOD}/../../kicad/libraries/fujinet-amiga.kicad_sym')]).to_file(str(P/'sym-lib-table'))
print('Wrote',len(specs),'documented pin-map symbols')

import subprocess
subprocess.run(['kicad-cli','sym','upgrade','--force',str(P/'Phase1.kicad_sym')],check=True)
