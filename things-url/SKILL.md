---
name: things-url
description: Things 3とClaude Codeのタスクを双方向で共有する。URLスキームによるタスク送信とAppleScriptによるタスク読み取りに対応する。macOS環境でThings 3とのタスク同期が必要な場合に使用する。Do NOT use for macOS以外の環境でのタスク管理。
metadata:
  version: "1.0.0"
---

# Things URL タスク共有スキル

Claude Codeで管理しているタスクとThings 3を双方向で共有するスキルです。URLスキームによるタスク送信（書き込み）と、AppleScript（osascript）によるタスク読み取りの両方をサポートし、人間とClaude Codeが同じタスク情報を共有できます。

## 概要

このスキルは以下の機能を提供します：

### 書き込み（Claude Code → Things 3）
- docs/sdd/tasks/のタスクをThings 3のプロジェクト・To-Doとして送信
- TodoWriteの現在のタスクリストをThings 3に送信
- 個別のTo-Do・プロジェクトを作成するURLを生成
- `add-json`コマンドによる一括インポートURL生成
- macOSの`open`コマンドによるURL直接実行

### 読み取り（Things 3 → Claude Code）（macOS限定）
- Things 3の今日・受信箱・各リストのタスクを取得
- プロジェクト一覧とプロジェクト内タスクの取得
- タスクの完了状態・タグ・メモの読み取り
- Things 3のタスク状態をTodoWriteやdocs/sdd/tasks/に反映

## このスキルを使用する場面

以下の状況でこのスキルを使用してください：

### タスク共有時（書き込み）
- Claude Codeで作成したタスクを人間のThings 3に反映したい場合
- SDDのタスク一覧を人間と共有したい場合
- プロジェクトの進捗を人間側でも確認可能にしたい場合

### タスク読み取り時（読み取り）
- Things 3で人間が管理しているタスクの状況を確認したい場合
- Things 3で完了マークされたタスクをClaude Code側にも反映したい場合
- Things 3のタスクをTodoWriteやdocs/sdd/tasks/に同期したい場合
- 「Thingsの今日のタスクを教えて」「プロジェクトの進捗を確認して」と依頼された場合

### プロジェクト管理時
- SDDのフェーズ全体をThingsプロジェクトとして管理したい場合
- 人間が確認すべきレビュータスクをThingsに送りたい場合
- 人間とClaude Codeのタスク分担を明確にしたい場合

## 基本的な使い方

### 1. SDDタスクをThingsに送信

「タスクをThingsに送って」「SDDのタスクをThingsと共有して」などと依頼されたら：

1. **docs/sdd/tasks/の読み取り**
   - タスク一覧（index）を確認
   - 各タスクのステータス・詳細を把握

2. **送信対象の確認**
   - ユーザーにどのタスクを送信するか確認
   - 全タスク or 特定ステータスのタスクのみ、を選択してもらう

3. **Things URL の生成**
   - タスク構造に応じて `add`、`add-project`、または `add-json` を使い分ける
   - URLをユーザーに提示

4. **URLの実行**
   - macOS環境であれば`open`コマンドで直接実行を提案
   - それ以外の場合はURLをコピー可能な形式で出力

### 2. TodoWriteタスクをThingsに送信

「今のタスクリストをThingsに送って」と依頼されたら：

1. **現在のTodoWriteの状態を確認**
   - pending/in_progress/completedの各タスクを把握

2. **Things URLを生成**
   - 各タスクをTo-Doとして`add-json`で一括作成
   - ステータスに応じたタグ付け（例: `in_progress` → タグ「進行中」）

3. **URLを実行または提示**

### 3. 個別タスクの作成

「Thingsにタスクを追加して」と依頼されたら：

1. タスクの内容をヒアリング
2. `things:///add` URLを生成
3. 実行または提示

### 4. Things 3のタスクを読み取る（macOS限定）

「Thingsのタスクを確認して」「今日のタスクを教えて」「Thingsから同期して」と依頼されたら：

