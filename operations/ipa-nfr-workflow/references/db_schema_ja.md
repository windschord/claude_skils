# DBスキーマ・データ形式リファレンス

`nfr_workflow.py` が管理するSQLite DBのスキーマと、各サブコマンドの入出力形式を定義する。

## スキーマ定義（SQL）

**スキーマの正定義は `scripts/nfr_schema.sql`**。`init` 実行時にこのSQLファイルが読み込まれてDBが構築される。スキーマ変更はSQLファイルに対して行うこと（Pythonコード内にDDLを重複定義しない）。

```sql
-- プロジェクト情報（1案件=1DB のため常に1行）
CREATE TABLE IF NOT EXISTS project (
    id           INTEGER PRIMARY KEY CHECK (id = 1),   -- 固定値1
    system_name  TEXT    NOT NULL,                     -- 対象システム名
    model_system INTEGER NOT NULL
                 CHECK (model_system IN (1, 2, 3)),    -- IPAモデルシステム分類
    created_at   TEXT    NOT NULL,                     -- 作成日時（JST）
    updated_at   TEXT    NOT NULL                      -- 更新日時（JST）
);

-- 項目マスタ（initで assets/master/ipa_nfr_items_ja.csv からロード。実行時は読み取り専用）
CREATE TABLE IF NOT EXISTS nfr_items (
    item_id         TEXT PRIMARY KEY,                  -- IPA 4階層ID（例: A.2.1.1）
    category        TEXT NOT NULL,                     -- カテゴリ記号（A〜F）
    category_name   TEXT NOT NULL,                     -- カテゴリ名（可用性 等）
    item_name       TEXT NOT NULL,                     -- 項目名
    question        TEXT,                              -- ヒアリング質問文（何を聞くか）
    metric_hint     TEXT,                              -- メトリクス・記入例
    priority        TEXT NOT NULL
                    CHECK (priority IN ('高', '中', '低')),  -- 後続作業への影響度による優先度
    priority_reason TEXT,                              -- 優先度の分類理由
    duplicate_of    TEXT                               -- 重複項目（○マーク）の代表項目ID
);

-- 対象システムの選択結果（ヒアリング結果の登録先。registerでUPSERT）
CREATE TABLE IF NOT EXISTS selections (
    item_id            TEXT PRIMARY KEY
                       REFERENCES nfr_items(item_id),  -- 対象項目
    level              TEXT,                           -- 選択レベル（L0-L5。無い項目は空）
    value              TEXT,                           -- 選択値・具体値
    note               TEXT,                           -- 備考・設計根拠
    customer_judgement TEXT DEFAULT '未確認'
                       CHECK (customer_judgement IN
                              ('未確認', '承認', '要修正', '要協議')),  -- 顧客判定
    updated_at         TEXT NOT NULL                   -- 更新日時（JST）
);

-- 顧客指摘（import-feedbackでExcelから取り込み。指摘本文の完全一致で重複排除）
CREATE TABLE IF NOT EXISTS feedback (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,  -- 指摘番号
    kind               TEXT NOT NULL
                       CHECK (kind IN ('item', 'out_of_grade')),
    item_id            TEXT REFERENCES nfr_items(item_id), -- 対象項目（out_of_gradeは原則NULL）
    classification     TEXT,                               -- 顧客記入の分類（out_of_gradeのみ）
    feedback           TEXT NOT NULL,                      -- 指摘・要求内容
    background         TEXT,                               -- 背景・理由（out_of_gradeのみ）
    requested_priority TEXT,                               -- 顧客の希望優先度（out_of_gradeのみ）
    judgement          TEXT,                               -- 指摘時の顧客判定（itemのみ）
    response           TEXT,                               -- 対応方針（ユーザー承認後に記録）
    status             TEXT NOT NULL DEFAULT 'open'
                       CHECK (status IN ('open', 'accepted', 'rejected', 'reflected')),
    imported_at        TEXT NOT NULL                       -- 取り込み日時（JST）
);
```

## スキーマ設計の補足

- **project**: 1案件=1DBの設計のため `CHECK (id = 1)` で1行に制限している
- **nfr_items.question**: ヒアリングで「何を聞くか」の正定義。`hearing-sheet` サブコマンドがこの列から質問一覧を機械生成する
- **nfr_items.duplicate_of**: IPAの重複項目（○マーク）の代表項目ID（例: C.1.1.1 → A.1.1.1）。`check` が両者の値一致を検証する
- **selections.note**: 推奨値の仮設定時は「推奨値（要確認）」と明記するルール
- **selections.customer_judgement**: Excel取込（import-feedback）で更新。CHECK制約の許容値外はスクリプトが取込時に警告してスキップする
- **feedback.kind**: `item`（グレード項目への指摘）/ `out_of_grade`（グレードでは表現できない要求）。out_of_gradeは `update-feedback --item-id` で後から項目へ紐付け可能
- **feedback.status**: `open`（未対応）→ `accepted`（受入・設計書へ反映予定）→ `reflected`（反映済み）、または `rejected`（見送り。理由をresponseに記録）

## register用JSON形式

```json
{
  "selections": [
    {
      "item_id": "A.2.1.1",
      "level": "L3",
      "value": "99.9%",
      "note": "モデルシステム2の推奨値"
    },
    {
      "item_id": "C.1.2.5",
      "level": "",
      "value": "1時間毎の増分＋日次フル",
      "note": "RPO 1時間以内に対応"
    }
  ]
}
```

- `item_id`: 必須。マスタに存在しないIDはスキップされ、警告が表示される
- `level`: L0-L5のレベル値がある項目のみ。ない場合は空文字またはnull
- `value`: 具体値。未定の場合でも登録する場合は「[要確認]」等を記載
- `note`: 設計根拠・補足。省略可
- トップレベルが配列のJSON（`[{...}, ...]`）も受け付ける
- 同一item_idを再登録すると上書き（UPSERT）される。顧客判定（customer_judgement）は上書きされない

## statusのライフサイクル

```text
selections.customer_judgement:
  未確認 → （import-feedback）→ 承認 / 要修正 / 要協議

feedback.status:
  open（取り込み直後）
    → accepted（ユーザー承認済み・設計書へ反映予定）→ reflected（設計書へ反映済み）
    → rejected（見送り。responseに理由を記録）
```

## よく使うクエリ（sqlite3 CLI）

```bash
# 優先度「高」で顧客判定が承認以外の項目（未登録の項目も含める）
sqlite3 -header nfr.db "SELECT i.item_id, i.item_name, s.customer_judgement
  FROM nfr_items i LEFT JOIN selections s ON s.item_id = i.item_id
  WHERE i.priority = '高'
    AND (s.customer_judgement IS NULL OR s.customer_judgement != '承認')"

# 未対応の指摘件数
sqlite3 nfr.db "SELECT COUNT(*) FROM feedback WHERE status = 'open'"
```
