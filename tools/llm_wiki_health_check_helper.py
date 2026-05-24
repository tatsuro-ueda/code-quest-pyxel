"""compiled wiki health-check 用の決定的な材料を JSON で返す CLI。

Problems:
    - `llm-wiki-health-check` の前半では、scope 決定、active graph 収集、
      orphan 候補整理、log 骨組み生成を毎回ほぼ手でそろえている。
    - 同じ compiled wiki を読んでも、AI ごとに path 一覧や構造 signal の
      並びがぶれやすく、分類判断の前処理コストが高い。

Solutions:
    - compiled wiki から scope、active graph、link signal、log scaffold を
      決定的に返す helper を 1 本にまとめる。
    - helper は read-only の構造 signal だけを返し、意味判断と prose は
      AI 側へ残す。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from datetime import date
from pathlib import Path


_DEFAULT_SCOPE_PATHS = (
    "llm-wiki/wiki/indexes/master-index.md",
    "llm-wiki/wiki/areas/*.md",
    "llm-wiki/wiki/query/*.md",
    "llm-wiki/wiki/summaries/knowledge/*.md",
    "llm-wiki/wiki/logs/health-check-log.md",
)
_GRAPH_ENTRYPOINT = "llm-wiki/wiki/indexes/master-index.md"
_TITLE_PATTERN = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)")
_MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")


# === Public API ===


def prepare_health_check_material(
    repo_root: Path,
    *,
    scope_hint: str | None = None,
    current_date: str | None = None,
) -> dict[str, object]:
    """compiled wiki health-check の前半材料を返す。

    Args:
        repo_root: repo root path。
        scope_hint: 任意の subtree 指定。
        current_date: log scaffold 用の日付文字列。

    Returns:
        scope、active graph、link signal、log scaffold を含む JSON 互換 dict。

    Policy:
        - helper は issue を断定せず、構造 signal だけを返す。
        - page 修正、schema 更新、log append は行わない。
    """
    date_label = current_date if current_date is not None else date.today().isoformat()
    scope_label, scope_paths, candidate_paths, graph_entrypoints = _detect_scope(
        repo_root,
        scope_hint,
    )
    pages = _load_pages(repo_root, candidate_paths)
    active_paths = _collect_active_paths(pages)
    orphan_signals = _collect_orphan_signals(pages, active_paths, graph_entrypoints)
    missing_target_signals = _collect_missing_target_signals(pages)
    crossref_signals = _collect_crossref_signals(pages, active_paths)
    return {
        "scope_label": scope_label,
        "scope_paths": scope_paths,
        "graph_entrypoints": graph_entrypoints,
        "active_page_paths": sorted(active_paths),
        "active_pages": _serialize_active_pages(pages, active_paths),
        "outlinks": _serialize_outlinks(pages, active_paths),
        "backlinks": _serialize_backlinks(pages, active_paths),
        "orphan_signals": orphan_signals,
        "missing_target_signals": missing_target_signals,
        "crossref_signals": crossref_signals,
        "log_scaffold": _build_log_scaffold(
            current_date=date_label,
            scope_label=scope_label,
            scope_paths=scope_paths,
        ),
        "missing_paths": [signal["missing_path"] for signal in missing_target_signals],
    }


def main(argv: list[str] | None = None) -> int:
    """CLI で health-check helper を実行して JSON を標準出力へ流す。"""
    args = _parse_args(argv)
    payload = prepare_health_check_material(
        Path(args.repo_root),
        scope_hint=args.scope_hint,
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
            "Prepare deterministic scope, graph signals, and log scaffold for "
            "llm-wiki health checks."
        ),
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--scope-hint", default=None, help="Optional subtree hint")
    parser.add_argument(
        "--current-date",
        default=None,
        help="Optional YYYY-MM-DD date for log scaffold",
    )
    return parser.parse_args(argv)


def _detect_scope(
    repo_root: Path,
    scope_hint: str | None,
) -> tuple[str, list[str], list[Path], list[str]]:
    """scope label、表示 path、読む候補 path、entrypoint を返す。"""
    if scope_hint:
        hinted_path = repo_root / scope_hint
        candidate_paths = _expand_scope_hint(hinted_path)
        relative_scope = _to_repo_relative(repo_root, hinted_path)
        graph_entrypoints = [relative_scope] if hinted_path.is_file() else []
        return scope_hint, [relative_scope], candidate_paths, graph_entrypoints

    candidate_paths: list[Path] = []
    for scope_path in _DEFAULT_SCOPE_PATHS:
        candidate_paths.extend((repo_root / "dummy").parent.glob(scope_path))
    candidate_paths = sorted({path.resolve(): path for path in candidate_paths}.values())
    return (
        "current wiki",
        list(_DEFAULT_SCOPE_PATHS),
        candidate_paths,
        [_GRAPH_ENTRYPOINT],
    )


def _expand_scope_hint(hinted_path: Path) -> list[Path]:
    """scope hint が file / directory のどちらでも path 一覧へ寄せる。"""
    if hinted_path.is_file():
        return [hinted_path]
    if hinted_path.is_dir():
        return sorted(hinted_path.rglob("*.md"))
    return []


def _load_pages(
    repo_root: Path,
    candidate_paths: list[Path],
) -> dict[str, dict[str, object]]:
    """scope 内の markdown page 群を path key で返す。"""
    pages: dict[str, dict[str, object]] = {}
    for path in candidate_paths:
        _register_page(repo_root, pages, path)

    while True:
        added_paths = _expand_linked_compiled_pages(repo_root, pages)
        if not added_paths:
            break

    title_to_path = {page["title"]: path for path, page in pages.items()}
    for page in pages.values():
        page["outlinks"] = _collect_outlinks(
            page_text=page["text"],
            page_path=page["path"],
            repo_root=repo_root,
            title_to_path=title_to_path,
        )

    for page in pages.values():
        page["backlink_count"] = 0
    for page in pages.values():
        for target_path in page["outlinks"]:
            if target_path in pages:
                pages[target_path]["backlink_count"] += 1
    return pages


def _register_page(
    repo_root: Path,
    pages: dict[str, dict[str, object]],
    path: Path,
) -> None:
    """page を pages dict に追加する。"""
    relative_path = _to_repo_relative(repo_root, path)
    if relative_path in pages:
        return
    text = path.read_text(encoding="utf-8")
    pages[relative_path] = {
        "path": relative_path,
        "title": _extract_title(text, path),
        "text": text,
        "outlinks": [],
        "backlink_count": 0,
    }


def _expand_linked_compiled_pages(
    repo_root: Path,
    pages: dict[str, dict[str, object]],
) -> list[str]:
    """既存 page から直接リンクされた compiled page を遅延ロードする。"""
    title_to_path = {page["title"]: path for path, page in pages.items()}
    added_paths: list[str] = []
    existing_paths = list(pages.keys())
    for page_path in existing_paths:
        page = pages[page_path]
        outlinks = _collect_outlinks(
            page_text=page["text"],
            page_path=page["path"],
            repo_root=repo_root,
            title_to_path=title_to_path,
        )
        for target_path in outlinks:
            if not target_path.startswith("llm-wiki/wiki/") or target_path in pages:
                continue
            absolute_target = repo_root / target_path
            if absolute_target.exists():
                _register_page(repo_root, pages, absolute_target)
                added_paths.append(target_path)
    return added_paths


def _extract_title(page_text: str, page_path: Path | str) -> str:
    """最初の H1 から title を返す。"""
    matched = _TITLE_PATTERN.search(page_text)
    if matched:
        return matched.group(1).strip()
    return Path(page_path).stem


def _collect_outlinks(
    *,
    page_text: str,
    page_path: str,
    repo_root: Path,
    title_to_path: dict[str, str],
) -> list[str]:
    """wikilink と markdown link から outlink path を集める。"""
    outlinks: list[str] = []
    seen_paths: set[str] = set()

    for raw_target in _WIKILINK_PATTERN.findall(page_text):
        target_path = title_to_path.get(raw_target.strip())
        if target_path is not None and target_path not in seen_paths:
            outlinks.append(target_path)
            seen_paths.add(target_path)
            continue
        missing_target = _build_missing_compiled_path(raw_target.strip())
        if missing_target not in seen_paths:
            outlinks.append(missing_target)
            seen_paths.add(missing_target)

    page_dir = Path(page_path).parent
    for raw_target in _MARKDOWN_LINK_PATTERN.findall(page_text):
        target_path = _normalize_markdown_target(
            repo_root,
            page_dir=page_dir,
            raw_target=raw_target,
        )
        if target_path not in seen_paths:
            outlinks.append(target_path)
            seen_paths.add(target_path)

    return outlinks


def _build_missing_compiled_path(link_target: str) -> str:
    """未解決 wikilink を compiled wiki 内の想定 path へ寄せる。"""
    slug = re.sub(r"[^a-z0-9]+", "-", link_target.lower()).strip("-")
    return f"llm-wiki/wiki/areas/{slug}.md"


def _normalize_markdown_target(
    repo_root: Path,
    *,
    page_dir: Path,
    raw_target: str,
) -> str:
    """markdown link target を repo-relative path へ寄せる。"""
    absolute_target = (repo_root / page_dir / raw_target).resolve()
    if absolute_target.is_relative_to(repo_root.resolve()):
        return absolute_target.relative_to(repo_root.resolve()).as_posix()
    return absolute_target.as_posix()


def _collect_active_paths(pages: dict[str, dict[str, object]]) -> set[str]:
    """master-index から辿れる active graph path 群を返す。"""
    active_paths: set[str] = set()
    queue: deque[str] = deque([_GRAPH_ENTRYPOINT])
    while queue:
        current_path = queue.popleft()
        if current_path in active_paths or current_path not in pages:
            continue
        active_paths.add(current_path)
        for target_path in pages[current_path]["outlinks"]:
            if target_path in pages and target_path not in active_paths:
                queue.append(target_path)
    return active_paths


def _collect_orphan_signals(
    pages: dict[str, dict[str, object]],
    active_paths: set[str],
    graph_entrypoints: list[str],
) -> list[dict[str, object]]:
    """active graph に含まれない compiled page を orphan 候補として返す。"""
    orphan_signals: list[dict[str, object]] = []
    for path, page in sorted(pages.items()):
        if path in active_paths or path in graph_entrypoints:
            continue
        if path.endswith("health-check-log.md"):
            continue
        orphan_signals.append(
            {
                "path": path,
                "title": page["title"],
                "reason": "not reachable from master-index active graph",
            }
        )
    return orphan_signals


def _collect_missing_target_signals(
    pages: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    """実在しない outlink target を signal として返す。"""
    missing_target_signals: list[dict[str, object]] = []
    for page in sorted(pages.values(), key=lambda item: item["path"]):
        for target_path in page["outlinks"]:
            if target_path in pages or not target_path.startswith("llm-wiki/wiki/"):
                continue
            missing_target_signals.append(
                {
                    "path": page["path"],
                    "title": page["title"],
                    "missing_path": target_path,
                    "reason": "linked page is not present in compiled wiki scope",
                }
            )
    return missing_target_signals


def _collect_crossref_signals(
    pages: dict[str, dict[str, object]],
    active_paths: set[str],
) -> list[dict[str, object]]:
    """導線が薄い active page を signal として返す。"""
    crossref_signals: list[dict[str, object]] = []
    for path in sorted(active_paths):
        if path == _GRAPH_ENTRYPOINT:
            continue
        page = pages[path]
        compiled_outlinks = [target for target in page["outlinks"] if target in active_paths]
        if page["backlink_count"] > 1 and len(compiled_outlinks) > 1:
            continue
        crossref_signals.append(
            {
                "path": path,
                "title": page["title"],
                "backlink_count": page["backlink_count"],
                "compiled_outlink_count": len(compiled_outlinks),
                "reason": "thin connectivity inside active graph",
            }
        )
    return crossref_signals


def _serialize_active_pages(
    pages: dict[str, dict[str, object]],
    active_paths: set[str],
) -> list[dict[str, object]]:
    """active page 情報を JSON 向け配列へ寄せる。"""
    return [
        {
            "path": path,
            "title": pages[path]["title"],
            "backlink_count": pages[path]["backlink_count"],
        }
        for path in sorted(active_paths)
    ]


def _serialize_outlinks(
    pages: dict[str, dict[str, object]],
    active_paths: set[str],
) -> list[dict[str, object]]:
    """active page ごとの outlink を JSON 向け配列へ寄せる。"""
    return [
        {
            "path": path,
            "targets": pages[path]["outlinks"],
        }
        for path in sorted(active_paths)
    ]


def _serialize_backlinks(
    pages: dict[str, dict[str, object]],
    active_paths: set[str],
) -> list[dict[str, object]]:
    """active page ごとの backlink count を JSON 向け配列へ寄せる。"""
    return [
        {
            "path": path,
            "count": pages[path]["backlink_count"],
        }
        for path in sorted(active_paths)
    ]


def _build_log_scaffold(
    *,
    current_date: str,
    scope_label: str,
    scope_paths: list[str],
) -> str:
    """health-check log entry の骨組みを返す。"""
    lines = [f"## [{current_date}] lint | {scope_label}", "", "- scope:"]
    for scope_path in scope_paths:
        lines.append(f"  - `{scope_path}`")
    lines.extend(
        [
            "- contradictions: none",
            "- stale_claims: none",
            "- orphan_pages: none",
            "- missing_concepts: none",
            "- missing_crossrefs: none",
            "- data_gaps: none",
            "- fix_now:",
            "  - none",
            "- next_ingest:",
            "  - none",
            "- candidate_source:",
            "  - none",
            "- notes:",
            "  - graph scaffold prepared by Python helper",
        ]
    )
    return "\n".join(lines)


def _to_repo_relative(repo_root: Path, path: Path) -> str:
    """path を repo root 起点の posix path へ寄せる。"""
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
