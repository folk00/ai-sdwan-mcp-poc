param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    & $Python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m py_compile `
    backend\app.py `
    backend\automation_engine.py `
    mcp_server\sdwan_tools_example.py `
    mcp_server\tool_catalog.py `
    scripts\print_tool_catalog.py

Write-Host "Development environment ready."
Write-Host "Run tests with: .\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v"
