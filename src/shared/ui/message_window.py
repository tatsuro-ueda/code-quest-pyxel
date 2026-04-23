from __future__ import annotations

"""メッセージウィンドウの行幅・改行位置（Phase 1 スケルトン）。

dialog_window.py より短いメッセージ向け。P1-G12（message_display 移動）で
_wrap_text がここの `wrap_width` を参照するようになる。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MessageWindowLayout:
    """短いメッセージ表示向けのウィンドウ寸法と行折返し幅。"""

    x: int = 8
    y: int = 208
    width: int = 240
    height: int = 44
    wrap_width: int = 28

    def rect(self) -> tuple[int, int, int, int]:
        """描画用に (x, y, width, height) のタプルを返す。"""
        return (self.x, self.y, self.width, self.height)
