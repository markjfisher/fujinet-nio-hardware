# Reproducible two-layer routing

The checked-in DSN and SES describe the current two-layer routing candidate.
The reviewed `two-layer-completion.json` completes GND, BERR and INT2 after
SES import and dangling-copper cleanup. It is bound to the exact session
SHA256 and pad/placement digest; it must not be applied to arbitrary new
routing sessions. The old four-layer board is available at repository commit
`7d2c536cdc554b39942488d1791c985eb286db0b`.

Reproduce the current board (explicitly overwrites generated CAD):

```sh
python scripts/generate.py
python scripts/import-routing.py
python scripts/check.py
python scripts/export.py
```

No router or NumPy installation is needed for that replay. The generator
retains the established footprints, silkscreen and A-5 geometry, prepares
straight finger escapes/duplicate-header links and exports a two-layer DSN.
Import fills both GND pours and removes unconnected islands. The complete
pipeline was tested in a scratch copy, as well as checking the release PCB.

To explore a new route without overwriting the release:

```sh
python scripts/two_layer.py /path/to/new-candidate
java -Xmx2g -Djava.awt.headless=true -jar /path/to/freerouting-executable.jar \
  -de /path/to/new-candidate/zorro-breakout.dsn \
  -do /path/to/new-candidate/zorro-breakout.ses \
  -mp 30 -mt 1 -da --gui.enabled=false --api_server.enabled=false \
  --router.job_timeout=00:04:00 --router.optimizer.enabled=true
python scripts/import-routing.py \
  --pcb /path/to/new-candidate/zorro-breakout.kicad_pcb \
  --session /path/to/new-candidate/zorro-breakout.ses --ground-pours
```

The selected base session came from local Freerouting **2.4.1**; no cloud
router was used. Signals use 0.30 mm tracks; power/GND 0.60; clearance 0.20.
A via keepout protects the tongue. Router completion messages are not
acceptance: the initial session had three missing connections, subsequently
completed and verified in KiCad. New sessions need their own completion
review, full verification and DRC; do not reuse the hash-bound paths blindly.

The router's [official release](https://github.com/freerouting/freerouting/releases/tag/v2.4.1)
Linux archive SHA256 is
`3ad5a956ab474b12f331d24195feadac90e8344b8e013c6a4ab26e203ce51519`.
The JAR is `lib/app/freerouting-executable.jar`.

Metrics and return-path limitations: [two-layer review](../docs/two-layer-review.md).
