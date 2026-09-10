#!/usr/bin/env python3
"""Generate the editable passive design. Requires KiCad's pcbnew Python module.

This is an explicit regeneration command: it replaces generated CAD files.
Routing is imported separately from a reviewed Specctra session.
"""
import csv
import json
from pathlib import Path
import uuid
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'kicad'
NAME = 'zorro-breakout'
ROWS = list(csv.DictReader((ROOT / 'data/pin-map.csv').open()))
BY_NET = {r['net_name']: r for r in ROWS}
NS = uuid.UUID('d8c1ce2d-9935-48eb-8d44-f24706cd4f19')
def uid(s): return str(uuid.uuid5(NS, s))
def q(s): return json.dumps(str(s), ensure_ascii=False)
def v(x, y): return p.VECTOR2I(p.FromMM(x), p.FromMM(y))
def mm(n): return p.FromMM(n)
def layers(*ids):
    result=p.LSET()
    for i in ids: result.AddLayer(i)
    return result

# ref, group, XY, paired contacts, per-row nets
GROUPS = [
    ('J2', 'ADDRESS', 108, 38, False, [f'A{i}' for i in range(1,24)]+['GND']),
    ('J3', 'DATA', 132, 38, False, [f'D{i}' for i in range(16)]+['GND']),
    ('J4', 'BUS CONTROL', 158, 48, True,
     ['AS_N','UDS_N','LDS_N','READ','DTACK_N','OVR_N','XRDY','RESET_N',
      'HLT_N','BERR_N','FC0','FC1','FC2','DOE','BUSRST_N','GND']),
    ('J5', 'AUTOCONFIG / SLOT CONTROL', 35, 66, True,
     ['SLAVE_N','CFGIN_N','CFGOUT_N','GND']),
    ('J6', 'INTERRUPTS', 72, 69, True, ['INT2_N','INT6_N','GND']),
    ('J7', 'DMA / ARBITRATION', 72, 88, False,
     ['OWN_N','BR_N','BGACK_N','BG_N','GBG_N','GND']),
    ('J8', 'CLOCKS', 35, 39, True, ['C3_N','CDAC','C1_N','E','CLK7M','GND']),
    ('J9', 'POWER', 35, 92, True, ['+5V','+5V','GND','GND','GND','GND']),
    ('J10', 'RESERVED / LEGACY', 72, 37, False,
     ['RESERVED_40','RESERVED_42','RESERVED_44','RESERVED_96',
      'LEGACY_VPA_N','LEGACY_VMA_N','NC_97','NC_98','SENSEZ3_91','GND']),
]
SPECIAL = {'RESET_N':'/RESET','CLK7M':'7M','SENSEZ3_91':'91 SenseZ3',
           'LEGACY_VPA_N':'48 /VPA*','LEGACY_VMA_N':'51 /VMA*',
           'READ':'READ (R/W)'}
def label(net):
    if net in SPECIAL: return SPECIAL[net]
    if net.startswith('RESERVED_'): return net.split('_')[1]+' Reserved'
    if net.startswith('NC_'): return net.split('_')[1]+' NC'
    r=BY_NET[net]
    return (r['physical_pin']+' ' if net not in ['GND','+5V'] else '')+r['zorro_ii_signal']

def draw_line(board, a, b, layer, width=.15):
    s=p.PCB_SHAPE(); s.SetShape(p.SHAPE_T_SEGMENT); s.SetStart(v(*a)); s.SetEnd(v(*b))
    s.SetLayer(layer); s.SetWidth(mm(width)); board.Add(s)

def text(board, value, x, y, size=1, layer=p.F_SilkS, left=False):
    t=p.PCB_TEXT(board); t.SetText(value); t.SetPosition(v(x,y))
    t.SetTextSize(v(size,size)); t.SetTextThickness(mm(.15)); t.SetLayer(layer)
    if left: t.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT)
    if layer==p.B_SilkS: t.SetMirrored(True)
    board.Add(t)

def track(board, net, a, b, layer, width=.3):
    t=p.PCB_TRACK(board); t.SetStart(v(*a)); t.SetEnd(v(*b)); t.SetLayer(layer)
    t.SetWidth(mm(width)); t.SetNet(net); board.Add(t)

