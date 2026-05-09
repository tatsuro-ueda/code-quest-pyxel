# Customer Jobs Stable Trace IDs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `docs/customer-jobs.md` machine-referenceable from `docs/stakeholder_voices.yml` so active requests can trace to stable customer-job ids and the checker can warn on broken request-level job refs.

**Architecture:** Add explicit stable tokens to the top-level job sections in `docs/customer-jobs.md`, register that doc in `facts.source_documents`, and extend request entries with `source_trace_refs`. Reuse the existing `source_traceability_integrity` rule instead of adding a parallel rule, then widen safe normalization so duplicated request trace lists can be autofixed without inventing prose.

**Tech Stack:** Python 3, `yaml`, `unittest`, markdown task notes under `steering/`

---

### Task 1: Add Red Tests for Request-Level Job Traceability

**Files:**
- Modify: `test/test_stakeholder_voices_checker.py`
- Read: `docs/stakeholder_voices.yml`
- Read: `docs/customer-jobs.md`

- [ ] **Step 1: Tighten the real-schema expectations for source docs**

```python
def test_real_rules_expose_requirement_first_facts(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))

    self.assertIn("source_documents", data["facts"])
    self.assertGreaterEqual(len(data["facts"]["source_documents"]), 7)
```

- [ ] **Step 2: Add a failing fixture test for broken request job refs**

```python
def test_run_checker_warns_when_request_source_trace_ref_points_to_unknown_ref(self):
    result = checker.run_checker(repo_root, rules_path)
    self.assertTrue(result["has_warnings"])
    self.assertEqual(result["results"][0]["failed_checks"], ["source_traceability_integrity"])
```

- [ ] **Step 3: Run the focused checker suite to confirm red**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q`
Expected: FAIL because the real YAML does not yet include `customer_jobs` and the checker does not inspect request `source_trace_refs`

### Task 2: Add Stable Customer-Job Tokens and Request Trace Refs

**Files:**
- Modify: `docs/customer-jobs.md`
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add unique stable tokens to the top job sections in `docs/customer-jobs.md`**

```markdown
## JCR 子ども（クリエイター） [JOB:JCR_CREATOR]
## JSC 親（成長支援） [JOB:JSC_PARENT_GROWTH]
```

- [ ] **Step 2: Register `customer_jobs` in the source document catalog**

```yaml
  source_documents:
    - id: customer_jobs
      path: docs/customer-jobs.md
```

- [ ] **Step 3: Add `source_trace_refs` to active requests**

```yaml
    - id: rq_child_edit_ownership
      source_trace_refs:
        - customer_jobs:JOB:JCR_CREATOR
        - customer_journeys:CJ23
        - product_requirements_platform:CJG23
```

- [ ] **Step 4: Run a focused schema test after the YAML/doc edits**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q -k "real_rules_expose_requirement_first_facts"`
Expected: PASS

### Task 3: Extend the Checker and Safe Normalization

**Files:**
- Modify: `tools/stakeholder_voices/check_stakeholder_voices.py`
- Modify: `tools/stakeholder_voices/fix_stakeholder_voices.py`
- Modify: `test/test_fix_stakeholder_voices.py`

- [ ] **Step 1: Extend `source_traceability_integrity` to inspect requests**

```python
for section_name in ("requests", "requirements", "acceptance"):
    ...
```

- [ ] **Step 2: Normalize request trace-ref lists safely**

```python
REQUEST_NORMALIZED_LIST_KEYS = ("source_trace_refs", "source_refs")
```

- [ ] **Step 3: Add a fixer test for duplicate request trace refs**

```python
self.assertEqual(request["source_trace_refs"], ["customer_jobs:JOB:JCR_CREATOR"])
```

- [ ] **Step 4: Run the stakeholder voice test suite**

Run: `python -m pytest test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`
Expected: PASS

### Task 4: Verify Real Repo State and Close the Task Note

**Files:**
- Modify: `steering/20260509-customer-jobs-stable-trace-ids.md`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Run the CLIs on the real repo**

Run: `python tools/check_stakeholder_voices.py`
Expected: JSON with `warning_rules: 0`

Run: `python tools/fix_stakeholder_voices.py`
Expected: JSON with `status: OK`

Run: `python tools/repair_stakeholder_voices.py`
Expected: JSON with `status: OK`

- [ ] **Step 2: Update the task note with actual execution evidence**

```markdown
## 5) Result（成果物）

- added stable customer job tokens and request-level source_trace_refs
- extended source trace validation to requests
- verified the real repo is still clean
```
