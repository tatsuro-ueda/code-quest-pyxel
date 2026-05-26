from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.llm_wiki_health_check_helper import prepare_health_check_material


def test_prepare_health_check_material_detects_scope_and_active_pages(
    tmp_path: Path,
) -> None:
    repo_root = _build_small_wiki_repo(tmp_path)

    payload = prepare_health_check_material(repo_root, current_date="2026-05-24")

    assert payload["scope_label"] == "current wiki"
    assert "llm-wiki/wiki/indexes/master-index.md" in payload["scope_paths"]
    assert payload["graph_entrypoints"] == ["llm-wiki/wiki/indexes/master-index.md"]
    assert "llm-wiki/wiki/areas/topic-a.md" in payload["active_page_paths"]


def test_prepare_health_check_material_collects_signals_and_scaffold(
    tmp_path: Path,
) -> None:
    repo_root = _build_small_wiki_repo(tmp_path)

    payload = prepare_health_check_material(repo_root, current_date="2026-05-24")

    assert payload["orphan_signals"][0]["path"] == "llm-wiki/wiki/areas/orphan-topic.md"
    assert (
        payload["missing_target_signals"][0]["missing_path"]
        == "llm-wiki/wiki/areas/Missing Topic.md"
    )
    assert any(
        signal["path"] == "llm-wiki/wiki/query/question-a.md"
        for signal in payload["crossref_signals"]
    )
    assert payload["log_scaffold"].startswith("## [2026-05-24] lint | current wiki")
    assert "- contradictions: none" in payload["log_scaffold"]
    assert "- notes:" in payload["log_scaffold"]


def test_prepare_health_check_material_preserves_japanese_area_titles(
    tmp_path: Path,
) -> None:
    repo_root = _build_small_wiki_repo(tmp_path)
    _write_page(
        repo_root / "llm-wiki/wiki/areas/topic-a.md",
        "# Topic A\n\nSee [[授業設計]] and [[Summary A]].\n",
    )

    payload = prepare_health_check_material(repo_root, current_date="2026-05-24")

    assert any(
        signal["missing_path"] == "llm-wiki/wiki/areas/授業設計.md"
        for signal in payload["missing_target_signals"]
    )


def test_prepare_health_check_material_uses_adapter_paths(tmp_path: Path) -> None:
    adapter_path = tmp_path / "llm-wiki/adapter.yml"
    adapter_path.parent.mkdir(parents=True, exist_ok=True)
    adapter_path.write_text(
        "\n".join(
            [
                "raw_root: llm-wiki/raw",
                "summary_root: llm-wiki/wiki/summaries",
                "master_index_path: knowledge/wiki/indexes/start.md",
                "source_inbox_path: knowledge/wiki/logs/source-inbox.md",
                "ingest_log_path: knowledge/wiki/logs/ingest-log.md",
                "health_check_log_path: knowledge/wiki/logs/health-check-log.md",
                "area_root: knowledge/wiki/areas",
                "query_root: knowledge/wiki/query",
                "candidate_root: knowledge/wiki/candidates",
                "tasknote_required_sections:",
                "  result: Result",
                "  discussion: Discussion",
                "  closing: Closing",
            ]
        ),
        encoding="utf-8",
    )
    _write_page(
        tmp_path / "knowledge/wiki/indexes/start.md",
        "# Start\n\n- [Topic A](../areas/topic-a.md)\n",
    )
    _write_page(tmp_path / "knowledge/wiki/areas/topic-a.md", "# Topic A\n")
    _write_page(tmp_path / "knowledge/wiki/logs/health-check-log.md", "# Log\n")

    payload = prepare_health_check_material(tmp_path, current_date="2026-05-24")

    assert payload["graph_entrypoints"] == ["knowledge/wiki/indexes/start.md"]
    assert payload["scope_paths"][0] == "knowledge/wiki/indexes/start.md"


def test_health_check_helper_cli_outputs_json(tmp_path: Path) -> None:
    repo_root = _build_small_wiki_repo(tmp_path)
    script_path = (
        Path(__file__).resolve().parents[1] / "tools/llm_wiki_health_check_helper.py"
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--repo-root",
            str(repo_root),
            "--current-date",
            "2026-05-24",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["scope_label"] == "current wiki"
    assert payload["log_scaffold"].startswith("## [2026-05-24] lint | current wiki")


def _build_small_wiki_repo(repo_root: Path) -> Path:
    _write_page(
        repo_root / "llm-wiki/wiki/indexes/master-index.md",
        "\n".join(
            [
                "# Master Index",
                "",
                "- [Topic A](../areas/topic-a.md)",
                "- [Question A](../query/question-a.md)",
                "- [Summary A](../summaries/knowledge/summary-a.md)",
            ]
        ),
    )
    _write_page(
        repo_root / "llm-wiki/wiki/areas/topic-a.md",
        "# Topic A\n\nSee [[Question A]] and [[Summary A]] and [[Missing Topic]].\n",
    )
    _write_page(
        repo_root / "llm-wiki/wiki/areas/orphan-topic.md",
        "# Orphan Topic\n\nNo inbound links.\n",
    )
    _write_page(
        repo_root / "llm-wiki/wiki/query/question-a.md",
        "# Question A\n\nRelated only to [[Topic A]].\n",
    )
    _write_page(
        repo_root / "llm-wiki/wiki/summaries/knowledge/summary-a.md",
        "# Summary A\n\nRelated to [[Topic A]].\n",
    )
    _write_page(repo_root / "llm-wiki/wiki/logs/health-check-log.md", "# Health Check Log\n")
    return repo_root


def _write_page(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
