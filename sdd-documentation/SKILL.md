---
name: sdd-documentation
description: ソフトウェア設計ドキュメント（SDD）を作成・管理・実装・トラブルシュートする。requirements/、design/、tasks/の作成、タスク実行、逆順レビュー、問題分析・修正を統括。SDDワークフロー全体の管理、エラー・バグ・動作不良の分析と修正、追加実装・機能追加に対応。
version: "1.0.0"
---

# SDD ドキュメンテーションスキル

ソフトウェア設計ドキュメント（SDD）の作成・管理・実装を統括するオーケストレータースキルです。

## 実行原則（タイムアウト防止）

**スキルが長時間応答しない問題を防止するため、以下のルールを厳守すること。**

### 1フェーズ1応答の原則

オーケストレーターは**1つのサブスキル工程を完了するごとに、必ずユーザーに結果を報告して応答を返す**こと。複数のサブスキルを連続実行してはならない。

```text
禁止パターン（タイムアウトの原因）:
  スキル呼び出し → requirements作成 → design作成 → tasks作成 → ... → 40分以上無応答

必須パターン:
  スキル呼び出し → requirements作成 → ユーザーに報告・確認待ち
  ユーザー承認   → design作成     → ユーザーに報告・確認待ち
  ユーザー承認   → tasks作成      → ユーザーに報告・確認待ち
```

### テンプレート・リファレンスの遅延読み込み

- **事前に全ファイルを読み込まない**: 使用するテンプレートのみ、使用する直前に1つずつ読み込む
- **リファレンスは必要時のみ参照**: 詳細ガイドは問題発生時や判断に迷った時にのみ読み込む

```text
禁止: 19個のテンプレートと19個のリファレンスを一括読み込み
必須: 「今からrequirements/index.mdを作成する」→ その時点でindex用テンプレートのみ読み込む
```

### 並列処理判定の適用タイミング

- **ドキュメント作成フェーズ（requirements/design/tasks）**: 並列処理判定は不要。順次作成する
- **タスク実行フェーズ**: タスク特定後に並列処理判定を実施（Agent tool + worktree）
- **トラブルシューティング**: 原因候補列挙後に並列処理判定を実施（Agent tool）
- **ドキュメント管理フルスキャン**: 4機能をAgent tool + worktreeで並列実行

### 進捗の可視化

各サブスキル実行中は、処理ステップをユーザーに出力して進捗を可視化すること。

```text
出力例:
  [requirements-defining] ステップ 1/5: 入力要件を読み込み中...
  [requirements-defining] ステップ 2/5: 情報を分類中（明示/不明）...
  [requirements-defining] ステップ 3/5: EARS記法で要件を生成中...
  [requirements-defining] ステップ 4/5: ユーザーストーリーを作成中...
  [requirements-defining] ステップ 5/5: index.mdを作成中...
  [requirements-defining] 完了: 5ファイル作成
```

### 情報分類の段階的処理

ユーザーからの入力が長文の場合、情報分類を一括で行わず段階的に処理すること。

```text
禁止: 長文入力を一度に全て分類（LLMへの単一リクエストが重くなりハングの原因）

必須: 段階的に分類
  Phase 1: 必須情報のみ確認（プロジェクト名、目的、対象ユーザー）
  Phase 2: 機能要件の整理
  Phase 3: 非機能要件の整理
```

### フォールバック戦略

スキルが正常に動作しない場合（長時間応答なし、エラー等）の代替手段を明確にしておくこと。

```text
フォールバック手順:
  1. スキル実行を中断
  2. テンプレートファイルを直接参照:
     - requirements: requirements-defining/assets/templates/
     - design: software-designing/assets/templates/
     - tasks: task-planning/assets/templates/
  3. Writeツールでテンプレートに基づきドキュメントを手動作成
  4. 作成後にチェックリストで品質確認
```

スキルの代わりにテンプレートを直接使用する手動作成は、スキル経由と同等の品質を達成できる。実績として手動作成は約5分で完了する。

## 概要

このスキルは、以下の6つのサブスキルを連携させて、要件定義から実装・メンテナンスまでの全工程を管理します：

| サブスキル | 役割 | 成果物 |
|-----------|------|--------|
| **requirements-defining** | EARS記法による要件定義 | docs/sdd/requirements/ |
| **software-designing** | 技術アーキテクチャ設計 | docs/sdd/design/ |
| **task-planning** | AIエージェント向けタスク分解 | docs/sdd/tasks/ |
| **task-executing** | タスク実行・逆順レビュー | 実装コード |
| **sdd-troubleshooting** | 問題分析・修正方針策定 | docs/sdd/troubleshooting/, docs/sdd/tasks/ |
| **sdd-document-management** | ドキュメント管理・メンテナンス | docs/sdd/archive/, docs/sdd/reports/ |

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
- docs/sdd/tasks/に沿って実装を行う場合
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

**重要: 各ステップ完了後に必ずユーザーに結果を報告し、承認を得てから次のステップに進むこと。**

