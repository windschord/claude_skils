# 実装同期チェックレポート

## 基本情報

| 項目 | 内容 |
|-----|------|
| 実行日時 | [YYYY-MM-DD HH:MM] |
| 対象ドキュメント | docs/sdd/design/api/, docs/sdd/design/database/, docs/sdd/design/components/ |
| 対象実装 | [実装ディレクトリ] |
| 実行者 | [実行者名/AI] |

## サマリー

| カテゴリ | 同期 | 乖離 | 優先度 |
|---------|-----|------|--------|
| API | X件 | X件 | - |
| データベース | X件 | X件 | - |
| コンポーネント | X件 | X件 | - |
| **合計** | **X件** | **X件** | - |

### 乖離の内訳

| 乖離タイプ | 件数 | 説明 |
|-----------|------|------|
| ドキュメント古い | X件 | 実装が先に変更された |
| 実装漏れ | X件 | ドキュメントにあるが実装がない |
| 未文書化 | X件 | 実装にあるがドキュメントがない |

---

## API乖離詳細

### ドキュメントが古い

実装が先に変更され、ドキュメントが追従していない箇所です。

#### API-001: POST /api/users

| 項目 | 内容 |
|-----|------|
| ドキュメント | docs/sdd/design/api/users.md |
| 実装ファイル | src/routes/users.ts |
| 優先度 | High |

**差異の詳細**

| 項目 | ドキュメント | 実装 |
|-----|-------------|------|
| レスポンスフィールド | `id`, `name`, `email` | `id`, `name`, `email`, `createdAt` |

```diff
ドキュメント定義:
{
  "id": "string",
  "name": "string",
  "email": "string"
}

実装:
{
  "id": "string",
  "name": "string",
  "email": "string",
+ "createdAt": "string"
}
```

**推奨アクション**
- [ ] docs/sdd/design/api/users.mdを更新して`createdAt`フィールドを追加

---

### 実装漏れ

ドキュメントに定義があるが、実装されていない箇所です。

#### API-002: PATCH /api/users/:id

| 項目 | 内容 |
|-----|------|
| ドキュメント | docs/sdd/design/api/users.md |
| 実装ファイル | 該当なし |
| 優先度 | High |

**推奨アクション**
- [ ] src/routes/users.tsにPATCHエンドポイントを実装
- [ ] または、ドキュメントから削除（不要な場合）

---

### 未文書化の実装

実装にあるが、ドキュメントに記載がない箇所です。

#### API-003: DELETE /api/users/:id

| 項目 | 内容 |
|-----|------|
| ドキュメント | 該当なし |
| 実装ファイル | src/routes/users.ts:45 |
| 優先度 | Medium |

**実装の内容**
```typescript
router.delete('/api/users/:id', async (req, res) => {
  // ユーザー削除処理
});
```

**推奨アクション**
- [ ] docs/sdd/design/api/users.mdにDELETEエンドポイントを追加
- [ ] または、実装を削除（不要な場合）

---

## データベース乖離詳細

### ドキュメントが古い

#### DB-001: usersテーブル

| 項目 | 内容 |
|-----|------|
| ドキュメント | docs/sdd/design/database/schema.md |
| 実装ファイル | prisma/schema.prisma |
| 優先度 | Medium |

**差異の詳細**

| カラム | ドキュメント | 実装 |
|--------|-------------|------|
| avatar_url | 未記載 | String? |
| updated_at | 未記載 | DateTime @updatedAt |

**推奨アクション**
- [ ] docs/sdd/design/database/schema.mdを更新

---

### 未文書化のテーブル

#### DB-002: sessionsテーブル

| 項目 | 内容 |
|-----|------|
| ドキュメント | 該当なし |
| 実装ファイル | prisma/schema.prisma |
| 優先度 | Medium |

**推奨アクション**
- [ ] docs/sdd/design/database/schema.mdにsessionsテーブルを追加

---

## コンポーネント乖離詳細

### インターフェース不一致

#### COMP-001: AuthService

| 項目 | 内容 |
|-----|------|
| ドキュメント | docs/sdd/design/components/auth.md |
| 実装ファイル | src/services/AuthService.ts |
| 優先度 | Medium |

**差異の詳細**

| メソッド | ドキュメント | 実装 |
|---------|-------------|------|
| login() | `login(email, password)` | `login(credentials: LoginDto)` |
| refreshToken() | 未記載 | 実装あり |

**推奨アクション**
- [ ] ドキュメントのメソッドシグネチャを更新
- [ ] refreshToken()メソッドを追加

---

## 修正計画

### 推奨対応順序

1. **Critical** - APIエンドポイントの不一致（本番影響あり）
2. **High** - 実装漏れ・ドキュメント古い（機能に影響）
3. **Medium** - データベース・コンポーネントの乖離
4. **Low** - 軽微な差異

### 対応オプション

| オプション | 内容 | 対象件数 |
|-----------|------|---------|
| A | ドキュメントを実装に合わせて更新 | X件 |
| B | 実装をドキュメントに合わせて修正 | X件（タスク作成） |
| C | 個別に対応を選択 | - |
| D | 今回は保留 | - |

---

## 承認

| 項目 | 内容 |
|-----|------|
| 承認日時 | [YYYY-MM-DD HH:MM] |
| 承認者 | [承認者名] |
| 選択した対応 | [A / B / C / D] |
| 個別指示 | [特定の項目に対する指示があれば記載] |
