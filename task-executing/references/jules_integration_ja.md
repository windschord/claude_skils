# Jules統合実行モード


<!-- TOC -->
## 目次

- [概要](#概要)
  - [実行モードの判定](#実行モードの判定)
  - [Jules APIモードの実行ステップ](#jules-apiモードの実行ステップ)
  - [Jules CLIモードの実行ステップ](#jules-cliモードの実行ステップ)
  - [タスクファイルへの段階的記録](#タスクファイルへの段階的記録)
  - [ハイブリッドモード](#ハイブリッドモード)
  - [Jules + Agent tool並列実行の連携パターン](#jules--agent-tool並列実行の連携パターン)
  - [エラーハンドリング（Jules固有）](#エラーハンドリングjules固有)
- [制約事項](#制約事項)
  - [自動実行を行わない場合](#自動実行を行わない場合)
<!-- /TOC -->

task-executingスキルにおけるJules統合（API/CLI）の詳細ガイドです。

## 概要

Googleの非同期コーディングエージェントJulesが利用可能な環境では、タスクの実装をJulesに委任できます。Julesは開発ブランチに対してPR（Pull Request）を作成し、レビュー→マージのフローでタスクを完了させます。

JulesとのインテグレーションにはAPIモード（推奨）とCLIモードの2つがあります:

| 項目 | APIモード（推奨） | CLIモード |
|------|------------------|-----------|
| スキル | jules-api | jules-cli |
| 通信方式 | REST API（curl） | CLIコマンド（`jules`） |
| 認証 | 環境変数 `JULES_API_KEY` | `jules auth login` |
| 対話性 | 双方向（メッセージ送受信、プラン承認） | 一方向（依頼→結果取得） |
| ブランチ指定 | APIパラメータで明示的に指定 | 依頼文テキストで指定 |
| Claude協調 | プラン評価・フィードバック送信 | なし |

### 実行モードの判定

タスク実行フェーズの開始時に、以下のフローで実行モードを判定します:

```text
┌──────────────────────────────────────────────────────────────┐
│                   実行モード判定フロー                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Q1. JULES_API_KEY が設定されているか？                       │
│      YES → Jules APIモード判定へ（Q2へ）                      │
│      NO  → Q1b. Jules CLIが利用可能か？（jules --version）    │
│             YES → Jules CLIモード判定へ（Q2へ）               │
│             NO  → ローカル実行モード（Agent/Agent Teams）     │
│                                                              │
│  Q2. 開発ブランチが指定されているか？                         │
│      YES → Q3へ                                              │
│      未指定 → ユーザーに開発ブランチを確認 → Q3へ             │
│                                                              │
│  Q3. ユーザーがJules実行を希望するか？                        │
│      全タスクJules → Jules APIモード / Jules CLIモード         │
│      一部Jules     → ハイブリッドモード                       │
│      Jules不要     → ローカル実行モード                       │
│                                                              │
│  結果:                                                       │
│  Jules APIモード     → 全タスクをAPI経由で依頼、対話的管理     │
│  Jules CLIモード     → 全タスクをCLI経由で依頼、PRベース      │
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

CLIモードと同様にdocs/sdd/tasks/index.mdからTODO状態のタスクを取得し、依存関係グラフを構築して並列実行可能なグループを特定します。

#### ステップ3: セッション作成（タスク依頼）

```bash
# 各タスクについてセッションを作成
curl -s 'https://jules.googleapis.com/v1alpha/sessions' \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{
    "prompt": "タスクの依頼文",
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
```

#### ステップ6: 完了確認とPR取得

```text
1. Get Session API でセッション状態を確認
2. session.output からPR情報（URL、タイトル）を取得
3. docs/sdd/tasks/ を更新
```

### Jules CLIモードの実行ステップ

#### ステップ1: 開発ブランチの確認

```text
1. 全体開発で使用する開発ブランチを確認（ユーザーに確認）
2. Julesに依頼する際、PRのターゲットブランチとして開発ブランチを指定
3. JulesはPRごとに自動でフィーチャーブランチを作成する
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

4. 各グループ内のタスクは複数のJulesインスタンスで非同期に並行実行
```

#### ステップ3: Jules依頼文の作成

各タスクについて、以下の情報を含む依頼文を作成します:

```text
タスク: [タスクタイトル]（[TASK-XXX]）

概要:
[タスクの詳細な説明]

受入基準:
- [基準1]
- [基準2]

技術的文脈:
- [フレームワーク、ライブラリ]
- [参照すべきファイルやコード]
- [制約事項]

PR作成先（開発ブランチ）: [ブランチ名]

コミット規約:
- feat/fix/docs等のprefixを使用
- タスクIDを含める（例: feat(auth): implement login endpoint [TASK-001]）
```

#### ステップ4: 複数Julesへの非同期依頼

並列実行可能なタスクは、複数のjulesコマンドを連続投入し、非同期タスクとして並行進行させます。各julesコマンドは即座に制御を返し、Jules側で非同期に作業が進行します:

```bash
# グループA: 3タスクを連続投入（各コマンドは非同期タスクを作成して即座に返る）
jules "$(cat <<'EOF'
タスク: ユーザー認証APIの実装（TASK-001）
...
PR作成先: develop
EOF
)"

jules "$(cat <<'EOF'
タスク: データモデルの定義（TASK-002）
...
PR作成先: develop
EOF
)"

jules "$(cat <<'EOF'
タスク: 設定ファイルの作成（TASK-003）
...
PR作成先: develop
EOF
)"
```

#### ステップ5: 進捗追跡とPR管理

```text
1. jules listで全タスクの進捗を一覧確認
2. 各タスクの状態に応じてdocs/sdd/tasks/を更新:

   Jules状態        → SDD状態       → TodoWrite
   ─────────────────────────────────────────────
   作業中           → IN_PROGRESS   → in_progress
   PR作成済み       → REVIEW        → in_progress（[REVIEW]付記）
   PRマージ済み     → DONE          → completed

3. PR作成時にPR番号をタスクファイルに記録:
   - Jules Task ID: task-abc123
   - PR: #42
   - PRブランチ: jules/task-001-auth-api

4. PRレビューはユーザーまたはリーダーが実施
5. PRマージ後にDONEに遷移
```

#### ステップ6: グループ間の順次実行

```text
グループA完了（全PRマージ済み）
      ↓
開発ブランチを最新に更新（git pull）
      ↓
グループBのタスクをJulesに依頼
      ↓
以降繰り返し
```

### タスクファイルへの段階的記録

Julesで実行したタスクには、進行に応じて段階的に情報を追記します:

**段階1: Jules依頼時（IDを即時記録）**

APIモード:
```markdown
## 実行情報
**実行方式**: Jules API
**Jules Session ID**: {SESSION_ID}
**PR作成先**: develop
**開始日時**: 2025-01-15 10:30
```

CLIモード:
```markdown
## 実行情報
**実行方式**: Jules CLI
**Jules Task ID**: task-abc123
**PR作成先**: develop
**開始日時**: 2025-01-15 10:30
```

**段階2: PR作成時（PR番号・ブランチを追記）**

```markdown
**PR番号**: #42
**PRブランチ**: jules/task-001-auth-api
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
├── Jules依頼管理:
│   ├── Jules-1: TASK-001（PR #41）
│   ├── Jules-2: TASK-002（PR #42）
│   └── Jules-3: TASK-003（PR #43）
├── ローカルAgent:
│   └── Agent-1: TASK-004（ローカル環境依存タスク）
└── 進捗管理:
    ├── jules listで定期確認
    ├── PRレビュー・マージ管理
    ├── docs/sdd/tasks/の更新
    └── TodoWriteの同期

手順:
1. リーダーがタスクを分析し、Jules向け/ローカル向けに分類
2. Jules向けタスクを複数のjulesコマンドで連続投入し非同期依頼
3. ローカル向けタスクはAgent Teams/Task toolで並列実行
4. リーダーはjules listで定期的にJulesの進捗を確認
5. PR作成されたらレビューし、問題なければマージ
6. 全タスク完了後にdocs/sdd/tasks/とTodoWriteを一括更新
7. 逆順レビューを実施
```

### エラーハンドリング（Jules固有）

```text
1. Jules依頼が失敗した場合:
   - jules status <task-id>でエラー内容を確認
   - 依頼文を修正して再依頼（jules retry <task-id>）
   - 繰り返し失敗する場合はローカル実行にフォールバック

2. PRにコンフリクトが発生した場合:
   - 開発ブランチの最新を取得
   - コンフリクトを解消
   - 必要に応じてJulesに再依頼

3. PRレビューで問題が見つかった場合:
   - Julesに修正を依頼（新規タスクとして）
   - または手動で修正してPRを更新
   - 修正内容をタスクファイルに記録

4. Julesが長時間応答しない場合:
   - jules status <task-id>で状態確認
   - 必要に応じてjules cancel <task-id>でキャンセル
   - ローカル実行にフォールバック
```

## 制約事項

### 自動実行を行わない場合

1. **タスクの曖昧性**: 受入基準が明確でない、実装方法が複数考えられる
2. **リスクの高い操作**: 本番環境への変更、データベースの削除操作
3. **ユーザーの判断が必要**: 技術選択、アーキテクチャの決定

これらの場合はユーザーに確認を求めます。
