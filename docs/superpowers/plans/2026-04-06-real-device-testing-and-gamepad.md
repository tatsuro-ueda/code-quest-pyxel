# Real Device Testing And Gamepad Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Pyxel export playable on a phone over the local network and wire Pyxel's standard virtual gamepad buttons into the current input flow.

**Architecture:** Keep `pyxel.html` as the exported playback artifact, add a tiny LAN preview server under `tools/`, and introduce a small input-binding helper under `src/` so `main.py` can accept both keyboard and `GAMEPAD1_BUTTON_*` without spreading duplicate checks everywhere.

**Tech Stack:** Python 3, Pyxel WASM export, `unittest`, standard library `http.server`

---

### Task 1: Define And Test Input Bindings

**Files:**
- Create: `src/input_bindings.py`
- Create: `test/test_input_bindings.py`
- Modify: `main.py`

- [ ] **Step 1: Write the failing tests**

```python
from src.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    UP_BUTTONS,
    any_btn,
    any_btnp,
)


class _FakePyxel:
    def __init__(self, held=(), pressed=()):
        for name in {
            *UP_BUTTONS,
            *DOWN_BUTTONS,
            *LEFT_BUTTONS,
            *RIGHT_BUTTONS,
            *CONFIRM_BUTTONS,
            *CANCEL_BUTTONS,
        }:
            setattr(self, name, name)
        self._held = set(held)
        self._pressed = set(pressed)

    def btn(self, code):
        return code in self._held

    def btnp(self, code):
        return code in self._pressed


def test_any_btn_accepts_keyboard_or_gamepad():
    assert any_btn(_FakePyxel(held={"KEY_UP"}), UP_BUTTONS)
    assert any_btn(_FakePyxel(held={"GAMEPAD1_BUTTON_DPAD_UP"}), UP_BUTTONS)


def test_any_btnp_accepts_a_and_b_buttons():
    assert any_btnp(_FakePyxel(pressed={"GAMEPAD1_BUTTON_A"}), CONFIRM_BUTTONS)
    assert any_btnp(_FakePyxel(pressed={"GAMEPAD1_BUTTON_B"}), CANCEL_BUTTONS)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test.test_input_bindings -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.input_bindings'`

- [ ] **Step 3: Write minimal implementation**

```python
UP_BUTTONS = ("KEY_UP", "GAMEPAD1_BUTTON_DPAD_UP")
DOWN_BUTTONS = ("KEY_DOWN", "GAMEPAD1_BUTTON_DPAD_DOWN")
LEFT_BUTTONS = ("KEY_LEFT", "GAMEPAD1_BUTTON_DPAD_LEFT")
RIGHT_BUTTONS = ("KEY_RIGHT", "GAMEPAD1_BUTTON_DPAD_RIGHT")
CONFIRM_BUTTONS = ("KEY_Z", "KEY_RETURN", "GAMEPAD1_BUTTON_A")
CANCEL_BUTTONS = ("KEY_X", "GAMEPAD1_BUTTON_B")


def any_btn(pyxel_module, button_names):
    return any(pyxel_module.btn(getattr(pyxel_module, name)) for name in button_names)


def any_btnp(pyxel_module, button_names):
    return any(pyxel_module.btnp(getattr(pyxel_module, name)) for name in button_names)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test.test_input_bindings -v`
Expected: PASS

- [ ] **Step 5: Wire `main.py` to the helper and re-check**

Use `any_btn` / `any_btnp` for:
- title confirm
- map movement
- map menu open
- battle/menu/message/town/ending confirm-cancel
- debug sequence detection with D-pad up/down

Run: `python -m unittest test.test_dialogue_integration test.test_input_bindings -v`
Expected: PASS and `main.py` now references `GAMEPAD1_BUTTON_A`, `GAMEPAD1_BUTTON_B`, and D-pad bindings through the helper.

### Task 2: Add A Repeatable LAN Preview Path

**Files:**
- Create: `tools/serve_pyxel_preview.py`
- Create: `test/test_preview_server.py`
- Create: `docs/requirements/98-real-device-testing.md`

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

from tools.serve_pyxel_preview import build_preview_urls


def test_build_preview_urls_prefers_pyxel_html():
    root = Path("/tmp/block-quest")
    urls = build_preview_urls("10.0.0.5", 8000, root)
    assert urls["pyxel"] == "http://10.0.0.5:8000/pyxel.html"
    assert urls["index"] == "http://10.0.0.5:8000/index.html"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test.test_preview_server -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools.serve_pyxel_preview'`

- [ ] **Step 3: Write minimal implementation**

```python
def build_preview_urls(host_ip, port, _root):
    base = f"http://{host_ip}:{port}"
    return {
        "pyxel": f"{base}/pyxel.html",
        "index": f"{base}/index.html",
    }
```

Then add a `main()` that:
- serves the repo root with `http.server.ThreadingHTTPServer`
- binds `0.0.0.0`
- prints localhost and LAN URLs for `pyxel.html`

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test.test_preview_server -v`
Expected: PASS

- [ ] **Step 5: Document the manual phone test flow**

Write `docs/requirements/98-real-device-testing.md` with:
- command to start the server
- same-Wi-Fi requirement
- the `pyxel.html` URL as the primary target
- a short checklist: title start, map movement, A confirm, B menu/cancel

### Task 3: Final Verification

**Files:**
- Verify: `main.py`
- Verify: `src/input_bindings.py`
- Verify: `tools/serve_pyxel_preview.py`
- Verify: `test/test_input_bindings.py`
- Verify: `test/test_preview_server.py`
- Verify: `docs/requirements/98-real-device-testing.md`

- [ ] **Step 1: Run focused tests**

Run: `python -m unittest test.test_input_bindings test.test_preview_server -v`
Expected: PASS

- [ ] **Step 2: Run the full suite**

Run: `python -m unittest discover -s test -p 'test_*.py' -v`
Expected: PASS

- [ ] **Step 3: Run compile checks**

Run: `python -m py_compile main.py src/input_bindings.py tools/serve_pyxel_preview.py test/test_input_bindings.py test/test_preview_server.py`
Expected: no output

- [ ] **Step 4: Smoke-print the preview URL**

Run: `python tools/serve_pyxel_preview.py --host 0.0.0.0 --port 8000`
Expected: console prints localhost and LAN URLs including `http://<LAN-IP>:8000/pyxel.html`

- [ ] **Step 5: Commit**

```bash
git add main.py src/input_bindings.py tools/serve_pyxel_preview.py \
  test/test_input_bindings.py test/test_preview_server.py \
  docs/requirements/98-real-device-testing.md \
  docs/superpowers/plans/2026-04-06-real-device-testing-and-gamepad.md
git commit -m "feat: add phone preview and virtual gamepad support"
```
