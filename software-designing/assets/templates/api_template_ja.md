# API: [エンドポイント名]

## 概要

**ベースパス**: `/api/[resource]`
**目的**: *このAPIの役割*

## 情報の明確性

### 明示された情報
- [ユーザーから明示的に指定されたAPI仕様]

### 不明/要確認の情報
- [ ] 認証方式: [JWT/セッション/APIキー等]
- [ ] レート制限: [あり/なし、具体的な数値]
- [ ] エラーレスポンス形式: [具体的なフォーマット]

---

## エンドポイント一覧

| メソッド | パス | 説明 |
|---------|------|------|
| GET | /api/resource | リソース一覧取得 |
| GET | /api/resource/:id | リソース詳細取得 |
| POST | /api/resource | リソース作成 |
| PUT | /api/resource/:id | リソース更新 |
| DELETE | /api/resource/:id | リソース削除 |

---

## GET /api/resource

**説明**: リソース一覧を取得

### リクエスト

**ヘッダー**:
| ヘッダー | 必須 | 説明 |
|---------|------|------|
| Authorization | Yes | Bearer {token} |

**クエリパラメータ**:
| パラメータ | 型 | 必須 | 説明 | デフォルト |
|-----------|-----|------|------|-----------|
| page | number | No | ページ番号 | 1 |
| limit | number | No | 取得件数 | 20 |
| sort | string | No | ソート順 | created_at:desc |

### レスポンス

**成功時 (200 OK)**:
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "name": "string",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

**エラー時 (401 Unauthorized)**:
```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "認証が必要です"
  }
}
```

---

## POST /api/resource

**説明**: リソースを新規作成

### リクエスト

**ヘッダー**:
| ヘッダー | 必須 | 説明 |
|---------|------|------|
| Authorization | Yes | Bearer {token} |
| Content-Type | Yes | application/json |

**ボディ**:
```json
{
  "name": "string (required, 1-100文字)",
  "description": "string (optional, max 500文字)"
}
```

### バリデーションルール

| フィールド | ルール |
|-----------|--------|
| name | 必須、1-100文字、英数字とハイフンのみ |
| description | 任意、最大500文字 |

### レスポンス

**成功時 (201 Created)**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**バリデーションエラー (400 Bad Request)**:
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力値が不正です",
    "details": [
      {
        "field": "name",
        "message": "名前は必須です"
      }
    ]
  }
}
```

---

## エラーコード一覧

| コード | HTTPステータス | 説明 |
|--------|---------------|------|
| UNAUTHORIZED | 401 | 認証が必要 |
| FORBIDDEN | 403 | アクセス権限なし |
| NOT_FOUND | 404 | リソースが見つからない |
| VALIDATION_ERROR | 400 | 入力値エラー |
| INTERNAL_ERROR | 500 | サーバー内部エラー |

## セキュリティ

- 認証: [JWT/セッション/APIキー]
- 認可: [RBAC/ABAC等]
- レート制限: [X req/min]
- CORS: [設定内容]

## 関連コンポーネント

- [ComponentA](../components/component-a.md): リクエスト処理
- [ComponentB](../components/component-b.md): データ永続化

## 関連要件

- [REQ-XXX](../../requirements/stories/US-XXX.md): [関連の説明]
