"""raw tasknote ingest 用の決定的な材料を JSON で返す CLI。

Problems:
    - `llm-wiki-capture-and-ingest-source` の tasknote flow では、
      `source_id` や summary draft path、section 材料抽出を毎回手で揃えている。
    - 同じ raw tasknote を読んでも、AI ごとに材料の並びや不足判定がぶれやすい。

Solutions:
    - raw tasknote から frontmatter、見出し、Tasklist、Discussion 系材料を
      決定的に抽出する helper を 1 本にまとめる。
    - CLI は JSON だけを返し、要約や意味づけは AI 側へ残す。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import yaml


_TASKNOTE_ROOT = ("llm-wiki", "raw", "tasknotes")
_SUMMARY_ROOT = ("llm-wiki", "wiki", "summaries", "tasknotes")
_REQUIRED_SECTIONS = ("Result", "Discussion", "Closing")
_HEADING_PATTERN = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_SECTION_PATTERN = re.compile(r"^##\s+(.+?)\s*$")
_DATED_STEM_PATTERN = re.compile(r"^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})-(?P<slug>.+)$")


# === Public API ===


def prepare_raw_tasknote(raw_tasknote_path: Path) -> dict[str, object]:
    """raw tasknote を読み、ingest 前半で使う構造化材料を返す。

    Args:
        raw_tasknote_path: `llm-wiki/raw/tasknotes/...` 配下の markdown path。

    Returns:
        source_id と summary draft path を含む JSON 互換 dict。

    Policy:
        - 欠けた section は捏造せず空配列と `missing_sections` で返す。
        - 要約文や quote 候補はこの helper で生成しない。
    """
    text = raw_tasknote_path.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(text)
    sections = _collect_sections(body)
    return {
        "source_id": _derive_source_id(raw_tasknote_path),
        "summary_draft_path": _derive_summary_draft_path(raw_tasknote_path),
        "source_type": "tasknote",
        "frontmatter": frontmatter,
        "headings": _collect_headings(body),
        "tasklist_items": _extract_tasklist_items(sections.get("Tasklist", [])),
        "result_facts": _normalize_lines(sections.get("Result", [])),
        "discussion_points": _normalize_lines(sections.get("Discussion", [])),
        "closing_points": _normalize_lines(sections.get("Closing", [])),
        "missing_sections": _collect_missing_sections(sections),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI で raw tasknote helper を実行して JSON を標準出力へ流す。"""
    args = _parse_args(argv)
    payload = prepare_raw_tasknote(Path(args.raw_tasknote_path))
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


# === Internal helpers (private) ===


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """CLI 引数を解析する。"""
    parser = argparse.ArgumentParser(
        description="Prepare deterministic JSON materials from a raw tasknote.",
    )
    parser.add_argument("raw_tasknote_path", help="Path under llm-wiki/raw/tasknotes/")
    return parser.parse_args(argv)


def _split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """frontmatter を dict と本文に分離する。"""
    if not text.startswith("---\n"):
        return {}, text

    _, frontmatter_block, body = text.split("---\n", 2)
    frontmatter = yaml.safe_load(frontmatter_block) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError("frontmatter must be a mapping")
    return _make_json_safe(frontmatter), body


def _derive_source_id(raw_tasknote_path: Path) -> str:
    """raw tasknote の stem から `YYYY-MM-DD-slug` を作る。"""
    stem = raw_tasknote_path.stem
    matched = _DATED_STEM_PATTERN.match(stem)
    if not matched:
        return stem
    return (
        f"{matched.group('year')}-{matched.group('month')}-"
        f"{matched.group('day')}-{matched.group('slug')}"
    )


def _derive_summary_draft_path(raw_tasknote_path: Path) -> str:
    """raw tasknote path を summary draft path へ変換する。"""
    subtree_parts = _extract_tasknote_subtree_parts(raw_tasknote_path)
    summary_file_name = f"{Path(subtree_parts[-1]).stem}-summary.md"
    summary_parts = _SUMMARY_ROOT + subtree_parts[:-1] + (summary_file_name,)
    return Path(*summary_parts).as_posix()


