"""One bounded MCP integration check. Writes only to a fresh temporary directory.

This tests tool plumbing, not a usable circuit or autorouter qualification.
Run with the installed tool venv Python after sourcing workspace scripts/env.sh.
"""
import asyncio
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main():
    launcher = Path(__file__).resolve().with_name("launch")
    scratch = Path(tempfile.mkdtemp(prefix="fujinet-kicad-smoke-"))
    schematic = scratch / "smoke.kicad_sch"
    board = scratch / "smoke.kicad_pcb"
    calls = []
    async with Client(StdioTransport(command=str(launcher), args=[]), timeout=60) as client:
        tools = await client.list_tools()
        assert {"schematic", "pcb", "library", "autoroute"} <= {t.name for t in tools}

        async def call(tool_name, **args):
            result = await client.call_tool(tool_name, args)
            data = result.data
            if not isinstance(data, dict):
                data = json.loads(result.content[0].text)
            if data.get("error") or data.get("status") == "error":
                raise RuntimeError(f"{tool_name}: {data}")
            calls.append({"tool": tool_name, "args": args, "result": data})
            return data

        await client.call_tool("get_usage_guidance", {})
        symbols = await call("library", operation="search", query="R", type="symbol", library="Device", limit=5)
        footprints = await call("library", operation="search", query="R_0603_1608Metric", type="footprint", limit=5)
        assert "Device" in json.dumps(symbols)
        assert "R_0603_1608Metric" in json.dumps(footprints)
        await call("schematic", operation="create", name="smoke")
        await call("schematic", operation="add_component", lib_id="Device:R", reference="R1",
                   value="10k", position=[50.8, 50.8], footprint="Resistor_SMD:R_0603_1608Metric")
        await call("schematic", operation="add_component", lib_id="Device:R", reference="R2",
                   value="10k", position=[76.2, 50.8], footprint="Resistor_SMD:R_0603_1608Metric")
        await call("schematic", operation="connect_pins_with_labels", comp1_ref="R1", pin1="2",
                   comp2_ref="R2", pin2="1", net_name="SMOKE")
        await call("schematic", operation="save", schematic_path=str(schematic))
        await call("pcb", operation="create", pcb_path=str(board))
        await call("pcb", operation="set_outline", pcb_path=str(board), x_mm=40, y_mm=40,
                   width_mm=30, height_mm=20)
        await call("pcb", operation="place_footprint", pcb_path=str(board),
                   library="Resistor_SMD", footprint_name="R_0603_1608Metric", reference="R1",
                   value="10k", x_mm=50, y_mm=50)
        await call("pcb", operation="move_footprint", pcb_path=str(board), reference="R1",
                   x_mm=55, y_mm=50)
        await call("pcb", operation="place_footprint", pcb_path=str(board),
                   library="Resistor_SMD", footprint_name="R_0603_1608Metric", reference="R2",
                   value="10k", x_mm=62, y_mm=50)
        await call("pcb", operation="add_net", pcb_path=str(board), net_name="/SMOKE")
        await call("pcb", operation="bulk_assign_pad_nets", pcb_path=str(board), assignments=[
            {"reference": "R1", "pad": "2", "net": "/SMOKE"},
            {"reference": "R2", "pad": "1", "net": "/SMOKE"}])
        routed = await call("autoroute", operation="run", pcb_path=str(board), passes=1)
        assert routed.get("unconnected_after_routing") == 0, routed
        await call("pcb", operation="list_footprints", pcb_path=str(board))

    # Independent KiCad read-back, not the MCP's own account of its write.
    netlist = scratch / "smoke.net"
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadxml",
                    "-o", str(netlist), str(schematic)], check=True, capture_output=True, text=True)
    comp = ET.parse(netlist).find("./components/comp[@ref='R1']")
    assert comp is not None and comp.findtext("value") == "10k"
    net = ET.parse(netlist).find("./nets/net[@name='/SMOKE']")
    assert net is not None
    assert {(n.get("ref"), n.get("pin")) for n in net.findall("node")} == {("R1", "2"), ("R2", "1")}
    readback = subprocess.run(["/usr/bin/python3", "-c", """
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1])
assert b is not None
r = b.FindFootprintByReference('R1')
assert r and r.GetValue() == '10k'
assert abs(pcbnew.ToMM(r.GetPosition().x)-55) < 0.001
assert abs(pcbnew.ToMM(r.GetPosition().y)-50) < 0.001
assert len(list(r.Pads())) == 2
assert len(list(b.GetTracks())) > 0
print('pcbnew read-back PASS')
""", str(board)], check=True, capture_output=True, text=True)
    reports = {}
    for domain, check, source in [("sch", "erc", schematic), ("pcb", "drc", board)]:
        output = scratch / f"{check}.json"
        subprocess.run(["kicad-cli", domain, check, "--format", "json", "-o", str(output),
                        str(source)], check=True, capture_output=True, text=True)
        reports[check] = json.loads(output.read_text())
    assert not reports["drc"].get("unconnected_items"), reports["drc"]
    # The intentionally incomplete resistor fixture has ERC findings. Do not
    # confuse a successful invocation of ERC/DRC with a passing circuit.
    evidence = {"result": "tool smoke PASS; circuit intentionally incomplete",
                "tool_count": len(tools), "calls": calls, "reports": reports,
                "pcb_readback": readback.stdout.strip()}
    (scratch / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"PASS: MCP read/write and independent KiCad read-back; evidence: {scratch}")


if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(main(), timeout=180))
