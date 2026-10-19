#!/usr/bin/env python3
"""package-skills.py - claude.ai（チャット）へアップロードできるスキルzipを生成する

claude.ai の「設定 > 機能 > スキル」へアップロードするzipは、スキルフォルダを
ルートに持つ必要がある（<skill-name>/SKILL.md ...）。本スクリプトはリポジトリ内の
全スキル（SKILL.mdを持つディレクトリ）を、スキルごとに1つのzipへまとめる。

他スキルへの相対リンク（例: ../ai-code-review/references/x.md）はzip単体では
解決できないため、リンク先ファイルを linked/ 配下へ同梱してリンクを書き換える。
リポジトリ内のファイルは変更しない（書き換えはzip内のコピーにのみ適用）。

使い方:
  python3 scripts/package-skills.py                 # 全スキルを dist/skills/ へ出力
  python3 scripts/package-skills.py task-planning   # 指定スキルのみ
  python3 scripts/package-skills.py --out build/    # 出力先を変更
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"node_modules", ".git", "dist", "__pycache__"}
SKIP_FILES = {".DS_Store"}
SKIP_SUFFIXES = {".pyc"}
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_CHARS = 64
MAX_DESCRIPTION_CHARS = 1024
MAX_ZIP_BYTES = 30 * 1024 * 1024
LINK_RE = re.compile(r"(\]\()([^)\s#]+)((?:#[^)\s]*)?\))")
FIXED_TIME = (2020, 1, 1, 0, 0, 0)  # 再現可能なzipにするため固定


def find_skills() -> list[Path]:
    skills = []
    for skill_md in sorted(ROOT.rglob("SKILL.md")):
        if SKIP_DIRS & set(skill_md.relative_to(ROOT).parts):
            continue
        skills.append(skill_md.parent)
    return skills


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("YAMLフロントマターがありません")
    keys: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            return keys
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            keys[m.group(1)] = m.group(2).strip()
    raise ValueError("YAMLフロントマターが閉じられていません")


def validate(skill_dir: Path) -> list[str]:
    errors = []
    try:
        fm = parse_frontmatter(skill_dir / "SKILL.md")
    except ValueError as e:
        return [str(e)]
    name = fm.get("name", "")
    if name != skill_dir.name:
        errors.append(f"name '{name}' がディレクトリ名 '{skill_dir.name}' と一致しません")
    if not NAME_RE.match(name) or len(name) > MAX_NAME_CHARS:
        errors.append(f"name '{name}' は小文字英数字とハイフンのみ・{MAX_NAME_CHARS}文字以内にしてください")
    desc = fm.get("description", "")
    if not desc:
        errors.append("description がありません")
    elif len(desc) > MAX_DESCRIPTION_CHARS:
        errors.append(f"description が{MAX_DESCRIPTION_CHARS}文字を超えています（{len(desc)}文字）")
    unknown = set(fm) - ALLOWED_FRONTMATTER_KEYS
    if unknown:
        errors.append(f"claude.aiが受け付けないフロントマターキー: {sorted(unknown)}")
    return errors


def iter_files(skill_dir: Path):
    for path in sorted(skill_dir.rglob("*")):
        rel = path.relative_to(skill_dir)
        if not path.is_file() or SKIP_DIRS & set(rel.parts):
            continue
        if path.name in SKIP_FILES or path.suffix in SKIP_SUFFIXES:
            continue
        yield path, rel


def rewrite_links(skill_dir: Path, path: Path, rel: Path, text: str, linked: dict[Path, Path], warnings: list[str]) -> str:
    """スキル外を指す相対リンクを、同梱先(linked/)への相対リンクへ書き換える。"""

    def repl(m: re.Match) -> str:
        target = m.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("/"):
            return m.group(0)
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(skill_dir.resolve())
            return m.group(0)  # スキル内リンクはそのまま
        except ValueError:
            pass
        if not resolved.is_file():
            return m.group(0)  # コード例中のサンプルリンク等は対象外
        if not resolved.is_relative_to(skill_dir.parent.resolve()):
            warnings.append(f"{rel}: 同梱対象外のリンク（カテゴリ外）: {target}")
            return m.group(0)
        bundled = Path("linked") / resolved.relative_to(skill_dir.parent.resolve())
        linked[bundled] = resolved
        new_target = Path(*([".."] * len(rel.parent.parts))) / bundled if rel.parent.parts else bundled
        return f"{m.group(1)}{new_target.as_posix()}{m.group(3)}"

    return LINK_RE.sub(repl, text)


def build_zip(skill_dir: Path, out_dir: Path) -> tuple[Path, list[str]]:
    name = skill_dir.name
    warnings: list[str] = []
    entries: dict[str, bytes] = {}
    linked: dict[Path, Path] = {}

    for path, rel in iter_files(skill_dir):
        data = path.read_bytes()
        if path.suffix == ".md":
            data = rewrite_links(skill_dir, path, rel, data.decode("utf-8"), linked, warnings).encode("utf-8")
        entries[f"{name}/{rel.as_posix()}"] = data

    for bundled, source in sorted(linked.items()):
        entries.setdefault(f"{name}/{bundled.as_posix()}", source.read_bytes())

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname in sorted(entries):
            info = zipfile.ZipInfo(arcname, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, entries[arcname])
    if zip_path.stat().st_size > MAX_ZIP_BYTES:
        warnings.append(f"zipが{MAX_ZIP_BYTES // 1024 // 1024}MBを超えています")
    return zip_path, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="claude.aiアップロード用のスキルzipを生成する")
    parser.add_argument("skills", nargs="*", help="対象スキル名（省略時は全スキル）")
    parser.add_argument("--out", default="dist/skills", help="出力先ディレクトリ（既定: dist/skills）")
    args = parser.parse_args()

    skills = find_skills()
    if args.skills:
        by_name = {s.name: s for s in skills}
        missing = [n for n in args.skills if n not in by_name]
        if missing:
            print(f"[ERR]  スキルが見つかりません: {', '.join(missing)}", file=sys.stderr)
            return 1
        skills = [by_name[n] for n in args.skills]

    out_dir = (ROOT / args.out) if not Path(args.out).is_absolute() else Path(args.out)
    failed = 0
    for skill_dir in skills:
        rel = skill_dir.relative_to(ROOT)
        errors = validate(skill_dir)
        if errors:
            failed += 1
            for e in errors:
                print(f"[ERR]  {rel}: {e}")
            continue
        zip_path, warnings = build_zip(skill_dir, out_dir)
        print(f"[OK]   {rel} -> {zip_path.relative_to(ROOT) if zip_path.is_relative_to(ROOT) else zip_path} ({zip_path.stat().st_size // 1024}KB)")
        for w in warnings:
            print(f"[WARN] {rel}: {w}")

    print(f"\n{len(skills) - failed}/{len(skills)} スキルのzipを生成しました")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
