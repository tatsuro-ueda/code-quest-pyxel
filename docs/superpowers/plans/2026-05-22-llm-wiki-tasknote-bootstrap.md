# LLM Wiki Tasknote Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the repo-local LLM Wiki shared package and leave an autonomous steering note that can drive the first rollout steps without re-discovery.

**Architecture:** Treat `steering/llm-wiki/` as a synced shared package, not the active execution note. Add one repo-local orchestration tasknote under `steering/` that records the package source, repo-specific default decisions, and the next child tasknote sequence (`03 -> 01 -> 02 -> ...`) so future sessions can continue from one entry point.

**Tech Stack:** Markdown, `rsync`, `git status`, repo-local steering notes

---

### Task 1: Sync The Shared Package

**Files:**
- Modify: `steering/llm-wiki/README.md`
- Modify: `steering/llm-wiki/フィール流LLM Wikiの作り方（途中まで）.md`
- Modify: `steering/llm-wiki/child-tasknotes/*.md`

- [x] **Step 1: Compare the shared source with the repo-local copy**

Run: `diff -ru /home/exedev/dotfiles/shared/llm-wiki-how-to /home/exedev/code-quest-pyxel/steering/llm-wiki`

Expected: README plus several child tasknotes differ, confirming the repo-local package is stale.

- [x] **Step 2: Replace the repo-local package in one bulk sync**

Run: `rsync -a --delete '/home/exedev/dotfiles/shared/llm-wiki-how-to/' '/home/exedev/code-quest-pyxel/steering/llm-wiki/'`

Expected: command exits with no output and the repo-local package matches the shared source.

- [x] **Step 3: Re-check the package diff**

Run: `diff -ru /home/exedev/dotfiles/shared/llm-wiki-how-to /home/exedev/code-quest-pyxel/steering/llm-wiki`

Expected: no diff output.

### Task 2: Add The Repo-Local Orchestration Note

**Files:**
- Create: `steering/2026年5月22日 LLM Wiki shared packageを導入して自律実行ルートを固定する.md`
- Reference: `steering/llm-wiki/README.md`
- Reference: `steering/llm-wiki/child-tasknotes/03-練習用プロジェクト向けLLM Wiki skeletonと命名ルールを置く.md`
- Reference: `steering/llm-wiki/child-tasknotes/09-architecture.mdをchecklist正本へ変換する.md`
- Reference: `steering/llm-wiki/child-tasknotes/10-ux-policy.mdをchecklist正本へ変換する.md`

- [x] **Step 1: Create a tasknote entry point with repo-specific defaults**

Write a steering note that captures:

```text
- the shared package has been synced into steering/llm-wiki
- future execution should start from child tasknote 03 before 01 because this repo has a strong SSoT/codegen policy
- default assumptions: root wiki/ output, generator-based raw creation, architecture_rules.yml as architecture source, existing docs are investigated directly for UX checklist conversion, hybrid query mode, closed tasknote cap 30
```

- [x] **Step 2: Give the note an executable Tasklist**

Include a `Tasklist` section with:

```text
- completed items for package sync and orchestration setup
- pending items for instantiating the first dated execution note from child 03
- pending items for actual wiki bootstrap work after the user leaves
```

- [x] **Step 3: Record the known process gap**

Document that `scripts/commit-tasknote.sh` does not exist in this repo, so the manage-tasknotes auto-commit convention cannot be followed verbatim here.

### Task 3: Verify The New Entry Point

**Files:**
- Verify: `steering/llm-wiki/**/*`
- Verify: `steering/2026年5月22日 LLM Wiki shared packageを導入して自律実行ルートを固定する.md`

- [x] **Step 1: Verify the synced package file set**

Run: `find steering/llm-wiki -maxdepth 3 -type f | sort`

Expected: README, one parent note, and 12 child tasknotes appear.

- [x] **Step 2: Verify the orchestration note is the only new steering entry point**

Run: `git status --short steering/llm-wiki 'steering/2026年5月22日 LLM Wiki shared packageを導入して自律実行ルートを固定する.md'`

Expected: untracked package directory plus one untracked orchestration note, with unrelated user changes untouched.

- [x] **Step 3: Verify the shared source and repo copy are now identical**

Run: `diff -ru /home/exedev/dotfiles/shared/llm-wiki-how-to /home/exedev/code-quest-pyxel/steering/llm-wiki`

Expected: no output.
