# Demo Screenshot Guide

Use these screenshots when presenting the project in a CV, reference, or
demos. Keep lab URLs, tokens, device UUIDs, and private IPs redacted if the
repository is public.

## Recommended Screenshots

1. GitLab pipeline overview

   Capture the full pipeline view showing these jobs green:

   ```text
   pipeline_plan
   install_dependencies
   unit_tests
   mcp_tool_smoke
   openapi_smoke
   terraform_validate
   lab_health
   lab_edge_dry_run
   lab_create_edge
   lab_edge_postcheck
   ```

2. Manual lab jobs

   Capture the `lab` stage showing the manual buttons or completed manual jobs.
   This proves the pipeline can be used as an approval gate before touching the
   private lab.

3. Lab create job summary

   Capture the `lab_create_edge` job output after success. The useful lines are:

   ```text
   apply_outcome: success
   hostname: SITE_xxx-Edge1
   system_ip: 10.x.x.x
   post_status: pass
   BFD down: 0
   config group: edge_basic In Sync
   ```

4. MCP tool catalog

   Capture the `mcp_tool_smoke` job or local output from:

   ```powershell
   python scripts\print_tool_catalog.py
   ```

   This shows the LLM-facing tools without exposing private backend code.

5. Code snippets

   Capture these files in your editor:

   ```text
   .gitlab-ci.yml
   scripts/lab_pipeline_client.py
   mcp_server/sdwan_tools_example.py
   backend/automation_engine.py
   ```

   These are the strongest proof points: CI/CD, lab API bridge, MCP tool
   surface, and deterministic automation logic.

## Suggested File Names

Put images under:

```text
docs/images/
```

Suggested names:

```text
gitlab-pipeline-green.png
gitlab-lab-manual-jobs.png
gitlab-lab-create-success.png
mcp-tool-catalog.png
code-gitlab-ci.png
code-lab-pipeline-client.png
```

## Redaction Checklist

Before committing screenshots, hide:

- API keys and tokens
- exact private lab URLs if needed
- raw device UUIDs or chassis IDs
- internal usernames
- browser bookmarks or personal tabs
- customer or restricted data

Public-safe labels like `SITE_530-Edge1`, `edge_basic`, `MCP`, `CML`, `SD-WAN`,
and `GitLab pipeline` are fine for a demo.
