#!/bin/bash
# Usage: echo "prompt text" | ./create-session.sh <source> <branch> <title>
set -euo pipefail
: "${JULES_API_KEY:?JULES_API_KEY is not set}"
SOURCE="${1:?Usage: $0 <source> <branch> <title>}"
BRANCH="${2:?}"
TITLE="${3:?}"
PROMPT=$(cat)
curl -sf 'https://jules.googleapis.com/v1alpha/sessions' \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d "$(jq -n --arg p "$PROMPT" --arg s "$SOURCE" --arg b "$BRANCH" --arg t "$TITLE" \
    '{prompt:$p,sourceContext:{source:$s,githubRepoContext:{startingBranch:$b}},automationMode:"AUTO_CREATE_PR",requirePlanApproval:true,title:$t}')"
