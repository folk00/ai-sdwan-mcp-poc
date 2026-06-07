from __future__ import annotations

from typing import Any


TOOL_CATALOG: list[dict[str, Any]] = [
    {
        "name": "get_devices",
        "summary": "List SD-WAN inventory from the sample automation engine.",
        "safe_mode": "read_only",
        "example_arguments": {},
    },
    {
        "name": "create_and_onboard_edge",
        "summary": "Create a dry-run branch edge plan and show the private onboarding workflow shape.",
        "safe_mode": "dry_run_by_default",
        "example_arguments": {
            "edge_label": "DEMO_AutomationSite",
            "dry_run": True,
            "approve": False,
        },
    },
    {
        "name": "diagnose_edge",
        "summary": "Resolve a device and return reachability, control, BFD, config sync, and alarm checks.",
        "safe_mode": "read_only",
        "example_arguments": {"identifier": "Edge1"},
    },
    {
        "name": "get_server_info",
        "summary": "Describe what the MCP server exposes and how the LLM should use it.",
        "safe_mode": "read_only",
        "example_arguments": {},
    },
]
