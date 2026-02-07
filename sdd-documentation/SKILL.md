---
name: sdd-documentation
description: ソフトウェア設計ドキュメント（SDD）を作成・管理・実装・トラブルシュートする。requirements/、design/、tasks/の作成、タスク実行、逆順レビュー、問題分析・修正を統括。SDDワークフロー全体の管理、エラー・バグ・動作不良の分析と修正、追加実装・機能追加に対応。
version: "1.0.0"
---

# SDD ドキュメンテーションスキル

ソフトウェア設計ドキュメント（SDD）の作成・管理・実装を統括するオーケストレータースキルです。

## 概要

このスキルは、以下の6つのサブスキルを連携させて、要件定義から実装・メンテナンスまでの全工程を管理します：

| サブスキル | 役割 | 成果物 |
|-----------|------|--------|
| **requirements-defining** | EARS記法による要件定義 | docs/requirements/ |
| **software-designing** | 技術アーキテクチャ設計 | docs/design/ |
| **task-planning** | AIエージェント向けタスク分解 | docs/tasks/ |
| **task-executing** | タスク実行・逆順レビュー | 実装コード |
| **sdd-troubleshooting** | 問題分析・修正方針策定 | docs/troubleshooting/, docs/tasks/ |
| **sdd-document-management** | ドキュメント管理・メンテナンス | docs/archive/, docs/reports/ |

## ドキュメント構成

```text
docs/
├── requirements/           # 要件定義
│   ├── index.md           # 目次・概要
│   ├── stories/US-XXX.md  # ユーザーストーリー詳細
│   └── nfr/*.md           # 非機能要件
├── design/                # 設計
│   ├── index.md           # 目次・アーキテクチャ概要
│   ├── components/*.md    # コンポーネント詳細
│   ├── api/*.md           # API設計詳細
│   ├── database/schema.md # データベーススキーマ
│   └── decisions/DEC-XXX.md # 技術的決定事項
├── tasks/                 # タスク管理
│   ├── index.md           # 目次・進捗サマリ
│   └── phase-N/TASK-XXX.md # タスク詳細
├── troubleshooting/       # トラブルシューティング
│   └── [YYYY-MM-DD]-[issue-name]/
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

## このスキルを使用する場面

### 一括初期化
- 新規プロジェクトでSDDドキュメント一式が必要な場合

### 全体管理
- 3つのドキュメント間の整合性を確認したい場合
- 逆順レビュー（タスク → 設計 → 要件）を実施したい場合

### 実装フェーズ
- docs/tasks/に沿って実装を行う場合
- 実装後の逆順レビューが必要な場合

### トラブルシューティング・デバッグ（必須）
**以下の状況では、必ず`sdd-troubleshooting`サブスキルを使用してください：**

- **テストエラー** - テストが失敗した場合（原因分析が必須）
- **ビルドエラー** - コンパイルエラー、型エラーが発生した場合
- **実行時エラー** - 例外、クラッシュ、異常終了が発生した場合
- **動作不良** - 期待と異なる動作をしている場合
- **バグ報告** - ユーザーからバグが報告された場合

**重要**: 修正コードを書く前に、必ず根本原因を分析してください。推測に基づく修正は禁止です。

### ドキュメント管理
- ドキュメント間の矛盾を検出・解消したい場合
- 実装とドキュメントの同期を確認したい場合
- 完了済みタスクをアーカイブしたい場合
- 肥大化したファイルを整理したい場合

### 個別作業が必要な場合
特定の工程のみ実施する場合は、各サブスキルを直接使用：
- 要件定義のみ → `requirements-defining`
- 設計のみ → `software-designing`
- タスク計画のみ → `task-planning`
- 実装のみ → `task-executing`
- 問題分析のみ → `sdd-troubleshooting`
- ドキュメント管理のみ → `sdd-document-management`

## ワークフロー

### 新規開発フロー

```text
1. 初期化 → docs/ディレクトリ構造を作成
      ↓
2. requirements-defining → docs/requirements/
      ↓ ユーザー確認・承認
3. software-designing → docs/design/
      ↓ ユーザー確認・承認
4. task-planning → docs/tasks/
      ↓ ユーザー確認・承認
5. ドキュメント逆順レビュー
      ↓
6. task-executing → 実装コード
      ↓
7. 実装逆順レビュー → 完了
```

### トラブルシューティングフロー（デバッグ・エラー修正時は必須）

**エラーやバグに遭遇したら、このフローに従ってください。修正コードを先に書くことは禁止です。**

```text
エラー/バグ発生
      ↓
┌─────────────────────────────────────────────────┐
│ ⚠️ 禁止: 推測で修正、原因不明のまま修正          │
└─────────────────────────────────────────────────┘
      ↓
