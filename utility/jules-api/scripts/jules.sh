#!/bin/bash
# jules.sh — Jules API 統合コマンド
#
# 旧 scripts/*.sh（list-sources.sh 等）をサブコマンドとして1本に統合したスクリプト。
#
# Usage:
#   jules.sh list-sources
#   echo "prompt" | jules.sh create-session <source> <branch> <title> [--force]
#   jules.sh list-sessions [page_size=10]
#   jules.sh get-session <session_id>
#   jules.sh approve-plan <session_id>
#   echo "message" | jules.sh send-message <session_id>
#   jules.sh list-activities <session_id> [page_size=20]
#   jules.sh get-pr-branch <owner> <repo> <pr_number>
#
# 認証情報の解決（優先順）:
#   1. JULES_API_KEY_OP_URI / GITHUB_TOKEN_OP_URI に1Passwordシークレット参照
#      （op://<vault>/<item>/<field>）が設定されていれば、実行時に `op read` で取得する。
#      環境変数には参照URIのみが載り、シークレット本体は載らないため安全。
#   2. 未設定の場合は JULES_API_KEY / GITHUB_TOKEN を直接使用する（後方互換）。
set -euo pipefail

API_BASE="https://jules.googleapis.com/v1alpha"

usage() {
  # 先頭のヘッダーコメントブロック（shebang除く）をそのままヘルプとして表示する
  awk 'NR == 1 { next } /^#/ { sub(/^# ?/, ""); print; next } { exit }' "$0"
}

die() {
  echo "Error: $*" >&2
  exit 1
}

