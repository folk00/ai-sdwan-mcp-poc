# Architecture Notes

This public version shows the design pattern without exposing the full private
lab implementation.

## The Pattern

```text
Operator
  -> LLM client
    -> MCP/OpenAPI tools
      -> FastAPI backend
        -> safety checks
          -> SD-WAN Manager / CML / AWS APIs
```

The important part is separation of responsibility:

- The LLM interprets the request and explains the result.
- MCP/OpenAPI defines what actions are available.
- FastAPI validates the request and executes deterministic code.
- Network and cloud APIs remain the source of truth.

## Why This Is Useful

A normal chatbot can explain SD-WAN. This system can check a real lab, create a
virtual branch, onboard it, validate it, and then explain what happened.

That is the difference between "AI for documentation" and "AI-assisted network
operations."

