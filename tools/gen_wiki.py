#!/usr/bin/env python3
"""Repo source から wiki raw/summaries を生成する最小 CLI。

このファイルに含まれる関数:

- generate_wiki: knowledge/tasknote source を raw/summaries に反映する
- run_main: CLI エントリ

Problems:
    - `wiki/` には skeleton だけがあり、raw と summaries を再現可能に増やす
      導線が無い。
    - source ごとに手で copy / summary を作ると path mirror がぶれやすく、
      後続の query / checklist が不安定になる。

Solutions:
    - repo 相対 path をそのまま `wiki/raw/...` に mirror し、
      `wiki/wiki/summaries/.../*-summary.md` を同じ相対構造で生成する。
    - summary は markdown/yaml を deterministic に整形し、最初の ingest を
      LLM 依存なしで再現可能にする。
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent.parent


# === Public API ===

def generate_wiki(
    *,
    knowledge_paths: list[str],
    tasknote_paths: list[str],
    repo_root: Path = ROOT,
    wiki_root: Path | None = None,
    today: str | None = None,
) -> dict[str, list[Path]]:
    """knowledge/tasknote source を raw と summaries に反映する。

    Args:
        knowledge_paths: `docs/...` のような repo 相対 source path。
        tasknote_paths: `steering/...` のような repo 相対 source path。
        repo_root: source 解決の基準 repo root。
        wiki_root: 出力先 root。未指定時は `<repo>/wiki`。
        today: frontmatter に書く日付。未指定時は `YYYY-MM-DD`。

    Returns:
        生成した raw path と summary path の list を返す。
    """
    return _run_generate_wiki(
        knowledge_paths=knowledge_paths,
        tasknote_paths=tasknote_paths,
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
    repo_root: Path,
    wiki_root: Path | None,
    today: str | None,
) -> dict[str, list[Path]]:
    repo_root = repo_root.resolve()
    wiki_root = _resolve_wiki_root(repo_root, wiki_root)
    ingested_on = today or _today_utc()
    raw_paths: list[Path] = []
    summary_paths: list[Path] = []

    _ensure_non_empty_targets(knowledge_paths, tasknote_paths)

    knowledge_results = _generate_group(
        repo_root=repo_root,
        wiki_root=wiki_root,
        relative_paths=knowledge_paths,
        source_type="knowledge",
        ingested_on=ingested_on,
    )
    tasknote_results = _generate_group(
        repo_root=repo_root,
        wiki_root=wiki_root,
        relative_paths=tasknote_paths,
        source_type="tasknote",
        ingested_on=ingested_on,
    )
    raw_paths.extend(knowledge_results["raw_paths"])
    raw_paths.extend(tasknote_results["raw_paths"])
    summary_paths.extend(knowledge_results["summary_paths"])
    summary_paths.extend(tasknote_results["summary_paths"])
    return {"raw_paths": raw_paths, "summary_paths": summary_paths}


def _run_main(argv: list[str] | None) -> int:
    parser = _build_parser()
    parsed_args = parser.parse_args(argv)
    try:
        result = generate_wiki(
            knowledge_paths=parsed_args.knowledge,
            tasknote_paths=parsed_args.tasknote,
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
    parser = argparse.ArgumentParser(description="Generate minimal wiki raw/summaries.")
    parser.add_argument("--knowledge", action="append", default=[], help="repo-relative knowledge path")
    parser.add_argument("--tasknote", action="append", default=[], help="repo-relative tasknote path")
    parser.add_argument("--repo-root", default=str(ROOT), help="repo root path")
    parser.add_argument("--wiki-root", default=None, help="output wiki root path")
    parser.add_argument("--today", default=None, help="ingest date for frontmatter (YYYY-MM-DD)")
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
    return (wiki_root or (repo_root / "wiki")).resolve()


def _ensure_non_empty_targets(knowledge_paths: list[str], tasknote_paths: list[str]) -> None:
    if knowledge_paths or tasknote_paths:
        return
    raise ValueError("at least one --knowledge or --tasknote path is required")


def _resolve_source_path(repo_root: Path, relative_path: str) -> Path:
    candidate = (repo_root / relative_path).resolve()
    if repo_root not in candidate.parents and candidate != repo_root:
        raise ValueError(f"path escapes repo root: {relative_path}")
    if not candidate.is_file():
        raise ValueError(f"source file is missing: {relative_path}")
    return candidate


def _raw_path_for(wiki_root: Path, relative_path: str, source_type: str) -> Path:
    base_dir = "knowledge" if source_type == "knowledge" else "tasknotes"
    return wiki_root / "raw" / base_dir / Path(relative_path)


def _summary_path_for(wiki_root: Path, relative_path: str, source_type: str) -> Path:
    base_dir = "knowledge" if source_type == "knowledge" else "tasknotes"
    relative = Path(relative_path)
    summary_name = f"{relative.stem}-summary.md"
    return wiki_root / "wiki" / "summaries" / base_dir / relative.parent / summary_name


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
    body = _strip_markdown_frontmatter(text) if _is_markdown(source_path) else text
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
) -> str:
    return "\n".join(
        [
            "---",
            f"source: {source}",
            f"source_type: {source_type}",
            f"last_ingested: {last_ingested}",
            f"size_class: {size_class}",
            "---",
            "",
        ]
    )


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


def _strip_markdown_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    marker = "\n---\n"
    closing_index = text.find(marker, 4)
    if closing_index == -1:
        return text
    return text[closing_index + len(marker):]


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
        return f"この source は「{title}」を扱う markdown で、主要トピックは {topic_text} です。{lead}"
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
        if stripped.startswith("**"):
            continue
        return stripped
    return ""


def _markdown_keywords(source_path: Path, title: str, body: str) -> list[str]:
    keywords = [source_path.stem, title]
    for topic in _markdown_topics(body):
        if topic not in keywords:
            keywords.append(topic)
    return keywords[:6]


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
        return f"この source は yaml 形式で、top-level keys は {key_text} です。facts 配下では {nested} を持ちます。"
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


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _today_utc() -> str:
    from datetime import datetime, UTC

    return datetime.now(UTC).date().isoformat()


if __name__ == "__main__":
    raise SystemExit(run_main())
