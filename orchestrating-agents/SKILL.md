---
name: orchestrating-agents
description: Orchestrates multi-step tasks autonomously using a 3-tier agent hierarchy (Director/Manager/Worker). Use when user says "run this end-to-end", "handle everything", "execute all tasks", or needs parallel task execution with queuing, course correction, and session resume. Provides FIFO task queue, escalation policy, git worktree isolation, and context persistence across agent sessions.
metadata:
  version: "1.0.0"
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

### 必須起動チェックリスト

起動時に以下の全ステップを順に実行すること。**スキップ禁止**。

```text
□ 1. 環境準備: .orchestrating-agents/ ディレクトリ作成 + .gitignore 更新（環境準備の最初に実施）
□ 2. ミッション定義: mission.md を作成（テンプレート必須参照）
□ 3. タスク分解: TaskCreate でキュー登録 + task_ledger.md を作成（テンプレート必須参照）
□ 4. セッション状態初期化: session_state.md を作成（テンプレート必須参照）
□ 5. 子セッション起動: general-purpose型で子を起動（テンプレート必須参照）
□ 6. キュー処理: FIFOでタスクを順次実行
```

### 1. 環境準備

```text
1. .orchestrating-agents/ ディレクトリを作成（存在しなければ）
2. .gitignore に以下のパターンを追加（未登録の場合）:
   .orchestrating-agents/mission.md
   .orchestrating-agents/task_ledger.md
   .orchestrating-agents/session_state.md
   .orchestrating-agents/archive/
```

**注意**: .gitignore の更新はディレクトリ作成直後、環境準備の最初に実施すること。後回しにしない。

### 2. ミッション定義

ユーザーの指示を受けたら、**テンプレートを読み込んでから** `.orchestrating-agents/mission.md` を作成:

```text
1. orchestrating-agents/assets/templates/mission_template_ja.md を Read ツールで読み込む（必須）
2. ユーザーの原文指示を保存
3. 目標・成功基準を解釈・記録
4. 実行計画を策定
```

テンプレート: `orchestrating-agents/assets/templates/mission_template_ja.md`

### 3. タスク分解とキュー登録

```text
1. 指示をタスクに分解
2. TaskCreate で各タスクをpending状態で登録
3. orchestrating-agents/assets/templates/task_ledger_template_ja.md を Read ツールで読み込む（必須）
4. .orchestrating-agents/task_ledger.md にタスク台帳を作成
5. 依存関係を分析し、実行順序を決定
```

テンプレート: `orchestrating-agents/assets/templates/task_ledger_template_ja.md`

### 4. セッション状態初期化

```text
1. orchestrating-agents/assets/templates/session_state_template_ja.md を Read ツールで読み込む（必須）
2. .orchestrating-agents/session_state.md を作成（親セッション情報を記録）
```

テンプレート: `orchestrating-agents/assets/templates/session_state_template_ja.md`

### 5. 子セッション起動

```text
Agent tool(
  subagent_type: "general-purpose",    # 必ず general-purpose を使用
  name: "child-<task-type>",
  run_in_background: true,
  isolation: "worktree",  # 並列実行時
  prompt: <親→子 指示フォーマット>
)
```

**重要**: 子は必ず `subagent_type: "general-purpose"` で起動すること。子が孫を起動する3階層モードでは Agent tool へのアクセスが必須であり（= tools に Agent が必要）、general-purpose 型はこの要件を確実に満たす。一貫性と確実性のため general-purpose に統一する。

テンプレート: `orchestrating-agents/assets/templates/parent_prompt_template_ja.md`（**Read ツールで読み込んでから使用**）

### 6. キュー処理（FIFO）

```text
1. TaskList でpendingの最古タスクを取得
2. 子セッションを起動して実行
3. 完了後、task_ledger.md を更新
4. session_state.md を更新（子セッション情報を反映）
5. 次のpendingタスクへ
```

詳細: `orchestrating-agents/references/queue_management_ja.md`

## 軌道変更メカニズム

Agent toolの `name` パラメータで子セッションに名前を付けて起動し、`SendMessage` で進行中の子に方針変更を伝達:

```text
1. 親: Agent tool(name: "child-task-exec", run_in_background: true) で子を起動
2. ユーザー: 方針変更を親に伝える
3. 親: SendMessage(to: "child-task-exec", message: 方針変更内容) で子に伝達
4. 子: 受信した変更を反映して作業を調整
5. 親: task_ledger.md の軌道変更履歴に記録
```

詳細: `orchestrating-agents/references/course_correction_ja.md`

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

詳細: `orchestrating-agents/references/escalation_policy_ja.md`

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

### マージ後の検証（必須）

worktreeマージ後、親は以下の検証を必ず実行すること:

```text
1. git diff HEAD~1..HEAD --name-only で全変更ファイルを一覧し、テスト関連以外の変更を確認
   → マージ直後にリポジトリルートで実行すること
   → テストファイルの判定基準: *.test.*, *_test.*, *_spec.*, __tests__/, test/, tests/ 配下
   （子に変更対象の制約を課している場合に使用。例: テストファイルのみ変更可、特定ディレクトリのみ変更可）
   （制約がない場合でも、意図しない変更の検出のため常に実行を推奨）
2. 差分に想定外のプロダクションコード変更がないか確認
   → 違反の例: 子の変更範囲外のファイル変更、削除されたファイル、新規依存関係の追加
   → 制約範囲は親→子指示の Constraints セクションで定義される
3. 全体テスト・ビルドを実行して統合問題を検出
   → 必須revert: コンパイルエラー、テスト失敗、型エラー
   → 判断による: lint警告のみの場合はrevert不要だが修正タスクを追加
4. 問題があれば git revert で該当マージを取り消し、子に制約を再度明示して再指示
```

**注意**: 子エージェントが制約を破ってプロダクションコードを変更するケースがある。マージ後の差分チェックを怠ると、PRレビューまで検知できない。ステップ1-2で変更が検出された場合は、ステップ3のテスト結果に関わらずrevertを検討すること。

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

詳細: `orchestrating-agents/references/context_persistence_ja.md`

### ワークオーダー

子は起動時にワークオーダーファイルを作成:

```text
1. orchestrating-agents/assets/templates/workorder_template_ja.md を Read ツールで読み込む（必須）
2. .orchestrating-agents/workorders/TASK-XXX.md にテンプレートに従って作成
```

テンプレート: `orchestrating-agents/assets/templates/workorder_template_ja.md`

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

テンプレート: `orchestrating-agents/assets/templates/session_state_template_ja.md`
詳細: `orchestrating-agents/references/session_resume_ja.md`

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

テンプレート: `orchestrating-agents/assets/templates/report_template_ja.md`

### 子→孫 指示フォーマット

テンプレート: `orchestrating-agents/assets/templates/child_prompt_template_ja.md`

## SDDスキルへの適用

| サブスキル | 階層モード | 理由 |
|-----------|-----------|------|
| requirements-defining | 2階層 | 単一作業、並列化不要 |
| software-designing | 2階層 | 同上 |
| task-planning | 2階層 | 同上 |
| task-executing | 3階層 | 複数タスクの並列実行が可能 |
| sdd-troubleshooting | 条件分岐 | 仮説3つ以上なら3階層 |
| sdd-document-management | 3階層 | フルスキャン時に5機能を並列実行 |

## テンプレート使用ルール（必須）

**テンプレートは「使用する直前にReadツールで読み込む」こと。独自フォーマットでの作成は禁止。**

| ファイル | テンプレート | タイミング |
|---------|------------|----------|
| mission.md | `orchestrating-agents/assets/templates/mission_template_ja.md` | 起動時 |
| task_ledger.md | `orchestrating-agents/assets/templates/task_ledger_template_ja.md` | 起動時 |
| session_state.md | `orchestrating-agents/assets/templates/session_state_template_ja.md` | 起動時 |
| 親→子 指示 | `orchestrating-agents/assets/templates/parent_prompt_template_ja.md` | 子セッション起動時 |
| 子→親 報告 | `orchestrating-agents/assets/templates/report_template_ja.md` | 子セッション完了時 |
| workorder | `orchestrating-agents/assets/templates/workorder_template_ja.md` | 子セッション内で起動時 |
| 子→孫 指示 | `orchestrating-agents/assets/templates/child_prompt_template_ja.md` | 孫セッション起動時 |

**注意**: 上記パスはReadツールに渡すフルパスです。リファレンスドキュメント内の短縮パス表記は説明用であり、実際のRead実行時は常にフルパスを使用してください。

## リソース

### リファレンス（progressive disclosure）

- 3階層プロトコル: `orchestrating-agents/references/hierarchy_protocol_ja.md`
- キュー管理仕様: `orchestrating-agents/references/queue_management_ja.md`
- エスカレーション方針: `orchestrating-agents/references/escalation_policy_ja.md`
- 軌道変更メカニズム: `orchestrating-agents/references/course_correction_ja.md`
- コンテキスト永続化: `orchestrating-agents/references/context_persistence_ja.md`
- セッションレジューム: `orchestrating-agents/references/session_resume_ja.md`

### テンプレート

- 親→子 指示: `orchestrating-agents/assets/templates/parent_prompt_template_ja.md`
- 子→孫 指示: `orchestrating-agents/assets/templates/child_prompt_template_ja.md`
- 報告フォーマット: `orchestrating-agents/assets/templates/report_template_ja.md`
- ミッションファイル: `orchestrating-agents/assets/templates/mission_template_ja.md`
- タスク台帳: `orchestrating-agents/assets/templates/task_ledger_template_ja.md`
- ワークオーダー: `orchestrating-agents/assets/templates/workorder_template_ja.md`
- セッション状態: `orchestrating-agents/assets/templates/session_state_template_ja.md`
