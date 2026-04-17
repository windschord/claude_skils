# Things 3 AppleScript リファレンス

Things 3のAppleScriptインターフェースを使ってタスクデータを読み取るためのリファレンスです。macOS環境でのみ利用可能です。

## 前提条件

- macOS上でThings 3がインストールされていること
- `osascript`コマンドが利用可能であること（macOS標準）

## 基本構文

```bash
osascript -e 'tell application "Things3" to [コマンド]'
```

複数行のスクリプト：

```bash
osascript <<'APPLESCRIPT'
tell application "Things3"
    -- スクリプト
end tell
APPLESCRIPT
```

## リスト一覧

Things 3には以下のビルトインリストがあります：

| リスト名 | 説明 |
|---|---|
| `Inbox` | 受信箱 |
| `Today` | 今日 |
| `Upcoming` | 近日中 |
| `Anytime` | いつでも |
| `Someday` | いつか |
| `Logbook` | ログブック |
| `Trash` | ゴミ箱 |

## タスクの読み取り

### 特定リストのタスク一覧を取得

```bash
# 今日のタスク名を取得
osascript -e 'tell application "Things3" to get name of to dos of list "Today"'

# 受信箱のタスク名を取得
osascript -e 'tell application "Things3" to get name of to dos of list "Inbox"'
```

### タスクの詳細プロパティを取得

```bash
# 今日のタスクの名前・メモ・ステータスを取得
osascript <<'APPLESCRIPT'
tell application "Things3"
    set todoList to to dos of list "Today"
    set output to ""
    repeat with t in todoList
        set taskName to name of t
        set taskNotes to notes of t
        set taskStatus to status of t
        set taskTags to name of tags of t
        set output to output & "---" & linefeed
        set output to output & "title: " & taskName & linefeed
        set output to output & "notes: " & taskNotes & linefeed
        set output to output & "status: " & taskStatus & linefeed
        set output to output & "tags: " & (taskTags as text) & linefeed
    end repeat
    return output
end tell
APPLESCRIPT
```

### タスクのプロパティ一覧

| プロパティ | 型 | 説明 |
|---|---|---|
| `name` | String | タスク名 |
| `id` | String | Things内部ID |
| `notes` | String | メモ |
| `status` | Enum | `open`, `completed`, `canceled` |
| `tag names` | String | タグ名の文字列（カンマ区切り）。`tag names of t` で取得 |
| `tags` | List | タグオブジェクトのリスト。`name of tags of t` でタグ名のリスト（List型）を取得。`as text` でカンマ区切り文字列に変換可能 |
| `due date` | Date | 期限 |
| `activation date` | Date | 開始日（whenに対応） |
| `modification date` | Date | 最終更新日 |
| `creation date` | Date | 作成日 |
| `completion date` | Date | 完了日 |
| `project` | Project | 所属プロジェクト |

## プロジェクトの読み取り

### プロジェクト一覧を取得

```bash
# すべてのプロジェクト名を取得
osascript -e 'tell application "Things3" to get name of projects'
```

### プロジェクト内のタスクを取得

```bash
# 特定プロジェクトのタスク名を取得
osascript -e 'tell application "Things3" to get name of to dos of project "プロジェクト名"'
```

### プロジェクトの詳細を取得

```bash
osascript <<'APPLESCRIPT'
tell application "Things3"
    set proj to project "プロジェクト名"
    set projName to name of proj
    set projNotes to notes of proj
    set projStatus to status of proj
    set todoList to to dos of proj

    set output to "project: " & projName & linefeed
    set output to output & "notes: " & projNotes & linefeed
    set output to output & "status: " & projStatus & linefeed
    set output to output & "tasks:" & linefeed

    repeat with t in todoList
        set taskName to name of t
        set taskStatus to status of t
        set output to output & "  - " & taskName & " [" & taskStatus & "]" & linefeed
    end repeat

    return output
end tell
APPLESCRIPT
```

### プロジェクトのプロパティ一覧

| プロパティ | 型 | 説明 |
|---|---|---|
| `name` | String | プロジェクト名 |
| `id` | String | Things内部ID |
| `notes` | String | メモ |
| `status` | Enum | `open`, `completed`, `canceled` |
| `tag names` | String | タグ（カンマ区切り） |
| `due date` | Date | 期限 |
| `area` | Area | 所属エリア |
| `to dos` | List | 配下のTo-Do一覧 |

## エリアの読み取り

```bash
# すべてのエリア名を取得
osascript -e 'tell application "Things3" to get name of areas'

# エリア内のプロジェクト名を取得
osascript -e 'tell application "Things3" to get name of projects of area "エリア名"'

# エリア内のTo-Do名を取得
osascript -e 'tell application "Things3" to get name of to dos of area "エリア名"'
```

## タグの読み取り

