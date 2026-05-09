# Stakeholder Voices Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a requirement-first `docs/stakeholder_voices.yml` plus `check / fix / repair` tooling so AI can update stakeholder-driven requirements and deterministically validate safe YAML drift.

**Architecture:** Mirror the `architecture_rules` tool split with thin top-level CLIs and a `tools/stakeholder_voices/` package, but use a requirement-first schema centered on `stakeholders`, `requests`, `requirements`, and `tasknote_contracts`. Start with focused red tests, implement deterministic checker rules first, then add fix/repair for safe YAML normalization only.

**Tech Stack:** Python 3, `yaml`, `unittest`, markdown task notes under `steering/`

---

### Task 1: Add Checker Red Tests

**Files:**
- Create: `test/test_stakeholder_voices_checker.py`
- Read: `docs/customer-jobs.md`
- Read: `docs/customer-journeys.md`
- Read: `docs/product-requirements-platform.md`
- Read: `docs/product-requirements-guardrails.md`

- [ ] **Step 1: Write failing tests for the missing checker and missing real YAML**

```python
def load_checker_module():
    try:
        import check_stakeholder_voices
    except ImportError as exc:
        raise AssertionError(f"tools/check_stakeholder_voices.py is missing: {exc}") from exc
    return check_stakeholder_voices


def test_real_rules_expose_requirement_first_facts(self):
    data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))
    self.assertIn("stakeholders", data["facts"])
    self.assertIn("requests", data["facts"])
    self.assertIn("requirements", data["facts"])
    self.assertIn("tasknote_contracts", data["facts"])


def test_cli_stdout_is_valid_json_for_default_repo(self):
    completed = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_stakeholder_voices.py")],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    self.assertEqual(completed.returncode, 0, completed.stderr)
    payload = json.loads(completed.stdout)
    self.assertTrue(payload["run_ok"])
```

- [ ] **Step 2: Run the checker tests to verify they fail**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q`  
Expected: FAIL because `tools/check_stakeholder_voices.py` and/or `docs/stakeholder_voices.yml` do not exist yet

### Task 2: Implement Requirement-First YAML and Checker

**Files:**
- Create: `docs/stakeholder_voices.yml`
- Create: `tools/check_stakeholder_voices.py`
- Create: `tools/stakeholder_voices/__init__.py`
- Create: `tools/stakeholder_voices/check_stakeholder_voices.py`
- Modify: `steering/20260509-stakeholder-voices-bootstrap.md`
- Test: `test/test_stakeholder_voices_checker.py`

- [ ] **Step 1: Add the real bootstrap YAML with stakeholder, request, requirement, and task note facts**

```yaml
meta:
  document_id: stakeholder_voices
  version: 1
  status: draft

