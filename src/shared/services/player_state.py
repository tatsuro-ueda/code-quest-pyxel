"""PlayerModel 移行のための互換 shim（framework-rule.md M4-4 Level 2）。

このファイルに含まれる関数・クラス：

- stats_for_level: stats_for_level を `def` キー dict に詰め直す互換 public 関数
- create_initial_player: PlayerModel.new_game を旧 dict 形式で返す public 関数
- dump_snapshot: player dict と town_pos からセーブ dict を組み立てる public 関数
- restore_snapshot: セーブ dict から player dict と town_pos を復元する public 関数
- player_model_to_dict: PlayerModel を旧互換 dict に変換する public 関数
- _renormalize_glitch_flag: legacy boss_defeated を新キーに移し替える内部 helper
- _strip_legacy_av_keys: CJ44 で撤去済の av 系キーを player から落とす内部 helper
- _build_restored_pair: 復元結果 dict (player, town_pos) を組み立てる内部 helper
- _build_player_dict_core: PlayerModel の数値・装備系を dict 化する内部 helper
- _build_player_dict_progress: PlayerModel の進行フラグ系を dict 化する内部 helper
- _has_legacy_glitch_lord_alias: legacy boss_defeated だけ残る player か判定する述語

Problems:
    - 旧 player dict / 新 PlayerModel の差分（`def` vs `defense` キー、撤去済
      av キーなど）を public 関数本体に書くと、互換性ルールが入口契約と
      混ざってしまう。
    - restore_snapshot は legacy alias の移行と撤去済キーの掃除を両方やるため、
      public 関数のままだと制御フロー（if）が直接残り CR203/CR204 を満たさない。

Solutions:
    - 互換変換は _renormalize_glitch_flag / _strip_legacy_av_keys /
      _build_restored_pair / _build_player_dict_core /
      _build_player_dict_progress の private helper に分離し、public 関数は
      「private 委譲 + return」のステップ列に揃える。
    - 旧 alias 判定は述語 _has_legacy_glitch_lord_alias にまとめ、複合 if を排除する。
"""
from __future__ import annotations

from typing import Any

from src.shared.state.player_model import (
    MAX_LEVEL,
    SAVE_VERSION,
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


# === Public API ===


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
    "dialog_flags",
    "town_talk_idx",
)


def stats_for_level(lv: int) -> dict[str, int]:  # noqa: CR100
    """旧 API 互換: `def` キーを使う dict を返す（PlayerModel 側は `defense`）。

    Args:
        lv: プレイヤーレベル（1 以上）。
    Returns:
        max_hp / max_mp / atk / def / agi を持つ int dict。
    Policy:
        - 関数名 stats_for_level は test 群と bundle wildcard import で固定参照
          されているため変更しない（# noqa: CR100）。
        - 値の算出は PlayerModel 側 stats_for_level に委ね、ここではキー名
          `defense` → `def` の置換のみ行う。
    """
    stats = _stats_for_level_defense(lv)
    return {
        "max_hp": stats["max_hp"],
        "max_mp": stats["max_mp"],
        "atk": stats["atk"],
        "def": stats["defense"],
        "agi": stats["agi"],
    }


def create_initial_player(
    start_x: int = 25,
    start_y: int = 6,
) -> dict[str, Any]:
    """ニューゲーム用レベル 1 プレイヤー dict を返す（旧 API 互換）。

    Args:
        start_x: 初期 X 座標（タイル単位）。
        start_y: 初期 Y 座標（タイル単位）。
    Returns:
        旧 player dict 形式の初期値（`def` キー付き）。
    Policy:
        - PlayerModel.new_game に委ね、dict 変換は player_model_to_dict に委譲する。
    """
    return player_model_to_dict(
        PlayerModel.new_game(start_x=start_x, start_y=start_y))


def dump_snapshot(
    player: dict[str, Any],
    town_pos: tuple[int, int],
) -> dict[str, Any]:
    """player dict からセーブ dict を作る（旧 API 互換）。

    Args:
        player: 旧形式の player dict。
        town_pos: 町に戻ったときの (x, y)。
    Returns:
        save_version / town_pos / player を持つセーブ dict。
    Policy:
        - SAVED_PLAYER_KEYS に含まれる key だけを抽出して保存する。
    """
    saved_player = {key: player[key]
                    for key in SAVED_PLAYER_KEYS if key in player}
    return {
        "save_version": SAVE_VERSION,
        "town_pos": [int(town_pos[0]), int(town_pos[1])],
        "player": saved_player,
    }


