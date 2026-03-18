# 親→子 指示テンプレート

以下のフォーマットで親が子セッションに指示を出す。

---

## Task Instruction
task_id: {{TASK-XXX}}
task_type: {{スキル種別（例: task-executing, requirements-defining）}}

## Objective
{{目的と期待成果物の詳細}}

## Context
{{プロジェクト情報}}
{{前フェーズの成果物パス}}
{{関連ドキュメントへの参照}}

## Constraints
- escalation_policy: {{エスカレーション基準の要約}}
- approval_authority: {{代理承認の範囲}}
- worktree: {{worktree使用有無}}

## Persistence
- workorder_path: .orchestrating-agents/workorders/{{TASK-XXX}}.md
- session_state_path: .orchestrating-agents/session_state.md

## Instructions
1. まず orchestrating-agents/assets/templates/workorder_template_ja.md を Read ツールで読み込むこと（必須）
2. workorder_pathにワークオーダーファイルをテンプレートに従って作成すること（スキップ禁止）
3. 作業完了後、orchestrating-agents/assets/templates/report_template_ja.md を Read ツールで読み込み、報告フォーマットに従って親に報告すること
4. 3階層モードで孫を起動する場合、orchestrating-agents/assets/templates/child_prompt_template_ja.md を Read ツールで読み込むこと
5. コンテキスト圧縮が発生した場合、workorder_pathを再読み込みすること

---

## 使用例

### 2階層モード（子が直接実務）

Task Instruction
task_id: TASK-001
task_type: requirements-defining

Objective
ユーザー認証機能の要件定義書を作成する

Context
プロジェクト: Webアプリケーション
前フェーズ: なし（新規開発）
関連: docs/sdd/requirements/

Constraints
- escalation_policy: 要件の曖昧さがあればエスカレーション
- approval_authority: テンプレート選択、ファイル命名は代理承認可
- worktree: false

### 3階層モード（子が孫に委譲）

Task Instruction
task_id: TASK-005
task_type: task-executing

Objective
Phase-2のタスク群（TASK-005a, TASK-005b, TASK-005c）を並列実行する

Context
プロジェクト: Webアプリケーション
前フェーズ: docs/sdd/tasks/phase-2/
関連: docs/sdd/design/components/

Constraints
- escalation_policy: ファイル削除・仕様変更はエスカレーション
- approval_authority: 技術的トレードオフ、リトライは代理承認可
- worktree: true（各孫をisolation: "worktree"で起動）
