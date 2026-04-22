from __future__ import annotations

from src.scenes.dialog.model import DialogStep

class DialogView:
    """会話シーンの描画用ビューモデルを組み立てる。"""

    def render(self, step: DialogStep | None) -> dict[str, object]:
        """現在ステップから話者・本文・選択肢の辞書を返す（None なら空表示）。"""
        if step is None:
            return {"speaker": None, "text": "", "choices": []}
        return {
            "speaker": step.speaker,
            "text": step.text,
            "choices": [choice.text for choice in step.choices],
        }
