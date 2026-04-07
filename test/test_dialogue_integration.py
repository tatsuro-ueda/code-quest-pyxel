from __future__ import annotations

import unittest
from pathlib import Path


PYXEL_ROOT = Path(__file__).resolve().parent.parent


class DialogueIntegrationTest(unittest.TestCase):
    def test_main_references_scene_names_instead_of_runtime_text(self):
        main_text = (PYXEL_ROOT / "main.py").read_text(encoding="utf-8")
        landmark_text = (PYXEL_ROOT / "src" / "landmark_events.py").read_text(
            encoding="utf-8"
        )

        for expected in (
            "find_landmark_event",
            "landmarkTreeSeen",
            "landmarkTowerSeen",
            "town.start.entry",
            "town.logic.entry",
            "town.algo.entry",
            "castle.professor.entry",
            "dungeon.glitch.enter",
            "dungeon.glitch.exit",
            "battle.normal.run.success",
            "battle.normal.run.fail",
            "battle.normal.item.heal",
            "battle.normal.item.mp_heal",
            "battle.normal.enemy_hit.sequential",
            "battle.normal.victory.early",
            "battle.normal.victory.mid",
            "battle.normal.victory.late",
            "battle.normal.defeat",
            "ending.main.line01",
        ):
            self.assertIn(expected, main_text)

        for scene_name in (
            "landmark.tree.first",
            "landmark.tower.first",
        ):
            self.assertIn(scene_name, landmark_text)

    def test_main_uses_shared_input_bindings_for_keyboard_and_gamepad(self):
        main_text = (PYXEL_ROOT / "main.py").read_text(encoding="utf-8")

        for expected in (
            "from src.input_bindings import",
            "UP_BUTTONS",
            "DOWN_BUTTONS",
            "LEFT_BUTTONS",
            "RIGHT_BUTTONS",
            "CONFIRM_BUTTONS",
            "CANCEL_BUTTONS",
            "TITLE_START_BUTTONS",
            "InputStateTracker",
            "any_btn",
        ):
            self.assertIn(expected, main_text)

    def test_main_uses_audio_manager_for_bgm(self):
        main_text = (PYXEL_ROOT / "main.py").read_text(encoding="utf-8")

        for expected in (
            "from src.audio_system import",
            "AudioManager",
            "choose_bgm_scene",
            "self.audio = AudioManager(pyxel)",
            "self.audio.play_scene(",
        ):
            self.assertIn(expected, main_text)

    def test_main_no_longer_hardcodes_dialogue_body_text(self):
        text = (PYXEL_ROOT / "main.py").read_text(encoding="utf-8")

        for phrase in (
            "はじめの村へようこそ！",
            "ロジックタウンだ。",
            "アルゴリズムの街。",
            "町に立ち寄り、装備を整えよう。",
            "世界樹だ。なぜか落ち着く。気持ちが、考えが、自由だ。",
            "通信塔だ。声が流れてくる。",
            "グリッチのサーバーに侵入した",
            "サーバーから脱出した。",
            "うまく逃げ切れた！",
            "逃げられない！",
            "まだ整理できていない…コインが半分になった。",
            "おめでとう！",
            "魔王グリッチを倒した！",
        ):
            self.assertNotIn(phrase, text)

        self.assertNotIn("ATTACK_TEXTS = [", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
