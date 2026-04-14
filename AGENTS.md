# AGENTS.md — Block Quest Pyxel Guide

## Scope

- This file applies to `/home/exedev/code-quest-pyxel`.
- Treat this as the only current project.
- Do not infer runtime or deploy settings from other directories, services, or repos unless they explicitly point to `code-quest-pyxel`.

## Current Runtime Truth

- The runtime entrypoint is `main.py`.
- The current implementation is a Pyxel + Python game.
- `pyxel.html` and `pyxel.pyxapp` are distribution artifacts.
- `index.html` is a selector page (2-version comparison for kids).
- `play.html` is an iframe wrapper that loads `pyxel.html`.
- If documentation and code disagree, trust the current code first.

## Primary Documents

- `docs/gherkins/` — customer journeys, gherkins, guardrails
- `docs/steering/` — active task notes
- `docs/steering/done/` — completed task notes

## Required Reading Before Certain Changes

Before implementing changes in any of these areas:
- build / release flow
- `index.html` / selector page
- `play.html` / wrapper
- preview / promote flow
- top-page change descriptions (`top_changes.json`, `preview_meta.json`)
- runtime / deploy / logs / public URL

you MUST read these documents first:
- `docs/gherkins/customer-journeys.md`
- `docs/gherkins/gherkin-platform.md`
- the matching active task note in `docs/steering/` if one exists
- the most relevant completed note in `docs/steering/done/` for the same area

At minimum, also inspect the current implementation and tests before editing:
- `tools/build_web_release.py`
- `test/test_build_web_release.py`

If docs and code disagree, identify the mismatch explicitly in the task note before implementation.

## Human Expectation Check

- `done` means what a human would naturally expect from the task title, not just "the code exists" or "tests pass".
- If a task says access logs are visible, the public runtime must actually record public traffic.
- If a task says web delivery works, verify the real served URL and the real process serving it.
- When the user points out a mismatch, treat it as a signal that the human expectation may be right. Check reality before defending the existing note.

For runtime / deploy / logs / share URL / build pipeline tasks, do not close the task note until all of these are true:
- the actual public path or VM path is identified
- the actual serving process is identified
- the real endpoint or file update is verified on that path
- the real runtime artifact (`.runtime/*.sqlite3`, served HTML, live endpoint, etc.) is checked directly

Every new steering note in these areas MUST include:
- what a human will believe is true when this note is marked `done`
- what real-world path/process/file proves it
- what exact live verification was run before closing it

Use `docs/steering/_template.md` when creating new task notes.

## SSoT (Single Source of Truth) Data Flow

Game data flows one-way. **Do not edit generated files directly.**

```
assets/*.yaml (enemies, items, weapons, armors, spells, shops)
  -> tools/gen_data.py
  -> src/generated/*.py (DO NOT EDIT)
  -> src/game_data.py (loader)
  -> main.py
```

## Guardrails — MUST FOLLOW

### Files you MUST NOT edit directly

| Path | Reason | What to do instead |
|---|---|---|
| `src/generated/*.py` | Auto-generated from YAML, **read-only (chmod 444)**. Direct write → Permission denied | Edit `assets/*.yaml`, then run `python tools/gen_data.py` |
| `*.pyxres` | Binary resource (art/sound) | Use Pyxel Code Maker |

### Files you MUST NOT import directly

| Path | Reason | What to do instead |
|---|---|---|
| `from src.generated.*` | Use loader | `from src.game_data import ENEMIES` etc. |

### After every change, run tests

```bash
python tools/gen_data.py    # Regenerate from YAML (if you edited YAML)
python -m pytest test/ -q   # 130 tests — MUST ALL PASS before committing
```

**If any test fails, fix the issue before committing.** Do not skip tests.

**Note:** A git pre-commit hook also runs pytest automatically on every `git commit`. If tests fail, the commit is blocked.

### Automated enforcement (no action needed)

These protections run automatically — you do not need to invoke them:

| Protection | When it runs | What happens |
|---|---|---|
| `src/generated/*.py` is read-only (chmod 444) | On every write attempt | Permission denied if you try to edit directly |
| git pre-commit hook | On every `git commit` | pytest runs; commit blocked if tests fail |

### Additional validation tools

```bash
python tools/test_headless.py      # G8: Headless startup test (1-frame draw)
python tools/test_save_compat.py   # G10: Save data compatibility test
python tools/test_web_compat.py    # G11: Web version test (Playwright)
```

## Project Rules

1. Keep project decisions scoped to this repository.
2. Do not edit `src/generated/` — edit `assets/*.yaml` instead.
3. Do not edit `*.pyxres` — use Pyxel Code Maker.
4. Run `pytest` after every change. All 130 tests must pass.
5. Keep story/theme wording consistent with existing dialogue (hiragana for kids).

## Change Checklist

- [ ] Edited the right source file (not a generated file)
- [ ] Ran `python tools/gen_data.py` (if YAML was changed)
- [ ] Ran `python -m pytest test/ -q` and all tests pass
- [ ] Did not break the selector page (`index.html` → `play.html` → `pyxel.html`)
- [ ] For runtime/deploy/log/share tasks, verified the real public path/process and not just local code/tests
