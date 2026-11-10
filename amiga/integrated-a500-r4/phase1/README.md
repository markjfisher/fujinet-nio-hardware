# R4 Phase 1 migration and verification

These are one-time, ordered migrations of the checkpointed R4 circuit, **not**
a source that regenerates the board. Native KiCad files remain authoritative
and may be edited normally. Do not rerun a completed migration on an edited
project. No old build, placement or routing generator was run.

`baseline-plan.json` is a historical input snapshot. `plan.py` describes the
five electrical substitutions; `stages.json` contains their complete pin
intent. `apply.py PROJECT STAGE` performs schematic operations through the
pinned MCP on a temporary candidate. `verify.py PROJECT STAGE` exports native
KiCad connectivity and ERC, checks every functional pin and cross-sheet net,
checks replacement gate/array maps, and exercises the guard truth table.
`sync.py PROJECT STAGE` adds replacement footprints with MCP and updates nets;
`sync_native.py` fills the MCP's missing removal, value/UUID-binding operations
and corrects canonical net names. It asserts that unaffected footprints retain
position, rotation, side, lock state and UUID. Added/repackaged components are
staged outside the board; they have not been placed for routing.

Native KiCad DRC with schematic parity runs after each sync. The baseline has
unrouted connections and existing warnings; these migrations do not produce
a fabrication release. Review the implementation report for current limits.

Run after `source scripts/env.sh`, using the pinned MCP venv Python for apply
and sync; use system Python with pcbnew for sync_native. Stages: protection,
I1, I2, R-A, R-B. Run only against the corresponding preceding checkpoint.
`make_symbols.py` uses kiutils 1.4.8 plus native `kicad-cli sym upgrade` because
the MCP has no symbol-library editor. Exact manufacturer pin maps are explicit
in that file. The 11A/04A symbols show whole physical packages, not extra GPIOs.

Observed tool gaps, handled without changing installed tools:

- The MCP library index ignores space-indented symbol definitions; native KiCad
  library serialization resolves this.
- Loaded-symbol pin queries omit some common-unit pins. Library API transforms
  supply coordinates; native whole-net comparison is the acceptance gate.
- MCP snaps positions. NC markers use actual placed positions through the public
  schematic API. That API also supplies missing sheet-pin deletion/page metadata.
- MCP net names and native DRC escape slashes differently. Functional names and
  unconnected pin names are restored separately and checked natively.
- A custom connector library must be visible to the writer; a failed temporary
  attempt was rejected when native read-back detected J40 missing.
