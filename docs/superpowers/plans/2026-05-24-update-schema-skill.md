# Update Schema Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a shared `update-schema` skill that reads `health-check-log` plus compiled wiki, promotes only stable recurring rules into the schema, and stops with `no schema change` when the evidence is insufficient.

**Architecture:** Keep the implementation documentation-first. Add one new common `SKILL.md` under the shared Claude skills directory, align the repo-local schema text to the same contract, verify discoverability with the sync script, and close the tasknote with a concrete dry-run criterion. The skill owns only `read -> compare recurring patterns -> map to current headings -> update or no-op`.

**Tech Stack:** markdown, shell utilities, Claude skill registry sync script

---

## Task 1: Add The Shared Skill

**Files:**

- Create: `/home/exedev/dotfiles/claude/.claude/skills/update-schema/SKILL.md`

- [ ] **Step 1: Create the skill frontmatter and purpose**

```md
---
name: update-schema
description: Use when the user wants to promote stable llm-wiki operating rules from `health-check-log` into the current schema, while keeping one-off incidents out of the defaults and stopping with `no schema change` when evidence is weak.
user_invocable: true
---
```

- [ ] **Step 2: Document the stable-rule workflow**

```md
## 概要

- `health-check-log` を主入力にする
- compiled wiki と current schema を補助入力にする
- recurring pattern だけを rule 候補にする
- incident、局所修正、暫定メモは昇格させない
- 候補が弱ければ `no schema change` で止まる
```

- [ ] **Step 3: Document current-heading mapping and stop conditions**

```md
1. `defaults` -> `Ingest Defaults` と `Health-Check Defaults`
2. `exceptions` -> `Exceptions`
3. `timing` -> `Default Flow` と `Update Rule`
4. `query_policy` -> `Query Defaults`
5. `batch_policy` -> `Batch Policy`
6. evidence が 1 回限りなら schema を更新しない
```

## Task 2: Align The Repo Schema

**Files:**

- Modify: `docs/llm-wiki-ops-schema.md`

- [ ] **Step 1: Extend Update Rule to match the skill**

```md
- `update-schema` は `health-check-log` を主入力にする
- recurring pattern だけを昇格候補にする
- tasknote 原文や局所事故は schema に直入れしない
- evidence が弱い回は `no schema change` で止める
```

- [ ] **Step 2: Keep heading reorg out of scope**

```md
- 現行見出しは維持し、内部対応で 5 バケットを扱う
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

- Modify: `steering/2026年5月24日 開発基盤：LLM Wikiのupdate-schemaスキルを作る.md`

- [ ] **Step 1: Mark the no-op criterion done when the contract is encoded**

```md
- [x] `health-check-log` を基準に `no schema change` の dry-run 観点を固めた
```

- [ ] **Step 2: Record created files and verification evidence**

```md
- `/home/exedev/dotfiles/claude/.claude/skills/update-schema/SKILL.md` を追加した
- `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py --check` は in sync だった
- `markdownlint-cli2` と tasknote lint を通した
```

- [ ] **Step 3: Close the note when the shared skill and schema alignment exist**

Run: `test -f /home/exedev/dotfiles/claude/.claude/skills/update-schema/SKILL.md && node /home/exedev/dotfiles/shared/linter/coding-rules/tasknote/run_tasknote_lint.mjs --config ./tasknote-lint.config.json 'steering/2026年5月24日 開発基盤：LLM Wikiのupdate-schemaスキルを作る.md'`
Expected: the skill file exists and the tasknote lint passes.
