from __future__ import annotations

import unittest

from backend.automation_engine import create_and_onboard_edge, diagnose_edge, list_devices
from mcp_server.tool_catalog import TOOL_CATALOG


class PublicFlowTests(unittest.TestCase):
    def test_inventory_has_sample_edges(self) -> None:
        devices = list_devices()["devices"]
        self.assertGreaterEqual(len(devices), 3)
        self.assertEqual(devices[0]["host_name"], "Edge1")

    def test_dry_run_generates_non_overlapping_targets(self) -> None:
        result = create_and_onboard_edge("DEMO_AutomationSite", approve=False, dry_run=True)
        self.assertEqual(result["status"], "dry_run")
        target = result["plan"]["target"]
        self.assertEqual(target["system_ip"], "10.0.0.4")
        self.assertEqual(target["public_wan_ip"], "172.16.1.4")
        self.assertEqual(target["biz_wan_ip"], "172.16.2.4")

    def test_mutation_requires_approval(self) -> None:
        result = create_and_onboard_edge("DEMO_AutomationSite", approve=False, dry_run=False)
        self.assertEqual(result["status"], "blocked")

    def test_diagnose_returns_operator_summary(self) -> None:
        result = diagnose_edge("Edge1")
        self.assertIn("operator_summary", result)
        self.assertEqual(result["postchecks"]["status"], "pass_with_warnings")

    def test_mcp_tool_catalog_exposes_core_tools(self) -> None:
        names = {tool["name"] for tool in TOOL_CATALOG}
        self.assertIn("get_devices", names)
        self.assertIn("create_and_onboard_edge", names)
        self.assertIn("diagnose_edge", names)


if __name__ == "__main__":
    unittest.main()
