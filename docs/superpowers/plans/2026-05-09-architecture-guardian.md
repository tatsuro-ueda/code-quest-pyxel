# Architecture Guardian Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** architecture rule 違反を検知するだけでなく、自動修復と再検査を最大 5 周回す guardian を追加する。

**Architecture:** 既存の `check_architecture_rules.py` を強化して診断 JSON を richer にし、その上に `architecture_guardian.py` を載せる。guardian は checker 結果から autofixable rule を選び、fixer を実行し、同じ repo を再検査して収束するまで回す。

**Tech Stack:** Python 3, unittest/pytest, subprocess, pathlib, PyYAML, json

---

## File Structure

- Modify: `tools/check_architecture_rules.py`
  - schema validation, `--rule-id`, `--fail-on-warning`, expected/observed support
- Create: `tools/architecture_guardian.py`
  - guardian loop, fixer registry, CLI
- Modify: `docs/architecture_rules.yml`
  - rule metadata normalization when needed by guardian tests
- Create: `test/test_architecture_guardian.py`
  - guardian loop / autofix / stop condition tests
- Modify: `test/test_architecture_rules_checker.py`
  - checker hardening tests
- Modify: `steering/done/20260509-architecture-guardian.md`
  - progress and results

### Task 1: checker hardening tests を先に書く

**Files:**
- Modify: `test/test_architecture_rules_checker.py`

- [ ] **Step 1: rule filtering の failing test を書く**

```python
def test_run_checker_can_filter_single_rule():
    checker = load_checker_module()
    result = checker.run_checker(ROOT, ROOT / "docs" / "architecture_rules.yml", rule_ids={"runtime_entry_chain"})
    assert result["summary"]["total_rules"] == 1
    assert [item["rule_id"] for item in result["results"]] == ["runtime_entry_chain"]
```

- [ ] **Step 2: fail-on-warning CLI の failing test を書く**

```python
def test_cli_fail_on_warning_returns_exit_one():
    completed = subprocess.run([... "--fail-on-warning" ...], check=False, ...)
    assert completed.returncode == 1
```

- [ ] **Step 3: expected / observed payload の failing test を書く**

```python
def test_warning_payload_contains_expected_and_observed():
    ...
    rule = by_rule["generated_files_edit_policy"]
    assert "expected" in rule
    assert "observed" in rule
```

- [ ] **Step 4: red を確認する**

Run: `python3 -m pytest test/test_architecture_rules_checker.py -q`  
Expected: FAIL on missing rule filter / fail-on-warning / expected-observed support

### Task 2: checker hardening を最小実装で通す

**Files:**
- Modify: `tools/check_architecture_rules.py`
- Test: `test/test_architecture_rules_checker.py`

- [ ] **Step 1: schema validation と registry validation を追加する**

```python
def validate_rules_schema(data: dict[str, Any]) -> None:
    ...
```

- [ ] **Step 2: `rule_ids` filter と `fail_on_warning` を実装する**

```python
def run_checker(..., rule_ids: set[str] | None = None) -> dict[str, Any]:
    ...
```

- [ ] **Step 3: warning record に `expected` / `observed` / `rule_source` を追加する**

```python
return {
    ...,
    "expected": outcome.expected,
    "observed": outcome.observed,
    "rule_source": str(context.rules_path),
}
```

- [ ] **Step 4: green を確認する**

Run: `python3 -m pytest test/test_architecture_rules_checker.py -q`  
Expected: PASS

### Task 3: guardian loop の failing test を書く

**Files:**
- Create: `test/test_architecture_guardian.py`

- [ ] **Step 1: guardian module import test を書く**

```python
def load_guardian_module():
    try:
        import architecture_guardian
    except ImportError as exc:
        raise AssertionError(...) from exc
```

- [ ] **Step 2: generated autofix loop の failing test を書く**

```python
def test_guardian_autofixes_generated_rule_until_clean():
    ...
    result = guardian.run_guardian(repo_root, rules_path, max_cycles=5)
    assert result["status"] == "AUTOFIXED"
    assert result["cycles"] <= 5
```

- [ ] **Step 3: no-fix remaining issue test を書く**

```python
def test_guardian_returns_needs_human_when_issue_remains():
    ...
    assert result["status"] == "NEEDS_HUMAN"
```

- [ ] **Step 4: red を確認する**

Run: `python3 -m pytest test/test_architecture_guardian.py -q`  
Expected: FAIL with missing guardian module

### Task 4: guardian loop と fixers を実装する

**Files:**
- Create: `tools/architecture_guardian.py`
- Test: `test/test_architecture_guardian.py`

- [ ] **Step 1: guardian result model と loop 骨格を実装する**

```python
def run_guardian(repo_root: Path, rules_path: Path, *, max_cycles: int = 5) -> dict[str, object]:
    ...
```

- [ ] **Step 2: generated / dist / runbook / runtime fixer registry を実装する**

```python
FIXER_REGISTRY = {
    "generated_files_edit_policy": fix_generated_files_edit_policy,
    ...
}
```

- [ ] **Step 3: autofix 関数を最小実装する**

```python
def fix_generated_files_edit_policy(...): ...
def fix_dist_not_source(...): ...
def fix_build_runbook_paths(...): ...
def fix_runtime_entry_chain(...): ...
```

- [ ] **Step 4: green を確認する**

Run: `python3 -m pytest test/test_architecture_guardian.py -q`  
Expected: PASS

### Task 5: integration verification と note 更新

**Files:**
- Modify: `steering/done/20260509-architecture-guardian.md`

- [ ] **Step 1: guardian CLI integration check を実行する**

Run: `python3 tools/architecture_guardian.py`  
Expected: valid JSON, exit 0 when clean or autofixed

- [ ] **Step 2: checker + guardian tests を実行する**

Run: `python3 -m pytest test/test_architecture_rules_checker.py test/test_architecture_guardian.py -q`  
Expected: PASS

- [ ] **Step 3: full pytest を実行する**

Run: `python3 -m pytest test/ -q`  
Expected: PASS

- [ ] **Step 4: steering note の Tasklist / Result / Discussion を更新する**

```markdown
- [x] T1: ...
```
