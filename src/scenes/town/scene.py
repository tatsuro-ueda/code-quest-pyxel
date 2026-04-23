from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pyxel

from src.scenes.town.model import TownModel
from src.scenes.town.presenter import TownPresenter
from src.scenes.town.view import TownView
from src.shared.services.input_bindings import (
    UP_BUTTONS,
    DOWN_BUTTONS,
    CONFIRM_BUTTONS,
    CANCEL_BUTTONS,
)
from src.shared.services.player_state import dump_snapshot
from src.shared.services.save_store import SaveStoreError, LocalStorageSaveStore


@dataclass
class TownScene:
    """town シーン（P1-G4 で Game から 10 メソッドを取り込み）。"""

    name: str = "town"
    model: TownModel = field(default_factory=TownModel)
    view: TownView = field(default_factory=TownView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = TownPresenter(self.model)

    def current_town_index(self) -> int:
        game = self.game
        import src.runtime.main_runtime as M
        if self.model.menu_pos is None:
            return 0
        return M.TOWN_INDEX_BY_POS.get(self.model.menu_pos, 0)

    def _inn_cost(self) -> int:
        import src.runtime.main_runtime as M
        idx = self.current_town_index()
        return M.INN_PRICES[idx] if idx < len(M.INN_PRICES) else M.INN_COST

    def update(self) -> None:
        """town 状態：メッセージ送り→マップ復帰。"""
        game = self.game
        if game is None:
            return
        if game.messages.any_advance_btnp():
            game.messages.index, done = game.messages.advance_page(game.messages.index, game.messages.lines)
            if done:
                game.state = "map"

    def update_menu(self) -> None:
        """town メニューの入力処理。"""
        game = self.game
        if game is None:
            return
        import src.runtime.main_runtime as M
        if game._btnp(UP_BUTTONS):
            game.sfx.play("cursor")
            self.model.menu_cursor = (self.model.menu_cursor - 1) % len(M.TOWN_MENU_LABELS)
            return
        if game._btnp(DOWN_BUTTONS):
            game.sfx.play("cursor")
            self.model.menu_cursor = (self.model.menu_cursor + 1) % len(M.TOWN_MENU_LABELS)
            return
        if game._btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            self._exit()
            return
        if game._btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            label = M.TOWN_MENU_LABELS[self.model.menu_cursor]
            if label == "はなす":
                self._talk()
            elif label in M.SHOP_KIND_BY_LABEL:
                game.shop_scene.enter(M.SHOP_KIND_BY_LABEL[label])
            elif label == "やどや":
                self._inn()
            elif label == "セーブ":
                self._save()
            elif label == "でる":
                self._exit()

    def _enter_message(self, lines, callback=None) -> None:
        """町メニュー内の通知。閉じたら town_menu に戻る。"""
        game = self.game
        game.messages.lines = lines
        game.messages.index = 0
        game.messages.callback = callback
        game.prev_state = "town_menu"
        game.state = "message"

    def _talk(self) -> None:
        """町NPCとの会話。"""
        game = self.game
        import src.runtime.main_runtime as M
        scene_name = M.TOWN_DIALOG_SCENES.get(self.model.menu_pos)
        if scene_name is not None:
            lines = game.messages.dialog_lines(scene_name, ProfessorPhase=game.professor_scene.phase())
            self._enter_message(lines)
            return
        idx = self.current_town_index()
        if idx >= len(M.TOWN_NPC_LINES):
            self._enter_message(["……ここには はなせるひとが いない。"])
            return
        npc_lines = M.TOWN_NPC_LINES[idx]
        talk_idx = game.player.get("town_talk_idx", [0, 0, 0])
        line = npc_lines[talk_idx[idx] % len(npc_lines)]
        talk_idx[idx] = (talk_idx[idx] + 1) % len(npc_lines)
        game.player["town_talk_idx"] = talk_idx
        self._enter_message([line])

    def _inn(self) -> None:
        """宿屋泊まり。"""
        game = self.game
        import src.runtime.main_runtime as M
        cost = self._inn_cost()
        if game.player["gold"] < cost:
            self._enter_message([M.INN_LACK_MSG])
            return
        game.player["gold"] -= cost
        game.player["hp"] = game.player["max_hp"]
        game.player["mp"] = game.player["max_mp"]
        game.player["poisoned"] = False
        self._enter_message([M.INN_OK_MSG])

    def _save(self) -> None:
        """セーブ実行。"""
        game = self.game
        import src.runtime.main_runtime as M
        snap = dump_snapshot(game.player, town_pos=self.model.menu_pos)
        try:
            game.save_store.save(snap)
        except SaveStoreError:
            is_web = isinstance(game.save_store, LocalStorageSaveStore)
            msg = M.SAVE_FAIL_MSG_WEB if is_web else M.SAVE_FAIL_MSG_DESKTOP
            self._enter_message([msg])
            return
        game._has_save = True
        game.sfx.play("save")
        self._enter_message([M.SAVE_OK_MSG])

    def _exit(self) -> None:
        """町メニューから出る。"""
        game = self.game
        game.state = "map"
        game.explore_scene.model.a_cooldown = True
        self.model.menu_pos = None

    def draw(self) -> None:
        """town 状態（メッセージ表示中）は draw_menu 側から呼ばれる場合に備えて空。"""
        game = self.game
        if game is None:
            return

    def draw_menu(self) -> None:
        """町メニュー画面を描画する。"""
        game = self.game
        if game is None:
            return
        import src.runtime.main_runtime as M
        game.explore_scene.draw()
        game.draw_status_bar()
        x, y, w, h = 20, 40, 216, 170
        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 7)
        game.messages.text(x + 8, y + 8, game.text_fmt.t("まちメニュー", "TOWN MENU"), 7)
        labels = M.TOWN_MENU_LABELS if game.has_jp_font else M.TOWN_MENU_LABELS_EN
        for i, label in enumerate(labels):
            ly = y + 28 + i * 16
            color = 10 if i == self.model.menu_cursor else 7
            marker = ">" if i == self.model.menu_cursor else " "
            game.messages.text(x + 16, ly, f"{marker} {label}", color)
        gold = game.player["gold"]
        game.messages.text(x + 8, y + h - 16, f"GOLD: {gold}", 6)
