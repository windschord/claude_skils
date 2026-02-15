# ファイル最適化レポート

## 基本情報

| 項目 | 内容 |
|-----|------|
| 実行日時 | [YYYY-MM-DD HH:MM] |
| 対象範囲 | docs/ |
| 実行者 | [実行者名/AI] |

## サマリー

| カテゴリ | 正常 | 注意 | 要対応 |
|---------|-----|------|--------|
| サイズ超過（500行以上） | X件 | X件 | X件 |
| セクション過多（10以上） | X件 | X件 | X件 |
| 重複コンテンツ（30%以上） | - | X件 | X件 |
| インデックス不整合 | - | - | X件 |

---

## 分割推奨ファイル

### 要対応（1000行以上）

#### OPT-001: docs/sdd/design/components/auth.md

| 項目 | 値 |
|-----|-----|
| 現在の行数 | 1,247行 |
| セクション数 | 28 |
| 状態 | 要対応 |

**現在の構造**

```text
# 認証コンポーネント
├── 概要
├── アーキテクチャ
├── ログイン機能
│   ├── フロー
│   ├── API
│   ├── バリデーション
│   └── エラーハンドリング
├── ログアウト機能
│   ├── フロー
│   └── API
├── 登録機能
│   ├── フロー
│   ├── API
│   ├── バリデーション
│   └── メール認証
├── パスワードリセット
│   ├── フロー
│   ├── API
│   └── トークン管理
├── セッション管理
│   ├── 概要
│   ├── トークン
│   └── リフレッシュ
└── セキュリティ考慮事項
```

**分割提案**

```text
docs/sdd/design/components/auth/
├── index.md          # 概要・アーキテクチャ（150行）
├── login.md          # ログイン機能（300行）
├── logout.md         # ログアウト機能（100行）
├── register.md       # 登録機能（350行）
├── password-reset.md # パスワードリセット（200行）
├── session.md        # セッション管理（200行）
└── security.md       # セキュリティ考慮事項（100行）
```

**分割後の構成詳細**

| ファイル | 含まれる内容 | 推定行数 |
|---------|-------------|---------|
| index.md | 概要、アーキテクチャ図、各機能へのリンク | 150行 |
| login.md | ログインフロー、API、バリデーション、エラー | 300行 |
| logout.md | ログアウトフロー、API | 100行 |
| register.md | 登録フロー、API、バリデーション、メール認証 | 350行 |
| password-reset.md | リセットフロー、API、トークン管理 | 200行 |
| session.md | セッション概要、トークン、リフレッシュ | 200行 |
| security.md | セキュリティ考慮事項、ベストプラクティス | 100行 |

**影響を受ける参照**

| 参照元 | 現在の参照 | 更新後の参照 |
|--------|-----------|-------------|
| docs/sdd/tasks/phase-1/TASK-005.md | components/auth.md | components/auth/login.md |
| docs/sdd/requirements/stories/US-001.md | components/auth.md | components/auth/index.md |

---

### 注意（500-1000行）

#### OPT-002: docs/sdd/tasks/index.md

| 項目 | 値 |
|-----|-----|
| 現在の行数 | 680行 |
| セクション数 | 15 |
| 状態 | 注意 |

**分析**

完了済みタスクが蓄積して肥大化しています。

**推奨アクション**
- [ ] 完了済みタスクをアーカイブ（アーカイブ機能を使用）
- [ ] アーカイブ後、行数は約200行に削減される見込み

---

## 重複コンテンツ

### 要対応（類似度50%以上）

#### DUP-001: ユーザー属性定義の重複

| 項目 | 内容 |
|-----|------|
| ファイルA | docs/sdd/requirements/stories/US-001.md |
| ファイルB | docs/sdd/design/components/user.md |
| 類似度 | 68% |
| 重複行数 | 45行 |

**重複箇所**

ファイルA（US-001.md）:
```markdown
### ユーザー属性

| 属性 | 型 | 必須 | 説明 |
|-----|-----|------|------|
| id | UUID | Yes | 一意識別子 |
| email | String | Yes | メールアドレス |
| name | String | Yes | 表示名 |
| avatar_url | String | No | プロフィール画像URL |
| created_at | DateTime | Yes | 作成日時 |
| updated_at | DateTime | Yes | 更新日時 |
```

