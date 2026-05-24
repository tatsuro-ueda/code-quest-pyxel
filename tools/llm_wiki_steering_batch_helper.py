"""steering/done の oldest batch ingest 下ごしらえを返す CLI。

Problems:
    - `steering/done/` から古い未 ingest tasknote を 10 件ずつ選ぶ作業が毎回手作業。
    - summary scaffold、related page 候補、index / log / inbox 追記 block が
      source ごとに少しずつぶれ、LLM の前処理コストが高い。

Solutions:
    - oldest 未 ingest source の選定、summary scaffold、related page shortlist、
      append block を Python helper で決定的に返す。
    - 最終的な意味づけや自然な prose は LLM に残し、helper は下ごしらえだけ行う。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

try:
    from tools.llm_wiki_tasknote_helper import prepare_tasknote_material
except ModuleNotFoundError:  # pragma: no cover - CLI fallback for `python tools/...`
    _SHARED_CORE = Path.home() / "dotfiles/shared/llm-wiki-core/python"
    if str(_SHARED_CORE) not in sys.path:
        sys.path.insert(0, str(_SHARED_CORE))
    from llm_wiki_tasknote_helper import prepare_tasknote_material


_STEERING_DONE_ROOT = ("steering", "done")
_RAW_TARGET_ROOT = ("llm-wiki", "raw", "tasknotes", "steering", "done")
_SUMMARY_TARGET_ROOT = ("llm-wiki", "wiki", "summaries", "tasknotes", "steering", "done")
_AREA_ROOT = ("llm-wiki", "wiki", "areas")
_INGEST_LOG_PATH = ("llm-wiki", "wiki", "logs", "ingest-log.md")
_SOURCE_INBOX_PATH = ("llm-wiki", "wiki", "logs", "source-inbox.md")
_MASTER_INDEX_PATH = ("llm-wiki", "wiki", "indexes", "master-index.md")
_TITLE_PATTERN = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]{2,}|[ぁ-んァ-ン一-龯]{2,}")
_COMPACT_DATED_STEM_PATTERN = re.compile(
    r"^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})-(?P<slug>.+)$"
)
_HYPHENATED_DATED_STEM_PATTERN = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<slug>.+)$"
)
_INDEX_DESCRIPTION_PLACEHOLDER = "TODO_SUMMARY_INDEX_DESCRIPTION"
_RISK_PLACEHOLDER = "TODO_RISK"
_NOTE_PLACEHOLDER = "TODO_NOTE"
_STOPWORDS = {
    "tasknote",
    "summary",
    "draft",
    "done",
    "open",
    "close",
    "closing",
    "discussion",
    "result",
    "tasklist",
    "source",
    "title",
    "today",
    "then",
    "when",
    "given",
}


# === Public API ===


def prepare_steering_done_batch(
    repo_root: Path,
    *,
    limit: int = 10,
    current_date: str | None = None,
) -> dict[str, object]:
    """steering/done oldest batch 用の構造化材料を返す。

    Args:
        repo_root: repo root path。
        limit: 最大選定件数。
        current_date: scaffold / append block 用の日付文字列。

    Returns:
        oldest 未 ingest source、summary scaffold、related page 候補、
        append block を含む JSON 互換 dict。
    """
    today = current_date or date.today().isoformat()
    area_pages = _load_area_pages(repo_root)
    history_weights = _build_history_area_weights(repo_root)
    sources: list[dict[str, object]] = []
    for source_path in _select_oldest_uningested_tasknotes(repo_root, limit):
        steering_text = source_path.read_text(encoding="utf-8")
        raw_target_path = _derive_raw_target_path(source_path)
        material = prepare_tasknote_material(
            steering_text,
            logical_raw_tasknote_path=raw_target_path,
        )
        source_title = _extract_tasknote_title(steering_text, source_path)
        display_label = _build_display_label(material["source_id"])
        related_candidates = _rank_related_pages(
            material,
            source_title=source_title,
            area_pages=area_pages,
            history_weights=history_weights,
        )
        sources.append(
            {
                "source_path": source_path.as_posix(),
                "raw_target_path": raw_target_path.as_posix(),
                "needs_raw_copy": not raw_target_path.exists(),
                **material,
                "source_title": source_title,
                "display_label": display_label,
                "summary_scaffold": _build_summary_scaffold(
                    material=material,
                    source_title=source_title,
                    current_date=today,
                ),
                "related_page_candidates": related_candidates,
                "append_blocks": _build_append_blocks(
                    material=material,
                    display_label=display_label,
                    related_candidates=related_candidates,
                    current_date=today,
                ),
            }
        )
    return {
        "batch_type": "steering_done_oldest_uningested",
        "limit": limit,
        "current_date": today,
        "selected_count": len(sources),
        "sources": sources,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI で steering batch helper を実行して JSON を標準出力へ流す。"""
    args = _parse_args(argv)
    payload = prepare_steering_done_batch(
        Path(args.repo_root),
        limit=args.limit,
        current_date=args.current_date,
    )
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


