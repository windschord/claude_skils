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

**推奨: 1Passwordシークレット参照**（`scripts/jules.sh`が実行時に`op read`で解決する。環境変数にシークレット本体を置かない）:

```bash
export JULES_API_KEY_OP_URI="op://<vault>/<item>/<field>"
```

直接指定（後方互換。生のcurlを使う場合はこちらが必要）:

```bash
export JULES_API_KEY="your-api-key-here"
```

`JULES_API_KEY_OP_URI`のみ設定されている環境で生のcurlを実行する場合は、`JULES_API_KEY=$(op read "$JULES_API_KEY_OP_URI")`で取得してから使用する。

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

**クエリパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `pageSize` | integer | 返却するソース数（1ページあたり） |
| `pageToken` | string | ページネーショントークン |

```bash
curl -s 'https://jules.googleapis.com/v1alpha/sources?pageSize=100' \
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
  ],
  "nextPageToken": "..."
}
```

> **重要**: 接続済みリポジトリが多い場合、1回のリクエストでは全件が返らないことがある。`nextPageToken` が存在する限り `pageToken` を指定して全ページを取得しないと、対象リポジトリが後方のページにあった場合に見つけられない。`scripts/jules.sh list-sources` は全ページを自動的に取得して結合する。

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

**推奨: スクリプト経由（特殊文字・日本語対応済み）**

```bash
cat <<'EOF' | scripts/jules.sh create-session "sources/github/owner/repo" "develop" "TASK-001: セッションタイトル"
タスク: `config.yaml` の設定修正（TASK-001）

O'Brien形式のキーが読み込まれない問題を修正する。
EOF
```

スクリプトは `jq --arg` でJSONを生成するため、バッククォート・シングルクォート・日本語を含む任意のプロンプトを安全に送れる。

**直接curlを使う場合（注意: 特殊文字で壊れる）**

```bash
# ⚠ プロンプトに特殊文字が含まれる場合はこの形式を使わないこと
curl -s 'https://jules.googleapis.com/v1alpha/sessions' \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{"prompt": "シンプルなASCIIプロンプトのみ安全", ...}'
```

**直接curlで特殊文字を含む場合: Pythonでファイル生成してから送る**

```bash
python3 - <<'PYEOF' > /tmp/jules_payload.json
import json
payload = {
    "prompt": """タスク: `config.yaml` の設定修正

O'Brien形式のキーが読み込まれない問題を修正する。""",
    "sourceContext": {
        "source": "sources/github/owner/repo",
        "githubRepoContext": {"startingBranch": "develop"}
    },
    "automationMode": "AUTO_CREATE_PR",
    "requirePlanApproval": True,
    "title": "TASK-001: セッションタイトル"
}
print(json.dumps(payload, ensure_ascii=False))
PYEOF

curl -s 'https://jules.googleapis.com/v1alpha/sessions' \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  --data-binary @/tmp/jules_payload.json
```

**レスポンス**: Session オブジェクト（下記リソース定義参照）

> **注意**: レスポンスおよび作成直後の `GET /sessions/{id}` では `webUrl` が `null` になる場合がある。`state` が `WORKING` に遷移した後で再取得すると `webUrl` が得られる。それまでは `https://jules.google` のセッション一覧からタイトルで探すよう案内する。

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
# 推奨: スクリプト経由（特殊文字・日本語対応済み）
cat <<'EOF' | scripts/jules.sh send-message "${SESSION_ID}"
追加の指示内容（特殊文字・日本語含む可能）
EOF

# または直接curl（シンプルなASCIIのみの場合）
curl -s "https://jules.googleapis.com/v1alpha/sessions/${SESSION_ID}:sendMessage" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{"prompt": "simple ASCII only message"}'
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
| `state` | string | output | セッションの現在の状態（下記 Session state 参照） |
| `webUrl` | string \| null | output | Julesウェブアプリでの閲覧URL（セッション作成直後は `null`、`state` が `WORKING` 以降で取得可能） |
| `sourceContext` | SourceContext | input | リポジトリとブランチの指定 |
| `requirePlanApproval` | boolean | input | プラン承認の要否 |
| `automationMode` | string | input | 自動化モード |
| `output` | SessionOutput | output | セッションの出力（PR情報等） |
| `createTime` | string | output | 作成日時 |
| `updateTime` | string | output | 最終更新日時 |

#### Session state

`Session.state` の取り得る値。Jules API はアルファ版のため、正式な値は[公式リファレンス](https://developers.google.com/jules/api/reference/rest)を確認してください。

| 値 | 意味 |
|----|------|
| `WORKING` | プラン生成中・承認待ち・実行中 |
| `DONE` | 正常完了（PR作成済み） |
| `FAILED` | エラーで停止 |

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
