#!/bin/bash
# Usage: echo "prompt text" | ./create-session.sh <source> <branch> <title> [--force]
#
# 同名タイトルの既存セッションがあれば作成を中断する。承認待ちの間にリトライして
# 同一タスクが重複登録されるのを防ぐためのガード。意図的に再作成する場合のみ
# 第4引数に --force を指定する。
set -euo pipefail
: "${JULES_API_KEY:?JULES_API_KEY is not set}"
SOURCE="${1:?Usage: $0 <source> <branch> <title> [--force]}"
BRANCH="${2:?}"
TITLE="${3:?}"
FORCE="${4:-}"

if [[ "$FORCE" != "--force" ]]; then
  PAGE_TOKEN=""
  EXISTING=""
  while :; do
    URL="https://jules.googleapis.com/v1alpha/sessions?pageSize=100"
    if [[ -n "$PAGE_TOKEN" ]]; then
      URL="${URL}&pageToken=${PAGE_TOKEN}"
    fi
    RESPONSE=$(curl -sf --connect-timeout 10 --max-time 60 \
      "$URL" \
      -H "x-goog-api-key: $JULES_API_KEY")
    MATCH=$(echo "$RESPONSE" | jq -r --arg t "$TITLE" '.sessions[]? | select(.title == $t) | .name')
    if [[ -n "$MATCH" ]]; then
      EXISTING="$MATCH"
      break
    fi
    PAGE_TOKEN=$(echo "$RESPONSE" | jq -r '.nextPageToken // empty')
    [[ -z "$PAGE_TOKEN" ]] && break
  done

  if [[ -n "$EXISTING" ]]; then
    echo "Error: title '$TITLE' のセッションが既に存在します（重複作成を防止するため中断しました）" >&2
    echo "既存セッション: $EXISTING" >&2
    echo "承認前のリトライによる重複でないか確認してください。意図的な再作成であれば第4引数に --force を指定してください。" >&2
    exit 1
  fi
fi

PROMPT=$(cat)
if [[ -z "${PROMPT//[[:space:]]/}" ]]; then
  echo "Error: prompt is empty" >&2
  exit 1
fi
curl -sf --connect-timeout 10 --max-time 120 \
  'https://jules.googleapis.com/v1alpha/sessions' \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d "$(jq -n --arg p "$PROMPT" --arg s "$SOURCE" --arg b "$BRANCH" --arg t "$TITLE" \
    '{prompt:$p,sourceContext:{source:$s,githubRepoContext:{startingBranch:$b}},automationMode:"AUTO_CREATE_PR",requirePlanApproval:true,title:$t}')"
