# J18 Damage VFX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add screen flash VFX on damage dealt (white) and received (red) in battle, using frame-counting overlay.

**Architecture:** Two instance variables (`vfx_timer`, `vfx_type`) + a constant dict `VFX_FLASH` + two methods (`_start_vfx`, `_draw_vfx_overlay`). Triggers are 1-line additions to existing attack functions. Overlay draws at the end of `draw_battle`.

**Tech Stack:** Pyxel (built-in `rect`/`frame_count`), Python unittest with pyxel mock

---

### Task 1: Add VFX constants and state initialization

**Files:**
- Modify: `main.py:4586` (after `battle_text_timer` init)
- Modify: `main.py` constants area (near other game constants)

- [ ] **Step 1: Add VFX_FLASH constant**

Find the area near other battle-related constants (after `BATTLE_ATTACK_SCENES` or similar game data). Add:

```python
VFX_FLASH = {
    "flash_white": {"color": 7, "duration": 4},
    "flash_red":   {"color": 8, "duration": 6},
}
```

- [ ] **Step 2: Add vfx state to `__init__`**

In `Game.__init__`, after line `self.battle_text_timer = 0` (line 4586), add:

```python
        self.vfx_timer = 0
        self.vfx_type = ""
```

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat(vfx): add VFX_FLASH constant and vfx state variables"
```

---

### Task 2: Write failing tests for VFX behavior

**Files:**
- Create: `test/test_damage_vfx.py`

- [ ] **Step 1: Write the test file**

```python
"""Tests for J18 Damage VFX (screen flash on damage)."""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _setup_pyxel_mock():
    """pyxel モジュールをモックして main.py をインポート可能にする。"""
    if "pyxel" in sys.modules:
        return
    mock_pyxel = types.ModuleType("pyxel")
    mock_pyxel.init = MagicMock()
    mock_pyxel.run = MagicMock()
    mock_pyxel.load = MagicMock()
    mock_pyxel.quit = MagicMock()
    mock_pyxel.images = [MagicMock() for _ in range(4)]
    mock_tilemap = MagicMock()
    mock_tilemap.pget = MagicMock(return_value=(0, 0))
    mock_pyxel.tilemaps = [mock_tilemap for _ in range(8)]
    mock_pyxel.sounds = [MagicMock() for _ in range(64)]
    mock_pyxel.musics = [MagicMock() for _ in range(8)]
    mock_pyxel.Font = MagicMock()
    mock_pyxel.KEY_RETURN = 0
    mock_pyxel.KEY_SPACE = 0
    mock_pyxel.KEY_UP = 0
    mock_pyxel.KEY_DOWN = 0
    mock_pyxel.KEY_LEFT = 0
    mock_pyxel.KEY_RIGHT = 0
    mock_pyxel.KEY_ESCAPE = 0
    mock_pyxel.GAMEPAD1_BUTTON_A = 0
    mock_pyxel.GAMEPAD1_BUTTON_B = 0
    mock_pyxel.GAMEPAD1_BUTTON_DPAD_UP = 0
    mock_pyxel.GAMEPAD1_BUTTON_DPAD_DOWN = 0
    mock_pyxel.GAMEPAD1_BUTTON_DPAD_LEFT = 0
    mock_pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT = 0
    mock_pyxel.frame_count = 0
    mock_pyxel.rect = MagicMock()
    mock_pyxel.cls = MagicMock()
    mock_pyxel.pset = MagicMock()
    mock_pyxel.rectb = MagicMock()
    mock_pyxel.pal = MagicMock()
    mock_pyxel.text = MagicMock()
    sys.modules["pyxel"] = mock_pyxel


_setup_pyxel_mock()
import main as game_module


class TestVfxFlashConstant(unittest.TestCase):
    """VFX_FLASH 定数が正しく定義されている。"""

    def test_flash_white_exists(self):
        vfx = game_module.VFX_FLASH
        self.assertIn("flash_white", vfx)
        self.assertEqual(vfx["flash_white"]["color"], 7)
        self.assertGreater(vfx["flash_white"]["duration"], 0)

    def test_flash_red_exists(self):
        vfx = game_module.VFX_FLASH
        self.assertIn("flash_red", vfx)
        self.assertEqual(vfx["flash_red"]["color"], 8)
        self.assertGreater(vfx["flash_red"]["duration"], 0)


class TestStartVfx(unittest.TestCase):
    """_start_vfx がタイマーとタイプを正しく設定する。"""

    def _make_game(self):
        """Game.__init__ を回避して最小限のインスタンスを作る。"""
        g = object.__new__(game_module.Game)
        g.vfx_timer = 0
        g.vfx_type = ""
        return g

    def test_start_flash_white(self):
        g = self._make_game()
        g._start_vfx("flash_white")
        self.assertEqual(g.vfx_type, "flash_white")
        self.assertEqual(g.vfx_timer, game_module.VFX_FLASH["flash_white"]["duration"])

    def test_start_flash_red(self):
        g = self._make_game()
        g._start_vfx("flash_red")
        self.assertEqual(g.vfx_type, "flash_red")
        self.assertEqual(g.vfx_timer, game_module.VFX_FLASH["flash_red"]["duration"])

    def test_start_unknown_type_does_nothing(self):
        g = self._make_game()
        g._start_vfx("nonexistent")
        self.assertEqual(g.vfx_timer, 0)
        self.assertEqual(g.vfx_type, "")


