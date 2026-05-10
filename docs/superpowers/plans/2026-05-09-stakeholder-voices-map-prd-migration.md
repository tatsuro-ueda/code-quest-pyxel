# Stakeholder Voices Map PRD Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate `docs/product-requirements-map.md` `CJG01-CJG07` into `docs/stakeholder_voices.yml` so map-editing requirements and acceptance scenarios become machine-referenceable and the coverage report no longer shows the map PRD as entirely missing.

**Architecture:** Keep the existing stakeholder request layer as the primary root unless a true request gap appears. Add seven map-focused requirements plus matching acceptance scenarios, each with `product_requirements_map:CJG0x` and `customer_journeys:CJ0x` trace refs. Prove progress with a real-repo coverage-report assertion first, then make the YAML changes, and finally re-run checker and coverage report together.

**Tech Stack:** Python 3, `yaml`, `unittest`, JSON CLI reports, markdown task notes under `steering/`

---

### Task 1: Add Red Tests For Map Coverage

**Files:**
- Modify: `test/test_source_trace_coverage_report.py`
- Modify: `test/test_stakeholder_voices_checker.py`
- Read: `docs/product-requirements-map.md`
- Read: `docs/customer-journeys.md`

- [ ] **Step 1: Add a real-repo coverage assertion for `product_requirements_map`**

```python
def test_real_repo_report_covers_all_map_prd_refs(self):
    payload = module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_map")
    self.assertEqual(document["referenced_refs"], ["CJG01", "CJG02", "CJG03", "CJG04", "CJG05", "CJG06", "CJG07"])
    self.assertEqual(document["missing_refs"], [])
```

- [ ] **Step 2: Add a real-repo checker assertion for requirement/acceptance growth**

```python
def test_real_rules_include_map_requirements_and_acceptance(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))
    self.assertGreaterEqual(len(data["facts"]["requirements"]), 17)
    self.assertGreaterEqual(len(data["facts"]["acceptance"]), 17)
```

- [ ] **Step 3: Run the focused suite to confirm red**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`
Expected: FAIL because the map PRD refs are still missing from stakeholder voices

### Task 2: Migrate `CJG01-CJG07` Into Stakeholder Voices

**Files:**
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add seven map-focused requirements**

```yaml
    - id: req_map_first_tile_visible
      derived_from_request_ids:
        - rq_child_edit_ownership
        - rq_parent_fast_feedback
      source_trace_refs:
        - customer_journeys:CJ01
        - product_requirements_map:CJG01
```

- [ ] **Step 2: Add seven matching acceptance scenarios**

```yaml
    - id: acc_map_first_tile_visible_roundtrip
      requirement_id: req_map_first_tile_visible
      source_trace_refs:
        - customer_journeys:CJ01
        - product_requirements_map:CJG01
      verification:
        mode: deterministic
        refs:
          - tools/build_codemaker.py
          - tools/probe_codemaker_layout.py
```

- [ ] **Step 3: Keep list normalization and frontmatter contracts valid**

```yaml
      affected_paths:
        - tools/build_codemaker.py
        - src/shared/services/image_banks.py
        - dist/
```

- [ ] **Step 4: Run focused checker and coverage tests**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`
Expected: PASS

### Task 3: Verify Real Repo State And Close The Task Note

**Files:**
- Modify: `steering/20260509-stakeholder-voices-map-prd-migration.md`
- Test: `test/test_source_trace_coverage_report.py`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Run the stakeholder-voices verification suite**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`
Expected: PASS

Run: `python tools/report_source_trace_coverage.py`
Expected: `product_requirements_map` shows seven referenced refs and zero missing refs

Run: `python tools/check_stakeholder_voices.py`
Expected: JSON with `warning_rules: 0`

- [ ] **Step 2: Update the task note with actual CoVe results**

```markdown
## 5) Result（成果物）

- migrated CJG01-CJG07 into stakeholder voices
- reduced product_requirements_map missing refs to zero
- kept checker and task note contracts green
```
