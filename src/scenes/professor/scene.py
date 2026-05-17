"""professor scene 本体（Model / View / Presenter の配線）。

Problems:
    - Scene に入力解釈と描画ロジックを直書きすると、レイヤが崩れて
      テスト時に Pyxel まで起動する必要が出る。
    - シーンごとに生成・配線手順がばらばらだと、新しいシーンを
      追加する時に何を持たせるか毎回考え直すことになる。

Solutions:
    - professor の Scene は Model / View / Presenter を保持し、
      update / draw を Presenter / View へ委譲する薄い配線に保つ。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.professor.model import ProfessorModel
from src.scenes.professor.presenter import ProfessorPresenter
from src.scenes.professor.view import ProfessorView


@dataclass
class ProfessorScene:
    """Professor イベント（P1-G10 で Game から 11 メソッドを取り込み）。"""

    # === Public API ===

    name: str = "professor"
    model: ProfessorModel = field(default_factory=ProfessorModel)
    view: ProfessorView = field(default_factory=ProfessorView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.presenter = ProfessorPresenter(self.model)

    def phase(self) -> str:
        """プレイヤーの進行度に応じた Professor phase（early/mid/late）。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game.player_model.glitch_lord_defeated:
            return "late"
        max_zone = game.player_model.max_zone_reached
        if max_zone >= 3:
            return "late"
        if max_zone >= 1:
            return "mid"
        return "early"

    def battle_phase(self, ratio: float) -> str:
        """HP比率から Professor battle phase キーを返す。

        Args:
            ratio: ratio の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        pct = ratio * 100
        for thr in (10, 25, 40, 55, 70, 85):
            if pct < thr:
                return str(thr)
        return "100"

    def enter_intro(self) -> None:
        """Professor 会話イベントに入る。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        player = game.player_model
        if player.professor_intro_seen:
            scene = "castle.professor.revisit_intro_01"
        else:
            scene = "castle.professor.intro_01"
        player.professor_intro_seen = True
        self.model.intro_lines = game.messages.dialog_lines(scene)
        self.model.intro_idx = 0
        self.model.is_choice_active = False
        self.model.choice_cursor = 1
        game.state = "professor_intro"

    def update_intro(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        self.presenter.update_intro(game, self)

    def draw_intro(self) -> None:
        """Professor intro 画面を描画する。

        Presenter が VM 組立て、View に委譲（M1-1 / M2-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        vm = self.presenter.build_intro_view_model(game)
        self.view.draw(vm, game.messages)

    def enter_ending_main(self) -> None:
        """Professor ending（撃破後）に入る。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        player = game.player_model
        if player.professor_ending_seen:
            scene = "castle.professor.revisit_epilogue_01"
        else:
            scene = "castle.professor.epilogue_01"
        player.professor_ending_seen = True
        self.model.ending_lines = game.messages.dialog_lines(scene)
        self.model.ending_idx = 0
        game.state = "professor_ending_main"

    def update_ending_main(self) -> None:
        """配線：Presenter に委譲（M3-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        self.presenter.update_ending_main(game)

    def draw_ending_main(self) -> None:
        """Professor ending main 画面を描画する。Presenter が VM 組立て、View に委譲。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        vm = self.presenter.build_ending_main_view_model(game)
        self.view.draw(vm, game.messages)

    def enter_ending_accepted(self) -> None:
        """Professor 受諾エンドに入る。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        self.model.ending_lines = game.messages.dialog_lines(
            "castle.professor.accepted_01"
        )
        self.model.ending_idx = 0
        game.state = "professor_ending_accepted"

    def update_ending_accepted(self) -> None:
        """配線：Presenter に委譲（M3-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        self.presenter.update_ending_accepted(game)

    def draw_ending_accepted(self) -> None:
        """Professor 受諾エンド画面を描画する。Presenter が VM 組立て、View に委譲。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        vm = self.presenter.build_ending_accepted_view_model(game)
        self.view.draw(vm, game.messages)

    def update(self) -> None:
        """Scene Protocol 互換。P1-G10 では個別 update_* を Game dispatcher が呼ぶ。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return None

    def draw(self) -> None:
        """Scene Protocol 互換。個別 draw_* を Game dispatcher が呼ぶ。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return None
