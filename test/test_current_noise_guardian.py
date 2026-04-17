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
    module = types.ModuleType("main_for_noise_guardian_test")
    module.__file__ = str((ROOT / "main.py").resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


class CurrentNoiseGuardianTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = load_main_module()

    def test_noise_guardian_is_not_in_current_normal_encounters(self):
        zone2_names = {enemy["name"] for enemy in self.main.ZONE_ENEMIES[2]}
        self.assertNotIn("ノイズガーディアン", zone2_names)

    def test_noise_guardian_event_battle_still_starts(self):
        game = self.main.Game.__new__(self.main.Game)
        game._start_battle = MagicMock()
        game._dialog_text = MagicMock(return_value="boss.noise_guardian.intro")
        game._noise_guardian_battle = False
        game.battle_text = ""

        self.main.Game._start_noise_guardian_battle(game)

        game._start_battle.assert_called_once_with(
            self.main.NOISE_GUARDIAN_DATA,
            is_glitch_lord=False,
        )
        self.assertTrue(game._noise_guardian_battle)
        self.assertEqual(game.battle_text, "boss.noise_guardian.intro")


if __name__ == "__main__":
    unittest.main()
