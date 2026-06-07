# Code Highlights

The public version keeps small snippets to show the idea without publishing the
full private automation engine.

## FastAPI Tool Shape

```python
@app.post("/api/sdwan/onboarding/by-label", operation_id="sdwanCreateAndOnboardEdge")
def create_and_onboard_edge(request: EdgeRequest) -> dict:
    if not request.dry_run and not request.approve:
        raise HTTPException(status_code=403, detail="approve=true is required")
    return {"mode": "dry_run", "edge_label": request.edge_label}
```

## MCP Tool Shape

```python
@mcp.tool()
def get_devices() -> dict:
    return {"devices": [{"host_name": "Edge1", "status": "normal"}]}
```

## Terraform Shape

```hcl
resource "aws_eip" "connector" {
  domain = "vpc"
}
```

The private version expands these patterns into real SD-WAN Manager calls, CML
node creation, bootstrap handling, config-group deployment, and postchecks.

