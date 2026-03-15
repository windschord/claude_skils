---
name: sdd-document-management
description: SDDドキュメントの整合性チェック、実装同期確認、アーカイブ（CLAUDE.md同期含む）、ファイル最適化、CLAUDE.md同期を行う。ドキュメント間の矛盾検出、実装との乖離確認、完了タスクの整理と仕様のCLAUDE.md転記、肥大化ファイルの分割が必要な場合に使用する。
version: "1.0.0"
---

# SDDドキュメント管理スキル

SDDワークフローで作成されたドキュメントのメンテナンス・整理を行い、品質と一貫性を維持します。

## 概要

| 問題 | 解決機能 |
|------|----------|
| ドキュメント間の仕様矛盾 | 整合性チェック |
| 実装とドキュメントの乖離 | 実装同期チェック |
| 完了済みタスクの蓄積 | アーカイブ |
| ファイルの肥大化 | ファイル最適化 |
| CLAUDE.mdと実装の乖離 | CLAUDE.md同期（定期的に実装コードと比較して乖離を検出） |
| アーカイブ後の仕様散逸 | アーカイブ時CLAUDE.md同期（完了プロジェクトの仕様をCLAUDE.mdに転記） |

### 共通原則

**すべての操作でユーザー承認を必須とする**

```text
チェック実行 → レポート出力 → ★ ユーザー承認 ★ → 修正/アーカイブ実行
```

**フルスキャン時はAgent toolで並列実行する（必須）**

```text
フルスキャン選択時:
  → Agent tool（isolation: worktree）で5機能を並列実行
  → 各サブエージェントがレポートを作成
  → メインセッションで結果を統合・サマリー作成
  → ★ ユーザー承認 ★
  → 修正は順次実行（ファイル競合回避）
```

## ドキュメントの役割

| ドキュメント | 役割 | 説明 |
|-------------|------|------|
| **CLAUDE.md** | 生きた仕様書 | 「今動いているもの」の現在形の記録。常にコンテキストに入る最重要ドキュメント |
| **アクティブSDD** | 計画書 | 「これから作るもの」の仕様。実装時にのみ参照 |
| **アーカイブSDD** | 過去の記録 | 「過去の計画」の考古学的資料。参照頻度は極低 |

**核心原則**: SDDは計画書、CLAUDE.mdは仕様書。プロジェクト完了時に計画書の内容を仕様書に転記するステップが必須。

```text
SDD完了 = archive移動 + CLAUDE.md更新（セット）
```

### CLAUDE.mdに含めるべきセクション

| セクション | 内容 |
|-----------|------|
| API Endpoints | 全APIエンドポイントの一覧 |
| DB Schema | テーブル定義と重要カラム |
| Services | サービス一覧と責務 |
| Pages | 画面一覧と主要機能 |
| WebSocket Message Types | メッセージ種別と方向（該当する場合） |
| State Machines | session_state等の状態遷移（該当する場合） |
| Business Rules | 環境選択ロジック等の重要なビジネスルール |
| Environment Variables | 環境変数の一覧 |

## このスキルを使用する場面

- 開発フェーズの区切りやリリース前にドキュメント整理を行いたい場合
- ドキュメント間に矛盾を発見した場合
- 実装とドキュメントの不一致に気づいた場合
- ファイルが大きくなりすぎて管理が難しい場合
- 完了済みタスクが蓄積してindex.mdが見づらくなった場合
- プロジェクト完了後にCLAUDE.mdへ仕様を反映したい場合

## 機能1: 整合性チェック

requirements、design、tasks間の矛盾や不整合を検出します。

- **要件→設計の整合性**: 要件カバレッジ、過剰設計、用語の一貫性
- **設計→タスクの整合性**: 設計カバレッジ、タスク過不足、参照の正確性
- **クロスリファレンス**: ID参照の有効性、ファイル参照、ステータス整合

**詳細**: [references/consistency_check_ja.md](references/consistency_check_ja.md)

## 機能2: 実装同期チェック

実装コードとドキュメントの乖離を検出します。

- **API同期**: エンドポイント、リクエスト/レスポンス、HTTPメソッド
- **データベース同期**: テーブル定義、カラム定義、リレーション
- **コンポーネント同期**: インターフェース、公開メソッド、依存関係
- **乖離の分類**: ドキュメント古い / 実装漏れ / 未文書化

