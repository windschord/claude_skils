# セッションレジューム手順

## 概要

セッションリミットやネットワーク切断等でエージェントセッションが停止した場合、ユーザーが「再開して」と指示するだけで全エージェントの状態を復元し、作業を継続する。本ドキュメントでは session_state.md の構造、更新タイミング、レジュームフロー、フォールバック手順を詳述する。

---

## session_state.md の構造

### 全体構造

```markdown
# Session State

## 親セッション
- status: <active | paused | completed>
- current_task: <現在処理中のタスクID、またはnull>
- last_updated: <タイムスタンプ>

## 子セッション
### child-task-exec
- name: child-task-exec
- agent_id: <Agent toolが返すID>
- status: <active | paused | completed | failed>
- task: TASK-003
- worktree_branch: worktree-child-task-exec
- last_updated: <タイムスタンプ>

### child-design
- name: child-design
- agent_id: <Agent toolが返すID>
- status: completed
- task: TASK-001
- worktree_branch: worktree-child-design
- last_updated: <タイムスタンプ>

## 孫セッション
### worker-impl-api
- parent: child-task-exec
- agent_id: <Agent toolが返すID>
- status: <active | paused | completed | failed>
- work: TASK-003-W01
- worktree_branch: worktree-worker-impl-api
- last_updated: <タイムスタンプ>

### worker-impl-ui
- parent: child-task-exec
- agent_id: <Agent toolが返すID>
- status: active
- work: TASK-003-W02
- worktree_branch: worktree-worker-impl-ui
- last_updated: <タイムスタンプ>
```

### フィールド説明

**親セッション:**

| フィールド | 説明 |
|-----------|------|
| status | 親セッションの状態。active（稼働中）、paused（一時停止）、completed（全タスク完了） |
| current_task | 現在処理中のタスクID。キュー処理中でなければ null |
| last_updated | 最後に更新した日時 |

**子セッション:**

| フィールド | 説明 |
|-----------|------|
| name | Agent tool の name パラメータで指定した名前 |
| agent_id | Agent tool が返すセッション識別子。resume 時に使用 |
| status | active（稼働中）、paused（一時停止）、completed（完了）、failed（失敗） |
| task | 担当タスクID |
| worktree_branch | 使用している Git Worktree のブランチ名 |
| last_updated | 最後に更新した日時 |

**孫セッション:**

| フィールド | 説明 |
|-----------|------|
| parent | 親となる子セッションの name |
| agent_id | Agent tool が返すセッション識別子。resume 時に使用 |
| status | active（稼働中）、paused（一時停止）、completed（完了）、failed（失敗） |
| work | 担当作業ID（TASK-XXX-W01 形式） |
| worktree_branch | 使用している Git Worktree のブランチ名 |
| last_updated | 最後に更新した日時 |

---

## session_state.md の更新タイミング

### 子セッション関連

| イベント | 更新内容 |
|---------|---------|
| 子の起動時 | 子セッションエントリを追加。status: active, agent_id を記録 |
| 子のステータス変更時 | status フィールドを更新 |
| 子の完了時 | status: completed に更新 |
| 子の失敗時 | status: failed に更新 |

### 孫セッション関連

| イベント | 更新内容 |
|---------|---------|
| 孫の起動時 | 孫セッションエントリを追加。parent, agent_id, status: active を記録 |
| 孫のステータス変更時 | status フィールドを更新 |
| 孫の完了時 | status: completed に更新 |
| 孫の失敗時 | status: failed に更新 |

### 更新者

- **親セッション情報**: 親が更新
- **子セッション情報**: 親が更新（子の起動・完了は親が検知するため）
- **孫セッション情報**: 子が workorder 内で管理し、マージ時に親が session_state.md に反映

---

## レジュームフロー

### 標準レジュームフロー

```text
1. ユーザー: 「再開して」
2. 親: .orchestrating-agents/session_state.md を読み込み
   → 子・孫のセッション情報（name, agent_id, status）を確認
3. 親: .orchestrating-agents/mission.md を読み込み
   → ユーザーの原文指示、目標、実行計画を復元
4. 親: .orchestrating-agents/task_ledger.md を読み込み
   → キュー状態（進行中/待機/完了）を復元
5. 親: 停止していた子を再開
   → Agent tool(resume: <agent_id>) で子セッションを再開
6. 子: .orchestrating-agents/workorders/TASK-XXX.md を読み込み
   → 親の指示内容、作業分解、孫の進捗状態を復元
7. 子: 停止していた孫を再開
   → Agent tool(resume: <agent_id>) で孫セッションを再開
8. 全エージェントが作業を再開
```

