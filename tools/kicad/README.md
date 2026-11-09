# KiCad tooling decision and agent operating guide

Decision: 2026-11-09. Use **blwfish/kicad-mcp** as the primary CAD execution
tool, with **native KiCad 10.0.7** as the independent checker. Use one server,
not four overlapping writers. This is a tooling selection, not approval of an
Amiga circuit or production layout.

## Comparison

Reviewed the source snapshots below, not just repository descriptions. The
selection favours a usable local schematic/placement/routing workflow over
tool count or stars. Only the selected tool was installed and exercised here;
the other three assessments are source/document reviews.

| Candidate | Useful capability | Material limitation for this project | Decision |
| --- | --- | --- | --- |
| [mash/kicad-skills](https://github.com/mash/kicad-skills/tree/a74dbcb96d0fcd98aa597061ef89e4f1b1aec7b4) | Compact CLI queries, dry-run edits, baseline comparisons, schematic visual cleanup | Its documented symbol-add operation clones an existing sibling; the PCB edit surface is mostly footprint edits/sync, not a complete placement/router workflow. Depends on a pinned fork of kiutils. | Useful focused fallback; do not install a second CAD writer now. |
| [AvatarSD/KiSkill](https://github.com/AvatarSD/KiSkill/tree/b27ce9e0f7bee10ef6dd606baabcbaf0c3c1eecc) | Headless engine, visual/semantic review, optional live PCB IPC | Routing implementation hard-codes Flatpak KiCad and a separately unpacked router bundle. This conflicts with our native installation. Its broad workflow still needs agent-authored procedural construction and placement choices. | Keep as an alternative; avoid adapting its platform plumbing now. |
| [nevenfo/kicad-agentic-mcp](https://github.com/nevenfo/kicad-agentic-mcp/tree/fc568cf188911e5a91ede54798003fe074b19404) | Typed plans, transactional edits, revision checks, live PCB IPC and evidence | Live PCB work needs the editor/API running. Maintainer reports limited Linux live QA. Stronger transaction model, but extra desktop coupling for our immediate workflow. | Preferred candidate if live GUI editing becomes necessary; not a second simultaneous writer. |
| [blwfish/kicad-mcp](https://github.com/blwfish/kicad-mcp/tree/c6a72ab643ed3b8d862325e3012b47e62792ce6f) | Schematic API, native pcbnew subprocess bridge, placement, FreeRouter integration, KiCad checks | Beta; upstream primarily uses macOS. File edits do not merge unsaved GUI changes. Whole-board pipeline/auto-fix can change placement or replace routing. | Selected, pinned, with independent read-back and checks. |

Sources supporting the implementation distinctions:

- [mash command surface](https://github.com/mash/kicad-skills/blob/a74dbcb96d0fcd98aa597061ef89e4f1b1aec7b4/README.md)
  and [dependency pin](https://github.com/mash/kicad-skills/blob/a74dbcb96d0fcd98aa597061ef89e4f1b1aec7b4/pyproject.toml).
- [KiSkill routing bridge](https://github.com/AvatarSD/KiSkill/blob/b27ce9e0f7bee10ef6dd606baabcbaf0c3c1eecc/kicad_lib/layout.py).
- [Agentic MCP platform limitations](https://github.com/nevenfo/kicad-agentic-mcp/blob/fc568cf188911e5a91ede54798003fe074b19404/README.md#known-limitations)
  and [live benchmark](https://github.com/nevenfo/kicad-agentic-mcp/blob/fc568cf188911e5a91ede54798003fe074b19404/docs/benchmark-pcb-live-v2.md).
  That benchmark documents discovered false-success bugs **and subsequent
  fixes**; do not cite its baseline failures as unfixed current defects, or
  generalise its small Windows fixtures to arbitrary boards.
- [blwfish operating guide](https://github.com/blwfish/kicad-mcp/blob/c6a72ab643ed3b8d862325e3012b47e62792ce6f/AGENT-INSTRUCTIONS.md),
  [Linux configuration](https://github.com/blwfish/kicad-mcp/blob/c6a72ab643ed3b8d862325e3012b47e62792ce6f/src/kicad_mcp/config.py),
  [routing operations](https://github.com/blwfish/kicad-mcp/blob/c6a72ab643ed3b8d862325e3012b47e62792ce6f/src/kicad_mcp/tools/pcb_autoroute.py).

KiSkill and blwfish declare MIT licences; Agentic MCP declares AGPL-3.0.
No root licence was found in the reviewed mash tree; clarify licensing before
redistributing its code. We are installing tools, not incorporating them into
the board design. This review does not make legal conclusions about derivatives.

## Local setup

The launcher is Linux-specific. Native `kicad-cli` and `/usr/bin/python3` with
`pcbnew` must be installed, plus KiCad symbol/footprint libraries, `uv`, Git and
Java. This machine has KiCad/pcbnew **10.0.7**, Python **3.13.15** for the MCP
venv, and Java **26.0.2.1**. Python for the server and native pcbnew need not be
the same interpreter.

From the workspace:

```sh
source scripts/env.sh
repos/fujinet-nio-hardware/tools/kicad/setup
repos/fujinet-nio-hardware/.local-tools/kicad/venv/bin/python \
  repos/fujinet-nio-hardware/tools/kicad/smoke.py
```

`setup` installs into ignored `.local-tools/kicad/`, using the exact server
commit and dependency versions in `requirements.lock`. It also installs
FreeRouter **2.2.3**, the selected MCP's validated version, checking the
download SHA256 recorded in the script. That hash was measured from the GitHub
release download during this review; it is not a separate publisher signature.
Do not silently upgrade. The existing passive breakout used **2.4.1**: leave
its recorded routing artifacts and reproduction process unchanged.

The Python snapshot is version-pinned, not a cross-platform or hash-locked
software supply-chain guarantee. A tool update gets a fresh dependency snapshot
and one smoke check; it does not trigger a hardware qualification campaign.

### MCP connection

Use the absolute path to `tools/kicad/launch` as a stdio server command. The
server was registered on this machine as `fujinet_kicad` using:

```sh
codex mcp add fujinet_kicad -- \
  /home/markf/dev/nio/fujinet-nio-workspace/repos/fujinet-nio-hardware/tools/kicad/launch
```

This is user-level Codex registration. To undo it, use
`codex mcp remove fujinet_kicad`; the tool installation remains local to this
checkout. For project-only registration, remove that entry and use the example
below instead. Do not register two writers for the same project.

The launcher sets the hardware repository search root and strict path checking.
Upstream strict mode also permits temporary paths and the user's KiCad
directory; not every operation (notably schematic save) uses that guard. It is
an accident-prevention measure, **not an OS sandbox**. Keep a single trusted
local client and no network listener.

Example project-local Codex configuration (substitute your checkout path):

```toml
[mcp_servers.fujinet_kicad]
command = "/absolute/workspace/repos/fujinet-nio-hardware/tools/kicad/launch"
startup_timeout_sec = 30
tool_timeout_sec = 180
```

Codex supports this in a trusted project's `.codex/config.toml`; see
[official MCP configuration](https://learn.chatgpt.com/docs/extend/mcp).
Start a new client session after configuration and check for the server's tools.
Do not infer active tool availability just because a config file exists.
Call `get_usage_guidance` once; query operation schemas rather than copying
stale examples. The reviewed server exposes **18** domain/standalone tools
(some repository metadata still advertises an older count).

No third-party skill bundles are required for this setup. The local
`AGENTS.md` supplies the project-specific operating rules. Do not import an
upstream instruction to use another model, start subagents or run automatic
self-improvement as a requirement of this project.

## Engineering requirements drive the tools

For the first active Amiga board, maintain a short table in the design's own
directory: `ID | requirement | implementation | verification | open decision`.
The electrical source of truth remains
[the board contract](../../amiga/docs/eventual-board-considerations.md).
The initial requirements cover:

- Three USB modes and transitions, with independent physical recovery access.
- Power source/current budget, VBUS/CC treatment and unpowered-board isolation.
- Complete RP allocation: no double allocation of Zorro, control and debug pins.
- Local servicing of Zorro cycles; asynchronous USB completion through mailbox
  state rather than waiting for ESP inside a bus cycle.
- Connector geometry, mechanical envelope, ESP antenna keepout, debug/service
  access, fabrication limits and a chosen stackup.

Do not use a firmware-to-schematic template to infer our Zorro pin allocation.
The selected server's firmware frontend has a narrow supported component set;
our RP/Zorro design needs an explicit reviewed signal table.

The execution loop is deliberately short:

1. **Define:** settle circuit choices using actual datasheets and the existing
   evidence; encode pin/net tables and mechanical/routing constraints.
2. **Execute:** query real library parts, construct the schematic through tools,
   export connectivity, then apply constrained placement and ordinary routing.
   Use candidate copies; save a baseline before each meaningful batch.
3. **Validate:** compare exported pin-to-net membership with the requirements,
   run independent KiCad ERC and DRC with schematic parity, inspect renders and
   confirm the critical physical/electrical constraints. Accept or fix only the
   affected batch.

The agent still owns engineering choices. A router cannot choose safe USB
host isolation, prove power-off bus behaviour, infer suitable level translation,
or establish a manufacturable impedance geometry from unspecified stackup.
USB differential-pair geometry, return paths and Zorro timing are **not proven
by ordinary autorouter completion**. No coupled-pair routing capability was
qualified in this review. Establish the critical-net route using an appropriate
KiCad routing capability or a small reviewed layout operation, then verify
whether the ordinary router preserves it before using it on that candidate.
Do not solve a tool gap with a long sequence of agent-guessed trace coordinates.

Do not run automatic board resizing, generic placement repair or global reroute
on a mechanically constrained board without checking the operation's effect.
The full pipeline is suited to scratch candidates, not incremental maintenance
of our released edge connector. Close the target GUI editor during file-based
mutations; never alternate unsaved GUI state and disk edits.

## Verification boundary

`smoke.py` uses a fresh temporary two-resistor fixture. It checks MCP discovery,
library lookup, schematic creation/connection/export, PCB placement/movement,
one routed net and independent KiCad read-back. It invokes real KiCad ERC/DRC;
the deliberately incomplete schematic has findings, so this is a **tool check**,
not acceptance of a functional circuit. Evidence is written to the printed
temporary directory. No existing CAD is changed.
The first completed run is recorded in [VERIFICATION.md](VERIFICATION.md).

For real designs, run `kicad-cli sch erc` and `kicad-cli pcb drc
--schematic-parity` on the saved candidate, retain the reports, and investigate
all new findings. Compare actual pin/net mappings, not just error totals. For
the passive breakout, its existing `scripts/check.py` remains authoritative.

No broad hardware retest is part of setup. The next design work is the shared
USB/power circuit and complete Zorro pin budget. Only a specific unresolved
electrical issue or changed circuit earns another physical experiment.

### KiCad 10 symbol compatibility and R1 findings

The A500 R1 build found a native-load failure that the original two-resistor
smoke could not reveal. KiCad 10 library symbols can contain
`property private` metadata; kicad-sch-api 0.5.6's formatter treated the keyword
as the property name and emitted the actual value without quotes. RP2350B and
Crystal_GND24 then produced schematics native KiCad could not load.

`setup` now applies the narrow, hash-guarded
[formatter compatibility patch](patches/kicad10-private-properties.patch)
through [apply-compat.py](apply-compat.py). Dependency versions remain pinned.
The patch corrects tool serialization of existing library metadata; it does
not patch or generate CAD files directly. Round-trip tests of both real symbol
definitions and native export of the full R1 hierarchy pass. Restart any
previously running MCP process before writing these symbols; R1's batch
constructor starts a fresh process through the configured repository launcher.

Other observed limitations, handled without changing the released design:

- `bulk_update_components` requires `reference_pattern`, not `reference`, in
  its criteria. An unrecognized key was silently ignored and selected all
  components. R1 uses anchored patterns and asserts exactly one update.
- `add_global_label` in the public schematic API does not serialize a global
  label in this pinned version. R1 uses MCP-supported hierarchical ports and
  independently checks their whole-net membership instead.
- A left sheet pin's distance is measured from the **bottom-left** corner.
  The top-left assumption disconnects the root wires. R1 accounts for this.
- Hierarchical-label shapes serialize as input in this API path; the R1 ports
  are used for connectivity, not as authoritative electrical direction models.
  Component pin types and the engineering signal table define direction.
- `add_wire_between_pins` can route through another pin. Native whole-net
  membership checks caught a temporary supply/ground short while adding local
  capacitor wiring. The candidate was corrected before acceptance. Inspect
  the route and re-export nets after such edits; tool success is insufficient.
- MCP still lacks page metadata and no-connect operations. R1 uses the public
  API for only those finishing operations, after the construction process exits.

See [R1 verification](../../amiga/integrated-a500-r1/review/verification.md).
