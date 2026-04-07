from __future__ import annotations


UP_BUTTONS = ("KEY_UP", "GAMEPAD1_BUTTON_DPAD_UP")
DOWN_BUTTONS = ("KEY_DOWN", "GAMEPAD1_BUTTON_DPAD_DOWN")
LEFT_BUTTONS = ("KEY_LEFT", "GAMEPAD1_BUTTON_DPAD_LEFT")
RIGHT_BUTTONS = ("KEY_RIGHT", "GAMEPAD1_BUTTON_DPAD_RIGHT")
CONFIRM_BUTTONS = ("KEY_Z", "KEY_SPACE", "KEY_RETURN", "GAMEPAD1_BUTTON_A")
CANCEL_BUTTONS = ("KEY_X", "KEY_ESCAPE", "GAMEPAD1_BUTTON_B", "GAMEPAD1_BUTTON_BACK")
TITLE_START_BUTTONS = CONFIRM_BUTTONS + ("GAMEPAD1_BUTTON_START",)

BUTTON_GROUPS = (
    UP_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    CONFIRM_BUTTONS,
    CANCEL_BUTTONS,
    TITLE_START_BUTTONS,
)


def any_btn(pyxel_module, button_names) -> bool:
    return any(pyxel_module.btn(getattr(pyxel_module, name)) for name in button_names)


def any_btnp(pyxel_module, button_names) -> bool:
    return any(pyxel_module.btnp(getattr(pyxel_module, name)) for name in button_names)


class InputStateTracker:
    def __init__(self):
        self._held = {button_names: False for button_names in BUTTON_GROUPS}
        self._pressed = {button_names: False for button_names in BUTTON_GROUPS}

    def update(self, pyxel_module):
        next_held = {}
        next_pressed = {}
        for button_names in BUTTON_GROUPS:
            held = any_btn(pyxel_module, button_names)
            next_held[button_names] = held
            next_pressed[button_names] = held and not self._held[button_names]
        self._held = next_held
        self._pressed = next_pressed

    def btn(self, button_names) -> bool:
        return self._held.get(button_names, False)

    def btnp(self, button_names) -> bool:
        return self._pressed.get(button_names, False)
