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
5. cat <<'EOF' | scripts/create-session.sh <source> <branch> <title>
   <依頼文（特殊文字・日本語を含んでも安全）>
   EOF
6. /goal を設定してJulesセッションの監視を開始
   （下記「Claudeの監視責任」を参照）
7. scripts/list-activities.sh ${SESSION_ID} で planGenerated を待機
   （sleep がブロックされる環境は下記「プラン待機の代替手段」を参照）
8. プランを評価してユーザーに確認 → scripts/approve-plan.sh ${SESSION_ID}
   （問題があれば先に echo "<修正依頼>" | scripts/send-message.sh ${SESSION_ID}）
9. scripts/list-activities.sh ${SESSION_ID} で completed を待機
10. scripts/get-session.sh ${SESSION_ID} | jq '.output' でPR URL取得
    （webUrl が null の場合は下記「webUrl が null の場合」を参照）
11. scripts/get-pr-branch.sh <owner> <repo> <pr_number> でJulesブランチ名取得・記録
12. docs/sdd/tasks/ をREVIEWに更新
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

## Claudeの監視責任

Julesへのタスク委任は「委任して終わり」ではない。**Claudeがタスクの受け入れ条件を満たす最終責任を持ち**、Julesの実行を能動的に監視・指示する。

### /goal による継続監視（推奨）

セッション作成後すぐに `/goal` でコンプリーション条件を設定する。Claudeはターン間で自動的に監視を続け、条件が満たされると停止する:

```text
/goal scripts/list-activities.sh ${SESSION_ID} の結果に completed イベントが存在し、
scripts/get-session.sh ${SESSION_ID} | jq '.output.pullRequests[0].url' でPR URLが取得でき、
タスクの受け入れ基準がすべてPR内容で確認できること。または30ターン経過したら停止する。
```

`/goal` がアクティブな間、Claudeは各ターンで自動的に以下を実行する:
1. `scripts/list-activities.sh ${SESSION_ID}` でアクティビティを確認
2. `planGenerated` があれば内容を評価し、問題があれば `send-message.sh` で修正を依頼してから `approve-plan.sh` で承認
3. `completed` になったらPRの内容を確認し、受け入れ基準との照合を報告

### /loop によるポーリング（sleep不可環境）

`sleep` がブロックされる環境や定期確認に `/loop` を使う:

```text
/loop 5m scripts/list-activities.sh ${SESSION_ID} | jq '.activities[-3:]' を確認し、
planGenerated があれば評価・approve-plan.sh を実行、completed であれば受け入れ基準を照合して報告
```

### 介入のタイミング

以下を検知した場合は `send-message.sh` で即座に介入する:

- プランが受け入れ条件をカバーしていない
- 実装の方向性が設計書と乖離している
- Julesが追加情報を求めている（ユーザーに確認後、回答を転送）
- コードの品質問題（テスト不足・エラーハンドリングの欠如等）

「これでいいだろう」と介入を省略しない。受け入れ条件を満たすまで監視・指示を継続する。

---

## プラン待機の代替手段

`sleep` が hooks 環境でブロックされる場合、以下のいずれかを使用する:

**方法1: Julesウェブアプリで手動確認（最も確実）**

```text
1. セッション作成後、ユーザーに案内:
   「プランが生成されたら https://jules.google でご確認ください。
    確認できたら「承認してください」とお伝えください。」
2. ユーザーから確認の返答を受け取ったら scripts/approve-plan.sh ${SESSION_ID} を実行
```

**方法2: バックグラウンド実行 + 完了通知待ち**

```bash
# Bash ツールで run_in_background: true を指定して投げ、通知を受けてから次ステップへ
scripts/list-activities.sh ${SESSION_ID} | jq '.activities[] | select(.planGenerated)'
```

完了通知が届いたら `approve-plan.sh` を実行する。

**方法3: Monitor ツールによるポーリング**

```bash
# Monitor ツールにこのコマンドを渡す（sleep は Monitor 内で実行される）
until scripts/list-activities.sh ${SESSION_ID} 2>/dev/null \
  | jq -e '.activities[] | select(.planGenerated)' > /dev/null; do sleep 15; done
```

---

## webUrl が null の場合

セッション作成直後は `webUrl` が `null` になる。`state` が `WORKING` に遷移後に再取得すると得られる場合がある:

```bash
scripts/get-session.sh ${SESSION_ID} | jq '{state, webUrl}'
```

webUrl が取得できない間は `https://jules.google` にアクセスしてセッション一覧から該当タイトルを探すようユーザーに案内する。

---

## JSONペイロードと特殊文字・日本語

スクリプト（`create-session.sh`・`send-message.sh`）は内部で `jq --arg` を使用してJSONを生成するため、**バッククォート・シングルクォート・日本語を含む任意のテキストを安全に送れる**。ヒアドキュメント（`<<'EOF'`）を使うとシェル展開なしで渡せる:

```bash
cat <<'EOF' | scripts/create-session.sh "$SOURCE" "$BRANCH" "TASK-001: 設定修正"
タスク: `config.yaml` の設定修正（TASK-001）

概要:
`production` 環境でO'Brien形式のキーが読み込まれない問題を修正する。

受入基準:
- テスト環境・本番環境で設定が正常に読み込まれること
EOF
```

`api_reference_ja.md` のcurlサンプルは説明用の簡略形式であり、特殊文字を含む場合はそのまま使用できない。curlを直接実行する必要がある場合はPythonでJSONファイルを生成してから送ること:

```bash
python3 - <<'PYEOF' > /tmp/jules_payload.json
import json, sys
payload = {
    "prompt": """タスク: `config.yaml` の設定修正

O'Brien形式のキーが読み込まれない問題を修正する。""",
    "sourceContext": {
        "source": "sources/github/owner/repo",
        "githubRepoContext": {"startingBranch": "develop"}
    },
    "automationMode": "AUTO_CREATE_PR",
    "requirePlanApproval": True,
    "title": "TASK-001: 設定修正"
}
print(json.dumps(payload, ensure_ascii=False))
PYEOF

curl -s 'https://jules.googleapis.com/v1alpha/sessions' \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  --data-binary @/tmp/jules_payload.json
```

---

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
