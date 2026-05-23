#!/usr/bin/env python3
"""Repo source から wiki raw/summaries と最小ナビゲーション層を生成する CLI。

このファイルに含まれる関数:

- generate_wiki: knowledge/tasknote/checklist source を raw/summaries に反映する
- run_main: CLI エントリ

Problems:
    - `wiki/` には skeleton だけがあり、raw と summaries を再現可能に増やす
      導線が無い。
    - source ごとに手で copy / summary を作ると path mirror がぶれやすく、
      後続の query / checklist が不安定になる。
    - summary を作っても `index.md` / `log.md` / tasknote index が無いと、
      次回セッションで入口探索からやり直しになる。

Solutions:
    - repo 相対 path をそのまま `llm-wiki/raw/...` に mirror し、
      `llm-wiki/wiki/summaries/.../*-summary.md` を同じ相対構造で生成する。
    - checklist は `llm-wiki/checklists/` を source としつつ、
      `raw/knowledge/checklists/` と `summaries/checklists/` に寄せる。
    - 生成後に `index.md` / `log.md` / `indexes/tasknotes.md` /
      `query/README.md` / `candidates/*.md` を deterministic に書き直す。
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent.parent
GENERIC_CANDIDATE_STOPWORDS = {
    "TL;DR",
    "Result",
    "Discussion",
    "Journey",
    "Feature",
    "Rule",
    "Scenario",
    "knowledge",
    "tasknote",
    "tasknotes",
    "checklist",
    "checklists",
    "source",
    "summary",
    "summaries",
    "wiki",
    "docs",
    "done",
    "raw",
    "index",
    "log",
    "note",
    "話題一覧",
    "シナリオ一覧",
    "変更範囲",
    "残課題メモ",
    "反省とルール化",
    "前提条件",
    "共通条件",
}
AREA_KEYWORDS = {
    "battle": ("battle", "呪文", "戦闘", "enemy", "boss"),
    "narrative": ("narrative", "dialog", "dialogue", "story", "セリフ", "会話"),
    "platform": ("platform", "web", "share", "公開", "url", "iframe", "fullscreen"),
    "guardrails": ("guardrail", "guardrails", "architecture", "framework", "lint", "rule"),
    "av": ("bgm", "sfx", "vfx", "audio", "sound", "av", "演出"),
    "map": ("map", "tile", "landmark", "world", "ダンジョン", "マップ"),
    "code-maker": ("code maker", "codemaker", "pyxres"),
}


# === Public API ===

def generate_wiki(
    *,
    knowledge_paths: list[str],
    tasknote_paths: list[str],
    checklist_paths: list[str] | None = None,
    repo_root: Path = ROOT,
    wiki_root: Path | None = None,
    today: str | None = None,
) -> dict[str, list[Path]]:
    """knowledge/tasknote/checklist source を raw と summaries に反映する。

    Args:
        knowledge_paths: `docs/...` のような repo 相対 source path。
        tasknote_paths: `steering/...` のような repo 相対 source path。
        checklist_paths: `llm-wiki/checklists/...` のような repo 相対 source path。
        repo_root: source 解決の基準 repo root。
        wiki_root: 出力先 root。未指定時は `<repo>/llm-wiki`。
        today: frontmatter に書く日付。未指定時は `YYYY-MM-DD`。

    Returns:
        生成した raw path と summary path の list を返す。
    """
    return _run_generate_wiki(
        knowledge_paths=knowledge_paths,
        tasknote_paths=tasknote_paths,
        checklist_paths=checklist_paths or [],
        repo_root=repo_root,
        wiki_root=wiki_root,
        today=today,
    )


def run_main(argv: list[str] | None = None) -> int:
    """CLI エントリ。

    Returns:
        成功時 0、引数エラー時 1。
    """
    return _run_main(argv)


def _run_generate_wiki(
    *,
    knowledge_paths: list[str],
    tasknote_paths: list[str],
    checklist_paths: list[str],
    repo_root: Path,
    wiki_root: Path | None,
    today: str | None,
) -> dict[str, list[Path]]:
    repo_root = repo_root.resolve()
    wiki_root = _resolve_wiki_root(repo_root, wiki_root)
    ingested_on = today or _today_utc()
    raw_paths: list[Path] = []
    summary_paths: list[Path] = []

    _ensure_non_empty_targets(knowledge_paths, tasknote_paths, checklist_paths)

    for source_type, relative_paths in (
        ("knowledge", knowledge_paths),
        ("tasknote", tasknote_paths),
        ("checklist", checklist_paths),
    ):
        if not relative_paths:
            continue
        group_results = _generate_group(
            repo_root=repo_root,
            wiki_root=wiki_root,
            relative_paths=relative_paths,
            source_type=source_type,
            ingested_on=ingested_on,
        )
        raw_paths.extend(group_results["raw_paths"])
        summary_paths.extend(group_results["summary_paths"])

    _write_navigation_artifacts(wiki_root)
    return {"raw_paths": raw_paths, "summary_paths": summary_paths}


def _run_main(argv: list[str] | None) -> int:
    parser = _build_parser()
    parsed_args = parser.parse_args(argv)
    try:
        result = generate_wiki(
            knowledge_paths=parsed_args.knowledge,
            tasknote_paths=parsed_args.tasknote,
            checklist_paths=parsed_args.checklist,
            repo_root=Path(parsed_args.repo_root),
            wiki_root=Path(parsed_args.wiki_root) if parsed_args.wiki_root else None,
            today=parsed_args.today,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for path in result["raw_paths"] + result["summary_paths"]:
        print(path)
    return 0


# === Internal helpers (private) ===

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate repo-local wiki raw/summaries and navigation."
    )
    parser.add_argument(
        "--knowledge",
        action="append",
        default=[],
        help="repo-relative knowledge path",
    )
    parser.add_argument(
        "--tasknote",
        action="append",
        default=[],
        help="repo-relative tasknote path",
    )
    parser.add_argument(
        "--checklist",
        action="append",
        default=[],
        help="repo-relative checklist path",
    )
    parser.add_argument("--repo-root", default=str(ROOT), help="repo root path")
    parser.add_argument("--wiki-root", default=None, help="output wiki root path")
    parser.add_argument(
        "--today",
        default=None,
        help="ingest date for frontmatter (YYYY-MM-DD)",
    )
    return parser


def _generate_group(
    *,
    repo_root: Path,
    wiki_root: Path,
    relative_paths: list[str],
    source_type: str,
    ingested_on: str,
) -> dict[str, list[Path]]:
    raw_paths: list[Path] = []
    summary_paths: list[Path] = []
    for relative_path in relative_paths:
        source_path = _resolve_source_path(repo_root, relative_path)
        raw_path = _raw_path_for(wiki_root, relative_path, source_type)
        summary_path = _summary_path_for(wiki_root, relative_path, source_type)
        _copy_source(source_path, raw_path)
        summary_text = _build_summary_text(
            source_path=source_path,
            raw_path=raw_path,
            wiki_root=wiki_root,
            source_type=source_type,
            ingested_on=ingested_on,
        )
        _write_text(summary_path, summary_text)
        raw_paths.append(raw_path)
        summary_paths.append(summary_path)
    return {"raw_paths": raw_paths, "summary_paths": summary_paths}


def _resolve_wiki_root(repo_root: Path, wiki_root: Path | None) -> Path:
    return (wiki_root or (repo_root / "llm-wiki")).resolve()


def _ensure_non_empty_targets(
    knowledge_paths: list[str],
    tasknote_paths: list[str],
    checklist_paths: list[str],
) -> None:
    if knowledge_paths or tasknote_paths or checklist_paths:
        return
    raise ValueError(
        "at least one --knowledge, --tasknote, or --checklist path is required"
    )


def _resolve_source_path(repo_root: Path, relative_path: str) -> Path:
    candidate = (repo_root / relative_path).resolve()
    if repo_root not in candidate.parents and candidate != repo_root:
        raise ValueError(f"path escapes repo root: {relative_path}")
    if not candidate.is_file():
        raise ValueError(f"source file is missing: {relative_path}")
    return candidate


def _raw_path_for(wiki_root: Path, relative_path: str, source_type: str) -> Path:
    relative = _output_relative_path(relative_path, source_type)
    if source_type == "tasknote":
        return wiki_root / "raw" / "tasknotes" / relative
    return wiki_root / "raw" / "knowledge" / relative


def _summary_path_for(wiki_root: Path, relative_path: str, source_type: str) -> Path:
    relative = _output_relative_path(relative_path, source_type)
    summary_name = f"{relative.stem}-summary.md"
    if source_type == "tasknote":
        return (
            wiki_root
            / "wiki"
            / "summaries"
            / "tasknotes"
            / relative.parent
            / summary_name
        )
    if source_type == "checklist":
        summary_parent = relative.parent
        if summary_parent.parts[:1] == ("checklists",):
            summary_parent = Path(*summary_parent.parts[1:])
        return (
            wiki_root
            / "wiki"
            / "summaries"
            / "checklists"
            / summary_parent
            / summary_name
        )
    summary_base = "checklists" if source_type == "checklist" else "knowledge"
    return (
        wiki_root
        / "wiki"
        / "summaries"
        / summary_base
        / relative.parent
        / summary_name
    )


def _output_relative_path(relative_path: str, source_type: str) -> Path:
    relative = Path(relative_path)
    if source_type != "checklist":
        return relative
    parts = list(relative.parts)
    if parts[:2] in (["wiki", "checklists"], ["llm-wiki", "checklists"]):
        parts = parts[2:]
    elif parts[:1] == ["checklists"]:
        parts = parts[1:]
    if not parts:
        return Path("checklists") / relative.name
    return Path("checklists").joinpath(*parts)


def _copy_source(source_path: Path, raw_path: Path) -> None:
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, raw_path)


def _build_summary_text(
    *,
    source_path: Path,
    raw_path: Path,
    wiki_root: Path,
    source_type: str,
    ingested_on: str,
) -> str:
    text = source_path.read_text(encoding="utf-8")
    metadata = _source_metadata_for(source_path, text, source_type)
    body = _source_body_for(source_path, text)
    size_class = _size_class_for(text)
    raw_relative = raw_path.relative_to(wiki_root).as_posix()
    if _is_yaml(source_path):
        title = _yaml_title_for(source_path, text)
        summary_paragraph = _build_yaml_summary_paragraph(text)
        topics = _yaml_topics(text)
        keywords = _yaml_keywords(source_path, text)
        notes = _yaml_notes(text)
    else:
        title = _markdown_title_for(source_path, body)
        summary_paragraph = _build_markdown_summary_paragraph(title, body)
        topics = _markdown_topics(body)
        keywords = _markdown_keywords(source_path, title, body)
        notes = _markdown_notes(body)
    frontmatter = _summary_frontmatter(
        source=raw_relative,
        source_type=source_type,
        last_ingested=ingested_on,
        size_class=size_class,
        metadata=metadata,
    )
    sections = [
        frontmatter,
        f"# {title}",
        "",
        "## TL;DR",
        "",
        summary_paragraph,
        "",
        "## 主要トピック",
        "",
        *[f"- {topic}" for topic in topics],
        "",
        "## キーワード",
        "",
        *[f"- {keyword}" for keyword in keywords],
        "",
        "## 注意点",
        "",
        *[f"- {note}" for note in notes],
        "",
    ]
    return "\n".join(sections)


def _summary_frontmatter(
    *,
    source: str,
    source_type: str,
    last_ingested: str,
    size_class: str,
    metadata: dict[str, Any],
) -> str:
    lines = [
        "---",
        f"source: {source}",
        f"source_type: {source_type}",
    ]
    for key in ("status", "replacement_of", "origin", "last_synced"):
        value = metadata.get(key)
        if value in (None, "", [], {}):
            continue
        lines.extend(_frontmatter_lines(key, value))
    lines.append(f"last_ingested: {last_ingested}")
    lines.append(f"size_class: {size_class}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _frontmatter_lines(key: str, value: Any) -> list[str]:
    if isinstance(value, list):
        lines = [f"{key}:"]
        for item in value:
            lines.append(f"  - {item}")
        return lines
    return [f"{key}: {value}"]


def _source_metadata_for(
    source_path: Path,
    text: str,
    source_type: str,
) -> dict[str, Any]:
    if _is_yaml(source_path):
        return _yaml_source_metadata(text)
    frontmatter, _ = _split_markdown_frontmatter(text)
    metadata: dict[str, Any] = {}
    status = frontmatter.get("status")
    if not isinstance(status, str) or not status.strip():
        if source_type in {"knowledge", "checklist"}:
            status = "active"
    if isinstance(status, str) and status.strip():
        metadata["status"] = status.strip()
    for key in ("replacement_of", "origin", "last_synced"):
        value = frontmatter.get(key)
        if value not in (None, "", [], {}):
            metadata[key] = value
    return metadata


def _yaml_source_metadata(text: str) -> dict[str, Any]:
    payload = _load_yaml_payload(text)
    if not isinstance(payload, dict):
        return {"status": "draft"}
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        return {"status": "draft"}
    metadata: dict[str, Any] = {}
    status = meta.get("status", "draft")
    if isinstance(status, str) and status.strip():
        metadata["status"] = status.strip()
    replacement_of = meta.get("intended_replacement_for")
    if replacement_of not in (None, "", [], {}):
        metadata["replacement_of"] = replacement_of
    return metadata


def _source_body_for(source_path: Path, text: str) -> str:
    if not _is_markdown(source_path):
        return text
    _, body = _split_markdown_frontmatter(text)
    return body


def _size_class_for(text: str) -> str:
    size = len(text.encode("utf-8"))
    if size < 10_000:
        return "small"
    if size < 50_000:
        return "medium"
    return "large"


def _is_markdown(path: Path) -> bool:
    return path.suffix.lower() == ".md"


def _is_yaml(path: Path) -> bool:
    return path.suffix.lower() in {".yml", ".yaml"}


def _split_markdown_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    marker = "\n---\n"
    closing_index = text.find(marker, 4)
    if closing_index == -1:
        return {}, text
    frontmatter_text = text[4:closing_index]
    payload = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(payload, dict):
        payload = {}
    body = text[closing_index + len(marker):]
    return payload, body


def _markdown_title_for(source_path: Path, body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return source_path.stem


def _markdown_topics(body: str) -> list[str]:
    topics: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            topics.append(stripped[3:].strip())
        elif stripped.startswith("### "):
            topics.append(stripped[4:].strip())
    return topics or ["見出し不足"]


def _build_markdown_summary_paragraph(title: str, body: str) -> str:
    topic_text = "、".join(_markdown_topics(body)[:4])
    lead = _first_markdown_paragraph(body)
    if lead:
        return (
            f"この source は「{title}」を扱う markdown で、"
            f"主要トピックは {topic_text} です。{lead}"
        )
    return f"この source は「{title}」を扱う markdown で、主要トピックは {topic_text} です。"


def _first_markdown_paragraph(body: str) -> str:
    skip_prefixes = ("🧱", "🎬", "✅", "❓", "👀", "📌", "📚", "🔗", "📝")
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in {"---", "***", "___"}:
            continue
        if stripped.startswith(skip_prefixes):
            continue
        if stripped.startswith("```"):
            continue
        if stripped.startswith(("flowchart ", "graph ", "classDef", "subgraph")):
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            continue
        if stripped.startswith(">"):
            continue
        if stripped.startswith("|"):
            continue
        if stripped.startswith("**"):
            continue
        return stripped
    return ""


def _markdown_keywords(source_path: Path, title: str, body: str) -> list[str]:
    keywords = [source_path.stem, title]
    for topic in _markdown_topics(body):
        if topic not in keywords:
            keywords.append(topic)
    return keywords[:8]


def _markdown_notes(body: str) -> list[str]:
    notes = []
    if "TODO" in body or "TBD" in body:
        notes.append("未確定の記述を含むため raw の確認が必要")
    notes.append("見出し抽出ベースの summary なので、細かな根拠は raw を参照する")
    return notes[:3]


def _yaml_title_for(source_path: Path, text: str) -> str:
    payload = _load_yaml_payload(text)
    if isinstance(payload, dict):
        meta = payload.get("meta")
        if isinstance(meta, dict):
            document_id = meta.get("document_id")
            if isinstance(document_id, str) and document_id.strip():
                return document_id.strip()
    return source_path.stem


def _build_yaml_summary_paragraph(text: str) -> str:
    payload = _load_yaml_payload(text)
    if not isinstance(payload, dict):
        return "この yaml source は top-level mapping ではないため、raw の確認が必要です。"
    top_keys = list(payload.keys())
    key_text = "、".join(top_keys[:5]) if top_keys else "なし"
    facts = payload.get("facts")
    if isinstance(facts, dict):
        nested = "、".join(list(facts.keys())[:4])
        return (
            f"この source は yaml 形式で、top-level keys は {key_text} です。"
            f"facts 配下では {nested} を持ちます。"
        )
    return f"この source は yaml 形式で、top-level keys は {key_text} です。"


def _yaml_topics(text: str) -> list[str]:
    payload = _load_yaml_payload(text)
    if not isinstance(payload, dict):
        return ["top-level mapping ではない"]
    topics: list[str] = []
    for key, value in payload.items():
        if isinstance(value, dict) and value:
            child_keys = ", ".join(list(value.keys())[:4])
            topics.append(f"{key}: {child_keys}")
        else:
            topics.append(str(key))
    return topics[:8]


def _yaml_keywords(source_path: Path, text: str) -> list[str]:
    payload = _load_yaml_payload(text)
    keywords = [source_path.stem]
    if not isinstance(payload, dict):
        return keywords
    for key in payload.keys():
        key_text = str(key)
        if key_text not in keywords:
            keywords.append(key_text)
    facts = payload.get("facts")
    if isinstance(facts, dict):
        for key in facts.keys():
            key_text = str(key)
            if key_text not in keywords:
                keywords.append(key_text)
    return keywords[:8]


def _yaml_notes(text: str) -> list[str]:
    payload = _load_yaml_payload(text)
    notes = []
    if not isinstance(payload, dict):
        notes.append("mapping 前提の summary なので raw 構造の再確認が必要")
    else:
        notes.append("top-level key と代表 subkey の抽出ベースなので、詳細 field は raw を参照する")
    return notes[:3]


def _load_yaml_payload(text: str) -> Any:
    payload = yaml.safe_load(text)
    return payload if payload is not None else {}


def _write_navigation_artifacts(wiki_root: Path) -> None:
    records = _collect_summary_records(wiki_root)
    _write_text(wiki_root / "wiki" / "index.md", _build_index_text(records))
    _write_text(wiki_root / "wiki" / "log.md", _build_log_text(records))
    _write_text(
        wiki_root / "wiki" / "indexes" / "tasknotes.md",
        _build_tasknote_index_text(wiki_root, records),
    )
    _write_text(
        wiki_root / "wiki" / "query" / "README.md",
        _build_query_readme_text(records),
    )
    concept_text, entity_text = _build_candidate_texts(records)
    _write_text(wiki_root / "wiki" / "candidates" / "concepts.md", concept_text)
    _write_text(wiki_root / "wiki" / "candidates" / "entities.md", entity_text)


def _collect_summary_records(wiki_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    summary_root = wiki_root / "wiki" / "summaries"
    for path in sorted(summary_root.rglob("*-summary.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter, body = _split_markdown_frontmatter(text)
        records.append(
            {
                "path": path,
                "summary_link": path.relative_to(wiki_root / "wiki").as_posix(),
                "source": str(frontmatter.get("source", "")),
                "source_type": str(frontmatter.get("source_type", "")),
                "status": str(frontmatter.get("status", "")),
                "title": _markdown_title_for(path, body),
                "tldr": _extract_tldr(body),
                "keywords": _extract_bullets(body, "## キーワード"),
                "topics": _extract_bullets(body, "## 主要トピック"),
                "last_ingested": str(frontmatter.get("last_ingested", "")),
                "text": text,
            }
        )
    return records


def _extract_tldr(body: str) -> str:
    lines = body.splitlines()
    collecting = False
    collected: list[str] = []
    for line in lines:
        if line.strip() == "## TL;DR":
            collecting = True
            continue
        if collecting and line.startswith("## "):
            break
        if collecting and line.strip():
            collected.append(line.strip())
    return " ".join(collected).strip()


def _extract_bullets(body: str, heading: str) -> list[str]:
    lines = body.splitlines()
    collecting = False
    bullets: list[str] = []
    for line in lines:
        if line.strip() == heading:
            collecting = True
            continue
        if collecting and line.startswith("## "):
            break
        stripped = line.strip()
        if collecting and stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def _build_index_text(records: list[dict[str, Any]]) -> str:
    sections = [
        "# wiki index",
        "",
        "repo-local wiki の入口。summary / checklist / tasknote をここから辿る。",
        "",
        "## navigation",
        "",
        "- [log.md](log.md)",
        "- [indexes/tasknotes.md](indexes/tasknotes.md)",
        "- [query/README.md](query/README.md)",
        "- [candidates/concepts.md](candidates/concepts.md)",
        "- [candidates/entities.md](candidates/entities.md)",
        "",
    ]
    grouped = defaultdict(list)
    for record in records:
        grouped[record["source_type"]].append(record)
    section_labels = (
        ("knowledge", "knowledge summaries"),
        ("tasknote", "tasknote summaries"),
        ("checklist", "checklist summaries"),
    )
    for source_type, label in section_labels:
        sections.extend([f"## {label}", ""])
        items = grouped.get(source_type, [])
        if not items:
            sections.extend(["- まだ生成されていない", ""])
            continue
        for record in items:
            sections.append(
                f"- [{record['title']}]({record['summary_link']})"
                f" — {record['tldr'] or 'TL;DR なし'}"
            )
            sections.append(f"  - source: `{record['source']}`")
        sections.append("")
    return "\n".join(sections).rstrip() + "\n"


def _build_log_text(records: list[dict[str, Any]]) -> str:
    sections = [
        "# wiki log",
        "",
        "summary に入った source の時系列ログ。",
        "",
        "## entries",
        "",
    ]
    ordered = sorted(
        records,
        key=lambda item: (item["last_ingested"], item["summary_link"]),
        reverse=True,
    )
    if not ordered:
        sections.append("- まだ記録がない")
    for record in ordered:
        date = record["last_ingested"] or "unknown-date"
        sections.append(
            f"- {date} | {record['source_type']} | "
            f"[{record['title']}]({record['summary_link']})"
        )
        sections.append(f"  - source: `{record['source']}`")
    sections.append("")
    return "\n".join(sections)


def _build_tasknote_index_text(
    wiki_root: Path,
    records: list[dict[str, Any]],
) -> str:
    sections = [
        "# tasknotes index",
        "",
        "| タスクノート | status | summary | raw |",
        "|---|---|---|---|",
    ]
    tasknotes = [record for record in records if record["source_type"] == "tasknote"]
    if not tasknotes:
        sections.append("| なし | - | - | - |")
        sections.append("")
        return "\n".join(sections)
    for record in tasknotes:
        raw_path = wiki_root / record["source"]
        status = _raw_markdown_frontmatter(raw_path).get("status", "-")
        title = record["title"]
        sections.append(
            f"| {title} | {status} | "
            f"[summary]({record['summary_link']}) | `{record['source']}` |"
        )
    sections.append("")
    return "\n".join(sections)


def _build_query_readme_text(records: list[dict[str, Any]]) -> str:
    knowledge_count = sum(1 for record in records if record["source_type"] == "knowledge")
    checklist_count = sum(1 for record in records if record["source_type"] == "checklist")
    tasknote_count = sum(1 for record in records if record["source_type"] == "tasknote")
    sections = [
        "# query",
        "",
        "generated wiki を読むときの read-only 入口。",
        "",
        "## read-only rules",
        "",
        "- query 中に `llm-wiki/raw/` を更新しない",
        "- 根拠は summary / checklist / index に限定して返す",
        "- 情報不足なら不足と書く",
        "- raw が古そうでも maintenance note 以外は更新しない",
        "",
        "## available sources",
        "",
        f"- knowledge summaries: {knowledge_count}",
        f"- checklist summaries: {checklist_count}",
        f"- tasknote summaries: {tasknote_count}",
        "",
        "## answer template",
        "",
        "```markdown",
        "## Q: <質問>",
        "",
        "### A",
        "",
        "<2〜5文の答え>",
        "",
        "### 根拠",
        "",
        "- `summaries/...`",
        "- `checklists/...`",
        "",
        "### 情報不足（あれば）",
        "",
        "- ...",
        "```",
        "",
    ]
    return "\n".join(sections)


def _build_candidate_texts(
    records: list[dict[str, Any]],
) -> tuple[str, str]:
    counts: Counter[str] = Counter()
    sources: dict[str, set[str]] = defaultdict(set)
    areas: dict[str, set[str]] = defaultdict(set)
    for record in records:
        for term in _candidate_terms_for(record):
            counts[term] += 1
            sources[term].add(record["summary_link"])
            area = _infer_area(record)
            if area != "-":
                areas[term].add(area)

    concept_rows: list[str] = []
    entity_rows: list[str] = []
    for term, count in sorted(
        counts.items(),
        key=lambda item: (-item[1], item[0].lower()),
    )[:20]:
        source_preview = ", ".join(sorted(sources[term])[:3]) or "-"
        area_preview = ", ".join(sorted(areas[term])) or "-"
        row = f"| {term} | {count} | {source_preview} | {area_preview} |"
        if _is_entity_term(term):
            entity_rows.append(row)
        else:
            concept_rows.append(row)

    concept_text = _candidate_table_text(
        title="concepts candidates",
        rows=concept_rows,
    )
    entity_text = _candidate_table_text(
        title="entities candidates",
        rows=entity_rows,
    )
    return concept_text, entity_text


def _candidate_terms_for(record: dict[str, Any]) -> set[str]:
    candidates: set[str] = set()
    for raw_term in [record["title"], *record["keywords"], *record["topics"]]:
        term = raw_term.strip()
        if not term or len(term) < 2:
            continue
        if re.match(r"^\d+\)", term):
            continue
        if any(marker in term for marker in ("（どこへ行くか）", "（完了条件）", "（どうやるか）", "（残課題の起票）")):
            continue
        if term in GENERIC_CANDIDATE_STOPWORDS:
            continue
        if term.lower() in {item.lower() for item in GENERIC_CANDIDATE_STOPWORDS}:
            continue
        candidates.add(term)
    text = f"{record['title']} {' '.join(record['keywords'])} {record['text']} {record['source']}"
    for match in re.findall(
        (
            r"(SSoT|Single Source of Truth|Code Maker|Pyxel|Pyxres|"
            r"Block Quest|Guardrail|Customer Job|Customer Journey|"
            r"ひらがな|実物確認|単一配信|dist|Battle|Narrative|Platform|"
            r"framework-rule\.md|architecture_rules\.yml|ux-policy\.md|"
            r"product-requirements-[a-z-]+\.md|CJ[A-Z0-9]+)"
        ),
        text,
        flags=re.IGNORECASE,
    ):
        normalized = match.strip()
        if normalized:
            candidates.add(normalized)
    return candidates


def _candidate_table_text(title: str, rows: list[str]) -> str:
    sections = [
        f"# {title}",
        "",
        "| 用語 | 頻度 | 出現 summary | 関連 area |",
        "|---|---:|---|---|",
    ]
    if not rows:
        sections.append("| なし | 0 | - | - |")
    else:
        sections.extend(rows)
    sections.append("")
    return "\n".join(sections)


def _is_entity_term(term: str) -> bool:
    if any(marker in term for marker in (".md", ".yml", ".yaml")):
        return True
    if any(marker in term for marker in ("Pyxel", "Pyxres", "Code Maker", "Block Quest")):
        return True
    if re.search(r"\bCJ[A-Z0-9]+\b", term):
        return True
    return bool(re.search(r"[A-Z][a-z]+", term))


def _infer_area(record: dict[str, Any]) -> str:
    haystack = (
        f"{record['source']} {record['title']} {' '.join(record['keywords'])}"
    ).lower()
    for area, keywords in AREA_KEYWORDS.items():
        if any(keyword.lower() in haystack for keyword in keywords):
            return area
    return "-"


def _raw_markdown_frontmatter(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.suffix.lower() != ".md":
        return {}
    text = path.read_text(encoding="utf-8")
    frontmatter, _ = _split_markdown_frontmatter(text)
    return frontmatter


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _today_utc() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).date().isoformat()


if __name__ == "__main__":
    raise SystemExit(run_main())
