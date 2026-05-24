# Source Summary Review Gate Extension Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `capture-and-ingest-source` so it shows a summary preview to the user and waits for approval before writing the summary draft file.

**Architecture:** Keep the change documentation-only. Update the shared skill so `human feedback -> summary preview -> user review -> finalize` is the required flow, keep fast path only for generating a provisional preview, and record the completed behavior in the extension tasknote.

**Tech Stack:** markdown, tasknote lint, markdownlint-cli2, AGENTS sync check

---

### Task 1: Update The Shared Skill Flow

**Files:**
- Modify: `/home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`

- [ ] **Step 1: Add the preview gate to the workflow**

```md
- 仮の `key_takeaways`、引用候補、`open_questions` を返す
- human feedback を受けたあとに summary preview を返す
- user approval 後にだけ summary draft を作る
```

- [ ] **Step 2: Split the current finalize step into preview and finalize**

```md
### 8. summary preview を返す
### 9. user review を待つ
### 10. 承認後に summary draft file を作る
```

- [ ] **Step 3: Tighten the fast path rule**

```md
- `go ahead` でも preview 提示は省略しない
- fast path は provisional preview 生成まで
- final file 作成は user check 後だけ
```

### Task 2: Close The Extension Tasknote

**Files:**
- Modify: `steering/2026年5月24日 開発基盤：capture-and-ingest-sourceに要約確認ゲートを追加する.md`

- [ ] **Step 1: Mark the tasknote as completed**

```md
status: done
> 状態：⑧ Closing
> 次のゲート：なし
```

- [ ] **Step 2: Record the concrete outputs**

```md
- skill 本体に preview -> review -> finalize を追加した
- fast path を preview 止まりに修正した
- tasknote lint / markdownlint / AGENTS sync check を通した
```

- [ ] **Step 3: Check the close conditions**

Run: `rg -n "summary preview|user review|final file|go ahead" /home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`
Expected: the review gate and fast-path boundary are both present in the skill.

### Task 3: Verify The Final State

**Files:**
- Verify only

- [ ] **Step 1: Lint the shared skill**

Run: `npx -y markdownlint-cli2 '/home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md'`
Expected: `Summary: 0 error(s)`

- [ ] **Step 2: Lint the extension tasknote**

Run: `node /home/exedev/dotfiles/shared/linter/coding-rules/tasknote/run_tasknote_lint.mjs --config ./tasknote-lint.config.json 'steering/2026年5月24日 開発基盤：capture-and-ingest-sourceに要約確認ゲートを追加する.md'`
Expected: `Summary: 0 error(s)`

- [ ] **Step 3: Confirm AGENTS registration is still in sync**

Run: `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py --check`
Expected: `in sync: /home/exedev/dotfiles/codex/.codex/AGENTS.md`
