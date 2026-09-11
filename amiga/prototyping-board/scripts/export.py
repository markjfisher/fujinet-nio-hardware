#!/usr/bin/env python3
"""Export current design only after verification; never order or upload it."""
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
PCB='kicad/zorro-breakout.kicad_pcb'
def run(*args): subprocess.run(args,cwd=ROOT,check=True)

def main():
    run(sys.executable,'scripts/check.py')
    (ROOT/'fabrication/gerbers').mkdir(exist_ok=True)
    (ROOT/'fabrication/drill').mkdir(exist_ok=True)
    run('kicad-cli','pcb','export','gerbers',PCB,'--layers',
        'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts',
        '--output','fabrication/gerbers/','--check-zones')
    run('kicad-cli','pcb','export','drill',PCB,'--output','fabrication/drill/',
        '--excellon-units','mm','--excellon-separate-th','--generate-map','--generate-report',
        '--report-path','fabrication/drill/report.txt')
    run('kicad-cli','sch','export','pdf','kicad/zorro-breakout.kicad_sch','--output','review/schematic.pdf')
    run('kicad-cli','sch','export','svg','kicad/zorro-breakout.kicad_sch','--output','review/')
    for side in ['front','back']:
        prefix='F' if side=='front' else 'B'
        args=['kicad-cli','pcb','export','svg',PCB,'--layers',f'{prefix}.SilkS,{prefix}.Mask,Edge.Cuts',
              '--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--black-and-white',
              '--output',f'review/layout-{side}.svg']
        if side=='back': args.append('--mirror')
        run(*args)
    run('kicad-cli','pcb','export','svg',PCB,'--layers','F.Cu,In1.Cu,In2.Cu,B.Cu,Edge.Cuts',
        '--mode-multi','--fit-page-to-board','--exclude-drawing-sheet','--output','review/copper/')
    # KiCad emits trailing spaces after filled-mask SVG paths.
    for svg in (ROOT/'review').rglob('*.svg'):
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    files=sorted(p for folder in ['fabrication/gerbers','fabrication/drill'] for p in (ROOT/folder).iterdir() if p.is_file())
    files.append(ROOT/'fabrication/README.md')
    (ROOT/'fabrication/SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT/'fabrication'))+'\n' for p in files))
    print('Exported local review/fabrication outputs. No files were uploaded or ordered.')

if __name__=='__main__': main()
