# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Claude Codeのスキルコレクションです。SDD（ソフトウェア設計ドキュメント）管理スキル群を中心に、分析・インタビュー・ユーティリティスキルを提供します。

## リポジトリのドキュメント構造

このリポジトリには2種類のドキュメントがあります:

| 種類 | 配置場所 | 対象読者 | 説明 |
|------|----------|----------|------|
| **ユーザー向けドキュメント** | `docs/` | 人間 | 使い方ガイド、スキルカタログ、ワークフロー解説、開発ガイド |
| **スキル内部リソース** | 各スキルディレクトリ | Claude Code | SKILL.md、references/、assets/templates/ |

```text
docs/                              # ユーザー向けドキュメント（人間が読む）
├── getting-started.md             # 導入ガイド
├── skill-catalog.md               # 全スキル一覧と使い方
├── sdd-workflow.md                # SDDワークフロー解説
└── development-guide.md           # スキル開発者向けガイド

{スキル名}/                         # スキル内部リソース（Claude Codeが読む）
├── SKILL.md                       # スキル定義
├── references/                    # スキル実行時にClaudeが参照するリファレンス
└── assets/templates/              # ドキュメント生成用テンプレート
```

## SDDスキル構成

```text
sdd-documentation（オーケストレーター）
    ├── requirements-defining    → docs/requirements/
    ├── software-designing       → docs/design/
    ├── task-planning            → docs/tasks/
    ├── task-executing           → 実装コード（逆順レビュー付き）
    ├── sdd-troubleshooting      → 問題分析・修正タスク（承認フロー付き）
    └── sdd-document-management  → ドキュメント管理・メンテナンス（承認フロー付き）
```

## スキルファイル一覧

### sdd-documentation/
- **SKILL.md** - 統合スキル定義（初期化・整合性チェック・逆順レビュー・エージェントチーム・タスク同期）
- **references/workflow_guide_ja.md** - ワークフローガイド
- **references/agent_teams_guide_ja.md** - エージェントチーム活用ガイド
- **references/task_sync_guide_ja.md** - タスク同期（TodoWrite連携）ガイド

### requirements-defining/
- **SKILL.md** - スキル定義ファイル
- **assets/templates/requirements_index_template_ja.md** - 要件目次テンプレート
- **assets/templates/user_story_template_ja.md** - ユーザーストーリーテンプレート
- **assets/templates/nfr_template_ja.md** - 非機能要件テンプレート
- **references/ears_notation_ja.md** - EARS記法の詳細ガイド

### software-designing/
- **SKILL.md** - スキル定義ファイル
- **assets/templates/design_index_template_ja.md** - 設計目次テンプレート
- **assets/templates/component_template_ja.md** - コンポーネント設計テンプレート
- **assets/templates/api_template_ja.md** - API設計テンプレート
- **assets/templates/database_template_ja.md** - データベース設計テンプレート
- **assets/templates/decision_template_ja.md** - 技術的決定テンプレート
- **references/design_patterns_ja.md** - 設計パターンリファレンス
- **references/ears_notation_ja.md** - EARS記法（要件参照用）

### task-planning/
- **SKILL.md** - スキル定義ファイル
- **assets/templates/tasks_index_template_ja.md** - タスク目次テンプレート
- **assets/templates/task_detail_template_ja.md** - タスク詳細テンプレート
- **references/task_guidelines_ja.md** - タスク管理ガイドライン

### task-executing/
- **references/execution_guide_ja.md** - 実行ガイド
- **references/commit_templates_ja.md** - コミットテンプレート

### sdd-troubleshooting/
- **SKILL.md** - スキル定義ファイル（問題確認・原因分析・承認フロー）
- **assets/templates/analysis_report_template_ja.md** - 分析レポートテンプレート
- **assets/templates/bugfix_task_template_ja.md** - バグ修正タスクテンプレート
- **references/analysis_guide_ja.md** - 分析ガイドライン

