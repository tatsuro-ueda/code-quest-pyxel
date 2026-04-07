# Publishing Pyxel Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a personal skill that guides Codex through building and locally previewing Pyxel web release artifacts for this project.

**Architecture:** Scaffold a new skill under `~/.agents/skills`, then replace the template with a concise workflow-based `SKILL.md` tailored to this repository's `tools/build_web_release.py` and `tools/serve_pyxel_preview.py` flow. Validate the finished skill with the provided skill validator.

**Tech Stack:** Markdown, Python helper scripts from the system `skill-creator` skill, local filesystem

---

### Task 1: Initialize the Skill Scaffold

**Files:**
- Create: `~/.agents/skills/publishing-pyxel-game/SKILL.md`
- Create: `~/.agents/skills/publishing-pyxel-game/agents/openai.yaml`

- [ ] **Step 1: Confirm the initializer interface**

```bash
python /home/exedev/.codex/skills/.system/skill-creator/scripts/init_skill.py --help
```

Expected: help text shows `skill_name`, `--path`, optional `--resources`, `--examples`, and repeatable `--interface`.

- [ ] **Step 2: Run the scaffold initializer**

```bash
python /home/exedev/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  publishing-pyxel-game \
  --path /home/exedev/.agents/skills \
  --interface display_name="Publishing Pyxel Game" \
  --interface short_description="Build and locally preview a Pyxel web release" \
  --interface default_prompt="Build pyxel.html and pyxel.pyxapp for this Pyxel project, explain the role of .build/web_release, and help me preview the result locally."
```

Expected: the directory `~/.agents/skills/publishing-pyxel-game/` exists with `SKILL.md` and `agents/openai.yaml`.

### Task 2: Replace the Template With Project-Specific Guidance

**Files:**
- Modify: `~/.agents/skills/publishing-pyxel-game/SKILL.md`

- [ ] **Step 1: Draft the final frontmatter and overview**

```markdown
---
name: publishing-pyxel-game
description: Use when working on a Pyxel project and needing to build or preview local web release artifacts such as pyxel.html, pyxel.pyxapp, app2html output, or a .build/web_release staging directory.
---

# Publishing Pyxel Game

## Overview

Build the project's local web-ready Pyxel artifacts first, then verify them through the generated `pyxel.html` or a LAN preview. Treat `.build/web_release` as a temporary working directory unless the repository says otherwise.
```

- [ ] **Step 2: Add the workflow for this repository**

```markdown
## Workflow

1. Inspect the repository for the current release flow instead of assuming a generic web build.
2. Prefer a repository-provided build script over raw Pyxel commands when one exists.
3. In `/home/exedev/code-quest-pyxel`, prefer:

~~~bash
./.venv/bin/python tools/build_web_release.py
~~~

4. Expect the main deliverables to be `pyxel.html` and `pyxel.pyxapp`.
5. Explain that `.build/web_release` is where the intermediate `app/`, `app.pyxapp`, and `app.html` files are assembled before the final copies are written to the project root.
6. If the user wants to test on another device on the same network, use:

~~~bash
python tools/serve_pyxel_preview.py --host 0.0.0.0 --port 8000
~~~
```

- [ ] **Step 3: Add boundaries and response guidance**

```markdown
## Boundaries

- Do not treat GitHub Pages, Netlify, Vercel, itch.io, or other external deployment targets as part of this skill.
- Do not assume `.build/web_release` is the final publish directory.
- Do not invent a frontend bundler workflow when the project already uses Pyxel CLI export.

## What To Explain

- Say which command produced the release.
- Name the final output files.
- When asked by beginners, explain the staging directory in simple language.
- If repository docs and code disagree, trust the current code first and mention the mismatch.
```

### Task 3: Validate the Skill

**Files:**
- Verify: `~/.agents/skills/publishing-pyxel-game/SKILL.md`
- Verify: `~/.agents/skills/publishing-pyxel-game/agents/openai.yaml`

- [ ] **Step 1: Run the validator**

```bash
python /home/exedev/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /home/exedev/.agents/skills/publishing-pyxel-game
```

Expected: validation succeeds with no frontmatter or naming errors.

- [ ] **Step 2: Inspect the final files**

```bash
sed -n '1,220p' /home/exedev/.agents/skills/publishing-pyxel-game/SKILL.md
sed -n '1,220p' /home/exedev/.agents/skills/publishing-pyxel-game/agents/openai.yaml
```

Expected: the skill is concise, Pyxel-specific, and references the current project commands and output files.
