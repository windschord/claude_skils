---
name: jules-api
description: Jules REST APIを使用してタスクを対話的に依頼・管理する。セッション作成・プラン承認・メッセージ送信・進捗監視をAPI経由で行い、Claudeと協調してタスクを完遂する。ベースブランチ指定とPR自動作成に対応。Do NOT use for JULES_API_KEY未設定の環境でのタスク実行（task-executingを使用すること）。
metadata:
  version: "1.0.0"
---

# Jules API統合スキル

Jules REST APIを使用して、docs/sdd/tasks/に記載されたタスクをGoogleの非同期コーディングエージェントJulesに対話的に依頼・管理するスキルです。

## 概要

このスキルは以下の機能を提供します:
- Jules REST APIを使用したセッション（タスク）の作成・管理
- ベースブランチの指定によるPR自動作成
- プラン承認ワークフロー（Claudeがプランを確認し、ユーザーと協議して承認）
- アクティビティ監視によるリアルタイム進捗追跡
- セッションへのメッセージ送信による対話的な指示追加
- Claudeとの協調作業（Julesの出力をClaudeが評価・フィードバック）

## 前提条件

### 環境変数

```bash
export JULES_API_KEY="your-api-key-here"
```

APIキーはJulesウェブアプリの設定ページ（Settings）で作成します。最大3つのAPIキーを保持できます。

### GitHubアプリのインストール

Jules APIでリポジトリを操作するには、事前にJulesウェブアプリからJules GitHubアプリをリポジトリにインストールする必要があります。

## このスキルを使用する場面

### タスク実行時
- docs/sdd/tasks/のタスクをJulesに依頼したい場合
- ベースブランチを指定してPRを自動作成したい場合
- Julesのプランを確認してから実行させたい場合
- Julesに対話的に追加指示を送りたい場合

### Claude協調作業時
- JulesのプランをClaudeが評価し、改善提案を行う場合
- Julesの実装結果をClaudeがレビューする場合
- 複雑なタスクでJulesとClaudeの役割を分担する場合

## ワークフロー

### 基本的な実行フロー

```text
1. 環境変数 JULES_API_KEY の確認
   ↓
2. docs/sdd/tasks/を読み取り、TODO状態のタスクをリスト表示
   ↓
3. ユーザーがタスクを選択
   ↓
4. ソース（リポジトリ）の確認（List Sources API）
   ↓
5. ユーザーにベースブランチを確認
   ↓
6. セッション作成（Create Session API）
   - prompt: タスクの依頼文
   - sourceContext: リポジトリとブランチ
   - automationMode: AUTO_CREATE_PR
   - requirePlanApproval: true（推奨）
   ↓
7. アクティビティ監視（List Activities API）
   - プラン生成を待機
   ↓
8. プランの確認と承認
   - Claudeがプランを評価
   - ユーザーに確認
   - Approve Plan API で承認
   ↓
9. 実行中の進捗監視
   - アクティビティを定期確認
   - 必要に応じてメッセージ送信（Send Message API）
   ↓
10. 完了確認
    - セッション状態を確認（Get Session API）
    - PR URLを取得
   ↓
11. docs/sdd/tasks/を更新（ステータスをREVIEWに変更）
   ↓
12. レビュー完了後、DONEにマーク
```

### 詳細な実行手順

#### ステップ1: 環境確認

```bash
# JULES_API_KEY の存在確認
if [ -z "$JULES_API_KEY" ]; then
  echo "Error: JULES_API_KEY is not set"
  exit 1
fi
```

APIキーが未設定の場合はユーザーに設定を依頼して中断します。

#### ステップ2: ソースの確認

```bash
curl -s 'https://jules.googleapis.com/v1alpha/sources' \
  -H "x-goog-api-key: $JULES_API_KEY" | jq .
```

接続済みリポジトリの一覧を取得し、対象リポジトリのソース名（`sources/github/{owner}/{repo}`形式）を特定します。

#### ステップ3: タスクの選択とベースブランチの確認

```text
ファシリテーター: docs/sdd/tasks/からタスクを確認しました。
                  以下のタスクが利用可能です:

                  1. Task 1.1: ユーザー認証APIの実装
                  2. Task 1.2: データモデルの定義

                  どのタスクをJulesに依頼しますか?

ユーザー: 1

ファシリテーター: ベースブランチ（PR作成先）を指定してください。
                  （例: main, develop, feature/xxx）

ユーザー: develop
```

#### ステップ4: セッション作成

