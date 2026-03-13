# GitHub Review APIリファレンス

GitHub PRのコメントは3つの異なるREST APIと1つのGraphQL APIで管理される。全種別のコメントを網羅するには、これらすべてを統合的に参照する必要がある。

## APIソース一覧

| # | API | 取得対象 | エンドポイント |
|---|-----|---------|--------------|
| 1 | Pull Request Comments | インラインコメント（コード行に紐づくスレッド） | `GET /repos/{owner}/{repo}/pulls/{pull_number}/comments` |
| 2 | Pull Request Reviews | レビュー全体（APPROVED/CHANGES_REQUESTED/COMMENTED + body） | `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews` |
| 3 | Issue Comments | PR全体へのコメント（レビュー外） | `GET /repos/{owner}/{repo}/issues/{issue_number}/comments` |
| 4 | GraphQL reviewThreads | インラインスレッドの解決状態 | GraphQL API |

## 1. Pull Request Comments（インラインコメント）

コード行に紐づくレビューコメントを取得する。

### gh CLIコマンド

```bash
# 全インラインコメントを取得
gh api repos/{owner}/{repo}/pulls/{PR番号}/comments --paginate

# 特定フィールドのみ取得
gh api repos/{owner}/{repo}/pulls/{PR番号}/comments --paginate \
  --jq '.[] | {id, user: .user.login, path, line, body, created_at, updated_at}'
```

### レスポンス構造（主要フィールド）

```json
{
  "id": 1234567890,
  "pull_request_review_id": 9876543210,
  "diff_hunk": "@@ -10,5 +10,7 @@ function example() {",
  "path": "src/app/api/environments/route.ts",
  "line": 341,
  "original_line": 340,
  "side": "RIGHT",
  "body": "applyResult.created が 0 でもフィルタリングが有効化される",
  "user": {
    "login": "coderabbitai[bot]"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "in_reply_to_id": null
}
```

### 重要フィールド

| フィールド | 説明 |
|-----------|------|
| `id` | コメントの一意ID |
| `pull_request_review_id` | 所属するレビューのID |
| `path` | 対象ファイルパス |
| `line` | 対象行番号（diffの新しい側） |
| `original_line` | 対象行番号（diffの元の側） |
| `diff_hunk` | コメント周辺のdiff（コンテキスト理解に有用） |
| `body` | コメント本文 |
| `user.login` | 投稿者（bot判定に使用） |
| `in_reply_to_id` | 返信先コメントID（スレッド構造の把握） |

## 2. Pull Request Reviews（レビュー本文）

レビュー全体のメタデータとbody（本文）を取得する。

### gh CLIコマンド

```bash
# 全レビューを取得
gh api repos/{owner}/{repo}/pulls/{PR番号}/reviews --paginate

# 特定フィールドのみ取得
gh api repos/{owner}/{repo}/pulls/{PR番号}/reviews --paginate \
  --jq '.[] | {id, user: .user.login, state, body, submitted_at}'
```

### レスポンス構造（主要フィールド）

```json
{
  "id": 3943619906,
  "user": {
    "login": "coderabbitai[bot]"
  },
  "body": "## Walkthrough\n...\n<details>\n<summary>Nitpick comments (2)</summary>\n...\n</details>",
  "state": "COMMENTED",
  "submitted_at": "2024-01-15T11:00:00Z",
  "commit_id": "abc123def456"
}
```

### 重要フィールド

| フィールド | 説明 |
|-----------|------|
| `id` | レビューの一意ID（新規レビュー検出に使用） |
| `body` | レビュー本文（Nitpick等が埋め込まれている場合あり） |
| `state` | レビュー状態: `APPROVED`, `CHANGES_REQUESTED`, `COMMENTED`, `DISMISSED`, `PENDING` |
| `submitted_at` | 投稿日時 |
| `commit_id` | レビュー対象のcommit SHA |
| `user.login` | 投稿者（bot判定に使用） |

### 注意事項

- **bodyが空の場合がある**: Copilot等はインラインコメントのみでbodyが空になることがある
- **bodyにHTMLが含まれる**: CodeRabbitはbodyに`<details>`タグ等のHTMLを含む
- **同一botから複数レビュー**: 同一のbotがpushごとに新しいレビューを生成する

## 3. Issue Comments（PR全体コメント）

レビュー外のコメント（PR全体に対するコメント）を取得する。

### gh CLIコマンド

```bash
# PR全体コメントを取得
gh api repos/{owner}/{repo}/issues/{PR番号}/comments --paginate

# 特定フィールドのみ取得
gh api repos/{owner}/{repo}/issues/{PR番号}/comments --paginate \
  --jq '.[] | {id, user: .user.login, body, created_at}'
```

### レスポンス構造

```json
{
  "id": 5678901234,
  "user": {
    "login": "coderabbitai[bot]"
  },
  "body": "## Summary by CodeRabbit\n- **New Features**\n  - ...\n- **Bug Fixes**\n  - ...",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### 用途

- CodeRabbitのSummaryコメント（PR全体の要約）
- CI botのステータスレポート
- 人間のPR全体に対するコメント

## 4. GraphQL reviewThreads（未解決スレッド検出）

インラインスレッドの解決状態を効率的に取得する。REST APIでは取得できない`isResolved`フラグを持つ。

### GraphQLクエリ

```bash
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          comments(last: 1) {
            nodes {
              body
              author {
                login
              }
              createdAt
            }
          }
        }
      }
    }
  }
}' -f owner='{owner}' -f repo='{repo}' -F pr={PR番号}
```

### レスポンス構造

```json
{
  "data": {
    "repository": {
      "pullRequest": {
        "reviewThreads": {
          "nodes": [
            {
              "id": "PRRT_kwDOABC123",
              "isResolved": false,
              "isOutdated": false,
              "path": "src/app/api/environments/route.ts",
              "line": 341,
              "comments": {
                "nodes": [
                  {
                    "body": "applyResult.created が 0 でもフィルタリングが有効化される",
                    "author": {
                      "login": "coderabbitai[bot]"
                    },
                    "createdAt": "2024-01-15T10:30:00Z"
                  }
                ]
              }
            }
          ]
        }
      }
    }
  }
}
```

### 重要フィールド

| フィールド | 説明 |
|-----------|------|
| `isResolved` | スレッドが解決済みか（`true`/`false`） |
| `isOutdated` | コードが変更されてスレッドが古くなったか |
| `path` | 対象ファイルパス |
| `line` | 対象行番号 |
| `comments(last:1)` | 最新のコメント（修正すべき指摘内容） |

### 制限事項

- `isResolved`はインラインスレッドにのみ適用される
- Review body内のコメント（CodeRabbit Nitpick等）はスレッドではないため、`isResolved`を持たない
- ページネーション: `first: 100`で最大100件。100件超の場合はカーソルベースのページネーションが必要

## owner/repoの取得方法

```bash
# 現在のリポジトリからowner/repoを取得
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
OWNER=$(echo $REPO | cut -d'/' -f1)
REPO_NAME=$(echo $REPO | cut -d'/' -f2)
```

## Rate Limit確認

```bash
# 残りレート確認
gh api rate_limit --jq '{
  rest: .resources.core | {remaining, reset: (.reset | strftime("%Y-%m-%dT%H:%M:%SZ"))},
  graphql: .resources.graphql | {remaining, reset: (.reset | strftime("%Y-%m-%dT%H:%M:%SZ"))}
}'
```

REST APIは1時間あたり5000リクエスト、GraphQL APIは1時間あたり5000ポイント。大量のコメントがあるPRでは、ページネーションによるリクエスト数に注意すること。
