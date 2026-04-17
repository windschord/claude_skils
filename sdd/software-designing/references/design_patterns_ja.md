# 設計パターンリファレンス

## アーキテクチャパターン

### レイヤードアーキテクチャ

```
┌─────────────────────────────┐
│     プレゼンテーション層      │  UI、API エンドポイント
├─────────────────────────────┤
│       ビジネスロジック層       │  ドメインロジック、サービス
├─────────────────────────────┤
│       データアクセス層        │  リポジトリ、ORM
├─────────────────────────────┤
│         データベース          │  永続化
└─────────────────────────────┘
```

**使用場面**: 標準的なWebアプリケーション
**メリット**: 責務の分離、テスト容易性
**デメリット**: 層間の依存関係、パフォーマンスオーバーヘッド

### クリーンアーキテクチャ

```
        ┌─────────────────┐
        │   Frameworks    │  外部ライブラリ、DB
        │  & Drivers      │
      ┌─┴─────────────────┴─┐
      │  Interface Adapters │  コントローラ、ゲートウェイ
    ┌─┴─────────────────────┴─┐
    │    Application Layer    │  ユースケース
  ┌─┴─────────────────────────┴─┐
  │       Domain Layer          │  エンティティ、ビジネスルール
  └─────────────────────────────┘
```

**使用場面**: 複雑なドメインロジックを持つアプリケーション
**メリット**: ドメイン中心、フレームワーク非依存
**デメリット**: 実装コストが高い

### マイクロサービス

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Service │  │ Service │  │ Service │
│    A    │  │    B    │  │    C    │
└────┬────┘  └────┬────┘  └────┬────┘
     │           │           │
     └───────────┼───────────┘
                 │
         ┌───────┴───────┐
         │  API Gateway  │
         └───────────────┘
```

**使用場面**: 大規模システム、独立したデプロイが必要
**メリット**: スケーラビリティ、技術選択の自由
**デメリット**: 運用複雑性、分散システムの課題

## コンポーネント設計パターン

### リポジトリパターン

```typescript
interface UserRepository {
  findById(id: string): Promise<User | null>;
  findAll(): Promise<User[]>;
  save(user: User): Promise<void>;
  delete(id: string): Promise<void>;
}

class PostgresUserRepository implements UserRepository {
  // 実装
}
```

**目的**: データアクセスロジックの抽象化

### サービスパターン

```typescript
class UserService {
  constructor(
    private userRepository: UserRepository,
    private emailService: EmailService
  ) {}

  async registerUser(data: RegisterUserDto): Promise<User> {
    const user = new User(data);
    await this.userRepository.save(user);
    await this.emailService.sendWelcomeEmail(user);
    return user;
  }
}
```

**目的**: ビジネスロジックのカプセル化

### ファクトリパターン

```typescript
class NotificationFactory {
  create(type: 'email' | 'sms' | 'push'): Notification {
    switch (type) {
      case 'email': return new EmailNotification();
      case 'sms': return new SmsNotification();
      case 'push': return new PushNotification();
    }
  }
}
```

**目的**: オブジェクト生成ロジックの分離

## API設計パターン

### RESTful API

| 操作 | HTTPメソッド | エンドポイント | 説明 |
|------|-------------|---------------|------|
| 一覧取得 | GET | /users | 全ユーザー取得 |
| 詳細取得 | GET | /users/:id | 特定ユーザー取得 |
| 作成 | POST | /users | ユーザー作成 |
| 更新 | PUT | /users/:id | ユーザー更新 |
| 削除 | DELETE | /users/:id | ユーザー削除 |

### エラーレスポンス形式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力値が不正です",
    "details": [
      {
        "field": "email",
        "message": "有効なメールアドレスを入力してください"
      }
    ]
  }
}
```

### ページネーション

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "perPage": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

## データベース設計パターン

### 正規化レベル

| レベル | 説明 | 使用場面 |
|--------|------|----------|
| 1NF | 繰り返しグループの排除 | 基本 |
| 2NF | 部分関数従属の排除 | 一般的なOLTP |
| 3NF | 推移的関数従属の排除 | 厳密なデータ整合性 |
| BCNF | 決定項がすべて候補キー | 高度な正規化 |

### インデックス戦略

```sql
-- 主キーインデックス（自動）
PRIMARY KEY (id)

-- 検索用インデックス
CREATE INDEX idx_users_email ON users(email);

-- 複合インデックス
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- 部分インデックス
CREATE INDEX idx_active_users ON users(status) WHERE status = 'active';
```

### ソフトデリート

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  deleted_at TIMESTAMP NULL,  -- NULLなら有効、値があれば削除済み
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 有効なレコードのみ取得
SELECT * FROM users WHERE deleted_at IS NULL;
```

## セキュリティパターン

### 認証方式

| 方式 | 特徴 | 使用場面 |
|------|------|----------|
| JWT | ステートレス、スケーラブル | SPA、モバイルアプリ |
| セッション | サーバー側で状態管理 | 従来のWebアプリ |
| OAuth 2.0 | 外部認証プロバイダ連携 | ソーシャルログイン |
| APIキー | シンプル、サービス間通信 | 内部API、B2B |

### 入力バリデーション

```typescript
// ホワイトリストバリデーション
const allowedFields = ['name', 'email', 'age'];
const sanitized = Object.keys(input)
  .filter(key => allowedFields.includes(key))
  .reduce((obj, key) => ({ ...obj, [key]: input[key] }), {});

// 型バリデーション
const schema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
});
```

## 状態管理パターン

### イベントソーシング

```
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Event 1 │ -> │ Event 2 │ -> │ Event 3 │
│ Created │    │ Updated │    │ Deleted │
└─────────┘    └─────────┘    └─────────┘
     │              │              │
     └──────────────┼──────────────┘
                    │
              ┌─────┴─────┐
              │  現在の状態  │
              └───────────┘
```

**使用場面**: 監査ログが必要、状態の履歴追跡

### CQRS（コマンドクエリ責務分離）

```
        ┌─────────────┐
        │   Command   │ ── 書き込み ──> ┌─────────┐
        │   Handler   │                 │ Write DB│
        └─────────────┘                 └─────────┘
                                              │
        ┌─────────────┐                       │ 同期
        │    Query    │ <── 読み取り ── ┌─────────┐
        │   Handler   │                 │ Read DB │
        └─────────────┘                 └─────────┘
```

**使用場面**: 読み取りと書き込みの負荷が異なる場合
