"""TMX → MapData アダプタ.

設計書 `docs/steering/20260406-TiledMapEditor/design.md` の §7.1 に対応。
外部依存ゼロ。標準ライブラリ `xml.etree.ElementTree` のみを使う。
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# データ構造
# ---------------------------------------------------------------------------


@dataclass
class GameObject:
    id: int
    type: str                     # npc / door / chest / trigger / spawn
    name: str
    x: int                        # ピクセル座標
    y: int
    width: int
    height: int
    properties: dict[str, str] = field(default_factory=dict)

    @property
    def tile_x(self) -> int:
        return self.x // 16 if self.x else 0

    @property
    def tile_y(self) -> int:
        return self.y // 16 if self.y else 0


@dataclass
class MapData:
    name: str
    width: int                                  # タイル単位
    height: int                                 # タイル単位
    tile_size: int                              # ピクセル
    ground: list[list[int]]                     # pyxelタイルID (gid-1)、空は-1
    decoration: list[list[int]]
    collision: list[list[bool]]                 # True=通れない
    objects: list[GameObject]
    spawn_points: dict[str, tuple[int, int]]    # name → (tile_x, tile_y)


# ---------------------------------------------------------------------------
# 内部ユーティリティ
# ---------------------------------------------------------------------------


class TMXLoadError(Exception):
    """TMXのパース失敗."""


def _parse_csv_layer(data_text: str, width: int, height: int) -> list[list[int]]:
    """CSV encoding の data 要素を 2D 配列に変換する."""
    rows = [row for row in data_text.strip().splitlines() if row.strip()]
    if len(rows) != height:
        raise TMXLoadError(
            f"CSV行数が不一致: 期待 {height}, 実際 {len(rows)}"
        )
    result: list[list[int]] = []
    for y, row in enumerate(rows):
        # 末尾カンマ対応
        values = [v for v in row.replace(" ", "").rstrip(",").split(",") if v]
        if len(values) != width:
            raise TMXLoadError(
                f"CSV列数が不一致 (row={y}): 期待 {width}, 実際 {len(values)}"
            )
        result.append([int(v) for v in values])
    return result


def _gid_to_tile_id(gid: int) -> int:
    """TMXのGID(1始まり)をPyxelタイルID(0始まり)に変換。0なら-1(空)。"""
    return gid - 1 if gid > 0 else -1


def _parse_properties(elem: ET.Element | None) -> dict[str, str]:
    if elem is None:
        return {}
    result: dict[str, str] = {}
    for prop in elem.findall("property"):
        name = prop.get("name")
        value = prop.get("value", "")
        if name:
            result[name] = value
    return result


def _parse_object(obj_elem: ET.Element) -> GameObject:
    obj_id = int(obj_elem.get("id", "0"))
    obj_type = obj_elem.get("type", "")
    name = obj_elem.get("name", "")
    x = int(float(obj_elem.get("x", "0")))
    y = int(float(obj_elem.get("y", "0")))
    w = int(float(obj_elem.get("width", "16")))
    h = int(float(obj_elem.get("height", "16")))
    properties = _parse_properties(obj_elem.find("properties"))
    return GameObject(
        id=obj_id,
        type=obj_type,
        name=name,
        x=x,
        y=y,
        width=w,
        height=h,
        properties=properties,
    )


# ---------------------------------------------------------------------------
# 公開API
# ---------------------------------------------------------------------------


def load(path: str | Path) -> MapData:
    """TMXを読み込み MapData を返す.

    検証は行わない。呼び出し前に `tmx_validator.validate()` を通すこと。
    """
    p = Path(path)
    try:
        tree = ET.parse(p)
    except ET.ParseError as exc:
        raise TMXLoadError(f"XMLパース失敗: {p}: {exc}") from exc

    root = tree.getroot()
    if root.tag != "map":
        raise TMXLoadError(f"ルート要素が map ではない: {root.tag}")

    width = int(root.get("width", "0"))
    height = int(root.get("height", "0"))
    tile_size = int(root.get("tilewidth", "16"))

    # レイヤー収集
    tile_layers: dict[str, list[list[int]]] = {}
    for layer in root.findall("layer"):
        lname = layer.get("name", "")
        data_elem = layer.find("data")
        if data_elem is None or data_elem.get("encoding") != "csv":
            raise TMXLoadError(
                f"layer '{lname}': data 要素は encoding='csv' 必須"
            )
        tile_layers[lname] = _parse_csv_layer(data_elem.text or "", width, height)

    # ground / decoration → pyxelタイルID、collision → bool配列
    ground_raw = tile_layers.get("ground")
    if ground_raw is None:
        raise TMXLoadError("ground レイヤーが存在しない")
    ground = [[_gid_to_tile_id(g) for g in row] for row in ground_raw]

    decoration_raw = tile_layers.get("decoration")
    if decoration_raw is None:
        decoration = [[-1] * width for _ in range(height)]
    else:
        decoration = [[_gid_to_tile_id(g) for g in row] for row in decoration_raw]

    collision_raw = tile_layers.get("collision")
    if collision_raw is None:
        raise TMXLoadError("collision レイヤーが存在しない")
    collision = [[g != 0 for g in row] for row in collision_raw]

    # オブジェクト層
    objects: list[GameObject] = []
    spawn_points: dict[str, tuple[int, int]] = {}
    for group in root.findall("objectgroup"):
        gname = group.get("name", "")
        for obj_elem in group.findall("object"):
            obj = _parse_object(obj_elem)
            if gname == "spawn":
                spawn_points[obj.name] = (obj.tile_x, obj.tile_y)
            elif gname == "objects":
                objects.append(obj)

    return MapData(
        name=p.stem,
        width=width,
        height=height,
        tile_size=tile_size,
        ground=ground,
        decoration=decoration,
        collision=collision,
        objects=objects,
        spawn_points=spawn_points,
    )
