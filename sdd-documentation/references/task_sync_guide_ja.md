# タスク同期ガイド

## 概要

SDDスキルで管理する`docs/sdd/tasks/`のタスクと、Claude Codeが内部で管理するTodoWriteのタスクを同期するためのガイドです。

### 目的

- **ユーザーへのリアルタイム進捗表示**: TodoWriteによりClaude CodeのUI上でタスクの進捗が見える
- **詳細仕様の保持**: docs/sdd/tasks/には受入基準・TDD手順・技術仕様を記載
- **エージェントチームとの連携**: チームメンバーのタスク完了もTodoWriteに反映

### 原則

```text
docs/sdd/tasks/ = Source of Truth（正）
TodoWrite   = 可視化レイヤー（副）
```

- 詳細な仕様・受入基準・TDD手順はdocs/sdd/tasks/に記載
- TodoWriteはタスクID・タイトル・ステータスのみ管理
- 同期の方向は常に SDD → TodoWrite（一方向）
- **非SDDタスクを保持**: TodoWrite更新時、SDDスキル以外で作成されたtodoを上書きしない

## マージプロトコル（非SDDタスクとの共存）

### 背景

Claude Codeはユーザーの指示に応じて自律的にTodoWriteにタスクを作成することがある（SDDスキルを経由しないタスク）。SDDスキルがTodoWriteを同期する際、これらの非SDDタスクを上書きしてはならない。

### 識別ルール

contentの**先頭パターン**でSDDタスクか非SDDタスクかを判定する:

| 種別 | 識別方法 | 例 |
|------|---------|-----|
| SDDタスク | contentが`[Phase-`または`[BLOCKED] [Phase-`で始まる | `[Phase-1/TASK-001] API実装` |
| 非SDDタスク | 上記パターンで始まらない | `テストを実行する` |

**注意**: `[TASK-`を含むかどうかではなく、先頭パターンで判定すること。contentの途中に`[TASK-`が含まれる非SDDタスク（例: `Review [TASK-001] implementation`）を誤検知しないため。

### マージ手順

SDDタスクをTodoWriteに同期する際は、以下の手順に従う:

