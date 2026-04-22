from __future__ import annotations

from dataclasses import dataclass

from src.scenes.dialog.model import DialogStep, StructuredDialogRunner


@dataclass
class DialogPresenter:
    """会話シーンの入力を Runner に委譲する presenter。"""

    runner: StructuredDialogRunner

    def start(self, scene_name: str) -> DialogStep:
        """指定シーンから会話を開始する。"""
        return self.runner.start(scene_name)

    def choose(self, index: int) -> DialogStep | None:
        """プレイヤーの選択肢を Runner へ伝えて次ステップを得る。"""
        return self.runner.choose(index)

    def continue_dialog(self) -> DialogStep | None:
        """選択肢なしのシーンを次へ進める。"""
        return self.runner.continue_dialog()
