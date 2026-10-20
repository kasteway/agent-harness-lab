"""Run the same calculation through direct HTTP and an MCP client/server."""

import asyncio
import json
import sys
import threading
import urllib.request

from .http_api import make_server
from .tools import ROOT


def call_direct_api(url):
    # The client knows the URL and request format in advance.
    request = urllib.request.Request(
        url + "/tools/compare_sla",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)


async def call_mcp():
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        raise RuntimeError("Install the optional MCP package with Python 3.10+: pip install -e '.[mcp]'") from exc

    # The MCP client launches our local server as a subprocess over stdio.
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "agent_lab.mcp_server"],
        cwd=str(ROOT),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            catalog = await session.list_tools()  # Discovery: no hard-coded tool schema here.
            names = [tool.name for tool in catalog.tools]
            if "compare_sla" not in names:
                raise RuntimeError("MCP server did not expose compare_sla")
            result = await session.call_tool("compare_sla", arguments={})
            if result.isError:
                raise RuntimeError("MCP server returned a tool error")
            if result.structuredContent is not None:
                value = result.structuredContent
                # FastMCP versions may wrap a non-dict return in {"result": ...}.
                if set(value) == {"result"}:
                    value = value["result"]
            else:
                value = json.loads(result.content[0].text)
            return names, value


def main():
    server = make_server()
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        direct = call_direct_api("http://127.0.0.1:" + str(server.server_port))
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)

    names, via_mcp = asyncio.run(call_mcp())
    print("DIRECT API: client knew POST /tools/compare_sla; result:")
    print(json.dumps(direct, indent=2))
    print("\nMCP: client discovered tools:", ", ".join(names))
    print("MCP: client called compare_sla; result:")
    print(json.dumps(via_mcp, indent=2))
    print("\nSame underlying calculation:", direct == via_mcp)
    if direct != via_mcp:
        raise SystemExit("The two interfaces returned different results")


if __name__ == "__main__":
    main()
