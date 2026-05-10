# Stakeholder Voices Trace Status Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate trace completeness from implementation status so `later/wont` stakeholder-voice items still participate in source-trace coverage and integrity checks without being forced to masquerade as active.

**Architecture:** Add red tests around `later` items in both the coverage report and the checker, update the tracked-status logic in the two tooling modules, and then restore `CJ14/CJ19` backlog items to `later` while keeping zero-missing coverage intact. Leave implementation-oriented rules untouched so only trace semantics change.

**Tech Stack:** Python 3, `yaml`, `unittest`, JSON CLI reports, markdown task notes under `steering/`

---

### Task 1: Add Red Tests For Tracked Later Items

**Files:**
- Modify: `test/test_source_trace_coverage_report.py`
- Modify: `test/test_stakeholder_voices_checker.py`

- [ ] **Step 1: Add a fixture test proving `later` items count toward source-trace coverage**

```python
def test_build_report_counts_later_status_trace_refs(self):
    report_module = load_report_module()
    # create a temporary rules file with one later requirement that holds source_trace_refs
    # expect the referenced ref to appear in the report
```

- [ ] **Step 2: Add a checker test proving `later` items are validated for trace integrity**

```python
def test_run_checker_warns_when_later_requirement_has_missing_source_trace(self):
    checker = load_checker_module()
    # build a temporary rules file with a later requirement and empty source_trace_refs
    # expect source_traceability_integrity to warn
```

- [ ] **Step 3: Run the focused suite to confirm red**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: FAIL because tooling still ignores `later` items

### Task 2: Implement Tracked-Status Logic

**Files:**
- Modify: `tools/stakeholder_voices/source_trace_coverage.py`
- Modify: `tools/stakeholder_voices/check_stakeholder_voices.py`

- [ ] **Step 1: Replace the active-only coverage iterator with a tracked-status iterator**

```python
TRACKED_TRACE_STATUSES = {"active", "later", "wont"}
```

- [ ] **Step 2: Use the same tracked-status rule in `source_traceability_integrity`**

```python
if item.get("status", "active") not in TRACKED_TRACE_STATUSES:
    continue
```

- [ ] **Step 3: Keep implementation-focused rules unchanged**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: PASS

### Task 3: Restore Deferred Items And Verify Real Repo State

**Files:**
- Modify: `docs/stakeholder_voices.yml`
- Modify: `steering/20260510-stakeholder-voices-trace-status-separation.md`

- [ ] **Step 1: Return deferred items to `later`**

```yaml
    - id: req_child_goal_guidance_visible
      status: later

    - id: acc_child_goal_guidance_visible
      status: later

    - id: req_scene_transition_polish_deferred
      status: later

    - id: acc_scene_transition_polish_deferred
      status: later
```

- [ ] **Step 2: Run the stakeholder-voices verification suite**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`  
Expected: PASS

Run: `python tools/report_source_trace_coverage.py`  
Expected: `total_missing_refs: 0`

Run: `python tools/check_stakeholder_voices.py`  
Expected: `warning_rules: 0`

- [ ] **Step 3: Update the task note and commit**

Run: `git add tools/stakeholder_voices/source_trace_coverage.py tools/stakeholder_voices/check_stakeholder_voices.py docs/stakeholder_voices.yml test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py steering/20260510-stakeholder-voices-trace-status-separation.md docs/superpowers/plans/2026-05-10-stakeholder-voices-trace-status-separation.md`
Run: `git commit -m "feat: separate trace coverage from implementation status"`
