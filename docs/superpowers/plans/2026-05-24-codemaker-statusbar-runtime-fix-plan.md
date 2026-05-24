# Code Maker Status Bar Runtime Alias Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent the Code Maker single-file bundle from crashing when `StatusBar._resolve_zone_name()` resolves the current zone.

**Architecture:** Add one bundle smoke regression that exercises the status bar zone-name path in the generated single-file bundle. Then make the smallest possible bundler change so `import src.runtime.main_runtime as runtime` survives bundling as a module alias, while preserving the existing `M` alias behavior.

**Tech Stack:** Python 3, pytest, git worktree, Code Maker bundler

---

### Task 1: Add a failing bundle regression and fix the alias rewrite

**Files:**
- Modify: `test/test_codemaker_bundle_smoke.py`
- Modify: `tools/codemaker_bundler.py`
- Verify: `steering/2026年5月24日 アプリ：Code Maker版ステータスバーのzone名描画で未定義エラー.md`

- [ ] **Step 1: Record the current bundled `_resolve_zone_name()` output**

Run:

```bash
python - <<'PY'
from tools.codemaker_bundler import build_bundled_source
source = build_bundled_source()
needle = "def _resolve_zone_name"
index = source.find(needle)
print(source[index:index + 400])
PY
```

Expected: bundled source shows `runtime.get_zone(...)` but no local `runtime = ...` binding above it.

- [ ] **Step 2: Write the failing regression test**

Add this test to `test/test_codemaker_bundle_smoke.py`:

```python
    def test_status_bar_zone_name_resolves_in_bundle(self):
        mod = self._exec_bundle()
        player = types.SimpleNamespace(y=0, in_dungeon=False)
        game = types.SimpleNamespace(has_jp_font=False)
        status_bar = mod.__dict__["StatusBar"](game=game)
        try:
            zone_name = status_bar._resolve_zone_name(player)
        except NameError as exc:  # pragma: no cover
            self.fail(f"StatusBar._resolve_zone_name() raised NameError: {exc}")
        self.assertIsInstance(zone_name, str)
        self.assertNotEqual(zone_name, "")
```

- [ ] **Step 3: Run the test to verify it fails for the right reason**

Run:

```bash
python -m pytest test/test_codemaker_bundle_smoke.py -q
```

Expected: FAIL in `test_status_bar_zone_name_resolves_in_bundle` with `NameError: name 'runtime' is not defined`.

- [ ] **Step 4: Implement the minimal bundler fix**

Update `tools/codemaker_bundler.py` so a single-line local module import with alias is rewritten to a module alias assignment instead of being dropped. The change should preserve the current special handling for `import src.runtime.main_runtime as M`.

Target shape:

```python
def _consume_one_import_line(
    lines: list[str],
    cursor: int,
    out_lines: list[str],
    line: str,
) -> int:
    module_alias_match = _LOCAL_MODULE_IMPORT_AS_RE.match(line)
    if module_alias_match is not None:
        _emit_module_alias(out_lines, line, module_alias_match)
        return cursor + 1
    ...
```

and

```python
def _emit_module_alias(
    out_lines: list[str],
    line: str,
    match: re.Match,
) -> None:
    indent = line[: len(line) - len(line.lstrip())]
    alias = match.group(1)
    out_lines.append(f"{indent}{alias} = M")
```

- [ ] **Step 5: Run the regression to verify it passes**

Run:

```bash
python -m pytest test/test_codemaker_bundle_smoke.py -q
```

Expected: PASS, including the new status bar regression.

- [ ] **Step 6: Run full verification**

Run:

```bash
python -m pytest test/ -q
```

Expected: all tests pass.

- [ ] **Step 7: Update the tasknote with results and close it**

Update:

- `status: done`
- `dateModified`
- `## 5) Tasklist`
- `## 6) 作業ログ`
- `## 7) 評価と成果物`
- `## 8) Discussion`
- `## 9) Closing`

Then move the note to `steering/done/` if it is fully complete.
