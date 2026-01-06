---
name: task-executing
description: docs/tasks/に記載されたタスクを実行し、実装を行います。タスクごとにステータス更新とコミットを作成し、実装完了後は逆順レビュー（実装→タスク→設計→要件）で整合性を確認します。SDDワークフローの実装フェーズで使用してください。
version: "1.0.0"
---

# タスク実行スキル

docs/tasks/に記載されたタスクを実行し、SDDワークフローに沿った実装を行います。

## 概要

このスキルは、SDDワークフローの実装フェーズを担当します：

```text
requirements-defining → software-designing → task-planning → task-executing
   (requirements/)         (design/)           (tasks/)         (実装)
```

### 主な機能
- docs/tasks/からタスクを読み取り、実行順序を決定
- タスクごとのステータス更新（TODO → IN_PROGRESS → DONE）
- 統一されたコミットテンプレートによるGit管理
- 実装後の逆順レビュー（実装→タスク→設計→要件の整合性確認）
- 並列実行可能なタスクの並列処理

## このスキルを使用する場面

### 実装フェーズ
- docs/tasks/のタスクを実行する場合
- SDDに沿った実装を行う場合
- タスクの進捗を管理したい場合

### SDDワークフロー統合
- sdd-documentationスキルから呼び出される場合
- 実装後の整合性確認が必要な場合

## ワークフロー

```text
1. docs/tasks/index.md読み取り
   ↓
2. 実行可能なタスクを特定（TODO状態、依存関係解消済み）
   ↓
3. 個別タスクファイルを読み込み
   ↓
4. ステータスをIN_PROGRESSに更新・コミット
   ↓
5. サブエージェントで実装
   ↓
6. 受入基準の確認
   ↓
7. コミット作成（テンプレート使用）
   ↓
8. ステータスをDONEに更新・コミット
   ↓
9. 逆順レビュー
   ↓
10. 次のタスクへ（または完了）
```

## タスクステータス管理

### ステータス遷移

```text
TODO → IN_PROGRESS → DONE
         ↓
      BLOCKED（問題発生時）
```

### 更新タイミング

| タイミング | ステータス | アクション |
|-----------|-----------|-----------|
| タスク開始時 | `IN_PROGRESS` | タスクファイルとindex.mdを更新、コミット |
| タスク完了時 | `DONE` | 完了サマリー追加、更新、コミット |
| 問題発生時 | `BLOCKED` | ブロック理由を記載 |

## 逆順レビュー

### レビューの流れ

```text
実装 → docs/tasks/ → docs/design/ → docs/requirements/
```

### 主要チェック項目

1. **実装 → タスク**: 受入基準達成、ファイル一致、テスト通過
2. **タスク → 設計**: コンポーネント/API/データモデル対応
3. **設計 → 要件**: 要件カバレッジ、過剰実装チェック

詳細は `references/execution_guide_ja.md` を参照。

## ベストプラクティス

1. **タスク開始時に必ずステータス更新**: IN_PROGRESSに変更してからコミット
2. **コミットテンプレートを厳守**: 関連ドキュメントへの参照を必ず含める
3. **受入基準を全て確認**: 一部でも未達成なら完了としない
4. **逆順レビューを省略しない**: 整合性確認で問題を早期発見
5. **絵文字を使用しない**: コミットメッセージ、ドキュメント全てで禁止

## SDDワークフローとの統合

sdd-documentationスキルは、以下の順序でサブスキルを呼び出します：

```text
1. requirements-defining → docs/requirements/作成
2. software-designing → docs/design/作成
3. task-planning → docs/tasks/作成
4. task-executing → 実装＆逆順レビュー（このスキル）
```

### 完了条件

- すべてのタスクがDONEステータス
- 逆順レビューで不整合がない（または解消済み）
- すべてのコミットが作成済み

## リソース

### リファレンス
- コミットテンプレート: `references/commit_templates_ja.md`
- 実行ガイド: `references/execution_guide_ja.md`
