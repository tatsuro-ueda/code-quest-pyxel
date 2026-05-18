"""アイテム使用の効果適用（PlayerModel への薄いブリッジ）。

このファイルに含まれる関数・クラス：

- 旧互換ブリッジ public 関数 use_item（PlayerModel.use_item に委譲し sfx/dialog 文字列を返す）
- player_model.use_item を呼び出し result 文字列を返す内部関数 _call_player_use_item
- result 文字列ごとに sfx と dialog_text を解決し UI 文字列を返す内部関数 _build_message_for_result
- HP 回復時の sfx 再生と dialog_text を組み立てる内部関数 _build_heal_message
- MP 回復時の sfx 再生と dialog_text を組み立てる内部関数 _build_mp_heal_message
- バグ汚染解除成功時の sfx 再生と固定文言を返す内部関数 _build_cure_ok_message
- バグ汚染不要時の固定文言を返す内部関数 _build_cure_none_message
- ワープ時の固定文言を返す内部関数 _build_warp_message

Problems:
    - PlayerModel.use_item の result 文字列ごとに sfx 再生と dialog 文言を public 関数に
      直書きすると、入口契約と分岐実装が混ざって読みにくくなる。
    - if/elif の連鎖を public 関数に置くと、新しい result 種別を追加するたびに
      公開シグネチャ周辺を触ることになる。

Solutions:
    - public 関数 use_item は「private 委譲 + return」のステップ列に揃え、
      result 文字列ごとの分岐と文言組み立ては private helper にまとめて切り出す。
    - sfx 再生と dialog_text 解決は scenes/menu などにも残るが、旧互換ブリッジとして
      同じ責務分割を踏襲する。
"""
from __future__ import annotations

from typing import Any


# === Public API ===

def use_item(game: Any, item_data: dict) -> str:
    """旧互換ブリッジ。ルール本体は PlayerModel.use_item() に委譲する。

    Args:
        game: sfx / messages / player_model / last_town_pos を持つ Game 互換オブジェクト。
        item_data: SSoT の ITEMS 1 件分（少なくとも name / value を含む）。
    Returns:
        UI 表示用のメッセージ文字列（該当する result が無ければ空文字）。
    Policy:
        - PlayerModel.use_item() の戻り値文字列をキーに、private helper へ委譲する
          ステップ列に揃える。
    """
    result = _call_player_use_item(game, item_data)
    return _build_message_for_result(game, item_data, result)


# === Internal helpers (private) ===

def _call_player_use_item(game: Any, item_data: dict) -> str:
    """PlayerModel.use_item() を呼び出して result 文字列を返す。

    Args:
        game: player_model と last_town_pos を持つ Game 互換オブジェクト。
        item_data: SSoT の ITEMS 1 件分。
    Returns:
        PlayerModel が決めた result 種別文字列。
    Policy:
        - last_town_pos 未設定時は既定値 (25, 6) を渡し、PlayerModel 側のルールに委ねる。
    """
    return game.player_model.use_item(
        item_data,
        town_pos=getattr(game, "last_town_pos", None) or (25, 6),
    )


def _build_message_for_result(game: Any, item_data: dict, result: str) -> str:
    """result 文字列に応じて sfx 再生と UI 文字列の組み立てを切り替える。

    Args:
        game: sfx と messages を持つ Game 互換オブジェクト。
        item_data: SSoT の ITEMS 1 件分。
        result: PlayerModel.use_item() の戻り値（"heal" / "mp_heal" /
            "cure_poison_ok" / "cure_poison_none" / "warp" / その他）。
    Returns:
        UI 表示用のメッセージ文字列（該当しない result は空文字）。
    Policy:
        - public 関数から制御フローを引き取り、result ごとの helper に委譲する。
    """
    if result == "heal":
        return _build_heal_message(game, item_data)
    if result == "mp_heal":
        return _build_mp_heal_message(game, item_data)
    if result == "cure_poison_ok":
        return _build_cure_ok_message(game, item_data)
    if result == "cure_poison_none":
        return _build_cure_none_message(item_data)
    if result == "warp":
        return _build_warp_message(item_data)
    return ""


def _build_heal_message(game: Any, item_data: dict) -> str:
    """HP 回復時の sfx 再生と dialog_text 解決を行う。

    Args:
        game: sfx と messages を持つ Game 互換オブジェクト。
        item_data: SSoT の ITEMS 1 件分（name / value を使う）。
    Returns:
        UI 表示用のメッセージ文字列。
    Policy:
        - sfx の "heal" を 1 度だけ再生する。
    """
    game.sfx.play("heal")
    return game.messages.dialog_text(
        "battle.normal.item.heal",
        item=item_data["name"],
        value=item_data["value"],
    )


def _build_mp_heal_message(game: Any, item_data: dict) -> str:
    """MP 回復時の sfx 再生と dialog_text 解決を行う。

    Args:
        game: sfx と messages を持つ Game 互換オブジェクト。
        item_data: SSoT の ITEMS 1 件分（name / value を使う）。
    Returns:
        UI 表示用のメッセージ文字列。
    Policy:
        - sfx の "heal" を 1 度だけ再生する。
    """
    game.sfx.play("heal")
    return game.messages.dialog_text(
        "battle.normal.item.mp_heal",
        item=item_data["name"],
        value=item_data["value"],
    )


def _build_cure_ok_message(game: Any, item_data: dict) -> str:
    """バグ汚染解除成功時の sfx 再生と固定文言を返す。

    Args:
        game: sfx を持つ Game 互換オブジェクト。
        item_data: SSoT の ITEMS 1 件分（name を使う）。
    Returns:
        UI 表示用のメッセージ文字列。
    Policy:
        - sfx の "cure" を 1 度だけ再生する。
    """
    game.sfx.play("cure")
    return f'{item_data["name"]}を使った。バグ汚染が消えた！'


def _build_cure_none_message(item_data: dict) -> str:
    """バグ汚染不要時の固定文言を返す。

    Args:
        item_data: SSoT の ITEMS 1 件分（name を使う）。
    Returns:
        UI 表示用のメッセージ文字列。
    Policy:
        - 副作用なし。
    """
    return f'{item_data["name"]}を使った。だが今は必要なかった。'


def _build_warp_message(item_data: dict) -> str:
    """ワープ時の固定文言を返す。

    Args:
        item_data: SSoT の ITEMS 1 件分（name を使う）。
    Returns:
        UI 表示用のメッセージ文字列。
    Policy:
        - 副作用なし（ワープ自体は PlayerModel 側で済んでいる）。
    """
    return f'{item_data["name"]}を使った。記録した場所に戻った。'
