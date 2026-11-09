"""Apply the reviewed KiCad 10 private-property formatter compatibility patch."""
from pathlib import Path
import hashlib
import inspect
import subprocess
import kicad_sch_api.core.formatter as formatter
path = Path(inspect.getfile(formatter))
original = '857948f643179ad80a1a366326ff0578a97d51728c5a357726b174f7a2de5849'
patched = 'addb84b52aad7df6d7ef1bd8654a5312558bb0fd2a60f4934cc782a936ce7502'
digest = hashlib.sha256(path.read_bytes()).hexdigest()
if digest == original:
    patch = Path(__file__).with_name('patches') / 'kicad10-private-properties.patch'
    subprocess.run(['patch', '--batch', str(path), str(patch)], check=True)
elif digest != patched:
    raise SystemExit('Unrecognized formatter source; review compatibility patch before applying')
assert hashlib.sha256(path.read_bytes()).hexdigest() == patched
print('KiCad 10 private-property compatibility patch present')
