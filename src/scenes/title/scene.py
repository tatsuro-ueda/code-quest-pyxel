from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.title.model import TitleModel
from src.scenes.title.presenter import TitlePresenter
from src.scenes.title.view import TitleView


@dataclass
class TitleScene:
    """タイトル画面の model/view/presenter を束ねる Scene 実装。"""

    name: str = "title"
    model: TitleModel = field(default_factory=TitleModel)
    view: TitleView = field(default_factory=TitleView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = TitlePresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。現状は状態更新なし。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在の model 状態から描画辞書を返す。"""
        return self.view.render(
            cursor=self.model.cursor,
            settings_open=self.model.settings_open,
        )