### レジューム時の状態復元詳細

**ステップ2: session_state.md の解析**

```text
- status: active の子セッションを特定 → 再開対象
- status: completed の子セッションはスキップ
- status: failed の子セッションは再起動が必要か判断
- status: paused の子セッションは再開対象
```

**ステップ5: 子セッションの再開**

```text
- session_state.md から agent_id を取得
- Agent tool(resume: <agent_id>) で再開を試みる
- 再開成功: 子が workorder を読み込んで作業を継続
- 再開失敗: フォールバック手順へ（後述）
```

**ステップ7: 孫セッションの再開**

```text
- 子が workorder から孫の情報を確認
- active/paused の孫に対して Agent tool(resume: <agent_id>) で再開を試みる
- 再開成功: 孫が作業を継続
- 再開失敗: 子が新しい孫を起動して残作業を引き継ぐ
```

---

## agent_id が無効な場合のフォールバック

### 無効になる原因

- セッション期限切れ（一定時間経過後にセッションが破棄される）
- サーバー側のリソース回収
- ネットワーク障害による接続断

### フォールバック手順

```text
1. Agent tool(resume: <agent_id>) が失敗
2. セッションが復元不可能と判断

--- 子セッションの場合 ---
3. 親が新しい子セッションを起動:
   Agent tool(
     subagent_type: "general-purpose",
     name: "<同じname>",
     run_in_background: true,
     isolation: "worktree",
     prompt: <再開用プロンプト>
   )
4. 再開用プロンプトに以下を含める:
   - workorder のパス: .orchestrating-agents/workorders/TASK-XXX.md
   - 「このワークオーダーを読み込み、未完了の作業から再開してください」という指示
   - 前回の worktree ブランチ情報（存在すれば同じブランチを使用）
5. 新しい子が workorder を読み込み、未完了の作業を特定
6. 未完了の作業から実行を再開

--- 孫セッションの場合 ---
3. 子が新しい孫セッションを起動:
   Agent tool(
     subagent_type: "<task-type>",
     name: "<同じname>",
     prompt: <再開用プロンプト>
   )
4. 再開用プロンプトに以下を含める:
   - 作業内容（workorder の該当作業セクション）
   - 完了済みの成果物パス（あれば）
   - 「前回の作業の続きから再開してください」という指示
5. 新しい孫が未完了部分から作業を再開
```

### Worktree の復旧

```text
1. 前回の worktree ブランチが残っている場合:
   - 同じブランチで新セッションを起動
   - 前回のコミット済み作業が保持されている

2. 前回の worktree ブランチが削除されている場合:
   - メインブランチから新しい worktree を作成
   - マージ済みの成果物はメインブランチに反映されているため、未マージ分のみ再実行
```

### session_state.md の更新

```text
1. 新しいセッションの agent_id で session_state.md を更新
2. status を active に戻す
3. last_updated を更新
```

---

## レジューム時の整合性チェック

レジューム実行前に、以下の整合性を確認する:

```text
1. mission.md が存在するか
   → 存在しない場合: レジューム不可。ユーザーに再指示を依頼
2. task_ledger.md が存在するか
   → 存在しない場合: mission.md から再構築を試みる
3. session_state.md が存在するか
   → 存在しない場合: task_ledger.md から状態を推定
4. workorder ファイルが存在するか
   → 存在しない場合: task_ledger.md の情報をもとに再作成
5. 成果物ファイルの存在確認
   → 完了済みタスクの成果物が存在するか確認
   → 存在しない場合: 当該タスクを再実行対象に含める
```

---

## レジューム時のユーザーへの報告

レジューム開始時に、親はユーザーに現在の状態を報告する:

```text
[orchestrating-agents] セッションレジューム

ミッション: <目標の要約>

状態:
- 完了済み: N タスク
- 進行中: N タスク（再開中）
- 待機中: N タスク

再開するタスク:
- TASK-XXX: <タスク概要>（子セッション再開）
- TASK-YYY: <タスク概要>（新規セッションで再開）

続行しますか?
```
