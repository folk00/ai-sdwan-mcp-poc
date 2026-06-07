from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network
from typing import Any


@dataclass(frozen=True)
class Device:
    host_name: str
    system_ip: str
    site_id: int
    public_wan_ip: str
    biz_wan_ip: str
    reachability: str = "reachable"
    validity: str = "valid"
    control_connections_up: int = 3
    bfd_up: int = 10
    bfd_total: int = 12
    config_group_status: str = "In Sync"
    blocking_alarms: int = 0


LAB_DEVICES: list[Device] = [
    Device("Edge1", "10.0.0.1", 501, "172.16.1.1", "172.16.2.1"),
    Device("Edge2", "10.0.0.2", 502, "172.16.1.2", "172.16.2.2"),
    Device("Edge3", "10.0.0.3", 503, "172.16.1.3", "172.16.2.3"),
]


def list_devices() -> dict[str, Any]:
    return {"devices": [_device_to_dict(device) for device in LAB_DEVICES]}


def create_edge_plan(edge_label: str) -> dict[str, Any]:
    """Build a deterministic, public-safe branch onboarding plan.

    The private version replaces this sample inventory with live reads from
    SD-WAN Manager and CML. The shape is intentionally similar: collect used
    values, choose safe targets, describe planned actions, then postcheck.
    """
    target = {
        "edge_label": edge_label,
        "hostname": _safe_hostname(edge_label),
        "site_id": _next_site_id(),
        "system_ip": _next_free_ip("10.0.0.0/24", {d.system_ip for d in LAB_DEVICES}),
        "public_wan_ip": _next_free_ip("172.16.1.0/24", {d.public_wan_ip for d in LAB_DEVICES}),
        "biz_wan_ip": _next_free_ip("172.16.2.0/24", {d.biz_wan_ip for d in LAB_DEVICES}),
        "config_group": "edge_basic",
    }
    return {
        "target": target,
        "reserved_values": {
            "system_ips": sorted(d.system_ip for d in LAB_DEVICES),
            "public_wan_ips": sorted(d.public_wan_ip for d in LAB_DEVICES),
            "biz_wan_ips": sorted(d.biz_wan_ip for d in LAB_DEVICES),
        },
        "planned_steps": [
            "validate current SD-WAN and CML inventory",
            "reserve non-overlapping system and transport IPs",
            "create or reuse the CML C8000V node",
            "attach INET and MPLS transport links",
            "prepare SD-WAN onboarding identity",
            "apply day0/bootstrap data",
            "attach edge_basic config group",
            "poll deployment task status",
            "run reachability, control, BFD, alarm, and config sync postchecks",
        ],
    }


def create_and_onboard_edge(edge_label: str, *, approve: bool, dry_run: bool) -> dict[str, Any]:
    plan = create_edge_plan(edge_label)
    if dry_run:
        return {
            "status": "dry_run",
            "applies_changes": False,
            "plan": plan,
            "next_action": "rerun with dry_run=false and approve=true to mutate the private lab",
        }
    if not approve:
        return {
            "status": "blocked",
            "applies_changes": False,
            "reason": "approve=true is required for mutation",
            "plan": plan,
        }
    return {
        "status": "accepted_public_example",
        "applies_changes": False,
        "plan": plan,
        "postchecks": run_postchecks(plan["target"]),
        "note": "The public repo never mutates a real SD-WAN or CML lab.",
    }


def diagnose_edge(identifier: str) -> dict[str, Any]:
    device = _find_device(identifier)
    if device is None:
        return {
            "identifier": identifier,
            "status": "not_found",
            "hint": "Use Edge1, Edge2, Edge3, or one of their sample system IPs.",
        }
    return {
        "identifier": identifier,
        "resolved_device": _device_to_dict(device),
        "postchecks": run_postchecks(_device_to_dict(device)),
        "operator_summary": (
            f"{device.host_name} is reachable, has {device.control_connections_up} "
            f"control connections up, BFD is {device.bfd_up}/{device.bfd_total}, "
            f"and config group status is {device.config_group_status}."
        ),
    }


def run_postchecks(target: dict[str, Any]) -> dict[str, Any]:
    total = int(target.get("bfd_total") or target.get("bfdSessionsTotal") or 12)
    up = int(target.get("bfd_up") or target.get("bfdSessionsUp") or 10)
    blocking_alarms = int(target.get("blocking_alarms") or 0)
    checks = [
        {
            "name": "reachability",
            "passed": target.get("reachability", "reachable") == "reachable",
            "detail": "device is reachable in SD-WAN inventory",
        },
        {
            "name": "control_connections",
            "passed": int(target.get("control_connections_up") or 3) >= 2,
            "detail": f"{target.get('control_connections_up', 3)} control connections up",
        },
        {
            "name": "bfd",
            "passed": up > 0,
            "detail": f"{up}/{total} BFD sessions up",
            "warning": "some BFD sessions are down" if up < total else None,
        },
        {
            "name": "config_group",
            "passed": target.get("config_group_status", "In Sync") == "In Sync",
            "detail": target.get("config_group_status", "In Sync"),
        },
        {
            "name": "alarms",
            "passed": blocking_alarms == 0,
            "detail": f"{blocking_alarms} blocking alarms",
        },
    ]
    failed = [check for check in checks if not check["passed"]]
    warnings = [check for check in checks if check.get("warning")]
    return {
        "status": "fail" if failed else "pass_with_warnings" if warnings else "pass",
        "failed_count": len(failed),
        "warning_count": len(warnings),
        "checks": checks,
    }


def _find_device(identifier: str) -> Device | None:
    needle = identifier.strip().lower()
    for device in LAB_DEVICES:
        if needle in {device.host_name.lower(), device.system_ip.lower()}:
            return device
    return None


def _next_site_id() -> int:
    return max(device.site_id for device in LAB_DEVICES) + 1


def _next_free_ip(cidr: str, used: set[str]) -> str:
    network = IPv4Network(cidr)
    reserved = {IPv4Address(ip) for ip in used}
    reserved.add(network.network_address)
    reserved.add(network.broadcast_address)
    for host in network.hosts():
        if host not in reserved and int(str(host).split(".")[-1]) != 254:
            return str(host)
    raise RuntimeError(f"no free address in {cidr}")


def _safe_hostname(edge_label: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in edge_label)
    return cleaned.strip("-_") or "AutomationSite"


def _device_to_dict(device: Device) -> dict[str, Any]:
    return {
        "host_name": device.host_name,
        "system_ip": device.system_ip,
        "site_id": device.site_id,
        "public_wan_ip": device.public_wan_ip,
        "biz_wan_ip": device.biz_wan_ip,
        "reachability": device.reachability,
        "validity": device.validity,
        "control_connections_up": device.control_connections_up,
        "bfd_up": device.bfd_up,
        "bfd_total": device.bfd_total,
        "config_group_status": device.config_group_status,
        "blocking_alarms": device.blocking_alarms,
    }
