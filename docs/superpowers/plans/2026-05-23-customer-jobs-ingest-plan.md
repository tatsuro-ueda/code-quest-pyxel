# Customer Jobs Ingest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingest `docs/customer-jobs.md` into the repo-local llm wiki by adding a summary, three related area pages, and the matching index/log updates.

**Architecture:** Reuse the already-synced raw source at `llm-wiki/raw/knowledge/docs/customer-jobs.md` as the immutable source. Add one summary page under `wiki/summaries/knowledge/`, add three related topic pages under `wiki/areas/`, and append the source to the content index and chronological logs without changing the schema or health-check layers.

**Tech Stack:** markdown files, shell utilities, pytest

---

### Task 1: Add The Customer Jobs Summary Layer

**Files:**
- Create: `llm-wiki/wiki/summaries/knowledge/customer-jobs-summary.md`

- [ ] **Step 1: Confirm the raw source is already present**

Run: `cmp -s docs/customer-jobs.md llm-wiki/raw/knowledge/docs/customer-jobs.md; echo $?`
Expected: `0`

- [ ] **Step 2: Create the summary page**

Write a summary with these sections:

```md
---
source: raw/knowledge/docs/customer-jobs.md
source_type: doc
status: active
origin:
  - docs/customer-jobs.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: medium
---

# Customer Jobs Summary

## TL;DR

## 主要ジョブ

## 競合理解

## 深い洞察

## キーワード

## 注意点
```

### Task 2: Add Three Related Area Pages

**Files:**
- Create: `llm-wiki/wiki/areas/continuous-experience-loop.md`
- Create: `llm-wiki/wiki/areas/parent-support-without-control.md`
- Create: `llm-wiki/wiki/areas/low-friction-sharing.md`

- [ ] **Step 1: Create the continuous experience page**

Include:

```md
# Continuous Experience Loop

## 核心

## 子ども側の連続性

## 競合が途切れさせる点

## 関連ページ
```

- [ ] **Step 2: Create the parent support page**

Include:

```md
# Parent Support Without Control

## 核心

## 親ジョブ

## 支えるが奪わない条件

## 関連ページ
```

- [ ] **Step 3: Create the low-friction sharing page**

Include:

```md
# Low Friction Sharing

## 核心

## 子どもと友達のジョブ

## 競合が止まる点

## 関連ページ
```

### Task 3: Update The Index And Logs

**Files:**
- Modify: `llm-wiki/wiki/indexes/master-index.md`
- Modify: `llm-wiki/wiki/logs/source-inbox.md`
- Modify: `llm-wiki/wiki/logs/ingest-log.md`

- [ ] **Step 1: Append the source to the master index**

Add one source entry and three area entries.

- [ ] **Step 2: Append a processed source-inbox entry**

Use this shape:

```md
## [2026-05-23] inbox | Customer Jobs

- source_id: `customer-jobs`
- source_path: `llm-wiki/raw/knowledge/docs/customer-jobs.md`
- status: processed
- owner: codex
- note: docs 層の顧客ジョブ文書を product knowledge source として ingest
```

- [ ] **Step 3: Append an ingest log entry**

Use this shape:

```md
## [2026-05-23] ingest | Customer Jobs

- source_id: `customer-jobs`
- source_path: `llm-wiki/raw/knowledge/docs/customer-jobs.md`
- created_pages:
- updated_pages:
- related_page_count: 3
- risks:
- notes:
```

### Task 4: Verify The Ingest

**Files:**
- Verify: `llm-wiki/wiki/summaries/knowledge/customer-jobs-summary.md`
- Verify: `llm-wiki/wiki/areas/continuous-experience-loop.md`
- Verify: `llm-wiki/wiki/areas/parent-support-without-control.md`
- Verify: `llm-wiki/wiki/areas/low-friction-sharing.md`

- [ ] **Step 1: Check the created files and index references**

Run: `find llm-wiki/wiki -maxdepth 3 -type f | sort && rg -n "customer-jobs|continuous-experience-loop|parent-support-without-control|low-friction-sharing" llm-wiki/wiki/indexes/master-index.md`
Expected: the new summary and area pages exist, and the index contains all four references.

- [ ] **Step 2: Run the repo test suite**

Run: `python -m pytest test/ -q`
Expected: `743 passed, 2 skipped, 14233 subtests passed`
