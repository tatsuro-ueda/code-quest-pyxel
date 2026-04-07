"""Game data YAML loaders.

JS版 (`game/index.html`) のハードコードデータを `assets/*.yaml` に外部化し、
ここから読み出す。`src/simple_yaml.safe_load` を流用する。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.simple_yaml import safe_load

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def load_yaml(path: str | Path) -> Any:
    """Load any YAML file under the project."""
    text = Path(path).read_text(encoding="utf-8")
    return safe_load(text)


def _load(name: str) -> Any:
    return load_yaml(ASSETS_DIR / name)


def load_enemies() -> list[dict[str, Any]]:
    return _load("enemies.yaml")


def load_items() -> list[dict[str, Any]]:
    return _load("items.yaml")


def load_weapons() -> list[dict[str, Any]]:
    return _load("weapons.yaml")


def load_armors() -> list[dict[str, Any]]:
    return _load("armors.yaml")


def load_spells() -> list[dict[str, Any]]:
    return _load("spells.yaml")


def load_shops() -> dict[str, Any]:
    return _load("shops.yaml")
