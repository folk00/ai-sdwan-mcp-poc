# MCP Flow

The main point of this project is not that an LLM can talk about networking.
The point is that an LLM can call typed tools and receive structured facts from
real automation code.

## Roles

```text
LLM client
  Understands the operator request, chooses a tool, explains the result.

MCP server
  Publishes a typed tool catalog. It does not contain the model.

FastAPI / automation engine
  Owns validation, guardrails, deterministic logic, and API calls.

Network/cloud APIs
  Source of truth in the private lab.
```

## Example

Operator prompt:

```text
Create a new AutomationSite edge and tell me if it is healthy.
```

Tool call:

```json
{
  "tool": "create_and_onboard_edge",
  "arguments": {
    "edge_label": "DEMO_AutomationSite",
    "dry_run": true,
    "approve": false
  }
}
```

Tool result:

```json
{
  "status": "dry_run",
  "applies_changes": false,
  "plan": {
    "target": {
      "hostname": "DEMO_AutomationSite",
      "system_ip": "10.0.0.4",
      "public_wan_ip": "172.16.1.4",
      "biz_wan_ip": "172.16.2.4",
      "config_group": "edge_basic"
    }
  }
}
```

LLM report:

```text
The plan is safe to review. It would create DEMO_AutomationSite using the next
available system IP and transport IPs, then attach edge_basic and run
postchecks. No mutation was performed because this was a dry run.
```

## Why This Matters

This design keeps the LLM useful but bounded. The model is not handed a shell or
raw credentials. It can only call tools that the backend exposes, and the backend
can reject unsafe requests before anything reaches the network.