def make_board():
    b=p.BOARD(); b.SetCopperLayerCount(4)
    b.GetDesignSettings().SetBoardThickness(mm(1.6))
    b.GetDesignSettings().m_MinClearance=mm(.2)
    b.GetDesignSettings().m_TrackMinWidth=mm(.25)
    nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass()
    nc.SetTrackWidth(mm(.3)); nc.SetClearance(mm(.2))
    nc.SetViaDiameter(mm(.65)); nc.SetViaDrill(mm(.3))
    nets={}
    for name in sorted(BY_NET):
        n=p.NETINFO_ITEM(b,name); b.Add(n); nets[name]=n
    # Tongue is the dimensioned Zorro edge, not an unqualified rectangular edge.
    outline=[(20,20),(200,20),(200,120),(169.26,120),(169.26,127.62),
             (40,127.62),(40,120),(20,120),(20,20)]
    for a,z in zip(outline,outline[1:]): draw_line(b,a,z,p.Edge_Cuts,.05)
    connector=p.FOOTPRINT(b); connector.SetReference('J1'); connector.SetValue('Zorro-II 100')
    connector.SetFPID(p.LIB_ID('ZorroBreakout','Zorro_II_100'))
    connector.SetPath(p.KIID_PATH('/'+uid('sheet')+'/'+uid('symbol:J1')))
    connector.SetAttributes(p.FP_EXCLUDE_FROM_POS_FILES)
    connector.SetPosition(v(104.63,124.12)); b.Add(connector)
    connector.Reference().SetVisible(False); connector.Value().SetVisible(False)
    for r in ROWS:
        n=int(r['physical_pin']); x=166.86-((n-1)//2)*2.54
        layer=p.F_Cu if n%2==0 else p.B_Cu
        pad=p.PAD(connector); pad.SetNumber(str(n)); pad.SetAttribute(p.PAD_ATTRIB_CONN)
        pad.SetShape(p.PAD_SHAPE_RECT); pad.SetSize(v(1.524,5))
        pad.SetPosition(v(x,124.12)); pad.SetLayerSet(layers(layer,p.F_Mask if n%2==0 else p.B_Mask))
        pad.SetNet(nets[r['net_name']]); connector.Add(pad)
        # Pre-route above the contact zone. Stagger opposite-face vias.
        vy=116 if n%2==0 else 113.5
        vx=x if n%2==0 else x-1
        path=[(x,122),(x,119),(vx,118),(vx,vy)] if n%2 else [(x,122),(vx,vy)]
        for a,z in zip(path,path[1:]):
            track(b,nets[r['net_name']],a,z,layer,.5 if r['net_name']=='GND' else .3)
        via=p.PCB_VIA(b); via.SetPosition(v(vx,vy)); via.SetWidth(mm(.65)); via.SetDrill(mm(.3))
        via.SetViaType(p.VIATYPE_THROUGH); via.SetLayerPair(p.F_Cu,p.B_Cu)
        via.SetNet(nets[r['net_name']]); b.Add(via)
        if n%10 in [0,1]: text(b,str(n),x,119.4,.8,p.F_SilkS if n%2==0 else p.B_SilkS)
    destinations={}
    components={'J1':[(str(r['physical_pin']),r['net_name']) for r in ROWS]}
    def header(ref,title,x,y,paired,ns):
        fp=p.FOOTPRINT(b); fp.SetReference(ref); fp.SetValue(title)
        fname=f'Header_{2 if paired else 1}x{len(ns):02d}'
        fp.SetFPID(p.LIB_ID('ZorroBreakout',fname))
        fp.SetPath(p.KIID_PATH('/'+uid('sheet')+'/'+uid('symbol:'+ref)))
        fp.SetPosition(v(x,y)); fp.SetAttributes(p.FP_THROUGH_HOLE)
        b.Add(fp); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        mapping=[]
        for i,net in enumerate(ns):
            for c in range(2 if paired else 1):
                num=str(i*(2 if paired else 1)+c+1)
                pad=p.PAD(fp); pad.SetNumber(num); pad.SetAttribute(p.PAD_ATTRIB_PTH)
                pad.SetShape(p.PAD_SHAPE_RECT if num=='1' else p.PAD_SHAPE_CIRCLE)
                ls=p.LSET.AllCuMask(); ls.AddLayer(p.F_Mask); ls.AddLayer(p.B_Mask)
                pad.SetSize(v(1.7,1.7)); pad.SetDrillSize(v(1,1)); pad.SetLayerSet(ls)
                pad.SetPosition(v(x+c*2.54,y+i*2.54)); pad.SetNet(nets[net]); fp.Add(pad)
                mapping.append((num,net)); destinations.setdefault(net,[]).append(ref+'.'+num)
            text(b,label(net),x+(6 if paired else 3),y+i*2.54,1,left=True)
            if paired:
                track(b,nets[net],(x,y+i*2.54),(x+2.54,y+i*2.54),p.F_Cu,.5 if net in ['GND','+5V'] else .3)
        components[ref]=mapping
        # Body outlines and generous courtyard.
        for lay,margin in [(p.F_SilkS,1.3),(p.F_CrtYd,1.6)]:
            xa,xb=x-margin,x+(2.54 if paired else 0)+margin
            ya,yb=y-margin,y+(len(ns)-1)*2.54+margin
            for a,z in [((xa,ya),(xb,ya)),((xb,ya),(xb,yb)),((xb,yb),(xa,yb)),((xa,yb),(xa,ya))]:
                shape=p.PCB_SHAPE(fp); shape.SetShape(p.SHAPE_T_SEGMENT)
                shape.SetStart(v(*a)); shape.SetEnd(v(*z)); shape.SetLayer(lay); shape.SetWidth(mm(.12 if lay==p.F_SilkS else .05)); fp.Add(shape)
        text(b,ref,x,y-3.3,1)
        # External library geometry contains no project nets or positions.
        copy=p.FOOTPRINT(fp); copy.SetPosition(v(0,0)); copy.SetReference('REF**'); copy.SetValue(fname)
        for pad in copy.Pads(): pad.SetNetCode(0)
        p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(CAD/'ZorroBreakout.pretty'),copy)
        return fp
    for args in GROUPS: header(*args)
    for i,net in enumerate(['-5V','+12V','-12V'],1):
        ref='TP'+str(i); x=35+(i-1)*13
        header(ref,net+' TEST ONLY',x,83,False,[net])
    # Category titles are separate from pin labels for legibility.
    for val,x,y,size in [('ADDRESS',115,32,1.4),('DATA',138,32,1.4),('BUS CONTROL',174,41,1.4),
                        ('CLOCKS',44,32,1.4),('RESERVED / LEGACY',80,30,1.15),
                        ('AUTOCONFIG',46,59,1.1),('SLOT CONTROL',46,61,1.1),
                        ('INTERRUPTS',83,63,1.15),('DMA / ARBITRATION',84,82,1.05),('POWER',45,87,1.3)]:
        text(b,val,x,y,size)
    text(b,'Fujinet-NIO Amiga Prototyping Board, © Mark Fisher 2026',110,24,1.4)
    text(b,'PASSIVE - NO LEVEL SHIFTING - 5V BUS',140,101,1.2)
    text(b,'Paired header pins carry the SAME signal',140,105,1)
    text(b,'DO NOT CONNECT DIRECTLY TO 3.3V LOGIC',110,109,1.1)
    text(b,'WITHOUT CHECKING ELECTRICAL COMPATIBILITY',110,111,1.1)
    text(b,'COMPONENT SIDE',183,94,1)
    text(b,'PIN 2 / PIN 1 ON REVERSE',177,117,1)
    text(b,'ZORRO PIN 1',177,117,1,p.B_SilkS)
    text(b,'SOLDER SIDE - ODD PINS',110,107,1.5,p.B_SilkS)
    # Continuous internal reference plane, pulled back from finger/tongue area.
    zone=p.ZONE(b); zone.SetLayer(p.In1_Cu); zone.SetNet(nets['GND']); zone.SetLocalClearance(mm(.25))
    zone.SetThermalReliefGap(mm(.25)); zone.SetThermalReliefSpokeWidth(mm(.3))
    zone.Outline().NewOutline()
    for xy in [(21,21),(199,21),(199,118),(21,118)]: zone.Outline().Append(int(mm(xy[0])),int(mm(xy[1])))
    b.Add(zone)
    # Library copy of the exact edge geometry, no copied upstream artwork.
    copy=p.FOOTPRINT(connector); copy.SetPosition(v(0,0)); copy.SetReference('REF**')
    for pad in copy.Pads(): pad.SetNetCode(0)
    p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(CAD/'ZorroBreakout.pretty'),copy)
    p.SaveBoard(str(CAD/(NAME+'.kicad_pcb')),b)
    dsn=ROOT/'routing'/(NAME+'.dsn')
    p.ExportSpecctraDSN(b,str(dsn))
    # Reserve In1 for a continuous GND plane; never let routing split it.
    content=dsn.read_text().replace('(layer In1.Cu\n      (type signal)', '(layer In1.Cu\n      (type power)')
    content=content.replace('    (boundary\n', '''
    (autoroute_settings
      (layer_rule F.Cu (active on) (preferred_direction vertical))
      (layer_rule In1.Cu (active off) (preferred_direction horizontal))
      (layer_rule In2.Cu (active on) (preferred_direction horizontal))
      (layer_rule B.Cu (active on) (preferred_direction vertical))
    )
    (boundary
''')
    dsn.write_text(content)
    with (ROOT/'data/verification.csv').open('w',newline='') as out:
        w=csv.writer(out); w.writerow(['physical_pin','zorro_ii_signal','schematic_net_name','pcb_footprint_pad','header_testpoint_references','category'])
        for r in ROWS:
            w.writerow([r['physical_pin'],r['zorro_ii_signal'],r['net_name'],'J1.'+r['physical_pin'],
                        ';'.join(destinations[r['net_name']]),r['category']])
    return components

