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
    ├── requirements-defining    → docs/sdd/requirements/
    ├── software-designing       → docs/sdd/design/
    ├── task-planning            → docs/sdd/tasks/
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
- **references/checklist_ja.md** - チェックリスト

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
- **references/cicd_guide_ja.md** - CI/CDガイド

### task-planning/
- **SKILL.md** - スキル定義ファイル
- **assets/templates/tasks_index_template_ja.md** - タスク目次テンプレート
- **assets/templates/task_detail_template_ja.md** - タスク詳細テンプレート
- **references/task_guidelines_ja.md** - タスク管理ガイドライン

### task-executing/ + agents/task-executing.md
- **agents/task-executing.md** - エージェント定義ファイル（model: sonnet、Agent toolのsubagent_typeとして使用）
- **references/execution_guide_ja.md** - 実行ガイド
- **references/commit_templates_ja.md** - コミットテンプレート
- **references/jules_integration_ja.md** - Jules連携ガイド

> **注**: task-executing はSKILL.mdを持たず、エージェント定義は `agents/task-executing.md` に配置。`task-executing/references/` のリソースを参照して動作する。

### sdd-troubleshooting/
- **SKILL.md** - スキル定義ファイル（問題確認・原因分析・承認フロー）
- **assets/templates/analysis_report_template_ja.md** - 分析レポートテンプレート
- **assets/templates/bugfix_task_template_ja.md** - バグ修正タスクテンプレート
- **references/analysis_guide_ja.md** - 分析ガイドライン

### sdd-document-management/
- **SKILL.md** - スキル定義ファイル（5機能の定義・承認フロー）
- **assets/templates/consistency_report_template_ja.md** - 整合性レポートテンプレート
- **assets/templates/sync_report_template_ja.md** - 同期レポートテンプレート
- **assets/templates/archive_report_template_ja.md** - アーカイブレポートテンプレート
- **assets/templates/optimize_report_template_ja.md** - 最適化レポートテンプレート
- **references/management_guide_ja.md** - 管理ガイドライン
- **references/consistency_check_ja.md** - 整合性チェックガイド
- **references/sync_check_ja.md** - 同期チェックガイド
- **references/archive_ja.md** - アーカイブガイド
- **references/optimize_ja.md** - 最適化ガイド
- **references/claude_md_sync_ja.md** - CLAUDE.md同期ガイド

### pr-comment-fixer/
- **SKILL.md** - スキル定義ファイル（PRレビューコメント自動修正）
- **references/github_review_api_ja.md** - GitHub Review API構造の解説
- **references/bot_comment_patterns_ja.md** - 各botのコメントパターン一覧
- **references/comment_collector_ja.md** - コメント収集ロジック詳細
- **references/fix_applicator_ja.md** - 修正適用ロジック詳細
- **references/loop_controller_ja.md** - ループ制御ロジック詳細
- **assets/templates/fix_report_template_ja.md** - 修正結果レポートテンプレート

### ai-code-review/
- **SKILL.md** - スキル定義ファイル（6観点からの体系的PRレビュー）
- **assets/templates/review_comment_template_ja.md** - レビューコメントテンプレート
- **references/review_guide_ja.md** - レビューガイド
- **references/rereview_guide_ja.md** - 再レビューガイド

### self-review/
- **SKILL.md** - スキル定義ファイル（ローカル変更の6観点セルフレビュー）
- **assets/templates/self_review_report_template_ja.md** - セルフレビューレポートテンプレート
- **references/self_review_guide_ja.md** - セルフレビューガイド（差分取得・修正適用・SDD連携）

### health-check/
- **SKILL.md** - スキル定義ファイル（インフラメトリクス定期調査・健全性評価）
- **assets/templates/health_check_report_template_ja.md** - ヘルスチェックレポートテンプレート
- **assets/templates/knowledge_base_template_ja.md** - ナレッジベーステンプレート
- **references/metrics_guide_ja.md** - メトリクスガイド
- **references/analysis_principles_ja.md** - 分析原則ガイド
- **references/browser_automation_guide_ja.md** - ブラウザ自動化ガイド

