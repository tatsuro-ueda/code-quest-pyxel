# Stakeholder Voices Source Traceability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add structured source traceability to `docs/stakeholder_voices.yml` so active requirements and acceptance scenarios can point to exact `CJ / CJG / M-rule` roots and the checker can validate that those references are still live.

**Architecture:** Keep `source_refs` as human-readable file-path references and add a separate machine-readable trace layer: `facts.source_documents` plus `source_trace_refs` lists. Extend the deterministic checker with a single traceability rule that validates doc ids, file existence, and trace token presence, then extend safe normalization to dedupe/sort trace-ref lists without touching prose.

**Tech Stack:** Python 3, `yaml`, `unittest`, markdown task notes under `steering/`

---

### Task 1: Add Traceability Red Tests

**Files:**
- Modify: `test/test_stakeholder_voices_checker.py`
- Read: `docs/stakeholder_voices.yml`
- Read: `docs/customer-journeys.md`
- Read: `docs/product-requirements-platform.md`
- Read: `docs/product-requirements-guardrails.md`
- Read: `docs/framework-rule.md`

- [ ] **Step 1: Extend the real-schema expectations to require `facts.source_documents`**

```python
def test_real_rules_expose_requirement_first_facts(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))

    self.assertIn("source_documents", data["facts"])
    self.assertGreaterEqual(len(data["facts"]["source_documents"]), 6)
```

- [ ] **Step 2: Add a failing fixture test for broken structured trace refs**

```python
def test_run_checker_warns_when_source_trace_ref_points_to_unknown_ref(self):
    result = checker.run_checker(repo_root, rules_path)
    self.assertTrue(result["has_warnings"])
    self.assertEqual(result["results"][0]["failed_checks"], ["source_traceability_integrity"])
```

- [ ] **Step 3: Run the checker tests to confirm traceability is red**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q`
Expected: FAIL because the real YAML and checker do not yet expose `facts.source_documents` or the traceability rule

### Task 2: Add Structured Traceability to the Real YAML

**Files:**
- Modify: `docs/stakeholder_voices.yml`
- Modify: `steering/20260509-stakeholder-voices-source-traceability.md`
- Read: `docs/product-requirements-map.md`
- Read: `docs/product-requirements-battle.md`

- [ ] **Step 1: Add the source document catalog**

```yaml
  source_documents:
    - id: customer_journeys
      path: docs/customer-journeys.md
    - id: product_requirements_platform
      path: docs/product-requirements-platform.md
    - id: product_requirements_guardrails
      path: docs/product-requirements-guardrails.md
    - id: framework_rule
      path: docs/framework-rule.md
```

- [ ] **Step 2: Add `source_trace_refs` to active requirements**

```yaml
    - id: req_safe_architecture_boundaries
      source_trace_refs:
        - customer_journeys:CJ37
        - customer_journeys:CJ44
        - product_requirements_guardrails:CJG37
        - framework_rule:M1
        - framework_rule:M2
        - framework_rule:M3
        - framework_rule:M4
        - framework_rule:M5
```

- [ ] **Step 3: Add `source_trace_refs` to active acceptance scenarios**

```yaml
    - id: acc_url_share_no_install_browser
      source_trace_refs:
        - customer_journeys:CJ21
        - product_requirements_platform:CJG21
```

- [ ] **Step 4: Run a focused checker slice for schema presence**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q -k "real_rules_expose_requirement_first_facts"`
Expected: PASS

### Task 3: Extend the Deterministic Checker

**Files:**
- Modify: `tools/stakeholder_voices/check_stakeholder_voices.py`
- Modify: `tools/check_stakeholder_voices.py`
- Test: `test/test_stakeholder_voices_checker.py`

- [ ] **Step 1: Require `facts.source_documents` in schema validation**

```python
for key in (
    "stakeholders",
    "requests",
    "requirements",
    "acceptance",
    "source_documents",
    "tasknote_contracts",
):
    if key not in facts:
        raise KeyError(f"facts missing key: {key}")
```

- [ ] **Step 2: Implement a traceability checker that validates doc ids and ref tokens**

```python
def check_source_traceability_integrity(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    ...
```

- [ ] **Step 3: Register the new rule and update the expected real-rule count**

```python
CHECK_REGISTRY = {
    ...
    "source_traceability_integrity": check_source_traceability_integrity,
}
```

- [ ] **Step 4: Run checker tests to satisfy Gherkin 1 to 3**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q`
Expected: PASS

### Task 4: Extend Safe Normalization for Trace Ref Lists

**Files:**
- Modify: `test/test_fix_stakeholder_voices.py`
- Modify: `test/test_repair_stakeholder_voices.py`
- Modify: `tools/stakeholder_voices/fix_stakeholder_voices.py`
- Modify: `tools/stakeholder_voices/repair_stakeholder_voices.py`

- [ ] **Step 1: Add red tests for duplicate `source_trace_refs`**

```python
self.assertEqual(
    requirement["source_trace_refs"],
    ["framework_rule:M1", "product_requirements_guardrails:CJG37"],
)
```

- [ ] **Step 2: Extend safe normalization to sort and dedupe trace-ref lists**

```python
REQUIREMENT_NORMALIZED_LIST_KEYS = (
    "derived_from_request_ids",
    "acceptance_ids",
    "stakeholder_ids",
    "source_trace_refs",
    "affected_paths",
    "verification_refs",
    "source_refs",
)
```

- [ ] **Step 3: Run fix and repair tests to satisfy Gherkin 4**

Run: `python -m pytest test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`
Expected: PASS

### Task 5: Final Verification and Task Note Updates

**Files:**
- Modify: `steering/20260509-stakeholder-voices-source-traceability.md`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Update the task note Tasklist/Result/Discussion based on what actually happened**

```markdown
## 5) Result（成果物）

- added `facts.source_documents`
- added `source_trace_refs` to active requirements and acceptance
- added `source_traceability_integrity` checker rule
```

- [ ] **Step 2: Run the focused verification suite and CLIs**

Run: `python -m pytest test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`
Expected: PASS

Run: `python tools/check_stakeholder_voices.py`
Expected: JSON with `warning_rules: 0`

Run: `python tools/fix_stakeholder_voices.py`
Expected: JSON with `status: OK`

Run: `python tools/repair_stakeholder_voices.py`
Expected: JSON with `status: OK`
