#!/bin/bash
# Usage: ./list-sources.sh
# 全ページを取得して結合する（対象リポジトリがpage 2以降にある場合に見落とさないため）
set -euo pipefail
: "${JULES_API_KEY:?JULES_API_KEY is not set}"

PAGE_TOKEN=""
ALL_SOURCES="[]"

while :; do
  URL="https://jules.googleapis.com/v1alpha/sources?pageSize=100"
  if [[ -n "$PAGE_TOKEN" ]]; then
    URL="${URL}&pageToken=${PAGE_TOKEN}"
  fi

  RESPONSE=$(curl -sf --connect-timeout 10 --max-time 60 \
    "$URL" \
    -H "x-goog-api-key: $JULES_API_KEY")

  ALL_SOURCES=$(jq -n --argjson acc "$ALL_SOURCES" --argjson resp "$RESPONSE" \
    '$acc + ($resp.sources // [])')

  PAGE_TOKEN=$(echo "$RESPONSE" | jq -r '.nextPageToken // empty')
  [[ -z "$PAGE_TOKEN" ]] && break
done

echo "$ALL_SOURCES" | jq '{sources: .}'