facts:
  stakeholders:
    - id: st_parent_customer
      type: customer
      label: 親
      status: active
  requests:
    - id: rq_parent_fast_feedback
      stakeholder_id: st_parent_customer
      status: active
      summary: 子どもの熱が冷める前に要望を試したい
      source_refs:
        - docs/customer-jobs.md
        - docs/customer-journeys.md
  requirements:
    - id: req_fast_feedback_loop
      status: active
      kind: experience
      priority: p1
      derived_from_request_ids:
        - rq_parent_fast_feedback
      stakeholder_ids:
        - st_parent_customer
      summary: 要望から再プレイまでを短時間で回す
      must:
        - 変更後に短時間で再確認できる
      must_not:
        - 子どもの集中が切れるほど待たせない
      affected_paths:
        - tools/build_codemaker.py
        - tools/build_web_release.py
      verification_refs:
        - tools/build_codemaker.py
        - tools/build_web_release.py
      source_refs:
        - docs/customer-journeys.md
        - docs/product-requirements-platform.md
  tasknote_contracts:
    note_glob: steering/*.md
    opt_in_frontmatter_key: requirement_ids
    required_frontmatter_keys:
      - requirement_ids
      - stakeholder_ids
      - affected_paths
      - verification_refs
      - done_checks
```

- [ ] **Step 2: Implement deterministic checker logic**

```python
def run_checker(repo_root: Path, rules_path: Path, rule_ids: set[str] | None = None) -> dict[str, Any]:
    data = load_rules(rules_path)
    ctx = CheckContext(repo_root=repo_root, rules_path=rules_path, data=data)
    results = []
    for rule in data["validation_rules"]:
        if rule_ids and rule["id"] not in rule_ids:
            continue
        outcome = run_rule(ctx, rule)
        results.append(build_result(rule, outcome))
    return build_payload(results)
```

- [ ] **Step 3: Add deterministic checks for id integrity, code hints, path existence, and opt-in task note frontmatter**

```python
CHECK_REGISTRY = {
    "id_uniqueness": check_id_uniqueness,
    "stakeholder_reference_integrity": check_stakeholder_reference_integrity,
    "request_reference_integrity": check_request_reference_integrity,
    "requirement_has_code_hints": check_requirement_has_code_hints,
    "referenced_paths_exist": check_referenced_paths_exist,
    "tasknote_frontmatter_integrity": check_tasknote_frontmatter_integrity,
    "normalized_requirement_lists": check_normalized_requirement_lists,
}
```

- [ ] **Step 4: Run the checker tests to verify they pass**

Run: `python -m pytest test/test_stakeholder_voices_checker.py -q`  
Expected: PASS

### Task 3: Add Fix and Repair Red Tests

**Files:**
- Create: `test/test_fix_stakeholder_voices.py`
- Create: `test/test_repair_stakeholder_voices.py`
- Read: `test/test_fix_architecture_rules.py`
- Read: `test/test_repair_architecture_rules.py`

- [ ] **Step 1: Write failing tests for missing fix and repair modules**

```python
def load_fixer_module():
    try:
        import fix_stakeholder_voices
    except ImportError as exc:
        raise AssertionError(f"tools/fix_stakeholder_voices.py is missing: {exc}") from exc
    return fix_stakeholder_voices


def test_run_fixer_normalizes_duplicate_requirement_lists(self):
    result = fixer.run_fixer(repo_root, rules_path)
    self.assertEqual(result["status"], "FIXED")
```

- [ ] **Step 2: Run the fix and repair tests to verify they fail**

Run: `python -m pytest test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`  
Expected: FAIL because fix and repair entrypoints do not exist yet

### Task 4: Implement Fix and Repair for Safe Normalization

**Files:**
- Create: `tools/fix_stakeholder_voices.py`
- Create: `tools/repair_stakeholder_voices.py`
- Create: `tools/stakeholder_voices/fix_stakeholder_voices.py`
- Create: `tools/stakeholder_voices/repair_stakeholder_voices.py`
- Modify: `tools/stakeholder_voices/__init__.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Implement YAML writer and list normalization fixer**

```python
def normalize_requirement_lists(data: dict[str, Any]) -> list[dict[str, str]]:
    fixes = []
    for requirement in data.get("facts", {}).get("requirements", []):
        for key in ("derived_from_request_ids", "stakeholder_ids", "affected_paths", "verification_refs", "source_refs"):
            normalized = sorted(dict.fromkeys(requirement.get(key, [])))
            if normalized != requirement.get(key, []):
                requirement[key] = normalized
                fixes.append({"kind": "yaml", "detail": f"normalized {requirement['id']}:{key}"})
    return fixes
```

- [ ] **Step 2: Implement fixer and repair loop entrypoints**

```python
def run_fixer(repo_root: Path, rules_path: Path, *, rule_ids: set[str] | None = None) -> dict[str, Any]:
    check = check_stakeholder_voices.run_checker(repo_root, rules_path, rule_ids=rule_ids)
    if not check["has_warnings"]:
        return {"status": "OK", "check": check, "applied_fixes": []}
    data = load_yaml(rules_path)
    applied_fixes = normalize_requirement_lists(data)
    if applied_fixes:
        write_yaml(rules_path, data)
    post = check_stakeholder_voices.run_checker(repo_root, rules_path, rule_ids=rule_ids)
    return {"status": "FIXED" if applied_fixes else "NEEDS_HUMAN", "check": check, "post_check": post, "applied_fixes": applied_fixes}
```

- [ ] **Step 3: Run the fix and repair tests to verify they pass**

Run: `python -m pytest test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`  
Expected: PASS

### Task 5: Final Verification and Task Note Updates

**Files:**
- Modify: `steering/20260509-stakeholder-voices-bootstrap.md`
- Test: `test/test_stakeholder_voices_checker.py`
- Test: `test/test_fix_stakeholder_voices.py`
- Test: `test/test_repair_stakeholder_voices.py`

- [ ] **Step 1: Run the focused verification commands**

Run: `python -m pytest test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q`  
Expected: PASS

- [ ] **Step 2: Run the three CLIs on the real repo**

Run: `python tools/check_stakeholder_voices.py`  
Expected: JSON with `run_ok: true`

Run: `python tools/fix_stakeholder_voices.py`  
Expected: JSON with `status: OK`

Run: `python tools/repair_stakeholder_voices.py`  
Expected: JSON with `status: OK`

- [ ] **Step 3: Update the task note result and discussion**

```markdown
## 5) Result（成果物）

### 2026-05-09 checker green
- checker red test を通して requirement-first schema と note frontmatter validator を実装した

## 6) Discussion（反省）
- 次ノート候補：stakeholder_voices を customer-journeys / repository-structure / architecture_rules へ接続する
```
