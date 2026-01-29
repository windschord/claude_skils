# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

このリポジトリは、Claude Codeのスキルとして使用するソフトウェア設計ドキュメント（SDD）管理システムです。EARS記法を用いた要件定義、技術設計、タスク管理の3つのスキルを提供し、構造化されたプロセスでドキュメントを作成・管理します。

## SDDスキル構成

オーケストレータースキルと6つのサブスキルで構成されます：

```text
sdd-documentation（オーケストレーター）
    │
    ├── requirements-defining    → docs/requirements/
    │
    ├── software-designing       → docs/design/
    │
    ├── task-planning            → docs/tasks/
    │
    ├── task-executing           → 実装コード（逆順レビュー付き）
    │
    ├── sdd-troubleshooting      → 問題分析・修正タスク（承認フロー付き）
    │
    └── sdd-document-management  → ドキュメント管理・メンテナンス（承認フロー付き）
```

### 出力ドキュメント構成

```
docs/
├── requirements/           # 要件定義
│   ├── index.md           # 目次・概要
│   ├── stories/           # ユーザーストーリー詳細
│   │   └── US-XXX.md
│   └── nfr/               # 非機能要件
│       └── performance.md
├── design/                # 設計
│   ├── index.md           # 目次・アーキテクチャ概要
│   ├── components/        # コンポーネント詳細
│   ├── api/               # API設計詳細
│   ├── database/          # データベーススキーマ
│   └── decisions/         # 技術的決定事項
├── tasks/                 # タスク管理
│   ├── index.md           # 目次・進捗サマリ
│   └── phase-N/           # フェーズ別タスク
│       └── TASK-XXX.md
├── troubleshooting/       # トラブルシューティング
│   └── [YYYY-MM-DD]-[issue-name]/
│       └── analysis.md    # 分析レポート
├── archive/               # アーカイブ（完了済み）
│   ├── tasks/             # 完了済みタスク
│   ├── decisions/         # 古い決定事項
│   └── troubleshooting/   # 完了した問題分析
└── reports/               # 管理レポート
    ├── consistency/       # 整合性チェックレポート
    ├── sync/              # 実装同期チェックレポート
    ├── archive/           # アーカイブレポート
    └── optimize/          # 最適化レポート
```

### sdd-documentation/
SDDドキュメント全体を統括するオーケストレータースキル：
- **SKILL.md** - 統合スキル定義（初期化・整合性チェック・逆順レビュー）
- **references/workflow_guide_ja.md** - ワークフローガイド

### requirements-defining/
EARS記法を用いた要件定義書を作成・管理するスキル：
- **SKILL.md** - スキル定義ファイル
- **assets/templates/requirements_index_template_ja.md** - 要件目次テンプレート
- **assets/templates/user_story_template_ja.md** - ユーザーストーリーテンプレート
- **assets/templates/nfr_template_ja.md** - 非機能要件テンプレート
- **references/ears_notation_ja.md** - EARS記法の詳細ガイド

### software-designing/
技術アーキテクチャ・設計書を作成・管理するスキル：
- **SKILL.md** - スキル定義ファイル
- **assets/templates/design_index_template_ja.md** - 設計目次テンプレート
- **assets/templates/component_template_ja.md** - コンポーネント設計テンプレート
- **assets/templates/api_template_ja.md** - API設計テンプレート
- **assets/templates/database_template_ja.md** - データベース設計テンプレート
- **assets/templates/decision_template_ja.md** - 技術的決定テンプレート
- **references/design_patterns_ja.md** - 設計パターンリファレンス
- **references/ears_notation_ja.md** - EARS記法（要件参照用）

### task-planning/
AIエージェント向け実装タスクを作成・管理するスキル：
- **SKILL.md** - スキル定義ファイル
- **assets/templates/tasks_index_template_ja.md** - タスク目次テンプレート
- **assets/templates/task_detail_template_ja.md** - タスク詳細テンプレート
- **references/task_guidelines_ja.md** - タスク管理ガイドライン

### task-executing/
タスクを実行し、実装を行うスキル：
- **SKILL.md** - スキル定義ファイル（逆順レビュー・コミットテンプレート含む）

### sdd-troubleshooting/
動作不良や問題を分析し、修正方針を策定するスキル：
- **SKILL.md** - スキル定義ファイル（問題確認・原因分析・承認フロー）
- **references/analysis_guide_ja.md** - 分析ガイドライン
- 問題事象の確認と再現手順の把握
- 根本原因の分析とコード調査
- 仕様（要件定義・設計）との照合
- 修正方針の策定と**ユーザー承認**（必須ゲート）
- 修正タスクの分割とdocs/tasks/への追加

### sdd-document-management/
ドキュメントのメンテナンス・整理を行うスキル：
- **SKILL.md** - スキル定義ファイル（4機能の定義・承認フロー）
- **references/management_guide_ja.md** - 管理ガイドライン
- **整合性チェック**: requirements ↔ design ↔ tasks間の矛盾検出
- **実装同期チェック**: 実装コードとドキュメントの乖離検出
- **アーカイブ**: 完了タスク・古い決定事項の整理
- **ファイル最適化**: 肥大化ファイルの分割・重複統合
- すべての操作で**ユーザー承認**（必須ゲート）

