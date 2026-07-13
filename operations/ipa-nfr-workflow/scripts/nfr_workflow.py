#!/usr/bin/env python3
"""IPA非機能要求グレード ワークフロー管理CLI。

ヒアリング結果のDB登録、顧客レビュー用Excelの出力、顧客指摘の取り込み、
運用設計書（Word）の生成を行う。

依存ライブラリ: openpyxl（Excel）、python-docx（Word）
    pip install openpyxl python-docx

サブコマンド:
    init             DBを初期化し、項目マスタ（優先度分類済み）をロードする
    register         ヒアリング結果（選択レベル・値）をJSONから登録する
    status           登録状況・指摘対応状況のサマリーを表示する
    export-excel     顧客レビュー用Excel（優先度色分け・記入欄付き）を出力する
    import-feedback  顧客が記入したExcelから指摘を取り込む
    list-feedback    取り込んだ指摘を一覧表示する（JSON）
    update-feedback  指摘への対応方針・状態を更新する
    dump             DB内容をJSON/Markdownで出力する（運用設計書生成の入力）
    export-word      Markdownの運用設計書をWord（.docx）に変換し付録を追加する
"""

import argparse
import contextlib
import csv
import json
import re
import signal
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
PRIORITY_ORDER = {"高": 0, "中": 1, "低": 2}
JUDGEMENTS = ["未確認", "承認", "要修正", "要協議"]
DEFAULT_MASTER = Path(__file__).resolve().parent.parent / "assets" / "master" / "ipa_nfr_items_ja.csv"

SHEET_GRADE = "非機能要求グレード"
SHEET_EXTRA = "グレード外要求"
SHEET_GUIDE = "記入ガイド"


def now() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")


def die(msg: str) -> None:
    print(f"エラー: {msg}", file=sys.stderr)
    sys.exit(1)


