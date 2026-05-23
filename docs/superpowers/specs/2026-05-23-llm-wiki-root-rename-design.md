# LLM Wiki Root Rename Design

**Goal:** Rename the repo-local LLM Wiki root from `wiki/` to `llm-wiki/` so the top-level purpose is explicit and the nested `wiki/wiki/` path confusion goes away.

**Scope:** This change updates the repo-local wiki root, generator defaults, tests, and active operational docs. It does not rewrite historical tasknote prose that records the old path at the time those notes were written.

## Current State

- The repo-local LLM Wiki currently lives under `wiki/`.
- Generated artifacts are split across `wiki/raw/`, `wiki/wiki/`, and `wiki/checklists/`.
- `tools/gen_wiki.py` and `test/test_gen_wiki.py` assume `wiki/` as the default output root.
- Operational docs such as `wiki/README.md` and generated query/index pages describe the old root directly.

## Problem

- `wiki/wiki/` is visually confusing in links, CLI output, and human discussion.
- The top-level directory name does not communicate that the tree is specific to the LLM Wiki workflow.
- Default generator behavior and tests reinforce the ambiguous path layout.

## Chosen Approach

Perform a hard repo-local root rename from `wiki/` to `llm-wiki/`.

- Keep the internal layout unchanged under the new root:
  - `llm-wiki/raw/`
  - `llm-wiki/wiki/`
  - `llm-wiki/checklists/`
- Update `tools/gen_wiki.py` so the default output root is `<repo>/llm-wiki`.
- Update tests so their fixture roots and checklist source paths use `llm-wiki`.
- Move existing generated and maintained artifacts into `llm-wiki/`.
- Update active operational docs and generated navigation artifacts to reference `llm-wiki`.

## Alternatives Considered

### 1. Keep `wiki/` and only rename the inner `wiki/`

Rejected because it keeps the ambiguous top-level root and does not match the requested rename intent.

### 2. Rename to `llm-wiki/` and leave a compatibility stub at `wiki/`

Rejected for now because it preserves two competing roots and reintroduces discovery ambiguity. If compatibility is later needed, a stub can be added as a separate change.

## File and Directory Impact

### Directories

- Rename: `wiki/` -> `llm-wiki/`

### Code

- Modify: `tools/gen_wiki.py`
  - change default wiki root resolution and path wording in docstrings/comments
- Modify: `test/test_gen_wiki.py`
  - update fixture paths and expected outputs

### Docs and Generated Artifacts

- Move and update: `llm-wiki/README.md`
- Regenerate under new root:
  - `llm-wiki/wiki/index.md`
  - `llm-wiki/wiki/log.md`
  - `llm-wiki/wiki/indexes/tasknotes.md`
  - `llm-wiki/wiki/query/README.md`
  - `llm-wiki/wiki/candidates/*.md`
- Update any active non-historical docs that instruct current operators to use the old root

## Non-Goals

- Rewriting historical `steering/done/*.md` notes just to replace old path strings
- Changing the internal subdirectory names (`raw`, `wiki`, `checklists`)
- Changing the ingest model, summary structure, or checklist semantics

## Verification

- `python -m pytest test/test_gen_wiki.py -q`
- `python -m pytest test/ -q`
- `find llm-wiki -maxdepth 3 -type d | sort`
- Spot-check for stale operational references with `rg`

## Risks and Mitigations

- Risk: hidden references to `wiki/` remain in active tooling or docs.
  - Mitigation: run `rg` across code, tests, and active docs and update the current operational surface.
- Risk: historical notes become inconsistent with current paths.
  - Mitigation: preserve them as historical records and limit path rewrites to active docs and generated artifacts.
- Risk: checklist ingest breaks if source paths are not updated.
  - Mitigation: update test fixtures and generator expectations for checklist sources under `llm-wiki/checklists/`.
