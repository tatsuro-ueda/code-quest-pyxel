# Stakeholder Voices Battle PRD Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate `docs/product-requirements-battle.md` `CJG08`, `CJG10`, `CJG13`, and `CJG29` into `docs/stakeholder_voices.yml` so battle-editing requirements and acceptance scenarios become machine-referenceable and the coverage report no longer shows the battle PRD as entirely missing.

**Architecture:** Reuse the existing request layer and add four battle-focused requirements plus four matching acceptance scenarios. Each migrated item will carry both `product_requirements_battle:CJGxx` and `customer_journeys:CJxx` trace refs. Prove progress with a real-repo coverage assertion first, then make the YAML changes, and finally re-run checker and coverage report together.

**Tech Stack:** Python 3, `yaml`, `unittest`, JSON CLI reports, markdown task notes under `steering/`

---

### Task 1: Add Red Tests For Battle Coverage

**Files:**
- Modify: `test/test_source_trace_coverage_report.py`
- Modify: `test/test_stakeholder_voices_checker.py`
- Read: `docs/product-requirements-battle.md`
- Read: `docs/customer-journeys.md`

- [ ] **Step 1: Add a real-repo coverage assertion for `product_requirements_battle`**

```python
def test_real_repo_report_covers_all_battle_prd_refs(self):
    report_module = load_report_module()
    payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
    document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_battle")
    self.assertEqual(document["referenced_refs"], ["CJG08", "CJG10", "CJG13", "CJG29"])
    self.assertEqual(document["missing_refs"], [])
```

- [ ] **Step 2: Increase the real-repo requirement and acceptance floor**

```python
def test_real_rules_expose_requirement_first_facts(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))
    self.assertGreaterEqual(len(data["facts"]["requirements"]), 21)
    self.assertGreaterEqual(len(data["facts"]["acceptance"]), 21)
```

- [ ] **Step 3: Run the focused suite to confirm red**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: FAIL because the battle PRD refs are still missing from stakeholder voices

### Task 2: Migrate `CJG08/CJG10/CJG13/CJG29` Into Stakeholder Voices

**Files:**
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add four battle-focused requirements**

```yaml
    - id: req_enemy_balance_adjustable
      derived_from_request_ids:
        - rq_parent_fast_feedback
      source_trace_refs:
        - customer_journeys:CJ08
        - product_requirements_battle:CJG08
```

- [ ] **Step 2: Add four matching acceptance scenarios**

```yaml
    - id: acc_enemy_balance_adjustable_roundtrip
      requirement_id: req_enemy_balance_adjustable
      source_trace_refs:
        - customer_journeys:CJ08
        - product_requirements_battle:CJG08
      verification:
        mode: deterministic
        refs:
          - test/test_cjg_data_progressions.py
          - test/test_cjg_battle_flow_smoke.py
```

- [ ] **Step 3: Keep path hints and frontmatter contracts valid**

```yaml
      affected_paths:
        - assets/enemies.yaml
        - assets/spells.yaml
        - src/game_data.py
        - src/scenes/battle/scene.py
```

- [ ] **Step 4: Run focused checker and coverage tests**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q`  
Expected: PASS

### Task 3: Verify Real Repo State And Close The Task Note

**Files:**
- Modify: `steering/20260509-stakeholder-voices-battle-prd-migration.md`
- Test: `test/test_source_trace_coverage_report.py`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Run the stakeholder-voices verification suite**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`  
Expected: PASS

Run: `python tools/report_source_trace_coverage.py`  
Expected: `product_requirements_battle` shows four referenced refs and zero missing refs

Run: `python tools/check_stakeholder_voices.py`  
Expected: JSON with `warning_rules: 0`

- [ ] **Step 2: Update the task note with actual CoVe results**

```markdown
## 5) Result（成果物）

- migrated CJG08/CJG10/CJG13/CJG29 into stakeholder voices
- reduced product_requirements_battle missing refs to zero
- kept checker and task note contracts green
```
