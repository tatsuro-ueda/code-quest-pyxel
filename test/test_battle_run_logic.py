from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_main_module():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType("main_for_battle_run_logic_test")
    module.__file__ = str((ROOT / "main.py").resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


class BattleRunLogicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = load_main_module()

    def make_game(self):
        game = self.main.Game.__new__(self.main.Game)
        game.vfx_timer = 0
        game.battle_phase = "menu"
        game.battle_menu = 3
        game.battle_text = ""
        game.battle_text_timer = 0
        game.battle_is_boss = False
        game.battle_is_professor = False
        game.battle_enemy = {"name": "Slime", "atk": 8, "def": 1}
        game.battle_enemy_hp = 10
        game.debug_mode = False
        game.player = {
            "hp": 20,
            "max_hp": 20,
            "def": 2,
            "armor": 0,
        }
        game.sfx = MagicMock()
        game._start_vfx = MagicMock()
        game._enemy_hit_scene_name = MagicMock(return_value="battle.normal.enemy_hit")
        game._dialog_text = MagicMock(side_effect=lambda scene_name, **_: scene_name)
        game._do_player_attack = MagicMock()
        game._do_enemy_attack = MagicMock()
        game._battle_victory = MagicMock()
        game._battle_defeat = MagicMock()
        game._btn = MagicMock(return_value=False)

        def btnp(buttons):
            return buttons == self.main.CONFIRM_BUTTONS

        game._btnp = MagicMock(side_effect=btnp)
        return game

    def test_failed_run_triggers_enemy_attack_after_fail_message(self):
        game = self.make_game()
        original_random = self.main.random.random
        self.main.random.random = lambda: 0.9
        try:
            self.main.Game.update_battle(game)
            self.assertEqual(game.battle_text, "battle.normal.run.fail")

            game._btnp = MagicMock(return_value=False)
            game.battle_text_timer = 1
            self.main.Game.update_battle(game)

            game._do_enemy_attack.assert_called_once_with()
        finally:
            self.main.random.random = original_random

    def test_successful_run_exits_battle_without_enemy_attack(self):
        game = self.make_game()
        original_random = self.main.random.random
        self.main.random.random = lambda: 0.1
        try:
            self.main.Game.update_battle(game)

            self.assertEqual(game.battle_text, "battle.normal.run.success")
            self.assertEqual(game.battle_phase, "result")
            game._do_enemy_attack.assert_not_called()
        finally:
            self.main.random.random = original_random


if __name__ == "__main__":
    unittest.main()
