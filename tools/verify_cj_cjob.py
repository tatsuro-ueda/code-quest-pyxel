"""タスクノートと customer-journeys.md / customer-jobs.md の整合を検証する CLI。

このファイルに含まれる関数・クラス：

- steering/*.md から CJ ID 集合を抽出する純粋関数
- customer-journeys.md から見出し ID 集合を抽出する純粋関数
- customer-journeys.md の各 CJ セクションから「該当カテゴリ」表記を抽出する純粋関数
- customer-jobs.md にカテゴリトークンが存在するかを判定する純粋関数
- main：引数解析・走査・exit code 制御
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CJ_ID_RE = re.compile(r"\bCJ\d+\b")
CJ_HEADING_RE = re.compile(r"^### (CJ\d+):", re.MULTILINE)
CATEGORY_LINE_RE = re.compile(r"該当カテゴリ：(.+?)→", re.DOTALL)
# 全角丸数字 ① 〜 ⑨（必要なら ⑩+ も拾えるよう範囲拡張）
CIRCLED_DIGIT_RE = re.compile(r"[①-⑳]")


def strip_code_blocks(text: str) -> str:
    """Markdown のコードブロック（``` フェンス）とインラインコード（` 単独）を除去する。

    Gherkin 例文として書いた CJ999、または `rg "CJ4[0-2]"` のような正規表現片からの
    false positive を防ぐ。
    """
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`\n]+`", "", text)
    return text


def collect_cj_ids_from_notes(steering_dir: Path) -> dict[str, set[Path]]:
    """steering/*.md から CJ ID を抽出し、CJ ID -> 出現したファイル集合 を返す。

    Gherkin 例文の false positive を避けるため、コードブロック内の CJ ID は除外する。
    """
    out: dict[str, set[Path]] = {}
    for md in sorted(steering_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        text_no_code = strip_code_blocks(text)
        for cj in set(CJ_ID_RE.findall(text_no_code)):
            out.setdefault(cj, set()).add(md)
    return out


def collect_cj_headings(journey_md: Path) -> set[str]:
    """customer-journeys.md の見出し集合 (### CJxx:) を返す。"""
    text = journey_md.read_text(encoding="utf-8")
    return set(CJ_HEADING_RE.findall(text))


def collect_cj_categories(journey_md: Path) -> dict[str, list[str]]:
    """customer-journeys.md から CJ ID -> カテゴリトークン（丸数字含む文字列）のリスト を抽出する。"""
    text = journey_md.read_text(encoding="utf-8")
    sections = re.split(r"^### ", text, flags=re.MULTILINE)
    out: dict[str, list[str]] = {}
    for sec in sections:
        m = re.match(r"(CJ\d+):", sec)
        if not m:
            continue
        cj = m.group(1)
        cats: list[str] = []
        for catline in CATEGORY_LINE_RE.findall(sec):
            for token in re.findall(r"[①-⑳][^,，、]+", catline):
                cats.append(token.strip())
        if cats:
            out[cj] = cats
    return out


def category_exists_in_jobs(category_token: str, jobs_text: str) -> bool:
    """カテゴリトークンが customer-jobs.md 内に登場するかを判定する。

    丸数字部分だけを抽出してマッチングする（後続のカテゴリ名は揺れる可能性があるため）。
    """
    m = CIRCLED_DIGIT_RE.search(category_token)
    if not m:
        return False
    return m.group(0) in jobs_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--steering", type=Path, default=Path("steering"),
                        help="タスクノートのルート（デフォルト: steering）")
    parser.add_argument("--journey", type=Path, default=Path("docs/customer-journeys.md"))
    parser.add_argument("--jobs", type=Path, default=Path("docs/customer-jobs.md"))
    args = parser.parse_args(argv)

    if not args.steering.is_dir():
        print(f"steering directory not found: {args.steering}", file=sys.stderr)
        return 2
    if not args.journey.is_file():
        print(f"customer-journeys.md not found: {args.journey}", file=sys.stderr)
        return 2
    if not args.jobs.is_file():
        print(f"customer-jobs.md not found: {args.jobs}", file=sys.stderr)
        return 2

    cj_in_notes = collect_cj_ids_from_notes(args.steering)
    headings = collect_cj_headings(args.journey)

    fail = 0

    # C1: タスクノート中の CJ ID は customer-journeys.md に実在する
    missing = sorted(set(cj_in_notes.keys()) - headings)
    if missing:
        for cj in missing:
            files = sorted(p.name for p in cj_in_notes[cj])
            print(f"CJ link broken: {cj} not found in customer-journeys.md (referenced by: {', '.join(files)})",
                  file=sys.stderr)
        fail += len(missing)
    else:
        print(f"CJ link OK: {len(cj_in_notes)} unique CJ IDs in steering/, all resolved", file=sys.stdout)

    # C2: 各 CJ の該当カテゴリが customer-jobs.md に実在する
    referenced_cjs = set(cj_in_notes.keys()) & headings
    cj_categories = collect_cj_categories(args.journey)
    jobs_text = args.jobs.read_text(encoding="utf-8")

    cjob_fail = 0
    cjob_checked = 0
    for cj in sorted(referenced_cjs):
        cats = cj_categories.get(cj, [])
        for cat in cats:
            cjob_checked += 1
            if not category_exists_in_jobs(cat, jobs_text):
                print(f"CJob category broken: {cj} 該当カテゴリ {cat!r} not found in customer-jobs.md",
                      file=sys.stderr)
                cjob_fail += 1
    if cjob_fail == 0:
        print(f"CJob category OK: {cjob_checked} category tokens checked", file=sys.stdout)
    fail += cjob_fail

    if fail:
        print(f"FAIL: {fail} integrity issues", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