1. **macOS環境の確認**
   - `uname`コマンドでmacOSであることを確認
   - macOS以外の場合はAppleScriptが使えない旨を伝えて終了

2. **読み取り対象の確認**
   - ユーザーにどのリスト/プロジェクトを読みたいか確認
   - 選択肢：今日、受信箱、特定のプロジェクト、全プロジェクト一覧

3. **AppleScriptでデータ取得**
   - `osascript`コマンドでThings 3からタスクデータを読み取る
   - 詳細は [AppleScriptリファレンス](references/applescript_reference_ja.md) を参照

4. **結果の表示**
   - 取得したタスク一覧を整形して表示
   - 必要に応じてTodoWriteやdocs/sdd/tasks/への同期を提案

### 5. Things 3のタスクをTodoWriteに同期する（macOS限定）

「ThingsのタスクをTodoWriteに反映して」と依頼されたら：

1. **Things 3からタスクを読み取る**（上記ステップ4と同様）
2. **現在のTodoWriteの状態と比較**
3. **ステータスのマッピング**（Things → TodoWrite）

   | Things status | Things tag | TodoWrite status |
   |---|---|---|
   | `open` | `進行中` | `in_progress` |
   | `open` | `TODO` またはタグなし | `pending` |
   | `open` | `レビュー` | `in_progress`（`[REVIEW]`付記） |
   | `open` | `ブロック` | `pending`（`[BLOCKED]`付記） |
   | `completed` | - | `completed` |
   | `canceled` | - | 除外（同期対象外） |

4. **ユーザー確認**
   - 変更内容を表示し、同期してよいか確認
5. **TodoWriteを更新**

### 6. Things 3のタスクをSDDタスクに同期する（macOS限定）

「ThingsのステータスをSDDに反映して」と依頼されたら：

1. **Things 3から該当プロジェクトのタスクを読み取る**
2. **docs/sdd/tasks/と照合**
   - タスク名に含まれる`[TASK-XXX]`のIDで照合
3. **ステータスの差分を検出**

   | Things status | Things tag | SDD ステータス |
   |---|---|---|
   | `open` | `TODO` | TODO |
   | `open` | `進行中` | IN_PROGRESS |
   | `open` | `レビュー` | REVIEW |
   | `open` | `ブロック` | BLOCKED |
   | `completed` | - | DONE |
   | `canceled` | - | 除外（同期対象外） |

4. **差分をユーザーに提示**
   - 変更があるタスクの一覧を表示
5. **ユーザー承認後にdocs/sdd/tasks/を更新**

## URL生成の原則

### コマンドの使い分け

| ユースケース | コマンド | 説明 |
|---|---|---|
| 単一のTo-Do作成 | `things:///add` | 1つのタスクを素早く追加 |
| プロジェクト作成 | `things:///add-project` | 見出し付きプロジェクトを作成 |
| 複数アイテム一括作成 | `things:///add-json` | 複雑な構造を一度に送信 |
| 既存アイテム表示 | `things:///show` | Things内のリストを表示 |
| 検索 | `things:///search` | Things内をキーワード検索 |

### パラメータのエンコーディング

すべてのパラメータはURLエンコード（パーセントエンコーディング）が必要です：

```text
タイトル: "APIの実装"
→ エンコード後: API%E3%81%AE%E5%AE%9F%E8%A3%85
```

**重要**: URLエンコードにはBashの`python3 -c`や`jq`を使用してください。手動でのエンコードは行いません。

### URL生成のコード例

#### 単一To-Doの追加（add）

```bash
# python3を使ったURLエンコードと実行
python3 -c "
import urllib.parse
params = {
    'title': 'APIエンドポイントの実装をレビュー',
    'notes': 'Claude Codeが実装したPOST /api/auth/loginのレビュー\n\n受入基準:\n- テスト通過\n- ESLintエラーゼロ',
    'when': 'today',
    'tags': 'Claude Code,レビュー',
    'list': 'プロジェクト名'
}
query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
url = f'things:///add?{query}'
print(url)
"
```

#### プロジェクトの追加（add-project）

