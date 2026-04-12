"""Game data module.

Generated data (src/generated/) を import し、派生データを構築する。
SSoT は assets/*.yaml → tools/gen_data.py → src/generated/*.py の一方通行。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def load_yaml(path: str | Path) -> Any:
    """Load any YAML file under the project."""
    text = Path(path).read_text(encoding="utf-8")
    return yaml.safe_load(text)


# --- generated data (YAML → gen_data.py → here) ---
from src.generated.enemies import ENEMIES
from src.generated.items import ITEMS
from src.generated.weapons import WEAPONS
from src.generated.armors import ARMORS
from src.generated.spells import SPELLS
from src.generated.shops import SHOPS
from src.generated.dialogue import DIALOGUE_JA, DIALOGUE_EN


# --- derived data ---

def _build_zone_enemies(enemies: list[dict[str, Any]]) -> dict[int, list]:
    """zone -> list[enemy] にグルーピング。ボス・教授等は除外。"""
    by_zone: dict[int, list] = {}
    for e in enemies:
        if e.get("is_boss") or e.get("is_professor") or e.get("post_clear_only"):
            continue
        by_zone.setdefault(e["zone"], []).append(e)
    return by_zone


ZONE_ENEMIES = _build_zone_enemies(ENEMIES)
BOSS_DATA = next(e for e in ENEMIES if e.get("is_boss"))
PROFESSOR_DATA = next(e for e in ENEMIES if e.get("is_professor"))
GLITCH_CLONE_DATA = next(e for e in ENEMIES if e.get("post_clear_only"))
NOISE_GUARDIAN_DATA = next(e for e in ENEMIES if e.get("is_noise_guardian"))

SPELL_BY_NAME = {s["name"]: s for s in SPELLS}

INN_PRICES = SHOPS["inn_prices"]
SHOP_LIST = SHOPS["shops"]


# --- boss phase logic ---

def boss_phase(hp_ratio: float) -> str:
    """Return a phase label based on the boss HP ratio.

    JS版 `getBossPhases` 相当:
      - hp_ratio > 0.6 → 'phase1'
      - 0.3 < hp_ratio <= 0.6 → 'phase2'
      - hp_ratio <= 0.3 → 'phase3'
    """
    if hp_ratio > 0.6:
        return "phase1"
    if hp_ratio > 0.3:
        return "phase2"
    return "phase3"


BOSS_PHASE_MESSAGES = {
    "phase2": "ボスの様子が変わった！",
    "phase3": "ボスは最後の力を振り絞っている！",
}


# --- backward-compatible loaders (for tests) ---

def load_enemies() -> list[dict[str, Any]]:
    return ENEMIES


def load_items() -> list[dict[str, Any]]:
    return ITEMS


def load_weapons() -> list[dict[str, Any]]:
    return WEAPONS


def load_armors() -> list[dict[str, Any]]:
    return ARMORS


def load_spells() -> list[dict[str, Any]]:
    return SPELLS


def load_shops() -> dict[str, Any]:
    return SHOPS


def load_dialogue(language: str) -> dict[str, Any]:
    if language == "ja":
        return DIALOGUE_JA
    if language == "en":
        return DIALOGUE_EN
    raise ValueError(f"unknown dialogue language: {language}")
