"""CJG/splash: スプラッシュ画面が自動遷移と任意キーで title に進む。

根拠:
- docs/customer-journeys.md CJ 冒頭「URL を開くだけで即プレイ」想定（splash は
  短く済ませて title に自動遷移するのが体験条件）
- docs/customer-jobs.md Job4（ゲームを楽しむ、待ち時間で離脱させない）

SplashScene.update は 90 フレームで自動遷移 or 任意キー即スキップの 2 経路。
pyxel stub 下で frame 累積と state 変化だけを固定化する。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.splash.scene import SplashScene


@dataclass
class _FakeInputState:
    pressed: set[tuple[int, ...]] = field(default_factory=set)

    def btnp(self, buttons) -> bool:
        # 配列型ボタン群をキーにまとめて一致チェック
        key = tuple(buttons) if hasattr(buttons, "__iter__") else (buttons,)
        return key in self.pressed

    def press(self, buttons):
        key = tuple(buttons) if hasattr(buttons, "__iter__") else (buttons,)
        self.pressed.add(key)


@dataclass
class _FakeGame:
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    state: str = "splash"


class SplashAutoAdvanceTest(unittest.TestCase):
    """90 frame 経過で state が title に変わる。それ未満では splash のまま。"""

    def test_frame_under_threshold_stays_on_splash(self):
        game = _FakeGame()
        scene = SplashScene(game=game)

        for _ in range(89):
            scene.update()

        self.assertEqual(game.state, "splash")
        self.assertEqual(scene.model.frame, 89)

    def test_reaching_90_frames_auto_advances_to_title(self):
        game = _FakeGame()
        scene = SplashScene(game=game)

        for _ in range(90):
            scene.update()

        self.assertEqual(game.state, "title")


class SplashKeySkipTest(unittest.TestCase):
    """CONFIRM / CANCEL いずれかが押されたら即 title に進む。"""

    def test_confirm_skips_to_title_immediately(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        game.input_state.press(CONFIRM_BUTTONS)
        scene = SplashScene(game=game)

        scene.update()  # 1 フレームでも遷移する

        self.assertEqual(game.state, "title")

    def test_cancel_also_skips_to_title(self):
        from src.shared.services.input_bindings import CANCEL_BUTTONS

        game = _FakeGame()
        game.input_state.press(CANCEL_BUTTONS)
        scene = SplashScene(game=game)

        scene.update()

        self.assertEqual(game.state, "title")


class SplashNoGameGuardTest(unittest.TestCase):
    """game が None でも update が crash しない（スケルトン状態の安全網）。"""

    def test_update_without_game_is_noop(self):
        scene = SplashScene(game=None)
        scene.update()  # 例外を投げなければ合格

        self.assertEqual(scene.model.frame, 0)


if __name__ == "__main__":
    unittest.main()
