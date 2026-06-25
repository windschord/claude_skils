#!/bin/bash
set -euo pipefail
: "${JULES_API_KEY:?JULES_API_KEY is not set}"
curl -sf --connect-timeout 10 --max-time 60 \
  'https://jules.googleapis.com/v1alpha/sources' \
  -H "x-goog-api-key: $JULES_API_KEY" | jq .
