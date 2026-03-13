# コメント収集ロジック

PRの全未対応コメントを3つのAPIソースとGraphQLから統合的に収集し、重複排除・対応済み判定を行うロジック。

## 収集フロー概要

```text
┌─────────────────────────────────────────────────────────────┐
│                    Comment Collector                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: GraphQL reviewThreads                              │
│    → 未解決インラインスレッド一覧                              │
│                                                             │
│  Step 2: REST GET /pulls/{pull_number}/reviews                │
│    → bot別パーサーでNitpick/コメント抽出                      │
│                                                             │
│  Step 3: REST GET /pulls/{pull_number}/comments              │
│    → インラインコメントの詳細(diff_hunk, path, line等)       │
│                                                             │
│  Step 3.5: REST GET /issues/{issue_number}/comments          │
│    → PR全体コメント（botのSummary等、通常スキップ）           │
│                                                             │
│  Step 4: 統合・重複排除                                      │
│    → path+line+内容で判定                                    │
│                                                             │
│  Step 5: 対応済み判定                                        │
│    → 既存commitのdiffと照合                                  │
│                                                             │
│  Output: UnresolvedComment[]                                │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: GraphQL reviewThreadsで未解決スレッド取得

### 目的

インラインスレッドのうち、`isResolved: false`のものを取得する。これがインラインコメントの「未解決」判定の正式なソースとなる。

### 実行コマンド

```bash
OWNER=$(gh repo view --json owner --jq '.owner.login')
REPO=$(gh repo view --json name --jq '.name')

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
              id
              body
              author {
                login
              }
              createdAt
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}' -f owner="$OWNER" -f repo="$REPO" -F pr={PR番号}
```

### 処理

1. `isResolved: false`のスレッドのみを抽出
2. 各スレッドの`comments(last:1)`から最新コメントを取得
3. `isOutdated: true`のスレッドは、コードが変更されているため優先度を下げるが、未解決として扱う

### 出力

```text
unresolvedThreads: [
  {
    source: "graphql_thread",
    threadId: "PRRT_kwDOABC123",
    reviewer: "coderabbitai[bot]",
    path: "src/app/api/environments/route.ts",
    line: 341,
    body: "applyResult.created が 0 でもフィルタリングが有効化される",
    isOutdated: false
  }
]
```

## Step 2: REST pulls/reviewsでレビュー本文取得

### 目的

各レビューのbodyフィールドを取得し、bot別パーサーでNitpick等のコメントを抽出する。

### 実行コマンド

```bash
gh api repos/{owner}/{repo}/pulls/{PR番号}/reviews --paginate \
  --jq '.[] | select(.body != null and .body != "") | {id, user: .user.login, body, state, submitted_at, commit_id}'
```

### 処理

1. bodyが空でないレビューのみを対象とする
2. `user.login`でbot種別を判定
3. bot別パーサーを適用してコメントを抽出（詳細は[bot_comment_patterns_ja.md](bot_comment_patterns_ja.md)参照）
4. レビューIDを`known_review_ids`に記録（新規レビュー検出用）

### 出力

```text
reviewBodyComments: [
  {
    source: "review_body",
    reviewId: 3943619906,
    reviewer: "coderabbitai[bot]",
    type: "nitpick",
    severity: "nitpick",
    path: "docs/sdd/tasks/network-filtering/index.md",
    line: null,
    body: "整合表に TASK-019 / REQ-009 のエントリが欠けている"
  }
]
```

## Step 3: REST pulls/commentsでインラインコメント詳細取得

### 目的

インラインコメントの詳細（diff_hunk、正確なpath/line）を取得する。Step 1のGraphQLスレッドと紐づけて情報を補完する。

### 実行コマンド

```bash
gh api repos/{owner}/{repo}/pulls/{PR番号}/comments --paginate \
  --jq '.[] | {id, pull_request_review_id, user: .user.login, path, line, original_line, diff_hunk, body, in_reply_to_id, created_at}'
```

### 処理

1. `in_reply_to_id`でスレッド構造を再構築
2. 各スレッドの最新コメント（最後の投稿）を取得
3. `diff_hunk`をコンテキスト情報として保持

### 出力

```text
inlineComments: [
  {
    source: "inline_comment",
    commentId: 1234567890,
    reviewId: 9876543210,
    reviewer: "coderabbitai[bot]",
    path: "src/app/api/environments/route.ts",
    line: 341,
    body: "applyResult.created が 0 でもフィルタリングが有効化される",
    diffHunk: "@@ -10,5 +10,7 @@ function example() {"
  }
]
```

## Step 4: 統合・重複排除

### 目的

Step 1-3.5の結果を統合し、同一指摘の重複を除去する。

### 重複判定ロジック

以下の条件をすべて満たす場合、同一指摘として重複とみなす:

1. `path`が一致
2. `line`が一致（nullの場合は`body`の類似度で判定）
3. `body`が類似（先頭100文字の一致、または内容の実質的同一性）

### 優先順位

同一指摘が複数ソースから取得された場合、以下の優先順位で1件に統合する:

1. **GraphQL reviewThreads** — `isResolved`状態を持つため最優先
2. **REST pulls/comments** — `diff_hunk`を持つため詳細情報が豊富
3. **REST pulls/reviews body** — 補完情報
4. **REST issues/comments** — PR全体コメント（通常はsummary/praiseとしてスキップ、必要時のみ補完）

### 統合結果の構造

```text
UnresolvedComment {
  id: string              // 一意な識別子（source_type + 元ID）
  source: string          // "graphql_thread" | "review_body" | "inline_comment" | "issue_comment"
  reviewer: string        // bot名 or ユーザー名
  type: string            // "actionable" | "nitpick" | "suggestion" | "praise" | "question" | "summary"
  severity: string        // "critical" | "major" | "minor" | "nitpick"
  path: string | null     // 対象ファイルパス
  line: number | null     // 対象行番号
  body: string            // コメント本文
  isThread: boolean       // GraphQLスレッドに対応するか
  threadId: string | null // GraphQLスレッドID（resolveに使用）
  reviewId: number | null // 所属レビューID
  diffHunk: string | null // diff context
  status: string          // "unresolved" | "already-addressed" | "skipped"
}
```

## Step 5: 対応済み判定

### 目的

既にcommitで修正済みのコメントを`already-addressed`に分類し、修正対象から除外する。

### 判定方法

1. `git diff`で最新のcommitによる変更を取得
2. 各コメントの`path`と`line`が変更対象に含まれるか確認
3. 変更内容がコメントの指摘と整合するか確認

### 実行コマンド

```bash
# PRのベースブランチとの差分を取得
BASE_BRANCH=$(gh pr view {PR番号} --json baseRefName --jq '.baseRefName')
git diff origin/$BASE_BRANCH...HEAD -- {path}
```

### 判定基準

- **対応済み**: コメントの`path`+`line`付近のコードが変更されており、指摘内容と整合する変更がある
- **未対応**: コメントの`path`+`line`付近に変更がない、または変更が指摘と無関係
- **判定不能**: `path`や`line`がnullの場合 → 未対応として扱う

## エラーハンドリング

### APIエラー時

- 404エラー: PRが存在しない可能性。ユーザーに報告して終了
- 403エラー: 権限不足またはRate Limit。Rate Limit情報を確認し、必要なら待機
- 5xx/ネットワークエラー: 最大3回リトライ（指数バックオフ）

### ページネーション

- GraphQL: `pageInfo.hasNextPage`で判定し、`endCursor`で次ページ取得
- REST: `--paginate`フラグで自動ページネーション
