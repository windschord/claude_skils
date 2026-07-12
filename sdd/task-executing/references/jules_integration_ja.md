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
│  Q1. JULES_API_KEY(_OP_URI) が設定されているか？              │
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

Jules認証情報（`JULES_API_KEY_OP_URI` または `JULES_API_KEY`）が設定されている場合に使用します。詳細は `utility/jules-api/SKILL.md` を参照してください。

#### ステップ1: ソースと開発ブランチの確認

```text
1. utility/jules-api/scripts/jules.sh list-sources でリポジトリのソース名を取得
   （全ページを自動取得するため、接続先が多い場合でも対象リポジトリを見落とさない。
    curlを直接叩く場合は pageToken による全ページ取得を必ず行うこと）
2. ユーザーに開発ブランチ（PR作成先）を確認
3. sourceContext パラメータに設定
```

#### ステップ2: タスクの依存関係分析と並列グループ化

```text
1. TODO状態のタスクを取得
   - Issueモード（デフォルト）: mcp__github__list_issues（labels: ["sdd:task","sdd:status/todo"], state: open）
   - ファイルモード: docs/sdd/tasks/index.mdから取得
2. 依存関係グラフを構築（Issueモードは依存Issue番号・sdd:group-* ラベルから）
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
4. 各タスクの状態に応じてタスク状態を更新（Issueモード: ラベル付け替え/close / ファイルモード: docs/sdd/tasks/）:

   セッション状態     → SDD状態       → Issueモード                  → TodoWrite
   ──────────────────────────────────────────────────────────────────────────
   作業中            → IN_PROGRESS   → sdd:status/in-progress        → in_progress
   PR作成済み        → REVIEW        → sdd:status/review             → in_progress（[REVIEW]付記）
   PRマージ済み      → DONE          → Issueをclose（completed）     → completed
```

> **PRとIssueの紐付け**: JulesセッションのプロンプトやPR本文に `(#Issue番号)` を含めることで、PRとIssueを相互参照できる（あくまで参照用）。Issueのclose（DONE）はステップ6のupdate処理で明示的に行う。

#### ステップ6: 完了確認とPR取得

```text
1. Get Session API でセッション状態を確認
2. session.output からPR情報（URL、タイトル）を取得
3. PRの実際の差分を確認する（サマリーだけで判断しない）。
   タスクのスコープ外の削除・既存テストの削除・既存公開APIの削除がないか確認し、
   問題があればマージ・DONE更新前にSend Message APIで修正を依頼する
   （詳細は utility/jules-api/SKILL.md の「PR差分の確認（必須）」を参照）
4. タスク状態を更新（Issueモード: 対応Issueをclose / ファイルモード: docs/sdd/tasks/）
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
    ├── タスク状態の更新（Issueモード: Issue close / ファイルモード: docs/sdd/tasks/）
    └── TodoWriteの同期

手順:
1. リーダーがタスクを分析し、Jules向け/ローカル向けに分類
2. Jules向けタスクの複数セッションをAPI経由で作成
3. ローカル向けタスクはAgent Teams/Task toolで並列実行
4. リーダーはList Activities APIで定期的にJulesの進捗を確認
5. プラン承認→実行監視→完了確認の対話ループ
6. PR作成されたらレビューし、問題なければマージ
7. 全タスク完了後にタスク状態（Issueモード: 各Issue close / ファイルモード: docs/sdd/tasks/）とTodoWriteを一括更新
8. 逆順レビューを実施
```

### エラーハンドリング（Jules固有）

```text
1. セッション作成が失敗した場合:
   - 【重要】タイムアウト等の曖昧な失敗時、ユーザーの作業承認を待たずに再実行してはならない。
     リクエストがJules側で成立していた場合、再実行は同一タスクの重複セッションを生成する
     （utility/jules-api/scripts/jules.sh create-session は同名タイトルの既存セッションを検知して
     自動で作成を中断するが、生のcurlを使う場合は utility/jules-api/scripts/jules.sh list-sessions で重複がないか
     必ず確認してから再実行する）
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
   【重要】新しいセッションを作成してはならない。新セッションは新ブランチ・新PRを生成し、
   元のPRを更新できない。必ず既存セッションを再利用すること。
   - タスクファイルの「Jules Session ID」を取得
   - Send Message API で既存セッションに修正指示を送信
   - 「既存のPRブランチを更新してください」と明記する
   - セッションが終了済みで応答しない場合のみ、タスクファイルの「Jules ブランチ名」を
     ローカルにチェックアウトして修正・プッシュすることで既存PRを更新する
     （startingBranch に Jules の作業ブランチを指定しても既存PRへの追加コミットにはならない）
   - 対応内容をタスクファイルの「レビュー対応履歴」セクションに記録
   詳細は utility/jules-api/SKILL.md の「レビュー指摘・仕様変更対応フロー」を参照

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
