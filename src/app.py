from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.scene_manager import Scene, SceneManager
from src.shared.services.game_state import GameState


@dataclass
class BlockQuestApp:
    """update/draw を SceneManager に委譲する実行シェル。

    Q3A 決定により、scene 間共有 state (GameState) と注入サービスを保有する。
    Phase 1 中は既存 scene がまだ services を使わないので、フィールドは
    optional（None 可）としておく。P1-G で scene 側が constructor で受け取る
    形に移行していく。
    """

    scene_manager: SceneManager
    game_state: GameState = field(default_factory=GameState)

    # --- 注入サービス（P1-G で scene が使うようになる。Phase 1 中は optional）---
    audio_manager: Any = None
    sfx_system: Any = None
    input_state_tracker: Any = None
    save_store: Any = None
    pyxel_module: Any = None
    image_banks: Any = None
    dialog_runner: Any = None
    message_display: Any = None
    vfx_system: Any = None

    def set_scene(self, scene: Scene) -> None:
        """表示するシーンを差し替える。

        Phase 1 中は scene に GameState を押し込まない。P1-G でメソッド移動時に、
        各 scene が constructor で GameState とサービスを受け取る形に切り替える。
        """
        self.scene_manager.set_scene(scene)

    def update(self) -> None:
        """毎フレームの更新を現在シーンへ回す。"""
        self.scene_manager.update()

    def draw(self) -> object | None:
        """毎フレームの描画結果を現在シーンから受け取る。"""
        return self.scene_manager.draw()
