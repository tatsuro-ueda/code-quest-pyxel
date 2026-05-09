# Stakeholder Voices Acceptance Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an acceptance layer to `docs/stakeholder_voices.yml` so P0/P1 requirements become Gherkin-like, checker/fix/repair can validate that layer, and task notes can track `acceptance_ids`.

**Architecture:** Keep the existing requirement-first catalog and add `facts.acceptance` as a sibling section under `facts`. Link active P0/P1 requirements to acceptance scenarios with `acceptance_ids`, then extend the deterministic checker so it can validate acceptance structure, verification mode, and task note frontmatter references without broadening autofix beyond safe list normalization.

**Tech Stack:** Python 3, `yaml`, `unittest`, markdown task notes under `steering/`

---

### Task 1: Add Acceptance-Layer Red Tests

**Files:**
- Modify: `test/test_stakeholder_voices_checker.py`
- Read: `docs/stakeholder_voices.yml`
- Read: `steering/20260509-stakeholder-voices-acceptance-layer.md`

- [ ] **Step 1: Extend the real-schema test so acceptance becomes part of the contract**

```python
def test_real_rules_expose_requirement_first_facts(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))

    self.assertIn("stakeholders", data["facts"])
    self.assertIn("requests", data["facts"])
    self.assertIn("requirements", data["facts"])
    self.assertIn("acceptance", data["facts"])
    self.assertIn("tasknote_contracts", data["facts"])
    self.assertGreaterEqual(len(data["facts"]["requirements"]), 10)
    self.assertGreaterEqual(len(data["facts"]["acceptance"]), 10)
```

- [ ] **Step 2: Add fixture tests for the new acceptance checks**

```python
def test_run_checker_warns_when_p0_requirement_lacks_acceptance(self):
    result = checker.run_checker(repo_root, rules_path)
    self.assertTrue(result["has_warnings"])
    self.assertEqual(result["results"][0]["failed_checks"], ["requirement_acceptance_integrity"])


def test_run_checker_warns_when_acceptance_has_no_verification(self):
    result = checker.run_checker(repo_root, rules_path)
    self.assertTrue(result["has_warnings"])
    self.assertEqual(result["results"][0]["failed_checks"], ["acceptance_has_verification"])


def test_run_checker_warns_when_tasknote_missing_acceptance_ids(self):
    result = checker.run_checker(repo_root, rules_path)
    self.assertTrue(result["has_warnings"])
    self.assertEqual(result["results"][0]["failed_checks"], ["tasknote_frontmatter_integrity"])
```

- [ ] **Step 3: Run the checker tests to confirm the acceptance expectations are red**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q`
Expected: FAIL because the current real YAML and checker do not yet expose `facts.acceptance` or acceptance-specific rules

### Task 2: Implement Acceptance Schema and P0/P1 Scenarios

**Files:**
- Modify: `docs/stakeholder_voices.yml`
- Modify: `steering/20260509-stakeholder-voices-acceptance-layer.md`
- Read: `docs/customer-journeys.md`
- Read: `docs/product-requirements-platform.md`
- Read: `docs/framework-rule.md`

- [ ] **Step 1: Add `acceptance_ids` to each active P0/P1 requirement**

```yaml
    - id: req_url_share_no_install
      priority: p1
      acceptance_ids:
        - acc_url_share_no_install_browser
```

- [ ] **Step 2: Add `facts.acceptance` entries with Gherkin-like fields**

```yaml
  acceptance:
    - id: acc_url_share_no_install_browser
      requirement_id: req_url_share_no_install
      priority: p1
      summary: 友達は URL だけでブラウザから遊び始められる
      given: Web build と公開 URL がある
      when: 友達がスマホまたは PC のブラウザで URL を開く
      then:
        - ゲームが読み込まれプレイ開始まで進める
        - 会員登録やログインを要求しない
      verification:
        mode: deterministic
        refs:
          - tools/build_web_release.py
          - tools/test_web_compat.py
```

- [ ] **Step 3: Update the acceptance task note frontmatter contract to require `acceptance_ids`**

```yaml
  tasknote_contracts:
    required_frontmatter_keys:
      - requirement_ids
      - acceptance_ids
      - stakeholder_ids
      - affected_paths
      - verification_refs
      - done_checks
