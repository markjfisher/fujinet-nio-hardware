# Host-protection placement acceptance

User approved this candidate and its transfer to authoritative R5. The root PCB
now matches the complete approved host-protection candidate semantically,
including all 42 component positions/references and nine groups. Existing
approved clusters, nets, identities, locks and mechanical geometry are preserved.

Preserve internal supervisor, supply and output-disable geometry and proposed
local ground-via sites. Their overall group positions may be reconsidered for
routing or remaining placement; this acceptance does not make their absolute
positions mechanical constraints. No outline change is authorised.

Transfer checked with native KiCad DRC/parity: unchanged baseline findings,
499 unconnected items, zero parity issues. Evidence is recorded in
`../control-logic/transfer-drc.json` and `../control-logic/verification.json`.
