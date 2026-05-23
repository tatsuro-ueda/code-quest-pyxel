# LLM Wiki First Cycle Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the repo-local LLM wiki through the first complete `setup -> ingest -> query -> health-check -> schema` cycle using the Karpathy gist as the first source.

**Architecture:** Keep the implementation manual and file-oriented. The raw gist becomes the immutable source of truth, the wiki layer gets one summary, a small set of related area pages, one saved answer, and chronological logs, and the schema layer captures only the defaults proven by this first cycle.

**Tech Stack:** markdown files, git, Python test suite, tasknote lint, shell utilities

---

### Task 1: Create The Minimal Wiki Surfaces

**Files:**
- Create: `llm-wiki/wiki/indexes/master-index.md`
- Create: `llm-wiki/wiki/logs/source-inbox.md`
- Create: `llm-wiki/wiki/logs/ingest-log.md`
- Create: `llm-wiki/wiki/logs/health-check-log.md`
- Modify: `steering/2026年5月23日 開発基盤：LLM Wikiの土台フォルダと基準ページを作る.md`

- [ ] **Step 1: Confirm the current wiki lacks the first-cycle files**

Run: `find llm-wiki/wiki -maxdepth 3 -type f | sort`

Expected: there is no `master-index.md`, no `logs/`, and no first-cycle query page yet.

- [ ] **Step 2: Create the starter pages with stable headings**

```md
# Master Index

## Sources

## Areas

## Queries

## Candidates

## Logs
```

```md
# Source Inbox

## [YYYY-MM-DD] inbox | source title
```

```md
# Ingest Log

## [YYYY-MM-DD] ingest | source title
```

```md
# Health Check Log

## [YYYY-MM-DD] lint | wiki scope
```

- [ ] **Step 3: Verify the starter pages exist**

Run: `find llm-wiki/wiki -maxdepth 3 -type f | sort`

Expected: output includes the new index and three log files.

### Task 2: Ingest The Karpathy Gist

**Files:**
- Create: `llm-wiki/raw/knowledge/2026-04-04-karpathy-llm-wiki.md`
- Create: `llm-wiki/wiki/summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md`
- Create: `llm-wiki/wiki/areas/persistent-wiki-vs-rag.md`
- Create: `llm-wiki/wiki/areas/ingest-query-lint-loop.md`
- Create: `llm-wiki/wiki/areas/schema-driven-wiki-maintainer.md`
- Modify: `llm-wiki/wiki/indexes/master-index.md`
- Modify: `llm-wiki/wiki/logs/source-inbox.md`
- Modify: `llm-wiki/wiki/logs/ingest-log.md`
- Modify: `steering/2026年5月23日 開発基盤：カルパシー資料1本で手動取り込みを試す.md`

- [ ] **Step 1: Fetch and save the raw gist**

Run: `curl -L https://gist.githubusercontent.com/karpathy/442a6bf555914893e9891c11519de94f/raw/llm-wiki.md`

Expected: the markdown source for `LLM Wiki` is returned.

- [ ] **Step 2: Wrap the raw gist in repo metadata and save it**

```md
---
title: LLM Wiki
source_url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
author: karpathy
source_type: gist
date_published: 2026-04-04
date_added: 2026-05-23
status: active
why_saved: Karpathy 型 LLM wiki の最初の source として使う
first_impression: persistent wiki と運用ループの核が 1 本にまとまっている
---
```

- [ ] **Step 3: Create the summary and three related area pages**

```md
## TL;DR
...
## 主要トピック
...
## キーワード
...
```

```md
## 核心
...
## 根拠
...
## 関連ページ
...
```

- [ ] **Step 4: Update the index and ingest logs**

Run: `find llm-wiki -maxdepth 4 -type f | sort`

Expected: the raw source, summary, three area pages, index, and logs are all present.

### Task 3: Save One Query Answer And One Candidate Source

**Files:**
- Create: `llm-wiki/wiki/query/2026-05-23-why-persistent-wiki-beats-rag.md`
- Create: `llm-wiki/wiki/candidates/2026-05-23-qmd-and-obsidian-tooling-candidate.md`
- Modify: `llm-wiki/wiki/indexes/master-index.md`
- Modify: `steering/2026年5月23日 開発基盤：Wikiへの質問と回答保存を試す.md`

- [ ] **Step 1: Pick one representative question**

Question: `Why does Karpathy argue that a persistent wiki compounds better than plain RAG?`

- [ ] **Step 2: Write the saved answer in markdown with evidence**

