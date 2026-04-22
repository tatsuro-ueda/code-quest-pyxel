from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class Scene(Protocol):
    """各シーン（title / explore / battle / dialog）が満たすインターフェース。"""

    name: str

    def update(self) -> None: ...
    def draw(self) -> object | None: ...


@dataclass
class SceneManager:
    """脱モノリス移行のための薄いシーン切り替え器。"""

    current_scene: Scene | None = None
    previous_scene_name: str | None = None
    history: list[str] = field(default_factory=list)

    def set_scene(self, scene: Scene) -> None:
        """現在シーンを切り替え、直前シーン名を履歴に積む。"""
        if self.current_scene is not None:
            self.previous_scene_name = self.current_scene.name
            self.history.append(self.current_scene.name)
        self.current_scene = scene

    def update(self) -> None:
        """毎フレームの更新を現在シーンへ委譲する。"""
        if self.current_scene is not None:
            self.current_scene.update()

    def draw(self) -> object | None:
        """毎フレームの描画を現在シーンへ委譲する（未設定なら None）。"""
        if self.current_scene is not None:
            return self.current_scene.draw()
        return None