```text
1. 初期化 → docs/sdd/ディレクトリ構造を作成
      ↓ ★ ユーザーに報告 ★
2. requirements-defining → docs/sdd/requirements/
      ↓ ★ ユーザーに結果を提示・承認待ち ★（ここで応答を返す）
3. software-designing → docs/sdd/design/
      ↓ ★ ユーザーに結果を提示・承認待ち ★（ここで応答を返す）
4. task-planning → docs/sdd/tasks/
      ↓ ★ ユーザーに結果を提示・承認待ち ★（ここで応答を返す）
5. 実行モード判定: Jules CLI / Agent tool並列処理（タスク実行フェーズのみ）
      ↓
6. ドキュメント逆順レビュー
      ↓ ★ ユーザーに結果を提示・承認待ち ★（ここで応答を返す）
7. task-executing → 実装コード
      ↓ ★ ユーザーに結果を提示 ★（ここで応答を返す）
8. 実装逆順レビュー → 完了
```

**各ステップの所要時間目安**: 1ステップあたり3-10分。10分を超える場合は作業が肥大化している可能性があるため、スコープを見直すこと。

### 並列処理判定基準

**注意: 並列処理判定はタスク実行フェーズ（ステップ5）でのみ実施する。ドキュメント作成フェーズ（ステップ1-4）では判定不要。**

判定条件:
1. 並列実行可能なタスクが2つ以上ある
2. タスク間に依存関係がない（同一グループ内）
3. 同一ファイルを変更する可能性が低い（高い場合は統合時コンフリクト多発のため順次実行を推奨）

- **すべてYES** → Agent tool（`isolation: worktree`）で並列実行
- **いずれかNO** → 単一セッションで順次実行

**方式**: Agent toolの`isolation: worktree`を使用し、各サブエージェントが独立したgit worktreeで動作。並行作業中の上書き衝突を防止できるが、統合時にマージコンフリクトが発生し得るため必要に応じて手動解決する。

**並列処理パターンと呼び出し例**: [references/agent_teams_guide_ja.md](references/agent_teams_guide_ja.md)

### タスク実行モード判定（Jules CLI統合）

Jules CLIが利用可能な場合のモード判定とアサイン戦略の詳細は [task-executing/references/jules_integration_ja.md](../task-executing/references/jules_integration_ja.md) を参照。

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
3. 仕様との照合（docs/sdd/requirements/, docs/sdd/design/）
      ↓
4. 修正方針の策定（どう直すか、影響範囲は）
      ↓
5. ★ ユーザー承認 ★（必須ゲート - 承認なしで実装禁止）
      ↓
6. タスク分割 → docs/sdd/tasks/に追加
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
docs/sdd/tasks/ → docs/sdd/design/ → docs/sdd/requirements/
```

詳細なチェック項目は `references/checklist_ja.md` を参照。

## EARS記法

詳細は [requirements-defining/references/ears_notation_ja.md](../requirements-defining/references/ears_notation_ja.md) を参照。

## 自律実行モード（orchestrating-agents連携）

複数フェーズを自律的に実行する場合は、`orchestrating-agents` スキルの3階層エージェント構造を活用する。

- 親（Director）がSDDワークフロー全体を管理
- 子（Manager）が各フェーズ（requirements/design/tasks/executing）を担当
- 孫（Worker）が個別タスクを並列実行（task-executingフェーズのみ）

詳細: `orchestrating-agents/SKILL.md`

### SDDスキルへの適用マッピング

| サブスキル | 階層モード | 理由 |
|-----------|-----------|------|
| requirements-defining | 2階層 | 単一作業、並列化不要 |
| software-designing | 2階層 | 同上 |
| task-planning | 2階層 | 同上 |
| task-executing | 3階層 | 複数タスクの並列実行が可能 |
| sdd-troubleshooting | 条件分岐 | 仮説3つ以上なら3階層 |
| sdd-document-management | 3階層 | フルスキャン時に5機能を並列実行 |

## 並列処理（Agent tool活用）

**条件を満たす場合は積極的に使用する。** 判定基準・パターン・呼び出し例は [references/agent_teams_guide_ja.md](references/agent_teams_guide_ja.md) を参照。

## タスク同期プロトコル

docs/sdd/tasks/のタスクとTodoWriteの同期ルール。詳細は [references/task_sync_guide_ja.md](references/task_sync_guide_ja.md) を参照。

## リソース

### リファレンス
- ワークフローガイド: `references/workflow_guide_ja.md`
- 検証チェックリスト: `references/checklist_ja.md`
- 並列処理ガイド: `references/agent_teams_guide_ja.md`
- タスク同期ガイド: `references/task_sync_guide_ja.md`

### サブスキル
- 要件定義: `requirements-defining/SKILL.md`
- 設計: `software-designing/SKILL.md`
- タスク計画: `task-planning/SKILL.md`
- タスク実行: `task-executing/SKILL.md`
- トラブルシューティング: `sdd-troubleshooting/SKILL.md`
- ドキュメント管理: `sdd-document-management/SKILL.md`
