---
name: orchestrating-agents
description: Orchestrates multi-step tasks autonomously using a 3-tier agent hierarchy (Director/Manager/Worker). Use when user says "run this end-to-end", "handle everything", "execute all tasks", or needs parallel task execution with queuing, course correction, and session resume. Provides FIFO task queue, escalation policy, git worktree isolation, and context persistence across agent sessions.
---

# Orchestrating Agents スキル

3階層の親子孫エージェント構造により、ユーザーが最初の指示を出すだけで自律的にタスクを完遂する共通基盤スキルです。

## 3階層アーキテクチャ

| 階層 | 役割 | 責務 |
|------|------|------|
| **親（Director）** | ユーザーとの唯一の対話窓口 | 指示解釈、子への委譲、達成評価、キュー管理、エスカレーション転送 |
| **子（Manager）** | フェーズの管理者 | 孫への作業分解・委譲、品質評価、代理承認、親への報告 |
| **孫（Worker）** | 実務の実行者 | 実装・分析・ドキュメント作成等の単一タスク実行 |

### Agent toolによる3階層実現

```text
親（メインセッション）
  └── Agent tool(subagent_type: "general-purpose") で子を起動
        └── 子が Agent tool で孫を起動
```

- 子は `general-purpose` 型で起動する（Agent toolを含む全ツールにアクセス可能）
- 孫は用途に応じた型で起動する（`task-executing` 等、Agent tool不要）
- 子が孫を起動するには `general-purpose` 型であることが必須

## 適応的階層選択

全てのケースで3階層を強制しない:

| 条件 | モード | 動作 |
|------|--------|------|
| 単純タスク | 2階層 | 子が直接実務を実行 |
| 複数タスクの並列実行・分解が必要 | 3階層 | 子が孫を起動して委譲 |

判定基準:
1. 並列実行可能な独立タスクが2つ以上あるか
2. 各タスクが異なるファイルセットを対象としているか
3. タスク間に依存関係がないか

## 実行前チェック（明示情報 / 不明情報）

親はタスク分解の前に、ユーザーの指示を以下のように分類する:

- **明示情報**: ユーザーが明確に指定した事項（対象、成果物、制約、期限など）
- **不明情報**: 推測が必要な事項、曖昧な記述、未指定の前提条件

**不明情報が1つでもある場合、実行を開始せずユーザーに確認する。** 「おそらく〜だろう」という推測は「不明」として扱う。

この分類は `mission.md` に記録し、子セッションへの指示にも含める。

## 起動フロー

### 1. ミッション定義

ユーザーの指示を受けたら、親は `.orchestrating-agents/mission.md` を作成:

```text
1. ユーザーの原文指示を保存
2. 目標・成功基準を解釈・記録
3. 実行計画を策定
4. .gitignore に一時ファイルのパターンを追加（未登録の場合）
```

テンプレート: `assets/templates/mission_template_ja.md`

### 2. タスク分解とキュー登録

```text
1. 指示をタスクに分解
2. TaskCreate で各タスクをpending状態で登録
3. .orchestrating-agents/task_ledger.md にタスク台帳を作成
4. 依存関係を分析し、実行順序を決定
```

テンプレート: `assets/templates/task_ledger_template_ja.md`

### 3. 子セッション起動

```text
Agent tool(
  subagent_type: "general-purpose",
  name: "child-<task-type>",
  run_in_background: true,
  isolation: "worktree",  # 並列実行時
  prompt: <親→子 指示フォーマット>
)
```

テンプレート: `assets/templates/parent_prompt_template_ja.md`

### 4. キュー処理（FIFO）

```text
1. TaskList でpendingの最古タスクを取得
2. 子セッションを起動して実行
3. 完了後、task_ledger.md を更新
4. 次のpendingタスクへ
```

詳細: `references/queue_management_ja.md`

## 軌道変更メカニズム

Agent toolの `name` パラメータで子セッションに名前を付けて起動し、`SendMessage` で進行中の子に方針変更を伝達:

```text
1. 親: Agent tool(name: "child-task-exec", run_in_background: true) で子を起動
2. ユーザー: 方針変更を親に伝える
3. 親: SendMessage(to: "child-task-exec", message: 方針変更内容) で子に伝達
4. 子: 受信した変更を反映して作業を調整
5. 親: task_ledger.md の軌道変更履歴に記録
```

詳細: `references/course_correction_ja.md`

## エスカレーション方針

| 判断レベル | 処理者 | 例 |
|-----------|--------|-----|
| 技術的トレードオフ | 子が代理承認 | ライブラリ選択、軽微なリファクタリング |
| 軽微な修正 | 子が代理承認 | typo修正、インポート追加 |
| リトライ判断 | 子が代理承認 | 一時的エラーの再試行 |
| ファイル削除・データ破壊 | 親→ユーザー | データベーステーブル削除 |
| 仕様変更 | 親→ユーザー | API契約の変更 |
| アーキテクチャ変更 | 親→ユーザー | フレームワーク変更 |
| 要件の曖昧さ | 親→ユーザー | 受入基準が不明確 |

詳細: `references/escalation_policy_ja.md`

## エラーハンドリング

```text
孫が失敗 → 子がリトライ（最大2回、コンテキスト追加）
         → 失敗継続なら親にエスカレーション

子が失敗 → 親がリトライ（最大1回）
         → 失敗継続ならユーザーに報告
```

