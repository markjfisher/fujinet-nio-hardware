#!/usr/bin/env python3
"""Compare the reviewed CSV with actual exported schematic nets and PCB pads.

Does not import the generator. ERC/DRC separately test the routed copper.
--self-test deliberately corrupts inputs in memory to prove mismatches fail.
"""
import argparse
from collections import defaultdict
import copy
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]
DUPLICATE={'AS_N','UDS_N','LDS_N','READ','DTACK_N','SLAVE_N','CFGIN_N',
           'CFGOUT_N','INT2_N','INT6_N','RESET_N','DOE','CLK7M','E'}

def compare(rows, schematic, pcb, table):
    """All four independently serialized artifacts must describe the same nets."""
    if [int(r['physical_pin']) for r in rows]!=list(range(1,101)):
        raise ValueError('CSV must enumerate physical pins 1–100 exactly once, in order')
    if set(k for k in pcb if k[0]=='J1')!={('J1',str(n)) for n in range(1,101)}:
        raise ValueError('PCB must have exactly 100 edge contacts')
    if len(table)!=100: raise ValueError('Verification table must have 100 rows')
    if set(schematic)!=set(pcb): raise ValueError('Schematic/PCB component pad sets differ')
    if schematic!=pcb:
        raise ValueError('Schematic/PCB net assignments differ: '+str([k for k in pcb if pcb[k]!=schematic[k]]))
    for r,t in zip(rows,table):
        n=r['physical_pin']; expected=r['net_name']; key=('J1',n)
        if schematic.get(key)!=expected or pcb.get(key)!=expected:
            raise ValueError(f'Pin {n}: expected {expected}, schematic={schematic.get(key)}, PCB={pcb.get(key)}')
        destinations={ref+'.'+pin for (ref,pin),net in pcb.items() if ref!='J1' and net==expected}
        if not destinations: raise ValueError(f'Pin {n} has no breakout')
        if set(t['header_testpoint_references'].split(';'))!=destinations:
            raise ValueError(f'Pin {n}: verification table destinations differ')
        for field,value in [('physical_pin',n),('zorro_ii_signal',r['zorro_ii_signal']),
                            ('schematic_net_name',expected),('pcb_footprint_pad','J1.'+n),('category',r['category'])]:
            if t[field]!=value: raise ValueError(f'Pin {n}: stale verification {field}')
        if expected in DUPLICATE and len(destinations)<2:
            raise ValueError(f'{expected} lacks duplicate access')
    if pcb['J1','28']!='A7' or pcb['J1','29']!='A1': raise ValueError('Printed AHRM 28/29 correction lost')
    isolated=[40,42,44,48,51,91,96,97,98]
    if len({pcb['J1',str(n)] for n in isolated})!=len(isolated): raise ValueError('Reserved/legacy contacts shorted together')
    if pcb['J1','91']=='GND': raise ValueError('SenseZ3 incorrectly grounded by board')
    for n in [8,10,20]:
        if any(ref!='J1' and not ref.startswith('TP') for (ref,pin),net in pcb.items() if net==pcb['J1',str(n)]):
            raise ValueError('Auxiliary rail escaped its dedicated test point')
    if pcb['J1','11']==pcb['J1','12']: raise ValueError('AutoConfig chain unintentionally bridged')

