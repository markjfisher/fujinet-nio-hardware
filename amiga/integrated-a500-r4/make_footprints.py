"""Native pcbnew API for custom footprints: MCP has no pad/library construction.

Never writes the shared library or prior candidates. Geometric facts for J40
are cross-checked against Matze's LKONT_43-SLOT-SOLDER and supplied Gerbers.
"""
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parent
LIB = ROOT / 'candidate.pretty'
LIB.mkdir(exist_ok=True)
def v(x,y): return k.VECTOR2I(k.FromMM(x), k.FromMM(y))
def footprint(name, description):
    f=k.FOOTPRINT(None); f.SetFPID(k.LIB_ID('candidate',name)); f.SetLibDescription(description)
    f.SetAttributes(k.FP_SMD); f.Reference().SetVisible(False); f.Value().SetVisible(False)
    return f
def pad(f,number,x,y,w,h,layer,paste=True):
    p=k.PAD(f); p.SetNumber(str(number)); p.SetAttribute(k.PAD_ATTRIB_SMD)
    p.SetShape(k.PAD_SHAPE_RECT); p.SetPosition(v(x,y)); p.SetSize(v(w,h))
    mask=k.F_Mask if layer==k.F_Cu else k.B_Mask
    layers=[layer,mask]
    if paste: layers.append(k.F_Paste if layer==k.F_Cu else k.B_Paste)
    ls=k.LSET()
    for layer_id in layers: ls.AddLayer(layer_id)
    p.SetLayerSet(ls); f.Add(p)
def line(f,x1,y1,x2,y2,layer=k.F_Fab,width=.1):
    s=k.PCB_SHAPE(f); s.SetShape(k.SHAPE_T_SEGMENT); s.SetStart(v(x1,y1));s.SetEnd(v(x2,y2));s.SetLayer(layer);s.SetWidth(k.FromMM(width));f.Add(s)
def box(f,x1,y1,x2,y2,layer):
    for a,b in [((x1,y1),(x2,y1)),((x2,y1),(x2,y2)),((x2,y2),(x1,y2)),((x1,y2),(x1,y1))]:line(f,*a,*b,layer)
def save(f):
    plugin=k.PCB_IO_MGR.FindPlugin(k.PCB_IO_MGR.KICAD_SEXP)
    plugin.FootprintSave(str(LIB),f)
    assert (LIB/(str(f.GetFPID().GetLibItemName())+'.kicad_mod')).exists()

f=footprint('A500_ED86_EdgeSolder','Wing Tat ED86BGFBK assembly reference; horizontal sidecar. Matze LKONT_43-SLOT-SOLDER geometry. Hand solder, no paste. Qualification pending.')
# Local x=0 is PCB edge. +x points toward Amiga, -x into sidecar.
# Eagle x -> KiCad y, Eagle y -> KiCad x accounts for opposite y conventions.
for i in range(43):
    y=-53.34+i*2.54
    pad(f,2*i+1,-5.334,y,9.5,1.65,k.F_Cu,False)
    pad(f,2*i+2,-5.334,y,9.5,1.65,k.B_Cu,False)
line(f,0,-55.88,0,55.88,k.Dwgs_User)
box(f,-10.334,-56.13,.25,56.13,k.F_CrtYd)
box(f,-10.334,-56.13,.25,56.13,k.B_CrtYd)
line(f,-11,-53.34,-12,-53.34,k.F_SilkS,.2)
save(f)

print('Native A500 footprint saved:', LIB)