1. 問題事象の確認（エラーメッセージ、再現手順、期待動作）
      ↓
2. 根本原因の分析（コードを追跡して原因を特定）
      ↓
3. 仕様との照合（docs/requirements/, docs/design/）
      ↓
4. 修正方針の策定（どう直すか、影響範囲は）
      ↓
5. ★ ユーザー承認 ★（必須ゲート - 承認なしで実装禁止）
      ↓
6. タスク分割 → docs/tasks/に追加
      ↓
7. task-executing → 修正実装
```

## ドキュメント初期化

「docsディレクトリを初期化してください」と依頼されたら：

1. **ディレクトリ構造の作成**
2. **requirements/index.md** - テンプレート: `requirements-defining/assets/templates/requirements_index_template_ja.md`
3. **design/index.md** - テンプレート: `software-designing/assets/templates/design_index_template_ja.md`
4. **tasks/index.md** - テンプレート: `task-planning/assets/templates/tasks_index_template_ja.md`

## 逆順レビュープロセス

```text
docs/tasks/ → docs/design/ → docs/requirements/
```

詳細なチェック項目は `references/checklist_ja.md` を参照。

## EARS記法クイックリファレンス

| パターン | 形式 | 使用場面 |
|---------|------|----------|
| 基本 | `システムは〜しなければならない` | 常時適用される要件 |
| イベント | `〜の時、システムは〜しなければならない` | イベント駆動要件 |
| 条件 | `もし〜ならば、システムは〜しなければならない` | 状態依存要件 |
| 継続 | `〜の間、システムは〜しなければならない` | 継続的要件 |
| 場所 | `〜において、システムは〜しなければならない` | コンテキスト固有要件 |

## ユーザーとの対話ガイドライン

### 情報分類プロセス

1. **明示された情報**: ユーザーが明確に述べた要件、仕様、制約
2. **不明な情報**: 推測が必要な項目（「おそらく〜」は不明として扱う）

### 確認の形式

```text
ドキュメント作成の前に、以下の点を確認させてください：

【明示された情報】
- [ユーザーから明示的に指定された内容]

【不明/要確認の情報】
1. [項目1]: [選択肢A] / [選択肢B] / その他
2. [項目2]: [具体的な質問]

上記の不明点について教えていただけますか？
```

## エージェントチームモード

SDDワークフローでは、エージェントチーム機能を活用して並列作業を行うことができます。

**前提条件**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` が有効であること

### チーム活用パターン

| パターン | 用途 |
|---------|------|
| 並列タスク実行 | 依存関係のない複数タスクをチームメンバーが同時実装 |
| 並列レビュー | 要件↔設計↔タスクの整合性を並列チェック |
| 競合仮説デバッグ | 複数仮説を並列調査、相互反証 |
| クロスレイヤー開発 | フロントエンド・バックエンド・テストを並列実装 |

### チーム運用ルール

1. **デリゲートモード推奨**: リーダーは調整に専念
2. **ファイル競合回避**: 各チームメンバーが異なるファイルセットを所有
3. **完了待機**: チームメンバーの完了を待ってから次のフェーズへ

**詳細**: [references/agent_teams_guide_ja.md](references/agent_teams_guide_ja.md)

## タスク同期プロトコル

docs/tasks/のタスクとTodoWriteを同期し、ユーザーにリアルタイムで進捗を表示します。

### ステータスマッピング

| SDD (docs/tasks/) | TodoWrite |
|-------------------|-----------|
| `TODO` | `pending` |
| `IN_PROGRESS` | `in_progress` |
| `DONE` | `completed` |
| `BLOCKED` | `pending`（[BLOCKED]付記） |

- **SDDが正（Source of Truth）**: 詳細仕様はdocs/tasks/に記載
- **TodoWriteは可視化用**: `[TASK-XXX]`形式でcontentに記載

**詳細**: [references/task_sync_guide_ja.md](references/task_sync_guide_ja.md)

## リソース

### リファレンス
- ワークフローガイド: `references/workflow_guide_ja.md`
- 検証チェックリスト: `references/checklist_ja.md`
- エージェントチームガイド: `references/agent_teams_guide_ja.md`
- タスク同期ガイド: `references/task_sync_guide_ja.md`

### サブスキル
- 要件定義: `requirements-defining/SKILL.md`
- 設計: `software-designing/SKILL.md`
- タスク計画: `task-planning/SKILL.md`
- タスク実行: `task-executing/SKILL.md`
- トラブルシューティング: `sdd-troubleshooting/SKILL.md`
- ドキュメント管理: `sdd-document-management/SKILL.md`
