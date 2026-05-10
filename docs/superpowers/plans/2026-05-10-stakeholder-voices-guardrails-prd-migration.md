# Stakeholder Voices Guardrails PRD Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the remaining `docs/product-requirements-guardrails.md` refs `CJG36`, `CJG38`, `CJG39`, `CJG40`, and `CJG44` into `docs/stakeholder_voices.yml` so the guardrails PRD has full trace coverage and the related safety requirements become machine-referenceable.

**Architecture:** Reuse the existing request layer and add five guardrails-focused requirements plus five matching acceptance scenarios. Existing coverage for `CJG35`, `CJG37`, and `CJG41` stays as-is; this slice fills only the remaining gaps. Prove progress with a real-repo coverage assertion first, then make the YAML changes, and finally re-run checker and coverage report together.

**Tech Stack:** Python 3, `yaml`, `unittest`, JSON CLI reports, markdown task notes under `steering/`

---

### Task 1: Add Red Tests For Guardrails Coverage

**Files:**
- Modify: `test/test_source_trace_coverage_report.py`
- Modify: `test/test_stakeholder_voices_checker.py`
- Read: `docs/product-requirements-guardrails.md`
- Read: `docs/customer-journeys.md`

- [ ] **Step 1: Add a real-repo coverage assertion for `product_requirements_guardrails`**

```python
def test_real_repo_report_covers_all_guardrails_prd_refs(self):
    report_module = load_report_module()
    payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_guardrails")
    self.assertEqual(
        document["referenced_refs"],
        ["CJG35", "CJG36", "CJG37", "CJG38", "CJG39", "CJG40", "CJG41", "CJG44"],
    )
    self.assertEqual(document["missing_refs"], [])
```

- [ ] **Step 2: Increase the real-repo requirement and acceptance floor**

```python
def test_real_rules_expose_requirement_first_facts(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))
    self.assertGreaterEqual(len(data["facts"]["requirements"]), 30)
    self.assertGreaterEqual(len(data["facts"]["acceptance"]), 30)
```

- [ ] **Step 3: Run the focused suite to confirm red**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: FAIL because the guardrails PRD refs are still partially missing from stakeholder voices

### Task 2: Migrate `CJG36/CJG38/CJG39/CJG40/CJG44` Into Stakeholder Voices

**Files:**
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add five guardrails-focused requirements**

```yaml
    - id: req_data_ssot_consistency
      derived_from_request_ids:
        - rq_ai_small_safe_surface
        - rq_developer_safe_boundaries
      source_trace_refs:
        - customer_journeys:CJ36
        - product_requirements_guardrails:CJG36
```

- [ ] **Step 2: Add five matching acceptance scenarios**

```yaml
    - id: acc_data_ssot_consistency_regen
      requirement_id: req_data_ssot_consistency
      source_trace_refs:
        - customer_journeys:CJ36
        - product_requirements_guardrails:CJG36
      verification:
        mode: deterministic
        refs:
          - tools/gen_data.py
          - test/test_cjg_data_progressions.py
```

- [ ] **Step 3: Keep path hints and trace contracts valid**

```yaml
      affected_paths:
        - assets/
        - src/generated/
        - src/game_data.py
        - tools/gen_data.py
```

- [ ] **Step 4: Run focused checker and coverage tests**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: PASS

### Task 3: Verify Real Repo State And Close The Task Note

**Files:**
- Modify: `steering/20260510-stakeholder-voices-guardrails-prd-migration.md`
- Test: `test/test_source_trace_coverage_report.py`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Run the stakeholder-voices verification suite**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`  
Expected: PASS

Run: `python tools/report_source_trace_coverage.py`  
Expected: `product_requirements_guardrails` shows eight referenced refs and zero missing refs

Run: `python tools/check_stakeholder_voices.py`  
Expected: JSON with `warning_rules: 0`

- [ ] **Step 2: Update the task note with actual CoVe results**

```markdown
## 5) Result（成果物）

- migrated CJG36/CJG38/CJG39/CJG40/CJG44 into stakeholder voices
- reduced product_requirements_guardrails missing refs to zero
- kept checker and task note contracts green
```
