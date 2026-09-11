# Reproducible local routing

The stored DSN and SES are the pre-mechanical-release routing input and
output for revision A. The released PCB retains exactly those routed
tracks/vias, but has the approved A-5 outline, finger widths and continuous
mask window applied by `scripts/mechanics.py`. The stored DSN is not the
current fabrication outline.
No cloud router was used. Routing uses Freerouting **2.4.1**, downloaded from
its [official release](https://github.com/freerouting/freerouting/releases/tag/v2.4.1).
The Linux distribution archive SHA256 is
`3ad5a956ab474b12f331d24195feadac90e8344b8e013c6a4ab26e203ce51519`.
The executable JAR is inside `lib/app/freerouting-executable.jar`.

After `python scripts/generate.py`, from the project directory:

```sh
java -Xmx2g -Djava.awt.headless=true -jar /path/to/freerouting-executable.jar \
  -de routing/zorro-breakout.dsn -do routing/zorro-breakout.ses \
  -mp 20 -mt 1 -da --gui.enabled=false --api_server.enabled=false \
  --router.job_timeout=00:02:00 --router.optimizer.enabled=false
python scripts/import-routing.py
python scripts/check.py
```

In1.Cu is explicitly disabled for signal routing; it is the GND plane.
The generator supplies the complete finger fan-out. The import script removes
only redundant vias/dead-end traces identified by fresh KiCad DRC reports,
then refills the plane. Final connectivity is judged by KiCad after import,
not by the router's completion message.

The stored session can be reimported without installing or running Java.
Do not reuse it after moving headers or changing connectivity/mechanics;
generate and review new routing instead. Regeneration overwrites the CAD.
