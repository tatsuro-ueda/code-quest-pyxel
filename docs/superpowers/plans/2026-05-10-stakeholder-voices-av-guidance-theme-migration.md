# Stakeholder Voices AV Guidance Theme Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the remaining AV/guidance journeys `CJ14/CJ15/CJ16/CJ17/CJ18/CJ19/CJ24`, add `docs/product-requirements-av.md` to source trace coverage, and carry `JOB:JPL_CHILD_PLAYER` plus `JOB:JSC_PARENT_GROWTH` into `docs/stakeholder_voices.yml`.

**Architecture:** Add one new source document contract, two new requests, and a focused set of AV/guidance requirements and acceptance scenarios. Use red tests to pin the expected coverage state first, including the reduced missing refs for `customer_jobs` and `customer_journeys`, then make the YAML changes and re-run the deterministic checker/report.

**Tech Stack:** Python 3, `yaml`, `unittest`, JSON CLI reports, markdown task notes under `steering/`

---

### Task 1: Add Red Tests For AV Coverage And Remaining Gap Counts

**Files:**
- Modify: `test/test_source_trace_coverage_report.py`
- Modify: `test/test_stakeholder_voices_checker.py`
- Read: `docs/customer-jobs.md`
- Read: `docs/customer-journeys.md`
- Read: `docs/product-requirements-av.md`

- [ ] **Step 1: Add a real-repo coverage assertion for `product_requirements_av`**

```python
def test_real_repo_report_covers_all_av_prd_refs(self):
    report_module = load_report_module()
    payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_av")
    self.assertEqual(
        document["referenced_refs"],
        ["CJG15", "CJG16", "CJG17", "CJG18", "CJG19", "CJG20", "CJG24", "CJG44"],
    )
    self.assertEqual(document["missing_refs"], [])
```

- [ ] **Step 2: Assert the reduced `customer_jobs` and `customer_journeys` missing sets**

```python
def test_real_repo_report_reduces_customer_job_missing_refs_to_autonomy_only(self):
    report_module = load_report_module()
    payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "customer_jobs")
    self.assertEqual(document["missing_refs"], ["JOB:JIS_PARENT_AUTONOMY"])


def test_real_repo_report_reduces_customer_journey_missing_refs_to_story_tail(self):
    report_module = load_report_module()
    payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "customer_journeys")
    self.assertEqual(document["missing_refs"], ["CJ09", "CJ27", "CJ28", "CJ30", "CJ42"])
```

- [ ] **Step 3: Raise the real-repo floor for source documents and counts**

```python
def test_real_rules_expose_requirement_first_facts(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))
    self.assertGreaterEqual(len(data["facts"]["source_documents"]), 8)
    self.assertGreaterEqual(len(data["facts"]["requirements"]), 37)
    self.assertGreaterEqual(len(data["facts"]["acceptance"]), 37)
```

- [ ] **Step 4: Run the focused suite to confirm red**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: FAIL because `product_requirements_av` is not yet a covered source document and the journey/job gaps are still larger

### Task 2: Add AV Source Coverage And Requests

**Files:**
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add the AV source document contract**

```yaml
    - id: product_requirements_av
      path: docs/product-requirements-av.md
      extraction:
        regex:
          - '\bCJG\d+\b'
```

- [ ] **Step 2: Add the child play-flow and parent growth-support requests**

```yaml
    - id: rq_child_keep_play_flow
      stakeholder_id: st_child_user
      source_trace_refs:
        - customer_jobs:JOB:JPL_CHILD_PLAYER
        - customer_journeys:CJ14
        - customer_journeys:CJ16
        - customer_journeys:CJ18

    - id: rq_parent_natural_growth_support
      stakeholder_id: st_parent_customer
      source_trace_refs:
        - customer_jobs:JOB:JSC_PARENT_GROWTH
        - customer_journeys:CJ15
        - customer_journeys:CJ17
        - customer_journeys:CJ24
```

- [ ] **Step 3: Run focused tests again to keep the failure localized**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: still FAIL, but now only because the AV/guidance requirements and acceptance entries are missing

### Task 3: Migrate AV And Guidance Requirements / Acceptance

**Files:**
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add AV and guidance requirements**

```yaml
    - id: req_field_bgm_place_identity
      source_trace_refs:
        - customer_journeys:CJ15
        - product_requirements_av:CJG15

    - id: req_battle_bgm_tension_switch
      source_trace_refs:
        - customer_journeys:CJ16
        - product_requirements_av:CJG16

    - id: req_event_sfx_feedback_binding
      source_trace_refs:
        - customer_journeys:CJ17
        - product_requirements_av:CJG17
```

- [ ] **Step 2: Add the deferred guidance / transition entries without hiding current gaps**

```yaml
    - id: req_child_goal_guidance_visible
      status: later
      source_trace_refs:
        - customer_journeys:CJ14

    - id: req_scene_transition_polish_deferred
      status: later
      source_trace_refs:
        - customer_journeys:CJ19
        - product_requirements_av:CJG19
```

- [ ] **Step 3: Add damage VFX and sound-editor truth**

```yaml
    - id: req_damage_vfx_hit_feedback
      source_trace_refs:
        - customer_journeys:CJ18
        - product_requirements_av:CJG18

    - id: req_sound_editor_runtime_truth
      source_trace_refs:
        - customer_journeys:CJ24
        - product_requirements_av:CJG24
```

- [ ] **Step 4: Update existing AV cross-links**

```yaml
    - id: req_effect_difference_playtestable
      source_trace_refs:
        - customer_journeys:CJ20
        - product_requirements_av:CJG20
        - product_requirements_platform:CJG20

    - id: req_simplicity_enables_change_speed
      source_trace_refs:
        - customer_journeys:CJ44
        - product_requirements_av:CJG44
        - product_requirements_guardrails:CJG44
```

- [ ] **Step 5: Run the focused suite to verify green**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: PASS

### Task 4: Verify Real Repo State, Update Note, And Commit

**Files:**
- Modify: `steering/20260510-stakeholder-voices-av-guidance-theme-migration.md`
- Test: `test/test_source_trace_coverage_report.py`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Run the stakeholder-voices verification suite**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`  
Expected: PASS

Run: `python tools/report_source_trace_coverage.py`  
Expected: `product_requirements_av` shows zero missing refs, `customer_jobs` is missing only autonomy, and `customer_journeys` is missing only the story-tail refs

Run: `python tools/check_stakeholder_voices.py`  
Expected: JSON with `warning_rules: 0`

- [ ] **Step 2: Update the task note with actual CoVe results and completion state**

```markdown
## 5) Result（成果物）

- added AV source coverage
- migrated CJ14/CJ15/CJ16/CJG17/CJ18/CJ19/CJ24 into stakeholder voices
- reduced remaining missing refs to the narrative/autonomy tail
```

- [ ] **Step 3: Commit the slice**

Run: `git add docs/stakeholder_voices.yml test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py steering/20260510-stakeholder-voices-av-guidance-theme-migration.md docs/superpowers/plans/2026-05-10-stakeholder-voices-av-guidance-theme-migration.md`  
Run: `git commit -m "feat: migrate av journeys into stakeholder voices"`