```bash
python3 -c "
import urllib.parse
params = {
    'title': 'SDD Phase 1: 基盤構築',
    'notes': 'SDDタスク管理 - Phase 1のタスク一覧',
    'when': 'today',
    'tags': 'SDD,Claude Code',
    'to-dos': '\n'.join([
        'TASK-001: データモデルの定義',
        'TASK-002: APIエンドポイントの実装',
        'TASK-003: 認証ミドルウェアの実装',
    ])
}
query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
url = f'things:///add-project?{query}'
print(url)
"
```

#### JSON一括インポート（add-json）

```bash
python3 -c "
import urllib.parse, json

data = [
    {
        'type': 'project',
        'attributes': {
            'title': 'SDD Phase 1: 基盤構築',
            'notes': 'Claude Codeで管理中のSDDタスク',
            'when': 'today',
            'tags': ['SDD', 'Claude Code'],
            'items': [
                {
                    'type': 'heading',
                    'attributes': {
                        'title': 'データ層'
                    }
                },
                {
                    'type': 'to-do',
                    'attributes': {
                        'title': 'TASK-001: データモデルの定義',
                        'notes': '推定工数: 1時間\nステータス: TODO',
                        'tags': ['TODO']
                    }
                },
                {
                    'type': 'to-do',
                    'attributes': {
                        'title': 'TASK-002: APIエンドポイントの実装',
                        'notes': '推定工数: 2時間\nステータス: TODO\n依存: TASK-001',
                        'tags': ['TODO']
                    }
                },
                {
                    'type': 'heading',
                    'attributes': {
                        'title': 'ミドルウェア層'
                    }
                },
                {
                    'type': 'to-do',
                    'attributes': {
                        'title': 'TASK-003: 認証ミドルウェアの実装',
                        'notes': '推定工数: 1.5時間\nステータス: IN_PROGRESS\n依存: TASK-001',
                        'tags': ['IN_PROGRESS']
                    }
                }
            ]
        }
    }
]

json_str = json.dumps(data, ensure_ascii=False)
encoded = urllib.parse.quote(json_str)
url = f'things:///add-json?data={encoded}'
print(url)
"
```

### URLの実行方法

```bash
# macOSで直接実行
open "things:///add?title=..."

# URLが長い場合は変数に格納して実行
URL=$(python3 -c "...URL生成スクリプト...")
open "$URL"
```

**注意**: `open`コマンドはmacOSでのみ動作します。実行前にOSを確認してください。

## SDDタスクのマッピング

### ステータスの対応

SDDタスクのステータスをThingsの状態にマッピングします：

| SDD ステータス | Things 状態 | タグ | when |
|---|---|---|---|
| TODO | 未完了 | `TODO` | （設定なし） |
| IN_PROGRESS | 未完了 | `進行中` | `today` |
| REVIEW | 未完了 | `レビュー` | `today` |
| DONE | 完了 | `完了` | （設定なし） |
| BLOCKED | 未完了 | `ブロック` | `someday` |

### タスク構造のマッピング

```text
docs/sdd/tasks/
├── index.md           → Things プロジェクト（全体）
├── phase-1/
│   ├── task-001.md    → Things To-Do（見出し「Phase 1」配下）
│   ├── task-002.md    → Things To-Do
│   └── task-003.md    → Things To-Do
└── phase-2/
    ├── task-004.md    → Things To-Do（見出し「Phase 2」配下）
    └── task-005.md    → Things To-Do
```

**マッピング結果**：
```text
Things プロジェクト: [プロジェクト名] SDDタスク
├── 見出し: Phase 1 - [フェーズ名]
│   ├── To-Do: TASK-001: [タスク名]
│   ├── To-Do: TASK-002: [タスク名]
│   └── To-Do: TASK-003: [タスク名]
└── 見出し: Phase 2 - [フェーズ名]
    ├── To-Do: TASK-004: [タスク名]
    └── To-Do: TASK-005: [タスク名]
```

### 受入基準のマッピング

タスクの受入基準はThingsのチェックリストにマッピングします：

