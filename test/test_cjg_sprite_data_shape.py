"""CJG/sprite_data: すべてのスプライト定数が 16x16 の矩形 grid。

根拠:
- docs/product-requirements-platform.md（Pyxel のスプライトサイズ）

Pyxel Code Maker で扱うスプライトは 16x16 ピクセルが基本。
全ての SPRITE（HERO_*/SLIME_*/BOSS_GLITCH 等）が 16 行 × 16 列になっていれば、
描画時に範囲外アクセスで落ちない。全てのピクセル値は 0〜15（Pyxel パレット）。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.constants import sprite_data as S


def _iter_sprite_constants():
    for name in dir(S):
        if name.startswith("_"):
            continue
        value = getattr(S, name)
        if isinstance(value, list) and value and isinstance(value[0], list):
            yield name, value


class SpriteShapeTest(unittest.TestCase):
    def test_every_sprite_has_16_rows(self):
        for name, sprite in _iter_sprite_constants():
            with self.subTest(sprite=name):
                self.assertEqual(len(sprite), 16, f"{name} が {len(sprite)} 行（16 行期待）")

    def test_every_sprite_has_16_columns(self):
        for name, sprite in _iter_sprite_constants():
            for row_idx, row in enumerate(sprite):
                with self.subTest(sprite=name, row=row_idx):
                    self.assertEqual(
                        len(row),
                        16,
                        f"{name}[{row_idx}] が {len(row)} 列（16 列期待）",
                    )

    def test_every_pixel_value_is_0_to_15(self):
        for name, sprite in _iter_sprite_constants():
            for row_idx, row in enumerate(sprite):
                for col_idx, value in enumerate(row):
                    with self.subTest(sprite=name, row=row_idx, col=col_idx):
                        self.assertIsInstance(value, int)
                        self.assertGreaterEqual(value, 0)
                        self.assertLessEqual(value, 15)

    def test_at_least_hero_and_boss_sprites_exist(self):
        """主要スプライトが存在する。"""
        self.assertTrue(hasattr(S, "HERO_DOWN"))
        self.assertTrue(hasattr(S, "BOSS_GLITCH"))


if __name__ == "__main__":
    unittest.main()
