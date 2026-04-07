"""Player factory and level/stat formulas.

JS版 (`game/index.html` 行806-814) の `expForLevel`/`statsForLevel`/`MAX_LEVEL`
を Python に移植した純粋関数群と、初期プレイヤー生成を担う。
"""

from __future__ import annotations

from typing import Any

MAX_LEVEL = 100


def exp_for_level(lv: int) -> int:
    """Return the experience needed to reach the given level.

    Mirrors the JS implementation:
        if(lv===2)return 26;
        return Math.floor(10*Math.pow(lv,2)+6*lv);
    """
    if lv == 2:
        return 26
    return int(10 * lv * lv + 6 * lv)


def stats_for_level(lv: int) -> dict[str, int]:
    """Return baseline player stats for the given level.

    Mirrors the JS implementation:
        {maxHp:30+lv*15, maxMp:10+lv*6, atk:5+lv*2, def:3+lv*3, agi:5+lv*2}
    """
    return {
        "max_hp": 30 + lv * 15,
        "max_mp": 10 + lv * 6,
        "atk": 5 + lv * 2,
        "def": 3 + lv * 3,
        "agi": 5 + lv * 2,
    }


def create_initial_player(start_x: int = 25, start_y: int = 6) -> dict[str, Any]:
    """Create a fresh player dict at level 1 using stats_for_level(1).

    The base stats keys (max_hp, max_mp, atk, def, agi) are set from
    stats_for_level(1), and current hp/mp default to their max values.
    """
    base = stats_for_level(1)
    return {
        "x": start_x,
        "y": start_y,
        "hp": base["max_hp"],
        "max_hp": base["max_hp"],
        "mp": base["max_mp"],
        "max_mp": base["max_mp"],
        "atk": base["atk"],
        "def": base["def"],
        "agi": base["agi"],
        "lv": 1,
        "exp": 0,
        "gold": 50,
        "weapon": 0,
        "armor": 0,
        "items": [{"id": 0, "qty": 3}],
        "spells": [],
        "poisoned": False,
        "in_dungeon": False,
        "boss_defeated": False,
        "max_zone_reached": 0,
        "landmarkTreeSeen": False,
        "landmarkTowerSeen": False,
        "dialog_flags": {},
    }
