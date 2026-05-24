# LLM Wiki Health Check Python Helper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic Python helper that prepares compiled wiki scope, graph signals, and a health-check log scaffold for `llm-wiki-health-check`.

**Architecture:** Reuse the existing helper pattern from `tools/llm_wiki_tasknote_helper.py` and `tools/llm_wiki_steering_batch_helper.py`: a single CLI-oriented module with a small public API and pure parsing helpers below it. Keep the helper read-only and signal-oriented; semantic classification remains in the skill/LLM layer.

**Tech Stack:** Python 3, `pathlib`, `re`, `json`, `pytest`

---

### Task 1: Lock Contract With Failing Tests

**Files:**
- Create: `test/test_llm_wiki_health_check_helper.py`
- Reference: `tools/llm_wiki_tasknote_helper.py`
- Reference: `tools/llm_wiki_steering_batch_helper.py`

- [ ] **Step 1: Write the failing tests**

```python
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.llm_wiki_health_check_helper import prepare_health_check_material


def test_prepare_health_check_material_detects_scope_and_active_pages(tmp_path: Path) -> None:
    repo_root = _build_small_wiki_repo(tmp_path)

    payload = prepare_health_check_material(repo_root, current_date="2026-05-24")

    assert payload["scope_label"] == "current wiki"
    assert "llm-wiki/wiki/indexes/master-index.md" in payload["scope_paths"]
    assert payload["graph_entrypoints"] == ["llm-wiki/wiki/indexes/master-index.md"]
    assert "llm-wiki/wiki/areas/topic-a.md" in payload["active_page_paths"]


def test_prepare_health_check_material_collects_signals_and_scaffold(tmp_path: Path) -> None:
    repo_root = _build_small_wiki_repo(tmp_path)

    payload = prepare_health_check_material(repo_root, current_date="2026-05-24")

    assert payload["orphan_signals"][0]["path"] == "llm-wiki/wiki/areas/orphan-topic.md"
    assert payload["missing_target_signals"][0]["missing_path"] == "llm-wiki/wiki/areas/missing-topic.md"
    assert any(signal["path"] == "llm-wiki/wiki/query/question-a.md" for signal in payload["crossref_signals"])
    assert payload["log_scaffold"].startswith("## [2026-05-24] lint | current wiki")
    assert "- contradictions: none" in payload["log_scaffold"]
    assert "- notes:" in payload["log_scaffold"]


def test_health_check_helper_cli_outputs_json(tmp_path: Path) -> None:
    repo_root = _build_small_wiki_repo(tmp_path)
    script_path = Path(__file__).resolve().parents[1] / "tools/llm_wiki_health_check_helper.py"

    completed = subprocess.run(
        [sys.executable, str(script_path), "--repo-root", str(repo_root), "--current-date", "2026-05-24"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)

    assert payload["scope_label"] == "current wiki"
    assert payload["log_scaffold"].startswith("## [2026-05-24] lint | current wiki")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test/test_llm_wiki_health_check_helper.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools.llm_wiki_health_check_helper'`

- [ ] **Step 3: Confirm fixture shape with a helper function in the test file**

```python
def _build_small_wiki_repo(repo_root: Path) -> Path:
    _write_page(
        repo_root / "llm-wiki/wiki/indexes/master-index.md",
        "# Master Index\n\n- [Topic A](../areas/topic-a.md)\n- [Question A](../query/question-a.md)\n- [Summary A](../summaries/knowledge/summary-a.md)\n",
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
```

- [ ] **Step 4: Re-run the test file and keep it red**

Run: `python -m pytest test/test_llm_wiki_health_check_helper.py -q`
Expected: FAIL for missing implementation module, not fixture syntax errors

- [ ] **Step 5: Commit**

```bash
git add test/test_llm_wiki_health_check_helper.py
git commit -m "test: add health check helper contract"
```

### Task 2: Implement Minimal Helper And CLI

