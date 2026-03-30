# Jules API統合実行モード


<!-- TOC -->
## 目次

- [概要](#概要)
  - [実行モードの判定](#実行モードの判定)
  - [Jules APIモードの実行ステップ](#jules-apiモードの実行ステップ)
  - [タスクファイルへの段階的記録](#タスクファイルへの段階的記録)
  - [ハイブリッドモード](#ハイブリッドモード)
  - [Jules + Agent tool並列実行の連携パターン](#jules--agent-tool並列実行の連携パターン)
  - [エラーハンドリング（Jules固有）](#エラーハンドリングjules固有)
- [制約事項](#制約事項)
  - [自動実行を行わない場合](#自動実行を行わない場合)
<!-- /TOC -->

task-executingスキルにおけるJules API統合の詳細ガイドです。

## 概要

Googleの非同期コーディングエージェントJulesが利用可能な環境では、タスクの実装をJulesに委任できます。Jules REST APIを使用してセッションを作成し、ベースブランチを指定してPR（Pull Request）を自動作成させます。Claudeと協調してプラン承認・進捗監視・対話的フィードバックを行い、レビュー→マージのフローでタスクを完了させます。

### 実行モードの判定

タスク実行フェーズの開始時に、以下のフローで実行モードを判定します:

```text
┌──────────────────────────────────────────────────────────────┐
│                   実行モード判定フロー                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Q1. JULES_API_KEY が設定されているか？                       │
│      YES → Q2へ                                              │
│      NO  → ローカル実行モード（Agent/Agent Teams）            │
│                                                              │
│  Q2. 開発ブランチが指定されているか？                         │
│      YES → Q3へ                                              │
│      未指定 → ユーザーに開発ブランチを確認 → Q3へ             │
│                                                              │
│  Q3. ユーザーがJules実行を希望するか？                        │
│      全タスクJules → Jules APIモード                          │
│      一部Jules     → ハイブリッドモード                       │
│      Jules不要     → ローカル実行モード                       │
│                                                              │
│  結果:                                                       │
│  Jules APIモード     → 全タスクをAPI経由で依頼、対話的管理     │
│  ハイブリッドモード   → 一部Jules（PR）、一部ローカル          │
│  ローカル実行モード   → Agent/Agent Teamsで直接実装            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Jules APIモードの実行ステップ

JULES_API_KEY が設定されている場合に使用します。詳細は `jules-api/SKILL.md` を参照してください。

#### ステップ1: ソースと開発ブランチの確認

```text
1. List Sources API でリポジトリのソース名を取得
   curl -s 'https://jules.googleapis.com/v1alpha/sources' \
     -H "x-goog-api-key: $JULES_API_KEY"
2. ユーザーに開発ブランチ（PR作成先）を確認
3. sourceContext パラメータに設定
```

#### ステップ2: タスクの依存関係分析と並列グループ化

```text
1. docs/sdd/tasks/index.mdからTODO状態のタスクを取得
2. 依存関係グラフを構築
3. 並列実行可能なグループを特定:

   例:
   グループA（並列実行可能）:
   - TASK-001: ユーザー認証API（依存なし）
   - TASK-002: データモデル定義（依存なし）
   - TASK-003: 設定ファイル作成（依存なし）

   グループB（グループA完了後）:
   - TASK-004: 認証ミドルウェア（依存: TASK-001）
   - TASK-005: APIバリデーション（依存: TASK-001, TASK-002）

4. 各グループ内のタスクは複数のJulesセッションで非同期に並行実行
```

#### ステップ3: セッション作成（タスク依頼）

各タスクについて、以下の情報を含むセッションを作成します:

```bash
# 各タスクについてセッションを作成
curl -s 'https://jules.googleapis.com/v1alpha/sessions' \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{
    "prompt": "タスク: ユーザー認証APIの実装（TASK-001）\n\n概要:\n...\n\n受入基準:\n- ...\n\n技術的文脈:\n- ...\n\nコミット規約:\n- feat/fix/docs等のprefixを使用\n- タスクIDを含める",
    "sourceContext": {
      "source": "sources/github/owner/repo",
      "githubRepoContext": {
        "startingBranch": "develop"
      }
    },
    "automationMode": "AUTO_CREATE_PR",
    "requirePlanApproval": true,
    "title": "TASK-XXX: タスクタイトル"
  }'
```

#### ステップ4: プラン承認ワークフロー

```text
1. List Activities API でプラン生成（planGenerated）を検出
2. Claudeがプランを評価（受入基準との整合、技術的妥当性）
3. ユーザーに確認
4. Approve Plan API で承認（または Send Message API で修正依頼）
```

#### ステップ5: 進捗追跡と対話

```text
1. List Activities API で進捗を定期確認
2. 必要に応じて Send Message API で追加指示
3. Claudeがアクティビティを分析し、問題を検知した場合はフィードバック
4. 各タスクの状態に応じてdocs/sdd/tasks/を更新:

   セッション状態     → SDD状態       → TodoWrite
   ─────────────────────────────────────────────
   作業中            → IN_PROGRESS   → in_progress
   PR作成済み        → REVIEW        → in_progress（[REVIEW]付記）
   PRマージ済み      → DONE          → completed
```

#### ステップ6: 完了確認とPR取得

```text
1. Get Session API でセッション状態を確認
2. session.output からPR情報（URL、タイトル）を取得
3. docs/sdd/tasks/ を更新
```

#### ステップ7: グループ間の順次実行

```text
グループA完了（全PRマージ済み）
      ↓
開発ブランチを最新に更新（git pull）
      ↓
グループBのタスクをJulesに依頼（新セッション作成）
      ↓
以降繰り返し
```

### タスクファイルへの段階的記録

Julesで実行したタスクには、進行に応じて段階的に情報を追記します:

**段階1: セッション作成時（Session IDを即時記録）**

```markdown
## 実行情報
**実行方式**: Jules API
**Jules Session ID**: {SESSION_ID}
**PR作成先**: develop
**開始日時**: 2025-01-15 10:30
```

**段階2: PR作成時（PR番号・URLを追記）**

```markdown
**PR番号**: #42
**PR URL**: https://github.com/owner/repo/pull/42
**PR作成日時**: 2025-01-15 12:15
```

**段階3: PRマージ時（マージ日時を追記、完了日時 = マージ日時）**

```markdown
**マージ日時**: 2025-01-15 14:00
```

### ハイブリッドモード

一部のタスクをJulesに、一部をローカル（Agent/Agent Teams）で実行する場合:

```text
割り当て判定基準:
┌─────────────────────────────────────────────────────────┐
│ Julesに向いているタスク:                                 │
│ - 明確な受入基準がある独立したタスク                      │
│ - 標準的な実装パターン（CRUD、API、モデル定義等）         │
│ - 時間がかかるが定型的な作業                              │
│                                                         │
│ ローカル実行に向いているタスク:                           │
│ - 既存コードの複雑なリファクタリング                      │
│ - 対話的な判断が必要なタスク                              │
│ - ローカル環境固有の作業（Docker設定、環境構築等）        │
│ - 複数ファイルの密結合な変更                              │
└─────────────────────────────────────────────────────────┘
```

### Jules + Agent tool並列実行の連携パターン

Agent tool並列実行とJulesを組み合わせて最大効率を実現するパターン:

```text
チームリーダー（オーケストレーター）
├── Jules依頼管理（API経由）:
│   ├── Session-1: TASK-001（PR #41）
│   ├── Session-2: TASK-002（PR #42）
│   └── Session-3: TASK-003（PR #43）
├── ローカルAgent:
│   └── Agent-1: TASK-004（ローカル環境依存タスク）
└── 進捗管理:
    ├── List Sessions/Activities APIで定期確認
    ├── プラン承認・フィードバック送信
    ├── PRレビュー・マージ管理
    ├── docs/sdd/tasks/の更新
    └── TodoWriteの同期

手順:
1. リーダーがタスクを分析し、Jules向け/ローカル向けに分類
2. Jules向けタスクの複数セッションをAPI経由で作成
3. ローカル向けタスクはAgent Teams/Task toolで並列実行
4. リーダーはList Activities APIで定期的にJulesの進捗を確認
5. プラン承認→実行監視→完了確認の対話ループ
6. PR作成されたらレビューし、問題なければマージ
7. 全タスク完了後にdocs/sdd/tasks/とTodoWriteを一括更新
8. 逆順レビューを実施
```

### エラーハンドリング（Jules固有）

```text
1. セッション作成が失敗した場合:
   - エラーレスポンスを確認（認証、ソース名、ブランチ名）
   - パラメータを修正して再作成
   - 繰り返し失敗する場合はローカル実行にフォールバック

2. セッション実行中にエラーが発生した場合:
   - List Activities API でエラー内容を確認（failedアクティビティ）
   - Send Message API で修正指示を送信
   - 解決しない場合は新規セッションを作成、またはローカル実行にフォールバック

3. PRにコンフリクトが発生した場合:
   - 開発ブランチの最新を取得
   - コンフリクトを解消
   - 必要に応じてJulesに再依頼（新規セッション）

4. PRレビューで問題が見つかった場合:
   - Send Message API でJulesに修正を依頼
   - または手動で修正してPRを更新
   - 修正内容をタスクファイルに記録

5. Julesが長時間応答しない場合:
   - Get Session API でセッション状態を確認
   - List Activities API で最新のアクティビティを確認
   - ローカル実行にフォールバック
```

## 制約事項

### 自動実行を行わない場合

1. **タスクの曖昧性**: 受入基準が明確でない、実装方法が複数考えられる
2. **リスクの高い操作**: 本番環境への変更、データベースの削除操作
3. **ユーザーの判断が必要**: 技術選択、アーキテクチャの決定

これらの場合はユーザーに確認を求めます。
