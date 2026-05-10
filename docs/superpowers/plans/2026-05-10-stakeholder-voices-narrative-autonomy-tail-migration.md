# Stakeholder Voices Narrative Autonomy Tail Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the remaining source-trace gaps by migrating `CJ09/CJ27/CJ28/CJ30/CJ42`, adding `docs/product-requirements-narrative.md` to source coverage, and linking `JOB:JIS_PARENT_AUTONOMY` into the approval loop.

**Architecture:** Add one narrative source document and one autonomy-support request, then extend the requirement/acceptance catalog with the remaining narrative and end-to-end journey contracts. Reuse the existing approval-loop requirements for autonomy linkage instead of inventing a parallel structure. Prove completion with red tests that expect zero missing refs.

**Tech Stack:** Python 3, `yaml`, `unittest`, JSON CLI reports, markdown task notes under `steering/`

---

### Task 1: Add Red Tests For Zero Remaining Gaps

**Files:**
- Modify: `test/test_source_trace_coverage_report.py`
- Modify: `test/test_stakeholder_voices_checker.py`
- Read: `docs/customer-jobs.md`
- Read: `docs/customer-journeys.md`
- Read: `docs/product-requirements-narrative.md`

- [ ] **Step 1: Add a real-repo coverage assertion for `product_requirements_narrative`**

```python
def test_real_repo_report_covers_all_narrative_prd_refs(self):
    report_module = load_report_module()
    payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_narrative")
    self.assertEqual(document["referenced_refs"], ["CJG09", "CJG14", "CJG27", "CJG30"])
    self.assertEqual(document["missing_refs"], [])
```

- [ ] **Step 2: Assert zero missing refs for `customer_jobs` and `customer_journeys`**

```python
def test_real_repo_report_covers_all_customer_job_refs(self):
    report_module = load_report_module()
    payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "customer_jobs")
    self.assertEqual(document["missing_refs"], [])


def test_real_repo_report_covers_all_customer_journey_refs(self):
    report_module = load_report_module()
    payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "customer_journeys")
    self.assertEqual(document["missing_refs"], [])
```

- [ ] **Step 3: Raise the real-repo floor again**

```python
def test_real_rules_expose_requirement_first_facts(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))
    self.assertGreaterEqual(len(data["facts"]["source_documents"]), 9)
    self.assertGreaterEqual(len(data["facts"]["requirements"]), 42)
    self.assertGreaterEqual(len(data["facts"]["acceptance"]), 42)
```

- [ ] **Step 4: Run the focused suite to confirm red**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: FAIL because narrative source coverage and the remaining journey/job refs are not yet migrated

### Task 2: Add Narrative Source Coverage And Autonomy Request

**Files:**
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add the narrative source document contract**

```yaml
    - id: product_requirements_narrative
      path: docs/product-requirements-narrative.md
      extraction:
        regex:
          - '\bCJG\d+\b'
```

- [ ] **Step 2: Add the autonomy-support request**

```yaml
    - id: rq_parent_supports_child_autonomy
      stakeholder_id: st_parent_customer
      source_trace_refs:
        - customer_jobs:JOB:JIS_PARENT_AUTONOMY
        - customer_journeys:CJ31
        - customer_journeys:CJ32
        - customer_journeys:CJ33
        - customer_journeys:CJ34
```

- [ ] **Step 3: Link that request into existing approval requirements**

```yaml
    - id: req_child_keeps_decision_power
      derived_from_request_ids:
        - rq_child_decision_power
        - rq_parent_supports_child_autonomy

    - id: req_role_swap_keeps_child_handle
      derived_from_request_ids:
        - rq_child_decision_power
        - rq_parent_supports_child_autonomy
```

- [ ] **Step 4: Run focused tests again to keep the failure localized**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: still FAIL, but now only because the remaining narrative/endgame requirements are missing

### Task 3: Migrate Narrative Tail Requirements / Acceptance

**Files:**
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add dialogue editing, branching, and ending requirements**

```yaml
    - id: req_dialogue_edit_replay_fast
      source_trace_refs:
        - customer_journeys:CJ09
        - product_requirements_narrative:CJG09

    - id: req_story_branch_choice_persists
      source_trace_refs:
        - customer_journeys:CJ27
        - product_requirements_narrative:CJG27

    - id: req_ending_ownership_visible
      source_trace_refs:
        - customer_journeys:CJ30
        - product_requirements_narrative:CJG30
```

- [ ] **Step 2: Add area-expansion and full-adventure requirements**

```yaml
    - id: req_new_area_addition_safe
      source_trace_refs:
        - customer_journeys:CJ28

    - id: req_full_adventure_completable
      source_trace_refs:
        - customer_journeys:CJ42
        - framework_rule:Golden Path Test
```

- [ ] **Step 3: Update the guidance requirement to carry `CJG14` from the narrative PRD**

```yaml
    - id: req_child_goal_guidance_visible
      source_trace_refs:
        - customer_journeys:CJ14
        - product_requirements_narrative:CJG14
```

- [ ] **Step 4: Add matching acceptance entries**

```yaml
    - id: acc_dialogue_edit_replay_fast
      requirement_id: req_dialogue_edit_replay_fast

    - id: acc_story_branch_choice_persists
      requirement_id: req_story_branch_choice_persists

    - id: acc_new_area_addition_safe
      requirement_id: req_new_area_addition_safe

    - id: acc_ending_ownership_visible
      requirement_id: req_ending_ownership_visible

    - id: acc_full_adventure_completable
      requirement_id: req_full_adventure_completable
```

- [ ] **Step 5: Run the focused suite to verify green**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: PASS

### Task 4: Verify Zero Missing Refs, Update Note, And Commit

**Files:**
- Modify: `steering/20260510-stakeholder-voices-narrative-autonomy-tail-migration.md`
- Test: `test/test_source_trace_coverage_report.py`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Run the stakeholder-voices verification suite**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`  
Expected: PASS

Run: `python tools/report_source_trace_coverage.py`  
Expected: `total_missing_refs: 0`

Run: `python tools/check_stakeholder_voices.py`  
Expected: JSON with `warning_rules: 0`

- [ ] **Step 2: Update the task note with actual completion evidence**

```markdown
## 5) Result（成果物）

- added narrative source coverage
- linked autonomy support into approval loop
- reduced all remaining source trace gaps to zero
```

- [ ] **Step 3: Commit the slice**

Run: `git add docs/stakeholder_voices.yml test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py steering/20260510-stakeholder-voices-narrative-autonomy-tail-migration.md docs/superpowers/plans/2026-05-10-stakeholder-voices-narrative-autonomy-tail-migration.md`  
Run: `git commit -m "feat: finish stakeholder voices trace coverage"`