```python
# 受入基準 → チェックリスト
{
    "type": "to-do",
    "attributes": {
        "title": "TASK-001: データモデルの定義",
        "checklist-items": [
            {"title": "prisma/schema.prismaにUserモデルが定義されている"},
            {"title": "prisma migrateが正常に実行できる"},
            {"title": "TypeScript型定義が自動生成される"}
        ]
    }
}
```

## ワークフロー

### SDDタスク一括送信フロー

```text
1. docs/sdd/tasks/のindex.mdを読み取る
   ↓
2. 各フェーズのタスク詳細を読み取る
   ↓
3. ユーザーに送信対象を確認（全タスク or フィルタ）
   ↓
4. タスク構造をThings JSONにマッピング
   ↓
5. add-json URLを生成
   ↓
6. ユーザーに確認してURL実行
   ↓
7. 完了を報告
```

### 詳細な実行手順

#### ステップ1: タスクの読み取りと確認

```text
[things-url] ステップ 1/4: docs/sdd/tasks/を読み取り中...

docs/sdd/tasks/から以下のタスクを検出しました：

Phase 1: 基盤構築（3タスク）
  - TASK-001: データモデルの定義 [TODO]
  - TASK-002: APIエンドポイントの実装 [IN_PROGRESS]
  - TASK-003: 認証ミドルウェア [TODO]

Phase 2: UI実装（2タスク）
  - TASK-004: ログイン画面 [TODO]
  - TASK-005: ダッシュボード [TODO]

すべてのタスクをThingsに送信しますか？
それとも特定のフェーズ・ステータスでフィルタしますか？
```

#### ステップ2: JSONの構築

```text
[things-url] ステップ 2/4: Things JSON を構築中...

以下の構造でThingsに送信します：

プロジェクト: [プロジェクト名] SDDタスク
├── Phase 1: 基盤構築
│   ├── TASK-001: データモデルの定義 [タグ: TODO]
│   ├── TASK-002: APIエンドポイントの実装 [タグ: 進行中, when: today]
│   └── TASK-003: 認証ミドルウェア [タグ: TODO]
└── Phase 2: UI実装
    ├── TASK-004: ログイン画面 [タグ: TODO]
    └── TASK-005: ダッシュボード [タグ: TODO]

この内容でURLを生成してよろしいですか？
```

#### ステップ3: URL生成と実行

```text
[things-url] ステップ 3/4: Things URL を生成中...

URLを生成しました。macOS環境のため直接実行します。
```

```bash
# URL生成と実行
URL=$(python3 -c "
import urllib.parse, json
# ... JSON構築とエンコード ...
")
open "$URL"
```

#### ステップ4: 完了報告

```text
[things-url] ステップ 4/4: 完了

Things 3に以下を送信しました：
- プロジェクト: 1件
- 見出し: 2件
- To-Do: 5件

Things 3アプリで確認してください。
```

### TodoWriteタスク送信フロー

```text
1. 現在のTodoWriteタスクを取得
   ↓
2. Things To-DoのJSON配列に変換
   ↓
3. ステータスに応じたタグ・when設定
   ↓
4. add-json URLを生成・実行
   ↓
5. 完了を報告
```

**変換例**：

TodoWriteの状態:
```text
- [x] TASK-001: データモデルの定義（completed）
- [>] TASK-002: APIエンドポイントの実装（in_progress）
- [ ] TASK-003: 認証ミドルウェア（pending）
```

Things JSONへの変換:
```json
[
  {
    "type": "to-do",
    "attributes": {
      "title": "TASK-001: データモデルの定義",
      "completed": true,
      "tags": ["完了"]
    }
  },
  {
    "type": "to-do",
    "attributes": {
      "title": "TASK-002: APIエンドポイントの実装",
      "when": "today",
      "tags": ["進行中"]
    }
  },
  {
    "type": "to-do",
    "attributes": {
      "title": "TASK-003: 認証ミドルウェア",
      "tags": ["TODO"]
    }
  }
]
```

## Things 3からの読み取り（macOS限定）

### 前提条件の確認

