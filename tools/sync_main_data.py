#!/usr/bin/env python3
"""Sync main.py's inlined game_data section from src/generated/*.

Usage:
    python tools/sync_main_data.py           # update main.py in place
    python tools/sync_main_data.py --check   # verify without modifying (exit 1 if stale)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN_PY = ROOT / "main.py"
GENERATED = ROOT / "src" / "generated"
GAME_DATA = ROOT / "src" / "game_data.py"

MARKER_START = "# === inlined: src/game_data.py ==="
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


def sync(check_only: bool = False) -> int:
    """Sync main.py's game_data section. Returns 0 on success, 1 on mismatch (check mode)."""
    content = MAIN_PY.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Find the game_data section
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == MARKER_START:
            start_idx = i
        elif start_idx is not None and end_idx is None:
            if line.startswith(MARKER_NEXT_SECTION) and i > start_idx:
                end_idx = i
                break

    if start_idx is None:
        print(f"error: marker '{MARKER_START}' not found in main.py", file=sys.stderr)
        return 1

    if end_idx is None:
        print("error: could not find next section marker after game_data", file=sys.stderr)
        return 1

    new_section = build_inlined_section()
    new_lines = lines[:start_idx + 1] + new_section.split("\n") + [""] + lines[end_idx:]
    new_content = "\n".join(new_lines)

    if check_only:
        if content == new_content:
            print("main.py game_data section is up to date.")
            return 0
        else:
            print("main.py game_data section is STALE. Run `make gen` to update.", file=sys.stderr)
            return 1

    MAIN_PY.write_text(new_content, encoding="utf-8")
    print(f"  synced: main.py game_data section ({end_idx - start_idx - 1} → {len(new_section.splitlines())} lines)")
    return 0


def main() -> int:
    check_only = "--check" in sys.argv
    return sync(check_only)


if __name__ == "__main__":
    sys.exit(main())
