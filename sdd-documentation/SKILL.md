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

### 概要

SDDワークフローでは、エージェントチーム機能を活用して並列作業を行うことができます。エージェントチームを使用することで、独立したタスクを複数のチームメンバーが同時に処理し、効率的にプロジェクトを進めることができます。

**前提条件**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` が有効であること（settings.jsonまたは環境変数で設定）

### チーム活用パターン

#### パターン1: 並列タスク実行

docs/tasks/に依存関係のない複数タスクがある場合、エージェントチームを使用して並列実行します。

```text
チームリーダー（sdd-documentation）
    │
    ├── チームメンバーA: TASK-001（認証API実装）
    ├── チームメンバーB: TASK-002（データモデル定義）
    └── チームメンバーC: TASK-003（設定ファイル作成）
```

**スポーンプロンプト例**:

```text
エージェントチームを作成して、以下のタスクを並列実行してください。
各チームメンバーにはtask-executingエージェントの手順に従って実装を進めてもらいます。

- チームメンバー1: docs/tasks/phase-1/TASK-001.md を実行
- チームメンバー2: docs/tasks/phase-1/TASK-002.md を実行
- チームメンバー3: docs/tasks/phase-1/TASK-003.md を実行

各タスクの詳細はファイルに記載されています。
タスクの完了後はステータスをDONEに更新し、コミットを作成してください。
ファイル競合を避けるため、各チームメンバーは担当タスクのファイルのみ編集してください。
```

**適用条件**:
- 3つ以上の独立したタスクがある
- 各タスクが異なるファイル・コンポーネントを対象としている
- タスク間に依存関係がない

#### パターン2: 並列調査・レビュー

トラブルシューティングや逆順レビューで複数の視点から同時に調査します。

```text
チームリーダー（sdd-documentation）
    │
    ├── チームメンバーA: 要件↔設計の整合性チェック
    ├── チームメンバーB: 設計↔タスクの整合性チェック
    └── チームメンバーC: 実装↔ドキュメントの同期チェック
```

#### パターン3: 競合仮説によるデバッグ

バグの原因が不明な場合、複数のチームメンバーが異なる仮説を並列で調査します。

```text
チームリーダー（sdd-troubleshooting）
    │
    ├── チームメンバーA: 仮説1を調査（データフロー問題）
    ├── チームメンバーB: 仮説2を調査（認証トークン問題）
    └── チームメンバーC: 仮説3を調査（非同期処理問題）
```

**重要**: チームメンバー間で互いの発見を共有し、仮説を検証・反証させる。

#### パターン4: クロスレイヤー開発

フロントエンド・バックエンド・テストにまたがる変更を並列で実装します。

```text
チームリーダー（sdd-documentation）
    │
    ├── チームメンバーA: フロントエンドコンポーネント実装
    ├── チームメンバーB: バックエンドAPI実装
    └── チームメンバーC: テスト作成
```

### チームを使用しない場面

以下の場合はサブエージェント（従来のTask tool）を使用:

| 状況 | 理由 |
|------|------|
| 順序依存のタスク | 前のタスクの結果が次に必要 |
| 同一ファイルの編集 | ファイル競合が発生する |
| 1-2個のタスク | チームのオーバーヘッドが利益を超える |
| 結果のみ必要 | チームメンバー間の議論が不要 |

### チーム運用ルール

1. **デリゲートモード推奨**: リーダーは調整に専念し、自ら実装しない（Shift+Tabで切替）
2. **プラン承認を要求**: リスクの高いタスクではチームメンバーにプラン承認を要求
3. **ファイル競合回避**: 各チームメンバーが異なるファイルセットを所有
4. **タスク同期**: チームメンバーのタスク完了時にdocs/tasks/とTodoWriteの両方を更新
5. **完了待機**: リーダーはチームメンバーの完了を待ってから次のフェーズに進む

### チーム活用ワークフロー（新規開発）

```text
1. 初期化 → docs/ディレクトリ構造を作成
      ↓
2. requirements-defining → docs/requirements/
      ↓ ユーザー確認・承認
3. software-designing → docs/design/
      ↓ ユーザー確認・承認
4. task-planning → docs/tasks/
      ↓ ユーザー確認・承認
      ↓ ★ TodoWriteにタスク一覧を同期 ★
5. ドキュメント逆順レビュー
      ↓ （エージェントチームで並列レビュー可能）
6. task-executing → 実装コード
      ↓ ★ エージェントチームで並列実行 ★
      ↓ ★ 完了ごとにTodoWriteのステータスも更新 ★
7. 実装逆順レビュー → 完了
```

## タスク同期プロトコル

### 概要

SDDスキルで管理するdocs/tasks/のタスクと、Claude Codeが内部で管理するTodoWriteのタスクを同期します。これにより、ユーザーはClaude CodeのUI上でリアルタイムにタスクの進捗を確認でき、docs/tasks/には詳細な実装仕様が残ります。

### 同期のタイミング

| イベント | SDD (docs/tasks/) | TodoWrite | 方向 |
|---------|-------------------|-----------|------|
| タスク計画完了時 | TASK-XXX.md作成 | todoを作成 | SDD → TodoWrite |
| タスク開始時 | ステータス: IN_PROGRESS | status: in_progress | SDD → TodoWrite |
| タスク完了時 | ステータス: DONE | status: completed | SDD → TodoWrite |
| タスクブロック時 | ステータス: BLOCKED | （備考追記） | SDD → TodoWrite |
| トラブルシュートでタスク追加 | 新規TASK-XXX.md | todoを追加 | SDD → TodoWrite |

### ステータスマッピング

| SDD (docs/tasks/) | TodoWrite | 説明 |
|-------------------|-----------|------|
| `TODO` | `pending` | 未着手 |
| `IN_PROGRESS` | `in_progress` | 実行中 |
| `DONE` | `completed` | 完了 |
| `BLOCKED` | `pending`（備考付き） | ブロック中 |
| `REVIEW` | `in_progress` | レビュー中 |

### 同期の実装方法

#### タスク計画完了時（task-planning）

docs/tasks/のタスクを作成した後、TodoWriteを呼び出してタスク一覧をセットする:

```text
【TodoWrite同期】
task-planningでタスクを作成した後、以下の形式でTodoWriteを更新:

todos = [
  { content: "[TASK-001] タスクタイトル", status: "pending", activeForm: "[TASK-001] タスクタイトルを実装中" },
  { content: "[TASK-002] タスクタイトル", status: "pending", activeForm: "[TASK-002] タスクタイトルを実装中" },
  ...
]
```

#### タスク実行時（task-executing）

各タスクの開始・完了時にTodoWriteのステータスも更新:

```text
1. タスク開始 → TASK-XXX.mdをIN_PROGRESSに → TodoWriteでin_progressに
2. タスク完了 → TASK-XXX.mdをDONEに → TodoWriteでcompletedに
3. 次のタスクへ → 次のTASK-XXXをin_progressに
```

#### トラブルシュート時（sdd-troubleshooting）

修正タスクが追加された場合、TodoWriteにも追加:

```text
修正タスク追加 → docs/tasks/にTASK-XXX.md追加 → TodoWriteにpendingで追加
```

### 注意事項

- **SDDが正（Source of Truth）**: 詳細な仕様・受入基準・TDD手順はdocs/tasks/に記載
- **TodoWriteは可視化用**: ユーザーへの進捗表示が主目的
- **タスクIDを含める**: TodoWriteのcontentには必ず`[TASK-XXX]`を含め、対応を明確にする
- **フェーズ情報を含める**: 必要に応じて`[Phase-1/TASK-001]`の形式でフェーズも記載

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
