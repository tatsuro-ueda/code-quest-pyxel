from __future__ import annotations

"""アイテム使用の効果適用（framework-rule.md M4-4 Level 2 に従い PlayerModel へ委譲）。

scenes/menu / scenes/battle から呼ばれる。PlayerModel にルールを集約した後も、
呼び出し側から sfx 再生と dialog_text 解決を必要とするため、薄いブリッジとして残す。
"""

from typing import Any


def use_item(game: Any, item_data: dict) -> str:
    """アイテム効果を適用し、表示用メッセージを返す（使えない場合は空文字列）。"""
    pm = game.player_model
    kind = item_data["type"]
    if kind == "heal":
        if pm.hp >= pm.max_hp:
            return ""
        pm.heal(item_data["value"])
        game.sfx.play("heal")
        return game.messages.dialog_text(
            "battle.normal.item.heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if kind == "mp_heal":
        pm.restore_mp(item_data["value"])
        game.sfx.play("heal")
        return game.messages.dialog_text(
            "battle.normal.item.mp_heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if kind == "cure_poison":
        if pm.cure_poison():
            game.sfx.play("cure")
            return f'{item_data["name"]}を使った。バグ汚染が消えた！'
        return f'{item_data["name"]}を使った。だが今は必要なかった。'
    if kind == "warp":
        tx, ty = getattr(game, "last_town_pos", None) or (25, 6)
        pm.x, pm.y = tx, ty
        pm.in_dungeon = False
        return f'{item_data["name"]}を使った。記録した場所に戻った。'
    return ""