**Files:**
- Create: `tools/llm_wiki_health_check_helper.py`
- Test: `test/test_llm_wiki_health_check_helper.py`

- [ ] **Step 1: Write the minimal public API and CLI**

```python
def prepare_health_check_material(
    repo_root: Path,
    *,
    scope_hint: str | None = None,
    current_date: str | None = None,
) -> dict[str, object]:
    ...


def main(argv: list[str] | None = None) -> int:
    ...
```

- [ ] **Step 2: Implement scope detection and active page collection**

```python
def _detect_scope_paths(repo_root: Path, scope_hint: str | None) -> tuple[str, list[str], list[Path]]:
    if scope_hint:
        target_path = repo_root / scope_hint
        return scope_hint, [Path("llm-wiki/wiki").joinpath(scope_hint).as_posix()], [target_path]
    return (
        "current wiki",
        [
            "llm-wiki/wiki/indexes/master-index.md",
            "llm-wiki/wiki/areas/*.md",
            "llm-wiki/wiki/query/*.md",
            "llm-wiki/wiki/summaries/knowledge/*.md",
            "llm-wiki/wiki/logs/health-check-log.md",
        ],
        [
            repo_root / "llm-wiki/wiki/indexes/master-index.md",
            *(repo_root / "llm-wiki/wiki/areas").glob("*.md"),
            *(repo_root / "llm-wiki/wiki/query").glob("*.md"),
            *(repo_root / "llm-wiki/wiki/summaries/knowledge").glob("*.md"),
            repo_root / "llm-wiki/wiki/logs/health-check-log.md",
        ],
    )
```

- [ ] **Step 3: Implement link parsing and signal extraction**

```python
_WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)")
_MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")


def _collect_outlinks(page_text: str, page_path: str) -> list[str]:
    ...


def _build_signals(active_pages: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    ...
```

- [ ] **Step 4: Implement the health-check log scaffold builder**

```python
def _build_log_scaffold(
    *,
    current_date: str,
    scope_label: str,
    scope_paths: list[str],
) -> str:
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
```

- [ ] **Step 5: Run the focused test file**

Run: `python -m pytest test/test_llm_wiki_health_check_helper.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tools/llm_wiki_health_check_helper.py test/test_llm_wiki_health_check_helper.py
git commit -m "feat: add llm wiki health check helper"
```

### Task 3: Integrate Notes And Verify

**Files:**
- Modify: `steering/2026年5月24日 開発基盤：llm-wiki-health-checkの下ごしらえをPythonに寄せる.md`
- Test: `test/test_llm_wiki_health_check_helper.py`
- Verify: `tools/llm_wiki_health_check_helper.py`

- [ ] **Step 1: Update the tasknote Result / Discussion / Closing**

```md
- [x] helper module と focused tests を追加した
- [x] scope / signal / log scaffold の JSON contract を実装した
- [x] CLI dry-run と focused pytest を通した
```

- [ ] **Step 2: Run the focused verification commands**

Run:
`python -m pytest test/test_llm_wiki_health_check_helper.py -q`
`python tools/llm_wiki_health_check_helper.py --repo-root . --current-date 2026-05-24`

Expected:
- pytest は全件 PASS
- CLI は JSON を出力し、`scope_label` と `log_scaffold` を含む

- [ ] **Step 3: Run repo-level regression checks for the helper family**

Run:
`python -m pytest test/test_llm_wiki_tasknote_helper.py test/test_llm_wiki_steering_batch_helper.py test/test_llm_wiki_health_check_helper.py -q`

Expected: PASS

- [ ] **Step 4: Run Python coding guide check on the new helper**

Run relevant naming / structure checks from `check-python-coding-guide` against:
`tools/llm_wiki_health_check_helper.py`

Expected: no actionable violations remain

- [ ] **Step 5: Commit**

```bash
git add 'steering/2026年5月24日 開発基盤：llm-wiki-health-checkの下ごしらえをPythonに寄せる.md'
git commit -m "docs: record health check helper implementation"
```
