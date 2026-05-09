from __future__ import annotations

"""アイテム使用の効果適用（framework-rule.md M4-4 Level 2 に従い PlayerModel へ委譲）。

scenes/menu / scenes/battle から呼ばれる。PlayerModel にルールを集約した後も、
呼び出し側から sfx 再生と dialog_text 解決を必要とするため、薄いブリッジとして残す。
"""

from typing import Any


def use_item(game: Any, item_data: dict) -> str:
    """旧互換ブリッジ。ルール本体は PlayerModel.use_item() に委譲する。"""
    result = game.player_model.use_item(
        item_data,
        town_pos=getattr(game, "last_town_pos", None) or (25, 6),
    )
    if result == "heal":
        game.sfx.play("heal")
        return game.messages.dialog_text(
            "battle.normal.item.heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if result == "mp_heal":
        game.sfx.play("heal")
        return game.messages.dialog_text(
            "battle.normal.item.mp_heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if result == "cure_poison_ok":
        game.sfx.play("cure")
        return f'{item_data["name"]}を使った。バグ汚染が消えた！'
    if result == "cure_poison_none":
        return f'{item_data["name"]}を使った。だが今は必要なかった。'
    if result == "warp":
        return f'{item_data["name"]}を使った。記録した場所に戻った。'
    return ""
