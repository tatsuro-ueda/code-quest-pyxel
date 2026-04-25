from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.ai_help.model import AiHelpModel
from src.scenes.ai_help.presenter import AiHelpPresenter
from src.scenes.ai_help.view import AiHelpView
from src.shared.services.input_bindings import CONFIRM_BUTTONS, CANCEL_BUTTONS


@dataclass
class AiHelpScene:
    """AI ヘルプ画面（P1-G9 で Game から 4 メソッドを取り込み）。"""

    name: str = "ai_help"
    model: AiHelpModel = field(default_factory=AiHelpModel)
    view: AiHelpView = field(default_factory=AiHelpView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = AiHelpPresenter(self.model)

    def enter(self) -> None:
        """AI ヘルプ画面に入る。"""
        game = self.game
        self.model.status = self._try_open_ai_chat()
        game.state = "ai_help"

    def _try_open_ai_chat(self) -> str:
        """環境に応じて AI を呼ぶ手段を試す。"""
        try:
            import js  # type: ignore
            try:
                js.window.open("https://claude.ai/new", "_blank")
                return "あたらしいタブで Claude をひらきました"
            except Exception:
                return "Claude.ai を てでひらいてください"
        except ImportError:
            pass
        try:
            import subprocess
            subprocess.run(["claude", "--version"], capture_output=True, timeout=2)
            return "ローカル Claude が つかえます"
        except Exception:
            pass
        return "Claude.ai を てでひらいてください"

    def update(self) -> None:
        """AI ヘルプの入力を処理する。"""
        game = self.game
        if game is None:
            return
        if game.input_state.btnp(CANCEL_BUTTONS) or game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("cancel")
            game.state = "menu"

    def draw(self) -> None:
        """AI ヘルプ画面を描画する。背景の重ね描きは scene が指揮し、
        パネル本体は Presenter→View で描画（M1-1 / M2-2 準拠）。"""
        game = self.game
        if game is None:
            return
        game.explore_scene.draw()
        game.status_bar.draw()
        vm = self.presenter.build_view_model(game)
        self.view.render(vm, game.messages)
