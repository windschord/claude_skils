# タスク同期ガイド


<!-- TOC -->
## 目次

- [概要](#概要)
  - [目的](#目的)
  - [原則](#原則)
- [マージプロトコル（非SDDタスクとの共存）](#マージプロトコル非sddタスクとの共存)
  - [背景](#背景)
  - [識別ルール](#識別ルール)
  - [マージ手順](#マージ手順)
  - [マージ例](#マージ例)
  - [注意事項](#注意事項)
- [ステータスマッピング](#ステータスマッピング)
- [同期手順](#同期手順)
  - [1. タスク計画完了時（task-planning）](#1-タスク計画完了時task-planning)
  - [2. タスク開始時（task-executing）](#2-タスク開始時task-executing)
  - [3. タスク完了時（task-executing）](#3-タスク完了時task-executing)
  - [4. タスクブロック時](#4-タスクブロック時)
  - [5. トラブルシュートでタスク追加時（sdd-troubleshooting）](#5-トラブルシュートでタスク追加時sdd-troubleshooting)
  - [6. ドキュメント管理でタスク追加時（sdd-document-management）](#6-ドキュメント管理でタスク追加時sdd-document-management)
- [エージェントチームとの連携](#エージェントチームとの連携)
  - [チームリーダーの責務](#チームリーダーの責務)
  - [チームメンバーの責務](#チームメンバーの責務)
  - [理由](#理由)
- [タスクIDの命名規則](#タスクidの命名規則)
  - [通常タスク](#通常タスク)
  - [バグ修正タスク](#バグ修正タスク)
  - [ドキュメント修正タスク](#ドキュメント修正タスク)
  - [BLOCKEDタスク](#blockedタスク)
- [注意事項](#注意事項-1)
  - [TodoWriteの制約](#todowriteの制約)
  - [非SDDタスクの保護](#非sddタスクの保護)
  - [同期が不要な場面](#同期が不要な場面)
  - [同期漏れの防止](#同期漏れの防止)
<!-- /TOC -->

## 概要

SDDスキルで管理するタスクと、Claude Codeが内部で管理するTodoWriteのタスクを同期するためのガイドです。

タスクの管理先には2モードあります。同期のロジックは共通で、参照元がIssueかファイルかが異なるだけです。

| モード | タスク管理先（Source of Truth） | 使う場面 |
|--------|-------------------------------|----------|
| **Issueモード（デフォルト）** | GitHub Issue（`label:sdd:task`） | 指定がない場合は常にこちら |
| ファイルモード（オプション） | `docs/sdd/tasks/` | ユーザーが「ファイルで」と明示した場合 |

### 目的

- **ユーザーへのリアルタイム進捗表示**: TodoWriteによりClaude CodeのUI上でタスクの進捗が見える
- **詳細仕様の保持**: Issue本文（Issueモード）／docs/sdd/tasks/（ファイルモード）に受入基準・TDD手順・技術仕様を記載
- **エージェントチームとの連携**: チームメンバーのタスク完了もTodoWriteに反映

### 原則

```text
Issueモード:  GitHub Issue（label:sdd:task） = Source of Truth（正）
ファイルモード: docs/sdd/tasks/               = Source of Truth（正）
TodoWrite                                    = 可視化レイヤー（副）
```

- 詳細な仕様・受入基準・TDD手順はSource of Truth（Issue本文 or docs/sdd/tasks/）に記載
- TodoWriteはタスクID・タイトル・ステータス（＋Issueモードでは `(#Issue番号)`）のみ管理
- 同期の方向は常に SDD（Issue/ファイル） → TodoWrite（一方向）
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

| SDDステータス | Issueモード（GitHub Issue） | ファイルモード | TodoWrite status | TodoWrite表示 |
|--------------|----------------------------|---------------|-----------------|---------------|
| `TODO` | open + `sdd:status/todo` | `TODO` | `pending` | 未着手として表示 |
| `IN_PROGRESS` | open + `sdd:status/in-progress` | `IN_PROGRESS` | `in_progress` | 実行中として表示 |
| `DONE` | **closed**（completed） | `DONE` | `completed` | 完了として表示 |
| `BLOCKED` | open + `sdd:status/blocked` | `BLOCKED` | `pending` | contentに`[BLOCKED]`付記 |
| `REVIEW` | open + `sdd:status/review` | `REVIEW` | `in_progress` | contentに`[REVIEW]`付記 |

## 同期手順

### 1. タスク計画完了時（task-planning）

すべてのタスクをTodoWriteに一括登録します。

**トリガー**: task-planningスキルがタスク一覧を作成完了した時点

**手順**:

```text
1. タスク一覧を読み取る
   - Issueモード: mcp__github__list_issues（labels: ["sdd:task"]）で起票済みIssueを取得
   - ファイルモード: docs/sdd/tasks/index.mdからタスク一覧を読み取る
2. 各タスクのID、タイトル、ステータス（Issueモードでは Issue番号）を取得
3. 現在のTodoWriteから非SDDタスク（contentが[Phase-または[BLOCKED] [Phase-で始まらないtodo）を抽出して保持
4. 非SDDタスク + SDDタスクをマージしてTodoWriteに登録:

TodoWrite({
  todos: [
    // --- 非SDDタスク（既存を保持） ---
    { content: "調査: 既存仕様の確認", status: "completed", activeForm: "..." },
    // --- SDDタスク（新規登録／Issueモードは (#Issue番号) を付与） ---
    {
      content: "[Phase-1/TASK-001](#12) ユーザー認証APIの実装",
      status: "pending",
      activeForm: "[TASK-001] ユーザー認証APIの実装"
    },
    {
      content: "[Phase-1/TASK-002](#13) データモデルの定義",
      status: "pending",
      activeForm: "[TASK-002] データモデルの定義"
    },
    {
      content: "[Phase-2/TASK-003](#14) API統合テスト",
      status: "pending",
      activeForm: "[TASK-003] API統合テスト"
    }
  ]
})

注意: activeFormはin_progress時にUIに表示される。pending登録時はcontentと同等の
静的な表現を使用し、「〜を実装中」のような進行形はin_progressへの遷移時に設定する。
非SDDタスクが存在しない場合はSDDタスクのみで構成する。
ファイルモードでは (#Issue番号) を省略する。
```

**命名規則**:
- content: `[Phase-N/TASK-XXX](#Issue番号) タスクタイトル`（ファイルモードは `(#Issue番号)` を省略）
- activeForm: `[TASK-XXX] タスクタイトルを{動詞}中`

### 2. タスク開始時（task-executing）

タスクの実行開始時にTodoWriteのステータスを更新します。

**トリガー**: task-executingがタスクのステータスをIN_PROGRESSに変更した時点

**手順**:

```text
1. Source of Truthのステータスを IN_PROGRESS に更新
   - Issueモード: mcp__github__issue_write（update）で `sdd:status/todo` を外し `sdd:status/in-progress` を付与
   - ファイルモード: docs/sdd/tasks/phase-N/TASK-XXX.md と index.md のステータスを更新してコミット
2. TodoWriteで該当タスクをin_progressに更新:

TodoWrite({
  todos: [
    { content: "[Phase-1/TASK-001](#12) ユーザー認証APIの実装", status: "in_progress", activeForm: "..." },
    { content: "[Phase-1/TASK-002](#13) データモデルの定義", status: "pending", activeForm: "..." },
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
1. Source of Truthを DONE に更新
   - Issueモード: mcp__github__issue_write（update）でステータスラベルを外し、Issueをclose（state: closed, state_reason: completed）
   - ファイルモード: docs/sdd/tasks/phase-N/TASK-XXX.md と index.md のステータスをDONEに更新してコミット
2. TodoWriteで該当タスクをcompletedに更新
3. 次のタスクがあればin_progressに設定
```

### 4. タスクブロック時

**トリガー**: task-executingがタスクのステータスをBLOCKEDに変更した時点

**手順**:

```text
1. Source of Truthを BLOCKED に更新
   - Issueモード: `sdd:status/blocked` に付け替え（Issueはopenのまま）
   - ファイルモード: docs/sdd/tasks/のステータスをBLOCKEDに更新
2. TodoWriteで該当タスクのcontentを更新:

content: "[BLOCKED] [Phase-1/TASK-001](#12) ユーザー認証APIの実装"
status: "pending"
```

### 5. トラブルシュートでタスク追加時（sdd-troubleshooting）

**トリガー**: sdd-troubleshootingが修正タスクを追加した時点

**手順**:

```text
1. 修正タスクを作成
   - Issueモード: mcp__github__issue_write（create）でラベル `sdd:task` + `sdd:bugfix` 付きIssueを起票
   - ファイルモード: docs/sdd/tasks/に新規TASK-XXX.mdを作成
2. TodoWriteに追加:
   既存のtodoリスト + 新しいtodo:
   { content: "[Phase-N/TASK-XXX](#12) [BugFix] 問題の修正", status: "pending", activeForm: "..." }
```

### 6. ドキュメント管理でタスク追加時（sdd-document-management）

**トリガー**: sdd-document-managementが整合性修正タスクを追加した時点

**手順**:

```text
1. 修正タスクを作成
   - Issueモード: mcp__github__issue_write（create）でラベル `sdd:task` + `sdd:docfix` 付きIssueを起票
   - ファイルモード: docs/sdd/tasks/に新規TASK-XXX.mdを作成
2. TodoWriteに追加:
   { content: "[Phase-N/TASK-XXX](#12) [DocFix] ドキュメント修正", status: "pending", activeForm: "..." }
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

チームメンバーは自分の担当タスクのステータスのみ更新します:

```text
1. 自分の担当タスクのステータスをIN_PROGRESSに更新
   - Issueモード: 担当Issueを `sdd:status/in-progress` に付け替え
   - ファイルモード: 担当TASK-XXX.mdのステータスをIN_PROGRESSに更新
2. 実装を実行
3. 担当タスクをDONEに更新
   - Issueモード: 担当Issueをclose（completed）
   - ファイルモード: TASK-XXX.mdのステータスをDONEに更新
4. リーダーに完了メッセージを送信

★ ファイルモードのindex.md更新はリーダーに委任（マージ競合回避） ★
★ TodoWriteの更新はリーダーに委任 ★
```

### 理由

- チームメンバーはリーダーのTodoWriteの現在の状態を知らない
- 複数メンバーが同時にTodoWriteを更新すると状態が不整合になる
- リーダーが一元管理することで整合性を維持

## タスクIDの命名規則

> Issueモードでは末尾に `(#Issue番号)` を付ける。ファイルモードでは省略する。
> 先頭の識別パターン（`[Phase-` / `[BLOCKED] [Phase-`）は両モード共通。

### 通常タスク

```text
content: "[Phase-1/TASK-001](#12) ユーザー認証APIの実装"
```

### バグ修正タスク

```text
content: "[Phase-2/TASK-010](#20) [BugFix] 認証トークンの有効期限修正"
```

### ドキュメント修正タスク

```text
content: "[Phase-3/TASK-015](#25) [DocFix] 設計書のAPI定義更新"
```

### BLOCKEDタスク

```text
content: "[BLOCKED] [Phase-1/TASK-003](#14) 外部API連携の実装"
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
7. Source of Truthのステータスを更新
     - Issueモード: Issueのラベル付け替え／close
     - ファイルモード: docs/sdd/tasks/更新＋コミット
   ↓
8. （ファイルモードのみ）コミット作成
   ↓
9. ★ TodoWrite同期 ★  ← Source of Truth更新後にTodoWriteへ反映
```

**順序の原則**: Source of Truth（IssueモードはGitHub Issue、ファイルモードはdocs/sdd/tasks/）の更新を先に行い、その後TodoWriteに反映する。SDDが正であるため、先にSource of Truthを確定させる。
