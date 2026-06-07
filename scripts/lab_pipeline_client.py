from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_ONBOARD_ENDPOINT = "/api/sdwan/onboarding/by-label"
DEFAULT_HEALTH_ENDPOINT = "/api/health"
DEFAULT_POSTCHECK_ENDPOINT = "/api/sdwan/onboarding/postchecks"
DEFAULT_DRY_RUN_ENDPOINT = "/api/cml/automation-edges/create"


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def _base_url() -> str:
    return _env("LAB_API_BASE_URL").rstrip("/")


def _endpoint(name: str, default: str) -> str:
    value = os.getenv(name, default)
    if not value.startswith("/"):
        value = "/" + value
    return value


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    api_key = os.getenv("LAB_API_KEY")
    if api_key:
        headers[os.getenv("LAB_API_KEY_HEADER", "x-api-key")] = api_key
    bearer = os.getenv("LAB_BEARER_TOKEN")
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    return headers


def _request(method: str, endpoint: str, payload: dict[str, Any] | None = None) -> Any:
    url = _base_url() + endpoint
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method, headers=_headers())
    timeout = int(os.getenv("LAB_API_TIMEOUT", "120"))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(
            json.dumps(
                {
                    "error": "lab_api_http_error",
                    "status": exc.code,
                    "endpoint": endpoint,
                    "body": body,
                },
                indent=2,
            )
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(
            json.dumps(
                {
                    "error": "lab_api_connection_error",
                    "endpoint": endpoint,
                    "reason": str(exc.reason),
                    "hint": "Use a stable public tunnel or a self-hosted GitLab Runner inside the lab/VPN.",
                },
                indent=2,
            )
        ) from exc


def _find_first(data: Any, keys: set[str]) -> Any:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in keys and value not in (None, ""):
                return value
        for value in data.values():
            found = _find_first(value, keys)
            if found not in (None, ""):
                return found
    elif isinstance(data, list):
        for item in data:
            found = _find_first(item, keys)
            if found not in (None, ""):
                return found
    return None


def _write_artifact(path: str, data: Any) -> None:
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _print_summary(label: str, data: Any) -> None:
    print(f"\n== {label} ==")
    print(json.dumps(data, indent=2, sort_keys=True))


def health(args: argparse.Namespace) -> None:
    result = _request("GET", _endpoint("LAB_HEALTH_ENDPOINT", DEFAULT_HEALTH_ENDPOINT))
    _write_artifact(args.output, result)
    _print_summary("health", result)


def dry_run(args: argparse.Namespace) -> None:
    dry_run_approve = os.getenv("LAB_DRY_RUN_APPROVE", "").lower() == "true"
    endpoint = _endpoint("LAB_DRY_RUN_ENDPOINT", DEFAULT_DRY_RUN_ENDPOINT)
    payload: dict[str, Any] = {"edge_label": args.edge_label, "dry_run": True}
    if "automation-edges/create" in endpoint:
        payload.update(
            {
                "approve_create": False,
                "with_links": True,
                "include_bootstrap": True,
                "bootstrap_source_device": os.getenv("LAB_SOURCE_DEVICE", "Edge1"),
            }
        )
    else:
        payload["approve"] = dry_run_approve
    result = _request("POST", endpoint, payload)
    _write_artifact(args.output, result)
    _print_summary("dry_run", result)


def apply(args: argparse.Namespace) -> None:
    if os.getenv("LAB_MUTATION_APPROVED", "").lower() != "true":
        raise SystemExit("LAB_MUTATION_APPROVED=true is required for apply.")
    payload = {
        "edge_label": args.edge_label,
        "approve": True,
        "dry_run": False,
    }
    result = _request("POST", _endpoint("LAB_ONBOARD_ENDPOINT", DEFAULT_ONBOARD_ENDPOINT), payload)
    _write_artifact(args.output, result)
    _print_summary("apply", result)


def postcheck(args: argparse.Namespace) -> None:
    payload: dict[str, Any] = {}
    if args.system_ip:
        payload["system_ip"] = args.system_ip
    if args.edge_label:
        payload["edge_label"] = args.edge_label
    if args.cml_node_id:
        payload["cml_node_id"] = args.cml_node_id

    if args.from_apply and Path(args.from_apply).exists():
        apply_result = json.loads(Path(args.from_apply).read_text(encoding="utf-8"))
        payload.setdefault("system_ip", _find_first(apply_result, {"system_ip", "target_system_ip"}))
        payload.setdefault("cml_node_id", _find_first(apply_result, {"cml_node_id", "node_id"}))
        payload.setdefault("edge_label", _find_first(apply_result, {"edge_label", "label", "hostname"}))

    payload = {key: value for key, value in payload.items() if value not in (None, "")}
    if not payload:
        raise SystemExit("Postcheck needs LAB_SYSTEM_IP, LAB_EDGE_LABEL, LAB_CML_NODE_ID, or --from-apply.")

    result = _request("POST", _endpoint("LAB_POSTCHECK_ENDPOINT", DEFAULT_POSTCHECK_ENDPOINT), payload)
    _write_artifact(args.output, result)
    _print_summary("postcheck", result)


def wait_postcheck(args: argparse.Namespace) -> None:
    attempts = int(os.getenv("LAB_POSTCHECK_ATTEMPTS", "10"))
    sleep_seconds = int(os.getenv("LAB_POSTCHECK_SLEEP_SECONDS", "30"))
    last_result: Any = None
    for attempt in range(1, attempts + 1):
        print(f"Postcheck attempt {attempt}/{attempts}")
        try:
            postcheck(args)
            last_result = json.loads(Path(args.output).read_text(encoding="utf-8"))
            if _looks_healthy(last_result):
                return
        except SystemExit as exc:
            if attempt == attempts:
                raise
            print(str(exc))
        time.sleep(sleep_seconds)
    raise SystemExit(json.dumps({"error": "postcheck_not_healthy", "last_result": last_result}, indent=2))


def _looks_healthy(result: Any) -> bool:
    text = json.dumps(result).lower()
    if '"status": "success"' in text or '"status": "ok"' in text or '"status": "pass"' in text:
        return True
    if '"reachable"' in text and '"down": 0' in text:
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Call a private lab automation API from CI/CD.")
    subparsers = parser.add_subparsers(required=True)

    health_parser = subparsers.add_parser("health")
    health_parser.add_argument("--output", default="lab-health.json")
    health_parser.set_defaults(func=health)

    dry_parser = subparsers.add_parser("dry-run")
    dry_parser.add_argument("--edge-label", default=os.getenv("LAB_EDGE_LABEL", "GitLab_AutomationSite"))
    dry_parser.add_argument("--output", default="lab-dry-run.json")
    dry_parser.set_defaults(func=dry_run)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--edge-label", default=os.getenv("LAB_EDGE_LABEL", "GitLab_AutomationSite"))
    apply_parser.add_argument("--output", default="lab-apply-result.json")
    apply_parser.set_defaults(func=apply)

    post_parser = subparsers.add_parser("postcheck")
    post_parser.add_argument("--edge-label", default=os.getenv("LAB_EDGE_LABEL"))
    post_parser.add_argument("--system-ip", default=os.getenv("LAB_SYSTEM_IP"))
    post_parser.add_argument("--cml-node-id", default=os.getenv("LAB_CML_NODE_ID"))
    post_parser.add_argument("--from-apply", default="lab-apply-result.json")
    post_parser.add_argument("--output", default="lab-postcheck.json")
    post_parser.set_defaults(func=postcheck)

    wait_parser = subparsers.add_parser("wait-postcheck")
    wait_parser.add_argument("--edge-label", default=os.getenv("LAB_EDGE_LABEL"))
    wait_parser.add_argument("--system-ip", default=os.getenv("LAB_SYSTEM_IP"))
    wait_parser.add_argument("--cml-node-id", default=os.getenv("LAB_CML_NODE_ID"))
    wait_parser.add_argument("--from-apply", default="lab-apply-result.json")
    wait_parser.add_argument("--output", default="lab-postcheck.json")
    wait_parser.set_defaults(func=wait_postcheck)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
