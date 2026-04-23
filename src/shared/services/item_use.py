from __future__ import annotations

"""アイテム使用の効果適用（P1-G14 で Game から取り込み）。

scenes/menu / scenes/battle から呼ばれる。sfx・dialog_text・last_town_pos に
依存するため game をそのまま受け取る。
"""

from typing import Any


def use_item(game: Any, item_data: dict) -> str:
    """アイテム効果を適用し、表示用メッセージを返す（使えない場合は空文字列）。"""
    kind = item_data["type"]
    if kind == "heal":
        if game.player["hp"] >= game.player["max_hp"]:
            return ""
        game.player["hp"] = min(game.player["max_hp"], game.player["hp"] + item_data["value"])
        game.sfx.play("heal")
        return game.messages.dialog_text(
            "battle.normal.item.heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if kind == "mp_heal":
        game.player["mp"] = min(game.player["max_mp"], game.player["mp"] + item_data["value"])
        game.sfx.play("heal")
        return game.messages.dialog_text(
            "battle.normal.item.mp_heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if kind == "cure_poison":
        if game.player.get("poisoned"):
            game.player["poisoned"] = False
            game.sfx.play("cure")
            return f'{item_data["name"]}を使った。バグ汚染が消えた！'
        return f'{item_data["name"]}を使った。だが今は必要なかった。'
    if kind == "warp":
        tx, ty = getattr(game, "last_town_pos", None) or (25, 6)
        game.player["x"], game.player["y"] = tx, ty
        game.player["in_dungeon"] = False
        return f'{item_data["name"]}を使った。記録した場所に戻った。'
    return ""
