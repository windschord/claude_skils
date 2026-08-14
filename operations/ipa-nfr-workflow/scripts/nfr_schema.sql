-- =============================================================
-- IPA非機能要求グレード ワークフロー 制約スキーマ（正定義）
-- 永続データは人間可読なYAML（nfr.yaml）であり、本ファイルは
-- 全コマンド実行時に構築されるインメモリSQLite（検証エンジン）の
-- 定義。YAMLの全行がここで定義されたCHECK/FK/PK/NOT NULL制約の
-- 検証を受ける。スキーマ変更は本ファイルに対して行うこと
-- （Pythonコード内にDDLを重複定義しない）。
-- =============================================================

-- プロジェクト情報（1案件=1データファイル のため常に1行）
CREATE TABLE IF NOT EXISTS project (
    id           INTEGER PRIMARY KEY CHECK (id = 1),   -- 固定値1
    system_name  TEXT    NOT NULL,                     -- 対象システム名
    model_system INTEGER NOT NULL
                 CHECK (model_system IN (1, 2, 3)),    -- IPAモデルシステム分類
    master_file  TEXT,                                 -- カスタム項目マスタCSVのパス（既定マスタ使用時はNULL）
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
    note               TEXT,                           -- 備考・設計根拠（推奨値の仮設定時は「推奨値（要確認）」と明記）
    customer_judgement TEXT DEFAULT '未確認'
                       CHECK (customer_judgement IN
                              ('未確認', '承認', '要修正', '要協議')),  -- 顧客判定（import-feedbackで更新）
    updated_at         TEXT NOT NULL                   -- 更新日時（JST）
);

-- 顧客指摘（import-feedbackでExcelから取り込み。指摘本文の完全一致で重複排除）
CREATE TABLE IF NOT EXISTS feedback (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,  -- 指摘番号
    kind               TEXT NOT NULL
                       CHECK (kind IN ('item', 'out_of_grade')),
                       -- item: グレード項目への指摘 / out_of_grade: グレードでは表現できない要求
    item_id            TEXT REFERENCES nfr_items(item_id), -- 対象項目（out_of_gradeは原則NULL）
    classification     TEXT,                               -- 顧客記入の分類（out_of_gradeのみ）
    feedback           TEXT NOT NULL,                      -- 指摘・要求内容
    background         TEXT,                               -- 背景・理由（out_of_gradeのみ）
    requested_priority TEXT,                               -- 顧客の希望優先度（out_of_gradeのみ）
    judgement          TEXT,                               -- 指摘時の顧客判定（itemのみ）
    response           TEXT,                               -- 対応方針（ユーザー承認後にupdate-feedbackで記録）
    status             TEXT NOT NULL DEFAULT 'open'
                       CHECK (status IN ('open', 'accepted', 'rejected', 'reflected')),
                       -- open: 未対応 → accepted: 受入（設計書へ反映予定）→ reflected: 反映済み / rejected: 見送り
    imported_at        TEXT NOT NULL                       -- 取り込み日時（JST）
);
