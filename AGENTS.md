# Hardware design agents

Read [the tooling decision and operating guide](tools/kicad/README.md) before
editing CAD. It records the selected MCP, setup, verification and limitations.
For Amiga work, the electrical contract is
[eventual-board-considerations.md](amiga/docs/eventual-board-considerations.md);
workspace `backlog/amiga-zorro-usb-bringup.md` owns progress and scope.

- Work from a short engineering requirements table: requirement, chosen
  implementation, evidence/check, unresolved decision. No new BMad hierarchy.
- Use the pinned KiCad MCP for supported CAD operations; use KiCad itself for
  independent netlist, ERC/DRC, rendering and read-back. Do not hand-generate or
  patch KiCad S-expressions. If an operation is unsupported, identify that
  specific gap and use a supported KiCad API or interactive editor operation.
- The agent owns circuit reasoning and validation. Tools own CAD serialization,
  placement calculations and ordinary routing. Tool success is not electrical
  correctness; ERC/DRC are necessary but cannot validate an unspecified design.
- One writer per project, including schematic state and GUI editors. Work on a
  candidate copy, preserve a baseline, and review semantic/netlist differences
  plus rendered output before accepting changes. Do not run whole-board
  generation, autoroute or auto-fix against the released passive breakout.
- Search libraries; check package and pin numbering against manufacturer
  documentation. Preserve reviewed connector geometry and custom libraries.
  A CAD library match alone does not establish the right physical part.
- Encode mechanical constraints, antenna keepout, power/ground paths and
  critical USB/bus routing requirements before placement/routing. Do not let
  generic auto-fix move fixed connectors or erase critical pre-routed copper.
- Independently run KiCad ERC and PCB DRC with schematic parity on the saved
  candidate. Report unresolved warnings and unchecked conditions; never hide
  them with exclusions to obtain a green report. Review renders as well.
- Run the cheapest check affected by a change. Repeat physical testing only
  for a changed circuit, unresolved electrical decision or observed failure.
  Existing USB/flash feasibility evidence permits design work now.
- Keep fabrication export separate from ordering. Do not upload designs to
  vendors, order boards, install unrelated skills, auto-update dependencies or
  publish repository changes as a side effect of tool setup.
