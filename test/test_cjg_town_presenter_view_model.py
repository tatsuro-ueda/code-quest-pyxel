"""CJG/town: TownPresenter.build_menu_view_model が正しい ViewModel を返す。

根拠:
- docs/framework-rule.md M2-2（ViewModel は Presenter で組み立てる）
- docs/product-requirements-narrative.md（町メニューの見た目）

build_menu_view_model は:
- title は "まちメニュー" (JP) or "TOWN MENU" (EN)
- labels は TOWN_MENU_LABELS（JP）or TOWN_MENU_LABELS_EN（EN）を基底に、
  「やどや」/「INN」のみ宿代を併記した形（やどや（{cost}G） / INN ({cost}G)）
- cursor は TownModel.menu_cursor
- gold は PlayerModel.gold
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.town.model import TownModel
from src.scenes.town.presenter import TownPresenter
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeTextFormat:
    use_jp: bool = True

    def t(self, jp: str, en: str) -> str:
        return jp if self.use_jp else en


@dataclass
class _FakeGame:
    has_jp_font: bool = True
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    text_fmt: _FakeTextFormat = field(default_factory=_FakeTextFormat)


def _expected_labels(base: tuple[str, ...], inn_cost: int) -> tuple[str, ...]:
    """基底ラベルから、「やどや」/「INN」だけ宿代併記した期待値を組み立てる。"""

    def fmt(label: str) -> str:
        if label == "やどや":
            return f"やどや（{inn_cost}G）"
        if label == "INN":
            return f"INN ({inn_cost}G)"
        return label

    return tuple(fmt(label) for label in base)


class TownMenuViewModelTest(unittest.TestCase):
    def test_jp_mode_uses_japanese_labels(self):
        from src.shared.constants.game_config import TOWN_MENU_LABELS

        game = _FakeGame()
        presenter = TownPresenter(model=TownModel(), game=game)
        inn_cost = presenter._get_inn_cost()

        vm = presenter.build_menu_view_model()

        self.assertEqual(vm.title, "まちメニュー")
        self.assertEqual(tuple(vm.labels), _expected_labels(TOWN_MENU_LABELS, inn_cost))

    def test_en_mode_uses_english_labels(self):
        from src.shared.constants.game_config import TOWN_MENU_LABELS_EN

        game = _FakeGame(has_jp_font=False)
        game.text_fmt.use_jp = False
        presenter = TownPresenter(model=TownModel(), game=game)
        inn_cost = presenter._get_inn_cost()

        vm = presenter.build_menu_view_model()

        self.assertEqual(vm.title, "TOWN MENU")
        self.assertEqual(tuple(vm.labels), _expected_labels(TOWN_MENU_LABELS_EN, inn_cost))

    def test_cursor_comes_from_model(self):
        game = _FakeGame()
        model = TownModel()
        model.menu_cursor = 3
        presenter = TownPresenter(model=model, game=game)

        vm = presenter.build_menu_view_model()

        self.assertEqual(vm.cursor, 3)

    def test_gold_comes_from_player_model(self):
        game = _FakeGame()
        game.player_model.gold = 12345
        presenter = TownPresenter(model=TownModel(), game=game)

        vm = presenter.build_menu_view_model()

        self.assertEqual(vm.gold, 12345)


if __name__ == "__main__":
    unittest.main()