```bash
curl -s 'https://jules.googleapis.com/v1alpha/sessions' \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{
    "prompt": "タスク: ユーザー認証APIの実装（TASK-001）\n\n概要:\nPOST /api/auth/login と POST /api/auth/logout のエンドポイントを実装してください。\n\n受入基準:\n- src/api/auth.tsが存在する\n- テストが通過する\n\n技術的文脈:\n- Next.js 14 App Router\n- JWT + bcrypt",
    "sourceContext": {
      "source": "sources/github/owner/repo",
      "githubRepoContext": {
        "startingBranch": "develop"
      }
    },
    "automationMode": "AUTO_CREATE_PR",
    "requirePlanApproval": true,
    "title": "TASK-001: ユーザー認証APIの実装"
  }'
```

レスポンスからセッションIDを取得して記録します。

#### ステップ5: プラン承認ワークフロー

セッション作成後、Julesがプランを生成するまでアクティビティを監視します:

```bash
# アクティビティを確認
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}/activities" \
  -H "x-goog-api-key: $JULES_API_KEY" | jq .
```

プラン生成（`planGenerated`アクティビティ）を検出したら:

1. **Claudeがプランを評価**: タスクの受入基準と照合し、過不足を確認
2. **ユーザーに確認**: プラン内容と評価結果を表示し、承認を求める
3. **承認実行**:

```bash
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}:approvePlan" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY"
```

プランに問題がある場合は、メッセージ送信で修正を依頼:

```bash
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}:sendMessage" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{
    "prompt": "プランを修正してください。テストファイルの作成が含まれていません。受入基準にテスト通過が含まれているため、テストファイルも作成してください。"
  }'
```

#### ステップ6: 進捗監視と対話

実行中はアクティビティを定期的に確認し、ユーザーに進捗を報告します:

```text
ファシリテーター: [jules-api] TASK-001 進捗確認
                  - セッション状態: 実行中
                  - 最新アクティビティ: progressUpdate
                  - 内容: src/api/auth.tsの実装を完了、テストファイルの作成中

                  追加指示はありますか?

ユーザー: エラーハンドリングも含めてください

ファシリテーター: Julesに追加指示を送信します。
```

```bash
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}:sendMessage" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{
    "prompt": "エラーハンドリングも実装してください。認証失敗時に適切なHTTPステータスコードとエラーメッセージを返すようにしてください。"
  }'
```

#### ステップ7: 完了確認とPR取得

セッション完了を検知したら、セッション情報からPR URLを取得します:

```bash
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}" \
  -H "x-goog-api-key: $JULES_API_KEY" | jq '.output'
```

#### ステップ8: docs/sdd/tasks/の更新

```markdown
## 実行情報
**実行方式**: Jules API
**Jules Session ID**: {SESSION_ID}
**PR作成先**: develop
**開始日時**: 2026-03-29 10:30
**PR番号**: #42
**PR URL**: https://github.com/owner/repo/pull/42
**PR作成日時**: 2026-03-29 12:15
```

## Jules依頼文の原則

### 基本構造

以下の依頼文フォーマットを使用します:

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

コミット規約:
- feat/fix/docs等のprefixを使用
- タスクIDを含める
```

**注意**: PRの作成先ブランチは依頼文ではなく`sourceContext.githubRepoContext.startingBranch`パラメータで指定します。

### 日本語での依頼

依頼文は日本語で記述します。技術用語・ファイルパス・コマンドは英語のまま使用してください。

## セッション作成パラメータ

### 必須パラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `prompt` | string | タスクの依頼文 |

### 推奨パラメータ

| パラメータ | 型 | 説明 | デフォルト |
|-----------|-----|------|-----------|
| `sourceContext.source` | string | ソース名（`sources/github/{owner}/{repo}`） | - |
| `sourceContext.githubRepoContext.startingBranch` | string | ベースブランチ | リポジトリのデフォルトブランチ |
| `automationMode` | string | `AUTO_CREATE_PR`でPR自動作成 | PR自動作成なし |
| `requirePlanApproval` | boolean | `true`でプラン承認を要求 | `false`（自動承認） |
| `title` | string | セッションタイトル | 自動生成 |

## Claude協調ワークフロー

### プラン評価

Julesがプランを生成した際、Claudeが以下の観点で評価します:

1. **受入基準との整合**: タスクの受入基準がプランのステップでカバーされているか
2. **技術的妥当性**: 適切な技術・パターンが選択されているか
3. **過不足の確認**: 不要なステップがないか、欠けているステップがないか
4. **リスク評価**: 既存コードへの影響、破壊的変更のリスク

評価結果をユーザーに提示し、承認・修正依頼・却下を判断してもらいます:

```text
ファシリテーター: Julesが以下のプランを生成しました:

                  1. src/api/auth.tsを作成
                  2. ログインエンドポイントを実装
                  3. ログアウトエンドポイントを実装

                  [Claudeの評価]
                  - 受入基準「テストが通過する」に対応するテスト作成ステップが不足
                  - bcryptによるハッシュ化の記述なし

                  推奨: テスト作成ステップの追加をJulesに依頼してから承認

                  どうしますか?
                  1. 承認する
                  2. 修正を依頼してから承認
                  3. 却下する
