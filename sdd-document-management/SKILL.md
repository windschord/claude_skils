---
name: sdd-document-management
description: SDDドキュメントの整合性チェック、実装同期確認、アーカイブ、ファイル最適化を行う。「ドキュメントの整合性をチェックして」「実装と同期確認して」「完了タスクをアーカイブして」「ファイルが大きすぎる」等の依頼時に使用。ドキュメント間の矛盾検出、実装との乖離確認、完了タスクの整理、肥大化ファイルの分割に対応する。
metadata:
  version: "1.0.0"
---

# SDDドキュメント管理スキル

SDDドキュメントのメンテナンス・整理を行い、品質と一貫性を維持する。

## 4つの機能

| 問題 | 解決機能 | 詳細リファレンス |
|------|----------|-----------------|
| ドキュメント間の仕様矛盾 | 整合性チェック | [references/consistency_check_ja.md](references/consistency_check_ja.md) |
| 実装とドキュメントの乖離 | 実装同期チェック | [references/sync_check_ja.md](references/sync_check_ja.md) |
| 完了済みタスクの蓄積 | アーカイブ | [references/archive_ja.md](references/archive_ja.md) |
| ファイルの肥大化 | ファイル最適化 | [references/optimize_ja.md](references/optimize_ja.md) |

### 共通原則

すべての操作で **チェック → レポート出力 → ユーザー承認 → 修正実行** の順序を守る。

## 機能1: 整合性チェック

requirements、design、tasks間の矛盾や不整合を検出する。
- 要件→設計の整合性（カバレッジ、過剰設計、用語一貫性）
- 設計→タスクの整合性（カバレッジ、タスク過不足、参照正確性）
- クロスリファレンス（ID参照有効性、ファイル参照、ステータス整合）

## 機能2: 実装同期チェック

実装コードとドキュメントの乖離を検出する。
- API同期（エンドポイント、リクエスト/レスポンス、HTTPメソッド）
- データベース同期（テーブル、カラム、リレーション）
- コンポーネント同期（インターフェース、公開メソッド、依存関係）
- 乖離の分類: ドキュメント古い / 実装漏れ / 未文書化

## 機能3: アーカイブ

完了済みタスクや古い決定事項をアーカイブディレクトリに移動する。
- 完了タスク → docs/sdd/archive/tasks/phase-N/
- 古い決定事項 → docs/sdd/archive/decisions/
- 完了トラブルシューティング → docs/sdd/archive/troubleshooting/
- ファイル移動時にインデックス更新と参照リンク更新を行う

## 機能4: ファイル最適化

肥大化ファイルの分割や重複内容の統合を提案する。
- サイズ: 500行未満=正常、500-1000行=注意、1000行以上=要対応
- セクション数: 10未満=正常、10-20=注意、20以上=要対応
- 重複: 類似度30%未満=軽微、30-50%=注意、50%以上=要対応

## ユーザー対話

### スキル起動時

```text
SDDドキュメント管理を開始します。どの機能を実行しますか？

1. 整合性チェック - ドキュメント間の矛盾を検出
2. 実装同期チェック - 実装とドキュメントの乖離を検出
3. アーカイブ - 完了タスク・古い決定事項を整理
4. ファイル最適化 - 肥大化ファイルの分割・重複統合
5. フルスキャン - 上記すべてをAgent toolで並列実行
```

### フルスキャン時のAgent tool並列実行（必須）

フルスキャンが選択された場合、Agent tool（`isolation: worktree`）で4機能を並列実行する。1つのメッセージで4つのAgent toolを同時に呼び出し、各サブエージェントはレポート作成のみ行う。メインセッションで結果を統合後にユーザー承認を得る。修正は順次実行（ファイル競合回避）。

詳細は [sdd-documentation/references/agent_teams_guide_ja.md](../sdd-documentation/references/agent_teams_guide_ja.md) を参照。

## 成果物の保存

```text
docs/sdd/reports/
├── consistency/[YYYY-MM-DD].md
├── sync/[YYYY-MM-DD].md
├── archive/[YYYY-MM-DD].md
└── optimize/[YYYY-MM-DD].md
```

## 推奨実行タイミング

| タイミング | 推奨機能 |
|-----------|---------|
| フェーズ完了時 | アーカイブ、ファイル最適化 |
| リリース前 | フルスキャン |
| 仕様変更後 | 整合性チェック |
| 大規模実装後 | 実装同期チェック |

## TodoWrite連携

- アーカイブ時: TodoWriteからも該当タスクを除外
- 整合性チェックによるタスク追加時: `[TASK-XXX] [DocFix] 修正内容` の形式でpendingとして追加

## リソース

### リファレンス
- 管理ガイドライン: [references/management_guide_ja.md](references/management_guide_ja.md)
- 整合性チェック: [references/consistency_check_ja.md](references/consistency_check_ja.md)
- 実装同期チェック: [references/sync_check_ja.md](references/sync_check_ja.md)
- アーカイブ: [references/archive_ja.md](references/archive_ja.md)
- ファイル最適化: [references/optimize_ja.md](references/optimize_ja.md)

### テンプレート
- 整合性チェックレポート: [assets/templates/consistency_report_template_ja.md](assets/templates/consistency_report_template_ja.md)
- 実装同期チェックレポート: [assets/templates/sync_report_template_ja.md](assets/templates/sync_report_template_ja.md)
- アーカイブレポート: [assets/templates/archive_report_template_ja.md](assets/templates/archive_report_template_ja.md)
- 最適化レポート: [assets/templates/optimize_report_template_ja.md](assets/templates/optimize_report_template_ja.md)
