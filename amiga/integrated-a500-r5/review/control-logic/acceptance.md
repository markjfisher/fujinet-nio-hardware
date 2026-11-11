# Control-logic placement acceptance

The user approved this candidate and its transfer to authoritative R5. The
root PCB now matches the complete approved control-logic candidate semantically:
35 footprint placements/references, the reviewed group memberships and two
reviewed standalone title/warning edits. All prior approved geometry is retained.

Footprint edits and text transfer used kicad-mcp. Reviewed groups were copied
with native KiCad because MCP has no group-edit operation; the gap was disclosed
before that fallback. Group identities, members and locks were preserved.

Transfer validation: native DRC unchanged (204 baseline findings, 499 unrouted
connections), zero schematic parity issues. The independent semantic equality
check and evidence live in `../service/verify.py`, `../service/verification.json`
and `../service/transfer-drc.json`.
