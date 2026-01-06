# Gitコミットテンプレート

task-executingスキルで使用するコミットテンプレートの詳細ガイドです。

## 実装コミット

```text
[タスクID] タスクタイトル

## 実装内容
- 実装した機能の説明
- 主な変更点

## 受入基準の達成状況
- [x] 基準1
- [x] 基準2

## 関連ドキュメント
- docs/tasks/[phase]/TASK-XXX.md: タスク詳細
- docs/design/components/[name].md: 関連コンポーネント
- docs/requirements/stories/US-XXX.md: 関連要件

## テスト
- テスト実行結果（npm test等）
```

### 実装コミットの例

```text
[Task 1.1] ユーザー認証APIエンドポイントの実装

## 実装内容
- POST /api/auth/login エンドポイントを実装
- POST /api/auth/logout エンドポイントを実装
- JWTトークン生成・検証ロジックを追加
- bcryptによるパスワードハッシュ化を実装

## 受入基準の達成状況
- [x] login/logoutエンドポイントが実装されている
- [x] JWTトークンが正しく生成・検証される
- [x] パスワードがbcryptでハッシュ化されている
- [x] エラーハンドリングが適切に実装されている
- [x] ユニットテストが実装され、すべて通過する

## 関連ドキュメント
- docs/tasks/phase-1/TASK-001.md: タスク詳細
- docs/design/components/authentication.md: AuthenticationComponent
- docs/requirements/stories/US-001.md: REQ-001, REQ-002

## テスト
npm test: 15 passed, 0 failed
```

## ステータス更新コミット

```text
Update tasks.md: タスクID completed

タスクタイトルを完了としてマーク。
完了サマリー: [1行の要約]
```

### ステータス更新コミットの例

```text
Update tasks.md: Task 1.1 completed

ユーザー認証APIエンドポイントの実装を完了としてマーク。
完了サマリー: POST /api/auth/login, /logoutを実装。JWT認証とbcryptハッシュ化を適用。
```

## セーフポイントコミット

重要な変更を行う前に安定した状態を保存するためのコミット。

```text
[タスクID] Safe point before: 変更の説明

大規模な変更を開始する前の安定した状態を保存。

次の変更予定:
- 変更内容1
- 変更内容2
```

## ベストプラクティス

1. **コミットメッセージは明確に**: 何を実装したか一目でわかるように
2. **関連ドキュメントを必ず記載**: トレーサビリティを確保
3. **テスト結果を含める**: 品質の証明
4. **受入基準をチェックリスト形式で**: 達成状況を明示
5. **絵文字を使用しない**: コミットメッセージ全体で禁止
