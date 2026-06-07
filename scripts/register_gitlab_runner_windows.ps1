param(
    [string]$RunnerName = "ai-sdwan-mcp-poc-local",
    [string]$Executor = "shell"
)

$ErrorActionPreference = "Stop"

if (-not $env:GITLAB_URL) {
    throw "Set GITLAB_URL first, for example: `$env:GITLAB_URL='https://gitlab.com'"
}

if (-not $env:GITLAB_RUNNER_TOKEN) {
    throw "Set GITLAB_RUNNER_TOKEN first. Create it in GitLab: Project -> Settings -> CI/CD -> Runners."
}

if (-not (Get-Command gitlab-runner -ErrorAction SilentlyContinue)) {
    throw "gitlab-runner is not installed. Install it first from GitLab Runner docs or with winget if available."
}

gitlab-runner register `
    --non-interactive `
    --url "$env:GITLAB_URL" `
    --token "$env:GITLAB_RUNNER_TOKEN" `
    --executor "$Executor" `
    --description "$RunnerName" `
    --tag-list "local,windows,mcp,sdwan,poc" `
    --run-untagged="true" `
    --locked="false"

Write-Host "GitLab Runner registered as $RunnerName."
Write-Host "Start it with: gitlab-runner run"

