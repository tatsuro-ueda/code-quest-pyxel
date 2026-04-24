"""CJG/text_format: 日本語フォント無し環境で英語フォールバックが効く。

根拠:
- docs/customer-journeys.md（スマホ / Code Maker 環境でも壊れずプレイできる）
- docs/product-requirements-platform.md（フォント読めなくても進行できる）

BDF フォントが無いと game.has_jp_font=False になる。そのときは
日本語ラベルの代わりに英語ラベルを使う。NAME_EN_MAP に載ってないものは
素通しで返す（訳抜けの安全網）。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.text_format import NAME_EN_MAP, TextFormat, name_en


@dataclass
class _FakeGame:
    has_jp_font: bool = True


class NameEnMapTest(unittest.TestCase):
    def test_known_enemy_translates(self):
        self.assertEqual(name_en("10ほスライム"), "10-step Slime")

    def test_known_weapon_translates(self):
        self.assertEqual(name_en("コードエディタ"), "Code Editor")

    def test_known_armor_translates(self):
        self.assertEqual(name_en("きほんのちしき"), "Basic Knowledge")

    def test_unknown_string_passes_through(self):
        self.assertEqual(name_en("アルゴリズムタワー"), "アルゴリズムタワー")

    def test_empty_string_passes_through(self):
        self.assertEqual(name_en(""), "")

    def test_every_mapped_value_is_ascii_only(self):
        """英語訳先が ASCII 範囲に収まる（BDF なし環境では Latin フォントで描画する想定）。"""
        for jp, en in NAME_EN_MAP.items():
            with self.subTest(jp=jp):
                try:
                    en.encode("ascii")
                except UnicodeEncodeError:
                    self.fail(f"`{jp}` → `{en}` に非 ASCII 文字が含まれる")


class TextFormatTest(unittest.TestCase):
    def test_jp_mode_returns_japanese(self):
        fmt = TextFormat(game=_FakeGame(has_jp_font=True))

        self.assertEqual(fmt.t("まちメニュー", "TOWN MENU"), "まちメニュー")
        self.assertEqual(fmt.name("10ほスライム"), "10ほスライム")

    def test_en_mode_returns_english(self):
        fmt = TextFormat(game=_FakeGame(has_jp_font=False))

        self.assertEqual(fmt.t("まちメニュー", "TOWN MENU"), "TOWN MENU")
        self.assertEqual(fmt.name("10ほスライム"), "10-step Slime")

    def test_en_mode_falls_through_for_unknown_names(self):
        """NAME_EN_MAP に無い名前もそのまま使われる（未翻訳で落ちない）。"""
        fmt = TextFormat(game=_FakeGame(has_jp_font=False))

        self.assertEqual(fmt.name("みしらぬなまえ"), "みしらぬなまえ")


if __name__ == "__main__":
    unittest.main()
