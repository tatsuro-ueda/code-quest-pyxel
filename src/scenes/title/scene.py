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
from src.shared.services.player_state import create_initial_player, restore_snapshot


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
        if game._btnp(UP_BUTTONS):
            self.model.cursor = (self.model.cursor - 1) % 3
            game.sfx.play("cursor")
            return
        if game._btnp(DOWN_BUTTONS):
            self.model.cursor = (self.model.cursor + 1) % 3
            game.sfx.play("cursor")
            return
        if game._btnp(CONFIRM_BUTTONS) or game._btnp(TITLE_START_BUTTONS):
            game.sfx.play("select")
            if self.model.cursor == 0:
                # はじめから: プレイヤー状態をクリーンに作り直す
                settings = {
                    "bgm_enabled": game.player.get("bgm_enabled", True),
                    "sfx_enabled": game.player.get("sfx_enabled", True),
                    "vfx_enabled": game.player.get("vfx_enabled", True),
                }
                game.player = create_initial_player()
                game.player.update(settings)
                game._apply_av_settings()
                game.state = "map"
                return
            if self.model.cursor == 2:
                game._open_settings("title")
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
        game.text(70, 80, "BLOCK QUEST", 7)
        game.text(50, 110, game._t("- コードのぼうけん -", "- A Coding Quest -"), 10)
        labels = [
            game._t("はじめから", "NEW GAME"),
            game._t("つづきから", "CONTINUE"),
            game._t("せってい", "SETTINGS"),
        ]
        for i, label in enumerate(labels):
            ly = 150 + i * 16
            enabled = (i != 1) or game._has_save
            base_color = 7 if enabled else 5
            color = 10 if (i == self.model.cursor and enabled) else base_color
            marker = ">" if i == self.model.cursor else " "
            game.text(80, ly, f"{marker} {label}", color)
        if self.model.cursor == 1 and not game._has_save:
            game.text(
                40, 200, game._t("(まだなにもかきとめていない)", "(no save yet)"), 5
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
            game.show_message([NO_RECORD_MSG])
            game.prev_state = "title"
            game.state = "message"
            return
        restored = restore_snapshot(snap)
        for key, value in restored["player"].items():
            game.player[key] = value
        game._apply_av_settings()
        tx, ty = restored["town_pos"]
        game.player["x"] = tx
        game.player["y"] = ty
        game.player["in_dungeon"] = False
        game.dungeon_map = None
        # ロード直後の暴発を防ぐため A クールダウンを立てる
        game._a_cooldown = True
        game.show_message([LOAD_OK_MSG])
        game.prev_state = "map"
        game.state = "message"
