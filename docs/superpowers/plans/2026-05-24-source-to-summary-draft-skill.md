# Source To Summary Draft Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a shared Claude skill that turns a URL or source note into a raw source file, an inbox entry, and an interactive summary draft for a Karpathy-style LLM wiki.

**Architecture:** Keep the implementation documentation-only. Add one new common `SKILL.md` under the shared Claude skills directory, make it discoverable to Codex via the sync script, and verify the result with sync and markdown-safe checks. The skill stops at `summary draft` and explicitly leaves related-page/index/log expansion to later routes.

**Tech Stack:** markdown, shell utilities, Claude skill registry sync script

---

### Task 1: Add The Shared Skill

**Files:**
- Create: `/home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`

- [ ] **Step 1: Create the skill frontmatter and purpose**

```md
---
name: capture-and-ingest-source
description: Use when the user wants to turn a URL, video link, or quick note into a raw source plus an interactive summary draft for a Karpathy-style LLM wiki. Triggers on "この資料を取り込んで", "raw に置いて ingest して", "保存候補にして" requests.
user_invocable: true
---
```

- [ ] **Step 2: Document the workflow and boundaries**

```md
## 実行手順
1. local schema と path を読む
2. source type と `source_id` を決める
3. raw file を作る
4. `source-inbox` を更新する
5. 仮の `key_takeaways` / 引用候補 / `open_questions` を返す
6. human feedback を反映して summary draft を作る
7. related pages / index / ingest log 更新の前で止まる
```
```

- [ ] **Step 3: Document the fallback behavior**

```md
- 本文を十分に取れない source は `raw_notes` で保存する
- user が `go ahead` と言ったら `why_saved` と `first_impression` を根拠に provisional draft を作る
- 引用や transcript を捏造しない
```

### Task 2: Sync And Verify Registration

**Files:**
- Modify: `/home/exedev/.codex/AGENTS.md`

- [ ] **Step 1: Sync the Claude skills into Codex AGENTS**

Run: `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py`
Expected: the AGENTS auto-registered block is updated or already up to date.

- [ ] **Step 2: Verify the registration is in sync**

Run: `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py --check`
Expected: `in sync: /home/exedev/.codex/AGENTS.md`

- [ ] **Step 3: Check for whitespace and markdown-safe diff issues**

Run: `git -C /home/exedev/dotfiles diff --check`
Expected: no output

### Task 3: Update The Tasknote And Record Evidence

**Files:**
- Modify: `steering/2026年5月24日 開発基盤：URLからraw保存と対話型ingest下書きまでを一気に行うスキルを作る.md`

- [ ] **Step 1: Mark the tasknote with the chosen common-skill direction**

```md
- [x] skill の保存先を共通 skill に決めた
```

- [ ] **Step 2: Record the concrete outputs and verification commands**

```md
- `claude/.claude/skills/capture-and-ingest-source/SKILL.md` を追加した
- `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py --check` は in sync だった
- `git -C /home/exedev/dotfiles diff --check` は通過した
```

- [ ] **Step 3: Close the note if all outputs exist**

Run: `test -f /home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md && python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py --check`
Expected: the skill file exists and AGENTS sync check passes.
