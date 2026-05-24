# Health Check Wiki Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a shared `health-check-wiki` skill that performs read-only linting of the current LLM wiki, records categorized findings in `health-check-log`, and stops before fix or schema update routes.

**Architecture:** Keep the implementation documentation-first. Add one new common `SKILL.md` under the shared Claude skills directory, align the repo-local schema defaults to the same contract, verify discoverability with the sync script, and close the tasknote with dry-run criteria. The skill owns only `read -> classify -> log -> stop`.

**Tech Stack:** markdown, shell utilities, Claude skill registry sync script

---

## Task 1: Add The Shared Skill

**Files:**

- Create: `/home/exedev/dotfiles/claude/.claude/skills/health-check-wiki/SKILL.md`

- [ ] **Step 1: Create the skill frontmatter and purpose**

```md
---
name: health-check-wiki
description: Use when the user wants to inspect the current llm-wiki for contradictions, stale claims, orphan pages, missing concepts, missing crossrefs, or data gaps, and record a read-only health-check log without fixing pages or updating schema.
user_invocable: true
---
```

- [ ] **Step 2: Document the read-only workflow**

```md
## 概要

- current wiki と log を読む
- `contradictions` `stale_claims` `orphan_pages`
  `missing_concepts` `missing_crossrefs` `data_gaps` を分類する
- `fix_now` `next_ingest` `candidate_source` `notes` を残す
- page 修正や schema 更新は行わずに止まる
```

- [ ] **Step 3: Document scope, output shape, and stop conditions**

```md
1. `master-index` `areas` `query` `summaries` `logs` を既定で読む
2. issue が無い項目は `none` と明記する
3. `no issue` の回でも log は残す
4. `fix_now` が見えても別 route へ渡して止まる
```

## Task 2: Align The Repo Schema

**Files:**

- Modify: `docs/llm-wiki-ops-schema.md`

- [ ] **Step 1: Extend Health-Check defaults to match the skill**

```md
- `data_gaps` を core 5 に加えた第 6 分類として扱う
- `health-check-wiki` は compiled wiki を主に読む read-only route である
- issue が無い項目は `none` と明記する
- `no issue` の回でも health-check log を残す
```

- [ ] **Step 2: Keep fix and schema work outside this route**

```md
- `fix_now` は repair route へ渡す
- schema 更新は `update-schema` route へ渡す
```

## Task 3: Sync And Verify Discoverability

**Files:**

- Modify: `/home/exedev/.codex/AGENTS.md`

- [ ] **Step 1: Sync the Claude skills into Codex AGENTS**

Run: `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py`
Expected: the auto-registered skills block is updated or already up to date.

- [ ] **Step 2: Verify sync state**

Run: `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py --check`
Expected: `in sync: /home/exedev/.codex/AGENTS.md`

- [ ] **Step 3: Check markdown-safe diffs**

Run: `git -C /home/exedev/dotfiles diff --check && git -C /home/exedev/code-quest-pyxel diff --check`
Expected: no output

## Task 4: Close The Tasknote

**Files:**

- Modify: `steering/2026年5月24日 開発基盤：LLM Wikiのhealth-check-wikiスキルを作る.md`

- [ ] **Step 1: Mark the dry-run criterion done when the contract is encoded**

```md
- [x] `health-check-log` の既存形式を基準に dry-run 観点を固めた
```

- [ ] **Step 2: Record created files and verification evidence**

```md
- `/home/exedev/dotfiles/claude/.claude/skills/health-check-wiki/SKILL.md` を追加した
- `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py --check` は in sync だった
- `markdownlint-cli2` と tasknote lint を通した
```

- [ ] **Step 3: Close the note when the shared skill and schema alignment exist**

Run: `test -f /home/exedev/dotfiles/claude/.claude/skills/health-check-wiki/SKILL.md && node /home/exedev/dotfiles/shared/linter/coding-rules/tasknote/run_tasknote_lint.mjs --config ./tasknote-lint.config.json 'steering/2026年5月24日 開発基盤：LLM Wikiのhealth-check-wikiスキルを作る.md'`
Expected: the skill file exists and the tasknote lint passes.
