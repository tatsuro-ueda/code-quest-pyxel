---
title: publishing-pyxel-game skill design
date: 2026-04-07
---

# publishing-pyxel-game

## Goal

Create a personal Codex skill that helps publish a Pyxel game to local web-ready artifacts by:

- building `pyxel.html` and `pyxel.pyxapp`
- explaining that `.build/web_release` is a staging/work directory
- offering a local/LAN preview flow for manual verification

This skill does not cover deployment to GitHub Pages or any other external host.

## Location

- Skill directory: `~/.agents/skills/publishing-pyxel-game/`
- Required file: `~/.agents/skills/publishing-pyxel-game/SKILL.md`

## Triggering Conditions

The skill should trigger when the user asks to:

- publish a Pyxel game
- build a Pyxel web release
- generate `pyxel.html` or `pyxel.pyxapp`
- run `app2html`
- preview a Pyxel browser build on the local network

The description should emphasize when to use the skill, not summarize its workflow.

## Project Assumptions

The first version of the skill is optimized for the current project at `/home/exedev/code-quest-pyxel`.

Known project-specific release flow:

1. `tools/build_web_release.py` stages runtime files into `.build/web_release/app`
2. It runs `pyxel package app app/main.py`
3. It runs `pyxel app2html app.pyxapp`
4. It copies the outputs to `pyxel.pyxapp` and `pyxel.html`

Known preview flow:

- `python tools/serve_pyxel_preview.py --host 0.0.0.0 --port 8000`

## User Outcome

After using the skill, Codex should reliably do the following:

1. Confirm the repository has a Pyxel-oriented release flow instead of assuming a generic web build.
2. Identify the build script or Pyxel CLI commands actually used by the project.
3. Build the local release artifacts.
4. Explain the role of `.build/web_release` in simple language when relevant.
5. Offer or run local/LAN preview verification when useful.
6. Avoid claiming that external deployment is part of the skill.

## Workflow

The skill should instruct Codex to follow this order:

1. Inspect the repo for the current release flow.
2. Prefer a project-provided build script when one exists.
3. For this project, prefer:
   `./.venv/bin/python tools/build_web_release.py`
4. Treat `pyxel.html` and `pyxel.pyxapp` as the main output artifacts.
5. Treat `.build/web_release` as an intermediate working directory.
6. If the user wants to test on another device, use the preview server and point them to `pyxel.html`.

## Non-Goals

The skill must explicitly stay out of scope for:

- GitHub Pages deployment
- Netlify, Vercel, itch.io, or any other hosting target
- release automation pipelines
- repository-specific git publishing steps unless the user separately asks for them

## Validation

The first implementation should be lightweight:

- create only `SKILL.md`
- keep instructions concise and easy to scan
- include the concrete filenames and commands used by this project

Success means the skill is discoverable and gives correct guidance for the current Pyxel project without drifting into external deployment advice.