読み取り機能を使用する前に、macOS環境であることを確認します：

```bash
if [[ "$(uname)" != "Darwin" ]]; then
    echo "読み取り機能はmacOS環境でのみ利用可能です"
    exit 1
fi
```

### 今日のタスクを読み取る

```text
[things-url] ステップ 1/3: macOS環境を確認中...
[things-url] ステップ 2/3: Things 3から今日のタスクを読み取り中...
```

```bash
osascript <<'APPLESCRIPT'
tell application "Things3"
    set todoList to to dos of list "Today"
    set output to ""
    set openCount to 0
    set doneCount to 0
    repeat with t in todoList
        set taskName to name of t
        set taskStatus to status of t
        if taskStatus is not canceled then
            set taskTagNames to name of tags of t
            set tagStr to ""
            repeat with i from 1 to count of taskTagNames
                if i > 1 then set tagStr to tagStr & ", "
                set tagStr to tagStr & item i of taskTagNames
            end repeat
            set output to output & "- " & taskName & " [" & taskStatus & "]"
            if tagStr is not "" then
                set output to output & " (tags: " & tagStr & ")"
            end if
            set output to output & linefeed
            if taskStatus is open then
                set openCount to openCount + 1
            else
                set doneCount to doneCount + 1
            end if
        end if
    end repeat
    if output is "" then
        return "(今日のタスクはありません)"
    end if
    set totalCount to openCount + doneCount
    set output to output & linefeed & "合計: " & totalCount & "件（未完了: " & openCount & "件、完了: " & doneCount & "件）"
    return output
end tell
APPLESCRIPT
```

```text
[things-url] ステップ 3/3: 完了

Things 3「今日」のタスク一覧：
- [TASK-001]: データモデルの定義 [open] (tags: 進行中, SDD)
- [TASK-002]: APIエンドポイントの実装 [open] (tags: TODO, SDD)
- レビュー依頼への対応 [open] (tags: レビュー)
- ミーティング準備 [completed]

合計: 4件（未完了: 3件、完了: 1件）
```

### プロジェクト一覧とタスクを読み取る

```bash
osascript <<'APPLESCRIPT'
tell application "Things3"
    set projList to projects
    set output to ""
    repeat with p in projList
        if status of p is open then
            set projName to name of p
            set todoList to to dos of p
            set openCount to 0
            set doneCount to 0
            repeat with t in todoList
                if status of t is open then
                    set openCount to openCount + 1
                else if status of t is not canceled then
                    set doneCount to doneCount + 1
                end if
            end repeat
            set output to output & "## " & projName & " (未完了: " & openCount & ", 完了: " & doneCount & ")" & linefeed
            repeat with t in todoList
                set taskName to name of t
                set taskStatus to status of t
                if taskStatus is open then
                    set output to output & "  - [ ] " & taskName & linefeed
                else if taskStatus is not canceled then
                    set output to output & "  - [x] " & taskName & linefeed
                end if
            end repeat
            set output to output & linefeed
        end if
    end repeat
    if output is "" then
        return "(アクティブなプロジェクトはありません)"
    end if
    return output
end tell
APPLESCRIPT
```

### 特定タグのタスクを読み取る

「Claude Code」タグや「SDD」タグが付いたタスクのみを取得する場合。全ビルトインリストおよびプロジェクト内を横断検索します：