# === Internal helpers (private) ===


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """CLI 引数を解析する。"""
    parser = argparse.ArgumentParser(
        description=(
            "Prepare oldest un-ingested steering/done tasknotes and deterministic "
            "batch ingest scaffolds."
        ),
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--limit", type=int, default=10, help="Maximum source count")
    parser.add_argument(
        "--current-date",
        default=None,
        help="Optional YYYY-MM-DD date for scaffold metadata",
    )
    return parser.parse_args(argv)


def _select_oldest_uningested_tasknotes(
    repo_root: Path,
    limit: int,
) -> list[Path]:
    """未 ingest の steering/done tasknote を古い順に返す。"""
    steering_dir = repo_root.joinpath(*_STEERING_DONE_ROOT)
    steering_paths = sorted(steering_dir.glob("*.md"), key=lambda path: path.name)
    candidates = [
        path
        for path in steering_paths
        if not repo_root.joinpath(_derive_summary_target_path(path)).exists()
    ]
    candidates.sort(key=_build_sort_key)
    return candidates[:limit]


def _build_sort_key(source_path: Path) -> tuple[str, str]:
    """frontmatter date 優先で oldest sort key を作る。"""
    tasknote_text = source_path.read_text(encoding="utf-8")
    frontmatter = _extract_frontmatter(tasknote_text)
    for key in ("dateCreated", "scheduled", "dateModified"):
        parsed = _parse_datetime_string(frontmatter.get(key))
        if parsed is not None:
            return (parsed.isoformat(), source_path.name)
    stem_date = _parse_date_from_stem(source_path.stem)
    if stem_date is not None:
        return (stem_date.isoformat(), source_path.name)
    return ("9999-12-31T23:59:59+00:00", source_path.name)


def _extract_frontmatter(tasknote_text: str) -> dict[str, object]:
    """frontmatter を mapping として返す。"""
    if not tasknote_text.startswith("---\n"):
        return {}
    _, frontmatter_block, _ = tasknote_text.split("---\n", 2)
    loaded = yaml.safe_load(frontmatter_block) or {}
    if isinstance(loaded, dict):
        return loaded
    return {}


def _parse_datetime_string(value: object) -> datetime | None:
    """frontmatter の日時値を datetime へ寄せる。"""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_date_from_stem(stem: str) -> datetime | None:
    """stem から日付部分だけを抜いて datetime を返す。"""
    for pattern in (_COMPACT_DATED_STEM_PATTERN, _HYPHENATED_DATED_STEM_PATTERN):
        matched = pattern.match(stem)
        if matched:
            return datetime.fromisoformat(
                f"{matched.group('year')}-{matched.group('month')}-{matched.group('day')}T00:00:00"
            )
    return None


def _derive_raw_target_path(source_path: Path) -> Path:
    """steering source を raw/tasknotes/steering/done 側の論理 path へ写す。"""
    return Path(*_RAW_TARGET_ROOT) / source_path.name


def _derive_summary_target_path(source_path: Path) -> Path:
    """steering source に対応する summary path を返す。"""
    return Path(*_SUMMARY_TARGET_ROOT) / f"{source_path.stem}-summary.md"


def _extract_tasknote_title(tasknote_text: str, source_path: Path) -> str:
    """最初の H1 から tasknote title を返す。"""
    matched = _TITLE_PATTERN.search(tasknote_text)
    if matched:
        return matched.group(1).strip()
    return _build_display_label(_derive_source_id_from_stem(source_path.stem))


def _load_area_pages(repo_root: Path) -> list[dict[str, object]]:
    """area page 群の path / title / token set を読む。"""
    area_dir = repo_root.joinpath(*_AREA_ROOT)
    area_pages: list[dict[str, object]] = []
    for area_path in sorted(area_dir.glob("*.md")):
        area_text = area_path.read_text(encoding="utf-8")
        relative_path = area_path.relative_to(repo_root).as_posix()
        area_pages.append(
            {
                "path": relative_path,
                "title": _extract_tasknote_title(area_text, area_path),
                "tokens": _collect_tokens(area_path.stem + " " + area_text),
            }
        )
    return area_pages


def _build_history_area_weights(
    repo_root: Path,
) -> dict[str, dict[str, float]]:
    """既存 ingest log から token -> area score の履歴重みを作る。"""
    ingest_log_path = repo_root.joinpath(*_INGEST_LOG_PATH)
    if not ingest_log_path.exists():
        return {}

    token_weights: dict[str, dict[str, float]] = {}
    for entry in _parse_ingest_log_entries(ingest_log_path.read_text(encoding="utf-8")):
        source_tokens = _collect_tokens(f"{entry['source_id']} {entry['title']}")
        for token in source_tokens:
            for area_path in entry["updated_area_paths"]:
                area_scores = token_weights.setdefault(token, {})
                area_scores[area_path] = area_scores.get(area_path, 0.0) + 1.0
    return token_weights


def _parse_ingest_log_entries(log_text: str) -> list[dict[str, object]]:
    """ingest log から source_id と updated area path を抜く。"""
    entries: list[dict[str, object]] = []
    current_entry: dict[str, object] | None = None
    in_updated_pages = False
    for line in log_text.splitlines():
        if line.startswith("## [") and " ingest | " in line:
            if current_entry is not None:
                entries.append(current_entry)
            current_entry = {
                "title": line.split(" ingest | ", 1)[1].strip(),
                "source_id": "",
                "updated_area_paths": [],
            }
            in_updated_pages = False
            continue
        if current_entry is None:
            continue
        if line.startswith("- source_id: `"):
            current_entry["source_id"] = line.split("`", 2)[1]
            continue
        if line.startswith("- updated_pages:"):
            in_updated_pages = True
            continue
        if line.startswith("- ") and not line.startswith("  - "):
            in_updated_pages = False
        if in_updated_pages and line.startswith("  - `"):
            updated_path = line.split("`", 2)[1]
            if "/areas/" in updated_path:
                current_entry["updated_area_paths"].append(updated_path)
    if current_entry is not None:
        entries.append(current_entry)
    return entries


def _rank_related_pages(
    material: dict[str, object],
    *,
    source_title: str,
    area_pages: list[dict[str, object]],
    history_weights: dict[str, dict[str, float]],
) -> list[dict[str, object]]:
    """history と text overlap から related area page 候補を返す。"""
    source_tokens = _collect_source_tokens(material, source_title)
    scored_candidates: list[dict[str, object]] = []
    for area_page in area_pages:
        history_score, history_tokens = _score_history_overlap(
            source_tokens,
            history_weights,
            area_page["path"],
        )
        lexical_tokens = sorted(source_tokens & area_page["tokens"])
        lexical_score = 0.25 * len(lexical_tokens)
        total_score = history_score + lexical_score
        if total_score <= 0:
            continue
        scored_candidates.append(
            {
                "path": area_page["path"],
                "title": area_page["title"],
                "score": round(total_score, 2),
                "reason": _build_candidate_reason(history_tokens, lexical_tokens),
            }
        )
    scored_candidates.sort(key=lambda item: (-item["score"], item["path"]))
    return scored_candidates[:4]


def _collect_source_tokens(
    material: dict[str, object],
    source_title: str,
) -> set[str]:
    """source 本文と metadata から related page 候補用 token set を作る。"""
    material_parts = [
        material["source_id"],
        source_title,
        " ".join(material["headings"]),
        " ".join(material["tasklist_items"]),
        " ".join(material["result_facts"]),
        " ".join(material["discussion_points"]),
        " ".join(material["closing_points"]),
    ]
    return _collect_tokens(" ".join(str(part) for part in material_parts))


def _collect_tokens(text: str) -> set[str]:
    """英数字 token と日本語連続語を lower set で返す。"""
    tokens = set()
    for matched in _TOKEN_PATTERN.findall(text):
        normalized = matched.lower()
        if normalized.isdigit():
            continue
        if normalized not in _STOPWORDS:
            tokens.add(normalized)
    return tokens


def _score_history_overlap(
    source_tokens: set[str],
    history_weights: dict[str, dict[str, float]],
    area_path: str,
) -> tuple[float, list[str]]:
    """履歴 token の一致から area score を計算する。"""
    total_score = 0.0
    matched_tokens: list[str] = []
    for token in sorted(source_tokens):
        area_score = history_weights.get(token, {}).get(area_path)
        if area_score:
            total_score += area_score
            matched_tokens.append(token)
    return total_score, matched_tokens


def _build_candidate_reason(
    history_tokens: list[str],
    lexical_tokens: list[str],
) -> str:
    """candidate の短い理由文を返す。"""
    if history_tokens:
        return f"history token match: {', '.join(history_tokens[:3])}"
    return f"text overlap: {', '.join(lexical_tokens[:3])}"


def _build_summary_scaffold(
    *,
    material: dict[str, object],
    source_title: str,
    current_date: str,
) -> dict[str, object]:
    """summary draft の frontmatter と markdown scaffold を返す。"""
    raw_target_path = Path(material["summary_draft_path"]).name.replace("-summary.md", ".md")
    source_frontmatter = {
        "source": f"raw/tasknotes/steering/done/{raw_target_path}",
        "source_type": "tasknote",
        "created": current_date,
        "status": "draft",
    }
    draft_title = (
        source_title
        if source_title.endswith("Summary Draft")
        else f"{source_title} Summary Draft"
    )
    markdown_template = "\n".join(
        [
            "---",
            f"source: {source_frontmatter['source']}",
            "source_type: tasknote",
            f"created: {current_date}",
            "status: draft",
            "---",
            "",
            f"# {draft_title}",
            "",
            "## summary",
            "",
            "TODO_SUMMARY",
            "",
            "## key_points",
            "",
            "- TODO_KEY_POINT_1",
            "- TODO_KEY_POINT_2",
            "- TODO_KEY_POINT_3",
            "",
            "## important_quotes",
            "",
            '- "TODO_QUOTE_1"',
            '- "TODO_QUOTE_2"',
            "",
            "## open_questions",
            "",
            "- TODO_OPEN_QUESTION_1",
            "- TODO_OPEN_QUESTION_2",
            "",
        ]
    )
    return {
        "frontmatter": source_frontmatter,
        "draft_title": draft_title,
        "markdown_template": markdown_template,
    }


def _build_append_blocks(
    *,
    material: dict[str, object],
    display_label: str,
    related_candidates: list[dict[str, object]],
    current_date: str,
) -> dict[str, str]:
    """source-inbox / master-index / ingest-log 追記 block を返す。"""
    raw_file_name = Path(material["summary_draft_path"]).name.replace("-summary.md", ".md")
    raw_target_path = f"llm-wiki/raw/tasknotes/steering/done/{raw_file_name}"
    summary_target_path = material["summary_draft_path"]
    updated_area_paths = [candidate["path"] for candidate in related_candidates]
    source_inbox_block = "\n".join(
        [
            f"## [{current_date}] inbox | {display_label}",
            "",
            f"- source_id: `{material['source_id']}`",
            f"- source_path: `{raw_target_path}`",
            "- status: inbox",
            "- owner: codex",
            (
                "- note: steering 古い未インジェスト組の tasknote として "
                f"{display_label} の記録を batch ingest 候補として保持"
            ),
        ]
    )
    master_index_block = "\n".join(
        [
            (
                f"- [Tasknote Summary: {display_label}]"
                f"(../summaries/tasknotes/steering/done/{Path(summary_target_path).name}): "
                f"{_INDEX_DESCRIPTION_PLACEHOLDER}"
            ),
            (
                f"- [Tasknote Raw: {display_label}]"
                f"(../../raw/tasknotes/steering/done/{raw_file_name}): "
                f"{display_label} の元 tasknote"
            ),
        ]
    )
    updated_page_lines = [
        f"  - `{path}`"
        for path in updated_area_paths + [
            Path(*_SOURCE_INBOX_PATH).as_posix(),
            Path(*_MASTER_INDEX_PATH).as_posix(),
        ]
    ]
    ingest_log_block = "\n".join(
        [
            f"## [{current_date}] ingest | {display_label}",
            "",
            f"- source_id: `{material['source_id']}`",
            f"- source_path: `{raw_target_path}`",
            "- created_pages:",
            f"  - `{summary_target_path}`",
            "- updated_pages:",
            *updated_page_lines,
            f"- related_page_count: {len(updated_area_paths)}",
            "- risks:",
            f"  - {_RISK_PLACEHOLDER}",
            "- notes:",
            f"  - {_NOTE_PLACEHOLDER}",
        ]
    )
    return {
        "source_inbox": source_inbox_block,
        "master_index": master_index_block,
        "ingest_log": ingest_log_block,
    }


def _build_display_label(source_id: object) -> str:
    """source_id から master-index 向けの短い表示ラベルを作る。"""
    if not isinstance(source_id, str):
        return "Tasknote"
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", source_id)
    words: list[str] = []
    for index, token in enumerate(slug.split("-")):
        if re.fullmatch(r"[a-z]+\d+", token):
            words.append(token.upper())
        elif token in {"llm", "ssot", "ux", "api", "html", "json", "url"}:
            words.append(token.upper())
        elif index == 0:
            words.append(token.capitalize())
        else:
            words.append(token.lower())
    return " ".join(words).strip() or "Tasknote"


def _derive_source_id_from_stem(stem: str) -> str:
    """stem から `YYYY-MM-DD-slug` 形式の source_id を返す。"""
    for pattern in (_COMPACT_DATED_STEM_PATTERN, _HYPHENATED_DATED_STEM_PATTERN):
        matched = pattern.match(stem)
        if matched:
            return (
                f"{matched.group('year')}-{matched.group('month')}-"
                f"{matched.group('day')}-{matched.group('slug')}"
            )
    return stem


if __name__ == "__main__":
    raise SystemExit(main())
