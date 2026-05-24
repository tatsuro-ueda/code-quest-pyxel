# Steering Batch Ingest Helper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Python helper that selects the oldest un-ingested steering done tasknotes in batches of 10 and prepares summary scaffolds, related-page candidates, and wiki append blocks.

**Architecture:** Reuse the existing raw-tasknote parsing helper for source-level material extraction, then layer a batch helper on top that scans `steering/done/`, derives logical raw paths under `llm-wiki/raw/tasknotes/steering/done/`, ranks related pages from prior ingest history plus lexical overlap, and emits deterministic JSON/markdown templates for downstream LLM review. Keep final meaning/prose decisions outside Python.

**Tech Stack:** Python 3, pathlib, json, pytest, markdown skill docs

---

### Task 1: Lock helper behavior with failing tests

**Files:**
- Create: `test/test_llm_wiki_steering_batch_helper.py`
- Read: `llm-wiki/wiki/indexes/master-index.md`
- Read: `llm-wiki/wiki/logs/ingest-log.md`

- [ ] Add tests for oldest-10 selection, summary scaffold shape, related page candidate shape, and append block generation.
- [ ] Run the focused test file and verify it fails because the batch helper does not exist yet.

### Task 2: Implement the batch helper

**Files:**
- Create: `tools/llm_wiki_steering_batch_helper.py`
- Modify: `tools/llm_wiki_tasknote_helper.py`

- [ ] Refactor tasknote helper so source-level material extraction can be reused with a logical raw path.
- [ ] Implement steering batch scanning, un-ingested detection, ordering, scaffold generation, related-page scoring, and append block output.
- [ ] Run the focused tests until green.

### Task 3: Wire the skill and close the tasknote

**Files:**
- Modify: `/home/exedev/dotfiles/claude/.claude/skills/llm-wiki-capture-and-ingest-source/SKILL.md`
- Modify: `steering/2026年5月24日 開発基盤：steeringの完了タスクノート10件取り込み定型をPythonに寄せる.md`

- [ ] Update the skill so the steering batch route calls the new helper first.
- [ ] Update the tasknote with Result/Discussion/Closing and mark it done if implementation and dry-run verification finish.

### Task 4: Verify and commit

**Files:**
- Verify touched helper/tests/docs/tasknote files

- [ ] Run focused pytest for the new helper.
- [ ] Run `python -m pytest test/ -q`.
- [ ] Run tasknote lint and markdownlint on the touched skill/tasknote files.
- [ ] Run the Python coding guide check mentally against edited Python files and make any final cleanups.
- [ ] Commit repo changes intentionally.
