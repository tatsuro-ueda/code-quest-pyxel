from __future__ import annotations

"""Player state lifecycle helpers.

This module groups pure player-domain helpers that are reused across
runtime, tests, and save compatibility checks:

- level/stat formulas
- initial player creation
- save snapshot serialization/restoration
"""

from typing import Any


MAX_LEVEL = 100
SAVE_VERSION = 1

# 明示リスト。新しいフィールドを保存対象にしたいときはここに追加する。
SAVED_PLAYER_KEYS: tuple[str, ...] = (
    "x", "y",
    "hp", "max_hp", "mp", "max_mp",
    "atk", "def", "agi",
    "lv", "exp", "gold",
    "weapon", "armor",
    "items", "spells",
    "poisoned",
    "in_dungeon",
    "glitch_lord_defeated",
    "max_zone_reached",
    "landmarkTreeSeen", "landmarkTowerSeen",
    "treeAsked", "towerNoiseCleared",
    "professor_intro_seen", "professor_defeated", "professor_ending_seen",
    "bgm_enabled", "sfx_enabled", "vfx_enabled",
    "dialog_flags",
    "town_talk_idx",
)


def exp_for_level(lv: int) -> int:
    """指定レベル到達に必要な累積経験値を返す。"""
    if lv == 2:
        return 26
    return int(10 * lv * lv + 6 * lv)


def stats_for_level(lv: int) -> dict[str, int]:
    """指定レベルでのプレイヤー基礎ステータスを返す。"""
    return {
        "max_hp": 30 + lv * 15,
        "max_mp": 10 + lv * 6,
        "atk": 5 + lv * 2,
        "def": 3 + lv * 3,
        "agi": 5 + lv * 2,
    }


def create_initial_player(start_x: int = 25, start_y: int = 6) -> dict[str, Any]:
    """ニューゲーム用のレベル1プレイヤー状態 dict を生成する。"""
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
        "glitch_lord_defeated": False,
        "max_zone_reached": 0,
        "landmarkTreeSeen": False,
        "landmarkTowerSeen": False,
        "towerEpilogueSeen": False,
        "treeAsked": False,
        "towerNoiseCleared": False,
        "professor_intro_seen": False,
        "professor_defeated": False,
        "professor_ending_seen": False,
        "bgm_enabled": True,
        "sfx_enabled": True,
        "vfx_enabled": True,
        "dialog_flags": {},
        "town_talk_idx": [0, 0, 0],
    }


def dump_snapshot(player: dict[str, Any], town_pos: tuple[int, int]) -> dict[str, Any]:
    """プレイヤー状態と街座標から、SaveStore に渡せる保存用スナップショットを作る。"""
    saved_player = {key: player[key] for key in SAVED_PLAYER_KEYS if key in player}
    return {
        "save_version": SAVE_VERSION,
        "town_pos": [int(town_pos[0]), int(town_pos[1])],
        "player": saved_player,
    }


def restore_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """SaveStore から読んだ旧形式も含む dict を、実行時が使える正規化形へ変換する。"""
    raw_pos = snapshot["town_pos"]
    player = dict(snapshot["player"])
    if "glitch_lord_defeated" not in player and "boss_defeated" in player:
        player["glitch_lord_defeated"] = bool(player.pop("boss_defeated"))
    player.setdefault("bgm_enabled", True)
    player.setdefault("sfx_enabled", True)
    player.setdefault("vfx_enabled", True)
    return {
        "player": player,
        "town_pos": (int(raw_pos[0]), int(raw_pos[1])),
    }
