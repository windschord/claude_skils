# Things URLスキーム リファレンス

Things 3のURLスキーム仕様のクイックリファレンスです。スキル実行時にパラメータを確認する際に参照してください。

## URLの基本形式

```text
things:///[コマンド]?[パラメータ1]=[値1]&[パラメータ2]=[値2]
```

すべてのパラメータ値はURLエンコード（パーセントエンコーディング）が必要です。

## コマンド一覧

### add - To-Doの作成

```text
things:///add?[パラメータ]
```

| パラメータ | 型 | 説明 |
|---|---|---|
| title | String | To-Doのタイトル |
| notes | String | メモ（最大10,000文字） |
| when | String | `today`, `tomorrow`, `evening`, `someday`, ISO8601日付, 自然言語（英語） |
| deadline | String | 期限（ISO8601日付） |
| tags | String | タグ（カンマ区切り） |
| checklist-items | String | チェックリスト項目（改行区切り）。Markdown形式で完了状態を指定可能 |
| list | String | 追加先プロジェクト・エリアのタイトル |
| list-id | String | 追加先プロジェクト・エリアのID（listより優先） |
| heading | String | プロジェクト内の見出しタイトル |
| heading-id | String | 見出しのID（headingより優先） |
| completed | Boolean | 完了状態にするか（デフォルト: false） |
| canceled | Boolean | キャンセル状態にするか（completedより優先） |
| creation-date | ISO8601 | 作成日（過去の日付のみ有効） |
| completion-date | ISO8601 | 完了日（completedがtrueかつ過去の日付のみ有効） |
| show-quick-entry | Boolean | Quick Entry画面を表示するか |
| reveal | Boolean | 作成後にTo-Doを表示するか |

### add-project - プロジェクトの作成

```text
things:///add-project?[パラメータ]
```

| パラメータ | 型 | 説明 |
|---|---|---|
| title | String | プロジェクトのタイトル |
| notes | String | メモ（最大10,000文字） |
| when | String | `today`, `tomorrow`, `evening`, `someday`, ISO8601日付 |
| deadline | String | 期限（ISO8601日付） |
| tags | String | タグ（カンマ区切り） |
| area | String | 追加先エリアのタイトル |
| area-id | String | 追加先エリアのID（areaより優先） |
| to-dos | String | To-Doタイトル（改行区切り） |
| completed | Boolean | 完了状態にするか |
| canceled | Boolean | キャンセル状態にするか |
| creation-date | ISO8601 | 作成日 |
| completion-date | ISO8601 | 完了日 |
| reveal | Boolean | 作成後にプロジェクトを表示するか |

### add-json - JSON一括インポート

```text
things:///add-json?data=[URLエンコードされたJSON]
```

**制限**: 10秒間に最大250アイテム

#### JSONの構造

トップレベルは配列で、各要素は`type`と`attributes`を持ちます。`data`パラメータには必ず配列`[...]`として渡してください。

**To-Do**（配列の要素として使用）:
```json
[
  {
    "type": "to-do",
    "attributes": {
    "title": "タスク名",
    "notes": "メモ",
    "when": "today",
    "deadline": "2026-03-20",
    "tags": ["タグ1", "タグ2"],
    "checklist-items": [
      {"title": "チェック項目1", "completed": false},
      {"title": "チェック項目2", "completed": true}
    ],
    "list": "プロジェクト名",
    "heading": "見出し名",
    "completed": false,
    "canceled": false,
    "creation-date": "2026-03-13"
  }
  }
]
```

**プロジェクト**:
```json
{
  "type": "project",
  "attributes": {
    "title": "プロジェクト名",
    "notes": "メモ",
    "when": "today",
    "deadline": "2026-03-31",
    "tags": ["タグ1"],
    "area": "エリア名",
    "items": [
      {
        "type": "heading",
        "attributes": {"title": "見出し1"}
      },
      {
        "type": "to-do",
        "attributes": {
          "title": "タスク1",
          "notes": "メモ"
        }
      }
    ]
  }
}
```

**見出し**（プロジェクト内のみ）:
```json
{
  "type": "heading",
  "attributes": {
    "title": "見出し名",
    "archived": false
  }
}
```

**チェックリスト項目**（To-Do内のみ）:
```json
{
  "title": "チェック項目",
  "completed": false,
  "canceled": false
}
```

#### JSONでの更新操作

