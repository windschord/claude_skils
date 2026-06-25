---
name: jules-api
description: Jules REST APIを使用してタスクを対話的に依頼・管理する。セッション作成・プラン承認・メッセージ送信・進捗監視をAPI経由で行い、Claudeと協調してタスクを完遂する。ベースブランチ指定とPR自動作成に対応。Do NOT use for JULES_API_KEY未設定の環境でのタスク実行（task-executingを使用すること）。
metadata:
  version: "2.0.0"
---

# Jules API統合スキル

## 前提条件

- `JULES_API_KEY` — JulesウェブアプリのSettings > APIキーで取得（最大3つ）
- `GITHUB_TOKEN` — PRブランチ取得時のみ必要（`repo`または`public_repo`スコープ）
- JulesウェブアプリからJules GitHubアプリを対象リポジトリにインストール済みであること

## スクリプト

`scripts/`配下のスクリプトを使用してAPIを操作する（すべて`jq`依存）:

| スクリプト | 引数 | 説明 |
|-----------|------|------|
| `list-sources.sh` | — | 接続済みリポジトリ一覧 |
| `create-session.sh` | `<source> <branch> <title>` / prompt: stdin | セッション作成 |
| `list-sessions.sh` | `[page_size=10]` | セッション一覧 |
| `get-session.sh` | `<session_id>` | セッション詳細・状態確認 |
| `approve-plan.sh` | `<session_id>` | プラン承認 |
| `send-message.sh` | `<session_id>` / message: stdin | メッセージ送信 |
| `list-activities.sh` | `<session_id> [page_size=20]` | アクティビティ一覧 |
| `get-pr-branch.sh` | `<owner> <repo> <pr_number>` | PRのheadブランチ名取得 |

## ワークフロー

### 起動時の判定

```text
Q. ユーザーの依頼はレビュー指摘・仕様変更への対応か？
   YES → レビュー対応フロー（既存セッションを再利用）
   NO  → 基本フロー（新規セッション作成）
```

レビュー指摘対応に新セッションを作成してはならない。新セッションは新ブランチ・新PRを生成し、元のPRを更新できない。

### 基本フロー

```text
1. JULES_API_KEY 確認
2. list-sources.sh でソース名（sources/github/{owner}/{repo}）を確認
3. docs/sdd/tasks/ でTODOタスクを確認・選択
4. ユーザーにベースブランチを確認
5. echo "<依頼文>" | scripts/create-session.sh <source> <branch> <title>
6. scripts/list-activities.sh ${SESSION_ID} で planGenerated を待機
7. プランを評価してユーザーに確認 → scripts/approve-plan.sh ${SESSION_ID}
   （問題があれば先に echo "<修正依頼>" | scripts/send-message.sh ${SESSION_ID}）
8. scripts/list-activities.sh ${SESSION_ID} で completed を待機
9. scripts/get-session.sh ${SESSION_ID} | jq '.output' でPR URL取得
10. scripts/get-pr-branch.sh <owner> <repo> <pr_number> でJulesブランチ名取得・記録
11. docs/sdd/tasks/ をREVIEWに更新
```

### レビュー対応フロー

**既存セッションを再利用する。**

```text
1. タスクファイルの「Jules Session ID」を確認
2. scripts/get-session.sh ${SESSION_ID} | jq '{state, webUrl}'
3. echo "<レビュー指摘と修正内容>" | scripts/send-message.sh ${SESSION_ID}
   - 「既存のPRブランチに修正してください」と明記
   - 「新しいPRは作成しないでください」と明記
4. scripts/list-activities.sh でプラン生成を確認（必要に応じて approve-plan.sh）
5. 完了後、タスクファイルにレビュー対応履歴を追記
```

セッション状態別の対応:

| state | 対応 |
|-------|------|
| `WORKING` | send-message で追加指示 |
| `DONE` | send-message で修正依頼（Jules が同一ブランチで再作業） |
| `FAILED` | 下記フォールバック参照 |

