---
name: pr-comment-fixer
description: GitHub PRのレビューコメント（インラインスレッド・レビュー本文・Issueコメント）を自動検出し、修正を適用するスキル。CodeRabbit・Copilot等のbotコメントにも対応。
version: "2.0.0"
---

# PRコメント自動修正スキル

GitHub PRのレビューコメント（CodeRabbit、Copilot等のbotコメント含む）を全APIソースから網羅的に検出し、コード修正を自動適用するスキルです。修正後のpushで生成される新規レビューも追跡し、全コメント対応完了まで修正ループを自動化します。

## 重要な原則

```text
+---------------------------------------------------------------+
| PRコメント修正の鉄則                                            |
+---------------------------------------------------------------+
| 1. 3つのAPIソースすべてからコメントを取得する                     |
|    （pulls/comments + pulls/reviews + issues/comments）         |
| 2. Review body内のNitpickを見逃さない                           |
|    （CodeRabbitの<details>タグ内等）                             |
| 3. 推測で修正しない - コメントの指摘内容を正確に理解してから修正    |
| 4. 設計判断が必要なコメントは自動修正せずユーザーに報告            |
| 5. push後は新規レビューの出現を監視してから完了判定               |
| 6. CI全チェックpassを確認してからループ完了                       |
+---------------------------------------------------------------+
```

## このスキルを使用する場面

### botレビュー指摘の一括対応

- CodeRabbit、Copilot等のbotがPRにレビューコメントを投稿した場合
- 複数のレビュー指摘を効率的に一括修正したい場合

### レビュー修正ループの自動化

- 修正→push→botの再レビュー→再修正のサイクルを自動化したい場合
- 手動でのコメント対応が煩雑な場合

### 修正漏れの防止

- Review body内のNitpickコメント等、見逃しやすいコメントを確実に検出したい場合
- 全種別のコメントを網羅的にチェックしたい場合

## 基本的な使い方

```text
/pr-comment-fixer {PR番号}
/pr-comment-fixer {PR番号} --max-loops 3
```

### 引数

| 引数 | 必須 | デフォルト | 説明 |
|------|------|-----------|------|
| PR番号 | 必須 | - | 対象のPR番号 |
| --max-loops | 任意 | 5 | 修正ループの最大回数 |

### 前提条件

- `gh` CLIがインストール済みで認証されていること
- 対象リポジトリのクローン内で実行すること
- 対象PRのブランチがチェックアウトされていること

## ワークフロー概要

```text
PR番号を受け取る
    │
    ├── 1. コメント収集（3 APIソース + GraphQL統合）
    │     → 全未対応コメント一覧を生成
    │
    ├── 2. コメント分類
    │     → auto-fixable / manual-required / already-addressed
    │
    ├── 3. 修正適用
    │     → auto-fixableコメントを順次修正
    │
    ├── 4. commit & push
    │
    ├── 5. bot再レビュー待機 & 新規レビュー検出
    │     │
    │     ├── 新規レビュー検出 → Step 1 に戻る
    │     └── 新規レビューなし → Step 6 へ
    │
    ├── 6. 完了判定
    │     │
    │     ├── 未解決コメント残存 → Step 1 に戻る（maxLoops未到達なら）
    │     └── 全条件クリア → 完了
    │
    └── 7. レポート出力
          → 修正済み・手動対応要・CI状態を報告
```

## 各ステップの詳細

### Step 1: コメント収集

3つのAPIソースとGraphQLから全コメントを統合的に取得する。

**詳細**: [references/comment_collector_ja.md](references/comment_collector_ja.md)

#### 収集元

| # | ソース | 取得対象 | 用途 |
|---|--------|---------|------|
| 1 | GraphQL reviewThreads | 未解決インラインスレッド | isResolved判定 |
| 2 | REST pulls/reviews | レビュー本文（body） | Nitpick等の抽出 |
| 3 | REST pulls/comments | インラインコメント詳細 | path/line/diff_hunk |
| 4 | REST issues/comments | PR全体コメント | Summary等（通常スキップ） |

#### bot別コメント構造

**詳細**: [references/bot_comment_patterns_ja.md](references/bot_comment_patterns_ja.md)

- **CodeRabbit**: Actionable → インラインスレッド、Nitpick → Review body内`<details>`タグ、Summary → Issueコメント
- **Copilot**: インラインコメント + suggestion形式
- **その他**: 汎用パーサーで処理