def run(self_test=False):
    rows=list(csv.DictReader((ROOT/'data/pin-map.csv').open()))
    table=list(csv.DictReader((ROOT/'data/verification.csv').open()))
    xml=ET.parse(ROOT/'review/schematic.net.xml')
    schematic={}
    for net in xml.findall('./nets/net'):
        for node in net.findall('node'):
            key=(node.attrib['ref'],node.attrib['pin'])
            if key in schematic: raise ValueError('Duplicate schematic node '+str(key))
            schematic[key]=net.attrib['name']
            if node.attrib['pintype']!='passive': raise ValueError('Non-passive symbol pin')
    b=p.LoadBoard(str(ROOT/'kicad/zorro-breakout.kicad_pcb'))
    pcb={}; footprints={fp.GetReference():fp for fp in b.GetFootprints()}
    for ref,fp in footprints.items():
        for pad in fp.Pads():
            key=(ref,pad.GetNumber())
            if key in pcb: raise ValueError('Duplicate physical pad '+str(key))
            pcb[key]=pad.GetNetname()
    compare(rows,schematic,pcb,table)
    assert b.GetCopperLayerCount()==4
    assert abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-1.6)<1e-6
    for pad in footprints['J1'].Pads():
        n=int(pad.GetNumber()); x=p.ToMM(pad.GetPosition().x); y=p.ToMM(pad.GetPosition().y)
        assert abs(x-(166.86-((n-1)//2)*2.54))<1e-6, f'Pin {n}: wrong X/pitch'
        assert abs(y-124.12)<1e-6, f'Pin {n}: wrong contact Y'
        assert abs(p.ToMM(pad.GetSize().x)-1.524)<1e-6
        assert abs(p.ToMM(pad.GetSize().y)-5)<1e-6
        assert pad.GetAttribute()==p.PAD_ATTRIB_CONN
        expected=p.F_Cu if n%2==0 else p.B_Cu
        other=p.B_Cu if n%2==0 else p.F_Cu
        assert pad.IsOnLayer(expected) and not pad.IsOnLayer(other), f'Pin {n}: face assignment'
        assert not pad.IsOnLayer(p.F_Paste) and not pad.IsOnLayer(p.B_Paste)
        assert pad.IsOnLayer(p.F_Mask if n%2==0 else p.B_Mask)
    # Every header uses standard 2.54 mm positions and a 1 mm finished hole.
    for ref,fp in footprints.items():
        if ref=='J1': continue
        origin=fp.GetPosition()
        for pad in fp.Pads():
            for delta in [pad.GetPosition().x-origin.x,pad.GetPosition().y-origin.y]:
                pitch=p.ToMM(delta)/2.54
                assert abs(pitch-round(pitch))<1e-5, ref+' header grid'
            assert abs(p.ToMM(pad.GetDrillSize().x)-1)<1e-6
    # Geometry includes the actual tongue, not merely the contact span.
    edge_segments=set()
    # KiCad 10's DRAWINGS iterator still calls Python 2's it.next().
    for i in range(len(b.Drawings())):
        d=b.Drawings()[i].Cast()
        if d.GetLayer()==p.Edge_Cuts:
            edge_segments.add(tuple(round(p.ToMM(z),5) for z in [d.GetStart().x,d.GetStart().y,d.GetEnd().x,d.GetEnd().y]))
    assert (169.26,127.62,40.,127.62) in edge_segments
    assert (169.26,120.,169.26,127.62) in edge_segments
    assert (40.,127.62,40.,120.) in edge_segments
    for i in range(len(b.Tracks())):
        item=b.Tracks()[i].Cast()
        if isinstance(item,p.PCB_VIA):
            assert p.ToMM(item.GetPosition().y)+p.ToMM(item.GetWidth(p.F_Cu))/2<120, 'Via in mating tongue'
        else:
            assert item.GetLayer()!=p.In1_Cu, 'Signal routing splits reference plane'
            if item.GetLayer()==p.In2_Cu:
                assert p.ToMM(max(item.GetStart().y,item.GetEnd().y))+p.ToMM(item.GetWidth())/2<120, 'Inner copper in tongue'
    tested=0
    if self_test:
        # Mutate each artifact independently, including an incorrect face mapping
        # represented as exchanged connector assignments.
        cases=[]
        bad=pcb.copy(); bad['J1','28'],bad['J1','29']=bad['J1','29'],bad['J1','28']; cases.append((rows,schematic,bad,table))
        bad=schematic.copy(); bad['J4','1']='GND'; cases.append((rows,bad,pcb,table))
        bad=copy.deepcopy(rows); bad[27]['net_name']='A1'; cases.append((bad,schematic,pcb,table))
        bad=copy.deepcopy(table); bad[0]['header_testpoint_references']='J9.1'; cases.append((rows,schematic,pcb,bad))
        bad=pcb.copy(); del bad['J1','100']; cases.append((rows,schematic,bad,table))
        for case in cases:
            try: compare(*case)
            except ValueError: tested+=1
            else: raise AssertionError('Mutation escaped consistency checker')
    result={'status':'PASS','physical_contacts':100,'schematic_pcb_pads':len(pcb),
            'nets':len(set(pcb.values())),'duplicate_signals_checked':len(DUPLICATE),
            'negative_cases_rejected':tested,'geometry':'PASS','passive_symbols':'PASS'}
    (ROOT/'review/consistency.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--self-test',action='store_true')
    run(ap.parse_args().self_test)
