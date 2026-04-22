from __future__ import annotations

import sys
import unittest
from pathlib import Path


PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))


class FakePyxel:
    def __init__(self, held=(), pressed=()):
        self._held = set(held)
        self._pressed = set(pressed)

    def __getattr__(self, name):
        return name

    def btn(self, code):
        return code in self._held

    def btnp(self, code):
        return code in self._pressed


class InputBindingsTest(unittest.TestCase):
    def _load_module(self):
        from src.shared.services.input_bindings import (
            CANCEL_BUTTONS,
            CONFIRM_BUTTONS,
            DOWN_BUTTONS,
            InputStateTracker,
            LEFT_BUTTONS,
            RIGHT_BUTTONS,
            TITLE_START_BUTTONS,
            UP_BUTTONS,
            any_btn,
            any_btnp,
        )

        return {
            "UP_BUTTONS": UP_BUTTONS,
            "DOWN_BUTTONS": DOWN_BUTTONS,
            "LEFT_BUTTONS": LEFT_BUTTONS,
            "RIGHT_BUTTONS": RIGHT_BUTTONS,
            "CONFIRM_BUTTONS": CONFIRM_BUTTONS,
            "CANCEL_BUTTONS": CANCEL_BUTTONS,
            "TITLE_START_BUTTONS": TITLE_START_BUTTONS,
            "InputStateTracker": InputStateTracker,
            "any_btn": any_btn,
            "any_btnp": any_btnp,
        }

    def test_any_btn_accepts_keyboard_or_gamepad_dpad(self):
        module = self._load_module()
        any_btn = module["any_btn"]
        up_buttons = module["UP_BUTTONS"]

        self.assertTrue(any_btn(FakePyxel(held={"KEY_UP"}), up_buttons))
        self.assertTrue(any_btn(FakePyxel(held={"GAMEPAD1_BUTTON_DPAD_UP"}), up_buttons))

    def test_any_btnp_accepts_console_style_confirm_and_cancel_buttons(self):
        module = self._load_module()
        any_btnp = module["any_btnp"]

        self.assertTrue(
            any_btnp(FakePyxel(pressed={"KEY_SPACE"}), module["CONFIRM_BUTTONS"])
        )
        self.assertTrue(
            any_btnp(FakePyxel(pressed={"GAMEPAD1_BUTTON_B"}), module["CONFIRM_BUTTONS"])
        )
        self.assertTrue(
            any_btnp(FakePyxel(pressed={"KEY_ESCAPE"}), module["CANCEL_BUTTONS"])
        )
        self.assertTrue(
            any_btnp(FakePyxel(pressed={"GAMEPAD1_BUTTON_A"}), module["CANCEL_BUTTONS"])
        )

    def test_title_start_buttons_accept_gamepad_start(self):
        module = self._load_module()
        any_btnp = module["any_btnp"]

        self.assertTrue(
            any_btnp(
                FakePyxel(pressed={"GAMEPAD1_BUTTON_START"}),
                module["TITLE_START_BUTTONS"],
            )
        )

    def test_bindings_include_expected_gamepad_constants(self):
        module = self._load_module()

        self.assertIn("GAMEPAD1_BUTTON_DPAD_LEFT", module["LEFT_BUTTONS"])
        self.assertIn("GAMEPAD1_BUTTON_DPAD_RIGHT", module["RIGHT_BUTTONS"])
        self.assertIn("GAMEPAD1_BUTTON_DPAD_DOWN", module["DOWN_BUTTONS"])
        self.assertIn("KEY_SPACE", module["CONFIRM_BUTTONS"])
        self.assertIn("GAMEPAD1_BUTTON_B", module["CONFIRM_BUTTONS"])
        self.assertIn("KEY_ESCAPE", module["CANCEL_BUTTONS"])
        self.assertIn("GAMEPAD1_BUTTON_A", module["CANCEL_BUTTONS"])
        self.assertIn("GAMEPAD1_BUTTON_BACK", module["CANCEL_BUTTONS"])
        self.assertIn("GAMEPAD1_BUTTON_START", module["TITLE_START_BUTTONS"])
        self.assertNotIn("GAMEPAD1_BUTTON_START", module["CONFIRM_BUTTONS"])

    def test_input_state_tracker_emits_pressed_once_for_confirm(self):
        module = self._load_module()
        tracker = module["InputStateTracker"]()
        pyxel = FakePyxel()

        tracker.update(pyxel)
        pyxel._held = {"GAMEPAD1_BUTTON_B"}
        tracker.update(pyxel)
        self.assertTrue(tracker.btn(module["CONFIRM_BUTTONS"]))
        self.assertTrue(tracker.btnp(module["CONFIRM_BUTTONS"]))

        tracker.update(pyxel)
        self.assertTrue(tracker.btn(module["CONFIRM_BUTTONS"]))
        self.assertFalse(tracker.btnp(module["CONFIRM_BUTTONS"]))

    def test_input_state_tracker_treats_start_as_title_only(self):
        module = self._load_module()
        tracker = module["InputStateTracker"]()
        pyxel = FakePyxel()

        tracker.update(pyxel)
        pyxel._held = {"GAMEPAD1_BUTTON_START"}
        tracker.update(pyxel)
        self.assertTrue(tracker.btnp(module["TITLE_START_BUTTONS"]))
        self.assertFalse(tracker.btn(module["CONFIRM_BUTTONS"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
