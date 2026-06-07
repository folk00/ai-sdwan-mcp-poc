#!/usr/bin/env bash
set -euo pipefail

RUNNER_NAME="${RUNNER_NAME:-ai-sdwan-mcp-poc-linux}"
EXECUTOR="${EXECUTOR:-shell}"

if [ -z "${GITLAB_URL:-}" ]; then
  echo "Set GITLAB_URL first, for example: export GITLAB_URL=https://gitlab.com" >&2
  exit 1
fi

if [ -z "${GITLAB_RUNNER_TOKEN:-}" ]; then
  echo "Set GITLAB_RUNNER_TOKEN first. Create it in GitLab: Project -> Settings -> CI/CD -> Runners." >&2
  exit 1
fi

if ! command -v gitlab-runner >/dev/null 2>&1; then
  echo "gitlab-runner is not installed. Install it first from GitLab Runner docs." >&2
  exit 1
fi

gitlab-runner register \
  --non-interactive \
  --url "$GITLAB_URL" \
  --token "$GITLAB_RUNNER_TOKEN" \
  --executor "$EXECUTOR" \
  --description "$RUNNER_NAME" \
  --tag-list "linux,mcp,sdwan,poc" \
  --run-untagged="true" \
  --locked="false"

echo "GitLab Runner registered as $RUNNER_NAME."

