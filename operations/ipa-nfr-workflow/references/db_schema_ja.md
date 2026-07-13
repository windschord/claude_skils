# DBスキーマ・データ形式リファレンス

`nfr_workflow.py` が管理するSQLite DBのスキーマと、各サブコマンドの入出力形式を定義する。

## テーブル構成

### project（プロジェクト情報・1行のみ）

| 列 | 型 | 説明 |
|----|-----|------|
| id | INTEGER | 常に1（単一プロジェクトDB） |
| system_name | TEXT | 対象システム名 |
| model_system | INTEGER | モデルシステム分類（1/2/3） |
| created_at / updated_at | TEXT | 作成・更新日時（JST） |

### nfr_items（項目マスタ・initでCSVからロード）

| 列 | 型 | 説明 |
|----|-----|------|
| item_id | TEXT PK | IPA 4階層ID（例: A.2.1.1） |
| category | TEXT | カテゴリ記号（A〜F） |
| category_name | TEXT | カテゴリ名（可用性 等） |
| item_name | TEXT | 項目名 |
| metric_hint | TEXT | メトリクス・記入例 |
| priority | TEXT | 優先度（高/中/低）— 後続作業への影響度による事前分類 |
| priority_reason | TEXT | 分類理由 |
| duplicate_of | TEXT | 重複項目（○マーク）の場合の代表項目ID（例: C.1.1.1 → A.1.1.1） |

### selections（対象システムの選択結果）

| 列 | 型 | 説明 |
|----|-----|------|
| item_id | TEXT PK | nfr_items への外部キー |
| level | TEXT | 選択レベル（L0-L5。レベル定義のない項目は空） |
| value | TEXT | 選択値・具体値（例: 99.9%、24時間365日） |
| note | TEXT | 備考・設計根拠。推奨値の仮設定時は「推奨値（要確認）」と明記 |
| customer_judgement | TEXT | 顧客判定（未確認/承認/要修正/要協議。CHECK制約で強制）— import-feedbackで更新 |
| updated_at | TEXT | 更新日時 |

### feedback（顧客指摘）

| 列 | 型 | 説明 |
|----|-----|------|
| id | INTEGER PK | 指摘番号（自動採番） |
| kind | TEXT | `item`（グレード項目への指摘）/ `out_of_grade`（グレード外要求） |
| item_id | TEXT | 対象項目ID（out_of_gradeは原則NULL。update-feedback --item-id で後から紐付け可能） |
| classification | TEXT | 顧客記入の分類（out_of_gradeのみ） |
| feedback | TEXT | 指摘・要求内容 |
| background | TEXT | 背景・理由（out_of_gradeのみ） |
| requested_priority | TEXT | 顧客の希望優先度（out_of_gradeのみ） |
| judgement | TEXT | 指摘時の顧客判定（itemのみ） |
| response | TEXT | 対応方針（ユーザー承認後に記録） |
| status | TEXT | `open` / `accepted` / `rejected` / `reflected` |
| imported_at | TEXT | 取り込み日時 |

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
