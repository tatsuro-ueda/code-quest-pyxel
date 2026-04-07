# AGENTS.md — Block Quest Pyxel Guide

## Scope

- This file applies to `/home/exedev/code-quest-pyxel`.
- Treat `/home/exedev/code-quest-pyxel` as the only current project.
- Ignore sibling directories under `/home/exedev/game/*`. They are older variants and not part of the active project.

## Current Runtime Truth

- The runtime entrypoint is `main.py`.
- The current implementation is a Pyxel + Python game, not a single-file HTML game.
- `pyxel.html` and `pyxel.pyxapp` are distribution artifacts for playback/export.
- `index.html` may exist as a static-hosting entrypoint that points to `pyxel.html`, but `pyxel.html` remains the underlying exported artifact.
- If documentation and confirmed code disagree, trust the current code first and then update the docs.

## Primary Documents

Read these first before changing gameplay, text, or project structure:

- `docs/00-pyxel-design.md`
- `docs/10-concept.md`
- `docs/20-requirements.md`
- `docs/30-story-concepts.md`
- `docs/35-story-design.md`
- `docs/50-map-concepts.md`
- `docs/55-map-design.md`
- `docs/60-visual-requirements.md`
- `docs/65-visual-design.md`
- `docs/70-audio-concepts.md`
- `docs/75-audio-design.md`
- `docs/80-sfx-concepts.md`
- `docs/85-sfx-design.md`
- `docs/95-testing.md`
- `docs/97-acceptance.feature`

## Supporting Documents

Use these when working on dialogue or ending text:

- `docs/38-cave-mission-dialogue.md`
- `docs/39-playthrough-text.md`
- `docs/87-ending-credits.md`

## Legacy Review Documents

These files currently contain older HTML-oriented assumptions. Do not treat them as the current source of truth until they are rewritten:

- `docs/90-architecture.md`
- `docs/92-functional-design.md`

When these documents conflict with `main.py` or `docs/00-pyxel-design.md`, follow the Pyxel implementation and update the docs.

## Project Rules

1. Keep project decisions scoped to `/home/exedev/code-quest-pyxel`.
2. Prefer edits that make docs match the current Pyxel implementation.
3. Do not reintroduce old HTML-only assumptions such as `index.html` as the runtime entrypoint unless the project is intentionally rewritten.
4. Keep runtime-focused guidance aligned with `main.py`, Pyxel assets, and the current numbered docs.
5. Treat distribution files separately from source files.

## Change Checklist

- Confirm the change is for the Pyxel project, not an old sibling variant.
- Check whether the docs already describe the current Pyxel behavior.
- If a doc still describes the old HTML version, mark or update it instead of treating it as authoritative.
- Keep story/theme wording consistent with the existing concept and story docs.
