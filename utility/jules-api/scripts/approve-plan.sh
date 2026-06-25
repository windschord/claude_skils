#!/bin/bash
set -euo pipefail
: "${JULES_API_KEY:?JULES_API_KEY is not set}"
SESSION_ID="${1:?Usage: $0 <session_id>}"
curl -sf --connect-timeout 10 --max-time 60 \
  "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}:approvePlan" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{}'
