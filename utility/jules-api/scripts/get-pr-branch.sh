#!/bin/bash
set -euo pipefail
: "${GITHUB_TOKEN:?GITHUB_TOKEN is not set}"
OWNER="${1:?Usage: $0 <owner> <repo> <pr_number>}"
REPO="${2:?}"
PR_NUMBER="${3:?}"
curl -sf --connect-timeout 10 --max-time 60 \
  "https://api.github.com/repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}" \
  -H "Authorization: token $GITHUB_TOKEN" | jq -r '.head.ref'