def connect(db_path: str, must_exist: bool = True) -> sqlite3.Connection:
    if must_exist and not Path(db_path).exists():
        die(f"DBファイルが見つかりません: {db_path}（先に init を実行してください）")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS project (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    system_name TEXT NOT NULL,
    model_system INTEGER NOT NULL CHECK (model_system IN (1, 2, 3)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS nfr_items (
    item_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    category_name TEXT NOT NULL,
    item_name TEXT NOT NULL,
    metric_hint TEXT,
    priority TEXT NOT NULL CHECK (priority IN ('高', '中', '低')),
    priority_reason TEXT,
    duplicate_of TEXT
);
CREATE TABLE IF NOT EXISTS selections (
    item_id TEXT PRIMARY KEY REFERENCES nfr_items(item_id),
    level TEXT,
    value TEXT,
    note TEXT,
    customer_judgement TEXT DEFAULT '未確認',
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL CHECK (kind IN ('item', 'out_of_grade')),
    item_id TEXT REFERENCES nfr_items(item_id),
    classification TEXT,
    feedback TEXT NOT NULL,
    background TEXT,
    requested_priority TEXT,
    judgement TEXT,
    response TEXT,
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'accepted', 'rejected', 'reflected')),
    imported_at TEXT NOT NULL
);
"""


# ---------------------------------------------------------------- init
def cmd_init(args) -> None:
    master = Path(args.master) if args.master else DEFAULT_MASTER
    if not master.exists():
        die(f"項目マスタが見つかりません: {master}")
    if Path(args.db).exists() and not args.force:
        die(f"DBが既に存在します: {args.db}（上書きする場合は --force を指定）")

    conn = connect(args.db, must_exist=False)
    conn.executescript(SCHEMA)
    conn.execute("DELETE FROM project")
    conn.execute(
        "INSERT INTO project (id, system_name, model_system, created_at, updated_at)"
        " VALUES (1, ?, ?, ?, ?)",
        (args.project, args.model_system, now(), now()),
    )
    with master.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    conn.execute("DELETE FROM nfr_items")
    for r in rows:
        conn.execute(
            "INSERT INTO nfr_items (item_id, category, category_name, item_name,"
            " metric_hint, priority, priority_reason, duplicate_of)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                r["item_id"], r["category"], r["category_name"], r["item_name"],
                r.get("metric_hint", ""), r["priority"], r.get("priority_reason", ""),
                r.get("duplicate_of") or None,
            ),
        )
    conn.commit()
    counts = conn.execute(
        "SELECT priority, COUNT(*) AS n FROM nfr_items GROUP BY priority"
    ).fetchall()
    summary = {r["priority"]: r["n"] for r in counts}
    print(f"DB初期化完了: {args.db}")
    print(f"  システム名: {args.project} / モデルシステム{args.model_system}")
    total = sum(summary.values())
    print(
        f"  項目マスタ: {total}項目"
        f"（高: {summary.get('高', 0)} / 中: {summary.get('中', 0)} / 低: {summary.get('低', 0)}）"
    )
    conn.close()


# ---------------------------------------------------------------- register
def cmd_register(args) -> None:
    conn = connect(args.db)
    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    selections = data.get("selections", data if isinstance(data, list) else [])
    if not selections:
        die("selections が空です")
    known = {r["item_id"] for r in conn.execute("SELECT item_id FROM nfr_items")}
    registered, skipped = 0, []
    for s in selections:
        item_id = s.get("item_id")
        if item_id not in known:
            skipped.append(item_id)
            continue
        conn.execute(
            "INSERT INTO selections (item_id, level, value, note, updated_at)"
            " VALUES (?, ?, ?, ?, ?)"
            " ON CONFLICT(item_id) DO UPDATE SET"
            " level = excluded.level, value = excluded.value, note = excluded.note,"
            " updated_at = excluded.updated_at",
            (item_id, s.get("level"), s.get("value"), s.get("note"), now()),
        )
        registered += 1
    conn.execute("UPDATE project SET updated_at = ?", (now(),))
    conn.commit()
    print(f"登録完了: {registered}項目")
    if skipped:
        print(f"  マスタに存在しないためスキップ: {', '.join(map(str, skipped))}")
    _print_missing_high(conn)
    conn.close()


def _print_missing_high(conn) -> None:
    missing = conn.execute(
        "SELECT i.item_id, i.item_name FROM nfr_items i"
        " LEFT JOIN selections s ON s.item_id = i.item_id"
        " WHERE i.priority = '高' AND s.item_id IS NULL ORDER BY i.item_id"
    ).fetchall()
    if missing:
        print(f"  未登録の優先度「高」項目: {len(missing)}件")
        for r in missing:
            print(f"    - {r['item_id']} {r['item_name']}")


# ---------------------------------------------------------------- status
def cmd_status(args) -> None:
    conn = connect(args.db)
    p = conn.execute("SELECT * FROM project").fetchone()
    if not p:
        die("プロジェクト情報がありません")
    print(f"システム名: {p['system_name']} / モデルシステム{p['model_system']}")
    rows = conn.execute(
        "SELECT i.priority, COUNT(*) AS total, COUNT(s.item_id) AS registered"
        " FROM nfr_items i LEFT JOIN selections s ON s.item_id = i.item_id"
        " GROUP BY i.priority"
    ).fetchall()
    print("登録状況（優先度別）:")
    for pr in ("高", "中", "低"):
        r = next((x for x in rows if x["priority"] == pr), None)
        if r:
            print(f"  {pr}: {r['registered']}/{r['total']} 項目")
    fb = conn.execute(
        "SELECT status, COUNT(*) AS n FROM feedback GROUP BY status"
    ).fetchall()
    if fb:
        print("顧客指摘の状況:")
        for r in fb:
            print(f"  {r['status']}: {r['n']}件")
    else:
        print("顧客指摘: 未取り込み")
    _print_missing_high(conn)
    conn.close()


# ---------------------------------------------------------------- export-excel
def _select_rows(conn):
    return conn.execute(
        "SELECT i.item_id, i.category, i.category_name, i.item_name, i.metric_hint,"
        " i.priority, i.duplicate_of, s.level, s.value, s.note, s.customer_judgement"
        " FROM nfr_items i LEFT JOIN selections s ON s.item_id = i.item_id"
        " ORDER BY CASE i.priority WHEN '高' THEN 0 WHEN '中' THEN 1 ELSE 2 END,"
        " i.item_id"
    ).fetchall()


def cmd_export_excel(args) -> None:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
        from openpyxl.utils import get_column_letter
        from openpyxl.worksheet.datavalidation import DataValidation
    except ImportError:
        die("openpyxl がインストールされていません: pip install openpyxl")

    conn = connect(args.db)
    p = conn.execute("SELECT * FROM project").fetchone()
    rows = _select_rows(conn)

    priority_fill = {
        "高": PatternFill("solid", fgColor="FDE9E9"),
        "中": PatternFill("solid", fgColor="FFF6DD"),
        "低": PatternFill("solid", fgColor="F2F2F2"),
    }
    priority_font = {
        "高": Font(color="B03030", bold=True),
        "中": Font(color="8A6D1A", bold=True),
        "低": Font(color="666666"),
    }
    header_fill = PatternFill("solid", fgColor="2F5496")
    header_font = Font(color="FFFFFF", bold=True)
    customer_fill = PatternFill("solid", fgColor="E7F0E7")
    thin = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    wrap = Alignment(wrap_text=True, vertical="top")

    wb = Workbook()

    # --- シート1: 非機能要求グレード ---
    ws = wb.active
    ws.title = SHEET_GRADE
    title = f"非機能要件確認シート - {p['system_name']}（モデルシステム{p['model_system']}）"
    ws.cell(row=1, column=1, value=title).font = Font(bold=True, size=14)
    ws.cell(
        row=2, column=1,
        value="優先度「高」は後続の設計作業への影響が大きい項目です。高→中→低の順にご確認ください。"
        "「顧客判定」「顧客コメント」列（緑色）にご記入ください。",
    ).font = Font(color="808080")

    headers = [
        ("No", 5), ("優先度", 8), ("カテゴリ", 16), ("項目ID", 10), ("項目名", 30),
        ("メトリクス（記入例）", 24), ("選択レベル", 10), ("選択値・具体値", 24),
        ("備考（設計根拠）", 30), ("顧客判定", 12), ("顧客コメント（指摘・要望）", 40),
    ]
    header_row = 4
    for col, (name, width) in enumerate(headers, start=1):
        c = ws.cell(row=header_row, column=col, value=name)
        c.fill = header_fill
        c.font = header_font
        c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(col)].width = width

    dv = DataValidation(
        type="list", formula1='"' + ",".join(JUDGEMENTS) + '"', allow_blank=True,
        showErrorMessage=True, errorTitle="入力エラー",
        error="未確認・承認・要修正・要協議 のいずれかを選択してください",
    )
    ws.add_data_validation(dv)

    for i, r in enumerate(rows, start=1):
        row = header_row + i
        dup = f"（{r['duplicate_of']}と重複項目）" if r["duplicate_of"] else ""
        values = [
            i, r["priority"], f"{r['category']}: {r['category_name']}", r["item_id"],
            r["item_name"] + dup, r["metric_hint"], r["level"] or "",
            r["value"] or "", r["note"] or "",
            r["customer_judgement"] or "未確認", "",
        ]
        for col, v in enumerate(values, start=1):
            c = ws.cell(row=row, column=col, value=v)
            c.border = border
            c.alignment = wrap
            if col in (10, 11):
                c.fill = customer_fill
        pc = ws.cell(row=row, column=2)
        pc.fill = priority_fill[r["priority"]]
        pc.font = priority_font[r["priority"]]
        pc.alignment = Alignment(horizontal="center", vertical="top")
        dv.add(ws.cell(row=row, column=10))

    ws.freeze_panes = ws.cell(row=header_row + 1, column=6)
    ws.auto_filter.ref = f"A{header_row}:K{header_row + len(rows)}"

    # --- シート2: グレード外要求 ---
    ws2 = wb.create_sheet(SHEET_EXTRA)
    ws2.cell(
        row=1, column=1,
        value="非機能要求グレードの項目では表現できないご要望・ご指摘は本シートにご記入ください。",
    ).font = Font(bold=True)
    extra_headers = [
        ("No", 5), ("分類", 16), ("要求・指摘内容", 50), ("背景・理由", 40),
        ("希望優先度", 12), ("備考", 24),
    ]
    for col, (name, width) in enumerate(extra_headers, start=1):
        c = ws2.cell(row=3, column=col, value=name)
        c.fill = header_fill
        c.font = header_font
        c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws2.column_dimensions[get_column_letter(col)].width = width
    dv2 = DataValidation(type="list", formula1='"高,中,低"', allow_blank=True)
    ws2.add_data_validation(dv2)
    for i in range(1, 21):
        row = 3 + i
        ws2.cell(row=row, column=1, value=i).border = border
        for col in range(2, 7):
            c = ws2.cell(row=row, column=col)
            c.border = border
            c.alignment = wrap
            c.fill = customer_fill
        dv2.add(ws2.cell(row=row, column=5))

    # --- シート3: 記入ガイド ---
    ws3 = wb.create_sheet(SHEET_GUIDE)
    guide = [
        ("本シートの目的", ""),
        ("", "IPA「非機能要求グレード2018」に基づき、対象システムの非機能要件の選択結果をご確認いただくためのシートです。"),
        ("", ""),
        ("優先度の意味（後続の設計・構築作業への影響度）", ""),
        ("高", "インフラ構成・アーキテクチャ・運用体制の根幹を決める項目。変更の後戻りコストが大きいため、最優先でご確認ください。"),
        ("中", "運用プロセス・手順の設計に影響する項目。設計工程の中で調整可能ですが、早期の確定が望まれます。"),
        ("低", "付加的・詳細レベルの項目。後工程での調整が比較的容易です。"),
        ("", ""),
        ("顧客判定の記入方法", ""),
        ("承認", "選択レベル・値のままで問題ない場合"),
        ("要修正", "値の変更が必要な場合（顧客コメント欄に修正内容をご記入ください）"),
        ("要協議", "打ち合わせでの協議を希望される場合（顧客コメント欄に論点をご記入ください）"),
        ("未確認", "まだ確認されていない項目（初期値）"),
        ("", ""),
        ("グレード外要求シートについて", ""),
        ("", "非機能要求グレードの項目体系では表現できないご要望（例: 特定の運用レポート、独自の承認フロー、組織固有の制約など）は「グレード外要求」シートに自由記述でご記入ください。運用設計書に反映します。"),
    ]
    ws3.column_dimensions["A"].width = 14
    ws3.column_dimensions["B"].width = 100
    for i, (a, b) in enumerate(guide, start=1):
        ca = ws3.cell(row=i, column=1, value=a)
        cb = ws3.cell(row=i, column=2, value=b)
        cb.alignment = wrap
        if a and not b:
            ca.font = Font(bold=True, size=12)
        elif a in priority_fill:
            ca.fill = priority_fill[a]
            ca.font = priority_font[a]
            ca.alignment = Alignment(horizontal="center")

    wb.save(args.output)
    high = sum(1 for r in rows if r["priority"] == "高")
    print(f"Excel出力完了: {args.output}")
    print(f"  {SHEET_GRADE}: {len(rows)}項目（うち優先度「高」{high}項目）")
    print(f"  {SHEET_EXTRA}: 記入欄20行 / {SHEET_GUIDE}: あり")
    conn.close()


# ---------------------------------------------------------------- import-feedback
def _header_map(ws, header_row: int) -> dict:
    return {
        (c.value or "").strip(): c.column
        for c in ws[header_row] if isinstance(c.value, str)
    }


def cmd_import_feedback(args) -> None:
    try:
        from openpyxl import load_workbook
    except ImportError:
        die("openpyxl がインストールされていません: pip install openpyxl")
    if not Path(args.input).exists():
        die(f"Excelファイルが見つかりません: {args.input}")

    conn = connect(args.db)
    wb = load_workbook(args.input, data_only=True)
    imported, updated_judgements, skipped_dup = [], 0, 0

    # --- シート1: 項目別の判定・コメント ---
    if SHEET_GRADE not in wb.sheetnames:
        die(f"シート「{SHEET_GRADE}」が見つかりません")
    ws = wb[SHEET_GRADE]
    hmap = _header_map(ws, 4)
    for need in ("項目ID", "顧客判定", "顧客コメント（指摘・要望）"):
        if need not in hmap:
            die(f"シート「{SHEET_GRADE}」に列「{need}」が見つかりません")
    known = {r["item_id"] for r in conn.execute("SELECT item_id FROM nfr_items")}
    for row in ws.iter_rows(min_row=5):
        item_id = row[hmap["項目ID"] - 1].value
        if not item_id or str(item_id).strip() not in known:
            continue
        item_id = str(item_id).strip()
        judgement = str(row[hmap["顧客判定"] - 1].value or "").strip()
        comment = str(row[hmap["顧客コメント（指摘・要望）"] - 1].value or "").strip()
        if judgement and judgement != "未確認":
            conn.execute(
                "UPDATE selections SET customer_judgement = ?, updated_at = ?"
                " WHERE item_id = ?",
                (judgement, now(), item_id),
            )
            updated_judgements += 1
        if comment:
            exists = conn.execute(
                "SELECT 1 FROM feedback WHERE kind = 'item' AND item_id = ?"
                " AND feedback = ?",
                (item_id, comment),
            ).fetchone()
            if exists:
                skipped_dup += 1
                continue
            cur = conn.execute(
                "INSERT INTO feedback (kind, item_id, feedback, judgement, imported_at)"
                " VALUES ('item', ?, ?, ?, ?)",
                (item_id, comment, judgement or None, now()),
            )
            imported.append((cur.lastrowid, "item", item_id, comment))

    # --- シート2: グレード外要求 ---
    if SHEET_EXTRA in wb.sheetnames:
        ws2 = wb[SHEET_EXTRA]
        hmap2 = _header_map(ws2, 3)
        col_content = hmap2.get("要求・指摘内容")
        if col_content:
            for row in ws2.iter_rows(min_row=4):
                content = str(row[col_content - 1].value or "").strip()
                if not content:
                    continue
                classification = str(
                    row[hmap2.get("分類", 2) - 1].value or ""
                ).strip() or None
                background = str(
                    row[hmap2.get("背景・理由", 4) - 1].value or ""
                ).strip() or None
                req_priority = str(
                    row[hmap2.get("希望優先度", 5) - 1].value or ""
                ).strip() or None
                exists = conn.execute(
                    "SELECT 1 FROM feedback WHERE kind = 'out_of_grade' AND feedback = ?",
                    (content,),
                ).fetchone()
                if exists:
                    skipped_dup += 1
                    continue
                cur = conn.execute(
                    "INSERT INTO feedback (kind, classification, feedback, background,"
                    " requested_priority, imported_at)"
                    " VALUES ('out_of_grade', ?, ?, ?, ?, ?)",
                    (classification, content, background, req_priority, now()),
                )
                imported.append((cur.lastrowid, "out_of_grade", classification, content))

    conn.commit()
    print(f"取り込み完了: {args.input}")
    print(f"  顧客判定の更新: {updated_judgements}項目")
    print(f"  新規指摘: {len(imported)}件（重複スキップ: {skipped_dup}件）")
    for fid, kind, target, text in imported:
        label = target if kind == "item" else f"グレード外/{target or '分類なし'}"
        print(f"    [#{fid}] {label}: {text[:60]}")
    conn.close()


# ---------------------------------------------------------------- list/update feedback
def cmd_list_feedback(args) -> None:
    conn = connect(args.db)
    sql = (
        "SELECT f.*, i.item_name, i.priority FROM feedback f"
        " LEFT JOIN nfr_items i ON i.item_id = f.item_id"
    )
    params = []
    if args.status:
        sql += " WHERE f.status = ?"
        params.append(args.status)
    sql += " ORDER BY f.id"
    rows = [dict(r) for r in conn.execute(sql, params)]
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    conn.close()


def cmd_update_feedback(args) -> None:
    conn = connect(args.db)
    row = conn.execute("SELECT * FROM feedback WHERE id = ?", (args.id,)).fetchone()
    if not row:
        die(f"指摘 #{args.id} が見つかりません")
    sets, params = [], []
    if args.response is not None:
        sets.append("response = ?")
        params.append(args.response)
    if args.status:
        sets.append("status = ?")
        params.append(args.status)
    if args.item_id:
        known = conn.execute(
            "SELECT 1 FROM nfr_items WHERE item_id = ?", (args.item_id,)
        ).fetchone()
        if not known:
            die(f"項目ID {args.item_id} はマスタに存在しません")
        sets.append("item_id = ?")
        params.append(args.item_id)
    if not sets:
        die("--response / --status / --item-id のいずれかを指定してください")
    params.append(args.id)
    conn.execute(f"UPDATE feedback SET {', '.join(sets)} WHERE id = ?", params)
    conn.commit()
    print(f"指摘 #{args.id} を更新しました")
    conn.close()


# ---------------------------------------------------------------- dump
def cmd_dump(args) -> None:
    conn = connect(args.db)
    p = dict(conn.execute("SELECT * FROM project").fetchone())
    items = [dict(r) for r in _select_rows(conn)]
    feedback = [
        dict(r) for r in conn.execute(
            "SELECT f.*, i.item_name FROM feedback f"
            " LEFT JOIN nfr_items i ON i.item_id = f.item_id ORDER BY f.id"
        )
    ]
    if args.format == "json":
        print(json.dumps(
            {"project": p, "items": items, "feedback": feedback},
            ensure_ascii=False, indent=2,
        ))
    else:
        print(f"# 非機能要件データ: {p['system_name']}（モデルシステム{p['model_system']}）\n")
        for pr in ("高", "中", "低"):
            subset = [i for i in items if i["priority"] == pr]
            print(f"## 優先度: {pr}（{len(subset)}項目）\n")
            print("| 項目ID | 項目名 | 選択レベル | 選択値 | 備考 | 顧客判定 |")
            print("|--------|--------|-----------|--------|------|---------|")
            for i in subset:
                print(
                    f"| {i['item_id']} | {i['item_name']} | {i['level'] or '未登録'} |"
                    f" {i['value'] or ''} | {i['note'] or ''} |"
                    f" {i['customer_judgement'] or '未確認'} |"
                )
            print()
        if feedback:
            print("## 顧客指摘一覧\n")
            print("| # | 区分 | 対象 | 指摘・要求内容 | 対応方針 | 状態 |")
            print("|---|------|------|---------------|---------|------|")
            for f in feedback:
                target = (
                    f"{f['item_id']} {f['item_name'] or ''}".strip()
                    if f["kind"] == "item"
                    else f"グレード外（{f['classification'] or '分類なし'}）"
                )
                print(
                    f"| {f['id']} | {'項目指摘' if f['kind'] == 'item' else 'グレード外要求'} |"
                    f" {target} | {f['feedback']} | {f['response'] or '未定'} | {f['status']} |"
                )
    conn.close()


# ---------------------------------------------------------------- export-word
INLINE_RE = re.compile(r"(\*\*.+?\*\*|`.+?`)")


def _add_runs(paragraph, text: str) -> None:
    for part in INLINE_RE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`") and len(part) > 1:
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
        else:
            paragraph.add_run(re.sub(r"\*([^*]+)\*", r"\1", part))


def _set_ja_font(doc, font_name: str = "游ゴシック") -> None:
    from docx.oxml.ns import qn
    for style_name in (
        "Normal", "Title", "Heading 1", "Heading 2", "Heading 3", "Heading 4",
        "List Bullet", "List Number",
    ):
        try:
            style = doc.styles[style_name]
        except KeyError:
            continue
        style.font.name = font_name
        style.element.rPr.rFonts.set(qn("w:eastAsia"), font_name)


def _add_table(doc, rows: list) -> None:
    cells = [
        [c.strip() for c in line.strip().strip("|").split("|")]
        for line in rows
        if not re.match(r"^\s*\|?[\s:|-]+\|?\s*$", line)
    ]
    if not cells:
        return
    ncols = max(len(r) for r in cells)
    table = doc.add_table(rows=len(cells), cols=ncols)
    table.style = "Table Grid"
    for ri, row in enumerate(cells):
        for ci in range(ncols):
            text = row[ci] if ci < len(row) else ""
            cell = table.cell(ri, ci)
            cell.text = ""
            para = cell.paragraphs[0]
            _add_runs(para, text)
            if ri == 0:
                for run in para.runs:
                    run.bold = True


def _markdown_to_docx(doc, md_text: str) -> None:
    lines = md_text.splitlines()
    i, in_code = 0, False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            para = doc.add_paragraph()
            run = para.add_run(line)
            run.font.name = "Consolas"
            i += 1
            continue
        stripped = line.strip()
        if not stripped or re.fullmatch(r"-{3,}", stripped):
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = min(len(m.group(1)), 4)
            doc.add_heading(re.sub(r"[*`]", "", m.group(2)), level=level)
            i += 1
            continue
        if stripped.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            _add_table(doc, block)
            continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            para = doc.add_paragraph(style="List Bullet")
            _add_runs(para, m.group(1))
            i += 1
            continue
        m = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if m:
            para = doc.add_paragraph(style="List Number")
            _add_runs(para, m.group(1))
            i += 1
            continue
        if stripped.startswith(">"):
            para = doc.add_paragraph()
            run = para.add_run(stripped.lstrip("> "))
            run.italic = True
            i += 1
            continue
        para = doc.add_paragraph()
        _add_runs(para, stripped)
        i += 1


def cmd_export_word(args) -> None:
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Pt
    except ImportError:
        die("python-docx がインストールされていません: pip install python-docx")
    if not Path(args.design).exists():
        die(f"運用設計書（Markdown）が見つかりません: {args.design}")

    conn = connect(args.db)
    p = conn.execute("SELECT * FROM project").fetchone()
    items = _select_rows(conn)
    feedback = conn.execute(
        "SELECT f.*, i.item_name FROM feedback f"
        " LEFT JOIN nfr_items i ON i.item_id = f.item_id ORDER BY f.id"
    ).fetchall()

    doc = Document()
    _set_ja_font(doc)
    doc.styles["Normal"].font.size = Pt(10.5)

    # 表紙
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(f"\n\n\n{p['system_name']}\n運用設計書")
    run.font.size = Pt(28)
    run.bold = True
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run(
        f"\nIPA非機能要求グレード2018準拠（モデルシステム{p['model_system']}）\n"
        f"{datetime.now(JST).strftime('%Y年%m月%d日')}"
    ).font.size = Pt(14)
    doc.add_page_break()

    # 本文（Markdown変換）
    _markdown_to_docx(doc, Path(args.design).read_text(encoding="utf-8"))

    # 付録: 非機能要件選択一覧（優先度別）
    doc.add_page_break()
    doc.add_heading("付録: 非機能要件選択一覧（優先度別）", level=1)
    doc.add_paragraph(
        "優先度は後続の設計・構築作業への影響度に基づく分類（高・中・低）です。"
    )
    for pr in ("高", "中", "低"):
        subset = [i for i in items if i["priority"] == pr]
        if not subset:
            continue
        doc.add_heading(f"優先度: {pr}（{len(subset)}項目）", level=2)
        table = doc.add_table(rows=1 + len(subset), cols=6)
        table.style = "Table Grid"
        for ci, h in enumerate(
            ["項目ID", "項目名", "選択レベル", "選択値・具体値", "備考", "顧客判定"]
        ):
            cell = table.cell(0, ci)
            cell.text = h
            cell.paragraphs[0].runs[0].bold = True
        for ri, it in enumerate(subset, start=1):
            vals = [
                it["item_id"], it["item_name"], it["level"] or "[要確認: 未登録]",
                it["value"] or "", it["note"] or "", it["customer_judgement"] or "未確認",
            ]
            for ci, v in enumerate(vals):
                table.cell(ri, ci).text = str(v)

    # 付録: 顧客指摘対応表
    if feedback:
        doc.add_heading("付録: 顧客指摘対応表", level=1)
        table = doc.add_table(rows=1 + len(feedback), cols=6)
        table.style = "Table Grid"
        for ci, h in enumerate(["#", "区分", "対象", "指摘・要求内容", "対応方針", "状態"]):
            cell = table.cell(0, ci)
            cell.text = h
            cell.paragraphs[0].runs[0].bold = True
        for ri, f in enumerate(feedback, start=1):
            target = (
                f"{f['item_id']} {f['item_name'] or ''}".strip()
                if f["kind"] == "item"
                else f"グレード外（{f['classification'] or '分類なし'}）"
            )
            vals = [
                str(f["id"]),
                "項目指摘" if f["kind"] == "item" else "グレード外要求",
                target, f["feedback"], f["response"] or "[要確認: 対応方針未定]",
                f["status"],
            ]
            for ci, v in enumerate(vals):
                table.cell(ri, ci).text = v

    doc.save(args.output)
    open_fb = sum(1 for f in feedback if f["status"] == "open")
    print(f"Word出力完了: {args.output}")
    print(f"  付録: 非機能要件{len(items)}項目 / 顧客指摘{len(feedback)}件（未対応 {open_fb}件）")
    conn.close()


# ---------------------------------------------------------------- main
def main() -> None:
    with contextlib.suppress(AttributeError, ValueError):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    parser = argparse.ArgumentParser(
        description="IPA非機能要求グレード ワークフロー管理CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="DB初期化＋項目マスタロード")
    p.add_argument("--db", required=True)
    p.add_argument("--project", required=True, help="対象システム名")
    p.add_argument("--model-system", type=int, required=True, choices=[1, 2, 3])
    p.add_argument("--master", help="項目マスタCSV（省略時は同梱マスタ）")
    p.add_argument("--force", action="store_true", help="既存DBを上書き")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("register", help="ヒアリング結果のJSON登録")
    p.add_argument("--db", required=True)
    p.add_argument("--input", required=True, help="JSONファイルパス（- で標準入力）")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("status", help="登録・指摘対応状況サマリー")
    p.add_argument("--db", required=True)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("export-excel", help="顧客レビュー用Excel出力")
    p.add_argument("--db", required=True)
    p.add_argument("--output", required=True, help="出力先 .xlsx パス")
    p.set_defaults(func=cmd_export_excel)

    p = sub.add_parser("import-feedback", help="顧客記入済みExcelの取り込み")
    p.add_argument("--db", required=True)
    p.add_argument("--input", required=True, help="顧客記入済み .xlsx パス")
    p.set_defaults(func=cmd_import_feedback)

    p = sub.add_parser("list-feedback", help="指摘一覧（JSON）")
    p.add_argument("--db", required=True)
    p.add_argument("--status", choices=["open", "accepted", "rejected", "reflected"])
    p.set_defaults(func=cmd_list_feedback)

    p = sub.add_parser("update-feedback", help="指摘の対応方針・状態更新")
    p.add_argument("--db", required=True)
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--response", help="対応方針")
    p.add_argument("--status", choices=["open", "accepted", "rejected", "reflected"])
    p.add_argument("--item-id", help="グレード外要求を項目に紐付ける場合の項目ID")
    p.set_defaults(func=cmd_update_feedback)

    p = sub.add_parser("dump", help="DB内容の出力（設計書生成の入力）")
    p.add_argument("--db", required=True)
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.set_defaults(func=cmd_dump)

    p = sub.add_parser("export-word", help="Markdown運用設計書のWord変換＋付録追加")
    p.add_argument("--db", required=True)
    p.add_argument("--design", required=True, help="運用設計書Markdownファイル")
    p.add_argument("--output", required=True, help="出力先 .docx パス")
    p.set_defaults(func=cmd_export_word)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