## その他のスキル

### depth-interviewing-career/
社員のキャリア観・働きがい・職場環境をデプスインタビュー形式で聞き出すスキル：
- **SKILL.md** - スキル定義ファイル
- オープンエンドな質問による本音の引き出し
- 構造化された分析レポートの作成

### depth-interviewing-product/
製品やサービスに対するユーザーの利用実態・満足度・改善要望を聞き出すスキル：
- **SKILL.md** - スキル定義ファイル
- 顧客インサイトの発見
- 構造化された分析レポートの作成

## スキルの使用方法

### 一括フロー（推奨）
`sdd-documentation`スキルを使用：
- ドキュメント一式の初期化
- 4つのドキュメントを順に作成・実装
- 整合性チェック・逆順レビュー

### 個別フロー
各サブスキルを直接使用：
1. **requirements-defining** - EARS記法で要件を定義 → `docs/requirements/`
2. **software-designing** - 要件を基に技術設計 → `docs/design/`
3. **task-planning** - 設計を基にタスク分解 → `docs/tasks/`
4. **task-executing** - タスクに沿って実装 → 実装コード
5. **sdd-troubleshooting** - 問題分析・修正方針策定 → `docs/troubleshooting/`, `docs/tasks/`
6. **sdd-document-management** - ドキュメント整理・メンテナンス → `docs/archive/`, `docs/reports/`

### EARS記法の基本パターン

| パターン | 形式 | 使用場面 |
|---------|------|----------|
| 基本 | `システムは〜しなければならない` | 常時適用される要件 |
| イベント | `〜の時、システムは〜しなければならない` | イベント駆動要件 |
| 条件 | `もし〜ならば、システムは〜しなければならない` | 状態依存要件 |
| 継続 | `〜の間、システムは〜しなければならない` | 継続的要件 |
| 場所 | `〜において、システムは〜しなければならない` | コンテキスト固有要件 |

## アーキテクチャ

### ドキュメントの関係性
```text
docs/requirements/ (何を作るか)
    ↓
docs/design/ (どのように作るか)
    ↓
docs/tasks/ (どのように実装するか)
```

### ワークフロー（新規開発）
1. **要件定義** - requirements-definingスキルでEARS記法を使って何を作るかを定義
2. **設計** - software-designingスキルでどのように作るかを文書化
3. **タスク計画** - task-planningスキルで実装を計画
4. **ドキュメント逆順レビュー** - タスク→設計→要件の整合性をチェック
5. **実装** - task-executingスキルでタスクに沿って実装
6. **実装逆順レビュー** - 実装→タスク→設計→要件の整合性をチェック
7. **反復** - プロジェクトの進展に応じて各スキルで更新

### ワークフロー（トラブルシューティング）
1. **問題事象の確認** - 現象・再現手順・期待動作を把握
2. **根本原因の分析** - コード調査で原因を特定
3. **仕様との照合** - 要件定義・設計に対する乖離を確認
4. **修正方針の策定** - 修正アプローチ・影響範囲を検討
5. **ユーザー承認** - 修正方針について**必ず承認を得る**（必須ゲート）
6. **タスク分割** - 修正タスクをdocs/tasks/に追加
7. **実装** - task-executingスキルで修正を実装

## デバッグ・エラー修正の必須プロセス

**エラーやバグに遭遇した場合は、必ず`sdd-troubleshooting`スキルを使用してください。**

### 対象となる状況

| 状況 | 例 | 必須アクション |
|-----|-----|---------------|
| テストエラー | `npm test`失敗、アサーションエラー | sdd-troubleshootingで原因分析 |
| ビルドエラー | コンパイルエラー、型エラー | sdd-troubleshootingで原因分析 |
| 実行時エラー | 例外スロー、クラッシュ | sdd-troubleshootingで原因分析 |
| 動作不良 | 期待と異なる動作 | sdd-troubleshootingで原因分析 |

### 禁止事項

```text
❌ 推測に基づく修正（「たぶんこれが原因」で修正）
❌ エラーメッセージだけを見て修正
❌ 原因不明のまま「とりあえず動くように」修正
❌ 検索で見つけた解決策をそのまま適用
❌ ユーザー承認なしで修正を実装
```

### 正しいプロセス

```text
エラー発生
    ↓
sdd-troubleshootingスキルを使用
    ↓
1. 問題事象を確認（エラーメッセージ、スタックトレース、再現手順）
2. 根本原因を分析（コードを追跡して原因を特定）
3. 仕様との照合（要件定義・設計との乖離を確認）
4. 修正方針を策定（どう直すか、影響範囲は）
5. ユーザー承認を得る（必須ゲート）
6. タスク分割して実装
```

## ドキュメント作成時の重要原則

### 情報の明確性（最重要）
すべてのドキュメント作成において、以下の原則を厳守してください：

