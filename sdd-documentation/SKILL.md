---
name: sdd-documentation
description: ソフトウェア設計ドキュメント（SDD）の作成・管理・実装・トラブルシュートを統括するオーケストレーター。「SDDを作成して」「要件定義から始めて」「設計ドキュメントを管理して」「エラーを分析して」等の依頼時に使用。requirements/design/tasks作成、タスク実行、逆順レビュー、問題分析・修正、ドキュメント管理を統括する。
metadata:
  version: "1.0.0"
---

# SDD ドキュメンテーションスキル

6つのサブスキルを連携し、要件定義から実装・メンテナンスまでの全工程を統括する。

| サブスキル | 役割 | 成果物 |
|-----------|------|--------|
| requirements-defining | EARS記法による要件定義 | docs/sdd/requirements/ |
| software-designing | 技術アーキテクチャ設計 | docs/sdd/design/ |
| task-planning | AIエージェント向けタスク分解 | docs/sdd/tasks/ |
| task-executing | タスク実行・逆順レビュー | 実装コード |
| sdd-troubleshooting | 問題分析・修正方針策定 | docs/sdd/troubleshooting/, docs/sdd/tasks/ |
| sdd-document-management | ドキュメント管理・メンテナンス | docs/sdd/archive/, docs/sdd/reports/ |

## 実行原則

### 1フェーズ1応答

1つのサブスキル工程を完了するごとに、必ずユーザーに結果を報告して応答を返す。複数のサブスキルを連続実行しない。各ステップの所要時間目安は3-10分。10分を超える場合はスコープを見直す。

### 遅延読み込み

テンプレートやリファレンスは使用する直前に1つずつ読み込む。事前に全ファイルを一括読み込みしない。

### 進捗の可視化

各サブスキル実行中は `[skill-name] ステップ N/M: 処理内容...` 形式で進捗を出力する。

### フォールバック

スキルが正常に動作しない場合は、各サブスキルの `assets/templates/` 配下のテンプレートを直接参照してWriteツールで手動作成する。

## ドキュメント構成

```text
docs/sdd/
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
└── reports/               # 管理レポート
```

## ワークフロー

### 新規開発フロー

各ステップ完了後に必ずユーザーに結果を報告し、承認を得てから次のステップに進む。

```text
1. 初期化 → docs/sdd/ディレクトリ構造を作成
      ↓ ユーザーに報告
2. requirements-defining → docs/sdd/requirements/
      ↓ ユーザーに結果を提示・承認待ち
3. software-designing → docs/sdd/design/
      ↓ ユーザーに結果を提示・承認待ち
4. task-planning → docs/sdd/tasks/
      ↓ ユーザーに結果を提示・承認待ち
5. 実行モード判定 → 並列処理判定
      ↓
6. ドキュメント逆順レビュー
      ↓ ユーザーに結果を提示・承認待ち
7. task-executing → 実装コード
      ↓ ユーザーに結果を提示
8. 実装逆順レビュー → 完了
```

### トラブルシューティングフロー

エラーやバグに遭遇したら、必ず `sdd-troubleshooting` サブスキルを使用する。修正コードを先に書くことは禁止。根本原因の分析 → ユーザー承認 → 実装の順序を厳守。

### 個別作業

特定の工程のみ実施する場合は、各サブスキルを直接使用する。

## 並列処理判定

ドキュメント作成フェーズ（ステップ1-4）では判定不要。タスク実行フェーズでのみ実施。

判定条件（すべてYESで並列実行）:
1. 並列実行可能なタスクが2つ以上ある
2. タスク間に依存関係がない
3. 同一ファイルを変更する可能性が低い

方式: Agent toolの `isolation: worktree` を使用。詳細は [references/agent_teams_guide_ja.md](references/agent_teams_guide_ja.md) を参照。

## ドキュメント初期化

「docsディレクトリを初期化してください」と依頼されたら、ディレクトリ構造を作成し、各index.mdを対応するテンプレートから生成する:
- requirements/index.md ← `requirements-defining/assets/templates/requirements_index_template_ja.md`
- design/index.md ← `software-designing/assets/templates/design_index_template_ja.md`
- tasks/index.md ← `task-planning/assets/templates/tasks_index_template_ja.md`

## 逆順レビュー

```text
docs/sdd/tasks/ → docs/sdd/design/ → docs/sdd/requirements/
```

詳細なチェック項目は [references/checklist_ja.md](references/checklist_ja.md) を参照。

## タスク同期プロトコル

docs/sdd/tasks/のタスクとTodoWriteの同期ルール。詳細は [references/task_sync_guide_ja.md](references/task_sync_guide_ja.md) を参照。

## リソース

- ワークフローガイド: [references/workflow_guide_ja.md](references/workflow_guide_ja.md)
- 検証チェックリスト: [references/checklist_ja.md](references/checklist_ja.md)
- 並列処理ガイド: [references/agent_teams_guide_ja.md](references/agent_teams_guide_ja.md)
- タスク同期ガイド: [references/task_sync_guide_ja.md](references/task_sync_guide_ja.md)
- Jules CLI統合: [task-executing/references/jules_integration_ja.md](../task-executing/references/jules_integration_ja.md)
- EARS記法: [requirements-defining/references/ears_notation_ja.md](../requirements-defining/references/ears_notation_ja.md)