### incident-rca/
- **SKILL.md** - なぜなぜ分析スキル
- **assets/templates/log_template_ja.md** - 分析ログテンプレート
- **assets/templates/result_template_ja.md** - 分析結果テンプレート
- **sessions/** - セッションデータ

### operations-design/
- **SKILL.md** - 運用設計スキル
- **assets/templates/conversation_log_template_ja.md** - ヒアリングログテンプレート
- **assets/templates/operations_design_template_ja.md** - 運用設計テンプレート（汎用）
- **assets/templates/operations_design_template_cloud_instance_ja.md** - 運用設計テンプレート（クラウドインスタンス）
- **assets/templates/operations_design_template_cloud_native_ja.md** - 運用設計テンプレート（クラウドネイティブ）
- **assets/templates/operations_design_template_onpremise_ja.md** - 運用設計テンプレート（オンプレミス）
- **assets/templates/operations_design_template_saas_ja.md** - 運用設計テンプレート（SaaS）
- **hearing_items/2-9_security_compliance_ja.md** - セキュリティコンプライアンスヒアリング項目
- **references/conversation_logging_ja.md** - ヒアリングログガイド
- **references/industry_research_guide_ja.md** - 業界調査ガイド
- **references/operations_design_guide_ja.md** - 運用設計ガイド

### report-summarizing/
- **SKILL.md** - レポート要約スキル
- **assets/templates/executive_summary_template_ja.md** - エグゼクティブサマリーテンプレート

### depth-interviewing-career/
- **SKILL.md** - キャリアインタビュースキル
- **assets/templates/interview_log_template_ja.md** - インタビューログテンプレート

### depth-interviewing-product/
- **SKILL.md** - 製品インタビュースキル
- **assets/templates/interview_log_template_ja.md** - インタビューログテンプレート

### knowledge-base/
- **SKILL.md** - ナレッジベース管理スキル

### things-url/
- **SKILL.md** - Things URLタスク共有スキル
- **references/applescript_reference_ja.md** - Things 3 AppleScriptリファレンス
- **references/url_scheme_reference_ja.md** - Things URLスキームリファレンス

### jules-cli/
- **SKILL.md** - Jules CLI統合スキル

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

docs/sdd/tasks/のタスクとTodoWriteを同期する:

| SDD | TodoWrite |
|-----|-----------|
| TODO | pending |
| IN_PROGRESS | in_progress |
| DONE | completed |
| BLOCKED | pending（[BLOCKED]付記） |
| REVIEW | in_progress（[REVIEW]付記） |

- **SDDが正**: 詳細仕様はdocs/sdd/tasks/に記載
- **タスクIDを含める**: `[TASK-XXX]`形式でcontentに記載
- **非SDDタスクの保持**: TodoWrite更新時、contentが`[Phase-`または`[BLOCKED] [Phase-`で始まらないtodoはそのまま保持する（SDDスキル外で作成されたタスクを上書きしない）

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

## README.mdの最新化ルール

スキルの追加・削除・名称変更・カテゴリ変更を行った場合、**README.mdも必ず同時に更新すること**。

### 更新対象箇所

1. **「利用可能なスキル」テーブル** - スキル名・カテゴリ・説明を追加/削除/修正
2. **「ディレクトリ構造」セクション** - ディレクトリツリーにスキルディレクトリを追加/削除

### 更新タイミング

- 新しいスキルディレクトリを作成したとき
- 既存スキルを削除・リネームしたとき
- スキルのカテゴリや説明を変更したとき
- `agents/`や`scripts/`等の共通ディレクトリに変更があったとき

### チェックリスト

スキル変更時のコミット前に以下を確認:

- [ ] README.mdの「利用可能なスキル」テーブルが実際のスキルディレクトリと一致している
- [ ] README.mdの「ディレクトリ構造」が実際のディレクトリ構成と一致している
- [ ] CLAUDE.mdの「スキルファイル一覧」セクションが最新である
