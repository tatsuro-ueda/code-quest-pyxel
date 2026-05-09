# Architecture Rules Checker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `docs/architecture_rules.yml` の `validation_rules` を読み、deterministic rule を repo 実体に照らして JSON warning として返す `tools/check_architecture_rules.py` を実装する。

**Architecture:** checker は YAML をロードして rule-runner として動く。`deterministic` rule だけを実行し、`llm_assisted` / `manual` は skipped result を返す。修正ガイドは YAML 側の `suggested_actions` を正本として持ち、Python はそれを結果 JSON に載せるだけにする。

**Tech Stack:** Python 3, PyYAML, unittest/pytest, subprocess, pathlib, json

---

## File Structure

- Create: `tools/check_architecture_rules.py`
  - YAML loader, rule filtering, deterministic check registry, CLI JSON 出力
- Modify: `docs/architecture_rules.yml`
  - 各 `validation_rules` に `suggested_actions` を追加
- Modify: `steering/done/20260509-architecture-rules-checker.md`
  - 実行用 Tasklist と進捗結果
- Create: `test/test_architecture_rules_checker.py`
  - checker の unit / integration test

### Task 1: 仕様テストと YAML 契約を先に固定する

**Files:**
- Modify: `docs/architecture_rules.yml`
- Create: `test/test_architecture_rules_checker.py`

- [ ] **Step 1: YAML 契約の failing test を書く**

```python
def test_validation_rules_include_suggested_actions():
    data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))
    rules = data["validation_rules"]
    assert rules, "validation_rules should not be empty"
    for rule in rules:
        assert "suggested_actions" in rule
        assert isinstance(rule["suggested_actions"], list)
```

- [ ] **Step 2: checker module import の failing test を書く**

```python
def load_checker_module():
    try:
        import check_architecture_rules
    except ImportError as exc:
        raise AssertionError(f"tools/check_architecture_rules.py is missing: {exc}") from exc
    return check_architecture_rules
```

- [ ] **Step 3: deterministic 実行 / skipped JSON の failing test を書く**

```python
def test_run_checker_executes_deterministic_rules_and_skips_others():
    mod = load_checker_module()
    result = mod.run_checker(ROOT, ROOT / "docs" / "architecture_rules.yml")
    assert result["run_ok"] is True
    assert result["summary"]["total_rules"] == 8
    assert result["summary"]["executed_rules"] == 4
    assert result["summary"]["skipped_rules"] == 4
```

- [ ] **Step 4: red を確認する**

Run: `python3 -m pytest test/test_architecture_rules_checker.py -q`  
Expected: FAIL with missing `check_architecture_rules.py` and/or missing `suggested_actions`

### Task 2: YAML metadata と checker 骨格を最小実装する

**Files:**
- Modify: `docs/architecture_rules.yml`
- Create: `tools/check_architecture_rules.py`
- Test: `test/test_architecture_rules_checker.py`

- [ ] **Step 1: `validation_rules` に `suggested_actions` を追加する**

```yaml
  - id: runtime_entry_chain
    ...
    message: runtime の入口構成が architecture 定義から外れている可能性があります
    suggested_actions:
      - facts.runtime.entry_chain の path / symbol と実コードの entry chain をそろえる
      - main.py, src/runtime/main_runtime.py, src/runtime/app.py の委譲関係を崩していないか確認する
```

- [ ] **Step 2: checker の最小骨格を実装する**

```python
def run_checker(repo_root: Path, rules_path: Path) -> dict[str, object]:
    data = load_rules(rules_path)
    results = []
    for rule in data["validation_rules"]:
        mode = rule["enforcement"]["mode"]
        if mode != "deterministic":
            results.append(skipped_result(rule))
            continue
        results.append(run_deterministic_rule(repo_root, data, rule))
    return build_output(results)
```

- [ ] **Step 3: CLI main を実装する**

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(...)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--rules-path", type=Path, default=ROOT / "docs" / "architecture_rules.yml")
    args = parser.parse_args(argv)
    result = run_checker(args.repo_root, args.rules_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
```

- [ ] **Step 4: Task 1 の test を green にする**

Run: `python3 -m pytest test/test_architecture_rules_checker.py -q`  
Expected: PASS on metadata/import/basic summary tests

### Task 3: deterministic check 4 件を TDD で実装する

**Files:**
- Create: `tools/check_architecture_rules.py`
- Test: `test/test_architecture_rules_checker.py`

- [ ] **Step 1: runtime/dist/generated/runbook の OK 判定 test を書く**

```python
def test_default_repo_marks_all_deterministic_rules_ok():
    mod = load_checker_module()
    result = mod.run_checker(ROOT, ROOT / "docs" / "architecture_rules.yml")
    by_rule = {item["rule_id"]: item for item in result["results"]}
    assert by_rule["runtime_entry_chain"]["status"] == "ok"
    assert by_rule["dist_not_source"]["status"] == "ok"
    assert by_rule["generated_files_edit_policy"]["status"] == "ok"
    assert by_rule["build_runbook_paths"]["status"] == "ok"
```

- [ ] **Step 2: warning payload test を書く**

```python
def test_cli_returns_warning_with_suggested_actions_and_exit_zero():
    broken_yaml = make_broken_rules_copy(...)
    completed = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_architecture_rules.py"),
         "--repo-root", str(ROOT), "--rules-path", str(broken_yaml)],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert payload["has_warnings"] is True
```

- [ ] **Step 3: deterministic check 関数を最小実装する**

```python
def wrapper_chain_present(context: CheckContext, rule: dict[str, object]) -> CheckOutcome: ...
def distribution_paths_marked_non_source(context: CheckContext, rule: dict[str, object]) -> CheckOutcome: ...
def generated_entries_mark_non_hand_editable_and_sources(context: CheckContext, rule: dict[str, object]) -> CheckOutcome: ...
def compare_runbook_commands_and_artifact_defs(context: CheckContext, rule: dict[str, object]) -> CheckOutcome: ...
```

- [ ] **Step 4: Task 3 の test を green にする**

Run: `python3 -m pytest test/test_architecture_rules_checker.py -q`  
Expected: PASS on deterministic OK and warning-path tests

### Task 4: CLI integration と最終検証

**Files:**
- Modify: `steering/done/20260509-architecture-rules-checker.md`
- Modify: `test/test_architecture_rules_checker.py`

- [ ] **Step 1: CLI JSON parse test を追加する**

```python
def test_cli_stdout_is_valid_json_for_default_repo():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_architecture_rules.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    payload = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert payload["run_ok"] is True
```

- [ ] **Step 2: checker 専用 test を実行する**

Run: `python3 -m pytest test/test_architecture_rules_checker.py -q`  
Expected: PASS

- [ ] **Step 3: 既存 verify/test を実行する**

Run: `python3 tools/check_architecture_rules.py`  
Expected: exit 0 and valid JSON

Run: `python3 -m pytest test/ -q`  
Expected: PASS

- [ ] **Step 4: steering note の Tasklist / Result / Discussion を更新する**

```markdown
- [x] T1: ...
```