#### フォールバック（セッション再利用不能時）

```bash
git fetch origin
git checkout <julesブランチ名>  # タスクファイルの「Jules ブランチ名」を使用
# 修正を実施
git add -p && git commit -m "fix: レビュー指摘への対応" && git push origin <julesブランチ名>
```

> `startingBranch`は「Julesがブランチを切り出すベース（PR作成先）」であり、既存PRのブランチを指定しても既存PRへのコミット追加にはならない。

## Jules依頼文の形式

```text
タスク: [タスクタイトル]（[TASK-XXX]）

概要:
[詳細な説明]

受入基準:
- [基準1]
- [基準2]

技術的文脈:
- [フレームワーク、ライブラリ]
- [参照ファイル、制約事項]

コミット規約:
- feat/fix/docs等のprefixを使用し、タスクIDを含める
```

PRの作成先ブランチは依頼文ではなく`startingBranch`パラメータで指定する。依頼文は日本語で、技術用語・ファイルパスは英語のまま使用する。

## セッション作成パラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `prompt` | string | タスクの依頼文（必須） |
| `sourceContext.source` | string | `sources/github/{owner}/{repo}` |
| `sourceContext.githubRepoContext.startingBranch` | string | ベースブランチ |
| `automationMode` | string | `AUTO_CREATE_PR`でPR自動作成 |
| `requirePlanApproval` | boolean | `true`でプラン承認要求（推奨） |
| `title` | string | セッションタイトル |

## Claude協調ワークフロー

### プラン評価観点

Julesがプランを生成したらClaudeが以下の観点で評価し、ユーザーに確認を求める:

1. 受入基準との整合（カバーされているか）
2. 技術的妥当性（適切な技術・パターンか）
3. 過不足の確認（不要・欠如ステップ）
4. リスク評価（既存コードへの影響、破壊的変更）

問題がある場合は`send-message.sh`で修正を依頼してから`approve-plan.sh`で承認する。

### 実行中のフィードバック

アクティビティを定期確認し、以下の場合に`send-message.sh`で介入する:
- コードの品質問題を検知した場合
- 進行方向が受入基準から逸れている場合
- 追加情報が必要な場合（ユーザーに確認してから伝達）

## 複数タスクの並行処理

依存関係のないタスクは複数セッションを同時作成できる:

```text
1. 並行実行可能タスクを特定（依存関係グラフ分析）
2. 各タスクの create-session.sh（共通ベースブランチ）
3. 全セッションの list-activities.sh を監視
4. 各セッションのプランを順次確認・承認
5. 完了後 docs/sdd/tasks/ を更新
```

セッション一覧の確認: `scripts/list-sessions.sh`

## docs/sdd/tasks/更新

**ステータス遷移**: `TODO → IN_PROGRESS → REVIEW → DONE`

**段階1（セッション作成時）**:
```markdown
## 実行情報
**実行方式**: Jules API
**Jules Session ID**: {SESSION_ID}
**PR作成先**: {ベースブランチ}
**開始日時**: {日時}
```

**段階2（PR作成時）**:
```markdown
**Jules ブランチ名**: {jules/task-xxx-xxxxxxxx}
**PR番号**: #{番号}
**PR URL**: {URL}
**PR作成日時**: {日時}
```

> **重要**: Julesブランチ名はフォールバック時に必要。`get-pr-branch.sh`で取得して必ず記録する。

**段階3（マージ時）**:
```markdown
**マージ日時**: {日時}
```

**段階4（レビュー対応時）**:
```markdown
## レビュー対応履歴

### {日時} レビュー指摘対応
**対応方法**: {既存セッション再利用（sendMessage）|ローカル修正}
**指摘内容**: [内容]
**対応内容**: [要約]
```

## リソース

- APIリファレンス: `jules-api/references/api_reference_ja.md`
- Jules API公式: https://developers.google.com/jules/api
- Julesウェブアプリ: https://jules.google