#### GitHub APIの構造

**詳細**: [references/github_review_api_ja.md](references/github_review_api_ja.md)

### Step 2: コメント分類

収集したコメントを3つのカテゴリに分類する。

| カテゴリ | 説明 | 対応 |
|---------|------|------|
| `auto-fixable` | コード修正で対応可能 | 自動修正 |
| `manual-required` | 設計判断が必要、対象ファイル不明等 | ユーザーに報告 |
| `already-addressed` | 既にcommitで修正済み | スキップ |

分類基準:
- `type`が`praise`または`summary` → スキップ
- `type`が`question` → manual-required
- `path`がnull → manual-required
- セキュリティ/アーキテクチャに関する`critical`指摘 → manual-required
- それ以外 → auto-fixable

### Step 3: 修正適用

**詳細**: [references/fix_applicator_ja.md](references/fix_applicator_ja.md)

auto-fixableコメントを順次修正する:

1. 対象ファイルをReadツールで読み込み
2. コメントの指摘内容を分析し、該当箇所を特定
3. Editツールで修正を適用
4. 修正内容を記録

注意事項:
- コメントの指摘に直接対応する最小限の修正のみ
- 周辺コードのリファクタリングは行わない
- suggestion形式（suggestionコードブロック）は提案コードでそのまま置換

### Step 4: commit & push

修正をまとめて1つのコミットにする。

コミットメッセージ:
```text
fix: address PR review comments

Addressed the following review comments:
- [{reviewer}] {path}:{line} - {summary}
...
```

### Step 5: bot再レビュー待機 & 新規レビュー検出

**詳細**: [references/loop_controller_ja.md](references/loop_controller_ja.md)

push後、botが再レビューを生成するまで待機する:

1. `gh pr checks`でCIステータスをポーリング（15秒間隔、最大120秒）
2. `pulls/reviews`で新規レビューIDの出現を監視
3. 全CIがcompletedになり、新規レビューが検出されなくなったら待機完了

新規レビュー検出:
- push前に記録した`known_review_ids`と現在のレビューID一覧を比較
- 新規IDがあれば → Step 1に戻る

### Step 6: 完了判定

以下のすべてを満たす場合にループ完了:

1. GraphQL reviewThreadsで`isResolved: false`のスレッド = 0
2. Review body内の未対応コメント = 0
3. CIチェックが全てpass
4. 新規レビューが検出されていない

### Step 7: レポート出力

**テンプレート**: [assets/templates/fix_report_template_ja.md](assets/templates/fix_report_template_ja.md)

修正結果を報告する:
- 修正済みコメント一覧（レビュアー、ソース、ファイル、行、対応内容）
- 手動対応が必要なコメント一覧（理由付き）
- CI最終状態
- ループ回数サマリー

## 制約事項・禁止事項

### 禁止事項

```text
- 設計判断が必要なコメントを自動修正しない
- コメントの指摘範囲を超えたリファクタリングを行わない
- force pushしない（通常のpushのみ）
- テスト失敗を無視して修正を続行しない（修正が原因の場合）
- Rate Limitを超過するリクエストを行わない
```

### GitHub API Rate Limit対応

- リクエスト間に適切な待機を挟む
- `gh api rate_limit`で残りレートを確認
- Rate Limit残量が少ない場合（残り100未満）はユーザーに警告

### ベストエフォート修正

自動修正できないコメントがあっても、対応可能なコメントは修正する。修正不可のコメントはレポートに明示し、ユーザーに手動対応を促す。

## リソース

| ファイル | 説明 |
|---------|------|
| [references/github_review_api_ja.md](references/github_review_api_ja.md) | GitHub Review API構造の解説 |
| [references/bot_comment_patterns_ja.md](references/bot_comment_patterns_ja.md) | 各botのコメントパターン一覧 |
| [references/comment_collector_ja.md](references/comment_collector_ja.md) | コメント収集ロジック詳細 |
| [references/fix_applicator_ja.md](references/fix_applicator_ja.md) | 修正適用ロジック詳細 |
| [references/loop_controller_ja.md](references/loop_controller_ja.md) | ループ制御ロジック詳細 |
| [assets/templates/fix_report_template_ja.md](assets/templates/fix_report_template_ja.md) | 修正結果レポートテンプレート |
