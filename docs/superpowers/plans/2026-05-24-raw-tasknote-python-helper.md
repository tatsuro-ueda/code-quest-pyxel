# Raw Tasknote Python Helper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Python helper that reads an existing raw tasknote and returns deterministic JSON materials for the `llm-wiki-capture-and-ingest-source` tasknote flow.

**Architecture:** Keep the behavior narrow. One helper module in `tools/` parses frontmatter and selected markdown sections, derives `source_id` and `summary_draft_path`, and prints JSON for the AI-side ingest flow. Tests cover path mapping, section extraction, and missing-section behavior before the skill document is updated to call the helper.

**Tech Stack:** Python 3, PyYAML, pytest, markdown skill docs

---

### Task 1: Lock The Helper Contract With Tests

**Files:**
- Create: `test/test_llm_wiki_tasknote_helper.py`
- Test: `test/test_llm_wiki_tasknote_helper.py`

- [ ] **Step 1: Write the failing contract tests**

```python
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
    assert payload["tasklist_items"]
    assert payload["discussion_points"]


def test_prepare_raw_tasknote_reports_missing_sections(tmp_path: Path) -> None:
    raw_path = tmp_path / "llm-wiki/raw/tasknotes/done/20260524-sample.md"
    raw_path.parent.mkdir(parents=True)
    raw_path.write_text(
        "---\\nstatus: open\\n---\\n\\n# Sample\\n\\n## 4) Tasklist\\n- [ ] one\\n",
        encoding="utf-8",
    )
    payload = prepare_raw_tasknote(raw_path)
    assert payload["result_facts"] == []
    assert payload["discussion_points"] == []
    assert payload["closing_points"] == []
    assert payload["missing_sections"] == ["Closing", "Discussion", "Result"]
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `python -m pytest test/test_llm_wiki_tasknote_helper.py -q`
Expected: FAIL with `ModuleNotFoundError` or missing helper symbols because the helper does not exist yet.

### Task 2: Implement The Minimal Helper

**Files:**
- Create: `tools/llm_wiki_tasknote_helper.py`
- Modify: `test/test_llm_wiki_tasknote_helper.py`
- Test: `test/test_llm_wiki_tasknote_helper.py`

- [ ] **Step 1: Implement the parsing and path helpers**

```python
def prepare_raw_tasknote(raw_tasknote_path: Path) -> dict[str, object]:
    text = raw_tasknote_path.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(text)
    headings = _collect_headings(body)
    sections = _collect_sections(body)
    return {
        "source_id": _derive_source_id(raw_tasknote_path),
        "summary_draft_path": _derive_summary_draft_path(raw_tasknote_path),
        "source_type": "tasknote",
        "frontmatter": frontmatter,
        "headings": headings,
        "tasklist_items": _extract_tasklist_items(sections.get("Tasklist", [])),
        "result_facts": _normalize_lines(sections.get("Result", [])),
        "discussion_points": _normalize_lines(sections.get("Discussion", [])),
        "closing_points": _normalize_lines(sections.get("Closing", [])),
        "missing_sections": _missing_sections(sections),
    }
```

- [ ] **Step 2: Add the CLI wrapper for JSON output**

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_tasknote_path")
    args = parser.parse_args(argv)
    payload = prepare_raw_tasknote(Path(args.raw_tasknote_path))
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run the focused tests and verify GREEN**

Run: `python -m pytest test/test_llm_wiki_tasknote_helper.py -q`
Expected: PASS

### Task 3: Wire The Skill Documentation To The Helper

**Files:**
- Modify: `/home/exedev/dotfiles/claude/.claude/skills/llm-wiki-capture-and-ingest-source/SKILL.md`
- Modify: `steering/2026年5月24日 開発基盤：raw tasknote ingestの単純作業をPythonに寄せる.md`

- [ ] **Step 1: Update the tasknote branch of the skill**

```md
- tasknote の `raw-source-path mode` では `python tools/llm_wiki_tasknote_helper.py <raw_tasknote_path>` を先に実行する
- Python helper が `source_id` `summary_draft_path` `frontmatter` `headings` `tasklist_items` `result_facts` `discussion_points` `closing_points` `missing_sections` を返す
- AI は helper JSON を材料にして gate 1 と summary preview を続ける
```

- [ ] **Step 2: Record dry-run evidence in the steering note**

```md
- [x] dry-run source 3 本で必要な材料差分を洗い出す
- [x] `llm-wiki-capture-and-ingest-source` 側の呼び出し位置を決める
- `python tools/llm_wiki_tasknote_helper.py llm-wiki/raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md`
- `python tools/llm_wiki_tasknote_helper.py llm-wiki/raw/tasknotes/done/20260412-g15-test-pinning.md`
- `python tools/llm_wiki_tasknote_helper.py llm-wiki/raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md`
```

### Task 4: Verify And Close The Loop

**Files:**
- Modify: `tools/llm_wiki_tasknote_helper.py`
- Modify: `test/test_llm_wiki_tasknote_helper.py`
- Modify: `/home/exedev/dotfiles/claude/.claude/skills/llm-wiki-capture-and-ingest-source/SKILL.md`
- Modify: `steering/2026年5月24日 開発基盤：raw tasknote ingestの単純作業をPythonに寄せる.md`

- [ ] **Step 1: Run Python style guidance checks**

Run: `sed -n '1,220p' /home/exedev/dotfiles/claude/.claude/skills/check-python-coding-guide/SKILL.md`
Expected: the Python coding guide checklist is applied after the helper edits.

- [ ] **Step 2: Run focused and repo-level verification**

Run: `python -m pytest test/test_llm_wiki_tasknote_helper.py -q && python -m pytest test/ -q`
Expected: the new helper tests pass and the repo test suite stays green.

- [ ] **Step 3: Re-run document lint checks**

Run: `node /home/exedev/dotfiles/shared/linter/coding-rules/tasknote/run_tasknote_lint.mjs --config ./tasknote-lint.config.json 'steering/2026年5月24日 開発基盤：raw tasknote ingestの単純作業をPythonに寄せる.md'`
Expected: PASS

- [ ] **Step 4: Check the skill markdown diff**

Run: `markdownlint-cli2 /home/exedev/dotfiles/claude/.claude/skills/llm-wiki-capture-and-ingest-source/SKILL.md`
Expected: PASS or no new markdown violations.
