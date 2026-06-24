#!/bin/bash
set -euo pipefail
: "${JULES_API_KEY:?JULES_API_KEY is not set}"
curl -sf 'https://jules.googleapis.com/v1alpha/sources' \
  -H "x-goog-api-key: $JULES_API_KEY" | jq .