```

- [ ] **Step 4: Run the targeted checker test slice for Gherkin 1**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q -k "real_rules_expose_requirement_first_facts or p0_requirement_lacks_acceptance"`
Expected: PASS

### Task 3: Extend the Deterministic Checker

**Files:**
- Modify: `tools/stakeholder_voices/check_stakeholder_voices.py`
- Modify: `tools/check_stakeholder_voices.py`
- Test: `test/test_stakeholder_voices_checker.py`

- [ ] **Step 1: Require `facts.acceptance` in schema validation and include acceptance ids in uniqueness checks**

```python
for key in ("stakeholders", "requests", "requirements", "acceptance", "tasknote_contracts"):
    if key not in facts:
        raise KeyError(f"facts missing key: {key}")
```

```python
id_sources = {
    "stakeholders": [item["id"] for item in facts["stakeholders"]],
    "requests": [item["id"] for item in facts["requests"]],
    "requirements": [item["id"] for item in facts["requirements"]],
    "acceptance": [item["id"] for item in facts["acceptance"]],
    "validation_rules": [item["id"] for item in ctx.data["validation_rules"]],
}
```

- [ ] **Step 2: Add acceptance integrity checks and verification-mode validation**

```python
def check_requirement_acceptance_integrity(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    ...


def check_acceptance_has_verification(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    ...
```

- [ ] **Step 3: Expand task note frontmatter validation to require and resolve `acceptance_ids`**

```python
unresolved_acceptance = [
    item for item in frontmatter.get("acceptance_ids", []) if item not in acceptance_ids
]
if unresolved_acceptance:
    note_errors["unknown_acceptance_ids"] = unresolved_acceptance
```

- [ ] **Step 4: Run the checker tests to satisfy Gherkin 2, 3, and 4**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q`
Expected: PASS

### Task 4: Extend Fix and Repair for Safe Acceptance Normalization

**Files:**
- Modify: `test/test_fix_stakeholder_voices.py`
- Modify: `test/test_repair_stakeholder_voices.py`
- Modify: `tools/stakeholder_voices/fix_stakeholder_voices.py`
- Modify: `tools/stakeholder_voices/repair_stakeholder_voices.py`
- Modify: `tools/fix_stakeholder_voices.py`
- Modify: `tools/repair_stakeholder_voices.py`

- [ ] **Step 1: Add red tests for `acceptance_ids` normalization**

```python
self.assertEqual(requirement["acceptance_ids"], ["acc_safe_architecture_boundaries_guard"])
```

- [ ] **Step 2: Extend the fixer normalization keys to cover `acceptance_ids`**

```python
NORMALIZED_LIST_KEYS = (
    "derived_from_request_ids",
    "stakeholder_ids",
    "acceptance_ids",
    "affected_paths",
    "verification_refs",
    "source_refs",
)
```

- [ ] **Step 3: Run fix and repair tests to verify the acceptance-aware normalization path passes**

Run: `python -m pytest test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`
Expected: PASS

### Task 5: Update Task Notes and Run Final Verification

**Files:**
- Modify: `steering/20260509-stakeholder-voices-bootstrap.md`
- Modify: `steering/20260509-stakeholder-voices-acceptance-layer.md`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Add `acceptance_ids` to the stakeholder_voices task notes**

```yaml
acceptance_ids:
  - acc_safe_architecture_boundaries_guard
  - acc_done_requires_real_artifacts_release_review
```

- [ ] **Step 2: Run the focused verification suite and the three CLIs**

Run: `python -m pytest test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`
Expected: PASS

Run: `python tools/check_stakeholder_voices.py`
Expected: JSON with `has_warnings: false`

Run: `python tools/fix_stakeholder_voices.py`
Expected: JSON with `status: OK`

Run: `python tools/repair_stakeholder_voices.py`
Expected: JSON with `status: OK`

- [ ] **Step 3: Update task note Result and Discussion with Gherkin checkpoints, concerns, and next notes**

```markdown
## 5) Result（成果物）

- Task 1: wrote red acceptance tests and confirmed missing acceptance schema failed
- Task 2: added `facts.acceptance` and linked all active P0/P1 requirements
- Task 3: expanded checker rules for acceptance and `acceptance_ids`
- Task 4: kept fixer/repair limited to safe normalization only
```
