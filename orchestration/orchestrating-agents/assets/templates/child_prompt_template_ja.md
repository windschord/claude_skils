# 子→孫 指示テンプレート

以下のフォーマットで子が孫セッションに指示を出す。

---

## Work Assignment
parent_task_id: {{TASK-XXX（親タスクID）}}
subtask_id: {{TASK-XXXa（サブタスクID）}}
worker_type: {{エージェント型（例: task-executing）}}

## Work Description
{{具体的な作業内容}}

## Target Files
{{対象ファイルのリスト}}

## Acceptance Criteria
{{受入基準のリスト}}

## Technical Context
{{実装に必要な技術的情報}}
{{依存関係}}
{{参照すべきドキュメント}}

## Completion Protocol
1. 受入基準をすべて確認すること
2. 作業完了後、以下の形式で報告すること:
   - 完了ステータス
   - 変更ファイルリスト
   - 受入基準の達成状況
3. エラー発生時は詳細を報告し、リトライ指示を待つこと

---

## 使用例

Work Assignment
parent_task_id: TASK-005
subtask_id: TASK-005a
worker_type: task-executing

Work Description
ユーザー認証APIのエンドポイントを実装する

Target Files
- src/api/auth.ts
- src/api/auth.test.ts

Acceptance Criteria
- POST /api/auth/login エンドポイントが動作する
- JWTトークンを返す
- テストがパスする

Technical Context
- フレームワーク: Express.js
- 認証: JWT (jsonwebtoken)
- 参照: docs/sdd/design/api/auth.md
