from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.automation_engine import (
    create_and_onboard_edge as run_create_and_onboard_edge,
)
from backend.automation_engine import diagnose_edge as run_diagnose_edge
from backend.automation_engine import list_devices


app = FastAPI(title="AI SD-WAN Automation PoC")


class EdgeRequest(BaseModel):
    edge_label: str
    approve: bool = False
    dry_run: bool = True


class DiagnoseRequest(BaseModel):
    identifier: str


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "public_example",
        "mutations_enabled": False,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/api/sdwan/devices", operation_id="sdwanListDevices")
def sdwan_devices() -> dict[str, object]:
    """Return sample SD-WAN inventory in the same shape the tools consume."""
    return list_devices()


@app.post("/api/sdwan/onboarding/by-label", operation_id="sdwanCreateAndOnboardEdge")
def create_and_onboard_edge(request: EdgeRequest) -> dict[str, object]:
    """Public-safe example of the private onboarding workflow shape."""
    if not request.dry_run and not request.approve:
        raise HTTPException(status_code=403, detail="approve=true is required")
    return run_create_and_onboard_edge(
        request.edge_label,
        approve=request.approve,
        dry_run=request.dry_run,
    )


@app.post("/api/sdwan/diagnose", operation_id="sdwanDiagnoseEdge")
def diagnose_edge(request: DiagnoseRequest) -> dict[str, object]:
    """Public-safe example of a structured diagnostic response."""
    return run_diagnose_edge(request.identifier)