### sdd-document-management/
- **SKILL.md** - スキル定義ファイル（4機能の定義・承認フロー）
- **assets/templates/consistency_report_template_ja.md** - 整合性レポートテンプレート
- **assets/templates/sync_report_template_ja.md** - 同期レポートテンプレート
- **assets/templates/archive_report_template_ja.md** - アーカイブレポートテンプレート
- **assets/templates/optimize_report_template_ja.md** - 最適化レポートテンプレート
- **references/management_guide_ja.md** - 管理ガイドライン
- **references/consistency_check_ja.md** - 整合性チェックガイド
- **references/sync_check_ja.md** - 同期チェックガイド
- **references/archive_ja.md** - アーカイブガイド
- **references/optimize_ja.md** - 最適化ガイド

### その他のスキル
- **incident-rca/SKILL.md** - なぜなぜ分析スキル
- **operations-design/SKILL.md** - 運用設計スキル
- **report-summarizing/SKILL.md** - レポート要約スキル
- **jules-cli/SKILL.md** - Jules CLI統合スキル
- **depth-interviewing-career/SKILL.md** - キャリアインタビュースキル
- **depth-interviewing-product/SKILL.md** - 製品インタビュースキル

## デバッグ・エラー修正の必須プロセス

**エラーやバグに遭遇した場合は、必ず`sdd-troubleshooting`スキルを使用してください。**

### 禁止事項

- 推測に基づく修正（「たぶんこれが原因」で修正）
- エラーメッセージだけを見て修正
- 原因不明のまま「とりあえず動くように」修正
- 検索で見つけた解決策をそのまま適用
- ユーザー承認なしで修正を実装

### 正しいプロセス

```text
エラー発生 → sdd-troubleshootingスキルを使用
1. 問題事象を確認（エラーメッセージ、スタックトレース、再現手順）
2. 根本原因を分析（コードを追跡して原因を特定）
3. 仕様との照合（要件定義・設計との乖離を確認）
4. 修正方針を策定（どう直すか、影響範囲は）
5. ユーザー承認を得る（必須ゲート）
6. タスク分割して実装
```

## ドキュメント作成時の重要原則

### 情報の明確性（最重要）

1. **情報の分類**: 「明示された情報」と「不明な情報」を分けてリストアップ。推測は「不明」として扱う
2. **不明な情報の確認**: 不明な情報が1つでもあれば実装前に必ず質問。推測で進めない
3. **サブエージェント向け完全性**: サブエージェントが質問なしに実装できるレベルの情報を記載

### タスク同期（TodoWrite連携）

docs/tasks/のタスクとTodoWriteを同期する:

| SDD | TodoWrite |
|-----|-----------|
| TODO | pending |
| IN_PROGRESS | in_progress |
| DONE | completed |
| BLOCKED | pending（[BLOCKED]付記） |
| REVIEW | in_progress（[REVIEW]付記） |

- **SDDが正**: 詳細仕様はdocs/tasks/に記載
- **タスクIDを含める**: `[TASK-XXX]`形式でcontentに記載

## スキル実行のタイムアウト防止

### 1フェーズ1応答の原則

- **1つのサブスキル工程が完了したら、必ずユーザーに結果を報告して応答を返す**
- 複数のサブスキルを連続実行しない
- 各フェーズの所要時間目安は3-10分。10分を超える場合はスコープを見直す

### テンプレート・リファレンスの遅延読み込み

- テンプレートやリファレンスは**使用する直前に1つずつ**読み込む
- 事前に全ファイルを一括読み込みしない

### 進捗の可視化

各サブスキル実行中は処理ステップをユーザーに出力すること:

```text
[skill-name] ステップ N/M: 処理内容...
[skill-name] 完了: N ファイル作成
```

### フォールバック戦略

スキルが正常に動作しない場合は、テンプレートを直接参照して手動作成に切り替えること:

1. スキル実行を中断
2. テンプレートファイルを直接参照（各サブスキルの`assets/templates/`配下）
3. Writeツールでドキュメントを手動作成
4. 作成後にチェックリストで品質確認
