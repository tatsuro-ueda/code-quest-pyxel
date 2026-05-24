# LLM Wiki Drift Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the two wiki content drifts identified by the 2026-05-24 health check and leave the current wiki wording aligned with the repo contract.

**Architecture:** Keep the fix strictly local to the two flagged pages. Preserve the health-check history, then rerun targeted verification so the repaired wiki can be judged from current page content rather than assumption.

**Tech Stack:** Markdown, ripgrep, Python helper CLI

---

### Task 1: Align the lint wording in the Karpathy summary

**Files:**
- Modify: `llm-wiki/wiki/summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md`

- [ ] **Step 1: Verify the current drift is present**

Run: `rg -n "core 5 と data gap" llm-wiki/wiki/summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md`
Expected: one match on the `lint:` line

- [ ] **Step 2: Replace the stale wording with the repo-local contract**

Edit the `lint:` bullet so it says:

```md
- lint: contradictions、stale claims、orphan pages、missing concepts、missing crossrefs、data_gaps を見て、次の source や質問候補を作る
```

- [ ] **Step 3: Verify the new wording is present**

Run: `rg -n "contradictions、stale claims、orphan pages、missing concepts、missing crossrefs、data_gaps" llm-wiki/wiki/summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md`
Expected: one match on the `lint:` line

### Task 2: Rename the umbrella tasknote summary heading

**Files:**
- Modify: `llm-wiki/wiki/summaries/tasknotes/steering/done/20260507-src-header-functions-for-all-files-summary.md`

- [ ] **Step 1: Verify the duplicated heading is present**

Run: `rg -n "^# 2026年5月7日 src/ ファイル先頭に関数一覧コメント（battle/view.py） Summary Draft$" llm-wiki/wiki/summaries/tasknotes/steering/done/20260507-src-header-functions-for-all-files-summary.md`
Expected: one match on the H1 line

- [ ] **Step 2: Replace the H1 with one that matches the umbrella note body**

Edit the H1 so it says:

```md
# 2026年5月7日 src/ ファイル先頭に関数一覧コメントを全体へ広げる Summary Draft
```

- [ ] **Step 3: Verify the new heading is present**

Run: `rg -n "^# 2026年5月7日 src/ ファイル先頭に関数一覧コメントを全体へ広げる Summary Draft$" llm-wiki/wiki/summaries/tasknotes/steering/done/20260507-src-header-functions-for-all-files-summary.md`
Expected: one match on the H1 line

### Task 3: Re-check the wiki state and log the outcome

**Files:**
- Modify: `llm-wiki/wiki/logs/health-check-log.md`

- [ ] **Step 1: Re-run the structural helper**

Run: `python tools/llm_wiki_health_check_helper.py --repo-root . > /tmp/llm_wiki_health_check.json`
Expected: exit code 0 and fresh helper output written to `/tmp/llm_wiki_health_check.json`

- [ ] **Step 2: Confirm no new structural issues were introduced**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
obj = json.loads(Path('/tmp/llm_wiki_health_check.json').read_text())
print('orphan_signal_count', len(obj['orphan_signals']))
print('missing_target_signal_count', len(obj['missing_target_signals']))
PY
```

Expected:

```text
orphan_signal_count 0
missing_target_signal_count 0
```

- [ ] **Step 3: Append a repair entry to the health-check log**

Append an entry recording that:
- the Karpathy summary `lint:` wording was aligned to `core 6 + data_gaps`
- the umbrella tasknote summary H1 was renamed to match its actual scope

- [ ] **Step 4: Verify the new log entry is present**

Run: `tail -n 30 llm-wiki/wiki/logs/health-check-log.md`
Expected: the appended `fix` entry appears at the end of the file
