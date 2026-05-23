# LLM Wiki Prune To Karpathy Minimum Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the current repo-local LLM Wiki helper-layer implementation so `llm-wiki/` is reduced to a raw-only base.

**Architecture:** Treat this as a bounded cleanup, not a redesign. Delete the helper tree under `llm-wiki/`, delete the dedicated generator and tests, delete rollout-only docs and tasknotes, then verify that only the raw base remains and the broader test suite still passes.

**Tech Stack:** git, markdown docs, Python test suite, ripgrep

---

### Task 1: Remove The `llm-wiki/` Helper Tree

**Files:**
- Delete: `llm-wiki/README.md`
- Delete: `llm-wiki/checklists/.gitkeep`
- Delete: `llm-wiki/checklists/architecture-checklist.md`
- Delete: `llm-wiki/checklists/framework-checklist.md`
- Delete: `llm-wiki/checklists/ux-checklist.md`
- Delete: `llm-wiki/wiki/areas/.gitkeep`
- Delete: `llm-wiki/wiki/candidates/.gitkeep`
- Delete: `llm-wiki/wiki/candidates/concepts.md`
- Delete: `llm-wiki/wiki/candidates/entities.md`
- Delete: `llm-wiki/wiki/index.md`
- Delete: `llm-wiki/wiki/indexes/.gitkeep`
- Delete: `llm-wiki/wiki/indexes/tasknotes.md`
- Delete: `llm-wiki/wiki/log.md`
- Delete: `llm-wiki/wiki/maintenance.md`
- Delete: `llm-wiki/wiki/query/.gitkeep`
- Delete: `llm-wiki/wiki/query/README.md`
- Delete: `llm-wiki/wiki/query/spot-check.md`
- Keep: `llm-wiki/raw/knowledge/.gitkeep`
- Keep: `llm-wiki/raw/tasknotes/.gitkeep`

- [ ] **Step 1: Capture the pre-delete tree**

Run: `find llm-wiki -maxdepth 3 -type f | sort`

Expected: output includes `llm-wiki/README.md`, files under `llm-wiki/checklists/`, and files under `llm-wiki/wiki/`.

- [ ] **Step 2: Delete the helper-layer files and directories**

```bash
git rm llm-wiki/README.md
git rm -r llm-wiki/checklists llm-wiki/wiki
```

- [ ] **Step 3: Verify that `llm-wiki/` is now raw-only**

Run: `find llm-wiki -maxdepth 3 -type f | sort`

Expected:

```text
llm-wiki/raw/knowledge/.gitkeep
llm-wiki/raw/tasknotes/.gitkeep
```

- [ ] **Step 4: Commit the tree reduction**

```bash
git add llm-wiki
git commit -m "refactor: prune llm-wiki helper tree"
```

### Task 2: Remove Generator Tooling And Dedicated Rollout Assets

**Files:**
- Delete: `tools/gen_wiki.py`
- Delete: `test/test_gen_wiki.py`
- Delete: `steering/llm-wiki/README.md`
- Delete: `steering/llm-wiki/フィール流LLM Wikiの作り方（途中まで）.md`
- Delete: `steering/llm-wiki/child-tasknotes/01-練習用プロジェクトの正本docsとGit snapshot候補を棚卸しする.md`
- Delete: `steering/llm-wiki/child-tasknotes/02-練習用プロジェクトのclosed tasknotes投入候補と順番を固定する.md`
- Delete: `steering/llm-wiki/child-tasknotes/03-練習用プロジェクト向けLLM Wiki skeletonと命名ルールを置く.md`
- Delete: `steering/llm-wiki/child-tasknotes/04-練習用プロジェクトでminimal ingestとsummariesを通す.md`
- Delete: `steering/llm-wiki/child-tasknotes/05-練習用プロジェクトでraw tasknotes indexとarea current-stateを通す.md`
- Delete: `steering/llm-wiki/child-tasknotes/06-練習用プロジェクトでread-only queryを通す.md`
- Delete: `steering/llm-wiki/child-tasknotes/07-練習用プロジェクトでraw knowledgeをrebuild summaries対象に含める.md`
- Delete: `steering/llm-wiki/child-tasknotes/08-練習用プロジェクトでconcept entity candidatesを出す.md`
- Delete: `steering/llm-wiki/child-tasknotes/09-architecture.mdをchecklist正本へ変換する.md`
- Delete: `steering/llm-wiki/child-tasknotes/10-ux-policy.mdをchecklist正本へ変換する.md`
- Delete: `steering/llm-wiki/child-tasknotes/11-checklist docsをwiki raw knowledgeとsummariesに反映する.md`
- Delete: `steering/llm-wiki/child-tasknotes/12-小さな開発task1本でLLM Wikiとchecklistを試運転する.md`
- Delete: `docs/superpowers/plans/2026-05-22-llm-wiki-tasknote-bootstrap.md`
- Delete: `docs/superpowers/plans/2026-05-23-llm-wiki-root-rename.md`
- Delete: `docs/superpowers/specs/2026-05-23-llm-wiki-root-rename-design.md`
- Delete: `steering/done/2026年5月22日 Karpathy方針へ寄せてindexとlogを先に通しarea current-stateを採用しない.md`
- Delete: `steering/done/2026年5月22日 練習用プロジェクトでminimal ingestとsummariesを通す.md`
- Delete: `steering/done/2026年5月22日 練習用プロジェクトのclosed tasknotes投入候補と順番を固定する.md`
- Delete: `steering/done/2026年5月22日 練習用プロジェクトの正本docsとGit snapshot候補を棚卸しする.md`
- Delete: `steering/done/2026年5月22日 練習用プロジェクト向けLLM Wiki skeletonと命名ルールを置く.md`
- Delete: `steering/done/2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す.md`
- Delete: `steering/done/2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する.md`
- Delete: `steering/done/2026年5月23日 開発基盤：LLM Wikiルートをllm-wikiへ改名する.md`

