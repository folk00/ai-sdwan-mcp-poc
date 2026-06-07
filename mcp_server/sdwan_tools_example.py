from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("sdwan-netops-public-example")


@mcp.tool()
def get_devices() -> dict[str, Any]:
    """Return a public-safe sample of SD-WAN inventory."""
    return {
        "devices": [
            {"host_name": "Edge1", "system_ip": "10.0.0.1", "status": "normal"},
            {"host_name": "Edge2", "system_ip": "10.0.0.2", "status": "normal"},
        ]
    }


@mcp.tool()
def create_and_onboard_edge(edge_label: str, approve: bool = False) -> dict[str, Any]:
    """Show the shape of the private CML + SD-WAN onboarding tool."""
    if not approve:
        return {
            "status": "blocked",
            "reason": "approve=true is required for mutation",
        }

    return {
        "status": "accepted",
        "edge_label": edge_label,
        "steps": [
            "create CML edge",
            "patch bootstrap",
            "attach config group",
            "run postchecks",
        ],
    }


if __name__ == "__main__":
    mcp.run()