```text
1. 現在のTodoWriteリストを確認する（直前のTodoWrite呼び出し内容を参照）
2. 非SDDタスクを抽出: contentが`[Phase-`または`[BLOCKED] [Phase-`で始まらないtodoを保持リストに入れる
3. SDDタスクを構築: docs/sdd/tasks/から最新のタスク一覧を構築
4. マージして書き込み: 非SDDタスク（保持） + SDDタスク（同期）をTodoWriteに渡す
```

### マージ例

```text
TodoWrite更新前:
  - "調査: 既存APIの仕様を確認する" (pending)    ← 非SDD（保持する）
  - "[Phase-1/TASK-001] API実装" (pending)       ← SDD

TASK-001のステータスがIN_PROGRESSに変わった場合:

TodoWrite更新後:
  - "調査: 既存APIの仕様を確認する" (pending)    ← 保持された
  - "[Phase-1/TASK-001] API実装" (in_progress)   ← 更新された
```

### 注意事項

- SDDスキルが管理するのはSDDタスク（contentが`[Phase-`または`[BLOCKED] [Phase-`で始まるtodo）のみ
- 非SDDタスクのステータスや内容をSDDスキルが変更してはならない
- 非SDDタスクの順序は保持する（先頭に配置）

## ステータスマッピング

| SDD (docs/sdd/tasks/) | TodoWrite status | TodoWrite表示 |
|-------------------|-----------------|---------------|
| `TODO` | `pending` | 未着手として表示 |
| `IN_PROGRESS` | `in_progress` | 実行中として表示 |
| `DONE` | `completed` | 完了として表示 |
| `BLOCKED` | `pending` | contentに`[BLOCKED]`付記 |
| `REVIEW` | `in_progress` | contentに`[REVIEW]`付記 |

## 同期手順

### 1. タスク計画完了時（task-planning）

docs/sdd/tasks/のすべてのタスクをTodoWriteに一括登録します。

**トリガー**: task-planningスキルがタスク一覧を作成完了した時点

**手順**:

```text
1. docs/sdd/tasks/index.mdからタスク一覧を読み取る
2. 各タスクのID、タイトル、ステータスを取得
3. 現在のTodoWriteから非SDDタスク（contentが[Phase-または[BLOCKED] [Phase-で始まらないtodo）を抽出して保持
4. 非SDDタスク + SDDタスクをマージしてTodoWriteに登録:

TodoWrite({
  todos: [
    // --- 非SDDタスク（既存を保持） ---
    { content: "調査: 既存仕様の確認", status: "completed", activeForm: "..." },
    // --- SDDタスク（新規登録） ---
    {
      content: "[Phase-1/TASK-001] ユーザー認証APIの実装",
      status: "pending",
      activeForm: "[TASK-001] ユーザー認証APIの実装"
    },
    {
      content: "[Phase-1/TASK-002] データモデルの定義",
      status: "pending",
      activeForm: "[TASK-002] データモデルの定義"
    },
    {
      content: "[Phase-2/TASK-003] API統合テスト",
      status: "pending",
      activeForm: "[TASK-003] API統合テスト"
    }
  ]
})

注意: activeFormはin_progress時にUIに表示される。pending登録時はcontentと同等の
静的な表現を使用し、「〜を実装中」のような進行形はin_progressへの遷移時に設定する。
非SDDタスクが存在しない場合はSDDタスクのみで構成する。
```

**命名規則**:
- content: `[Phase-N/TASK-XXX] タスクタイトル`
- activeForm: `[TASK-XXX] タスクタイトルを{動詞}中`

### 2. タスク開始時（task-executing）

タスクの実行開始時にTodoWriteのステータスを更新します。

**トリガー**: task-executingがタスクのステータスをIN_PROGRESSに変更した時点

**手順**:

```text
1. docs/sdd/tasks/phase-N/TASK-XXX.mdのステータスをIN_PROGRESSに更新
2. docs/sdd/tasks/index.mdを更新
3. コミット
4. TodoWriteで該当タスクをin_progressに更新:

TodoWrite({
  todos: [
    { content: "[Phase-1/TASK-001] ユーザー認証APIの実装", status: "in_progress", activeForm: "..." },
    { content: "[Phase-1/TASK-002] データモデルの定義", status: "pending", activeForm: "..." },
    ...
  ]
})
```

**注意**: TodoWriteは全体を置き換えるため、変更対象以外のtodoもすべて含めること。非SDDタスク（contentが`[Phase-`で始まらないtodo）が存在する場合もそのまま保持して含めること。

### 3. タスク完了時（task-executing）

タスクの完了時にTodoWriteのステータスを更新します。

**トリガー**: task-executingがタスクのステータスをDONEに変更した時点

**手順**:

```text
1. docs/sdd/tasks/phase-N/TASK-XXX.mdのステータスをDONEに更新
2. docs/sdd/tasks/index.mdを更新
3. コミット
4. TodoWriteで該当タスクをcompletedに更新
5. 次のタスクがあればin_progressに設定
```

### 4. タスクブロック時

**トリガー**: task-executingがタスクのステータスをBLOCKEDに変更した時点

**手順**:

```text
1. docs/sdd/tasks/のステータスをBLOCKEDに更新
2. TodoWriteで該当タスクのcontentを更新:

content: "[BLOCKED] [Phase-1/TASK-001] ユーザー認証APIの実装"
status: "pending"
```

### 5. トラブルシュートでタスク追加時（sdd-troubleshooting）

**トリガー**: sdd-troubleshootingが修正タスクをdocs/sdd/tasks/に追加した時点

**手順**:

```text
1. docs/sdd/tasks/に新規TASK-XXX.mdを作成
2. TodoWriteに追加:
   既存のtodoリスト + 新しいtodo:
   { content: "[Phase-N/TASK-XXX] [BugFix] 問題の修正", status: "pending", activeForm: "..." }
```

### 6. ドキュメント管理でタスク追加時（sdd-document-management）

**トリガー**: sdd-document-managementが整合性修正タスクを追加した時点

**手順**:

```text
1. docs/sdd/tasks/に新規TASK-XXX.mdを作成
2. TodoWriteに追加:
   { content: "[Phase-N/TASK-XXX] [DocFix] ドキュメント修正", status: "pending", activeForm: "..." }
```

## エージェントチームとの連携

### チームリーダーの責務

エージェントチームで並列タスク実行する場合、TodoWriteの更新はリーダーが担当します:

```text
1. チームメンバーをスポーン（各メンバーにタスクを割り当て）
2. メンバーが完了報告を送信
3. リーダーがTodoWriteを一括更新:
   - 完了したタスク → completed
   - 次の実行対象タスク → in_progress
4. すべてのメンバー完了後、最終更新
```

### チームメンバーの責務

チームメンバーは自分の担当TASK-XXX.mdのステータスのみ更新します:

```text
1. 自分の担当TASK-XXX.mdのステータスをIN_PROGRESSに更新
2. 実装を実行
3. TASK-XXX.mdのステータスをDONEに更新
4. リーダーに完了メッセージを送信

★ docs/sdd/tasks/index.mdの更新はリーダーに委任（マージ競合回避） ★
★ TodoWriteの更新はリーダーに委任 ★
```

### 理由

- チームメンバーはリーダーのTodoWriteの現在の状態を知らない
- 複数メンバーが同時にTodoWriteを更新すると状態が不整合になる
- リーダーが一元管理することで整合性を維持

## タスクIDの命名規則

### 通常タスク

```text
content: "[Phase-1/TASK-001] ユーザー認証APIの実装"
```

### バグ修正タスク

```text
content: "[Phase-2/TASK-010] [BugFix] 認証トークンの有効期限修正"
```

### ドキュメント修正タスク

```text
content: "[Phase-3/TASK-015] [DocFix] 設計書のAPI定義更新"
```

### BLOCKEDタスク

```text
content: "[BLOCKED] [Phase-1/TASK-003] 外部API連携の実装"
```

## 注意事項

### TodoWriteの制約

- TodoWriteは全体を置き換える（差分更新ではない）
- 更新時は既存のtodoリスト全体を渡す必要がある
- in_progressは同時に1つのみが推奨（ただしチーム実行時は複数可）

### 非SDDタスクの保護

- TodoWrite更新時は、SDDタスク以外のtodoを必ず保持すること
- SDDスキルが管理するのはSDDタスク（contentが`[Phase-`または`[BLOCKED] [Phase-`で始まるtodo）のみ
- 非SDDタスクのステータスや内容をSDDスキルが変更してはならない

### 同期が不要な場面

- 要件定義（requirements-defining）: タスクがまだ存在しない
- 設計（software-designing）: タスクがまだ存在しない
- 逆順レビュー: タスクの状態変更がない（レビュー結果は別途報告）

### 同期漏れの防止

各スキルのワークフロー内に「TodoWrite同期」ステップを明示的に含める:

```text
5. 実装
   ↓
6. 受入基準の確認
   ↓
7. docs/sdd/tasks/のステータスを更新（SDD = Source of Truth）
   ↓
8. コミット作成
   ↓
9. ★ TodoWrite同期 ★  ← SDD更新・コミット後にTodoWriteへ反映
```

**順序の原則**: docs/sdd/tasks/（SDD）の更新とコミットを先に行い、その後TodoWriteに反映する。SDDが正であるため、先にSource of Truthを確定させる。