## Git Worktreeによる並列実行

子・孫を複数同時に起動する場合、`isolation: "worktree"` で各セッションが独立したgit worktreeで動作:

```text
親セッション（メインブランチ）
├── 子1: Agent tool(isolation: "worktree", name: "child-requirements")
├── 子2: Agent tool(isolation: "worktree", name: "child-task-exec")
│   ├── 孫2a: Agent tool(isolation: "worktree")
│   └── 孫2b: Agent tool(isolation: "worktree")
```

- 各worktreeは独立したブランチで動作
- 孫の完了後、子がworktreeの変更をマージ
- 子の完了後、親がworktreeの変更をメインブランチにマージ
- マージコンフリクト発生時は親が解決

## コンテキスト永続化

親・子セッションがコンテキスト圧縮されても状態を維持するための永続化メカニズム。

### ファイル配置

```text
.orchestrating-agents/
├── mission.md                  # 親のミッション定義（.gitignore対象）
├── task_ledger.md              # タスク台帳（.gitignore対象）
├── session_state.md            # セッション状態（.gitignore対象）
├── archive/                    # アーカイブ（.gitignore対象）
│   └── completed_tasks.md
└── workorders/                 # 子のワークオーダー（git追跡対象）
    ├── TASK-001.md
    └── TASK-002.md
```

**git追跡方針**: `workorders/` は子がworktree内でコミット・親がメインブランチにマージするため、git追跡対象とする。それ以外（`mission.md`、`task_ledger.md`、`session_state.md`、`archive/`）はセッション固有の一時データとして `.gitignore` に追加する。

`.gitignore` への追加内容:
```text
.orchestrating-agents/mission.md
.orchestrating-agents/task_ledger.md
.orchestrating-agents/session_state.md
.orchestrating-agents/archive/
```

- **mission.md**: 親のみが更新（.gitignore対象）
- **task_ledger.md**: 親のみが更新（.gitignore対象）
- **workorders/TASK-XXX.md**: 子が作成・コミット（git追跡対象）

詳細: `references/context_persistence_ja.md`

### ワークオーダー

子は起動時にワークオーダーファイルを作成:

```text
.orchestrating-agents/workorders/TASK-XXX.md
```

テンプレート: `assets/templates/workorder_template_ja.md`

## セッションレジューム

セッションリミット等で停止した場合、ユーザーが「再開して」と指示するだけで全エージェントをレジューム可能。

### レジュームフロー

```text
1. ユーザー: 「再開して」
2. 親: .orchestrating-agents/session_state.md を読み込み
3. 親: mission.md を読み込み（目標の復元）
4. 親: task_ledger.md を読み込み（キュー状態の復元）
5. 親: 停止していた子を Agent tool(resume: agent_id) で再開
6. 子: workorders/TASK-XXX.md を読み込み（作業状態の復元）
7. 子: 停止していた孫を Agent tool(resume: agent_id) で再開
```

テンプレート: `assets/templates/session_state_template_ja.md`
詳細: `references/session_resume_ja.md`

## 通信プロトコル

### 親→子 指示フォーマット

```markdown
## Task Instruction
task_id: <ID>
task_type: <スキル種別>

## Objective
<目的と期待成果物>

## Context
<プロジェクト情報、前フェーズ成果物パス>

## Constraints
- escalation_policy: <エスカレーション基準>
- approval_authority: <代理承認範囲>
```

### 子→親 報告フォーマット

```markdown
## Task Report
task_id: <ID>
status: <completed | failed | escalation_required>

## Results
<成果物概要、作成ファイルリスト>

## Escalations (if any)
- type: <approval_needed | risk_warning | blocker>
  description: <内容>
```

テンプレート: `assets/templates/report_template_ja.md`

### 子→孫 指示フォーマット

テンプレート: `assets/templates/child_prompt_template_ja.md`

## SDDスキルへの適用

| サブスキル | 階層モード | 理由 |
|-----------|-----------|------|
| requirements-defining | 2階層 | 単一作業、並列化不要 |
| software-designing | 2階層 | 同上 |
| task-planning | 2階層 | 同上 |
| task-executing | 3階層 | 複数タスクの並列実行が可能 |
| sdd-troubleshooting | 条件分岐 | 仮説3つ以上なら3階層 |
| sdd-document-management | 3階層 | フルスキャン時に5機能を並列実行 |

## リソース

### リファレンス（progressive disclosure）

- 3階層プロトコル: `references/hierarchy_protocol_ja.md`
- キュー管理仕様: `references/queue_management_ja.md`
- エスカレーション方針: `references/escalation_policy_ja.md`
- 軌道変更メカニズム: `references/course_correction_ja.md`
- コンテキスト永続化: `references/context_persistence_ja.md`
- セッションレジューム: `references/session_resume_ja.md`

### テンプレート

- 親→子 指示: `assets/templates/parent_prompt_template_ja.md`
- 子→孫 指示: `assets/templates/child_prompt_template_ja.md`
- 報告フォーマット: `assets/templates/report_template_ja.md`
- ミッションファイル: `assets/templates/mission_template_ja.md`
- タスク台帳: `assets/templates/task_ledger_template_ja.md`
- ワークオーダー: `assets/templates/workorder_template_ja.md`
- セッション状態: `assets/templates/session_state_template_ja.md`
