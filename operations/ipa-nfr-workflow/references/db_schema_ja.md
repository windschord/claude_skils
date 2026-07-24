# データ形式・制約スキーマリファレンス

`nfr_workflow.py` が管理するデータの保存形式（YAML）、制約スキーマ（SQL DDL）、各サブコマンドの入出力形式を定義する。

## データ保持の仕組み（YAML単一正＋インメモリSQLite検証）

- **永続化される正データは人間可読なYAMLファイル（`nfr.yaml`）ただ1つ**。Git diffで変更をレビューできる
- **SQLiteはディスクに保存されない**。`init` を除く全サブコマンドが起動時に「YAMLロード → `:memory:` SQLiteを制約スキーマから再構築 → 全行INSERT」を行い、この時点でCHECK/FK/PK/NOT NULLの全制約が検証される。YAMLの変更（手編集含む）は次のコマンド実行時に必ず最新内容で検証される（`init` は新規作成のためロードしないが、保存時のラウンドトリップ検証で同じロード処理による検証を受ける）
- **保存はラウンドトリップ検証つき**: 「検証済みインメモリDBの直列化 → 再ロードによる再検証 → 内容一致確認 → 原子的rename」の順で行われ、制約違反の内容や壊れたファイルがYAMLに残ることはない
- 手編集後の明示的な確認には `validate` サブコマンドを使う

## 保存形式（nfr.yaml）

```yaml
format_version: 1          # 必須。1のみ許容（欠落・他の値はロード時に拒否される）
project:
  system_name: B2B受発注管理SaaS
  model_system: 2          # 1〜3のみ許容
  master_file: null        # カスタム項目マスタ使用時のみパス
  created_at: '2026-07-24 11:41:00'
  updated_at: '2026-07-24 11:41:00'
selections:                # 項目IDをキーとするマッピング（重複キーはロード時にエラー）
  A.2.1.1:
    item_name: 稼働率       # 参考表示（保存のたびにマスタから自動付記。編集しても無視される）
    priority: 高            # 同上
    level: L3
    value: 99.9%
    note: 推奨値で合意
    customer_judgement: 未確認   # 未確認/承認/要修正/要協議のみ許容
    updated_at: '2026-07-24 11:41:00'
feedback:                  # 指摘のリスト
- id: 1
  kind: item               # item / out_of_grade のみ許容
  item_id: A.2.1.1         # マスタに存在するIDのみ許容（FK相当）
  item_name: 稼働率         # 参考表示
  classification: null
  feedback: 稼働率は99.95%にしてほしい
  background: null
  requested_priority: null
  judgement: 要修正
  response: null
  status: open             # open/accepted/rejected/reflected のみ許容
  imported_at: '2026-07-24 11:45:00'
```

## 制約スキーマ定義（SQL）

**制約の正定義は `scripts/nfr_schema.sql`**。全コマンドがインメモリSQLite構築時にこのSQLファイルを読み込み、YAMLの全行が以下の制約検証を受ける。スキーマ変更はSQLファイルに対して行うこと（Pythonコード内にDDLを重複定義しない）。

```sql
-- プロジェクト情報（1案件=1データファイル のため常に1行）
CREATE TABLE IF NOT EXISTS project (
    id           INTEGER PRIMARY KEY CHECK (id = 1),   -- 固定値1
    system_name  TEXT    NOT NULL,                     -- 対象システム名
    model_system INTEGER NOT NULL
                 CHECK (model_system IN (1, 2, 3)),    -- IPAモデルシステム分類
    master_file  TEXT,                                 -- カスタム項目マスタCSVのパス（既定時はNULL）
    created_at   TEXT    NOT NULL,                     -- 作成日時（JST）
    updated_at   TEXT    NOT NULL                      -- 更新日時（JST）
);

-- 項目マスタ（全コマンドが assets/master/ipa_nfr_items_ja.csv から毎回ロード。YAMLには保存されない）
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

- **project**: 1案件=1データファイルの設計のため `CHECK (id = 1)` で1行に制限している
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

## データの確認方法

正データはYAMLなのでエディタ・Git diffでそのまま確認できる。集計・横断確認にはサブコマンドを使う:

```bash
# 登録状況・指摘対応状況のサマリー
python3 <スキルディレクトリ>/scripts/nfr_workflow.py status --data nfr.yaml

# 全項目の現在値一覧（未登録含む）
python3 <スキルディレクトリ>/scripts/nfr_workflow.py hearing-sheet --data nfr.yaml --all

# 未対応の指摘一覧（JSON）
python3 <スキルディレクトリ>/scripts/nfr_workflow.py list-feedback --data nfr.yaml --status open

# 手編集後の制約検証
python3 <スキルディレクトリ>/scripts/nfr_workflow.py validate --data nfr.yaml
```