既存アイテムの更新には`operation`と`id`を指定します。`add-json`経由の更新でも`auth-token`が必要です（URLパラメータとして`things:///add-json?data=[JSON]&auth-token=[TOKEN]`の形式で渡します）:

```json
{
  "type": "to-do",
  "operation": "update",
  "id": "THINGS_ITEM_ID",
  "attributes": {
    "when": "today",
    "append-notes": "\n更新メモ"
  }
}
```

**更新専用パラメータ**:
- `prepend-notes`: メモの先頭に追記
- `append-notes`: メモの末尾に追記
- `prepend-checklist-items`: チェックリストの先頭に追加
- `append-checklist-items`: チェックリストの末尾に追加
- `add-tags`: 既存タグに追加

### update - 既存To-Doの更新

```text
things:///update?id=[ID]&auth-token=[TOKEN]&[パラメータ]
```

`id`と`auth-token`は必須。その他のパラメータは`add`と同様（値なしで指定するとクリア）。

追加パラメータ:
- `prepend-notes`: メモの先頭に追記
- `append-notes`: メモの末尾に追記

### update-project - 既存プロジェクトの更新

```text
things:///update-project?id=[ID]&auth-token=[TOKEN]&[パラメータ]
```

`id`と`auth-token`は必須。その他のパラメータは`add-project`と同様。

追加パラメータ:
- `prepend-notes`: メモの先頭に追記
- `append-notes`: メモの末尾に追記

### show - アイテムの表示

```text
things:///show?id=[ID]
```

| パラメータ | 型 | 説明 |
|---|---|---|
| id | String | アイテムのIDまたはリスト名 |
| query | String | フィルタクエリ（`/show?id=today&filter-tags=タグ名`等） |
| filter-tags | String | タグでフィルタ（カンマ区切り） |

**ビルトインリストのID**:
- `inbox` - 受信箱
- `today` - 今日
- `upcoming` - 近日中
- `anytime` - いつでも
- `someday` - いつか
- `logbook` - ログブック
- `trash` - ゴミ箱
- `all-projects` - すべてのプロジェクト

### search - 検索

```text
things:///search?query=[検索語]
```

| パラメータ | 型 | 説明 |
|---|---|---|
| query | String | 検索キーワード |

## x-callback-url

作成したアイテムのIDを取得する場合、`x-success`と`x-cancel`パラメータにコールバックURLを指定します。パラメータ値はURLエンコードが必要です：

```text
things:///add?title=%E3%82%BF%E3%82%B9%E3%82%AF&x-success=myapp%3A%2F%2Fcallback&x-cancel=myapp%3A%2F%2Fcanceled
```

上記は以下のデコード済み値に対応します：
- `title` = `タスク`
- `x-success` = `myapp://callback`
- `x-cancel` = `myapp://canceled`

コールバックURLに`x-things-id`パラメータが付与されます。

## auth-tokenについて

既存アイテムの変更（update、update-project）にはauth-tokenが必要です。

**取得方法**:
- Mac: Things → Settings → General → Enable Things URLs → Manage
- iOS: Settings → General → Things URLs

## URLエンコードのユーティリティ

### python3を使ったエンコード

```bash
# 単純なパラメータのエンコード
python3 -c "
import urllib.parse
params = {'title': 'タスク名', 'when': 'today'}
print('things:///add?' + urllib.parse.urlencode(params, quote_via=urllib.parse.quote))
"
```

### JSONデータのエンコード

```bash
# add-json用のエンコード
python3 -c "
import urllib.parse, json
data = [{'type': 'to-do', 'attributes': {'title': 'タスク名'}}]
encoded = urllib.parse.quote(json.dumps(data, ensure_ascii=False))
print(f'things:///add-json?data={encoded}')
"
```

## whenパラメータの値

| 値 | 説明 |
|---|---|
| `today` | 今日 |
| `tomorrow` | 明日 |
| `evening` | 今晩 |
| `someday` | いつか |
| `2026-03-20` | 特定の日付（ISO8601） |
| `2026-03-20@17:00` | 日時指定（リマインダー） |
| `in 3 days` | 自然言語（英語のみ） |
| `next tuesday` | 自然言語（英語のみ） |

## 注意事項

- パラメータの最大文字数: 4,000文字（エンコード前）
- notesの最大文字数: 10,000文字（エンコード前）
- 10秒間に最大250アイテム（add-json）
- 日付のフォーマット: ISO8601（`yyyy-mm-dd`）
- 自然言語日付は英語のみ対応
- Things 3はmacOS/iOS/iPadOS専用