```bash
osascript <<'APPLESCRIPT'
tell application "Things3"
    set targetTag to "SDD"
    set listNames to {"Inbox", "Today", "Upcoming", "Anytime", "Someday"}
    set output to ""

    -- 各ビルトインリストを検索
    repeat with listName in listNames
        set currentList to contents of listName
        repeat with t in to dos of list currentList
            set tagNames to name of tags of t
            if tagNames contains targetTag then
                set taskName to name of t
                set taskStatus to status of t
                if taskStatus is open then
                    set output to output & "- [ ] [" & currentList & "] " & taskName & linefeed
                else if taskStatus is not canceled then
                    set output to output & "- [x] [" & currentList & "] " & taskName & linefeed
                end if
            end if
        end repeat
    end repeat

    -- 各プロジェクト内も検索
    repeat with p in projects
        if status of p is open then
            repeat with t in to dos of p
                set tagNames to name of tags of t
                if tagNames contains targetTag then
                    set taskName to name of t
                    set taskStatus to status of t
                    if taskStatus is open then
                        set output to output & "- [ ] [" & name of p & "] " & taskName & linefeed
                    else if taskStatus is not canceled then
                        set output to output & "- [x] [" & name of p & "] " & taskName & linefeed
                    end if
                end if
            end repeat
        end if
    end repeat

    if output is "" then
        return "(「" & targetTag & "」タグのタスクはありません)"
    end if
    return output
end tell
APPLESCRIPT
```

### Things → TodoWrite 同期フロー

```text
1. osascriptでThings 3から対象リスト/プロジェクトのタスクを取得
   ↓
2. 現在のTodoWriteの状態と比較
   ↓
3. 差分を検出してユーザーに提示
   ↓
4. ユーザー承認
   ↓
5. TodoWriteを更新
   ↓
6. 完了を報告
```

**差分提示の例**：

```text
[things-url] Things → TodoWrite 同期

以下の変更を検出しました：

変更あり:
  [TASK-001]: データモデルの定義
    Things: completed → TodoWrite: in_progress → 更新: completed
  [TASK-003]: 認証ミドルウェア
    Things: open (tag: 進行中) → TodoWrite: pending → 更新: in_progress

変更なし:
  [TASK-002]: APIエンドポイントの実装 (in_progress)

TodoWriteを更新してよろしいですか？
```

### Things → SDD タスク同期フロー

