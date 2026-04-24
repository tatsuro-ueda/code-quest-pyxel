from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pyxel

from src.scenes.title.model import TitleModel
from src.scenes.title.presenter import TitlePresenter
from src.scenes.title.view import TitleView
from src.shared.services.input_bindings import (
    UP_BUTTONS,
    DOWN_BUTTONS,
    CONFIRM_BUTTONS,
    TITLE_START_BUTTONS,
)
from src.shared.state.player_model import PlayerModel


LOAD_OK_MSG = "きろくをよみかえした。りかいがもどってくる。"
NO_RECORD_MSG = "まだなにもかきとめていない…"


@dataclass
class TitleScene:
    """タイトル画面の model/view/presenter を束ねる Scene 実装。

    P1-G1（J53）で Game.update_title / Game.draw_title / Game._do_load を
    ここに取り込んだ。`game` バックリファレンス経由で Game のサービス／
    state にアクセスする（Phase 1 transitional pattern）。
    """

    name: str = "title"
    model: TitleModel = field(default_factory=TitleModel)
    view: TitleView = field(default_factory=TitleView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = TitlePresenter(self.model)

    def update(self) -> None:
        """タイトル画面の入力処理と state 遷移。"""
        game = self.game
        if game is None:
            return
        if game.input_state.btnp(UP_BUTTONS):
            self.model.cursor = (self.model.cursor - 1) % 3
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(DOWN_BUTTONS):
            self.model.cursor = (self.model.cursor + 1) % 3
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(CONFIRM_BUTTONS) or game.input_state.btnp(TITLE_START_BUTTONS):
            game.sfx.play("select")
            if self.model.cursor == 0:
                # はじめから: プレイヤー状態をクリーンに作り直す（AV設定は引き継ぐ）
                prev = game.player_model
                fresh = PlayerModel.new_game()
                fresh.bgm_enabled = prev.bgm_enabled
                fresh.sfx_enabled = prev.sfx_enabled
                fresh.vfx_enabled = prev.vfx_enabled
                game.player_model = fresh
                game.settings_scene.apply_av()
                game.state = "map"
                return
            if self.model.cursor == 2:
                game.settings_scene.open("title")
                return
            # つづきから — has_save が False ならグレーアウト
            if not game._has_save:
                return
            self._do_load()

    def draw(self) -> dict[str, object] | None:
        """タイトル画面を Pyxel に描画する。

        game が設定されていない場合（単体テスト）は view.render で snapshot を返す。
        通常実行時（game 設定済み）は Pyxel に直接描画して None を返す。
        """
        game = self.game
        if game is None:
            return self.view.render(
                cursor=self.model.cursor,
                settings_open=self.model.settings_open,
            )
        pyxel.cls(1)
        game.messages.text(70, 80, "BLOCK QUEST", 7)
        game.messages.text(50, 110, game.text_fmt.t("- コードのぼうけん -", "- A Coding Quest -"), 10)
        labels = [
            game.text_fmt.t("はじめから", "NEW GAME"),
            game.text_fmt.t("つづきから", "CONTINUE"),
            game.text_fmt.t("せってい", "SETTINGS"),
        ]
        for i, label in enumerate(labels):
            ly = 150 + i * 16
            enabled = (i != 1) or game._has_save
            base_color = 7 if enabled else 5
            color = 10 if (i == self.model.cursor and enabled) else base_color
            marker = ">" if i == self.model.cursor else " "
            game.messages.text(80, ly, f"{marker} {label}", color)
        if self.model.cursor == 1 and not game._has_save:
            game.messages.text(
                40, 200, game.text_fmt.t("(まだなにもかきとめていない)", "(no save yet)"), 5
            )

    def _do_load(self) -> None:
        """セーブデータを読み出して player / state を復元する。"""
        game = self.game
        if game is None:
            return
        snap = game.save_store.load()
        if snap is None:
            # 破損やバージョン未来のセーフティネット
            game._has_save = False
            game.messages.show([NO_RECORD_MSG])
            game.prev_state = "title"
            game.state = "message"
            return
        restored_player, (tx, ty) = PlayerModel.from_snapshot(snap)
        game.player_model = restored_player
        game.settings_scene.apply_av()
        game.player_model.x = tx
        game.player_model.y = ty
        game.player_model.in_dungeon = False
        game.dungeon_map = None
        # ロード直後の暴発を防ぐため A クールダウンを立てる
        game.explore_scene.model.a_cooldown = True
        game.messages.show([LOAD_OK_MSG])
        game.prev_state = "map"
        game.state = "message"