**詳細**: [references/sync_check_ja.md](references/sync_check_ja.md)

## 機能3: アーカイブ

完了済みタスクや古い決定事項をアーカイブディレクトリに移動し、**実装結果をCLAUDE.mdに反映**します。

- **完了タスク**: ステータスDONE → docs/sdd/archive/tasks/phase-N/
- **古い決定事項**: 明示的指定 or 一定期間経過 → docs/sdd/archive/decisions/
- **古いトラブルシューティング**: 修正完了 → docs/sdd/archive/troubleshooting/
- ファイル移動時にインデックス更新と参照のリンク更新を行う
- **CLAUDE.md同期（必須）**: アーカイブ時に実装結果をCLAUDE.mdの各仕様セクションに反映

```text
アーカイブフロー:
  archive移動 → インデックス更新 → ★ CLAUDE.md更新 ★（セット）

CLAUDE.mdへの反映対象:
  - 新規API → API Endpointsセクション
  - 新規テーブル/列 → DB Schemaセクション
  - 新規サービス → Servicesセクション
  - 新規ページ → Pagesセクション
  - 新規WebSocket → WebSocket Message Typesセクション
  - 新規環境変数 → Environment Variablesセクション
  - 状態遷移 → State Machinesセクション
  - ビジネスルール → Business Rulesセクション
```

**詳細**: [references/archive_ja.md](references/archive_ja.md)

## 機能4: ファイル最適化

肥大化したファイルの分割や重複内容の統合を提案します。

- **サイズ基準**: 500行未満=正常、500-1000行=注意、1000行以上=要対応
- **セクション数基準**: 10未満=正常、10-20=注意、20以上=要対応
- **重複基準**: 類似度30%未満=軽微、30-50%=注意、50%以上=要対応
- 機能別分割・フェーズ別分割のパターンを提案

**詳細**: [references/optimize_ja.md](references/optimize_ja.md)

## 機能5: CLAUDE.md同期

CLAUDE.mdの仕様記載と実装コードの乖離を検出し、CLAUDE.mdを最新状態に更新します。

- **API同期**: CLAUDE.mdのAPI一覧 vs `src/app/api/`（または該当するルーティングディレクトリ）の実ファイル
- **サービス同期**: CLAUDE.mdのServices一覧 vs `src/services/`（または該当するディレクトリ）の実ファイル
- **DBスキーマ同期**: CLAUDE.mdのDB Schema vs `src/db/schema.ts`（またはスキーマ定義ファイル）の実定義
- **ページ同期**: CLAUDE.mdのPages一覧 vs `src/app/`（または該当するページディレクトリ）の実ファイル
- **不足セクション検出**: CLAUDE.mdに存在すべきセクションの有無を確認
  - 必須: API Endpoints, DB Schema, Services, Environment Variables
  - 推奨: Pages, WebSocket Message Types, State Machines, Business Rules

```text
実行手順:
1. CLAUDE.mdの各仕様セクションを解析
2. 対応する実装コードをスキャン
3. 乖離を検出しレポートを作成
4. ★ ユーザー承認 ★
5. CLAUDE.mdを更新
```

**詳細**: [references/claude_md_sync_ja.md](references/claude_md_sync_ja.md)

## ユーザー対話ガイドライン

### スキル起動時

```text
SDDドキュメント管理を開始します。

どの機能を実行しますか？

1. 整合性チェック - ドキュメント間の矛盾を検出
2. 実装同期チェック - 実装とドキュメントの乖離を検出
3. アーカイブ - 完了タスク・古い決定事項を整理 + CLAUDE.md更新
4. ファイル最適化 - 肥大化ファイルの分割・重複統合
5. CLAUDE.md同期 - CLAUDE.mdと実装コードの乖離を検出・更新
6. フルスキャン - 上記すべてをAgent toolで並列実行
```

### フルスキャン選択時のAgent tool並列実行（必須）

フルスキャンが選択された場合、**必ずAgent tool（`isolation: worktree`）で5機能を並列実行**する。1つのメッセージで5つのAgent toolを同時に呼び出す:

