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


def test_prepare_raw_tasknote_returns_json_safe_frontmatter() -> None:
    payload = prepare_raw_tasknote(
        Path("llm-wiki/raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md")
    )

    encoded = json.dumps(payload, ensure_ascii=False)

    assert "2026-04-12T22:00:00" in encoded