class TestDrawVfxOverlay(unittest.TestCase):
    """_draw_vfx_overlay が正しくオーバーレイを描画する。"""

    def _make_game(self):
        g = object.__new__(game_module.Game)
        g.vfx_timer = 0
        g.vfx_type = ""
        return g

    def test_no_overlay_when_timer_zero(self):
        import pyxel
        pyxel.rect.reset_mock()
        g = self._make_game()
        g.vfx_timer = 0
        g._draw_vfx_overlay()
        pyxel.rect.assert_not_called()

    def test_overlay_drawn_on_even_frame(self):
        import pyxel
        pyxel.rect.reset_mock()
        g = self._make_game()
        g.vfx_timer = 4  # even → draw
        g.vfx_type = "flash_white"
        g._draw_vfx_overlay()
        pyxel.rect.assert_called_once_with(0, 0, 256, 256, 7)

    def test_no_overlay_on_odd_frame(self):
        import pyxel
        pyxel.rect.reset_mock()
        g = self._make_game()
        g.vfx_timer = 3  # odd → skip
        g.vfx_type = "flash_white"
        g._draw_vfx_overlay()
        pyxel.rect.assert_not_called()

    def test_red_flash_uses_color_8(self):
        import pyxel
        pyxel.rect.reset_mock()
        g = self._make_game()
        g.vfx_timer = 2  # even → draw
        g.vfx_type = "flash_red"
        g._draw_vfx_overlay()
        pyxel.rect.assert_called_once_with(0, 0, 256, 256, 8)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest test/test_damage_vfx.py -v`

Expected: FAIL — `VFX_FLASH` may exist (from Task 1) but `_start_vfx` and `_draw_vfx_overlay` are not yet defined.

- [ ] **Step 3: Commit**

```bash
git add test/test_damage_vfx.py
git commit -m "test(vfx): add failing tests for damage VFX flash"
```

---

### Task 3: Implement `_start_vfx` and `_draw_vfx_overlay`

**Files:**
- Modify: `main.py` (add two methods to `Game` class)

- [ ] **Step 1: Add `_start_vfx` method**

Add this method to the `Game` class, near the battle helper methods (after `_do_enemy_attack` around line 5613):

```python
    def _start_vfx(self, vfx_type):
        cfg = VFX_FLASH.get(vfx_type)
        if cfg:
            self.vfx_type = vfx_type
            self.vfx_timer = cfg["duration"]
```

- [ ] **Step 2: Add `_draw_vfx_overlay` method**

Add this method right before `draw_battle` (around line 6519):

```python
    def _draw_vfx_overlay(self):
        if self.vfx_timer <= 0:
            return
        cfg = VFX_FLASH.get(self.vfx_type)
        if not cfg:
            return
        if self.vfx_timer % 2 == 0:
            pyxel.rect(0, 0, 256, 256, cfg["color"])
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `python -m pytest test/test_damage_vfx.py -v`

Expected: All 7 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat(vfx): implement _start_vfx and _draw_vfx_overlay"
```

---

### Task 4: Wire triggers and integrate into battle loop

**Files:**
- Modify: `main.py:5536-5537` (`_do_player_attack`)
- Modify: `main.py:5600-5601` (`_do_enemy_attack`)
- Modify: `main.py:5437-5441` (spell attack section)
- Modify: `main.py:5377` (`update_battle` top)
- Modify: `main.py:6614` (`draw_battle` end)

- [ ] **Step 1: Add VFX trigger to `_do_player_attack`**

In `_do_player_attack`, after `self.sfx.play("attack")` (line 5536), add:

```python
        self._start_vfx("flash_white")
```

- [ ] **Step 2: Add VFX trigger to `_do_enemy_attack`**

In `_do_enemy_attack`, after `self.sfx.play("hit")` (line 5600), add:

```python
        self._start_vfx("flash_red")
```

- [ ] **Step 3: Add VFX trigger to spell attack**

In the spell_select confirm handler, after `self.sfx.play("magic")` (line 5438), add:

```python
                self._start_vfx("flash_white")
```

- [ ] **Step 4: Add VFX timer decrement to `update_battle`**

At the top of `update_battle` (line 5377), after `def update_battle(self):`, add:

```python
        if self.vfx_timer > 0:
            self.vfx_timer -= 1
```

- [ ] **Step 5: Add VFX overlay call to end of `draw_battle`**

At the very end of `draw_battle` (after line 6613, the last line of item_select drawing), add:

```python
        self._draw_vfx_overlay()
```

- [ ] **Step 6: Run all tests**

Run: `python -m pytest test/ -v`

Expected: All tests PASS (including existing tests and new VFX tests).

- [ ] **Step 7: Commit**

```bash
git add main.py
git commit -m "feat(vfx): wire damage flash triggers into battle loop"
```

---

### Task 5: Run full test suite and build verification

**Files:** None (verification only)

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest test/ -v`

Expected: All tests PASS.

- [ ] **Step 2: Build web release**

Run: `python tools/build_web_release.py`

Expected: Build succeeds without errors.

- [ ] **Step 3: Verify no regressions in git log**

Run: `git log origin/main..HEAD --oneline`

Expected: Only the commits from this feature branch, no extra commits.

- [ ] **Step 4: Final commit if any fixups needed, otherwise done**
