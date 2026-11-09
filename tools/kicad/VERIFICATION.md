# Local tool verification — 2026-11-09

Scope: tools/setup only. No production schematic, board or fabrication artifact
was changed. Selected server: blwfish/kicad-mcp `0.18.2`, source commit
`c6a72ab643ed3b8d862325e3012b47e62792ce6f`. Dependencies are in `requirements.lock`.

Environment: Linux, native KiCad and pcbnew 10.0.7, MCP Python 3.13.15,
FastMCP 4.1.6, kicad-sch-api 0.5.6, FreeRouter 2.2.3, Java 26.0.2.1.

Commands from workspace root:

```sh
source scripts/env.sh
repos/fujinet-nio-hardware/tools/kicad/setup
repos/fujinet-nio-hardware/.local-tools/kicad/venv/bin/python \
  repos/fujinet-nio-hardware/tools/kicad/smoke.py
```

Result: **PASS for the tool integration**. Smoke fixture contained two 10k
0603 resistors, one connecting net and intentionally unconnected outer pins.

| Observation | Evidence |
| --- | --- |
| MCP handshake and tool discovery | 18 tools; required schematic/PCB/library/router tools present |
| Installed library lookup | Device resistor symbol and 0603 resistor footprint found |
| Schematic generation | KiCad XML export contains R1=10k and `/SMOKE` joining exactly R1.2 and R2.1 |
| PCB edit | Native pcbnew independently reads R1 at (55, 50) mm, value 10k, two pads |
| Autorouting | One pass, one copper segment, zero vias, zero unconnected items |
| Independent KiCad DRC | Zero violations and zero unconnected items on the scratch PCB |
| Independent KiCad ERC | Two expected `pin_not_connected` errors for the intentionally incomplete schematic |

The smoke does not check schematic/PCB UUID parity, render quality, preservation
of an existing routed design, coupled USB routing, electrical behaviour or
manufacturing readiness. Those are not implied by its pass. Real designs need
schematic parity and visual review as specified in the operating guide.

Raw local artifacts: `/tmp/fujinet-kicad-smoke-juxb8e1g/`, including
`evidence.json`, KiCad files, netlist and check reports. A compact persistent
result is [smoke-result.json](smoke-result.json); the script recreates fresh
artifacts rather than depending on `/tmp` retention.

The initial sandboxed stdio probe started the server but did not complete the
handshake; the same check and the full smoke succeeded outside that execution
sandbox. This is an environment limitation, not evidence that every client
integration is working. User-level Codex registration `fujinet_kicad` points to
the repository launcher; the current conversation's tool catalogue is not
hot-reloaded. Verify availability in a new session.

Early smoke-script corrections concerned a plain-text guidance response, a
Python parameter-name collision, and KiCad's `/` prefix for root-sheet local
nets. No upstream code changes or workarounds were needed for the passing run.

Additional checks passed: repeat `setup` (72 pinned packages unchanged, router
hash verified), `bash -n` for setup/launcher, Python AST parsing, local Markdown
link existence, `git diff --check` in workspace and hardware repo, and
`codex mcp get fujinet_kicad` (enabled, stdio, expected absolute launcher path).
