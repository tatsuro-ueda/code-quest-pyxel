"""raw tasknote から deterministic な ingest 材料を返す helper。

このファイルに含まれる関数・クラス：

- prepare_raw_tasknote: raw tasknote file を読み、JSON 互換 payload を返す
- prepare_tasknote_material: tasknote text と論理 path から payload を返す
- main: CLI で payload JSON を stdout へ流す

Problems:
    - raw tasknote ingest の入口が LLM 任せだと、section 抽出や path 派生が
      毎回ぶれ、related page 推薦や summary scaffold 生成の前処理が不安定になる。
    - shared helper 不在環境で wrapper だけ残ると、repo test が self-import
      で壊れ、local verification ができなくなる。

Solutions:
    - repo 内に最小の deterministic helper を持ち、frontmatter / headings /
      selected sections / derived paths を Python で固定する。
    - adapter.yml による section 名マッピングだけを受け、意味づけや prose は
      後段の LLM に残す。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import yaml


_COMPACT_DATED_STEM_PATTERN = re.compile(
    r"^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})-(?P<slug>.+)$"
)
_HYPHENATED_DATED_STEM_PATTERN = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<slug>.+)$"
)
_SECTION_ORDER = ("Tasklist", "Result", "Discussion", "Closing")
_DEFAULT_SECTION_LABELS = {
    "tasklist": "Tasklist",
    "result": "Result",
    "discussion": "Discussion",
    "closing": "Closing",
}


# === Public API ===


def prepare_raw_tasknote(raw_tasknote_path: Path) -> dict[str, object]:
    """raw tasknote file を読み、deterministic payload を返す。"""
    tasknote_text = raw_tasknote_path.read_text(encoding="utf-8")
    return prepare_tasknote_material(
        tasknote_text,
        logical_raw_tasknote_path=raw_tasknote_path,
    )


def prepare_tasknote_material(
    tasknote_text: str,
    *,
    logical_raw_tasknote_path: Path | str,
) -> dict[str, object]:
    """tasknote text と論理 path から ingest 用 payload を返す。"""
    logical_path = Path(logical_raw_tasknote_path)
    frontmatter, body = _split_frontmatter(tasknote_text)
    headings = _collect_headings(body)
    section_labels = _load_section_labels(logical_path)
    sections = _collect_sections(body, section_labels)
    return {
        "source_id": _derive_source_id(logical_path),
        "summary_draft_path": _derive_summary_draft_path(logical_path).as_posix(),
        "source_type": "tasknote",
        "frontmatter": _make_json_safe(frontmatter),
        "headings": headings,
        "tasklist_items": _extract_tasklist_items(sections.get("Tasklist", [])),
        "result_facts": _normalize_content_lines(sections.get("Result", [])),
        "discussion_points": _normalize_content_lines(
            sections.get("Discussion", [])
        ),
        "closing_points": _normalize_content_lines(sections.get("Closing", [])),
        "missing_sections": _collect_missing_sections(sections),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI で tasknote material を JSON 出力する。"""
    args = _parse_args(argv)
    payload = prepare_raw_tasknote(Path(args.raw_tasknote_path))
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


# === Internal helpers (private) ===


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """CLI 引数を解析する。"""
    parser = argparse.ArgumentParser(
        description="Prepare deterministic ingest material from a raw tasknote.",
    )
    parser.add_argument("raw_tasknote_path")
    return parser.parse_args(argv)


def _split_frontmatter(tasknote_text: str) -> tuple[dict[str, object], str]:
    """frontmatter と本文を分離する。"""
    if not tasknote_text.startswith("---\n"):
        return {}, tasknote_text
    parts = tasknote_text.split("---\n", 2)
    if len(parts) < 3:
        return {}, tasknote_text
    loaded = yaml.safe_load(parts[1]) or {}
    frontmatter = loaded if isinstance(loaded, dict) else {}
    return frontmatter, parts[2]


def _collect_headings(body: str) -> list[str]:
    """本文の level-2 heading 一覧を順序維持で返す。"""
    headings: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            headings.append(line[3:].strip())
    return headings


