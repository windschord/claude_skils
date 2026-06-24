#!/bin/bash
# Usage: echo "message" | ./send-message.sh <session_id>
set -euo pipefail
: "${JULES_API_KEY:?JULES_API_KEY is not set}"
SESSION_ID="${1:?Usage: $0 <session_id>}"
PROMPT=$(cat)
curl -sf "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}:sendMessage" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d "$(jq -n --arg p "$PROMPT" '{prompt:$p}')"
