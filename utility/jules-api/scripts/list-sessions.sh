#!/bin/bash
# Usage: ./list-sessions.sh [page_size]
set -euo pipefail
: "${JULES_API_KEY:?JULES_API_KEY is not set}"
PAGE_SIZE="${1:-10}"
curl -sf --connect-timeout 10 --max-time 60 \
  "https://jules.googleapis.com/v1alpha/sessions?pageSize=${PAGE_SIZE}" \
  -H "x-goog-api-key: $JULES_API_KEY" | jq '.sessions[] | {name, title, state}'
