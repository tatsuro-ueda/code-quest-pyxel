# LLM Wiki Root Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the repo-local LLM Wiki root from `wiki/` to `llm-wiki/`, update generator defaults, and keep active docs and generated artifacts aligned.

**Architecture:** Keep the internal structure unchanged under the new root and update only the root directory name plus code/docs that assume it. Drive the generator behavior change with failing tests first, then move the existing artifact tree and refresh active documentation to point at the new location.

**Tech Stack:** Python, pytest, git worktree, markdown docs

---

### Task 1: Lock The New Root In Tests

**Files:**
- Modify: `test/test_gen_wiki.py`
- Modify later: `tools/gen_wiki.py`
- Test: `test/test_gen_wiki.py`

- [ ] **Step 1: Write the failing tests**

```python
    def test_generate_wiki_defaults_output_root_to_llm_wiki(self):
        gen_wiki = load_gen_wiki_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)
            knowledge_path = repo_root / "docs" / "customer-jobs.md"
            knowledge_path.write_text("# 顧客のジョブ\n", encoding="utf-8")

            result = gen_wiki.generate_wiki(
                knowledge_paths=["docs/customer-jobs.md"],
                tasknote_paths=[],
                repo_root=repo_root,
                today="2026-05-23",
            )

            expected_raw = repo_root / "llm-wiki" / "raw" / "knowledge" / "docs" / "customer-jobs.md"
            self.assertEqual(result["raw_paths"], [expected_raw])
            self.assertTrue(expected_raw.is_file())
```

```python
            llm_wiki_root = repo_root / "llm-wiki"
            result = gen_wiki.generate_wiki(
                knowledge_paths=[],
                tasknote_paths=[],
                checklist_paths=["llm-wiki/checklists/ux-checklist.md"],
                repo_root=repo_root,
                wiki_root=llm_wiki_root,
                today="2026-05-23",
            )
```

```python
            query_text = query_readme.read_text(encoding="utf-8")
            self.assertIn("`llm-wiki/raw/`", query_text)
```

- [ ] **Step 2: Run the targeted test to verify RED**

Run: `python -m pytest test/test_gen_wiki.py -q`

Expected: FAIL because `_resolve_wiki_root()` still defaults to `repo_root / "wiki"` and checklist fixtures still point at `wiki/checklists/...`.

- [ ] **Step 3: Write the minimal implementation**

```python
def _resolve_wiki_root(repo_root: Path, wiki_root: Path | None) -> Path:
    return (wiki_root or (repo_root / "llm-wiki")).resolve()
```

```python
        checklist_paths: `llm-wiki/checklists/...` のような repo 相対 source path。
        wiki_root: 出力先 root。未指定時は `<repo>/llm-wiki`。
```

```python
        "- query 中に `llm-wiki/raw/` を更新しない",
```

- [ ] **Step 4: Run the targeted test to verify GREEN**

Run: `python -m pytest test/test_gen_wiki.py -q`

Expected: PASS with all `test_gen_wiki` cases green.

- [ ] **Step 5: Commit**

```bash
git add test/test_gen_wiki.py tools/gen_wiki.py
git commit -m "test: lock llm-wiki generator root"
```

### Task 2: Move The Artifact Tree And Active Docs

**Files:**
- Rename: `wiki/` -> `llm-wiki/`
- Modify: `llm-wiki/README.md`
- Modify: `llm-wiki/wiki/query/README.md`
- Modify: `llm-wiki/wiki/query/spot-check.md`
- Verify: `llm-wiki/wiki/index.md`
- Verify: `llm-wiki/wiki/log.md`

- [ ] **Step 1: Move the existing tree**

Run: `mv wiki llm-wiki`

Expected: the repo root contains `llm-wiki/` and no longer contains `wiki/`.

- [ ] **Step 2: Update active doc wording**

```md
# llm-wiki

`llm-wiki/` is the repo-local home for LLM Wiki artifacts.

- `llm-wiki/raw/` is a generated snapshot layer built from canonical inputs.
- `llm-wiki/wiki/` contains derived summaries, indexes, query artifacts, and maintenance notes.
- `llm-wiki/checklists/` contains derived checklist docs that can be queried from the wiki layer.
```

```md
- query 中に `llm-wiki/raw/` を更新しない
```

```md
- `llm-wiki/wiki/summaries/knowledge/docs/architecture_rules-summary.md`
- `llm-wiki/wiki/indexes/tasknotes.md`
```

- [ ] **Step 3: Spot-check the moved navigation artifacts**

Run: `sed -n '1,120p' llm-wiki/wiki/index.md`

Expected: existing links remain relative and still resolve inside `llm-wiki/wiki/`.

- [ ] **Step 4: Commit**

```bash
git add llm-wiki
git commit -m "refactor: rename wiki root to llm-wiki"
```

### Task 3: Refresh Verification Notes And Run Full Checks

**Files:**
- Modify: `steering/2026年5月23日 開発基盤：LLM Wikiルートをllm-wikiへ改名する.md`
- Modify: `docs/superpowers/specs/2026-05-23-llm-wiki-root-rename-design.md`
- Verify: `test/`

- [ ] **Step 1: Update the current tasknote with execution results**

```md
### Result

- `wiki/` を `llm-wiki/` へ改名した
- `tools/gen_wiki.py` の default root を `<repo>/llm-wiki` に更新した
- `python -m pytest test/test_gen_wiki.py -q` と `python -m pytest test/ -q` を通した
```

```md
- [x] `wiki/` を `llm-wiki/` へ改名する
- [x] `tools/gen_wiki.py` の default root と path 文言を更新する
```

- [ ] **Step 2: Update the spec wording so file references match reality**

```md
- The repo-local LLM Wiki currently lives under `llm-wiki/`.
- Rename: `llm-wiki/` -> already applied in repo state
```

- [ ] **Step 3: Run verification**

Run: `python -m pytest test/test_gen_wiki.py -q`
Expected: PASS

Run: `python -m pytest test/ -q`
Expected: PASS

Run: `find llm-wiki -maxdepth 3 -type d | sort`
Expected: `llm-wiki/raw`, `llm-wiki/wiki`, and `llm-wiki/checklists` all appear

Run: `rg -n "wiki/wiki|wiki/raw|wiki/checklists" llm-wiki tools test`
Expected: only intentional historical or inner-layout references remain; no active root references requiring further changes

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-05-23-llm-wiki-root-rename-design.md \
  'steering/2026年5月23日 開発基盤：LLM Wikiルートをllm-wikiへ改名する.md'
git commit -m "docs: record llm-wiki root rename"
```
