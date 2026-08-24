#!/usr/bin/env python3
"""reqctl.py - 要求レジストリ（YAML）の検証・生成・影響分析ツール.

サブコマンド:
  validate  レジストリの構造・参照・矛盾を検査する
  generate  index.md / traceability.md / graph.md を生成する
  impact    指定IDの影響範囲（依存・被依存・ストーリー・検証）を出力する
  next-id   次に採番すべきIDを出力する
  stats     要求・ストーリーの件数サマリを出力する

依存: PyYAML のみ（それ以外は標準ライブラリ）
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import json
import math
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("PyYAML が必要です: pip install pyyaml\n")
    sys.exit(3)

# --------------------------------------------------------------------------
# 定数
# --------------------------------------------------------------------------

REQ_ID_RE = re.compile(r"^REQ-\d{3,}$")
US_ID_RE = re.compile(r"^US-\d{3,}$")

REQ_TYPES = {"functional", "quality", "constraint"}
REQ_STATUS = {"draft", "active", "deprecated", "superseded"}
REQ_PRIORITY = {"must", "should", "could", "wont"}
STORY_STATUS = {"draft", "active", "done", "dropped"}
VERIFY_KINDS = {"test", "manual", "review", "metric"}
OPS = {"<", "<=", ">", ">=", "==", "!="}

LIVE_STATUS = {"draft", "active"}  # 生きている要求
RETIRED_STATUS = {"deprecated", "superseded"}

DEFAULT_AMBIGUOUS = [
    "適切に", "適宜", "必要に応じて", "など", "なるべく", "可能な限り",
    "高速", "十分", "柔軟", "簡単に", "素早く", "使いやすい",
    "ユーザーフレンドリー", "基本的に", "原則として", "極力",
]

DEFAULT_STALE_DAYS = 365
SIMILARITY_THRESHOLD = 0.90

LEVEL_ERROR = "ERROR"
LEVEL_WARN = "WARN"
LEVEL_INFO = "INFO"


# --------------------------------------------------------------------------
# 読み込み
# --------------------------------------------------------------------------

class Registry:
    """レジストリ全体（要求・ストーリー・用語・ポリシー）を保持する."""

    def __init__(self):
        self.requirements: dict[str, dict] = {}
        self.stories: dict[str, dict] = {}
        self.terms: dict[str, dict] = {}
        self.policy: dict = {}
        self.sources: dict[str, str] = {}  # ID -> 定義元ファイル
        self.load_errors: list[tuple[str, str]] = []

    def story_reqs(self, sid: str, live_only: bool = True) -> list[str]:
        """ストーリーに紐付く要求IDを要求側の stories から導出する（唯一の正）."""
        return sorted(
            rid for rid, r in self.requirements.items()
            if sid in (r.get("stories") or [])
            and (not live_only or r.get("status") in LIVE_STATUS)
        )

    @property
    def ambiguous_words(self) -> list[str]:
        return self.policy.get("ambiguous_words", DEFAULT_AMBIGUOUS)

    @property
    def multi_value_keys(self) -> set[str]:
        return set(self.policy.get("multi_value_keys", []))

    @property
    def stale_days(self) -> int:
        return int(self.policy.get("stale_days", DEFAULT_STALE_DAYS))


def load_registry(root: Path) -> Registry:
    """root 配下の YAML を再帰的に読み込んでマージする（generated/ は除外）."""
    reg = Registry()
    if not root.exists():
        reg.load_errors.append((str(root), "ディレクトリが存在しません"))
        return reg

    files = sorted(
        p for p in root.rglob("*.y*ml")
        if "generated" not in p.relative_to(root).parts
    )
    for path in files:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            reg.load_errors.append((str(path), f"YAMLパースエラー: {exc}"))
            continue
        if data is None:
            continue
        if not isinstance(data, dict):
            reg.load_errors.append((str(path), "トップレベルはマッピングである必要があります"))
            continue

        rel = str(path)
        for item in data.get("requirements") or []:
            if not isinstance(item, dict):
                reg.load_errors.append((rel, "requirements の要素がマッピングではありません"))
                continue
            rid = item.get("id")
            if rid in reg.requirements:
                reg.load_errors.append((rel, f"要求IDが重複しています: {rid} (既出: {reg.sources.get(rid)})"))
                continue
            if rid:
                reg.requirements[rid] = item
                reg.sources[rid] = rel

        for item in data.get("stories") or []:
            if not isinstance(item, dict):
                reg.load_errors.append((rel, "stories の要素がマッピングではありません"))
                continue
            sid = item.get("id")
            if sid in reg.stories:
                reg.load_errors.append((rel, f"ストーリーIDが重複しています: {sid} (既出: {reg.sources.get(sid)})"))
                continue
            if sid:
                reg.stories[sid] = item
                reg.sources[sid] = rel

        for item in data.get("terms") or []:
            if isinstance(item, dict) and item.get("name"):
                reg.terms[item["name"]] = item

        if isinstance(data.get("policy"), dict):
            reg.policy.update(data["policy"])

    return reg


# --------------------------------------------------------------------------
# 検査結果
# --------------------------------------------------------------------------

def finding(level: str, code: str, target: str, message: str, hint: str = "") -> dict:
    return {"level": level, "code": code, "target": target, "message": message, "hint": hint}


# --------------------------------------------------------------------------
# 検査: 構造
# --------------------------------------------------------------------------

def check_schema(reg: Registry) -> list[dict]:
    out = []
    for rid, r in reg.requirements.items():
        if not REQ_ID_RE.match(rid):
            out.append(finding(LEVEL_ERROR, "E-IDFMT", rid, "要求IDの書式が不正です（REQ-0001 形式）"))

        for field in ("title", "statement", "type", "status", "priority"):
            if not r.get(field):
                out.append(finding(LEVEL_ERROR, "E-SCHEMA", rid, f"必須フィールドがありません: {field}"))

        if r.get("type") and r["type"] not in REQ_TYPES:
            out.append(finding(LEVEL_ERROR, "E-SCHEMA", rid, f"type が不正です: {r['type']}（許容: {sorted(REQ_TYPES)}）"))
        if r.get("status") and r["status"] not in REQ_STATUS:
            out.append(finding(LEVEL_ERROR, "E-SCHEMA", rid, f"status が不正です: {r['status']}（許容: {sorted(REQ_STATUS)}）"))
        if r.get("priority") and r["priority"] not in REQ_PRIORITY:
            out.append(finding(LEVEL_ERROR, "E-SCHEMA", rid, f"priority が不正です: {r['priority']}（許容: {sorted(REQ_PRIORITY)}）"))

        for v in r.get("verification") or []:
            if not isinstance(v, dict) or not v.get("kind") or not v.get("ref"):
                out.append(finding(LEVEL_ERROR, "E-SCHEMA", rid, "verification の要素には kind と ref が必要です"))
            elif v["kind"] not in VERIFY_KINDS:
                out.append(finding(LEVEL_ERROR, "E-SCHEMA", rid, f"verification.kind が不正です: {v['kind']}"))

        for m in r.get("measures") or []:
            if not isinstance(m, dict):
                out.append(finding(LEVEL_ERROR, "E-SCHEMA", rid, "measures の要素はマッピングである必要があります"))
                continue
            if not m.get("subject") or m.get("op") not in OPS or not isinstance(m.get("value"), (int, float)):
                out.append(finding(
                    LEVEL_ERROR, "E-SCHEMA", rid,
                    "measures には subject / op（比較演算子）/ value（数値）が必要です"))

        for key in ("asserts", "forbids"):
            for a in r.get(key) or []:
                if not isinstance(a, dict) or not a.get("key") or "value" not in a:
                    out.append(finding(LEVEL_ERROR, "E-SCHEMA", rid, f"{key} の要素には key と value が必要です"))

    for sid, s in reg.stories.items():
        if not US_ID_RE.match(sid):
            out.append(finding(LEVEL_ERROR, "E-IDFMT", sid, "ストーリーIDの書式が不正です（US-001 形式）"))
        for field in ("as_a", "i_want", "so_that"):
            if not s.get(field):
                out.append(finding(LEVEL_ERROR, "E-SCHEMA", sid, f"必須フィールドがありません: {field}"))
        if s.get("acceptance"):
            out.append(finding(
                LEVEL_ERROR, "E-DUPLINK", sid,
                "ストーリー側に acceptance は書きません（リンクの二重管理は禁止）",
                "要求側の stories フィールドで紐付けてください。受入要求一覧は generated/ に自動生成されます"))
        if s.get("status") and s["status"] not in STORY_STATUS:
            out.append(finding(LEVEL_ERROR, "E-SCHEMA", sid, f"status が不正です: {s['status']}（許容: {sorted(STORY_STATUS)}）"))
    return out


def check_rationale(reg: Registry) -> list[dict]:
    """理由なき要求を許さない（このスキルの中核ルール）."""
    out = []
    for rid, r in reg.requirements.items():
        rat = r.get("rationale")
        if not isinstance(rat, dict):
            out.append(finding(LEVEL_ERROR, "E-RATIONALE", rid,
                               "rationale がありません。要求には必ず理由を紐付けてください"))
            continue
        why = (rat.get("why") or "").strip()
        if len(why) < 10:
            out.append(finding(LEVEL_ERROR, "E-RATIONALE", rid,
                               "rationale.why が空または短すぎます（10文字以上で「なぜこの要求が必要か」を記述）"))
        if not rat.get("source"):
            out.append(finding(LEVEL_WARN, "W-RATIONALE-SRC", rid,
                               "rationale.source（誰の要望/どの決定に由来するか）が未記入です"))
        decided = rat.get("decided_at")
        if decided:
            try:
                d = _parse_date(decided)
                age = (datetime.date.today() - d).days
                if age > reg.stale_days and r.get("status") == "active":
                    out.append(finding(LEVEL_WARN, "W-STALE", rid,
                                       f"rationale.decided_at から {age} 日経過しています。理由がまだ有効か再確認してください"))
            except ValueError:
                out.append(finding(LEVEL_ERROR, "E-SCHEMA", rid,
                                   f"rationale.decided_at の日付書式が不正です: {decided}（YYYY-MM-DD）"))
        else:
            out.append(finding(LEVEL_WARN, "W-RATIONALE-DATE", rid, "rationale.decided_at が未記入です"))
    return out


def _parse_date(value) -> datetime.date:
    if isinstance(value, datetime.date):
        return value
    return datetime.datetime.strptime(str(value), "%Y-%m-%d").date()


def check_references(reg: Registry) -> list[dict]:
    out = []
    for rid, r in reg.requirements.items():
        for field in ("depends_on", "conflicts_with", "supersedes", "refines"):
            for ref in r.get(field) or []:
                if ref not in reg.requirements:
                    out.append(finding(LEVEL_ERROR, "E-REF", rid, f"{field} の参照先が存在しません: {ref}"))
        for ref in r.get("stories") or []:
            if ref not in reg.stories:
                out.append(finding(LEVEL_ERROR, "E-REF", rid, f"stories の参照先が存在しません: {ref}"))
        for term in r.get("terms") or []:
            if reg.terms and term not in reg.terms:
                out.append(finding(LEVEL_WARN, "W-TERM-UNDEF", rid, f"用語集に未定義の用語です: {term}"))

    return out


def check_cycles(reg: Registry) -> list[dict]:
    """depends_on / refines の循環を検出する."""
    out = []
    graph = {
        rid: [x for x in (r.get("depends_on") or []) + (r.get("refines") or []) if x in reg.requirements]
        for rid, r in reg.requirements.items()
    }
    state: dict[str, int] = {}
    stack: list[str] = []
    reported: set[tuple[str, ...]] = set()

    def dfs(node: str):
        state[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            if state.get(nxt, 0) == 0:
                dfs(nxt)
            elif state.get(nxt) == 1:
                cycle = stack[stack.index(nxt):] + [nxt]
                key = tuple(sorted(set(cycle)))
                if key not in reported:
                    reported.add(key)
                    out.append(finding(LEVEL_ERROR, "E-CYCLE", nxt,
                                       "依存関係が循環しています: " + " -> ".join(cycle)))
        stack.pop()
        state[node] = 2

    for rid in graph:
        if state.get(rid, 0) == 0:
            dfs(rid)
    return out


def check_lifecycle(reg: Registry) -> list[dict]:
    """削除の代わりに廃止（tombstone）を強制し、廃止済みへの参照を禁ずる."""
    out = []
    superseded_by: dict[str, list[str]] = {}
    for rid, r in reg.requirements.items():
        for old in r.get("supersedes") or []:
            superseded_by.setdefault(old, []).append(rid)

    for rid, r in reg.requirements.items():
        status = r.get("status")
        if status == "superseded":
            if rid not in superseded_by:
                out.append(finding(LEVEL_ERROR, "E-SUPERSEDE", rid,
                                   "status が superseded ですが、これを supersedes する要求がありません"))
        elif rid in superseded_by:
            out.append(finding(LEVEL_ERROR, "E-SUPERSEDE", rid,
                               f"{', '.join(superseded_by[rid])} に supersedes されていますが status が {status} です"))

        if status in RETIRED_STATUS and not (r.get("rationale") or {}).get("retired_why"):
            out.append(finding(LEVEL_ERROR, "E-RETIRE", rid,
                               f"status が {status} の要求には rationale.retired_why（廃止理由）が必要です"))

        if status in LIVE_STATUS:
            for field in ("depends_on", "refines"):
                for ref in r.get(field) or []:
                    tgt = reg.requirements.get(ref)
                    if tgt and tgt.get("status") in RETIRED_STATUS:
                        out.append(finding(LEVEL_ERROR, "E-DEAD-REF", rid,
                                           f"生きている要求が廃止済み要求を {field} で参照しています: {ref}（status={tgt.get('status')}）"))

    for sid, s in reg.stories.items():
        if s.get("status") not in {"draft", "active"}:
            continue
        linked = [rid for rid, r in reg.requirements.items() if sid in (r.get("stories") or [])]
        if linked and not reg.story_reqs(sid):
            out.append(finding(LEVEL_ERROR, "E-DEAD-STORY", sid,
                               f"紐付く要求がすべて廃止済みです（{', '.join(sorted(linked))}）",
                               "ストーリーを dropped/done にするか、置換後の要求を紐付けてください"))
    return out


# --------------------------------------------------------------------------
# 検査: 矛盾
# --------------------------------------------------------------------------

def _accepted_conflicts(reg: Registry) -> set[frozenset[str]]:
    """conflicts_with で相互宣言されたペア＝許容済みの緊張関係."""
    pairs = set()
    for rid, r in reg.requirements.items():
        for other in r.get("conflicts_with") or []:
            if other in reg.requirements and rid in (reg.requirements[other].get("conflicts_with") or []):
                pairs.add(frozenset((rid, other)))
    return pairs


def check_declared_conflicts(reg: Registry) -> list[dict]:
    out = []
    for rid, r in reg.requirements.items():
        for other in r.get("conflicts_with") or []:
            if other not in reg.requirements:
                continue
            back = reg.requirements[other].get("conflicts_with") or []
            if rid not in back:
                out.append(finding(LEVEL_ERROR, "E-CONFLICT-ONEWAY", rid,
                                   f"conflicts_with が片方向です: {other} 側にも {rid} を宣言してください"))
            if not (r.get("rationale") or {}).get("tradeoff"):
                out.append(finding(LEVEL_ERROR, "E-CONFLICT-NOTRADEOFF", rid,
                                   f"{other} との衝突を宣言していますが rationale.tradeoff（許容理由）がありません"))
    return out


def _interval(op: str, value: float):
    """単一制約を (lo, lo_strict, hi, hi_strict) に変換する."""
    if op == "<":
        return (-math.inf, False, value, True)
    if op == "<=":
        return (-math.inf, False, value, False)
    if op == ">":
        return (value, True, math.inf, False)
    if op == ">=":
        return (value, False, math.inf, False)
    if op == "==":
        return (value, False, value, False)
    return None  # != は区間で表せないので個別処理


def _intersect(a, b):
    lo, lo_s, hi, hi_s = a
    lo2, lo_s2, hi2, hi_s2 = b
    if lo2 > lo or (lo2 == lo and lo_s2):
        lo, lo_s = lo2, lo_s2
    if hi2 < hi or (hi2 == hi and hi_s2):
        hi, hi_s = hi2, hi_s2
    return (lo, lo_s, hi, hi_s)


def _empty(iv) -> bool:
    lo, lo_s, hi, hi_s = iv
    if lo > hi:
        return True
    return lo == hi and (lo_s or hi_s)


def check_numeric_conflicts(reg: Registry) -> list[dict]:
    """同一 subject の数値制約が同時に成立しないケースを検出する."""
    out = []
    accepted = _accepted_conflicts(reg)
    by_subject: dict[str, list[tuple[str, dict]]] = {}
    for rid, r in reg.requirements.items():
        if r.get("status") not in LIVE_STATUS:
            continue
        for m in r.get("measures") or []:
            if not isinstance(m, dict) or m.get("op") not in OPS:
                continue
            if not isinstance(m.get("value"), (int, float)):
                continue
            by_subject.setdefault(m["subject"], []).append((rid, m))

    for subject, entries in sorted(by_subject.items()):
        units = {str(m.get("unit") or "") for _, m in entries}
        if len(units) > 1:
            out.append(finding(LEVEL_WARN, "W-UNIT", subject,
                               f"subject '{subject}' で単位が混在しています: {sorted(units)}。数値矛盾の判定をスキップしました",
                               "単位を統一するか subject を分けてください"))
            continue

        ranged = [(rid, m) for rid, m in entries if m["op"] != "!="]
        # ペア単位の矛盾（報告しやすい形）
        pair_reported: set[frozenset[str]] = set()
        for i in range(len(ranged)):
            for j in range(i + 1, len(ranged)):
                rid_a, ma = ranged[i]
                rid_b, mb = ranged[j]
                if rid_a == rid_b:
                    continue
                key = frozenset((rid_a, rid_b))
                if key in accepted or key in pair_reported:
                    continue
                iv = _intersect(_interval(ma["op"], ma["value"]), _interval(mb["op"], mb["value"]))
                if _empty(iv):
                    pair_reported.add(key)
                    unit = ma.get("unit") or ""
                    out.append(finding(
                        LEVEL_ERROR, "E-CONFLICT-NUM", f"{rid_a} x {rid_b}",
                        f"'{subject}' に対して同時に満たせない制約です: "
                        f"{rid_a}({ma['op']}{ma['value']}{unit}) と {rid_b}({mb['op']}{mb['value']}{unit})",
                        "いずれかを変更するか、両者に conflicts_with と rationale.tradeoff を宣言してください"))

        # 全体としての充足不能（ペアでは検出できないケース）
        if not pair_reported and len(ranged) > 2:
            iv = (-math.inf, False, math.inf, False)
            for _, m in ranged:
                iv = _intersect(iv, _interval(m["op"], m["value"]))
            if _empty(iv):
                ids = ", ".join(sorted({rid for rid, _ in ranged}))
                out.append(finding(LEVEL_ERROR, "E-CONFLICT-NUM", subject,
                                   f"'{subject}' の制約群が全体として充足不能です: {ids}"))

        # != と 1点確定の衝突
        point = None
        iv = (-math.inf, False, math.inf, False)
        for _, m in ranged:
            iv = _intersect(iv, _interval(m["op"], m["value"]))
        if not _empty(iv) and iv[0] == iv[2]:
            point = iv[0]
        if point is not None:
            for rid, m in entries:
                if m["op"] == "!=" and m["value"] == point:
                    out.append(finding(LEVEL_ERROR, "E-CONFLICT-NUM", rid,
                                       f"'{subject}' は他の制約により {point} に確定しますが、{rid} が != {point} を要求しています"))
    return out


def check_fact_conflicts(reg: Registry) -> list[dict]:
    """asserts（こうであること）/ forbids（こうでないこと）の衝突を検出する."""
    out = []
    accepted = _accepted_conflicts(reg)
    multi = reg.multi_value_keys
    asserts: dict[str, list[tuple[str, object]]] = {}
    forbids: dict[str, list[tuple[str, object]]] = {}

    for rid, r in reg.requirements.items():
        if r.get("status") not in LIVE_STATUS:
            continue
        for a in r.get("asserts") or []:
            if isinstance(a, dict) and a.get("key"):
                asserts.setdefault(a["key"], []).append((rid, a.get("value")))
        for a in r.get("forbids") or []:
            if isinstance(a, dict) and a.get("key"):
                forbids.setdefault(a["key"], []).append((rid, a.get("value")))

    for key, entries in sorted(asserts.items()):
        if key in multi:
            continue
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                (rid_a, va), (rid_b, vb) = entries[i], entries[j]
                if rid_a == rid_b or va == vb:
                    continue
                if frozenset((rid_a, rid_b)) in accepted:
                    continue
                out.append(finding(
                    LEVEL_ERROR, "E-CONFLICT-FACT", f"{rid_a} x {rid_b}",
                    f"'{key}' に異なる値を要求しています: {rid_a}={va!r} / {rid_b}={vb!r}",
                    "値を揃えるか、key を multi_value_keys に登録するか、conflicts_with を宣言してください"))

    for key, entries in sorted(forbids.items()):
        for rid_f, vf in entries:
            for rid_a, va in asserts.get(key, []):
                if rid_a == rid_f or va != vf:
                    continue
                if frozenset((rid_a, rid_f)) in accepted:
                    continue
                out.append(finding(
                    LEVEL_ERROR, "E-CONFLICT-FACT", f"{rid_a} x {rid_f}",
                    f"'{key}={va!r}' を {rid_a} が要求し {rid_f} が禁止しています"))
    return out


# --------------------------------------------------------------------------
# 検査: 品質・カバレッジ
# --------------------------------------------------------------------------

def check_quality(reg: Registry) -> list[dict]:
    out = []
    for rid, r in reg.requirements.items():
        stmt = r.get("statement") or ""
        if r.get("status") not in LIVE_STATUS:
            continue
        for word in reg.ambiguous_words:
            if word in stmt:
                out.append(finding(LEVEL_WARN, "W-AMBIGUOUS", rid,
                                   f"曖昧な表現が含まれています: 「{word}」",
                                   "測定可能な条件・数値に置き換えてください"))
        if "システムは" not in stmt or not re.search(r"(なければならない|てはならない|ないものとする)", stmt):
            out.append(finding(LEVEL_WARN, "W-EARS", rid,
                               "EARS記法に沿っていない可能性があります（「システムは〜しなければならない」を含む形へ）"))
        for name, term in reg.terms.items():
            for alias in term.get("aliases") or []:
                if alias and alias in stmt and name not in stmt:
                    out.append(finding(LEVEL_WARN, "W-TERM-ALIAS", rid,
                                       f"用語ゆれです: 「{alias}」ではなく正規語「{name}」を使用してください"))
    return out


def check_duplicates(reg: Registry) -> list[dict]:
    out = []
    live = [(rid, re.sub(r"[\s、。,.「」（）()]", "", r.get("statement") or ""))
            for rid, r in reg.requirements.items() if r.get("status") in LIVE_STATUS]
    for i in range(len(live)):
        for j in range(i + 1, len(live)):
            (rid_a, sa), (rid_b, sb) = live[i], live[j]
            if not sa or not sb:
                continue
            ratio = difflib.SequenceMatcher(None, sa, sb).ratio()
            if ratio >= SIMILARITY_THRESHOLD:
                out.append(finding(LEVEL_WARN, "W-DUP", f"{rid_a} x {rid_b}",
                                   f"要求文が酷似しています（類似度 {ratio:.0%}）。重複の可能性があります"))
    return out


def check_coverage(reg: Registry, check_tests: bool, repo_root: Path) -> list[dict]:
    """テスト条件＝要求とユーザーストーリーが満たされること、を担保する検査."""
    out = []
    story_of_req = {rid: list(r.get("stories") or []) for rid, r in reg.requirements.items()}

    for rid, r in reg.requirements.items():
        if r.get("status") != "active":
            continue
        if not r.get("verification"):
            out.append(finding(LEVEL_ERROR, "E-NOVERIFY", rid,
                               "active な要求に verification がありません（検証不能な要求は認めません）"))
        if r.get("type") == "functional" and not story_of_req.get(rid):
            out.append(finding(LEVEL_WARN, "W-ORPHAN-REQ", rid,
                               "どのユーザーストーリーにも紐付いていない機能要求です"))
        if check_tests:
            for v in r.get("verification") or []:
                if not isinstance(v, dict) or v.get("kind") != "test":
                    continue
                ref = str(v.get("ref") or "")
                path = repo_root / ref.split("::", 1)[0]
                if not path.exists():
                    out.append(finding(LEVEL_ERROR, "E-TESTMISS", rid,
                                       f"verification が指すテストファイルが存在しません: {ref}"))

    for sid, s in reg.stories.items():
        if s.get("status") in {"dropped"}:
            continue
        if not reg.story_reqs(sid):
            out.append(finding(LEVEL_ERROR, "E-ORPHAN-US", sid,
                               "受入条件となる有効な要求が1件もありません",
                               "このストーリーを満たす要求に stories: [<このID>] を追加してください"))
    return out


# --------------------------------------------------------------------------
# validate
# --------------------------------------------------------------------------

def run_validate(reg: Registry, check_tests: bool, repo_root: Path) -> list[dict]:
    findings = [finding(LEVEL_ERROR, "E-LOAD", src, msg) for src, msg in reg.load_errors]
    findings += check_schema(reg)
    findings += check_rationale(reg)
    findings += check_references(reg)
    findings += check_cycles(reg)
    findings += check_lifecycle(reg)
    findings += check_declared_conflicts(reg)
    findings += check_numeric_conflicts(reg)
    findings += check_fact_conflicts(reg)
    findings += check_quality(reg)
    findings += check_duplicates(reg)
    findings += check_coverage(reg, check_tests, repo_root)
    order = {LEVEL_ERROR: 0, LEVEL_WARN: 1, LEVEL_INFO: 2}
    findings.sort(key=lambda f: (order.get(f["level"], 9), f["code"], f["target"]))
    return findings


def print_findings(findings: list[dict], reg: Registry) -> None:
    errors = [f for f in findings if f["level"] == LEVEL_ERROR]
    warns = [f for f in findings if f["level"] == LEVEL_WARN]
    if not findings:
        print("[OK] 検査対象に問題は見つかりませんでした")
    for f in findings:
        mark = "[ERR] " if f["level"] == LEVEL_ERROR else "[WARN]"
        print(f"{mark} {f['code']:<22} {f['target']}: {f['message']}")
        if f["hint"]:
            print(f"        ヒント: {f['hint']}")
    print()
    print(f"要求 {len(reg.requirements)} 件 / ストーリー {len(reg.stories)} 件 / "
          f"エラー {len(errors)} 件 / 警告 {len(warns)} 件")


# --------------------------------------------------------------------------
# generate
# --------------------------------------------------------------------------

STATUS_LABEL = {
    "draft": "起案中", "active": "有効", "deprecated": "廃止", "superseded": "置換済",
    "done": "完了", "dropped": "取下げ",
}


def _link_list(ids) -> str:
    return ", ".join(ids) if ids else "-"


def gen_index(reg: Registry) -> str:
    lines = ["# 要求一覧（自動生成 / 手で編集しないこと）", "",
             f"生成日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
             "## ユーザーストーリー", "",
             "| ID | として | したい | なぜなら | 状態 | 受入要求 |",
             "|----|--------|--------|----------|------|----------|"]
    for sid in sorted(reg.stories):
        s = reg.stories[sid]
        lines.append(
            f"| {sid} | {s.get('as_a','')} | {s.get('i_want','')} | {s.get('so_that','')} | "
            f"{STATUS_LABEL.get(s.get('status'), s.get('status',''))} | {_link_list(reg.story_reqs(sid))} |")

    lines += ["", "## 要求", "",
              "| ID | 種別 | 優先度 | 状態 | 要求文 | 理由 | ストーリー | 検証 |",
              "|----|------|--------|------|--------|------|------------|------|"]
    for rid in sorted(reg.requirements):
        r = reg.requirements[rid]
        rat = (r.get("rationale") or {}).get("why", "")
        ver = ", ".join(f"{v.get('kind')}:{v.get('ref')}" for v in r.get("verification") or []) or "-"
        lines.append(
            f"| {rid} | {r.get('type','')} | {r.get('priority','')} | "
            f"{STATUS_LABEL.get(r.get('status'), r.get('status',''))} | {r.get('statement','')} | "
            f"{rat} | {_link_list(r.get('stories'))} | {ver} |")

    retired = [rid for rid in sorted(reg.requirements)
               if reg.requirements[rid].get("status") in RETIRED_STATUS]
    if retired:
        lines += ["", "## 廃止・置換された要求（墓標）", "",
                  "| ID | 要求文 | 状態 | 廃止理由 | 置換先 |",
                  "|----|--------|------|----------|--------|"]
        sup_by = {}
        for rid, r in reg.requirements.items():
            for old in r.get("supersedes") or []:
                sup_by.setdefault(old, []).append(rid)
        for rid in retired:
            r = reg.requirements[rid]
            lines.append(
                f"| {rid} | {r.get('statement','')} | {STATUS_LABEL.get(r.get('status'))} | "
                f"{(r.get('rationale') or {}).get('retired_why','')} | {_link_list(sup_by.get(rid))} |")
    return "\n".join(lines) + "\n"


def gen_traceability(reg: Registry) -> str:
    lines = ["# トレーサビリティマトリクス（自動生成 / 手で編集しないこと）", "",
             "ユーザーストーリー → 要求 → 検証手段。テストの合格条件はこの表がすべて埋まっていること。", "",
             "| ストーリー | 要求 | 要求文 | 検証手段 |",
             "|------------|------|--------|----------|"]
    covered: set[str] = set()
    for sid in sorted(reg.stories):
        acc = reg.story_reqs(sid)
        if not acc:
            lines.append(f"| {sid} | (なし) | - | **未定義** |")
            continue
        for rid in acc:
            covered.add(rid)
            r = reg.requirements.get(rid, {})
            ver = ", ".join(f"{v.get('kind')}:{v.get('ref')}" for v in r.get("verification") or []) or "**未定義**"
            lines.append(f"| {sid} | {rid} | {r.get('statement','')} | {ver} |")

    orphans = [rid for rid, r in sorted(reg.requirements.items())
               if r.get("status") == "active" and rid not in covered]
    lines += ["", "## ストーリー未紐付けの有効要求", ""]
    lines += [f"- {rid}: {reg.requirements[rid].get('statement','')}" for rid in orphans] or ["- なし"]

    active = [r for r in reg.requirements.values() if r.get("status") == "active"]
    verified = [r for r in active if r.get("verification")]
    rate = f"{len(verified)}/{len(active)}" if active else "0/0"
    pct = f"{len(verified) / len(active) * 100:.0f}%" if active else "-"
    lines += ["", "## カバレッジ", "", f"- 検証手段が定義された有効要求: {rate}（{pct}）"]
    return "\n".join(lines) + "\n"


def gen_graph(reg: Registry) -> str:
    lines = ["# 要求関係グラフ（自動生成 / 手で編集しないこと）", "", "```mermaid", "graph LR"]
    for sid in sorted(reg.stories):
        lines.append(f'  {sid.replace("-", "_")}(["{sid}"])')
    for rid in sorted(reg.requirements):
        r = reg.requirements[rid]
        node = rid.replace("-", "_")
        if r.get("status") in RETIRED_STATUS:
            lines.append(f'  {node}["{rid} (廃止)"]')
        else:
            lines.append(f'  {node}["{rid}"]')
    for sid in sorted(reg.stories):
        for rid in reg.story_reqs(sid, live_only=False):
            lines.append(f'  {sid.replace("-", "_")} --> {rid.replace("-", "_")}')
    for rid, r in sorted(reg.requirements.items()):
        node = rid.replace("-", "_")
        for dep in r.get("depends_on") or []:
            lines.append(f'  {node} -.依存.-> {dep.replace("-", "_")}')
        for old in r.get("supersedes") or []:
            lines.append(f'  {old.replace("-", "_")} ==置換==> {node}')
        for other in r.get("conflicts_with") or []:
            if rid < other:
                lines.append(f'  {node} <-.衝突許容.-> {other.replace("-", "_")}')
    lines.append("```")
    return "\n".join(lines) + "\n"


def run_generate(reg: Registry, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, content in (("index.md", gen_index(reg)),
                          ("traceability.md", gen_traceability(reg)),
                          ("graph.md", gen_graph(reg))):
        path = out_dir / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


# --------------------------------------------------------------------------
# impact
# --------------------------------------------------------------------------

def run_impact(reg: Registry, target: str) -> int:
    if target not in reg.requirements and target not in reg.stories:
        sys.stderr.write(f"ID が見つかりません: {target}\n")
        return 1

    print(f"# 影響範囲: {target}")
    if target in reg.stories:
        s = reg.stories[target]
        acc = reg.story_reqs(target, live_only=False)
        print(f"\n## ストーリー\n- {s.get('as_a')} として {s.get('i_want')}（{s.get('so_that')}）")
        print(f"- 受入要求: {_link_list(acc)}")
        for rid in acc:
            r = reg.requirements.get(rid, {})
            print(f"  - {rid}: {r.get('statement','')}")
        return 0

    r = reg.requirements[target]
    print(f"\n## 対象要求\n- 要求文: {r.get('statement')}")
    print(f"- 状態: {r.get('status')} / 優先度: {r.get('priority')} / 種別: {r.get('type')}")
    print(f"- 理由: {(r.get('rationale') or {}).get('why','')}")
    print(f"- 定義元: {reg.sources.get(target)}")

    dependents = sorted(rid for rid, x in reg.requirements.items()
                        if target in (x.get("depends_on") or []) + (x.get("refines") or []))
    print("\n## この要求に依存している要求（変更時に壊れる側）")
    print("\n".join(f"- {rid}: {reg.requirements[rid].get('statement','')}" for rid in dependents) or "- なし")

    print("\n## この要求が依存している要求")
    deps = (r.get("depends_on") or []) + (r.get("refines") or [])
    print("\n".join(f"- {d}: {reg.requirements.get(d, {}).get('statement','')}" for d in deps) or "- なし")

    stories = sorted(r.get("stories") or [])
    print("\n## 関連ユーザーストーリー")
    print("\n".join(f"- {sid}: {reg.stories.get(sid, {}).get('i_want','')}" for sid in stories) or "- なし")

    print("\n## 検証手段（変更時に更新が必要なテスト）")
    print("\n".join(f"- {v.get('kind')}: {v.get('ref')}" for v in r.get("verification") or []) or "- なし")

    subjects = {m.get("subject") for m in r.get("measures") or []}
    siblings = sorted(rid for rid, x in reg.requirements.items()
                      if rid != target and subjects & {m.get("subject") for m in x.get("measures") or []})
    print("\n## 同じ測定対象を持つ要求（数値矛盾が起きやすい相手）")
    print("\n".join(f"- {rid}" for rid in siblings) or "- なし")

    print("\n## 許容済みの衝突相手")
    print("\n".join(f"- {c}" for c in r.get("conflicts_with") or []) or "- なし")
    return 0


# --------------------------------------------------------------------------
# next-id / stats
# --------------------------------------------------------------------------

def run_next_id(reg: Registry, kind: str) -> int:
    if kind == "req":
        nums = [int(rid.split("-")[1]) for rid in reg.requirements if REQ_ID_RE.match(rid)]
        print(f"REQ-{max(nums, default=0) + 1:04d}")
    else:
        nums = [int(sid.split("-")[1]) for sid in reg.stories if US_ID_RE.match(sid)]
        print(f"US-{max(nums, default=0) + 1:03d}")
    return 0


def run_stats(reg: Registry) -> int:
    counts: dict[str, int] = {}
    for r in reg.requirements.values():
        counts[r.get("status", "?")] = counts.get(r.get("status", "?"), 0) + 1
    print(f"要求: {len(reg.requirements)} 件")
    for status in sorted(counts):
        print(f"  {status}: {counts[status]}")
    print(f"ストーリー: {len(reg.stories)} 件")
    print(f"用語: {len(reg.terms)} 件")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="要求レジストリの検証・生成・影響分析")
    parser.add_argument("--dir", default="docs/requirements", help="レジストリのルート（既定: docs/requirements）")
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="構造・参照・矛盾を検査する")
    p_val.add_argument("--strict", action="store_true", help="警告もエラー扱いにする")
    p_val.add_argument("--json", action="store_true", help="JSON で出力する")
    p_val.add_argument("--check-tests", action="store_true", help="verification が指すテストファイルの存在も確認する")
    p_val.add_argument("--repo-root", default=".", help="テストファイル存在確認の基準ディレクトリ")

    p_gen = sub.add_parser("generate", help="index/traceability/graph を生成する")
    p_gen.add_argument("--out", default=None, help="出力先（既定: <dir>/generated）")

    p_imp = sub.add_parser("impact", help="影響範囲を出力する")
    p_imp.add_argument("id", help="REQ-XXXX または US-XXX")

    p_nid = sub.add_parser("next-id", help="次のIDを出力する")
    p_nid.add_argument("kind", choices=["req", "us"])

    sub.add_parser("stats", help="件数サマリを出力する")

    args = parser.parse_args(argv)
    root = Path(args.dir)
    reg = load_registry(root)

    if args.command == "validate":
        findings = run_validate(reg, args.check_tests, Path(args.repo_root))
        if args.json:
            print(json.dumps({
                "requirements": len(reg.requirements),
                "stories": len(reg.stories),
                "findings": findings,
            }, ensure_ascii=False, indent=2))
        else:
            print_findings(findings, reg)
        if any(f["level"] == LEVEL_ERROR for f in findings):
            return 1
        if args.strict and any(f["level"] == LEVEL_WARN for f in findings):
            return 2
        return 0

    if args.command == "generate":
        out_dir = Path(args.out) if args.out else root / "generated"
        for path in run_generate(reg, out_dir):
            print(f"生成: {path}")
        return 0

    if args.command == "impact":
        return run_impact(reg, args.id)

    if args.command == "next-id":
        return run_next_id(reg, args.kind)

    if args.command == "stats":
        return run_stats(reg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
