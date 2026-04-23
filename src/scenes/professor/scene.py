from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pyxel

from src.scenes.professor.model import ProfessorModel
from src.scenes.professor.presenter import ProfessorPresenter
from src.scenes.professor.view import ProfessorView
from src.shared.services.input_bindings import (
    UP_BUTTONS,
    DOWN_BUTTONS,
    CONFIRM_BUTTONS,
)


@dataclass
class ProfessorScene:
    """Professor イベント（P1-G10 で Game から 11 メソッドを取り込み）。"""

    name: str = "professor"
    model: ProfessorModel = field(default_factory=ProfessorModel)
    view: ProfessorView = field(default_factory=ProfessorView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = ProfessorPresenter(self.model)

    def phase(self) -> str:
        """プレイヤーの進行度に応じた Professor phase（early/mid/late）。"""
        game = self.game
        if game.player["glitch_lord_defeated"]:
            return "late"
        max_zone = game.player["max_zone_reached"]
        if max_zone >= 3:
            return "late"
        if max_zone >= 1:
            return "mid"
        return "early"

    def battle_phase(self, ratio: float) -> str:
        """HP比率から Professor battle phase キーを返す。"""
        pct = ratio * 100
        for thr in (10, 25, 40, 55, 70, 85):
            if pct < thr:
                return str(thr)
        return "100"

    def enter_intro(self) -> None:
        """Professor 会話イベントに入る。"""
        game = self.game
        p = game.player
        if p.get("professor_intro_seen"):
            scene = "castle.professor.revisit_intro_01"
        else:
            scene = "castle.professor.intro_01"
        p["professor_intro_seen"] = True
        self.model.intro_lines = game.messages.dialog_lines(scene)
        self.model.intro_idx = 0
        self.model.choice_active = False
        self.model.choice_cursor = 1
        game.state = "professor_intro"

    def update_intro(self) -> None:
        """intro のページ送りと選択肢。"""
        game = self.game
        if game is None:
            return
        import src.runtime.main_runtime as M
        m = self.model
        if not m.choice_active:
            if game.input_state.btnp(CONFIRM_BUTTONS):
                m.intro_idx, done = game.messages.advance_page(m.intro_idx, m.intro_lines)
                if done:
                    m.choice_active = True
            return
        # choice mode
        if game.input_state.btnp(UP_BUTTONS) or game.input_state.btnp(DOWN_BUTTONS):
            m.choice_cursor = 1 - m.choice_cursor
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            if m.choice_cursor == 0:
                self.enter_ending_accepted()
            else:
                game.battle_scene.start(M.PROFESSOR_DATA, is_professor=True)

    def draw_intro(self) -> None:
        """Professor intro 画面を描画する。"""
        game = self.game
        if game is None:
            return
        m = self.model
        pyxel.cls(0)
        if m.intro_lines and m.intro_idx < len(m.intro_lines):
            for i, sub in enumerate(
                game.messages.current_page_lines(
                    m.intro_lines, m.intro_idx, max_chars=28, max_rows=6,
                )
            ):
                game.messages.text(16, 60 + i * 14, sub, 7)
            if not m.choice_active and (pyxel.frame_count // 15) % 2:
                game.messages.text(228, 200, "v", 7)
        if m.choice_active:
            labels = (
                ["うけいれる", "ことわる"]
                if game.has_jp_font
                else ["ACCEPT", "REFUSE"]
            )
            for i, label in enumerate(labels):
                color = 10 if i == m.choice_cursor else 7
                marker = ">" if i == m.choice_cursor else " "
                game.messages.text(96, 180 + i * 16, f"{marker} {label}", color)

    def enter_ending_main(self) -> None:
        """Professor ending（撃破後）に入る。"""
        game = self.game
        p = game.player
        if p.get("professor_ending_seen"):
            scene = "castle.professor.revisit_epilogue_01"
        else:
            scene = "castle.professor.epilogue_01"
        p["professor_ending_seen"] = True
        self.model.ending_lines = game.messages.dialog_lines(scene)
        self.model.ending_idx = 0
        game.state = "professor_ending_main"

    def update_ending_main(self) -> None:
        """Professor ending main のページ送り。"""
        game = self.game
        if game is None:
            return
        m = self.model
        if game.input_state.btnp(CONFIRM_BUTTONS):
            m.ending_idx, done = game.messages.advance_page(m.ending_idx, m.ending_lines)
            if done:
                game.explore_scene.model.a_cooldown = True
                game.state = "map"

    def draw_ending_main(self) -> None:
        """Professor ending main 画面を描画する。"""
        game = self.game
        if game is None:
            return
        m = self.model
        pyxel.cls(0)
        if m.ending_lines and m.ending_idx < len(m.ending_lines):
            for i, sub in enumerate(
                game.messages.current_page_lines(
                    m.ending_lines, m.ending_idx, max_chars=28, max_rows=6,
                )
            ):
                game.messages.text(16, 80 + i * 14, sub, 10)
            if (pyxel.frame_count // 15) % 2:
                game.messages.text(228, 200, "v", 7)

    def enter_ending_accepted(self) -> None:
        """Professor 受諾エンドに入る。"""
        game = self.game
        self.model.ending_lines = game.messages.dialog_lines("castle.professor.accepted_01")
        self.model.ending_idx = 0
        game.state = "professor_ending_accepted"

    def update_ending_accepted(self) -> None:
        """Professor 受諾エンドのページ送り。"""
        game = self.game
        if game is None:
            return
        m = self.model
        if game.input_state.btnp(CONFIRM_BUTTONS):
            m.ending_idx, done = game.messages.advance_page(m.ending_idx, m.ending_lines)
            if done:
                game.state = "title"
                game.explore_scene.model.a_cooldown = True

    def draw_ending_accepted(self) -> None:
        """Professor 受諾エンド画面を描画する。"""
        game = self.game
        if game is None:
            return
        m = self.model
        pyxel.cls(0)
        if m.ending_lines and m.ending_idx < len(m.ending_lines):
            for i, sub in enumerate(
                game.messages.current_page_lines(
                    m.ending_lines, m.ending_idx, max_chars=28, max_rows=6,
                )
            ):
                game.messages.text(16, 90 + i * 14, sub, 6)
            if (pyxel.frame_count // 15) % 2:
                game.messages.text(228, 210, "v", 7)

    def update(self) -> None:
        """Scene Protocol 互換。P1-G10 では個別 update_* を Game dispatcher が呼ぶ。"""
        return None

    def draw(self) -> None:
        """Scene Protocol 互換。個別 draw_* を Game dispatcher が呼ぶ。"""
        return None
