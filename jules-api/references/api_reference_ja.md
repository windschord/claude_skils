# Jules REST API リファレンス


<!-- TOC -->
## 目次

- [概要](#概要)
- [認証](#認証)
- [ベースURL](#ベースurl)
- [エンドポイント一覧](#エンドポイント一覧)
  - [Sources API](#sources-api)
  - [Sessions API](#sessions-api)
  - [Activities API](#activities-api)
- [リソース定義](#リソース定義)
  - [Session](#session)
  - [Activity](#activity)
  - [SourceContext](#sourcecontext)
  - [SessionOutput](#sessionoutput)
- [エラーハンドリング](#エラーハンドリング)
- [レート制限とリトライ](#レート制限とリトライ)
<!-- /TOC -->

Jules REST API（v1alpha）のリファレンスです。

## 概要

Jules REST APIは3つのコアコンセプトで構成されます:

| コンセプト | 説明 |
|-----------|------|
| **Source** | 入力ソース（GitHubリポジトリ）。事前にJulesウェブアプリからGitHubアプリのインストールが必要 |
| **Session** | 特定のコンテキスト内での一連の作業単位。プロンプトとソースで開始される |
| **Activity** | セッション内の個々のイベント。プラン生成、メッセージ、進捗更新、完了等 |

## 認証

### APIキーの取得

1. [Julesウェブアプリ](https://jules.google)にアクセス
2. Settings ページに移動
3. 新しいAPIキーを作成（最大3つ）

### 環境変数への設定

```bash
export JULES_API_KEY="your-api-key-here"
```

### リクエストヘッダー

すべてのAPIリクエストに以下のヘッダーを付与します:

```text
x-goog-api-key: $JULES_API_KEY
Content-Type: application/json
```

## ベースURL

```text
https://jules.googleapis.com/v1alpha/
```

**注意**: Jules APIはアルファ版です。仕様、APIキー、定義は変更される可能性があります。

## エンドポイント一覧

### Sources API

#### List Sources - ソース一覧

接続済みリポジトリの一覧を取得します。

```text
GET /v1alpha/sources
```

```bash
curl -s 'https://jules.googleapis.com/v1alpha/sources' \
  -H "x-goog-api-key: $JULES_API_KEY"
```

**レスポンス例**:

```json
{
  "sources": [
    {
      "name": "sources/github/owner/repo",
      "displayName": "owner/repo"
    }
  ]
}
```

ソース名は `sources/github/{owner}/{repo}` 形式です。セッション作成時の `sourceContext.source` にこの値を使用します。

### Sessions API

#### Create Session - セッション作成

新しいセッション（タスク）を作成します。

```text
POST /v1alpha/sessions
```

**リクエストボディ**:

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `prompt` | string | 必須 | タスクの依頼文 |
| `title` | string | 任意 | セッションタイトル（未指定時は自動生成） |
| `sourceContext` | SourceContext | 任意 | リポジトリとブランチの指定（リポレスセッションでは不要） |
| `requirePlanApproval` | boolean | 任意 | `true`でプラン承認を要求（デフォルト: `false`で自動承認） |
| `automationMode` | string | 任意 | `AUTO_CREATE_PR`でPR自動作成（デフォルト: PR作成なし） |

```bash
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
    "title": "TASK-001: セッションタイトル"
  }'
```

**レスポンス**: Session オブジェクト（下記リソース定義参照）

#### List Sessions - セッション一覧

```text
GET /v1alpha/sessions
```

**クエリパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `pageSize` | integer | 返却するセッション数（1-100、デフォルト: 30） |
| `pageToken` | string | ページネーショントークン |

```bash
curl -s 'https://jules.googleapis.com/v1alpha/sessions?pageSize=10' \
  -H "x-goog-api-key: $JULES_API_KEY"
```

#### Get Session - セッション詳細

```text
GET /v1alpha/sessions/{sessionId}
```

```bash
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}" \
  -H "x-goog-api-key: $JULES_API_KEY"
```

**レスポンス**: Session オブジェクト

#### Approve Plan - プラン承認

セッション内の保留中のプランを承認します。`requirePlanApproval: true` で作成したセッションで使用します。

```text
POST /v1alpha/sessions/{sessionId}:approvePlan
```

```bash
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}:approvePlan" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY"
```

**リクエストボディ**: 空

#### Send Message - メッセージ送信

アクティブなセッションにメッセージを送信します。フィードバック、追加指示、質問への回答に使用します。

```text
POST /v1alpha/sessions/{sessionId}:sendMessage
```

**リクエストボディ**:

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `prompt` | string | 必須 | 送信するメッセージ |

```bash
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}:sendMessage" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{
    "prompt": "追加の指示内容"
  }'
```

**レスポンス**: 空（エージェントの応答は次のアクティビティとして取得）

### Activities API

#### List Activities - アクティビティ一覧

セッション内のアクティビティ（イベント）を一覧取得します。進捗監視、メッセージ取得、成果物アクセスに使用します。

```text
GET /v1alpha/sessions/{sessionId}/activities
```

**クエリパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `pageSize` | integer | 返却するアクティビティ数（1-100、デフォルト: 50） |
| `pageToken` | string | ページネーショントークン |

```bash
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}/activities?pageSize=20" \
  -H "x-goog-api-key: $JULES_API_KEY"
```

## リソース定義

### Session

セッションは特定のコンテキスト内での一連の作業を表します。

| フィールド | 型 | 入出力 | 説明 |
|-----------|-----|--------|------|
| `name` | string | output | リソース名（`sessions/{session}`形式） |
| `id` | string | output | セッションID |
| `prompt` | string | input | タスクの依頼文 |
| `title` | string | input/output | セッションタイトル |
| `state` | string | output | セッションの現在の状態 |
| `webUrl` | string | output | Julesウェブアプリでの閲覧URL |
| `sourceContext` | SourceContext | input | リポジトリとブランチの指定 |
| `requirePlanApproval` | boolean | input | プラン承認の要否 |
| `automationMode` | string | input | 自動化モード |
| `output` | SessionOutput | output | セッションの出力（PR情報等） |
| `createTime` | string | output | 作成日時 |
| `updateTime` | string | output | 最終更新日時 |

### Activity

アクティビティはセッション内の個々のイベントを表します。イベントソースパターンに従い、一度発生したアクティビティは変更されません。各アクティビティは以下のイベントフィールドのうち1つだけが設定されます。

| イベントフィールド | 説明 |
|-------------------|------|
| `planGenerated` | プランが生成された。ステップのリストを含む |
| `planApproved` | プランが承認された |
| `userMessage` | ユーザーがメッセージを送信した |
| `agentMessage` | Julesがメッセージを送信した |
| `progressUpdate` | 進捗が更新された |
| `completed` | セッションが完了した |
| `failed` | セッションが失敗した |

### SourceContext

セッションのソース（リポジトリ）コンテキストです。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `source` | string | ソース名（`sources/github/{owner}/{repo}`形式） |
| `githubRepoContext` | object | GitHubリポジトリ固有のコンテキスト |
| `githubRepoContext.startingBranch` | string | ベースブランチ（PR作成先のブランチ） |

### SessionOutput

セッションの出力結果です。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `pullRequests` | PullRequest[] | 作成されたPRの一覧 |

**PullRequest**:

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `url` | string | PRのURL |
| `title` | string | PRタイトル |
| `description` | string | PRの説明 |

## エラーハンドリング

### HTTPステータスコード

| コード | 説明 | 対処 |
|--------|------|------|
| 400 | リクエスト不正 | リクエストボディを確認 |
| 401 | 認証エラー | APIキーを確認 |
| 403 | アクセス権限なし | APIキーの権限、GitHubアプリのインストールを確認 |
| 404 | リソース未発見 | セッションID、ソース名を確認 |
| 429 | レート制限超過 | リトライ間隔を空ける |
| 500 | サーバーエラー | リトライする |

### エラーレスポンスの形式

```json
{
  "error": {
    "code": 400,
    "message": "Error description",
    "status": "INVALID_ARGUMENT"
  }
}
```

## レート制限とリトライ

APIリクエストが失敗した場合、以下のリトライ戦略を使用します:

```text
リトライ戦略: 指数バックオフ（最大4回）
- 1回目リトライ: 2秒後
- 2回目リトライ: 4秒後
- 3回目リトライ: 8秒後
- 4回目リトライ: 16秒後
```

リトライ対象:
- ネットワークエラー
- HTTP 429（レート制限）
- HTTP 500/502/503（サーバーエラー）

リトライ非対象:
- HTTP 400（リクエスト不正）
- HTTP 401/403（認証・権限エラー）
- HTTP 404（リソース未発見）
