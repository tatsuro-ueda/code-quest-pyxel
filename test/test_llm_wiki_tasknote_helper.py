import json
from pathlib import Path

from tools.llm_wiki_tasknote_helper import prepare_raw_tasknote


def test_prepare_raw_tasknote_maps_known_repo_path() -> None:
    payload = prepare_raw_tasknote(
        Path("llm-wiki/raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md")
    )

    assert payload["source_id"] == "2026-04-12-g12-rebuild-codemaker-zip"
    assert (
        payload["summary_draft_path"]
        == "llm-wiki/wiki/summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md"
    )
    assert payload["source_type"] == "tasknote"


def test_prepare_raw_tasknote_extracts_expected_materials() -> None:
    payload = prepare_raw_tasknote(
        Path("llm-wiki/raw/tasknotes/done/20260412-g15-test-pinning.md")
    )

    assert payload["frontmatter"]["status"] == "done"
    assert "4) Tasklist" in payload["headings"]
    assert any("simple_yaml" in item for item in payload["tasklist_items"])
    assert payload["result_facts"] == []
    assert any("PyYAML" in item for item in payload["discussion_points"])
    assert "Result" in payload["missing_sections"]
    assert "Closing" in payload["missing_sections"]


def test_prepare_raw_tasknote_reports_missing_sections(tmp_path: Path) -> None:
    raw_path = tmp_path / "llm-wiki/raw/tasknotes/done/20260524-sample.md"
    raw_path.parent.mkdir(parents=True)
    raw_path.write_text(
        "---\nstatus: open\n---\n\n# Sample\n\n## 4) Tasklist\n- [ ] one\n",
        encoding="utf-8",
    )

    payload = prepare_raw_tasknote(raw_path)

    assert payload["result_facts"] == []
    assert payload["discussion_points"] == []
    assert payload["closing_points"] == []
    assert payload["missing_sections"] == ["Result", "Discussion", "Closing"]


def test_prepare_raw_tasknote_uses_adapter_section_mapping(tmp_path: Path) -> None:
    adapter_path = tmp_path / "llm-wiki/adapter.yml"
    adapter_path.parent.mkdir(parents=True, exist_ok=True)
    adapter_path.write_text(
        "\n".join(
            [
                "raw_root: llm-wiki/raw",
                "summary_root: llm-wiki/wiki/summaries",
                "master_index_path: llm-wiki/wiki/indexes/master-index.md",
                "source_inbox_path: llm-wiki/wiki/logs/source-inbox.md",
                "ingest_log_path: llm-wiki/wiki/logs/ingest-log.md",
                "health_check_log_path: llm-wiki/wiki/logs/health-check-log.md",
                "area_root: llm-wiki/wiki/areas",
                "query_root: llm-wiki/wiki/query",
                "candidate_root: llm-wiki/wiki/candidates",
                "tasknote_required_sections:",
                "  result: Outcome",
                "  discussion: Notes",
                "  closing: Wrap Up",
            ]
        ),
        encoding="utf-8",
    )
    raw_path = tmp_path / "llm-wiki/raw/tasknotes/done/20260524-sample.md"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(
        "---\nstatus: open\n---\n\n# Sample\n\n## 4) Tasklist\n- [ ] one\n\n## 6) Outcome\n- fixed\n\n## 7) Notes\n- explain why\n\n## 8) Wrap Up\n- next gate\n",
        encoding="utf-8",
    )

    payload = prepare_raw_tasknote(raw_path)

    assert payload["result_facts"] == ["fixed"]
    assert payload["discussion_points"] == ["explain why"]
    assert payload["closing_points"] == ["next gate"]
    assert payload["missing_sections"] == []


def test_prepare_raw_tasknote_returns_json_safe_frontmatter() -> None:
    payload = prepare_raw_tasknote(
        Path("llm-wiki/raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md")
    )

    encoded = json.dumps(payload, ensure_ascii=False)

    assert "2026-04-12T22:00:00" in encoded
