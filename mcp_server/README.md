# MCP Server

This folder is the public-safe MCP server example.

The important file is:

```text
mcp_server/sdwan_tools_example.py
```

It creates a real FastMCP server object:

```python
mcp = FastMCP("sdwan-netops-public-example")
```

and registers tools with decorators:

```python
@mcp.tool()
def get_devices() -> dict:
    return list_devices()
```

## Tools

| Tool | Purpose | Mode |
| --- | --- | --- |
| `get_devices` | List sample SD-WAN inventory | read-only |
| `create_and_onboard_edge` | Build a branch onboarding plan | dry-run by default |
| `diagnose_edge` | Return health and postcheck data | read-only |
| `get_server_info` | Explain the tool catalog | read-only |

## Run The MCP Server

```powershell
python mcp_server\sdwan_tools_example.py
```

That process speaks MCP over stdio. An MCP-capable client can launch it and call
the tools.

## Example MCP Client Config

See [mcp_config.example.json](mcp_config.example.json). Replace the path with
your local clone path.

```json
{
  "mcpServers": {
    "sdwan-netops-public-example": {
      "command": "python",
      "args": [
        "C:/path/to/ai-sdwan-mcp-poc/mcp_server/sdwan_tools_example.py"
      ]
    }
  }
}
```

## What The Private Version Adds

The private lab uses the same MCP pattern, but the tool body calls real
automation code:

```text
LLM -> MCP tool -> FastAPI/tool layer -> SD-WAN Manager + CML APIs
```

The public version keeps sample data so the repo is safe to share.