```md
# Why Persistent Wiki Beats Plain RAG

## Question

## Answer

## Evidence

## Confidence
```

- [ ] **Step 3: Split any external gap into a candidate source**

```md
# Candidate Source: qmd And Obsidian Tooling

## Missing Fact

## Why Needed

## Search Hint

## Priority
```

- [ ] **Step 4: Verify the query and candidate files are indexed**

Run: `rg -n "why-persistent-wiki-beats-rag|qmd-and-obsidian-tooling-candidate" llm-wiki/wiki/indexes/master-index.md`

Expected: both pages are listed in the master index.

### Task 4: Run The First Health Check

**Files:**
- Modify: `llm-wiki/wiki/logs/health-check-log.md`
- Modify: `steering/2026年5月23日 開発基盤：Wikiの健全性チェックを試す.md`

- [ ] **Step 1: Inspect the first-cycle wiki pages**

Run: `find llm-wiki/wiki -maxdepth 3 -type f | sort`

Expected: summaries, areas, query, candidates, index, and logs are all present.

- [ ] **Step 2: Record the core-5 health-check result**

```md
## [YYYY-MM-DD] lint | first-cycle wiki

- contradictions:
- stale_claims:
- orphan_pages:
- missing_concepts:
- missing_crossrefs:
- fix_now:
- next_ingest:
- candidate_source:
```

- [ ] **Step 3: Verify the log contains all three routing buckets**

Run: `rg -n "fix_now|next_ingest|candidate_source" llm-wiki/wiki/logs/health-check-log.md`

Expected: all three labels are present.

### Task 5: Capture Defaults In The Schema Layer

**Files:**
- Create: `docs/llm-wiki-ops-schema.md`
- Modify: `steering/2026年5月23日 開発基盤：LLM Wiki運用をスキーマへ文書化する.md`

- [ ] **Step 1: Write the schema doc with the fixed headings**

```md
# LLM Wiki Ops Schema

## Purpose
## Default Flow
## File Layout
## Ingest Defaults
## Query Defaults
## Health-Check Defaults
## Batch Policy
## Exceptions
## Update Rule
```

- [ ] **Step 2: Populate it only with defaults proven by the first cycle**

Run: `sed -n '1,240p' docs/llm-wiki-ops-schema.md`

Expected: the schema doc contains defaults for setup, ingest, query, health-check, batch gating, and update timing.

### Task 6: Verify And Record Completion

**Files:**
- Modify: `steering/2026年5月23日 開発基盤：Karpathy型LLM Wiki運用の親ノート.md`
- Modify: `steering/2026年5月23日 開発基盤：LLM Wikiの土台フォルダと基準ページを作る.md`
- Modify: `steering/2026年5月23日 開発基盤：カルパシー資料1本で手動取り込みを試す.md`
- Modify: `steering/2026年5月23日 開発基盤：Wikiへの質問と回答保存を試す.md`
- Modify: `steering/2026年5月23日 開発基盤：Wikiの健全性チェックを試す.md`
- Modify: `steering/2026年5月23日 開発基盤：LLM Wiki運用をスキーマへ文書化する.md`

- [ ] **Step 1: Run tasknote lint for the touched tasknotes**

Run:

```bash
node /home/exedev/dotfiles/shared/linter/coding-rules/tasknote/run_tasknote_lint.mjs \
  --config ./tasknote-lint.config.json \
  'steering/2026年5月23日 開発基盤：Karpathy型LLM Wiki運用の親ノート.md' \
  'steering/2026年5月23日 開発基盤：LLM Wikiの土台フォルダと基準ページを作る.md' \
  'steering/2026年5月23日 開発基盤：カルパシー資料1本で手動取り込みを試す.md' \
  'steering/2026年5月23日 開発基盤：Wikiへの質問と回答保存を試す.md' \
  'steering/2026年5月23日 開発基盤：Wikiの健全性チェックを試す.md' \
  'steering/2026年5月23日 開発基盤：LLM Wiki運用をスキーマへ文書化する.md'
```

Expected: `Summary: 0 error(s)`

- [ ] **Step 2: Run the full repo test suite**

Run: `python -m pytest test/ -q`

Expected: PASS

- [ ] **Step 3: Record the actual first-cycle outputs in the tasknotes**

```md
## 6) Result

- 作成したファイル
- 追加した log entry
- query と health-check の要点
```

```md
## 7) Discussion

### 2026-05-23T..Z（実行）

**Observe**：
**Think**：
**Act**：
```
