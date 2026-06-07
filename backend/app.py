from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="AI SD-WAN Automation PoC")


class EdgeRequest(BaseModel):
    edge_label: str
    approve: bool = False
    dry_run: bool = True


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "public_example",
        "mutations_enabled": False,
    }


@app.post("/api/sdwan/onboarding/by-label", operation_id="sdwanCreateAndOnboardEdge")
def create_and_onboard_edge(request: EdgeRequest) -> dict[str, object]:
    """Public-safe example of the private onboarding workflow shape."""
    if not request.dry_run and not request.approve:
        raise HTTPException(status_code=403, detail="approve=true is required")

    return {
        "mode": "dry_run" if request.dry_run else "approved_example",
        "edge_label": request.edge_label,
        "workflow": [
            "validate lab inventory",
            "generate non-overlapping IPAM values",
            "create or reuse CML edge",
            "attach transport links",
            "prepare SD-WAN onboarding",
            "attach config group",
            "run postchecks",
        ],
        "note": "This public example does not mutate a real lab.",
    }


@app.post("/api/sdwan/diagnose", operation_id="sdwanDiagnoseEdge")
def diagnose_edge(identifier: str) -> dict[str, object]:
    """Public-safe example of a structured diagnostic response."""
    return {
        "identifier": identifier,
        "reachability": "reachable",
        "control_connections_up": 3,
        "bfd": {"up": 10, "total": 12},
        "config_group": "In Sync",
        "blocking_alarms": 0,
        "status": "pass_with_warnings",
    }

