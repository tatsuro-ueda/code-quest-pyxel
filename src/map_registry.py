"""マップレジストリ.

設計書 §7.3 に対応。起動時に全TMXを検証→ロード→登録し、
シーン遷移時は参照切り替えのみで済むようにする。
"""

from __future__ import annotations

from pathlib import Path

from . import tiled_loader, tmx_validator
from .tiled_loader import MapData


class MapRegistry:
    def __init__(self) -> None:
        self._maps: dict[str, MapData] = {}
        self._active: str | None = None

    # -- ロード -----------------------------------------------------------

    def load_all(self, maps_dir: str | Path) -> None:
        """maps_dir 配下の全TMXを検証・ロードして登録する.

        1つでも検証失敗があれば ValidationError を送出し、何もロードしない
        （沈黙の失敗を作らない方針）.
        """
        d = Path(maps_dir)
        tmx_files = sorted(d.glob("*.tmx"))
        if not tmx_files:
            raise FileNotFoundError(f"TMXファイルが見つからない: {d}")

        # 先に全件検証
        for tmx in tmx_files:
            tmx_validator.validate_or_raise(tmx)

        # 検証OKなのでロード
        loaded: dict[str, MapData] = {}
        for tmx in tmx_files:
            data = tiled_loader.load(tmx)
            loaded[data.name] = data
        self._maps = loaded

    # -- アクセス ---------------------------------------------------------

    def get(self, name: str) -> MapData:
        if name not in self._maps:
            raise KeyError(f"マップ未登録: {name}")
        return self._maps[name]

    def set_active(self, name: str) -> None:
        if name not in self._maps:
            raise KeyError(f"マップ未登録: {name}")
        self._active = name

    def active(self) -> MapData:
        if self._active is None:
            raise RuntimeError("アクティブマップ未設定")
        return self._maps[self._active]

    def names(self) -> list[str]:
        return sorted(self._maps.keys())