ファイルB（user.md）:
```markdown
### ユーザーエンティティ

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| id | UUID | Yes | 一意識別子 |
| email | String | Yes | メールアドレス |
| name | String | Yes | 表示名 |
| avatarUrl | String | No | プロフィール画像URL |
| createdAt | DateTime | Yes | 作成日時 |
| updatedAt | DateTime | Yes | 更新日時 |
```

**推奨アクション**

1. 共通定義ファイルを作成:
   ```text
   docs/sdd/design/common/user-entity.md
   ```

2. 各ファイルを参照に変更:
   - US-001.md: 「ユーザー属性は[共通定義](../../design/common/user-entity.md)を参照」
   - user.md: 「ユーザーエンティティは[共通定義](../common/user-entity.md)を参照」

---

### 注意（類似度30-50%）

#### DUP-002: バリデーションルールの類似

| 項目 | 内容 |
|-----|------|
| ファイルA | docs/sdd/design/api/users.md |
| ファイルB | docs/sdd/design/components/validation.md |
| 類似度 | 42% |

**分析**

部分的な重複があります。統合を検討してください。

**推奨アクション**
- [ ] validation.mdに統合し、users.mdから参照

---

## インデックス不整合

### 目次に含まれていないファイル

以下のファイルがindex.mdの目次に含まれていません。

| ファイル | 所属インデックス |
|---------|-----------------|
| docs/sdd/tasks/phase-2/TASK-015.md | docs/sdd/tasks/index.md |
| docs/sdd/tasks/phase-2/TASK-016.md | docs/sdd/tasks/index.md |
| docs/sdd/design/components/notification.md | docs/sdd/design/index.md |

**推奨アクション**
- [ ] docs/sdd/tasks/index.mdにTASK-015, TASK-016を追加
- [ ] docs/sdd/design/index.mdにnotification.mdを追加

---

### 削除済みファイルへの参照

以下のファイルは削除されていますが、目次に残っています。

| 参照 | 所属インデックス |
|-----|-----------------|
| docs/sdd/design/components/legacy-auth.md | docs/sdd/design/index.md |

**推奨アクション**
- [ ] docs/sdd/design/index.mdからlegacy-auth.mdへの参照を削除

---

## 最適化計画

### 即座に対応

1. [ ] インデックス不整合の修正（目次の更新）

### 計画的に対応

1. [ ] OPT-001: auth.mdの分割
2. [ ] DUP-001: ユーザー属性定義の統合

### 他の機能と連携

1. [ ] OPT-002: tasks/index.mdの肥大化 → アーカイブ機能で対応

---

## 実行オプション

| オプション | 内容 |
|-----------|------|
| A | すべての最適化を実行 |
| B | ファイル分割のみ実行 |
| C | 重複統合のみ実行 |
| D | インデックス再生成のみ実行 |
| E | 個別に選択 |
| F | 今回は実行せずレポートのみ保存 |

---

## 承認

| 項目 | 内容 |
|-----|------|
| 承認日時 | [YYYY-MM-DD HH:MM] |
| 承認者 | [承認者名] |
| 選択したオプション | [A / B / C / D / E / F] |
| 個別指示 | [特定の項目に対する指示があれば記載] |

---

## 実行結果

（実行後に記入）

### 分割実行結果

| 対象 | 結果 | 作成ファイル数 |
|-----|------|---------------|
| auth.md | 完了 | 7ファイル |

### 統合実行結果

| 対象 | 結果 | 更新ファイル数 |
|-----|------|---------------|
| ユーザー属性定義 | 完了 | 3ファイル |

### インデックス更新結果

| 対象 | 追加 | 削除 |
|-----|------|------|
| docs/sdd/tasks/index.md | 2件 | 0件 |
| docs/sdd/design/index.md | 1件 | 1件 |

### 実行ログ

```text
[実行ログをここに記載]
```