def make_schematic(components):
    """Self-contained native schematic with passive connector symbols and named nets."""
    lib=[]; placed=[]; wires=[]; labels=[]; annotations=[]
    # One A2 sheet: edge at left; categorized headers in three columns.
    poses={'J1':(55,45)}
    for i,ref in enumerate(list(components)[1:]):
        col=i%3; row=i//3; poses[ref]=(240+col*105,[45,140,230,300][row])
    for ref,mapping in components.items():
        if ref=='J1':
            count=100; name='Zorro_II_100'; rows=50; pitch=5.08; width=55.88
        else:
            count=len(mapping); name='Connector_'+str(count); rows=count; pitch=2.54; width=12.7
        # Unique symbol per reference avoids library name collisions with different functions.
        libname='ZorroBreakout:'+ref
        height=(rows-1)*pitch
        body=f'(rectangle (start 0 2.54) (end {width} {-height-2.54}) (stroke (width .254) (type default)) (fill (type background)))'
        pins=[]
        for i,(num,net) in enumerate(mapping):
            idx=i//2 if ref=='J1' else i
            right=(ref=='J1' and int(num)%2==0)
            px=width+5.08 if right else -5.08; py=-idx*pitch
            pinname=net if ref=='J1' else num
            pins.append(f'(pin passive line (at {px} {py} {180 if right else 0}) (length 5.08) (name {q(pinname)} (effects (font (size 1 1)))) (number {q(num)} (effects (font (size 1 1)))))')
        lib.append(f'(symbol {q(libname)} (pin_names (offset .5)) (in_bom yes) (on_board yes) (property "Reference" "J" (at 0 5.08 0) (effects (font (size 1.27 1.27)))) (property "Value" {q(name)} (at 0 7.62 0) (effects (font (size 1.27 1.27)))) (symbol {q(ref+"_0_1")} {body}) (symbol {q(ref+"_1_1")} {" ".join(pins)}))')
        x,y=(round(a/1.27)*1.27 for a in poses[ref])
        title='Zorro-II 100' if ref=='J1' else next((g[1] for g in GROUPS if g[0]==ref),mapping[0][1]+' TEST ONLY')
        footprint='ZorroBreakout:Zorro_II_100' if ref=='J1' else 'ZorroBreakout:'+next(
            ('Header_'+str(2 if g[4] else 1)+'x'+f'{len(g[5]):02d}' for g in GROUPS if g[0]==ref),'Header_1x01')
        placed.append(f'''(symbol (lib_id {q(libname)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)
          (uuid {uid('symbol:'+ref)})
          (property "Reference" {q(ref)} (at {x+width/2} {y-7.62} 0) (effects (font (size 1.27 1.27))))
          (property "Value" {q(title)} (at {x+width/2} {y-5.08} 0) (effects (font (size 1.27 1.27))))
          (property "Footprint" {q(footprint)} (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
          {''.join(f'(pin {q(num)} (uuid {uid(ref+":pin:"+num)}))' for num,net in mapping)}
          (instances (project {q(NAME)} (path "/{uid('sheet')}" (reference {q(ref)}) (unit 1)))))''')
        for i,(num,net) in enumerate(mapping):
            idx=i//2 if ref=='J1' else i; right=ref=='J1' and int(num)%2==0
            px=x+width+5.08 if right else x-5.08; py=y+idx*pitch
            end=px+7.62 if right else px-7.62
            wires.append(f'(wire (pts (xy {px} {py}) (xy {end} {py})) (stroke (width 0) (type default)) (uuid {uid(ref+":wire:"+num)}))')
            labels.append(f'(global_label {q(net)} (shape bidirectional) (at {end} {py} {180 if right else 0}) (effects (font (size 1 1)) (justify {"left" if right else "right"})) (uuid {uid(ref+":label:"+num)}))')
    for i,(val,x,y) in enumerate([
        ('PASSIVE ZORRO-II BREAKOUT — no active electronics; no level shifting',25,20),
        ('J1: odd contacts = reverse / even contacts = component side. Pin 28=A7; pin 29=A1.',25,315),
        ('Reserved, NC, legacy and SenseZ3 points remain isolated. NC describes the host function, not an unrouted pad.',25,322),
        ('Paired header pins share the same net. CFGlN/CFGOUT are NOT bridged. See README for downstream-card configuration.',25,329),
        ('DO NOT CONNECT DIRECTLY TO 3.3V LOGIC WITHOUT CHECKING ELECTRICAL COMPATIBILITY',25,336),
        ('Mechanical release hold: confirm bevel callout against a legible A-5 / mating connector drawing.',25,343),
        ('Fujinet-NIO Amiga Prototyping Board, © Mark Fisher 2026',25,355)]):
        annotations.append(f'(text {q(val)} (at {x} {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid("note:"+str(i))}))')
    content=f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid('sheet')}) (paper "A2")
      (title_block (title "Passive Zorro-II development breakout") (date "2026-09-10") (rev "A-review") (company "Mark Fisher"))
      (lib_symbols {''.join(lib)}) {''.join(wires)} {''.join(labels)} {''.join(placed)} {''.join(annotations)})'''
    (CAD/(NAME+'.kicad_sch')).write_text(content)
    (CAD/'ZorroBreakout.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(lib).replace('ZorroBreakout:','')+')')

def main():
    for folder in ['kicad/ZorroBreakout.pretty','routing','fabrication','review','data']:
        (ROOT/folder).mkdir(parents=True,exist_ok=True)
    (CAD/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "ZorroBreakout") (type "KiCad") (uri "${KIPRJMOD}/ZorroBreakout.pretty") (options "") (descr "Project-local passive connectors")))\n')
    (CAD/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "ZorroBreakout") (type "KiCad") (uri "${KIPRJMOD}/ZorroBreakout.kicad_sym") (options "") (descr "Project-local passive symbols")))\n')
    project={'meta':{'filename':NAME+'.kicad_pro','version':1},
             'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.25,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_copper_edge_clearance':.5}}},
             'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.3,'via_diameter':.65,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.3,'diff_pair_gap':.25,'diff_pair_via_gap':.25,'wire_width':6,'bus_width':12}],'meta':{'version':3}}}
    (CAD/(NAME+'.kicad_pro')).write_text(json.dumps(project,indent=2)+'\n')
    components=make_board(); make_schematic(components)
    print('Generated CAD, project-local libraries, routing input, and verification table.')

if __name__=='__main__': main()
