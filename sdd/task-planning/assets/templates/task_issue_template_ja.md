# タスクIssueテンプレート（デフォルト）

> このテンプレートは、SDDのタスクを **GitHub Issue** として起票する際の本文フォーマットです。
> 1タスク = 1 Issue とし、詳細（受入基準・TDD手順・技術仕様）はすべてこのIssue本文に集約します。
> `docs/sdd/tasks/` のファイルは作成しません（ファイル生成はオプション。`tasks_index_template_ja.md` / `task_detail_template_ja.md` を参照）。

---

## Issueメタデータ（起票時に設定）

| 項目 | 値 | 設定方法 |
|------|-----|---------|
| **タイトル** | `[TASK-XXX] タスクタイトル` | Issue title |
| **フェーズ** | Phase-N | ラベル `sdd:phase-N` |
| **ステータス** | TODO | ラベル `sdd:status/todo`（DONE時はIssueをclose） |
| **タスク種別** | 通常 / BugFix / DocFix | ラベル `sdd:task`（＋`sdd:bugfix`等） |
| **並列グループ** | A / B / ... | ラベル `sdd:group-A`（任意） |
| **依存Issue** | #12, #13 | 本文「依存関係」に記載 |

**必須ラベル**: `sdd:task`（SDD管理タスクの識別）、`sdd:phase-N`、`sdd:status/todo`

> ラベルが未作成の場合は、初回起票前に作成する（下記「ラベル体系」を参照）。

---

## Issue本文フォーマット

以下をそのままIssue本文（body）に貼り付けて記入する。

```markdown
> **サブエージェント実行指示**
> このIssueは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

## あなたのタスク

**[タスクタイトル]** を実装してください。

### 実装の目標

[このタスクで達成すべきことを1-3文で明確に記述]

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 作成 | `src/path/to/new-file.ts` | [ファイルの目的] |
| 変更 | `src/path/to/existing.ts` | [変更内容の概要] |
| 作成 | `src/path/to/__tests__/file.test.ts` | ユニットテスト |

---

## 技術的コンテキスト

### 使用技術
- 言語: [TypeScript/Python等]
- フレームワーク: [React/Next.js/Express等]
- テストフレームワーク: [Jest/Vitest/pytest等]

### 参照すべきファイル
- `@src/path/to/reference.ts` - [参照理由]
- `@src/path/to/similar-feature.ts` - [参照理由]

### 関連する設計書
- `@docs/sdd/design/components/component-a.md` - [関連コンポーネントの設計]
- `@docs/sdd/design/api/endpoint.md` - [関連APIの仕様]

### 関連する要件
- `@docs/sdd/requirements/stories/US-XXX.md` - [対応するユーザーストーリー]

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `src/path/to/new-file.ts` が作成されている
- [ ] [具体的な機能が動作すること]
- [ ] ユニットテストが作成され、すべてパスする
- [ ] ミューテーションスコアが85%以上である（検証: `npx stryker run` 等）
- [ ] `npm run lint` でエラーが0件である
- [ ] `npm run typecheck` でエラーが0件である

---

## 実装手順（TDD）

### ステップ1: テストを先に作成
1. `src/path/to/__tests__/file.test.ts` を作成
2. 受入基準に対応するテストケースを実装
3. テストを実行して失敗することを確認: `npm test`
4. コミット: `test: Add tests for [feature]`

### ステップ2: 機能を実装
1. `src/path/to/new-file.ts` を作成/変更
2. 受入基準を満たすように実装
3. テストがすべてパスすることを確認: `npm test`
4. Lintとタイプチェックがパスすることを確認

### ステップ3: コミットして完了
1. 変更をコミット: `feat: Implement [feature] (#<Issue番号>)`
2. 受入基準をすべて確認

---

## 実装の詳細仕様

### 入出力仕様
**入力:**
- `param1`: [型] - [説明]

**出力:**
- [型] - [説明]

### エラー処理
- [エラーケース1]: [期待する処理]

---

## 情報の明確性チェック

### 明示された情報
- [x] [明確に指定された仕様1]

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| [項目名] | [推測内容や不明点] | [ ] 未確認 / [x] 確認済み |

> **重要**: 未確認の項目がある場合、このタスクを実行する前に必ず確認を取ってください。

---

## 依存関係

- 前提Issue: #12（データモデルの定義）が完了していること / なし
- 並列実行: グループA（#13, #14 と並行実行可能）

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-XXX |
| **フェーズ** | Phase-N |
| **推定工数** | X分 |
| **対応要件** | REQ-XXX |
| **対応設計** | DEC-XXX |
```

---

## ラベル体系

| ラベル | 用途 | 例 |
|--------|------|-----|
| `sdd:task` | SDD管理タスクIssueの識別（目次フィルタ用・必須） | - |
| `sdd:phase-N` | フェーズ分類（フェーズディレクトリの代替） | `sdd:phase-1` |
| `sdd:status/todo` | ステータス: 未着手 | - |
| `sdd:status/in-progress` | ステータス: 作業中 | - |
| `sdd:status/review` | ステータス: レビュー待ち | - |
| `sdd:status/blocked` | ステータス: ブロック中 | - |
| `sdd:group-X` | 並列実行グループ（任意） | `sdd:group-A` |
| `sdd:bugfix` | バグ修正タスク（任意） | - |
| `sdd:docfix` | ドキュメント修正タスク（任意） | - |

> **DONEステータス**: 専用ラベルは使わず、**Issueをclose**（state_reason: `completed`）することで表現する。

---

## ステータスとGitHub Issue状態の対応

| SDDステータス | Issue状態 | ラベル操作 |
|--------------|-----------|-----------|
| `TODO` | open | `sdd:status/todo` |
| `IN_PROGRESS` | open | `sdd:status/todo` を外し `sdd:status/in-progress` を付与 |
| `REVIEW` | open | `sdd:status/review` に付け替え |
| `BLOCKED` | open | `sdd:status/blocked` に付け替え |
| `DONE` | **closed** | ステータスラベルを外し、Issueをclose（completed） |

---

## 目次（index.md）の代替

Issueモードでは `docs/sdd/tasks/index.md` を作成しません。タスク一覧・進捗の把握は
GitHub Issue検索で行います：

- 全タスク: `label:sdd:task`
- 未着手のみ: `label:sdd:task label:sdd:status/todo state:open`
- Phase 1: `label:sdd:task label:sdd:phase-1`
- 完了タスク: `label:sdd:task state:closed`

取得には `mcp__github__list_issues`（`labels` 指定）または `mcp__github__search_issues` を使用する。
