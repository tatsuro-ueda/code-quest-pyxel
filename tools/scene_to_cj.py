"""コード変更から関連 CJ / カスタマージョブカテゴリへの影響範囲を提示する CLI。

このファイルに含まれる関数・クラス：

- 対応表 JSON を読み込む純粋関数
- git diff --name-only から変更ファイル一覧を取得するヘルパ
- 変更ファイル一覧から scene 名 / area 名を抽出する純粋関数
- customer-journeys.md から CJ ID → カテゴリを引く純粋関数（verify_cj_cjob と同じロジック）
- 対応表中の CJ ID が customer-journeys.md に実在することを検証する関数
- main：--list / --since の 2 モードを切り替える
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


CJ_HEADING_RE = re.compile(r"^### (CJ\d+):", re.MULTILINE)
CATEGORY_LINE_RE = re.compile(r"該当カテゴリ：(.+?)→", re.DOTALL)


def load_map(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def changed_files(since: str) -> list[str]:
    """`git diff --name-only <since> HEAD` の結果を返す。"""
    out = subprocess.run(
        ["git", "diff", "--name-only", since, "HEAD"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        return []
    return [l for l in out.stdout.splitlines() if l.strip()]


def extract_scenes_and_areas(files: list[str], scene_keys: list[str], area_keys: list[str]
                              ) -> tuple[set[str], set[str]]:
    """変更ファイルから scene 名と area 名を抽出する。"""
    scenes: set[str] = set()
    areas: set[str] = set()
    for f in files:
        parts = f.split("/")
        if len(parts) >= 3 and parts[0] == "src" and parts[1] == "scenes":
            scene = parts[2]
            if scene in scene_keys:
                scenes.add(scene)
        if len(parts) >= 2 and parts[0] == "src":
            area = parts[1]
            if area in area_keys:
                areas.add(area)
    return scenes, areas


def collect_cj_categories(journey_md: Path) -> dict[str, list[str]]:
    """customer-journeys.md から CJ ID -> カテゴリトークンのリストを抽出する。"""
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


def verify_map_against_journey(mapping: dict, journey_md: Path) -> list[str]:
    """対応表中の CJ ID が customer-journeys.md に実在するかを検証し、欠損リストを返す。"""
    text = journey_md.read_text(encoding="utf-8")
    headings = set(CJ_HEADING_RE.findall(text))
    missing: list[str] = []
    for group_name in ("scenes", "areas"):
        for key, cjs in mapping.get(group_name, {}).items():
            for cj in cjs:
                if cj not in headings:
                    missing.append(f"{group_name}.{key} -> {cj}")
    return missing


def print_for_keys(label: str, keys: set[str], mapping: dict, group: str,
                   cj_categories: dict[str, list[str]]) -> None:
    """label と key 群について、対応する CJ + カテゴリを stdout に出す。"""
    if not keys:
        return
    print(f"## {label}")
    for key in sorted(keys):
        cjs = mapping.get(group, {}).get(key, [])
        print(f"- {key} → {', '.join(cjs) if cjs else '(no CJ mapped)'}")
        for cj in cjs:
            cats = cj_categories.get(cj, [])
            cats_str = ", ".join(cats) if cats else "(no categories)"
            print(f"    {cj}: {cats_str}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--map", type=Path, default=Path("tools/scene_to_cj.json"),
                        help="対応表 JSON")
    parser.add_argument("--journey", type=Path, default=Path("docs/customer-journeys.md"))
    parser.add_argument("--list", action="store_true",
                        help="全 scene / area の対応表を一覧表示する")
    parser.add_argument("--since", type=str, default=None,
                        help="この commit-ish から HEAD までの差分から影響範囲を出す（例: HEAD~1）")
    parser.add_argument("--verify-only", action="store_true",
                        help="対応表の CJ ID が customer-journeys.md に実在するかだけ検証する")
    args = parser.parse_args(argv)

    if not args.map.is_file():
        print(f"map file not found: {args.map}", file=sys.stderr)
        return 2

    mapping = load_map(args.map)

    missing = verify_map_against_journey(mapping, args.journey)
    if missing:
        for m in missing:
            print(f"map references missing CJ: {m}", file=sys.stderr)
        if args.verify_only:
            return 1

    if args.verify_only:
        print("scene_to_cj map OK", file=sys.stdout)
        return 0

    cj_categories = collect_cj_categories(args.journey)

    if args.list:
        print_for_keys("scenes", set(mapping.get("scenes", {}).keys()), mapping, "scenes", cj_categories)
        print_for_keys("areas", set(mapping.get("areas", {}).keys()), mapping, "areas", cj_categories)
        if missing:
            return 1
        return 0

    if args.since:
        files = changed_files(args.since)
        scenes, areas = extract_scenes_and_areas(
            files,
            list(mapping.get("scenes", {}).keys()),
            list(mapping.get("areas", {}).keys()),
        )
        if not scenes and not areas:
            print(f"no relevant scene / area changes since {args.since}", file=sys.stdout)
            return 0
        print_for_keys("changed scenes", scenes, mapping, "scenes", cj_categories)
        print_for_keys("changed areas", areas, mapping, "areas", cj_categories)
        if missing:
            return 1
        return 0

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
