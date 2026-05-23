# LLM Wiki Reduction To Raw-Only Base

## Goal

Reduce the repo-local `llm-wiki/` implementation to a raw-only base.

The intended end state for this task is:

- `llm-wiki/` keeps only `raw/`
- repo-local helper layers such as `wiki/`, `checklists/`, summaries, query notes, and candidates are removed
- generation tooling and tests dedicated to that helper layer are removed
- docs and tasknotes that exist specifically to create or maintain that helper layer are removed

This task does not rebuild a new Karpathy-style wiki yet. It only clears the current extra structure.

## Motivation

The current repo-local LLM Wiki implementation grew beyond the minimal pattern the user wants to return to.

Karpathy's core framing is:

- raw sources are immutable source material
- the wiki layer is LLM-maintained markdown
- the schema guides workflows and conventions

For this task, the user wants to go even smaller first: keep the raw base and remove the current repo-specific helper system before deciding what to rebuild.

Reference:

- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## Scope

### In scope

- Remove `llm-wiki/README.md`
- Remove `llm-wiki/checklists/`
- Remove `llm-wiki/wiki/`
- Remove `tools/gen_wiki.py`
- Remove `test/test_gen_wiki.py`
- Remove spec / plan / steering notes whose purpose is the current helper-layer rollout
- Clean up active references to deleted paths and files

### Out of scope

- Designing the next wiki structure
- Replacing `gen_wiki.py` with a new tool
- Writing new `index.md` or `log.md`
- Reorganizing unrelated tasknotes, docs, or tests
- Changing canonical project docs such as `docs/framework-rule.md` or `docs/ux-policy.md`

## Target State

After this task:

- `llm-wiki/` exists only as a container for `raw/`
- there is no repo-local generated wiki navigation layer
- there is no repo-local checklist layer under `llm-wiki/`
- there is no `gen_wiki` implementation or dedicated test file
- there are no active docs that instruct contributors to use the deleted helper layers

Historical references that happen to mention `llm-wiki` in broader contexts do not need to be exhaustively erased unless they are part of the dedicated rollout assets being removed.

## Removal Rules

### Rule 1: Keep `raw/`, remove helper layers

Keep:

- `llm-wiki/raw/`

Remove:

- `llm-wiki/README.md`
- `llm-wiki/checklists/`
- `llm-wiki/wiki/`

### Rule 2: Remove helper-layer tooling

Remove:

- `tools/gen_wiki.py`
- `test/test_gen_wiki.py`

If any test, doc, or tasknote exists only to support this toolchain, remove it as part of the same change.

### Rule 3: Remove dedicated rollout documentation

Remove documents that exist specifically to introduce, rename, or operate the current repo-local helper-layer implementation, including:

- `steering/llm-wiki/`
- `docs/superpowers/plans/*llm-wiki*`
- `docs/superpowers/specs/*llm-wiki*` that describe the old helper rollout
- `steering/done/` notes whose main subject is building or evolving this helper-layer structure

Keep broader project docs unless they actively instruct current users to rely on the removed helper layers.

### Rule 4: Do not rebuild during cleanup

This change stops at deletion and cleanup. It does not replace the deleted structure with a new `wiki/`, `index.md`, `log.md`, or any new ingestion workflow.

## Candidate File Sets

### `llm-wiki/` tree

Remove:

- `llm-wiki/README.md`
- `llm-wiki/checklists/`
- `llm-wiki/wiki/`

Keep:

- `llm-wiki/raw/`

### Tooling and tests

Remove:

- `tools/gen_wiki.py`
- `test/test_gen_wiki.py`

### Dedicated rollout docs

Expected removal candidates:

- `steering/llm-wiki/README.md`
- `steering/llm-wiki/フィール流LLM Wikiの作り方（途中まで）.md`
- `steering/llm-wiki/child-tasknotes/*`
- `docs/superpowers/plans/2026-05-22-llm-wiki-tasknote-bootstrap.md`
- `docs/superpowers/plans/2026-05-23-llm-wiki-root-rename.md`
- `docs/superpowers/specs/2026-05-23-llm-wiki-root-rename-design.md`
- `steering/done/2026年5月22日 Karpathy方針へ寄せてindexとlogを先に通しarea current-stateを採用しない.md`
- `steering/done/2026年5月22日 練習用プロジェクトのclosed tasknotes投入候補と順番を固定する.md`
- `steering/done/2026年5月22日 練習用プロジェクトの正本docsとGit snapshot候補を棚卸しする.md`
- `steering/done/2026年5月22日 練習用プロジェクト向けLLM Wiki skeletonと命名ルールを置く.md`
- `steering/done/2026年5月22日 練習用プロジェクトでminimal ingestとsummariesを通す.md`
- `steering/done/2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す.md`
- `steering/done/2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する.md`
- `steering/done/2026年5月23日 開発基盤：LLM Wikiルートをllm-wikiへ改名する.md`

The final removal list can expand slightly if other files are discovered to be dedicated only to this rollout.

## Verification

Run:

```bash
rg -n "gen_wiki|llm-wiki/wiki|llm-wiki/checklists|summaries/|query/|candidates/" .
python -m pytest test/ -q
find llm-wiki -maxdepth 3 -type f | sort
```

Success means:

- no active repo surface still depends on the removed helper-layer structure
- full test suite still passes
- `llm-wiki/` contains only the remaining `raw/` base

## Risks

### Risk 1: Over-deleting historical notes

Mitigation:

- focus deletions on dedicated rollout files
- do not broadly rewrite unrelated historical material

### Risk 2: Hidden references to deleted paths

Mitigation:

- use `rg` after deletion
- fix or remove any remaining active references

### Risk 3: Removing files that tests still rely on

Mitigation:

- run full `pytest`
- either remove dead references or restore only what is truly required by unrelated functionality
