"""Pure functions for serializing Game.player state to a savable dict.

Only keys in SAVED_PLAYER_KEYS are persisted, preventing accidental leakage
of debug-only or transient battle state into save files.
"""
from __future__ import annotations

from typing import Any

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
    "boss_defeated",
    "max_zone_reached",
    "landmarkTreeSeen", "landmarkTowerSeen",
    "dialog_flags",
)


def dump_snapshot(player: dict[str, Any], town_pos: tuple[int, int]) -> dict[str, Any]:
    """Game.player から保存用 dict を組み立てる。

    town_pos はセーブを実行した町タイルの座標。ロード時にプレイヤーを
    同じタイル上に出現させるために使う。
    """
    saved_player = {key: player[key] for key in SAVED_PLAYER_KEYS if key in player}
    return {
        "save_version": SAVE_VERSION,
        "town_pos": [int(town_pos[0]), int(town_pos[1])],
        "player": saved_player,
    }


def restore_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """SaveStore.load() の結果を Game に流し込みやすい形に整える。

    Returns:
        {"player": dict, "town_pos": tuple[int, int]}
    """
    raw_pos = snapshot["town_pos"]
    return {
        "player": dict(snapshot["player"]),
        "town_pos": (int(raw_pos[0]), int(raw_pos[1])),
    }
