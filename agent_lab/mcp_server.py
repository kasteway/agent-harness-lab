"""Optional MCP adapter exposing the same vetted tools to external MCP clients."""

from .tools import compare_sla, find_driver, retrieve_notes


def main():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install -e '.[mcp]'") from exc

    server = FastMCP("Agent Harness Lab")
    server.tool()(compare_sla)
    server.tool()(find_driver)
    server.tool()(retrieve_notes)
    # An MCP server is an interface; the CLI's in-process agent loop does not
    # secretly call this server. Connect an MCP client to exercise it.
    server.run()


if __name__ == "__main__":
    main()