```

### 実行中のフィードバック

Julesの実行中にClaudeがアクティビティを分析し、必要に応じてフィードバックを提案します:

- コードの品質問題を検知した場合: メッセージ送信で修正を依頼
- 進行方向が受入基準から逸れている場合: 軌道修正の指示を送信
- 追加情報が必要な場合: ユーザーに確認してからJulesに伝達

## 複数タスクの並行処理

### 並行セッションの作成

依存関係のないタスクは複数のセッションを同時に作成できます:

```text
1. 並行実行可能なタスクを特定（依存関係グラフ分析）
2. 各タスクのセッションを作成（ベースブランチは共通）
3. 全セッションのアクティビティを監視
4. 各セッションのプランを順次確認・承認
5. 完了したセッションからPR情報を取得
6. 全PR完了後にdocs/sdd/tasks/を更新
```

### セッション一覧の確認

```bash
curl -s 'https://jules.googleapis.com/v1alpha/sessions?pageSize=10' \
  -H "x-goog-api-key: $JULES_API_KEY" | jq '.sessions[] | {name, title, state}'
```

## docs/sdd/tasks/更新の原則

### ステータス遷移

```text
TODO → IN_PROGRESS（セッション作成後）→ REVIEW（PR作成済み）→ DONE（PRマージ済み）
```

### 実行情報の段階的記録

**段階1: セッション作成時（即時記録）**

```markdown
## 実行情報
**実行方式**: Jules API
**Jules Session ID**: {SESSION_ID}
**PR作成先**: {ベースブランチ}
**開始日時**: {日時}
```

**段階2: PR作成時（セッション完了後に追記）**

```markdown
**PR番号**: #{PR番号}
**PR URL**: {PR URL}
**PR作成日時**: {日時}
```

**段階3: PRマージ時（レビュー承認後に追記）**

```markdown
**マージ日時**: {日時}
```

## エラーハンドリング

### API認証エラー

```text
HTTP 401/403 の場合:
1. JULES_API_KEY が正しく設定されているか確認
2. APIキーの有効期限を確認
3. Julesウェブアプリで新しいキーを生成
```

### セッション作成エラー

```text
1. ソース名が正しいか確認（List Sources APIで確認）
2. GitHubアプリがリポジトリにインストールされているか確認
3. ブランチ名が存在するか確認
4. エラー内容をユーザーに報告
```

### セッション実行エラー

```text
1. アクティビティからエラー内容を確認
2. メッセージ送信で修正を依頼
3. 解決しない場合はセッションを放棄し、新規セッションまたはローカル実行にフォールバック
4. docs/sdd/tasks/をBLOCKEDに更新
```

### ネットワークエラー

APIリクエスト失敗時は最大4回まで指数バックオフ（2s, 4s, 8s, 16s）でリトライします。

## 制約事項

### APIの制限

- Jules APIはアルファ版であり、仕様変更の可能性がある
- APIキーは最大3つまで保持可能
- セッション一覧のページサイズは1-100（デフォルト30）
- アクティビティ一覧のページサイズは1-100（デフォルト50）

### 実行の制限

以下の場合はJulesへの依頼を控えます:
1. **タスクの曖昧性**: 受入基準が不明確な場合は依頼しない
2. **リスクの高い操作**: 本番環境への直接変更は行わない
3. **ユーザーの判断が必要な場合**: 技術選択やアーキテクチャの決定

## リソース

### リファレンス

- APIリファレンス: `jules-api/references/api_reference_ja.md`

### 外部リンク

- Jules API公式ドキュメント: https://developers.google.com/jules/api
- Jules APIリファレンス: https://developers.google.com/jules/api/reference/rest
- Julesウェブアプリ: https://jules.google
