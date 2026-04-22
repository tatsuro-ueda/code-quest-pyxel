from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.dialog.model import DialogStep, StructuredDialogRunner
from src.scenes.dialog.presenter import DialogPresenter
from src.scenes.dialog.view import DialogView


@dataclass
class DialogScene:
    """会話シーンの Runner/view/presenter を束ね、現在ステップを保持する Scene 実装。"""

    runner: StructuredDialogRunner
    name: str = "dialog"
    view: DialogView = field(default_factory=DialogView)
    active_step: DialogStep | None = None

    def __post_init__(self) -> None:
        """Runner を共有する presenter を生成する。"""
        self.presenter = DialogPresenter(self.runner)

    def start(
        self,
        scene_name: str,
        *,
        state: dict[str, Any] | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> DialogStep:
        """会話を開始し、現在ステップを保持しつつ返す。"""
        self.active_step = self.runner.start(scene_name, state=state, extra_context=extra_context)
        return self.active_step

    def choose(self, index: int) -> DialogStep | None:
        """選択肢を選んで現在ステップを更新する。"""
        self.active_step = self.presenter.choose(index)
        return self.active_step

    def continue_dialog(self) -> DialogStep | None:
        """次シーンへ進めて現在ステップを更新する。"""
        self.active_step = self.presenter.continue_dialog()
        return self.active_step

    def update(self) -> None:
        """毎フレーム更新。現状は状態更新なし。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在ステップを view で描画辞書に変換して返す。"""
        return self.view.render(self.active_step)