```bash
# すべてのタグ名を取得
osascript -e 'tell application "Things3" to get name of tags'

# 特定タグが付いたタスクを全リストから取得
osascript <<'APPLESCRIPT'
tell application "Things3"
    set targetTag to "Claude Code"
    set listNames to {"Inbox", "Today", "Upcoming", "Anytime", "Someday"}
    set output to ""

    -- 各ビルトインリストを検索
    repeat with listName in listNames
        set currentList to contents of listName
        set todoList to to dos of list currentList
        repeat with t in todoList
            if (name of tags of t) contains targetTag then
                set output to output & "[" & currentList & "] " & name of t & linefeed
            end if
        end repeat
    end repeat

    -- 各プロジェクト内も検索
    repeat with p in projects
        if status of p is open then
            repeat with t in to dos of p
                if (name of tags of t) contains targetTag then
                    set output to output & "[" & name of p & "] " & name of t & linefeed
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

## 構造化されたJSON出力

Claude Codeでの処理に適したJSON形式で出力するパターンです。

### JSONエスケープ用ヘルパー関数

以下のJSON出力スクリプトでは、共通のヘルパー関数（`escapeJSON`、`replaceText`）を使用します。各スクリプトの末尾（`end tell`の後）にこのヘルパー関数を追加してください：

```applescript
on escapeJSON(theText)
    set theText to my replaceText(theText, "\\", "\\\\")
    set theText to my replaceText(theText, "\"", "\\\"")
    set theText to my replaceText(theText, return, "\\n")
    set theText to my replaceText(theText, linefeed, "\\n")
    set theText to my replaceText(theText, tab, "\\t")
    return theText
end escapeJSON

on replaceText(theText, searchString, replacementString)
    set AppleScript's text item delimiters to searchString
    set theItems to text items of theText
    set AppleScript's text item delimiters to replacementString
    set theText to theItems as text
    set AppleScript's text item delimiters to ""
    return theText
end replaceText
```

### 今日のタスクをJSON形式で取得

```bash
osascript <<'APPLESCRIPT'
tell application "Things3"
    set todoList to to dos of list "Today"
    set jsonItems to "["
    set isFirst to true

    repeat with t in todoList
        if not isFirst then
            set jsonItems to jsonItems & ","
        end if
        set isFirst to false

        set taskName to name of t
        set taskNotes to notes of t
        set taskStatus to status of t as text
        set taskID to id of t

        -- エスケープ処理
        set taskName to my escapeJSON(taskName)
        set taskNotes to my escapeJSON(taskNotes)

        set jsonItems to jsonItems & "{\"id\":\"" & taskID & "\",\"title\":\"" & taskName & "\",\"notes\":\"" & taskNotes & "\",\"status\":\"" & taskStatus & "\"}"
    end repeat

    set jsonItems to jsonItems & "]"
    return jsonItems
end tell

-- 上記「JSONエスケープ用ヘルパー関数」をここに追加
APPLESCRIPT
```

### プロジェクトとタスクをJSON形式で取得

```bash
osascript <<'APPLESCRIPT'
tell application "Things3"
    set projList to projects
    set jsonProjects to "["
    set isFirstProj to true

    repeat with p in projList
        if status of p is open then
            if not isFirstProj then
                set jsonProjects to jsonProjects & ","
            end if
            set isFirstProj to false

            set projName to my escapeJSON(name of p)
            set projID to id of p
            set projStatus to status of p as text

            set todoList to to dos of p
            set jsonTodos to "["
            set isFirstTodo to true

            repeat with t in todoList
                if not isFirstTodo then
                    set jsonTodos to jsonTodos & ","
                end if
                set isFirstTodo to false

                set taskName to my escapeJSON(name of t)
                set taskID to id of t
                set taskStatus to status of t as text

                set jsonTodos to jsonTodos & "{\"id\":\"" & taskID & "\",\"title\":\"" & taskName & "\",\"status\":\"" & taskStatus & "\"}"
            end repeat

            set jsonTodos to jsonTodos & "]"
            set jsonProjects to jsonProjects & "{\"id\":\"" & projID & "\",\"title\":\"" & projName & "\",\"status\":\"" & projStatus & "\",\"tasks\":" & jsonTodos & "}"
        end if
    end repeat

    set jsonProjects to jsonProjects & "]"
    return jsonProjects
end tell

-- 上記「JSONエスケープ用ヘルパー関数」をここに追加
APPLESCRIPT
```

## タスク数のカウント

```bash
# 今日のタスク数
osascript -e 'tell application "Things3" to count of to dos of list "Today"'

# 受信箱のタスク数
osascript -e 'tell application "Things3" to count of to dos of list "Inbox"'

# プロジェクト内のタスク数
osascript -e 'tell application "Things3" to count of to dos of project "プロジェクト名"'
```

## プラットフォーム確認

AppleScript読み取りを実行する前に、macOS環境であることを確認してください：

```bash
# macOSかどうかの確認
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS - AppleScript利用可能
    osascript -e 'tell application "Things3" to get name of to dos of list "Today"'
else
    echo "AppleScriptはmacOS環境でのみ利用可能です"
fi
```

## 注意事項

- AppleScriptによる読み取りはThings 3が起動していなくても動作しますが、初回アクセス時にThings 3が起動します
- 大量のタスクを取得する場合、パフォーマンスに注意してください（数百件以上は分割取得を推奨）
- `osascript`の出力はUTF-8テキストです。日本語も正常に扱えます
- 初回実行時、macOSの「システム設定 → プライバシーとセキュリティ → オートメーション」でターミナル（またはClaude Code）からThings 3へのアクセスを許可する必要があります