def _load_section_labels(logical_path: Path) -> dict[str, str]:
    """adapter.yml があれば section 名マッピングを読む。"""
    adapter_path = _find_adapter_path(logical_path)
    if adapter_path is None:
        return dict(_DEFAULT_SECTION_LABELS)
    loaded = yaml.safe_load(adapter_path.read_text(encoding="utf-8")) or {}
    required = loaded.get("tasknote_required_sections", {})
    if not isinstance(required, dict):
        return dict(_DEFAULT_SECTION_LABELS)
    section_labels = dict(_DEFAULT_SECTION_LABELS)
    for key in ("tasklist", "result", "discussion", "closing"):
        value = required.get(key)
        if isinstance(value, str) and value.strip():
            section_labels[key] = value.strip()
    return section_labels


def _find_adapter_path(logical_path: Path) -> Path | None:
    """論理 path から `llm-wiki/adapter.yml` を探索する。"""
    if logical_path.is_absolute():
        start_path = logical_path
    else:
        start_path = (Path.cwd() / logical_path).resolve()
    for parent in (start_path, *start_path.parents):
        candidate = parent / "adapter.yml"
        if candidate.exists():
            return candidate
        if parent.name == "llm-wiki":
            candidate = parent / "adapter.yml"
            if candidate.exists():
                return candidate
    return None


def _collect_sections(
    body: str,
    section_labels: dict[str, str],
) -> dict[str, list[str]]:
    """本文を canonical section ごとの行リストへまとめる。"""
    sections: dict[str, list[str]] = {}
    current_name: str | None = None
    for line in body.splitlines():
        if line.startswith("## "):
            current_name = _match_section_name(line[3:].strip(), section_labels)
            if current_name is not None:
                sections.setdefault(current_name, [])
            continue
        if current_name is None:
            continue
        sections[current_name].append(line)
    return sections


def _match_section_name(
    raw_heading: str,
    section_labels: dict[str, str],
) -> str | None:
    """raw heading を canonical section 名へ寄せる。"""
    normalized = _normalize_heading_label(raw_heading)
    for key, label in section_labels.items():
        if normalized == _normalize_heading_label(label):
            return key.capitalize()
    return None


def _normalize_heading_label(label: str) -> str:
    """番号付き heading を section 名へ正規化する。"""
    stripped = re.sub(r"^\d+\)\s*", "", label).strip()
    return re.sub(r"[（(].*$", "", stripped).strip()


def _extract_tasklist_items(lines: list[str]) -> list[str]:
    """Tasklist section から checklist 項目だけを返す。"""
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("- ["):
            continue
        normalized = re.sub(r"^- \[[ xX]\]\s*", "", stripped).strip()
        if normalized:
            items.append(normalized)
    return items


def _normalize_content_lines(lines: list[str]) -> list[str]:
    """section 本文から空行・subheading を除き、箇条書き記号を落として返す。"""
    normalized_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("### "):
            continue
        stripped = re.sub(r"^- \[[ xX]\]\s*", "", stripped)
        stripped = re.sub(r"^-+\s*", "", stripped).strip()
        if stripped:
            normalized_lines.append(stripped)
    return normalized_lines


def _collect_missing_sections(sections: dict[str, list[str]]) -> list[str]:
    """不足している canonical section 名を固定順で返す。"""
    return [name for name in _SECTION_ORDER if name not in sections]


def _derive_source_id(logical_path: Path) -> str:
    """file stem から source_id を返す。"""
    stem = logical_path.stem
    compact = _COMPACT_DATED_STEM_PATTERN.match(stem)
    if compact is not None:
        return (
            f"{compact.group('year')}-{compact.group('month')}-{compact.group('day')}"
            f"-{compact.group('slug')}"
        )
    hyphenated = _HYPHENATED_DATED_STEM_PATTERN.match(stem)
    if hyphenated is not None:
        return stem
    return stem


def _derive_summary_draft_path(logical_path: Path) -> Path:
    """raw tasknote path に対応する summary draft path を返す。"""
    parts = list(logical_path.parts)
    marker = ("llm-wiki", "raw", "tasknotes")
    for index in range(len(parts) - len(marker) + 1):
        if tuple(parts[index:index + len(marker)]) == marker:
            suffix = parts[index + len(marker):]
            return Path(
                *parts[:index],
                "llm-wiki",
                "wiki",
                "summaries",
                "tasknotes",
                *suffix[:-1],
                f"{logical_path.stem}-summary.md",
            )
    return Path(
        "llm-wiki",
        "wiki",
        "summaries",
        "tasknotes",
        f"{logical_path.stem}-summary.md",
    )


def _make_json_safe(value: object) -> object:
    """datetime/date を含む frontmatter を JSON 安全な shape へ寄せる。"""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {
            str(key): _make_json_safe(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_make_json_safe(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
