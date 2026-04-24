from __future__ import annotations

"""PlayerModel 移行のための互換 shim（framework-rule.md M4-4 Level 2）。

新規コードは ``src.shared.state.player_model.PlayerModel`` を直接使うこと。
このモジュールは Scene 内の段階的移行が完了するまで残し、完了後に削除する。
"""

from typing import Any

from src.shared.state.player_model import (
    MAX_LEVEL,
    SAVE_VERSION,
    PlayerItem,
    PlayerModel,
    exp_for_level,
    stats_for_level as _stats_for_level_defense,
)

__all__ = [
    "MAX_LEVEL",
    "SAVE_VERSION",
    "SAVED_PLAYER_KEYS",
    "exp_for_level",
    "stats_for_level",
    "create_initial_player",
    "dump_snapshot",
    "restore_snapshot",
]


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


def stats_for_level(lv: int) -> dict[str, int]:
    """旧 API 互換: `def` キーを使う dict を返す（PlayerModel 側は `defense`）。"""
    s = _stats_for_level_defense(lv)
    return {
        "max_hp": s["max_hp"],
        "max_mp": s["max_mp"],
        "atk": s["atk"],
        "def": s["defense"],
        "agi": s["agi"],
    }


def create_initial_player(start_x: int = 25, start_y: int = 6) -> dict[str, Any]:
    """ニューゲーム用レベル1プレイヤー dict を返す（旧 API 互換）。"""
    return player_model_to_dict(PlayerModel.new_game(start_x=start_x, start_y=start_y))


def dump_snapshot(player: dict[str, Any], town_pos: tuple[int, int]) -> dict[str, Any]:
    """player dict からセーブ dict を作る（旧 API 互換）。"""
    saved_player = {key: player[key] for key in SAVED_PLAYER_KEYS if key in player}
    return {
        "save_version": SAVE_VERSION,
        "town_pos": [int(town_pos[0]), int(town_pos[1])],
        "player": saved_player,
    }


def restore_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """セーブ dict から player dict と town_pos を復元する（旧 API 互換）。"""
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


def player_model_to_dict(pm: PlayerModel) -> dict[str, Any]:
    """PlayerModel を旧互換 dict に変換する（Scene 内 player dict 参照の互換用）。

    キー名は旧セーブ形式と同じ。`defense` は `def` として出力される。
    """
    return {
        "x": pm.x, "y": pm.y,
        "hp": pm.hp, "max_hp": pm.max_hp,
        "mp": pm.mp, "max_mp": pm.max_mp,
        "atk": pm.atk, "def": pm.defense, "agi": pm.agi,
        "lv": pm.lv, "exp": pm.exp, "gold": pm.gold,
        "weapon": pm.weapon, "armor": pm.armor,
        "items": [{"id": it.id, "qty": it.qty} for it in pm.items],
        "spells": list(pm.spells),
        "poisoned": pm.poisoned,
        "in_dungeon": pm.in_dungeon,
        "glitch_lord_defeated": pm.glitch_lord_defeated,
        "max_zone_reached": pm.max_zone_reached,
        "landmarkTreeSeen": pm.landmarkTreeSeen,
        "landmarkTowerSeen": pm.landmarkTowerSeen,
        "towerEpilogueSeen": pm.towerEpilogueSeen,
        "treeAsked": pm.treeAsked,
        "towerNoiseCleared": pm.towerNoiseCleared,
        "professor_intro_seen": pm.professor_intro_seen,
        "professor_defeated": pm.professor_defeated,
        "professor_ending_seen": pm.professor_ending_seen,
        "bgm_enabled": pm.bgm_enabled,
        "sfx_enabled": pm.sfx_enabled,
        "vfx_enabled": pm.vfx_enabled,
        "dialog_flags": dict(pm.dialog_flags),
        "town_talk_idx": list(pm.town_talk_idx),
    }
