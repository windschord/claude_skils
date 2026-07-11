---
name: jules-api
description: Jules REST APIを使用してタスクを対話的に依頼・管理する。セッション作成・プラン承認・メッセージ送信・進捗監視をAPI経由で行い、Claudeと協調してタスクを完遂する。ベースブランチ指定とPR自動作成に対応。認証はJULES_API_KEY_OP_URI（1Passwordシークレット参照）またはJULES_API_KEYで行う。Do NOT use for 認証情報未設定の環境でのタスク実行（task-executingを使用すること）。
metadata:
  version: "3.0.0"
---

# Jules API統合スキル

## 前提条件

- Jules APIキー — JulesウェブアプリのSettings > APIキーで取得（最大3つ）。下記「認証情報の設定」参照
- GitHubトークン — PRブランチ取得時のみ必要（`repo`または`public_repo`スコープ）
- JulesウェブアプリからJules GitHubアプリを対象リポジトリにインストール済みであること

### 認証情報の設定

`scripts/jules.sh`は以下の優先順で認証情報を解決する:

| 優先 | 環境変数 | 内容 |
|------|----------|------|
| 1 | `JULES_API_KEY_OP_URI` / `GITHUB_TOKEN_OP_URI` | 1Passwordシークレット参照（`op://<vault>/<item>/<field>`）。実行時に`op read`で取得 |
| 2 | `JULES_API_KEY` / `GITHUB_TOKEN` | シークレットの直接指定（後方互換） |

**1Passwordシークレット参照を推奨する。** 環境変数には参照URIのみが載り、シークレット本体はプロセス環境・シェル履歴・設定ファイルに残らない。1Password CLI（`op`）のインストールとサインインが前提。

Claude Codeの`settings.json`（`.claude/settings.json`または`~/.claude/settings.json`）に設定する例:

```json
{
  "env": {
    "JULES_API_KEY_OP_URI": "op://Private/Jules/api-key",
    "GITHUB_TOKEN_OP_URI": "op://Private/GitHub/token"
  }
}
```

`JULES_API_KEY_OP_URI`が設定されているのに`op`が見つからない・`op read`が失敗する場合、スクリプトはエラーで停止する（直接指定へ黙ってフォールバックしない）。

## スクリプト

`scripts/jules.sh`のサブコマンドでAPIを操作する（`jq`依存）:

| サブコマンド | 引数 | 説明 |
|-------------|------|------|
| `list-sources` | — | 接続済みリポジトリ一覧（全ページを自動取得） |
| `create-session` | `<source> <branch> <title> [--force]` / prompt: stdin | セッション作成（同名タイトルの重複作成を自動検知して中断） |
| `list-sessions` | `[page_size=10]` | セッション一覧 |
| `get-session` | `<session_id>` | セッション詳細・状態確認 |
| `approve-plan` | `<session_id>` | プラン承認 |
| `send-message` | `<session_id>` / message: stdin | メッセージ送信 |
| `list-activities` | `<session_id> [page_size=20]` | アクティビティ一覧 |
| `get-pr-branch` | `<owner> <repo> <pr_number>` | PRのheadブランチ名取得 |

ヘルプ表示: `scripts/jules.sh help`

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
1. 認証情報の確認（JULES_API_KEY_OP_URI または JULES_API_KEY。上記「認証情報の設定」参照）
2. jules.sh list-sources でソース名（sources/github/{owner}/{repo}）を確認
   （全ページを自動取得するため、対象リポジトリが多数の接続先の後方にあっても見落とさない）
3. docs/sdd/tasks/ でTODOタスクを確認・選択
4. ユーザーにベースブランチを確認
5. cat <<'EOF' | scripts/jules.sh create-session <source> <branch> <title>
   <依頼文（特殊文字・日本語を含んでも安全）>
   EOF
   同名タイトルの既存セッションがある場合はスクリプトがエラーで中断する
   （下記「リトライ時の重複防止」を参照。曖昧な失敗時に承認を待たず再実行しないこと）
