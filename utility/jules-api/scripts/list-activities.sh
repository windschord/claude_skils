#!/bin/bash
# Usage: ./list-activities.sh <session_id> [page_size]
set -euo pipefail
: "${JULES_API_KEY:?JULES_API_KEY is not set}"
SESSION_ID="${1:?Usage: $0 <session_id> [page_size]}"
PAGE_SIZE="${2:-20}"
curl -sf "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}/activities?pageSize=${PAGE_SIZE}" \
  -H "x-goog-api-key: $JULES_API_KEY" | jq .