# resolve_secret <op_uri_var> <direct_var>
# 1Passwordシークレット参照を優先して解決し、標準出力にシークレットを返す
resolve_secret() {
  local op_uri_var="$1" direct_var="$2"
  local op_uri="${!op_uri_var:-}" direct="${!direct_var:-}"

  if [[ -n "$op_uri" ]]; then
    [[ "$op_uri" == op://* ]] \
      || die "$op_uri_var は op://<vault>/<item>/<field> 形式で指定してください（現在値は op:// で始まっていません）"
    command -v op >/dev/null 2>&1 \
      || die "$op_uri_var が設定されていますが 1Password CLI (op) が見つかりません。https://developer.1password.com/docs/cli/ からインストールしてください"
    op read --no-newline "$op_uri" \
      || die "op read に失敗しました（$op_uri_var の参照先・1Passwordのサインイン状態を確認してください）"
  elif [[ -n "$direct" ]]; then
    printf '%s' "$direct"
  else
    die "$op_uri_var（1Passwordシークレット参照）または $direct_var（直接指定）のいずれかを設定してください"
  fi
}

require_jules_key() {
  JULES_API_KEY="$(resolve_secret JULES_API_KEY_OP_URI JULES_API_KEY)"
}

require_github_token() {
  GITHUB_TOKEN="$(resolve_secret GITHUB_TOKEN_OP_URI GITHUB_TOKEN)"
}

jules_curl() {
  # jules_curl <max_time> <url> [curl args...]
  local max_time="$1" url="$2"
  shift 2
  curl -sf --connect-timeout 10 --max-time "$max_time" \
    "$url" \
    -H "x-goog-api-key: $JULES_API_KEY" \
    "$@"
}

read_stdin_prompt() {
  PROMPT=$(cat)
  if [[ -z "${PROMPT//[[:space:]]/}" ]]; then
    die "stdinからの入力が空です"
  fi
}

cmd_list_sources() {
  require_jules_key
  # 全ページを取得して結合する（対象リポジトリがpage 2以降にある場合に見落とさないため）
  local page_token="" all_sources="[]" url response
  while :; do
    url="${API_BASE}/sources?pageSize=100"
    [[ -n "$page_token" ]] && url="${url}&pageToken=${page_token}"
    response=$(jules_curl 60 "$url")
    all_sources=$(jq -n --argjson acc "$all_sources" --argjson resp "$response" \
      '$acc + ($resp.sources // [])')
    page_token=$(echo "$response" | jq -r '.nextPageToken // empty')
    [[ -z "$page_token" ]] && break
  done
  echo "$all_sources" | jq '{sources: .}'
}

cmd_create_session() {
  # 同名タイトルの既存セッションがあれば作成を中断する。承認待ちの間にリトライして
  # 同一タスクが重複登録されるのを防ぐためのガード。意図的に再作成する場合のみ
  # --force を指定する。
  local source="${1:?Usage: $0 create-session <source> <branch> <title> [--force]}"
  local branch="${2:?}" title="${3:?}" force="${4:-}"
  require_jules_key

  if [[ "$force" != "--force" ]]; then
    local page_token="" existing="" url response match
    while :; do
      url="${API_BASE}/sessions?pageSize=100"
      [[ -n "$page_token" ]] && url="${url}&pageToken=${page_token}"
      response=$(jules_curl 60 "$url")
      match=$(echo "$response" | jq -r --arg t "$title" '.sessions[]? | select(.title == $t) | .name')
      if [[ -n "$match" ]]; then
        existing="$match"
        break
      fi
      page_token=$(echo "$response" | jq -r '.nextPageToken // empty')
      [[ -z "$page_token" ]] && break
    done

    if [[ -n "$existing" ]]; then
      echo "Error: title '$title' のセッションが既に存在します（重複作成を防止するため中断しました）" >&2
      echo "既存セッション: $existing" >&2
      echo "承認前のリトライによる重複でないか確認してください。意図的な再作成であれば --force を指定してください。" >&2
      exit 1
    fi
  fi

  read_stdin_prompt
  jules_curl 120 "${API_BASE}/sessions" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg p "$PROMPT" --arg s "$source" --arg b "$branch" --arg t "$title" \
      '{prompt:$p,sourceContext:{source:$s,githubRepoContext:{startingBranch:$b}},automationMode:"AUTO_CREATE_PR",requirePlanApproval:true,title:$t}')"
}

cmd_list_sessions() {
  local page_size="${1:-10}"
  require_jules_key
  jules_curl 60 "${API_BASE}/sessions?pageSize=${page_size}" \
    | jq '.sessions[] | {name, title, state}'
}

cmd_get_session() {
  local session_id="${1:?Usage: $0 get-session <session_id>}"
  require_jules_key
  jules_curl 60 "${API_BASE}/sessions/${session_id}" | jq .
}

cmd_approve_plan() {
  local session_id="${1:?Usage: $0 approve-plan <session_id>}"
  require_jules_key
  jules_curl 60 "${API_BASE}/sessions/${session_id}:approvePlan" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{}'
}

cmd_send_message() {
  local session_id="${1:?Usage: $0 send-message <session_id> (message: stdin)}"
  require_jules_key
  read_stdin_prompt
  jules_curl 60 "${API_BASE}/sessions/${session_id}:sendMessage" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg p "$PROMPT" '{prompt:$p}')"
}

cmd_list_activities() {
  local session_id="${1:?Usage: $0 list-activities <session_id> [page_size]}"
  local page_size="${2:-20}"
  require_jules_key
  jules_curl 60 "${API_BASE}/sessions/${session_id}/activities?pageSize=${page_size}" | jq .
}

cmd_get_pr_branch() {
  local owner="${1:?Usage: $0 get-pr-branch <owner> <repo> <pr_number>}"
  local repo="${2:?}" pr_number="${3:?}"
  require_github_token
  curl -sf --connect-timeout 10 --max-time 60 \
    "https://api.github.com/repos/${owner}/${repo}/pulls/${pr_number}" \
    -H "Authorization: token $GITHUB_TOKEN" | jq -r '.head.ref'
}

COMMAND="${1:-}"
[[ -n "$COMMAND" ]] || { usage >&2; exit 1; }
shift

case "$COMMAND" in
  list-sources)    cmd_list_sources "$@" ;;
  create-session)  cmd_create_session "$@" ;;
  list-sessions)   cmd_list_sessions "$@" ;;
  get-session)     cmd_get_session "$@" ;;
  approve-plan)    cmd_approve_plan "$@" ;;
  send-message)    cmd_send_message "$@" ;;
  list-activities) cmd_list_activities "$@" ;;
  get-pr-branch)   cmd_get_pr_branch "$@" ;;
  help|--help|-h)  usage ;;
  *)
    echo "Error: 不明なコマンド: $COMMAND" >&2
    usage >&2
    exit 1
    ;;
esac
