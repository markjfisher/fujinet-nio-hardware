#!/usr/bin/env python3
"""Verify current design without regenerating it. Source workspace env first."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
CAD='kicad/zorro-breakout'
def run(*args):
    print('+ '+' '.join(args),flush=True)
    subprocess.run(args,cwd=ROOT,check=True)

def main():
    run('kicad-cli','sch','export','netlist',CAD+'.kicad_sch','--format','kicadxml','--output','review/schematic.net.xml')
    run(sys.executable,'scripts/verify.py','--self-test')
    run('kicad-cli','sch','erc',CAD+'.kicad_sch','--severity-all','--exit-code-violations','--output','review/erc.rpt')
    run('kicad-cli','pcb','drc',CAD+'.kicad_pcb','--refill-zones','--save-board','--schematic-parity',
        '--severity-all','--exit-code-violations','--format','json','--output','review/drc.json')
    run('kicad-cli','pcb','drc',CAD+'.kicad_pcb','--schematic-parity','--severity-all',
        '--exit-code-violations','--output','review/drc.rpt')
    result=json.loads((ROOT/'review/drc.json').read_text())
    for key in ['violations','unconnected_items','schematic_parity']:
        assert not result[key], key+' is not empty'
    print('PASS: 100-contact consistency, geometry, negative cases, ERC, DRC and schematic parity.')

if __name__=='__main__': main()