```text
1. osascriptでThings 3からSDDプロジェクトのタスクを取得
   ↓
2. `[TASK-XXX]` IDでdocs/sdd/tasks/の各タスクと照合
   ※ `[TASK-XXX]`形式のIDを持つタスクのみ同期対象とする
   ※ `[TASK-XXX]`パターンに一致しないファイルはスキップして保持する
   ↓
3. ステータスの差分を検出
   ↓
4. ユーザーに差分を提示
   ↓
5. ユーザー承認
   ↓
6. docs/sdd/tasks/のタスクファイルを更新
   ※ `[TASK-XXX]` IDで照合されたファイルのみ更新する
   ※ 非SDDタスク（外部作成のファイル）は変更・削除しない
   ↓
7. TodoWriteも連動更新
   ※ 非SDDタスクのtodo（contentが`[Phase-`または`[BLOCKED] [Phase-`で始まらないもの）はそのまま保持する
   ↓
8. 完了を報告
```

## 既存アイテムの更新

### auth-tokenの取得

既存のThingsアイテムを更新するには`auth-token`が必要です：

```text
auth-tokenはThings 3の設定画面から確認できます：
- Mac: Things → Settings → General → Enable Things URLs → Manage
- iOS: Settings → General → Things URLs

auth-tokenをお知らせください（このスキルでは保存しません）。
```

### 更新URLの生成

auth-tokenはコマンドライン引数に直書きせず、環境変数経由で安全に渡します：

```bash
# ステップ1: ユーザーからauth-tokenを受け取り環境変数に設定
read -s -p "Things auth-token: " THINGS_AUTH_TOKEN && echo

# ステップ2: 環境変数経由でpython3に渡し、直接openコマンドで実行
THINGS_AUTH_TOKEN="$THINGS_AUTH_TOKEN" python3 -c "
import urllib.parse, subprocess, os
auth_token = os.environ['THINGS_AUTH_TOKEN']
params = {
    'id': 'THINGS_ITEM_ID',
    'auth-token': auth_token,
    'when': 'today',
    'append-notes': '\n\n[更新: YYYY-MM-DD] ステータスがIN_PROGRESSに変更されました'
}
query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
url = f'things:///update?{query}'
subprocess.run(['open', url])
"
```

**セキュリティ上の注意**:
- auth-tokenはコマンドライン引数に直書きしないでください。シェル履歴（`~/.bash_history`）やプロセス一覧（`ps`）に残るおそれがあります
- `read -s`で標準入力から受け取り、環境変数経由でスクリプトに渡してください
- auth-tokenを含むURLは`print()`で標準出力に表示しないでください
- auth-tokenはファイルに保存しません。毎回ユーザーに確認します

## Areaの活用

プロジェクトをThingsのAreaに配置する場合：

```python
# add-projectでareaを指定
params = {
    'title': 'SDD Phase 1',
    'area': '開発プロジェクト',  # 既存のArea名
    # ...
}
```

```python
# add-jsonでarea指定
{
    "type": "project",
    "attributes": {
        "title": "SDD Phase 1",
        "area": "開発プロジェクト",
        # ...
    }
}
```

## 制約事項

### Things URLスキームの制限

1. **文字数制限**: パラメータの最大エンコード前文字数は4,000文字（notesは10,000文字）
2. **レート制限**: 10秒間に最大250アイテム
3. **macOS/iOS限定**: Things 3はAppleプラットフォーム専用
4. **更新にはauth-tokenが必要**: 既存アイテムの更新にはユーザーからのauth-token提供が必要
5. **IDの取得**: x-callback-urlを使わない限り、作成したアイテムのIDは自動取得できない

### スキルの制限

1. **読み取り機能はmacOSのみ**: AppleScript（`osascript`）はmacOS環境でのみ動作。Linux/Windows環境では書き込み（URL生成）のみ利用可能
2. **自動同期は非対応**: Things側での変更のClaude Codeへの反映はユーザーの明示的な指示が必要です。自動検知を行わない理由は、意図しないステータス変更の伝播を防ぎデータ整合性を保つためです。将来的にはThings MCPサーバーとの連携で自動同期の実現を検討しています（「今後の拡張」を参照）
3. **auth-tokenの永続化なし**: セキュリティのため、auth-tokenは保存しない
4. **`open`コマンドはmacOSのみ**: Linux/Windows環境ではURLの提示のみ

## ベストプラクティス

### 適切な粒度での送信

**良い例**: フェーズごとにプロジェクトを分けて送信
```text
プロジェクト: Phase 1 - 基盤構築（5タスク）
プロジェクト: Phase 2 - UI実装（3タスク）
```

**悪い例**: 全タスクを1つのプロジェクトに詰め込む
```text
プロジェクト: 全タスク（50タスク）  # 見通しが悪い
```

### タグの活用

一貫したタグ付けでフィルタリングを容易にします：

**推奨タグ**：
- `Claude Code`: Claude Codeから送信されたタスクであることを示す
- `SDD`: SDDプロセスのタスクであることを示す
- ステータスタグ: `TODO`、`進行中`、`レビュー`、`ブロック`

### notesへの文脈情報の記載

Things側で人間が判断できるよう、十分な文脈をnotesに含めます：

```text
notes に含めるべき情報：
- タスクの目的・背景
- 受入基準（チェックリストにも反映）
- 依存関係
- 関連ファイルパス
- 推定工数
```

### 定期的な同期

大きな進捗があったタイミングで再送信を提案します：
- フェーズの開始時
- 複数タスクのステータスが変わった時
- 新しいタスクが追加された時

## リソース

### リファレンス
- [Things URLスキームリファレンス](references/url_scheme_reference_ja.md) - コマンドとパラメータの詳細
- [Things AppleScriptリファレンス](references/applescript_reference_ja.md) - AppleScriptによるタスク読み取り

### 外部リソース
- Things URLスキーム公式ドキュメント: https://culturedcode.com/things/support/articles/2803573/
- ThingsJSONCoder（Swift）: https://github.com/culturedcode/ThingsJSONCoder

## 今後の拡張

このスキルは将来的に以下の機能追加を検討しています：

- Things MCPサーバーとの連携による自動同期（現在はAppleScriptベースの手動同期）
- Shortcuts連携によるiOS/iPadOSからの操作
- プロジェクトテンプレートの事前定義
- タスク完了時の自動通知URL生成
