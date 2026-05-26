"""CJG/menu: ステータス画面に次レベルまでの必要経験値を表示する。

根拠:
- docs/product-requirements-battle.md（レベルアップ判定が正常に動作する）
- steering/2026年5月26日（ブロクエ）レベルが上がらない.png

`Lv2 / EXP102` の証跡はロジック不良ではなく、既存仕様 `exp_for_level(3)=108`
にまだ届いていない状態だった。子どもからは「上がらない」と見えやすいので、
menu の status panel に残り必要 EXP を明示し、次のレベルまであといくつかを
その場で読めるようにする。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.menu.model import MenuModel
from src.scenes.menu.presenter import MenuPresenter
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeTextFormat:
    use_jp: bool = True

    def t(self, jp: str, en: str) -> str:
        return jp if self.use_jp else en

    def name(self, text: str) -> str:
        return text


@dataclass
class _FakeGame:
    has_jp_font: bool = True
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    text_fmt: _FakeTextFormat = field(default_factory=_FakeTextFormat)


class MenuStatusPanelNextLevelTest(unittest.TestCase):
    def test_status_panel_shows_remaining_exp_to_next_level(self):
        game = _FakeGame()
        game.player_model.lv = 2
        game.player_model.exp = 102
        model = MenuModel()
        model.sub = "status"
        presenter = MenuPresenter(model=model)

        vm = presenter.build_view_model(presenter.build_labels(game), game)

        self.assertIsNotNone(vm.sub_panel)
        lines = [row.text for row in vm.sub_panel.rows]
        self.assertIn("レベル 2  けいけん 102", lines)
        self.assertIn("つぎまで 6", lines)


if __name__ == "__main__":
    unittest.main()
