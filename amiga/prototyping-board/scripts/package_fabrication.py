#!/usr/bin/env python3
"""Run export and package fabrication outputs for PCBWay upload."""

import sys
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAB = ROOT / 'fabrication'
BUILD = ROOT / 'build'
EXPORT_SCRIPT = ROOT / 'scripts' / 'export.py'
ARCHIVE_NAME = 'zorro-breakout-fabrication.zip'


def run_export() -> None:
    """Run the existing export flow to refresh and verify all outputs."""
    subprocess.run([sys.executable, str(EXPORT_SCRIPT)], cwd=ROOT, check=True)


def collect_fabrication_files() -> list[Path]:
    """Collect files required for PCBWay upload."""
    files = []
    for subdir in ('gerbers', 'drill'):
        folder = FAB / subdir
        if not folder.exists():
            raise FileNotFoundError(f'Required fabrication folder missing: {folder}')
        files.extend(sorted(p for p in folder.rglob('*') if p.is_file()))

    for required in (FAB / 'README.md', FAB / 'SHA256SUMS'):
        if not required.exists():
            raise FileNotFoundError(f'Required file missing: {required}')
        files.append(required)

    return files


def main() -> None:
    run_export()
    files = collect_fabrication_files()

    BUILD.mkdir(exist_ok=True)
    archive = BUILD / ARCHIVE_NAME
    with zipfile.ZipFile(archive, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, arcname=str(path.relative_to(ROOT)))

    print(f'Created fabrication package: {archive}')


if __name__ == '__main__':
    main()
