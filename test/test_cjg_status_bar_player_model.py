"""CJG/crash regression: StatusBar.draw() は game.player_model 経由で描画する。

根拠:
- docs/customer-jobs.md Make3「ガードレール: クラッシュで好循環が途絶」
- steering/done/20260425-player-dict-residue-crash-fix.md

StatusBar はマップ / メニュー / 戦闘 など**常時描画**の層。`game.player` dict が
廃止された後に `p = game.player` が残っていて AttributeError で即落ちしていた。
今後も `game.player` 参照が復活しないように、PlayerModel 経由で描画が完了する
ことを pyxel をスタブして確認する。
"""

from __future__ import annotations

import re
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class _FakePyxel:
    """StatusBar.draw が呼ぶ pyxel.rect / rectb を受け止めるだけのスタブ。"""

    def __init__(self) -> None:
        self.rect_calls: list[tuple] = []
        self.rectb_calls: list[tuple] = []

    def rect(self, x, y, w, h, col):
        self.rect_calls.append((x, y, w, h, col))

    def rectb(self, x, y, w, h, col):
        self.rectb_calls.append((x, y, w, h, col))


@dataclass
class _FakeMessages:
    calls: list[tuple] = field(default_factory=list)

    def text(self, x: int, y: int, s: str, col: int) -> None:
        self.calls.append((x, y, s, col))


@dataclass
class _FakeGame:
    player_model: Any = None
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    has_jp_font: bool = True
    debug_mode: bool = False


class StatusBarPlayerModelTest(unittest.TestCase):
    def setUp(self):
        from src.shared.state.player_model import PlayerModel

        self.PlayerModel = PlayerModel
        self.fake_pyxel = _FakePyxel()

    def _build_game(self):
        return _FakeGame(player_model=self.PlayerModel.new_game())

    def test_draw_completes_with_player_model_and_writes_level_hp_mp(self):
        from src.shared.ui import status_bar as status_bar_mod
        from src.shared.ui.status_bar import StatusBar

        game = self._build_game()
        bar = StatusBar(game=game)

        with patch.object(status_bar_mod, "pyxel", self.fake_pyxel):
            bar.draw()

        # rect が少なくとも 1 回呼ばれる（背景矩形 + HP/MP ゲージ）
        self.assertGreater(len(self.fake_pyxel.rect_calls), 0)
        # messages.text に レベル / HP / MP を含む文字列が渡される
        rendered = " / ".join(call[2] for call in game.messages.calls)
        self.assertIn("レベル", rendered)
        self.assertIn("HP", rendered)
        self.assertIn("MP", rendered)

    def test_draw_with_zero_max_hp_does_not_divide_by_zero(self):
        """max_hp=0 の不整合データでも ZeroDivisionError で落ちないこと。"""
        from src.shared.ui import status_bar as status_bar_mod
        from src.shared.ui.status_bar import StatusBar

        game = self._build_game()
        game.player_model.hp = 0
        game.player_model.max_hp = 0
        game.player_model.mp = 0
        game.player_model.max_mp = 0
        bar = StatusBar(game=game)

        with patch.object(status_bar_mod, "pyxel", self.fake_pyxel):
            bar.draw()  # 落ちないことが要件

    def test_draw_uses_english_zone_names_when_no_jp_font(self):
        from src.shared.ui import status_bar as status_bar_mod
        from src.shared.ui.status_bar import StatusBar

        game = self._build_game()
        game.has_jp_font = False
        bar = StatusBar(game=game)

        with patch.object(status_bar_mod, "pyxel", self.fake_pyxel):
            bar.draw()

        rendered = " / ".join(call[2] for call in game.messages.calls)
        # English ゾーン名のいずれかが含まれる
        self.assertTrue(
            any(word in rendered for word in ("Grasslands", "Logic", "Algo", "Desert", "Glitch")),
            f"英語ゾーン名が描画されていない: {rendered}",
        )


class StatusBarDungeonZoneTest(unittest.TestCase):
    """in_dungeon のときは "グリッチのどうくつ" が描画される（zone=4）。"""

    def test_in_dungeon_zone_name_is_glitch_cave_jp(self):
        from src.shared.ui import status_bar as status_bar_mod
        from src.shared.ui.status_bar import StatusBar

        game = _FakeGame(player_model=self._pm())
        game.player_model.in_dungeon = True
        bar = StatusBar(game=game)

        with patch.object(status_bar_mod, "pyxel", _FakePyxel()):
            bar.draw()

        rendered = " / ".join(call[2] for call in game.messages.calls)
        self.assertIn("グリッチのどうくつ", rendered)

    def test_in_dungeon_zone_name_is_glitch_cave_en(self):
        from src.shared.ui import status_bar as status_bar_mod
        from src.shared.ui.status_bar import StatusBar

        game = _FakeGame(player_model=self._pm(), has_jp_font=False)
        game.player_model.in_dungeon = True
        bar = StatusBar(game=game)

        with patch.object(status_bar_mod, "pyxel", _FakePyxel()):
            bar.draw()

        rendered = " / ".join(call[2] for call in game.messages.calls)
        self.assertIn("Glitch Cave", rendered)

    def _pm(self):
        from src.shared.state.player_model import PlayerModel

        return PlayerModel.new_game()


class StatusBarNoGamePlayerAttrTest(unittest.TestCase):
    """status_bar.py に `game.player` の dict 風アクセスが残っていないこと（grep ガード）。"""

    def test_status_bar_does_not_reference_game_player_dict(self):
        path = ROOT / "src" / "shared" / "ui" / "status_bar.py"
        text = path.read_text(encoding="utf-8")

        # `game.player` 単体参照（`game.player_model` は除外）
        matches = [
            line
            for line in text.splitlines()
            if re.search(r"game\.player(?!_model)(?:[^_a-zA-Z0-9]|$)", line)
        ]
        self.assertEqual(
            matches,
            [],
            f"status_bar.py で game.player dict 参照が残っている: {matches}",
        )


if __name__ == "__main__":
    unittest.main()