def _extract_tasknote_subtree_parts(raw_tasknote_path: Path) -> tuple[str, ...]:
    """`llm-wiki/raw/tasknotes/` から先の subtree を取り出す。"""
    parts = raw_tasknote_path.parts
    root_length = len(_TASKNOTE_ROOT)
    for index in range(len(parts) - root_length + 1):
        if parts[index:index + root_length] == _TASKNOTE_ROOT:
            return parts[index + root_length:]
    raise ValueError(
        f"raw tasknote path must be under {'/'.join(_TASKNOTE_ROOT)}: "
        f"{raw_tasknote_path}"
    )


def _collect_headings(body: str) -> list[str]:
    """本文中の level 2 以上の heading text を順番どおり返す。"""
    headings: list[str] = []
    for line in body.splitlines():
        matched = _HEADING_PATTERN.match(line)
        if matched:
            headings.append(matched.group(2).strip())
    return headings


def _collect_sections(body: str) -> dict[str, list[str]]:
    """level 2 section ごとの本文行を集める。"""
    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    for line in body.splitlines():
        matched = _SECTION_PATTERN.match(line)
        if matched:
            current_section = _normalize_section_name(matched.group(1))
            sections.setdefault(current_section, [])
            continue
        if current_section is not None:
            sections[current_section].append(line)
    return sections


def _normalize_section_name(heading: str) -> str:
    """`4) Tasklist` のような heading から section 名だけを抜く。"""
    stripped = heading.strip()
    matched = re.match(r"^\d+[\.\)]\s*(.+)$", stripped)
    if matched:
        stripped = matched.group(1).strip()
    if "Tasklist" in stripped:
        return "Tasklist"
    if "Discussion" in stripped:
        return "Discussion"
    if "Closing" in stripped:
        return "Closing"
    if "Result" in stripped:
        return "Result"
    return stripped


def _extract_tasklist_items(lines: list[str]) -> list[str]:
    """Tasklist section の checkbox 行だけを整形して返す。"""
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^- \[[ xX]\] ", stripped):
            items.append(_strip_list_marker(stripped))
    return items


def _normalize_lines(lines: list[str]) -> list[str]:
    """section 本文から要点候補になりうる行だけを抜く。"""
    normalized: list[str] = []
    in_code_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not stripped:
            continue
        if stripped == "---" or stripped.startswith("%%"):
            continue
        if stripped.startswith("### "):
            continue
        if _is_mermaid_noise(stripped):
            continue
        normalized.append(_strip_list_marker(stripped))
    return normalized


def _is_mermaid_noise(stripped: str) -> bool:
    """mermaid block の制御行や class 定義行を弾く。"""
    mermaid_prefixes = (
        "flowchart ",
        "subgraph ",
        "classDef ",
        "class ",
    )
    return (
        stripped in {"mermaid", "end"}
        or stripped.startswith(mermaid_prefixes)
        or "-->" in stripped
    )


def _strip_list_marker(line: str) -> str:
    """markdown list/quote marker を取り除く。"""
    stripped = re.sub(r"^- \[[ xX]\]\s+", "", line)
    stripped = re.sub(r"^[-*]\s+", "", stripped)
    stripped = re.sub(r"^\d+\.\s+", "", stripped)
    stripped = re.sub(r"^>\s+", "", stripped)
    return stripped.strip()


def _collect_missing_sections(sections: dict[str, list[str]]) -> list[str]:
    """契約対象の required section で欠けているものを返す。"""
    return [section for section in _REQUIRED_SECTIONS if section not in sections]


def _make_json_safe(value: object) -> object:
    """yaml.safe_load の戻り値を JSON serializable な値へ寄せる。"""
    if isinstance(value, dict):
        return {
            str(key): _make_json_safe(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


if __name__ == "__main__":
    raise SystemExit(main())
