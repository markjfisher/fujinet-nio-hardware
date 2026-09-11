#!/usr/bin/env python3
"""Read-only route/placement metrics; lengths exclude copper-pour paths."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import pcbnew as p


def placement_digest(b):
    pads=sorted((f.GetReference(), pad.GetNumber(), pad.GetNetname(),
                 pad.GetPosition().x,pad.GetPosition().y,pad.GetSize().x,
                 pad.GetSize().y,pad.GetDrillSize().x,pad.GetDrillSize().y,
                 pad.GetLayerSet().FmtHex(),pad.GetOrientationDegrees())
                for f in b.GetFootprints() for pad in f.Pads())
    return hashlib.sha256(json.dumps(pads).encode()).hexdigest()


def metrics(b):
    count=Counter(); length=Counter(); via_nets=Counter(); widths={}
    for i in range(len(b.Tracks())):
        t=b.Tracks()[i].Cast()
        if isinstance(t,p.PCB_VIA): via_nets[t.GetNetname()]+=1
        else:
            layer=b.GetLayerName(t.GetLayer());count[layer]+=1
            length[layer]+=p.ToMM(t.GetLength())
            widths[t.GetNetname()]=min(widths.get(t.GetNetname(),1e9),p.ToMM(t.GetWidth()))
    return dict(layers=b.GetCopperLayerCount(), placement_sha256=placement_digest(b),
                segments=dict(count),length_mm={k:round(v,3) for k,v in length.items()},
                total_length_mm=round(sum(length.values()),3),via_count=sum(via_nets.values()),
                via_nets=dict(sorted(via_nets.items())),minimum_width_by_net=widths,
                ground_zones=[dict(layer=b.GetLayerName(z.GetLayer()),
                                   net=z.GetNetname(),area_mm2=round(z.GetFilledArea()/1e12,2))
                              for z in b.Zones() if not z.GetIsRuleArea()])


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('pcb',type=Path)
    ap.add_argument('--output',type=Path);args=ap.parse_args()
    result=metrics(p.LoadBoard(str(args.pcb)))
    result['pcb_sha256']=hashlib.sha256(args.pcb.read_bytes()).hexdigest()
    text=json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    else: print(text,end='')
