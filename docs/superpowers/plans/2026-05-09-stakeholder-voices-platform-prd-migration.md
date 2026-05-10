# Stakeholder Voices Platform PRD Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the remaining `docs/product-requirements-platform.md` refs `CJG12`, `CJG20`, `CJG25`, and `CJG26` into `docs/stakeholder_voices.yml` so the platform PRD has full trace coverage and the related ownership / bugfix / portability requirements become machine-referenceable.

**Architecture:** Reuse the existing request layer and add four platform-focused requirements plus four matching acceptance scenarios. For `CJG20`, keep the trace token as `product_requirements_platform:CJG20` for current coverage compatibility, while also citing `docs/product-requirements-av.md` in `source_refs` for the moved narrative context. Prove progress with a real-repo coverage assertion first, then make the YAML changes, and finally re-run checker and coverage report together.

**Tech Stack:** Python 3, `yaml`, `unittest`, JSON CLI reports, markdown task notes under `steering/`

---

### Task 1: Add Red Tests For Platform Coverage

**Files:**
- Modify: `test/test_source_trace_coverage_report.py`
- Modify: `test/test_stakeholder_voices_checker.py`
- Read: `docs/product-requirements-platform.md`
- Read: `docs/product-requirements-av.md`
- Read: `docs/customer-journeys.md`

- [ ] **Step 1: Add a real-repo coverage assertion for `product_requirements_platform`**

```python
def test_real_repo_report_covers_all_platform_prd_refs(self):
    report_module = load_report_module()
    payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_platform")
    self.assertEqual(
        document["referenced_refs"],
        ["CJG12", "CJG20", "CJG21", "CJG22", "CJG23", "CJG25", "CJG26", "CJG31", "CJG32", "CJG33", "CJG34", "CJG43"],
    )
    self.assertEqual(document["missing_refs"], [])
```

- [ ] **Step 2: Increase the real-repo requirement and acceptance floor**

```python
def test_real_rules_expose_requirement_first_facts(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))
    self.assertGreaterEqual(len(data["facts"]["requirements"]), 25)
    self.assertGreaterEqual(len(data["facts"]["acceptance"]), 25)
```

- [ ] **Step 3: Run the focused suite to confirm red**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: FAIL because the platform PRD refs are still partially missing from stakeholder voices

### Task 2: Migrate `CJG12/CJG20/CJG25/CJG26` Into Stakeholder Voices

**Files:**
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add four platform-focused requirements**

```yaml
    - id: req_bugfix_replay_safe
      derived_from_request_ids:
        - rq_parent_fast_feedback
        - rq_ai_small_safe_surface
      source_trace_refs:
        - customer_journeys:CJ12
        - product_requirements_platform:CJG12
```

- [ ] **Step 2: Add four matching acceptance scenarios**

```yaml
    - id: acc_bugfix_replay_safe_loop
      requirement_id: req_bugfix_replay_safe
      source_trace_refs:
        - customer_journeys:CJ12
        - product_requirements_platform:CJG12
      verification:
        mode: deterministic
        refs:
          - tools/test_headless.py
          - tools/test_save_compat.py
          - tools/test_web_compat.py
```

- [ ] **Step 3: Keep path hints and trace compatibility valid**

```yaml
      affected_paths:
        - tools/build_codemaker.py
        - tools/build_web_release.py
        - tools/render_release_selector.py
        - src/shared/services/image_banks.py
```

- [ ] **Step 4: Run focused checker and coverage tests**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: PASS

### Task 3: Verify Real Repo State And Close The Task Note

**Files:**
- Modify: `steering/20260509-stakeholder-voices-platform-prd-migration.md`
- Test: `test/test_source_trace_coverage_report.py`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Run the stakeholder-voices verification suite**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`  
Expected: PASS

Run: `python tools/report_source_trace_coverage.py`  
Expected: `product_requirements_platform` shows twelve referenced refs and zero missing refs

Run: `python tools/check_stakeholder_voices.py`  
Expected: JSON with `warning_rules: 0`

- [ ] **Step 2: Update the task note with actual CoVe results**

```markdown
## 5) Result（成果物）

- migrated CJG12/CJG20/CJG25/CJG26 into stakeholder voices
- reduced product_requirements_platform missing refs to zero
- kept checker and task note contracts green
```
