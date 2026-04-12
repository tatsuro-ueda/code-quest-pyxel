#!/usr/bin/env python3
"""Generate src/generated/*.py from assets/*.yaml (SSoT).

Usage:
    python tools/gen_data.py          # generate all
    python tools/gen_data.py enemies  # generate one
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
import stat

# -- paths ------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
GENERATED = ROOT / "src" / "generated"

import yaml

HEADER = "# GENERATED - DO NOT EDIT  (source: assets/{yaml})\n"

# -- registry: yaml_name -> (variable_name, type_hint) ----------------------
TARGETS: dict[str, tuple[str, str]] = {
    "enemies": ("ENEMIES", "list[dict[str, Any]]"),
    "items": ("ITEMS", "list[dict[str, Any]]"),
    "weapons": ("WEAPONS", "list[dict[str, Any]]"),
    "armors": ("ARMORS", "list[dict[str, Any]]"),
    "spells": ("SPELLS", "list[dict[str, Any]]"),
    "shops": ("SHOPS", "dict[str, Any]"),
    "dialogue": ("DIALOGUE_JA", "dict[str, Any]"),
}


def _repr_value(obj: Any, indent: int = 0) -> str:
    """Pretty-print a Python literal with readable indentation."""
    pad = "    " * indent
    inner = "    " * (indent + 1)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for k, v in obj.items():
            items.append(f"{inner}{_repr_value(k)}: {_repr_value(v, indent + 1)}")
        return "{\n" + ",\n".join(items) + f",\n{pad}" + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        if all(not isinstance(e, (dict, list)) for e in obj):
            return "[" + ", ".join(_repr_value(e) for e in obj) + "]"
        items = [f"{inner}{_repr_value(e, indent + 1)}" for e in obj]
        return "[\n" + ",\n".join(items) + f",\n{pad}]"
    if isinstance(obj, str):
        return repr(obj)
    if isinstance(obj, bool):
        return repr(obj)
    if obj is None:
        return "None"
    return repr(obj)


def _write_generated_module(out_path: Path, lines: list[str]) -> None:
    """Write a generated Python module and restore read-only permissions."""
    if out_path.exists():
        out_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    out_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def _dialogue_module_lines(data: Any) -> list[str]:
    """Build the generated module for dialogue data."""
    if not isinstance(data, dict):
        raise TypeError("dialogue.yaml must be a mapping with 'ja' and 'en' keys")
    if not isinstance(data.get("ja"), dict):
        raise TypeError("dialogue.yaml: 'ja' must be a mapping")
    if not isinstance(data.get("en"), dict):
        raise TypeError("dialogue.yaml: 'en' must be a mapping")

    return [
        HEADER.format(yaml="dialogue.yaml"),
        "from __future__ import annotations\n",
        "from typing import Any\n",
        "",
        f"DIALOGUE_JA: dict[str, Any] = {_repr_value(data['ja'])}\n",
        "",
        f"DIALOGUE_EN: dict[str, Any] = {_repr_value(data['en'])}\n",
    ]


def generate_one(name: str) -> bool:
    """Generate src/generated/{name}.py from assets/{name}.yaml.

    Returns True on success, False on error.
    """
    if name not in TARGETS:
        print(f"error: unknown target '{name}' (known: {', '.join(TARGETS)})",
              file=sys.stderr)
        return False

    var_name, type_hint = TARGETS[name]
    yaml_path = ASSETS / f"{name}.yaml"
    out_path = GENERATED / f"{name}.py"

    if not yaml_path.exists():
        print(f"error: {yaml_path} not found", file=sys.stderr)
        return False

    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"error: {yaml_path}: {e}", file=sys.stderr)
        return False
    except OSError as e:
        print(f"error: {yaml_path}: {e}", file=sys.stderr)
        return False

    GENERATED.mkdir(parents=True, exist_ok=True)

    if name == "dialogue":
        try:
            lines = _dialogue_module_lines(data)
        except TypeError as e:
            print(f"error: {yaml_path}: {e}", file=sys.stderr)
            return False
    else:
        lines = [
            HEADER.format(yaml=f"{name}.yaml"),
            "from __future__ import annotations\n",
            "from typing import Any\n",
            "",
            f"{var_name}: {type_hint} = {_repr_value(data)}\n",
        ]
    _write_generated_module(out_path, lines)

    # ensure __init__.py exists
    init = GENERATED / "__init__.py"
    if not init.exists():
        init.write_text("", encoding="utf-8")
        init.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

    print(f"  generated: {out_path.relative_to(ROOT)}")
    return True


def main() -> int:
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(TARGETS)
    ok = True
    for name in targets:
        if not generate_one(name):
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