```text
【Agent tool 呼び出し1】 整合性チェック
  subagent_type: general-purpose
  isolation: worktree
  prompt: 整合性チェックを実行し、レポートを docs/sdd/reports/consistency/ に作成

【Agent tool 呼び出し2】 実装同期チェック
  subagent_type: general-purpose
  isolation: worktree
  prompt: 実装同期チェックを実行し、レポートを docs/sdd/reports/sync/ に作成

【Agent tool 呼び出し3】 アーカイブ対象検出
  subagent_type: general-purpose
  isolation: worktree
  prompt: アーカイブ対象を検出し、レポートを docs/sdd/reports/archive/ に作成

【Agent tool 呼び出し4】 ファイル最適化分析
  subagent_type: general-purpose
  isolation: worktree
  prompt: ファイル最適化を分析し、レポートを docs/sdd/reports/optimize/ に作成

【Agent tool 呼び出し5】 CLAUDE.md同期チェック
  subagent_type: general-purpose
  isolation: worktree
  prompt: CLAUDE.mdと実装コードの乖離を検出し、レポートを docs/sdd/reports/claude-md-sync/ に作成
```

各サブエージェントはレポート作成のみ行い、修正は実行しない。メインセッションで結果を統合後にユーザー承認を得る。

**並列処理パターンの詳細**: `sdd-documentation/references/agent_teams_guide_ja.md`

### 修正実行前

修正内容をリスト化してユーザーに提示し、承認を得てから実行する。

## 成果物の保存

```text
docs/sdd/reports/
├── consistency/[YYYY-MM-DD].md
├── sync/[YYYY-MM-DD].md
├── archive/[YYYY-MM-DD].md
├── optimize/[YYYY-MM-DD].md
└── claude-md-sync/[YYYY-MM-DD].md
```

## 推奨実行タイミング

| タイミング | 推奨機能 |
|-----------|---------|
| フェーズ完了時 | アーカイブ（CLAUDE.md同期含む）、ファイル最適化 |
| リリース前 | フルスキャン |
| 仕様変更後 | 整合性チェック |
| 大規模実装後 | 実装同期チェック、CLAUDE.md同期 |
| プロジェクト完了時 | アーカイブ（CLAUDE.md同期は必須） |

## Agent toolによる並列チェック（フルスキャン時は必須）

**フルスキャン時はAgent tool（`isolation: worktree`）で5機能を並列実行する。**各サブエージェントが独立したworktreeでチェック・レポート作成を行い、メインセッションが結果を統合する。

```text
メインセッション（結果統合・ユーザー承認）
├── Agent tool + worktree: 整合性チェック → docs/sdd/reports/consistency/
├── Agent tool + worktree: 実装同期チェック → docs/sdd/reports/sync/
├── Agent tool + worktree: アーカイブ対象検出 → docs/sdd/reports/archive/
├── Agent tool + worktree: ファイル最適化分析 → docs/sdd/reports/optimize/
└── Agent tool + worktree: CLAUDE.md同期チェック → docs/sdd/reports/claude-md-sync/
```

- 1つのメッセージで5つのAgent toolを同時に呼び出して並列実行
- レポート作成は並列（worktreeで隔離）、修正実行は順次（ファイル競合回避）
- 各worktreeからレポートファイルを取得してメインブランチに統合
- 統合サマリー作成後、必ずユーザー承認を得る

## TodoWrite連携

- **アーカイブ時**: タスクをアーカイブしたらTodoWriteからも該当タスクを除外
- **整合性チェックによるタスク追加時**: `[TASK-XXX] [DocFix] 修正内容` の形式でTodoWriteにpendingとして追加

## リソース

### リファレンス
- 管理ガイドライン: `references/management_guide_ja.md`
- 整合性チェック: `references/consistency_check_ja.md`
- 実装同期チェック: `references/sync_check_ja.md`
- アーカイブ: `references/archive_ja.md`
- ファイル最適化: `references/optimize_ja.md`
- CLAUDE.md同期: `references/claude_md_sync_ja.md`

### テンプレート
- 整合性チェックレポート: `assets/templates/consistency_report_template_ja.md`
- 実装同期チェックレポート: `assets/templates/sync_report_template_ja.md`
- アーカイブレポート: `assets/templates/archive_report_template_ja.md`
- 最適化レポート: `assets/templates/optimize_report_template_ja.md`
