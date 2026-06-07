# GitLab Runner

GitLab CI has two parts:

```text
.gitlab-ci.yml  = pipeline as code
GitLab Runner   = machine that executes jobs
GitLab web UI   = visual pipeline graph and logs
```

This repo already includes `.gitlab-ci.yml`. To see the GitLab pipeline UI, the
repo must be imported or mirrored into GitLab.

## Do You Need To Register?

Yes, if you want a self-hosted runner.

You need:

1. A GitLab account.
2. A GitLab project.
3. A runner token from:

```text
Project -> Settings -> CI/CD -> Runners
```

Without that token, a laptop or EC2 instance cannot be attached to the GitLab
project.

## Runner Options

### GitLab Hosted Runner

No installation. GitLab provides the runner.

Best for:

- tests
- lint
- Terraform fmt/validate
- public-safe demos

### Local Runner

Install GitLab Runner on your laptop and register it with the project token.

Best for private repos where the pipeline needs local VPN/lab access.

Do not use a local runner for untrusted public projects.

### AWS Runner

Install GitLab Runner on an EC2 instance and register it with the project token.

Best for private automation that needs AWS access, controlled IAM roles, or a
stable always-on runner.

## Register On Windows

Install GitLab Runner, then run:

```powershell
$env:GITLAB_URL = "https://gitlab.com"
$env:GITLAB_RUNNER_TOKEN = "<token-from-gitlab>"
.\scripts\register_gitlab_runner_windows.ps1
```

Start it:

```powershell
gitlab-runner run
```

## Register On Linux / AWS EC2

Install GitLab Runner, then run:

```bash
export GITLAB_URL="https://gitlab.com"
export GITLAB_RUNNER_TOKEN="<token-from-gitlab>"
bash scripts/register_gitlab_runner_linux.sh
```

## Security Boundary

For this public repo, the safest setup is hosted CI only. A self-hosted runner
should be used only in a private repo with locked-down secrets and clear
approval rules.