6. /goal を設定してJulesセッションの監視を開始
   （下記「Claudeの監視責任」を参照）
7. scripts/jules.sh list-activities ${SESSION_ID} で planGenerated を待機
   （sleep がブロックされる環境は下記「プラン待機の代替手段」を参照）
8. プランを評価してユーザーに確認 → scripts/jules.sh approve-plan ${SESSION_ID}
   （問題があれば先に echo "<修正依頼>" | scripts/jules.sh send-message ${SESSION_ID}）
9. scripts/jules.sh list-activities ${SESSION_ID} で completed を待機
10. scripts/jules.sh get-session ${SESSION_ID} | jq -r '.output.pullRequests[0].url' でPR URL取得
    （webUrl が null の場合は下記「webUrl が null の場合」を参照）
11. PRの差分を確認する（下記「PR差分の確認（必須）」を参照）
    既存機能の意図しない削除・変更を検知したら jules.sh send-message で修正依頼 → 9に戻る
12. scripts/jules.sh get-pr-branch <owner> <repo> <pr_number> でJulesブランチ名取得・記録
13. docs/sdd/tasks/ をREVIEWに更新
```

### レビュー対応フロー

**既存セッションを再利用する。**

```text
1. タスクファイルの「Jules Session ID」を確認
2. scripts/jules.sh get-session ${SESSION_ID} | jq '{state, webUrl}'
3. echo "<レビュー指摘と修正内容>" | scripts/jules.sh send-message ${SESSION_ID}
   - 「既存のPRブランチに修正してください」と明記
   - 「新しいPRは作成しないでください」と明記
4. scripts/jules.sh list-activities でプラン生成を確認（必要に応じて jules.sh approve-plan）
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
/goal scripts/jules.sh list-activities ${SESSION_ID} の結果に completed イベントが存在し、
scripts/jules.sh get-session ${SESSION_ID} | jq '.output.pullRequests[0].url' でPR URLが取得でき、
タスクの受け入れ基準がすべてPR内容で確認できること。または30ターン経過したら停止する。
```

`/goal` がアクティブな間、Claudeは各ターンで自動的に以下を実行する:
1. `scripts/jules.sh list-activities ${SESSION_ID}` でアクティビティを確認
2. `planGenerated` があれば内容を評価し、問題があれば `jules.sh send-message` で修正を依頼してから `jules.sh approve-plan` で承認
3. `completed` になったらPRの内容を確認し、受け入れ基準との照合を報告

### /loop によるポーリング（sleep不可環境）

`sleep` がブロックされる環境や定期確認に `/loop` を使う:

```text
/loop 5m scripts/jules.sh list-activities ${SESSION_ID} | jq '.activities[-3:]' を確認し、
planGenerated があれば評価・jules.sh approve-plan を実行、completed であれば受け入れ基準を照合して報告
```

### 介入のタイミング

以下を検知した場合は `jules.sh send-message` で即座に介入する:

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
2. ユーザーから確認の返答を受け取ったら scripts/jules.sh approve-plan ${SESSION_ID} を実行
```

**方法2: バックグラウンド実行 + 完了通知待ち**

```bash
# Bash ツールで run_in_background: true を指定して投げ、通知を受けてから次ステップへ
scripts/jules.sh list-activities ${SESSION_ID} | jq '.activities[] | select(.planGenerated)'
```

完了通知が届いたら `jules.sh approve-plan` を実行する。

**方法3: Monitor ツールによるポーリング**

```bash
# Monitor ツールにこのコマンドを渡す（sleep は Monitor 内で実行される）
until scripts/jules.sh list-activities ${SESSION_ID} 2>/dev/null \
  | jq -e '.activities[] | select(.planGenerated)' > /dev/null; do sleep 15; done
```

---

## リトライ時の重複防止

`jules.sh create-session` はセッション作成前に同名タイトルの既存セッションを検索し、見つかった場合はエラーで中断する。

