from __future__ import annotations

from dataclasses import dataclass

from src.core.scene_manager import Scene, SceneManager


@dataclass
class BlockQuestApp:
    """update/draw を SceneManager に委譲する最小の実行シェル。"""

    scene_manager: SceneManager

    def set_scene(self, scene: Scene) -> None:
        """表示するシーンを差し替える。"""
        self.scene_manager.set_scene(scene)

    def update(self) -> None:
        """毎フレームの更新を現在シーンへ回す。"""
        self.scene_manager.update()

    def draw(self) -> object | None:
        """毎フレームの描画結果を現在シーンから受け取る。"""
        return self.scene_manager.draw()
