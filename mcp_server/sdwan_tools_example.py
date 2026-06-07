from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from backend.automation_engine import create_and_onboard_edge as run_create_edge
from backend.automation_engine import diagnose_edge as run_diagnose_edge
from backend.automation_engine import list_devices
from mcp_server.tool_catalog import TOOL_CATALOG


mcp = FastMCP("sdwan-netops-public-example")


@mcp.tool()
def get_devices() -> dict[str, Any]:
    """Return a public-safe sample of SD-WAN inventory."""
    return list_devices()


@mcp.tool()
def create_and_onboard_edge(
    edge_label: str,
    approve: bool = False,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Show the shape of the private CML + SD-WAN onboarding tool."""
    return run_create_edge(edge_label, approve=approve, dry_run=dry_run)


@mcp.tool()
def diagnose_edge(identifier: str) -> dict[str, Any]:
    """Resolve a sample edge and return an operator-style health report."""
    return run_diagnose_edge(identifier)


@mcp.tool()
def get_server_info() -> dict[str, Any]:
    """Explain the public example tool surface."""
    return {
        "server": "sdwan-netops-public-example",
        "llm_role": "selects tools and explains JSON results",
        "mcp_role": "typed tool bridge",
        "backend_role": "validates requests and owns deterministic automation logic",
        "tools": TOOL_CATALOG,
    }


if __name__ == "__main__":
    mcp.run()