- [ ] **Step 1: Confirm the dedicated rollout assets still exist**

Run: `test -f tools/gen_wiki.py && test -f test/test_gen_wiki.py && find steering/llm-wiki -maxdepth 3 -type f | sort | head`

Expected: command succeeds and prints files under `steering/llm-wiki/`.

- [ ] **Step 2: Delete the generator, tests, and dedicated rollout docs**

```bash
git rm tools/gen_wiki.py test/test_gen_wiki.py
git rm -r steering/llm-wiki
git rm docs/superpowers/plans/2026-05-22-llm-wiki-tasknote-bootstrap.md \
  docs/superpowers/plans/2026-05-23-llm-wiki-root-rename.md \
  docs/superpowers/specs/2026-05-23-llm-wiki-root-rename-design.md
git rm 'steering/done/2026年5月22日 Karpathy方針へ寄せてindexとlogを先に通しarea current-stateを採用しない.md' \
  'steering/done/2026年5月22日 練習用プロジェクトでminimal ingestとsummariesを通す.md' \
  'steering/done/2026年5月22日 練習用プロジェクトのclosed tasknotes投入候補と順番を固定する.md' \
  'steering/done/2026年5月22日 練習用プロジェクトの正本docsとGit snapshot候補を棚卸しする.md' \
  'steering/done/2026年5月22日 練習用プロジェクト向けLLM Wiki skeletonと命名ルールを置く.md' \
  'steering/done/2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す.md' \
  'steering/done/2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する.md' \
  'steering/done/2026年5月23日 開発基盤：LLM Wikiルートをllm-wikiへ改名する.md'
```

- [ ] **Step 3: Verify that active surfaces no longer depend on the deleted helper layers**

Run:

```bash
rg -n "gen_wiki|llm-wiki/wiki|llm-wiki/checklists|summaries/|query/|candidates/" \
  AGENTS.md docs llm-wiki test tools steering \
  --glob '!llm-wiki/raw/**' \
  --glob '!docs/superpowers/specs/2026-05-23-llm-wiki-prune-to-karpathy-minimum-design.md' \
  --glob '!docs/superpowers/plans/2026-05-23-llm-wiki-prune-to-karpathy-minimum-plan.md' \
  --glob '!steering/2026年5月23日 開発基盤：llm-wikiをカルパシー最小形まで削減する.md'
```

Expected: no matches.

- [ ] **Step 4: Commit the rollout cleanup**

```bash
git add tools test docs steering
git commit -m "refactor: remove llm-wiki rollout assets"
```

### Task 3: Run Full Verification And Record The Cleanup

**Files:**
- Modify: `steering/2026年5月23日 開発基盤：llm-wikiをカルパシー最小形まで削減する.md`
- Verify: `test/`

- [ ] **Step 1: Run the full test suite**

Run: `python -m pytest test/ -q`

Expected: PASS with the repo test suite green.

- [ ] **Step 2: Update the tasknote with the actual results**

```md
## 5) Tasklist

- [x] 削減設計を spec に固定する
- [x] `llm-wiki/` を raw-only にする
- [x] `tools/gen_wiki.py` と `test/test_gen_wiki.py` を削除する
- [x] 専用 docs と tasknotes を削除する
- [x] `rg` と `pytest` で verify する

## 6) Result

- `llm-wiki/` から `README.md`、`checklists/`、`wiki/` を削除し、`raw/` だけを残した
- `tools/gen_wiki.py` と `test/test_gen_wiki.py` を削除した
- `steering/llm-wiki/`、旧 rollout plan/spec、専用 done note 群を削除した
- `rg` の active-surface check を通し、`python -m pytest test/ -q` を通した
```

```md
## 7) Discussion

### 2026-05-23 <time>（完了）

**Observe**：`llm-wiki` の helper tree と `gen_wiki` 周辺は repo 内で独立した rollout 単位として閉じていた。  
**Think**：raw-only へ戻すには、helper tree だけでなく、その導入と保守のための専用 docs/tasknotes も同時に消す必要があった。  
**Act**：helper tree、tooling、専用 docs を一括整理し、test suite で回帰が無いことを確認した。
```

- [ ] **Step 3: Commit the execution record**

```bash
git add 'steering/2026年5月23日 開発基盤：llm-wikiをカルパシー最小形まで削減する.md'
git commit -m "docs: record llm-wiki reduction results"
```
