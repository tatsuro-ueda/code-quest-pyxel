"""CJG/vfx: VfxSystem.start と draw_overlay の挙動。

根拠:
- docs/product-requirements-av.md（VFX）

2026-05-07 改訂（CJ44 確定版）：vfx_enabled の概念は撤去済（VFX は常に ON）。
未知の vfx_type は start しても timer が立たない。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.vfx import VfxSystem
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)


class StartVfxTest(unittest.TestCase):
    def test_start_with_known_type_sets_timer(self):
        game = _FakeGame()
        vfx = VfxSystem(game=game)

        vfx.start("flash_red")

        self.assertEqual(vfx.type, "flash_red")
        self.assertGreater(vfx.timer, 0)

    def test_start_with_unknown_type_does_not_set_timer(self):
        game = _FakeGame()
        vfx = VfxSystem(game=game)

        vfx.start("unknown_effect_name")

        self.assertEqual(vfx.timer, 0)

    def test_start_overrides_previous_timer(self):
        game = _FakeGame()
        vfx = VfxSystem(game=game)
        vfx.start("flash_red")
        vfx.timer = 1

        vfx.start("flash_white")

        self.assertEqual(vfx.type, "flash_white")
        self.assertGreater(vfx.timer, 1)


if __name__ == "__main__":
    unittest.main()
