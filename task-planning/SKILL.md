---
name: task-planning
description: 設計書から実装タスクを分解・管理する。「タスクを計画して」「設計からタスクに分解して」「実装計画を立てて」等の依頼時に使用。AIエージェント向けの具体的な実装指示とTDD手順を定義し、requirements/design/との整合性を逆順レビューで確認する。
metadata:
  version: "1.0.0"
---

# タスク計画スキル

設計書を基に、AIエージェントが実行可能な具体的なタスクに分解する。

## 成果物

```text
docs/sdd/tasks/
├── index.md                 # 目次・進捗サマリ・並列実行グループ
├── phase-1/
│   ├── TASK-001.md          # タスク詳細
│   └── TASK-002.md
└── phase-2/
    └── TASK-003.md
```

## 前提条件

docs/sdd/requirements/、docs/sdd/design/が存在する場合は読み込み、タスクとの整合性を確認する。

## タスク粒度の目安

| 分類 | 作業時間 | 内容例 |
|------|----------|--------|
| シンプル | 10-20分 | 単一ファイル作成、基本関数実装 |
| 標準 | 20-40分 | 複数ファイル、APIエンドポイント |
| 複雑 | 40-90分 | 複数コンポーネント統合 |
| 要分解 | 90分以上 | さらに小さいタスクに分解 |

## タスク定義の必須要素

各タスクには以下を必ず含める:

- **対象ファイルパス**: 絶対パスで記載
- **実装詳細**: 使用技術・ライブラリ、関数シグネチャ、型定義
- **情報の明確性**: 「明示された情報」と「不明/要確認の情報」を分離
- **TDD手順**: テスト作成 → 失敗確認 → テストコミット → 実装 → 通過確認 → 実装コミット
- **受入基準**: テスト可能な具体的条件
- **依存関係**: 他タスクとの依存
- **推定工数・ステータス**: TODO/IN_PROGRESS/DONE/BLOCKED/REVIEW

推測に基づく実装指示は含めない。不明な情報は「不明」として明記する。

## ワークフロー

### 新規作成フロー

1. **ドキュメント確認**: requirements/、design/を読み込む
2. **情報分類**: 明示された情報と不明な情報を分類。不明点があればユーザーに確認
3. **フェーズ分け**: 作業を論理的なフェーズに分割
4. **タスク分解**: 各フェーズのタスクを `phase-N/TASK-XXX.md` として作成
5. **index.md作成**: 目次・進捗サマリ・並列実行グループを記述
6. **逆順レビュー**: タスク → 設計 → 要件の整合性確認
7. **TodoWrite同期**: タスク一覧をTodoWriteに同期
8. **ユーザー確認**: 承認を得て完了

### タスク追加フロー

1. `phase-N/TASK-XXX.md` を作成
2. index.mdのタスク一覧テーブルにリンクを追加
3. 依存関係を更新

## エージェントチーム向け設計

タスク計画時は常に並列実行を前提として設計する。ただし並列化のためだけに過剰に分割しない。

### 設計原則

1. **ファイル独立性（最重要）**: 各タスクが異なるファイルセットを対象とする。同一ファイルを複数タスクが編集する設計は禁止
2. **並列実行グループの明示**: index.mdに並列実行可能なタスクグループを明記
3. **コンテキストの完全性**: 各タスクがスポーンプロンプトだけで実行できるよう、対象ファイル絶対パス・設計ドキュメントパス・技術スタック・テスト要件を記載

### index.mdでの並列実行グループ記載例

```markdown
## 並列実行グループ

### グループA（並列実行可能）
| タスク | 対象ファイル | 依存 |
|--------|-------------|------|
| TASK-001 | src/auth/** | なし |
| TASK-002 | src/api/** | なし |
| TASK-003 | src/models/** | なし |

### グループB（グループA完了後）
| タスク | 対象ファイル | 依存 |
|--------|-------------|------|
| TASK-004 | src/services/auth-service.ts | TASK-001 |
| TASK-005 | src/services/api-service.ts | TASK-002 |
```

詳細は [sdd-documentation/references/agent_teams_guide_ja.md](../sdd-documentation/references/agent_teams_guide_ja.md) を参照。

## 逆順レビュー

タスク → 設計 → 要件の整合性を確認する。詳細チェック項目は [sdd-documentation/references/checklist_ja.md](../sdd-documentation/references/checklist_ja.md) を参照。不整合発見時はリストアップしてユーザーに確認してから修正する。

## タスク同期（TodoWrite連携）

タスク計画完了時にTodoWriteへ同期する。詳細は [sdd-documentation/references/task_sync_guide_ja.md](../sdd-documentation/references/task_sync_guide_ja.md) を参照。

## 検証チェックリスト

- [ ] タスクが適切な粒度に分解されている（20-40分程度）
- [ ] 各タスクに受入基準がある
- [ ] 各タスクの「情報の明確性」セクションが記載されている
- [ ] 推測に基づく実装指示が含まれていない
- [ ] TDD手順が含まれている
- [ ] すべてのタスクがdesign/のコンポーネント/APIに対応している
- [ ] 並列実行グループが明示されている
- [ ] TodoWriteにタスク一覧が同期されている

## リソース

### テンプレート
- 目次: [assets/templates/tasks_index_template_ja.md](assets/templates/tasks_index_template_ja.md)
- タスク詳細: [assets/templates/task_detail_template_ja.md](assets/templates/task_detail_template_ja.md)

### リファレンス
- タスクガイドライン: [references/task_guidelines_ja.md](references/task_guidelines_ja.md)

### 命名規則

| ファイル種別 | 命名規則 | 例 |
|-------------|---------|-----|
| フェーズ | `phase-N` | `phase-1` |
| タスク | `TASK-XXX.md` | `TASK-001.md` |

タスクIDはプロジェクト全体で一意。フェーズをまたいでも連番を維持。

### リンク形式

index.mdでは `[詳細](phase-1/TASK-001.md) @phase-1/TASK-001.md` のようにマークダウン形式と@形式を併記する。
