# Remove Live YAML Docs Toolchain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the live-repo `architecture_rules` and `stakeholder_voices` YAML-driven docs toolchain while keeping the markdown docs and gameplay code intact.

**Architecture:** Treat the YAML files plus their checker/fix/repair/report scripts and dedicated tests as one removable development layer. Keep the live documentation centered on `AGENTS.md`, `docs/architecture.md`, `docs/repository-structure.md`, `docs/framework-rule.md`, `docs/customer-jobs.md`, and `docs/customer-journeys.md`, and leave `llm-wiki/` plus old plan/history files untouched.

**Tech Stack:** Python, pytest, markdown docs, git

---

### Task 1: Lock the New Live-Repo Contract

**Files:**
- Modify: `test/test_cjg_framework_rule_guards.py`
- Modify: `test/test_architecture_layout.py`
- Create: `test/test_live_docs_surface.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run the targeted tests and confirm they fail for the old YAML/toolchain assumptions**
- [ ] **Step 3: Update the live-doc expectations to the markdown-only surface**
- [ ] **Step 4: Re-run the targeted tests and keep them red until code/docs cleanup lands**

### Task 2: Remove the Obsolete Toolchain

**Files:**
- Delete: `tools/check_architecture_rules.py`
- Delete: `tools/fix_architecture_rules.py`
- Delete: `tools/repair_architecture_rules.py`
- Delete: `tools/report_source_trace_coverage.py`
- Delete: `tools/check_stakeholder_voices.py`
- Delete: `tools/fix_stakeholder_voices.py`
- Delete: `tools/repair_stakeholder_voices.py`
- Delete: `tools/architecture_rules/__init__.py`
- Delete: `tools/architecture_rules/check_architecture_rules.py`
- Delete: `tools/architecture_rules/fix_architecture_rules.py`
- Delete: `tools/architecture_rules/repair_architecture_rules.py`
- Delete: `tools/stakeholder_voices/__init__.py`
- Delete: `tools/stakeholder_voices/check_stakeholder_voices.py`
- Delete: `tools/stakeholder_voices/fix_stakeholder_voices.py`
- Delete: `tools/stakeholder_voices/repair_stakeholder_voices.py`
- Delete: `tools/stakeholder_voices/source_trace_coverage.py`
- Delete: `docs/architecture_rules.yml`
- Delete: `docs/stakeholder_voices.yml`
- Delete: `test/test_architecture_rules_checker.py`
- Delete: `test/test_fix_architecture_rules.py`
- Delete: `test/test_repair_architecture_rules.py`
- Delete: `test/test_stakeholder_voices_checker.py`
- Delete: `test/test_fix_stakeholder_voices.py`
- Delete: `test/test_repair_stakeholder_voices.py`
- Delete: `test/test_source_trace_coverage_report.py`

- [ ] **Step 1: Remove the obsolete CLI shims, implementation packages, YAML docs, and dedicated tests**
- [ ] **Step 2: Keep unrelated gameplay/runtime files unchanged**

### Task 3: Repair the Live Docs Surface

**Files:**
- Modify: `docs/repository-structure.md`
- Modify: `README.md`

- [ ] **Step 1: Remove the tool listings and wording that still advertise the deleted YAML toolchain**
- [ ] **Step 2: Point readers back to the surviving markdown SSoT docs**

### Task 4: Verify and Commit

**Files:**
- Verify only

- [ ] **Step 1: Run targeted pytest for the updated live-doc tests**
- [ ] **Step 2: Run `python3 tools/verify_module_docstrings.py src/ --skip-missing-docstring`**
- [ ] **Step 3: Run `python -m pytest test/ -q`**
- [ ] **Step 4: Commit with a single cleanup-focused message**
