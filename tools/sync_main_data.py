#!/usr/bin/env python3
"""Sync bundled game's inlined data sections from src/generated/*.

Usage:
    python tools/sync_main_data.py           # update main.py / main_development.py in place
    python tools/sync_main_data.py --check   # verify without modifying (exit 1 if stale)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "src" / "generated"
GAME_DATA = ROOT / "src" / "game_data.py"
SYNC_TARGETS = (
    ROOT / "main.py",
    ROOT / "main_development.py",
)

MARKER_START = "# === inlined: src/game_data.py ==="
MARKER_DIALOGUE_START = "# === inlined: src/generated/dialogue.py ==="
MARKER_NEXT_SECTION = "# === inlined: src/"


def build_inlined_section() -> str:
    """Build the inlined game_data content from generated + game_data.py."""
    # 1. Read all generated data files
    data_lines: list[str] = []
    data_lines.append('"""Game data — generated from assets/*.yaml via tools/gen_data.py.')
    data_lines.append("")
    data_lines.append("SSoT: assets/*.yaml → tools/gen_data.py → src/generated/*.py")
    data_lines.append('この定義を直接編集しないでください。YAML を編集して `make gen` を実行してください。')
    data_lines.append('"""')
    data_lines.append("")
    data_lines.append("")
    data_lines.append("from typing import Any")
    data_lines.append("")

    # Read each generated file and extract the data definition
    for name in ("enemies", "items", "weapons", "armors", "spells", "shops"):
        gen_file = GENERATED / f"{name}.py"
        if not gen_file.exists():
            print(f"error: {gen_file} not found. Run `make gen` first.", file=sys.stderr)
            sys.exit(1)
        for line in gen_file.read_text(encoding="utf-8").splitlines():
            # Skip header, imports, blank lines at top
            if line.startswith("# GENERATED"):
                continue
            if line.startswith("from __future__"):
                continue
            if line.startswith("from typing"):
                continue
            data_lines.append(line)

    # 2. Read game_data.py and extract derived data + functions (skip imports and generated imports)
    data_lines.append("")
    data_lines.append("# --- derived data ---")
    in_derived = False
    for line in GAME_DATA.read_text(encoding="utf-8").splitlines():
        # Skip module docstring, imports, generated imports
        if line.startswith('"""') or line.startswith("from __future__"):
            continue
        if line.startswith("from typing"):
            continue
        if line.startswith("from pathlib"):
            continue
        if line.startswith("from src.generated"):
            continue
        if line.startswith("from src.simple_yaml"):
            continue
        if line.startswith("ASSETS_DIR"):
            continue
        if "def load_yaml" in line:
            # Skip load_yaml function (uses simple_yaml, not needed in inlined version)
            in_derived = False
            continue
        if line.startswith("# --- generated data"):
            in_derived = True
            continue
        if line.startswith("# --- derived data") or line.startswith("# --- boss phase") or line.startswith("# --- backward"):
            in_derived = True
            data_lines.append(line)
            continue
        if in_derived:
            data_lines.append(line)

    return "\n".join(data_lines)


def _read_generated_definition_lines(name: str) -> list[str]:
    """Return generated constant definitions without headers/imports."""
    gen_file = GENERATED / f"{name}.py"
    if not gen_file.exists():
        print(f"error: {gen_file} not found. Run `make gen` first.", file=sys.stderr)
        sys.exit(1)

    lines: list[str] = []
    for line in gen_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("# GENERATED"):
            continue
        if line.startswith("from __future__"):
            continue
        if line.startswith("from typing"):
            continue
        lines.append(line)
    return lines


def build_inlined_dialogue_section() -> str:
    """Build the inlined dialogue content from generated dialogue data."""
    data_lines: list[str] = []
    data_lines.append('"""Dialogue data — generated from assets/dialogue.yaml via tools/gen_data.py.')
    data_lines.append("")
    data_lines.append("SSoT: assets/dialogue.yaml → tools/gen_data.py → src/generated/dialogue.py")
    data_lines.append('この定義を直接編集しないでください。assets/dialogue.yaml を編集して `make gen` を実行してください。')
    data_lines.append('"""')
    data_lines.append("")
    data_lines.append("")
    data_lines.append("from typing import Any")
    data_lines.append("")
    data_lines.extend(_read_generated_definition_lines("dialogue"))
    return "\n".join(data_lines)


def _replace_inlined_section(
    lines: list[str],
    marker_start: str,
    new_section: str,
) -> list[str]:
    """Replace one # === inlined: ... === section in a bundled game file."""
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == marker_start:
            start_idx = i
        elif start_idx is not None and end_idx is None:
            if line.startswith(MARKER_NEXT_SECTION) and i > start_idx:
                end_idx = i
                break

    if start_idx is None:
        print(f"error: marker '{marker_start}' not found in target file", file=sys.stderr)
        sys.exit(1)

    if end_idx is None:
        print(f"error: could not find next section marker after {marker_start}", file=sys.stderr)
        sys.exit(1)

    return lines[:start_idx + 1] + new_section.split("\n") + [""] + lines[end_idx:]


def sync_file(target_path: Path, check_only: bool = False) -> int:
    """Sync one bundled game file. Returns 0 on success, 1 on mismatch."""
    content = target_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = _replace_inlined_section(lines, MARKER_START, build_inlined_section())
    new_lines = _replace_inlined_section(
        new_lines,
        MARKER_DIALOGUE_START,
        build_inlined_dialogue_section(),
    )
    new_content = "\n".join(new_lines)

    if check_only:
        if content == new_content:
            print(f"{target_path.name} generated sections are up to date.")
            return 0
        else:
            print(
                f"{target_path.name} generated sections are STALE. Run `make gen` to update.",
                file=sys.stderr,
            )
            return 1

    target_path.write_text(new_content, encoding="utf-8")
    print(f"  synced: {target_path.name} generated sections")
    return 0


def sync(check_only: bool = False) -> int:
    """Sync all bundled game files that exist in the repo."""
    exit_code = 0
    for target_path in SYNC_TARGETS:
        if not target_path.exists():
            continue
        exit_code = max(exit_code, sync_file(target_path, check_only=check_only))
    return exit_code


def main() -> int:
    check_only = "--check" in sys.argv
    return sync(check_only)


if __name__ == "__main__":
    sys.exit(main())