**曖昧な失敗（タイムアウト・応答なし等）が起きても、ユーザーの作業承認を待たずに`jules.sh create-session`を再実行してはならない。** リクエストがJules側では成功していた場合、再実行は同一タスクの重複セッションを生成する。

```text
失敗時の対応:
1. scripts/jules.sh list-sessions で同名タイトルのセッションが既に存在しないか確認する
2. 存在する場合はそのセッションを使う（再作成しない）
3. 存在しない場合のみ、失敗原因（認証・パラメータ等）を特定してから再実行する
4. 原因が不明なまま闇雲にリトライしない。2-3回失敗した場合はユーザーに報告し、指示を仰ぐ
5. 意図的に同名タイトルで再作成する必要がある場合のみ、jules.sh create-session の第4引数に --force を指定する
```

---

## PR差分の確認（必須）

Julesは既存機能との差分を十分理解せずに、関係のないコードを削除してしまうことがある。**PRをREVIEW・マージ判断する前に、必ず実際の差分内容を読む。**サマリーや `+N/-M` の統計だけで判断しない。

```text
1. GitHub MCPツール（pull_request_read等）や git diff でPR全体の差分を取得する
2. 削除・変更された行ごとに、今回のタスクの受入基準・変更目的と関連があるか確認する
3. 以下に該当する削除を検知したら、REVIEW/DONEにせず jules.sh send-message で理由を確認する:
   - タスクのスコープ外のファイル・関数・分岐が削除されている
   - 既存のテストケースが削除・スキップされている（失敗回避のための削除を含む）
   - 既存の公開API・設定・エクスポートが削除されている
4. 不要な削除であればJulesに復元を依頼し、再度差分を確認してからREVIEWに進める
5. 削除の意図が不明な場合はマージ前にユーザーへ報告し、承認を得る
```

---

## webUrl が null の場合

セッション作成直後は `webUrl` が `null` になる。`state` が `WORKING` に遷移後に再取得すると得られる場合がある:

```bash
scripts/jules.sh get-session ${SESSION_ID} | jq '{state, webUrl}'
```

webUrl が取得できない間は `https://jules.google` にアクセスしてセッション一覧から該当タイトルを探すようユーザーに案内する。

---

## JSONペイロードと特殊文字・日本語

スクリプト（`jules.sh create-session`・`jules.sh send-message`）は内部で `jq --arg` を使用してJSONを生成するため、**バッククォート・シングルクォート・日本語を含む任意のテキストを安全に送れる**。ヒアドキュメント（`<<'EOF'`）を使うとシェル展開なしで渡せる:

```bash
cat <<'EOF' | scripts/jules.sh create-session "$SOURCE" "$BRANCH" "TASK-001: 設定修正"
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
4. リスク評価（既存コードへの影響、破壊的変更、既存機能の削除の有無）

問題がある場合は`jules.sh send-message`で修正を依頼してから`jules.sh approve-plan`で承認する。プラン承認は差分内容の保証にはならないため、完了後は必ず「PR差分の確認（必須）」を実施する。

### 実行中のフィードバック

アクティビティを定期確認し、以下の場合に`jules.sh send-message`で介入する:
- コードの品質問題を検知した場合
- 進行方向が受入基準から逸れている場合
- 追加情報が必要な場合（ユーザーに確認してから伝達）

## 複数タスクの並行処理

依存関係のないタスクは複数セッションを同時作成できる:

```text
1. 並行実行可能タスクを特定（依存関係グラフ分析）
2. 各タスクの jules.sh create-session（共通ベースブランチ）
3. 全セッションの jules.sh list-activities を監視
4. 各セッションのプランを順次確認・承認
5. 完了後 docs/sdd/tasks/ を更新
```

セッション一覧の確認: `scripts/jules.sh list-sessions`

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

> **重要**: Julesブランチ名はフォールバック時に必要。`jules.sh get-pr-branch`で取得して必ず記録する。

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
