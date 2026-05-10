# Architecture Rules label_ja Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `docs/architecture_rules.yml` の主要 `id` 付きブロックへ `label_ja` を追加し、checker / fixer がそれを保持したまま current worktree の coverage key 変更とも両立する状態にする。

**Architecture:** 先に focused test で `label_ja` 可読性契約と `guardian_autofix` 両立を固定し、その後 checker/fixer を更新する。最後に YAML 本体へ `label_ja` を投入し、CLI と focused pytest で Gherkin を満たすことを確認する。

**Tech Stack:** Python, PyYAML, pytest, repo-local YAML task notes

---

### Task 1: Focused Red Tests For label_ja And Coverage Metadata

**Files:**
- Modify: `test/test_architecture_rules_checker.py`
- Modify: `test/test_fix_architecture_rules.py`
- Test: `test/test_architecture_rules_checker.py`
- Test: `test/test_fix_architecture_rules.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_validation_rules_include_label_ja_on_major_sections(self):
    data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))
    self.assertTrue(all("label_ja" in item for item in data["facts"]["principles"]))
    self.assertTrue(all("label_ja" in item for item in data["facts"]["flows"]))
    self.assertTrue(all("label_ja" in item for item in data["facts"]["entry_points"]))
    self.assertTrue(all("label_ja" in item for item in data["facts"]["runbooks"]))
    self.assertTrue(all("label_ja" in item for item in data["facts"]["codemaker_bundle_contracts"]))
    self.assertTrue(all("label_ja" in item for item in data["facts"]["migration_notes"]))
    self.assertTrue(all("label_ja" in item for item in data["validation_rules"]))

def test_validation_rules_include_guardian_autofix_metadata(self):
    data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))
    for rule in data["validation_rules"]:
        coverage = rule["coverage"]
        self.assertIn("guardian_autofix", coverage)
        self.assertNotIn("repair_autofix", coverage)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test/test_architecture_rules_checker.py test/test_fix_architecture_rules.py -q`
Expected: FAIL because `label_ja` is missing and checker/tests still expect `repair_autofix`

- [ ] **Step 3: Add a fixer preservation test**

```python
def test_fix_runtime_entry_chain_preserves_label_ja(self):
    # runtime_entry_chain に label_ja がある YAML fixture を作り、
    # fixer 実行後も label_ja が残ることを確認する
```

- [ ] **Step 4: Run the fixer test to verify it fails**

Run: `python -m pytest test/test_fix_architecture_rules.py -q`
Expected: FAIL because runtime entry canonicalization currently drops unknown keys

- [ ] **Step 5: Commit**

```bash
git add test/test_architecture_rules_checker.py test/test_fix_architecture_rules.py
git commit -m "test: define architecture_rules label_ja contract"
```

### Task 2: Make Checker Accept Current Coverage Key And Preserve label_ja

**Files:**
- Modify: `tools/architecture_rules/check_architecture_rules.py`
- Modify: `tools/architecture_rules/fix_architecture_rules.py`
- Test: `test/test_architecture_rules_checker.py`
- Test: `test/test_fix_architecture_rules.py`

- [ ] **Step 1: Update the checker schema and coverage review logic**

```python
REPAIR_AUTOFIX_KEY = "guardian_autofix"

for key in ("deterministic_review", "next_checker_unit", "rationale"):
    if key not in coverage:
        raise KeyError(...)
if REPAIR_AUTOFIX_KEY not in coverage:
    raise KeyError(...)
```

- [ ] **Step 2: Run focused checker tests**

Run: `python -m pytest test/test_architecture_rules_checker.py -q`
Expected: still FAIL because `docs/architecture_rules.yml` has no `label_ja` yet

- [ ] **Step 3: Preserve extra keys when fixing runtime entry points**

```python
def _entry_matches_canonical(current, canonical):
    # canonical keys だけ比較し、label_ja などの extra key は許容する

def _merge_entry_preserving_extras(current, canonical):
    # canonical field は上書きするが、label_ja は残す
```

- [ ] **Step 4: Run focused fixer tests**

Run: `python -m pytest test/test_fix_architecture_rules.py -q`
Expected: PASS for the new preservation test

- [ ] **Step 5: Commit**

```bash
git add tools/architecture_rules/check_architecture_rules.py tools/architecture_rules/fix_architecture_rules.py
git commit -m "feat: preserve architecture_rules label_ja metadata"
```

### Task 3: Populate label_ja In YAML And Verify Gherkin

**Files:**
- Modify: `docs/architecture_rules.yml`
- Modify: `steering/20260509-architecture-rules-label-ja.md`
- Test: `test/test_architecture_rules_checker.py`
- Test: `test/test_fix_architecture_rules.py`

- [ ] **Step 1: Add `label_ja` to the major sections**

```yaml
- id: code_maker_primary_editor
  label_ja: Code Maker を子どもの正式編集面として守る
  summary: Pyxel Code Maker は子どもの正式な編集面である。
```

- [ ] **Step 2: Run focused tests**

Run: `python -m pytest test/test_architecture_rules_checker.py test/test_fix_architecture_rules.py -q`
Expected: PASS

- [ ] **Step 3: Run CLI verification for the gherkin scenarios**

Run: `python tools/check_architecture_rules.py`
Expected: JSON with `run_ok: true`

Run: `python tools/fix_architecture_rules.py --rule-id runtime_entry_chain`
Expected: `status` is `OK` or `FIXED`, with no loss of `label_ja`

- [ ] **Step 4: Update the task note result/discussion**

```markdown
## 5) Result
- 追加した `label_ja` 対象
- checker/fixer compatibility の検証結果

## 6) Discussion
- 今後 `id` を増やすときは同時に `label_ja` を付ける
```

- [ ] **Step 5: Commit**

```bash
git add docs/architecture_rules.yml steering/20260509-architecture-rules-label-ja.md
git commit -m "docs: add label_ja to architecture rules"
```
