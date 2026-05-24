# Docs Multi Ingest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingest `docs/customer-journeys.md`, `docs/framework-rule.md`, and `docs/old-customer-jobs.md` into the repo-local llm wiki with source summaries, related area-page updates, and index/log updates.

**Architecture:** Treat each docs file as a knowledge source in the raw layer. Reuse existing area pages where the themes overlap, add a small set of new area pages where the wiki has no current concept page, and append every ingest to the content index and chronological logs so later query and health-check passes can trace the evolution.

**Tech Stack:** markdown files, shell utilities, pytest

---

### Task 1: Prepare Sources And Summaries

**Files:**
- Create: `llm-wiki/raw/knowledge/docs/old-customer-jobs.md`
- Create: `llm-wiki/wiki/summaries/knowledge/customer-journeys-summary.md`
- Create: `llm-wiki/wiki/summaries/knowledge/framework-rule-summary.md`
- Create: `llm-wiki/wiki/summaries/knowledge/old-customer-jobs-summary.md`

- [ ] **Step 1: Confirm customer-journeys and framework-rule raw copies already exist**

Run: `find llm-wiki/raw/knowledge/docs -maxdepth 1 -type f | sort`
Expected: `customer-journeys.md` and `framework-rule.md` are already present.

- [ ] **Step 2: Add a raw copy for old-customer-jobs**

Mirror the contents of `docs/old-customer-jobs.md` into `llm-wiki/raw/knowledge/docs/old-customer-jobs.md`.

- [ ] **Step 3: Write the three source summaries**

Each summary should use this shape:

```md
---
source: raw/knowledge/docs/<name>.md
source_type: doc
status: active
origin:
  - docs/<name>.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: medium
---

# <Title> Summary

## TL;DR

## 主要トピック

## キーワード

## 注意点
```

### Task 2: Propagate To Related Area Pages

**Files:**
- Create: `llm-wiki/wiki/areas/fast-feedback-development-loop.md`
- Create: `llm-wiki/wiki/areas/approval-loop-and-child-agency.md`
- Create: `llm-wiki/wiki/areas/guardrails-protect-the-loop.md`
- Create: `llm-wiki/wiki/areas/single-source-of-truth-and-golden-path.md`
- Create: `llm-wiki/wiki/areas/view-presenter-model-boundaries.md`
- Create: `llm-wiki/wiki/areas/no-silent-failure-and-migration-safety.md`
- Modify: `llm-wiki/wiki/areas/continuous-experience-loop.md`
- Modify: `llm-wiki/wiki/areas/parent-support-without-control.md`
- Modify: `llm-wiki/wiki/areas/low-friction-sharing.md`

- [ ] **Step 1: Add the three journeys-derived area pages**

Add pages for the fast feedback loop, the approval loop, and guardrails as loop protection.

- [ ] **Step 2: Add the three framework-derived area pages**

Add pages for SSoT + golden path, MVP boundaries, and no silent failure + migration safety.

- [ ] **Step 3: Update the three existing jobs-derived area pages**

Use `old-customer-jobs` to strengthen:
- `continuous-experience-loop.md`
- `parent-support-without-control.md`
- `low-friction-sharing.md`

### Task 3: Update Index And Logs

**Files:**
- Modify: `llm-wiki/wiki/indexes/master-index.md`
- Modify: `llm-wiki/wiki/logs/source-inbox.md`
- Modify: `llm-wiki/wiki/logs/ingest-log.md`

- [ ] **Step 1: Add source and area entries to the master index**

Add all three summaries, all three raw-source links, and the six new area pages.

- [ ] **Step 2: Append three source-inbox entries**

Append processed inbox entries for:
- `customer-journeys`
- `framework-rule`
- `old-customer-jobs`

- [ ] **Step 3: Append three ingest-log entries**

Record created/updated pages, related page counts, and any interpretation risks for all three sources.

### Task 4: Verify

**Files:**
- Verify: all newly created summaries and area pages

- [ ] **Step 1: Check file creation and index references**

Run: `find llm-wiki/wiki -maxdepth 3 -type f | sort && rg -n "customer-journeys|framework-rule|old-customer-jobs|fast-feedback-development-loop|approval-loop-and-child-agency|guardrails-protect-the-loop|single-source-of-truth-and-golden-path|view-presenter-model-boundaries|no-silent-failure-and-migration-safety" llm-wiki/wiki/indexes/master-index.md`
Expected: all new summary/area pages exist and are referenced in the master index.

- [ ] **Step 2: Run the repo test suite**

Run: `python -m pytest test/ -q`
Expected: `743 passed, 2 skipped, 14233 subtests passed`
