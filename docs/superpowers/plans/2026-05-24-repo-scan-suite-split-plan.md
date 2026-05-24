# Repo-Scan Suite Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the next tranche of expensive tests so daily pytest excludes repo-wide scan checks and high-value integration smoke while preserving explicit smoke and nightly entrypoints.

**Architecture:** Keep production code unchanged. Mark only the expensive real-repo scan tests in `architecture_rules_checker` and `source_trace_coverage_report` as nightly, and mark the high-value `web_runtime_server` plus bundle-exec smoke tests as smoke. Then wire the new markers into `pytest.ini`, `Makefile`, and `README`, and measure the three suites separately.

**Tech Stack:** Python, pytest markers, Makefile, Markdown tasknotes

---

### Task 1: Put The Task Into Execution State

**Files:**
- Create: `docs/superpowers/plans/2026-05-24-repo-scan-suite-split-plan.md`
- Modify: `steering/2026年5月24日 開発基盤：日常pytestをさらに軽くするため重い全走査テストを別枠化する.md`

- [ ] Step 1: Keep this plan file as the execution handoff for the work
- [ ] Step 2: Update the tasknote frontmatter from `status: open` to `status: in-progress`
- [ ] Step 3: Update the tasknote gate so execution can proceed without another checkpoint
- [ ] Step 4: Add the plan path or execution note in `Tasklist` / `作業ログ`

### Task 2: Move Repo-Wide Scan Tests Into A Nightly Bucket

**Files:**
- Modify: `test/test_architecture_rules_checker.py`
- Modify: `test/test_source_trace_coverage_report.py`
- Modify: `pytest.ini`

- [ ] Step 1: Mark the expensive real-repo scan tests in `test_architecture_rules_checker.py` with a new nightly marker
- [ ] Step 2: Mark the real-repo coverage-report tests in `test_source_trace_coverage_report.py` with the same nightly marker
- [ ] Step 3: Extend `pytest.ini` so the default daily run excludes the nightly marker
- [ ] Step 4: Run focused nightly tests to confirm they still pass when explicitly selected

### Task 3: Move High-Value Integration Smoke Into The Smoke Bucket

**Files:**
- Modify: `test/test_web_runtime_server.py`
- Modify: `test/test_codemaker_bundle_smoke.py`
- Modify: `pytest.ini`
- Modify: `Makefile`
- Modify: `README.md`

- [ ] Step 1: Mark `WebRuntimeServerTest` as high-value smoke
- [ ] Step 2: Mark only `BundledSourceLoadsTest` in `test_codemaker_bundle_smoke.py` as high-value smoke, leaving the alias unit tests in daily
- [ ] Step 3: Extend `pytest.ini` so daily excludes the new smoke marker too
- [ ] Step 4: Update `make test-smoke` to run both `real_repo_smoke` and `high_value_smoke`
- [ ] Step 5: Add a `make test-nightly` entrypoint for the repo-scan tests
- [ ] Step 6: Document the daily / smoke / nightly split in `README.md`

### Task 4: Verify, Measure, And Record

**Files:**
- Modify: `steering/2026年5月24日 開発基盤：日常pytestをさらに軽くするため重い全走査テストを別枠化する.md`

- [ ] Step 1: Run focused checks for the changed test files
- [ ] Step 2: Run `make test-smoke` and `make test-nightly`
- [ ] Step 3: Run the updated default daily suite with `python3 -m pytest test/ -q --durations=80`
- [ ] Step 4: Compare the new daily time against the recorded `12.59s` baseline
- [ ] Step 5: Update `作業ログ`, `評価と成果物`, `Discussion`, and `Closing`
- [ ] Step 6: Mark the tasknote `status: done` only if the split and measurements are complete
