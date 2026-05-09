# Stakeholder Voices Coverage Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic source-trace coverage report so `docs/stakeholder_voices.yml` can explain per-document migration progress, missing stable refs, and broken extraction contracts without hiding traceability errors.

**Architecture:** Extend each `facts.source_documents` entry with an extraction contract, then add a dedicated coverage-report module that reads the YAML, extracts stable refs from each source doc, and compares them with active `source_trace_refs` used by requests, requirements, and acceptance. Keep checker/fixer behavior stable and make the report itself fail closed when doc ids, files, or extraction contracts are broken.

**Tech Stack:** Python 3, `yaml`, `re`, `json`, `unittest`, markdown task notes under `steering/`

---

### Task 1: Add Red Tests for the Coverage Report Contract

**Files:**
- Create: `test/test_source_trace_coverage_report.py`
- Read: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add a fixture test for total/referenced/missing counts**

```python
def test_build_report_counts_total_referenced_and_missing_refs(self):
    report = module.build_report(repo_root, rules_path)
    self.assertEqual(report["documents"][0]["total_refs"], 2)
    self.assertEqual(report["documents"][0]["referenced_refs"], ["JOB:JCR_CHILD_CREATOR"])
    self.assertEqual(report["documents"][0]["missing_refs"], ["JOB:JPL_CHILD_PLAYER"])
```

- [ ] **Step 2: Add a fixture test for broken extraction contracts**

```python
def test_build_report_fails_closed_when_source_document_has_no_extraction_contract(self):
    report = module.build_report(repo_root, rules_path)
    self.assertEqual(report["status"], "BROKEN_TRACEABILITY")
```

- [ ] **Step 3: Run the new report tests to confirm red**

Run: `python -m pytest test/test_source_trace_coverage_report.py -q`
Expected: FAIL because the report tool and extraction contract do not exist yet

### Task 2: Add Source-Document Extraction Contracts

**Files:**
- Modify: `docs/stakeholder_voices.yml`

- [ ] **Step 1: Add extraction regexes for jobs, journeys, and CJG docs**

```yaml
    - id: customer_jobs
      path: docs/customer-jobs.md
      extraction:
        regex:
          - 'JOB:[A-Z0-9_]+'
```

- [ ] **Step 2: Add mixed extraction rules for framework-rule**

```yaml
    - id: framework_rule
      path: docs/framework-rule.md
      extraction:
        regex:
          - '\bM[1-5]\b'
        literals:
          - SSoT
          - Golden Path Test
          - No Silent Failure
```

- [ ] **Step 3: Run a focused schema smoke after the YAML change**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q -k "real_rules_expose_requirement_first_facts"`
Expected: PASS

### Task 3: Implement the Coverage Report Tool

**Files:**
- Create: `tools/stakeholder_voices/source_trace_coverage.py`
- Create: `tools/report_source_trace_coverage.py`
- Test: `test/test_source_trace_coverage_report.py`

- [ ] **Step 1: Implement stable-ref extraction from source documents**

```python
def extract_stable_refs(repo_root: Path, source_document: dict[str, Any]) -> set[str]:
    ...
```

- [ ] **Step 2: Implement report assembly and fail-closed error reporting**

```python
def build_report(repo_root: Path, rules_path: Path) -> dict[str, Any]:
    ...
```

- [ ] **Step 3: Add a thin CLI wrapper**

```python
payload = run_report(ROOT, args.rules_path)
print(json.dumps(payload, ensure_ascii=False, indent=2))
```

- [ ] **Step 4: Run the focused report tests to satisfy Gherkin 1 to 3**

Run: `python -m pytest test/test_source_trace_coverage_report.py -q`
Expected: PASS

### Task 4: Verify the Real Repo and Close the Task Note

**Files:**
- Modify: `steering/20260509-stakeholder-voices-coverage-report.md`
- Test: `test/test_source_trace_coverage_report.py`
- Test: `test/test_stakeholder_voices_checker.py`

- [ ] **Step 1: Run the combined verification suite**

Run: `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`
Expected: PASS

Run: `python tools/report_source_trace_coverage.py`
Expected: JSON with per-document `total_refs`, `referenced_refs`, and `missing_refs`

Run: `python tools/check_stakeholder_voices.py`
Expected: JSON with `warning_rules: 0`

- [ ] **Step 2: Update the task note with actual coverage numbers and next candidates**

```markdown
## 5) Result（成果物）

- added source document extraction contracts
- added a deterministic coverage report
- recorded per-document missing refs for follow-up task notes
```
