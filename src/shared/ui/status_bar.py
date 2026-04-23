from __future__ import annotations

"""ステータスバーの配置寸法と描画（P1-G15 / Phase 1 整合性修正）。

Q6 決定：bar は UI 寄りのため `shared/ui/` に置く。座標を持つ
`StatusBarLayout` と、描画ロジックを持つ `StatusBar` を同居させる。
"""

from dataclasses import dataclass
from typing import Any

import pyxel


@dataclass(frozen=True)
class StatusBarLayout:
    """画面上部のステータスバー（HP / MP / LV / 所持金など）の寸法。"""

    x: int = 0
    y: int = 0
    width: int = 256
    height: int = 16

    def rect(self) -> tuple[int, int, int, int]:
        """描画用に (x, y, width, height) のタプルを返す。"""
        return (self.x, self.y, self.width, self.height)


@dataclass
class StatusBar:
    """レベル/ゾーン名/HP/MP と HP/MP バーを画面上部に描画する。"""

    game: Any = None

    def draw(self):
        """ステータスバーを 1 行分描画する。"""
        import src.runtime.main_runtime as M
        game = self.game
        pyxel.rect(0, 0, 256, 24, 1)
        p = game.player
        zone = M.get_zone(p["y"], p["in_dungeon"])
        zone_name = M.ZONE_NAMES.get(zone, "???") if game.has_jp_font else M.ZONE_NAMES_EN.get(zone, "???")
        game.messages.text(4, 2, f"レベル{p['lv']} {zone_name}", 7)
        game.messages.text(4, 13, f"HP{p['hp']}/{p['max_hp']} MP{p['mp']}/{p['max_mp']}", 7)
        bar_x = 170; bar_w = 60
        pyxel.rect(bar_x, 4, bar_w, 6, 0)
        hp_ratio = p["hp"] / max(1, p["max_hp"])
        pyxel.rect(bar_x, 4, int(bar_w * hp_ratio), 6, 11 if hp_ratio > 0.3 else 8)
        pyxel.rect(bar_x, 14, bar_w, 6, 0)
        mp_ratio = p["mp"] / max(1, p["max_mp"])
        pyxel.rect(bar_x, 14, int(bar_w * mp_ratio), 6, 12)
        if game.debug_mode:
            game.messages.text(130, 2, "DEBUG", 8)