def restore_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """セーブ dict から player dict と town_pos を復元する（旧 API 互換）。

    Args:
        snapshot: dump_snapshot で生成したセーブ dict。
    Returns:
        player / town_pos を持つ dict（player は旧 dict 形式）。
    Policy:
        - legacy `boss_defeated` → `glitch_lord_defeated` の rename と
          CJ44 で撤去済の bgm/sfx/vfx_enabled の掃除は private helper に委ねる。
    """
    raw_pos = snapshot["town_pos"]
    player = dict(snapshot["player"])
    _renormalize_glitch_flag(player)
    _strip_legacy_av_keys(player)
    return _build_restored_pair(player, raw_pos)


def player_model_to_dict(pm: PlayerModel) -> dict[str, Any]:  # noqa: CR100
    """PlayerModel を旧互換 dict に変換する（Scene 内 player dict 参照の互換用）。

    キー名は旧セーブ形式と同じ。`defense` は `def` として出力される。

    Args:
        pm: 変換元の PlayerModel。
    Returns:
        旧 player dict（数値・装備・進行フラグをまとめたフラットな dict）。
    Policy:
        - 関数名 player_model_to_dict は bundle wildcard / test から固定参照されて
          いるため変更しない（# noqa: CR100）。
        - 数値・装備系は _build_player_dict_core に、進行フラグ系は
          _build_player_dict_progress に分離し、本関数は merge のみ行う。
    """
    out = _build_player_dict_core(pm)
    out.update(_build_player_dict_progress(pm))
    return out


# === Internal helpers (private) ===


def _has_legacy_glitch_lord_alias(player: dict[str, Any]) -> bool:
    """legacy `boss_defeated` のみ残る player かを判定する。

    Args:
        player: 復元中の player dict。
    Returns:
        `glitch_lord_defeated` 未設定かつ `boss_defeated` が存在するなら True。
    Policy:
        - 真なら _renormalize_glitch_flag が legacy alias を新キーに移す。
    """
    return ("glitch_lord_defeated" not in player
            and "boss_defeated" in player)


def _renormalize_glitch_flag(player: dict[str, Any]) -> None:
    """legacy `boss_defeated` を `glitch_lord_defeated` に移し替える。

    Args:
        player: 復元中の player dict（in-place で書き換える）。
    Policy:
        - 述語 _has_legacy_glitch_lord_alias を経由して判定する。
        - alias 移行後、`boss_defeated` キーは取り除く（pop）。
    """
    if not _has_legacy_glitch_lord_alias(player):
        return
    player["glitch_lord_defeated"] = bool(player.pop("boss_defeated"))


_LEGACY_AV_KEYS: tuple[str, ...] = (
    "bgm_enabled",
    "sfx_enabled",
    "vfx_enabled",
)


def _strip_legacy_av_keys(player: dict[str, Any]) -> None:
    """CJ44 で撤去済の bgm/sfx/vfx_enabled キーを player から落とす。

    Args:
        player: 復元中の player dict（in-place で書き換える）。
    Policy:
        - 2026-05-07 改訂（CJ44 確定版）。古いセーブに残っていても無視する。
    """
    for legacy_av_key in _LEGACY_AV_KEYS:
        player.pop(legacy_av_key, None)


def _build_restored_pair(
    player: dict[str, Any],
    raw_pos: Any,
) -> dict[str, Any]:
    """復元結果の player / town_pos を dict にまとめて返す。

    Args:
        player: 移行・掃除済みの player dict。
        raw_pos: snapshot["town_pos"]（list / tuple）。
    Returns:
        player / town_pos を持つ復元結果 dict。
    Policy:
        - town_pos は int の tuple に正規化する。
    """
    return {
        "player": player,
        "town_pos": (int(raw_pos[0]), int(raw_pos[1])),
    }


def _build_player_dict_core(pm: PlayerModel) -> dict[str, Any]:
    """PlayerModel の数値・装備・所持品系を旧 dict 形式で返す。

    Args:
        pm: 変換元の PlayerModel。
    Returns:
        座標・HP/MP・能力値・装備・items/spells を持つ dict。
    Policy:
        - キー `def` は PlayerModel 側 `defense` のリネーム。
        - items は dataclass のリストから dict のリストに直列化する。
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
    }


def _build_player_dict_progress(pm: PlayerModel) -> dict[str, Any]:
    """PlayerModel の進行フラグ系（ダンジョン・ランドマーク・professor 等）を返す。

    Args:
        pm: 変換元の PlayerModel。
    Returns:
        in_dungeon / glitch_lord_defeated / landmark / professor /
        dialog_flags 等を持つ dict。
    Policy:
        - dialog_flags は新規 dict にコピー、town_talk_idx は list にコピーする。
    """
    return {
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
        "dialog_flags": dict(pm.dialog_flags),
        "town_talk_idx": list(pm.town_talk_idx),
    }
