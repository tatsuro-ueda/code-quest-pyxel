from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.llm_wiki_steering_batch_helper import prepare_steering_done_batch


def test_prepare_steering_done_batch_selects_oldest_uningested_sources(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path
    _write_area_pages(repo_root)
    _write_ingest_log(repo_root, [])

    for day in range(1, 13):
        if day == 5:
            file_name = "2026-04-20-hyphen-style-preview.md"
            created_at = "2026-04-05T09:00:00.000+00:00"
        else:
            file_name = f"202604{day:02d}-sample-task-{day}.md"
            created_at = f"2026-04-{day:02d}T09:00:00.000+00:00"
        _write_tasknote(
            repo_root / "steering/done" / file_name,
            created_at=created_at,
            title=f"2026年4月{day}日 Sample Task {day}",
            discussion_line=f"sample discussion {day}",
        )

    summary_dir = repo_root / "llm-wiki/wiki/summaries/tasknotes/steering/done"
    summary_dir.mkdir(parents=True, exist_ok=True)
    (summary_dir / "20260401-sample-task-1-summary.md").write_text(
        "# existing",
        encoding="utf-8",
    )

    payload = prepare_steering_done_batch(repo_root, limit=10, current_date="2026-05-24")

    selected_names = [Path(item["source_path"]).name for item in payload["sources"]]

    assert len(selected_names) == 10
    assert selected_names[0] == "20260402-sample-task-2.md"
    assert selected_names[3] == "2026-04-20-hyphen-style-preview.md"
    assert "20260412-sample-task-12.md" not in selected_names


def test_prepare_steering_done_batch_builds_scaffold_and_append_blocks(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path
    _write_area_pages(repo_root)
    _write_ingest_log(repo_root, [])
    _write_tasknote(
        repo_root / "steering/done/20260418-preview-selector-cache.md",
        created_at="2026-04-18T09:00:00.000+00:00",
        title="2026年4月18日 Preview Selector Cache",
        discussion_line="preview selector current cache",
    )

    payload = prepare_steering_done_batch(repo_root, limit=10, current_date="2026-05-24")
    source = payload["sources"][0]

    assert (
        source["raw_target_path"]
        == "llm-wiki/raw/tasknotes/steering/done/20260418-preview-selector-cache.md"
    )
    assert (
        source["summary_scaffold"]["frontmatter"]["source"]
        == "raw/tasknotes/steering/done/20260418-preview-selector-cache.md"
    )
    assert source["summary_scaffold"]["frontmatter"]["created"] == "2026-05-24"
    assert "## summary" in source["summary_scaffold"]["markdown_template"]
    assert "TODO_SUMMARY" in source["summary_scaffold"]["markdown_template"]
    assert "- status: inbox" in source["append_blocks"]["source_inbox"]
    assert "Tasknote Summary:" in source["append_blocks"]["master_index"]
    assert "TODO_RISK" in source["append_blocks"]["ingest_log"]
    assert "TODO_NOTE" in source["append_blocks"]["ingest_log"]


def test_prepare_steering_done_batch_scores_related_pages_from_history(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path
    _write_area_pages(repo_root)
    _write_ingest_log(
        repo_root,
        [
            {
                "title": "Preview Selector Flow",
                "source_id": "2026-04-10-preview-selector-flow",
                "source_path": "llm-wiki/raw/tasknotes/steering/done/20260410-preview-selector-flow.md",
                "updated_pages": [
                    "llm-wiki/wiki/areas/platform-sharing-and-approval-ops.md",
                    "llm-wiki/wiki/areas/approval-loop-and-child-agency.md",
                ],
                "related_page_count": 2,
            },
            {
                "title": "Preview Current Promote",
                "source_id": "2026-04-11-preview-current-promote",
                "source_path": "llm-wiki/raw/tasknotes/steering/done/20260411-preview-current-promote.md",
                "updated_pages": [
                    "llm-wiki/wiki/areas/platform-sharing-and-approval-ops.md",
                ],
                "related_page_count": 1,
            },
        ],
    )
    _write_tasknote(
        repo_root / "steering/done/20260418-preview-selector-cache.md",
        created_at="2026-04-18T09:00:00.000+00:00",
        title="2026年4月18日 Preview Selector Cache",
        discussion_line="preview selector current cache",
    )

    payload = prepare_steering_done_batch(repo_root, limit=10, current_date="2026-05-24")
    candidates = payload["sources"][0]["related_page_candidates"]

    assert candidates[0]["path"] == "llm-wiki/wiki/areas/platform-sharing-and-approval-ops.md"
    assert candidates[1]["path"] == "llm-wiki/wiki/areas/approval-loop-and-child-agency.md"
    assert "preview" in candidates[0]["reason"].lower()
    assert candidates[0]["score"] > candidates[1]["score"] > 0


def test_steering_batch_helper_cli_outputs_json(tmp_path: Path) -> None:
    repo_root = tmp_path
    _write_area_pages(repo_root)
    _write_ingest_log(repo_root, [])
    _write_tasknote(
        repo_root / "steering/done/20260418-preview-selector-cache.md",
        created_at="2026-04-18T09:00:00.000+00:00",
        title="2026年4月18日 Preview Selector Cache",
        discussion_line="preview selector current cache",
    )
    script_path = Path(__file__).resolve().parents[1] / "tools/llm_wiki_steering_batch_helper.py"

    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--repo-root",
            str(repo_root),
            "--limit",
            "1",
            "--current-date",
            "2026-05-24",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["selected_count"] == 1
    assert payload["sources"][0]["source_id"] == "2026-04-18-preview-selector-cache"


def _write_tasknote(
    path: Path,
    *,
    created_at: str,
    title: str,
    discussion_line: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                "status: done",
                f"dateCreated: {created_at}",
                f"scheduled: {created_at}",
                "---",
                "",
                f"# {title}",
                "",
                "## 4) Tasklist",
                "- [x] prepare preview selector cache",
                "",
                "## 8) Discussion",
                f"- {discussion_line}",
                "",
                "## 9) Closing",
                "- 状態: done",
            ]
        ),
        encoding="utf-8",
    )


def _write_area_pages(repo_root: Path) -> None:
    area_dir = repo_root / "llm-wiki/wiki/areas"
    area_dir.mkdir(parents=True, exist_ok=True)
    areas = {
        "platform-sharing-and-approval-ops.md": (
            "# Platform Sharing And Approval Ops\n\n"
            "preview selector current approval sharing platform cache\n"
        ),
        "approval-loop-and-child-agency.md": (
            "# Approval Loop And Child Agency\n\n"
            "preview current approval child agency selector\n"
        ),
        "battle-balance-and-spell-design.md": (
            "# Battle Balance And Spell Design\n\n"
            "battle spell damage enemy turn balance\n"
        ),
    }
    for file_name, body in areas.items():
        (area_dir / file_name).write_text(body, encoding="utf-8")


def _write_ingest_log(repo_root: Path, entries: list[dict[str, object]]) -> None:
    log_path = repo_root / "llm-wiki/wiki/logs/ingest-log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    blocks = ["# Ingest Log", ""]
    for entry in entries:
        blocks.extend(
            [
                f"## [2026-05-24] ingest | {entry['title']}",
                "",
                f"- source_id: `{entry['source_id']}`",
                f"- source_path: `{entry['source_path']}`",
                "- created_pages:",
                "  - `llm-wiki/wiki/summaries/tasknotes/steering/done/sample-summary.md`",
                "- updated_pages:",
            ]
        )
        for updated_page in entry["updated_pages"]:
            blocks.append(f"  - `{updated_page}`")
        blocks.extend(
            [
                f"- related_page_count: {entry['related_page_count']}",
                "- risks:",
                "  - sample risk",
                "- notes:",
                "  - sample note",
                "",
            ]
        )
    log_path.write_text("\n".join(blocks), encoding="utf-8")
