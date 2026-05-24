# Test Suite Trim Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove low-value tests from the daily suite, move thin real-repo CLI smoke checks to a separate suite, and preserve meaningful regression coverage.

**Architecture:** Keep runtime behavior unchanged. Delete helper-only and subset tests, migrate any still-useful assertions into the CJG/current-path tests, then add a pytest marker that excludes real-repo smoke checks from the default `pytest test/` run while keeping an explicit smoke entrypoint.

**Tech Stack:** Python, pytest, Makefile, tasknote lint

---

### Task 1: Move The Task Into Execution State

**Files:**
- Modify: `steering/2026年5月24日 開発基盤：存在価値が薄いテストを整理して実行時間を削る.md`
- Create: `docs/superpowers/plans/2026-05-24-test-suite-trim-plan.md`

- [ ] Step 1: Update the tasknote frontmatter from `status: open` to `status: in-progress`
- [ ] Step 2: Update the tasknote gate so execution proceeds without another user checkpoint
- [ ] Step 3: Record this plan path in the tasknote `Tasklist` or `作業ログ`

### Task 2: Delete Helper-Only And Subset Tests

**Files:**
- Delete: `test/test_shop_logic.py`
- Delete: `test/test_spell_logic.py`
- Delete: `test/test_cjg_town_entry_sets_current_town.py`
- Delete: `test/test_landmark_events.py`
- Modify: `test/test_cjg_save_store_contract.py`
- Modify: `test/test_cjg_save_store_file.py`
- Delete: `test/test_save_store.py`

- [ ] Step 1: Remove the two helper-only test files
- [ ] Step 2: Remove the duplicate town and landmark subset files
- [ ] Step 3: Copy the still-valuable save-store assertions into the CJG files
- [ ] Step 4: Remove the old aggregated save-store file once its unique assertions have moved
- [ ] Step 5: Run the focused affected tests and confirm they stay green

### Task 3: Split Thin Real-Repo CLI Smoke From The Daily Suite

**Files:**
- Create: `pytest.ini`
- Modify: `test/test_architecture_rules_checker.py`
- Modify: `test/test_fix_architecture_rules.py`
- Modify: `test/test_repair_architecture_rules.py`
- Modify: `test/test_stakeholder_voices_checker.py`
- Modify: `test/test_fix_stakeholder_voices.py`
- Modify: `test/test_repair_stakeholder_voices.py`
- Modify: `Makefile`
- Modify: `README.md`

- [ ] Step 1: Add a `real_repo_smoke` pytest marker and exclude it from default collection with `addopts`
- [ ] Step 2: Mark the six real-repo CLI smoke tests with that marker
- [ ] Step 3: Add a dedicated `make test-smoke` entrypoint that runs only those tests
- [ ] Step 4: Document the split in `README.md`
- [ ] Step 5: Run the smoke suite explicitly and confirm it still passes

### Task 4: Verify, Measure, And Record

**Files:**
- Modify: `steering/2026年5月24日 開発基盤：存在価値が薄いテストを整理して実行時間を削る.md`

- [ ] Step 1: Run the updated daily suite with `pytest test/ -q --durations=40`
- [ ] Step 2: Compare the new duration to the recorded `12.78s` baseline
- [ ] Step 3: Update the tasknote `作業ログ`, `評価と成果物`, `Discussion`, and `Closing`
- [ ] Step 4: Mark the tasknote `status: done` only if deletion, smoke split, and measurement are all complete
