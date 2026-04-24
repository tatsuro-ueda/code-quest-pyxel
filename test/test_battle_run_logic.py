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


def _pm_from_dict(d):
    from src.shared.state.player_model import PlayerModel, PlayerItem
    pm = PlayerModel()
    for k, v in d.items():
        attr = "defense" if k == "def" else k
        if attr == "items":
            v = [PlayerItem(id=i["id"], qty=i["qty"]) for i in v]
        setattr(pm, attr, v)
    return pm


class BattleRunLogicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = load_main_module()

    def make_game(self):
        from src.scenes.battle.scene import BattleScene
        from src.shared.services.message_display import MessageDisplay
        from src.shared.services.vfx import VfxSystem
        from src.shared.services.input_bindings import InputStateTracker
        game = self.main.Game.__new__(self.main.Game)
        game.vfx = VfxSystem(game=game)
        game.input_state = InputStateTracker()
        game.debug_mode = False
        game.player_model = _pm_from_dict({
            "hp": 20,
            "max_hp": 20,
            "def": 2,
            "armor": 0,
        })
        game.sfx = MagicMock()
        game._start_vfx = MagicMock()
        game.messages = MessageDisplay(game=game)
        game.messages.dialog_text = MagicMock(side_effect=lambda scene_name, **_: scene_name)
        game.input_state.btn = MagicMock(return_value=False)

        def btnp(buttons):
            return buttons == self.main.CONFIRM_BUTTONS

        game.input_state.btnp = MagicMock(side_effect=btnp)
        game.battle_scene = BattleScene(game=game)
        m = game.battle_scene.model
        m.menu = 3
        m.enemy = {"name": "Slime", "atk": 8, "def": 1}
        m.enemy_hp = 10
        game.battle_scene.do_player_attack = MagicMock()
        game.battle_scene.do_enemy_attack = MagicMock()
        game.battle_scene.victory = MagicMock()
        game.battle_scene.defeat = MagicMock()
        game.battle_scene.enemy_hit_scene_name = MagicMock(return_value="battle.normal.enemy_hit")
        return game

    def test_failed_run_triggers_enemy_attack_after_fail_message(self):
        game = self.make_game()
        m = game.battle_scene.model
        original_random = self.main.random.random
        self.main.random.random = lambda: 0.9
        try:
            game.battle_scene.update()
            self.assertEqual(m.text, "battle.normal.run.fail")

            game.input_state.btnp = MagicMock(return_value=False)
            m.text_timer = 1
            game.battle_scene.update()

            game.battle_scene.do_enemy_attack.assert_called_once_with()
        finally:
            self.main.random.random = original_random

    def test_successful_run_exits_battle_without_enemy_attack(self):
        game = self.make_game()
        m = game.battle_scene.model
        original_random = self.main.random.random
        self.main.random.random = lambda: 0.1
        try:
            game.battle_scene.update()

            self.assertEqual(m.text, "battle.normal.run.success")
            self.assertEqual(m.phase, "result")
            game.battle_scene.do_enemy_attack.assert_not_called()
        finally:
            self.main.random.random = original_random


if __name__ == "__main__":
    unittest.main()