1. **情報の分類**
   - ユーザーの指示から「明示された情報」と「不明な情報」を分けてリストアップ
   - 「おそらく〜だろう」という推測は「不明」として扱う
   - 推測に基づく設計・タスク作成は行わない

2. **不明な情報の確認**
   - 不明な情報が1つでもあれば、実装前に必ず質問する
   - 確認なしに推測で進めない
   - すべての不明点が解消されてから設計・タスク作成を開始

3. **サブエージェント向け完全性**
   - 設計書・タスクには、サブエージェントが質問なしに実装できるレベルの情報を記載
   - ファイルパス、型定義、入出力仕様、エラー処理など具体的に記述

### 要件定義（docs/requirements/）
- **index.md**: 目次・概要・要件サマリ
- **stories/US-XXX.md**: 各ユーザーストーリーとEARS記法の受入基準
- **nfr/*.md**: 非機能要件（カテゴリ別ファイル）
- 要件IDは一意（REQ-XXX、NFR-XXX）
- 各要件はテスト可能で測定可能
- 「しなければならない」で統一

### 設計（docs/design/）
- **index.md**: 目次・アーキテクチャ概要・情報明確性チェック
- **components/*.md**: コンポーネント詳細（目的・責務・インターフェース）
- **api/*.md**: API設計詳細（エンドポイント・リクエスト/レスポンス）
- **database/schema.md**: データベーススキーマ
- **decisions/DEC-XXX.md**: 技術的決定事項（選択肢・根拠）
- アーキテクチャ図にはMermaid形式を使用

### タスク管理（docs/tasks/）
- **index.md**: 目次・進捗サマリ・全体の情報明確性チェック
- **phase-N/TASK-XXX.md**: 個別タスク詳細
- タスクは適切な粒度に分解（AIエージェント作業時間で20-40分程度）
- 各タスクに受入基準、依存関係、見積もり時間を記載
- ステータス: `TODO`, `IN_PROGRESS`, `BLOCKED`, `REVIEW`, `DONE`
- **各タスクに「情報の明確性」セクションを含める**

## 検証チェックリスト

ドキュメントをレビューする際の確認項目：

### 要件定義書
- ✅ ユーザーストーリーが明確に定義されている
- ✅ すべての要件がEARS記法に従っている
- ✅ 要件IDが一意である
- ✅ 各要件がテスト可能である
- ✅ 非機能要件が含まれている

### 設計書
- ✅ アーキテクチャ概要が記載されている
- ✅ 主要コンポーネントが定義されている
- ✅ インターフェースが明確である
- ✅ 技術的決定事項と根拠が記載されている
- ✅ 必要に応じて図表が含まれている
- ✅ **情報の明確性チェックが完了している**
- ✅ **不明/要確認の情報がすべて解消されている**

### タスク管理書
- ✅ タスクが適切な粒度に分解されている
- ✅ 各タスクに受入基準がある
- ✅ 依存関係が明確である
- ✅ 見積もり時間が記載されている
- ✅ ステータスが有効な値である
- ✅ **各タスクの「情報の明確性」セクションが記載されている**
- ✅ **推測に基づく実装指示が含まれていない**

## 逆順レビュープロセス（整合性チェック）

ドキュメント作成・修正後は、逆順（タスク → 設計 → 要件）でレビューを行い、矛盾や過不足を確認する：

### チェックの流れ
```text
docs/tasks/ → docs/design/ → docs/requirements/
```

### 確認項目
1. **タスク → 設計**: タスクが参照するコンポーネント/APIはdesign/に定義されているか
2. **設計 → 要件**: すべての要件（REQ-XXX）に対応する設計要素があるか
3. **過剰チェック**: 要件にない機能が設計やタスクに含まれていないか
4. **漏れチェック**: 設計やタスクに対応しない要件がないか

### 不整合発見時
矛盾や過不足を発見した場合は、**ユーザーに確認してからドキュメントを修正する**

## リファレンスの活用

- ワークフローガイド: `sdd-documentation/references/workflow_guide_ja.md`
- EARS記法ガイド: `requirements-defining/references/ears_notation_ja.md`
- 設計パターン: `software-designing/references/design_patterns_ja.md`
- タスクガイドライン: `task-planning/references/task_guidelines_ja.md`
- 分析ガイドライン: `sdd-troubleshooting/references/analysis_guide_ja.md`
- 管理ガイドライン: `sdd-document-management/references/management_guide_ja.md`
- テンプレート: 各サブスキルの`assets/templates/`配下

## ベストプラクティス

1. **なぜから始める** - 目的を理解するためユーザーストーリーから開始
2. **具体的に** - 測定可能な値を使用
3. **要件ごとに1つ** - 複合要件を避ける
4. **すべてをテスト可能に** - 各要件は検証可能でなければならない
5. **依存関係を追跡** - 関連タスクを明確にリンク
6. **最新を保つ** - 作業の進行に応じてステータスを更新
7. **情報を分類する** - 明示された情報と不明な情報を常に区別する
8. **推測しない** - 「おそらく〜」は「不明」として扱い、必ず確認する
