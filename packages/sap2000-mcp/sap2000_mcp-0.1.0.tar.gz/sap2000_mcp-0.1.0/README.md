# sap2000-mcp

First minimal MCP server for controlling SAP2000 from an AI agent (e.g. Cursor AI, Claude, GPT).

Status: early preview. MCP/tool UX is evolving and most general-purpose agents won’t yet perform complex SAP2000 tasks reliably. We’ll iterate quickly to make agent workflows far more effective.

We welcome ideas: open an issue with feature requests, missing tools, or workflow suggestions.

Install (PyPI):
```bash
pip install sap2000-mcp
```

Install (dev):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Use with Cursor (Settings → Features → MCP → Edit Config):
```json
{
  "mcpServers": {
    "sap2000-mcp": {
      "command": "/Users/you/path/to/engmcp/venv/bin/python",
      "args": ["-m", "sap2000_mcp"]
    }
  }
}
```

Notes:
- SAP2000 integration requires Windows (COM). On macOS, `sap2000_is_available` will be false.
- More tools and agent patterns coming soon. PRs and issues are appreciated.
