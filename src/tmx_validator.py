"""TMX検証モジュール.

設計書 §7.2 / §10 に対応。不正なTMXは起動時に必ず拒否する。
AIエージェントが編集した結果もこの検証を通すこと。
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# 規約定義（設計書 §4, §5 と同期すること）
# ---------------------------------------------------------------------------

ALLOWED_TILE_LAYERS: frozenset[str] = frozenset({"ground", "decoration", "collision"})
ALLOWED_OBJECT_GROUPS: frozenset[str] = frozenset({"objects", "spawn"})
REQUIRED_LAYERS: frozenset[str] = frozenset({"ground", "collision"})
REQUIRED_OBJECT_GROUPS: frozenset[str] = frozenset({"spawn"})

# type → 必須プロパティ名の集合
OBJECT_SCHEMA: dict[str, frozenset[str]] = {
    "npc": frozenset({"dialog_id"}),
    "door": frozenset({"target_map", "spawn_point"}),
    "chest": frozenset({"item_id"}),
    "trigger": frozenset({"event_id"}),
    "spawn": frozenset(),
}


# ---------------------------------------------------------------------------
# 例外
# ---------------------------------------------------------------------------


class ValidationError(Exception):
    """TMX検証エラー（致命的、起動を止める）."""


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


# ---------------------------------------------------------------------------
# 内部
# ---------------------------------------------------------------------------


def _parse_properties(elem: ET.Element | None) -> dict[str, str]:
    if elem is None:
        return {}
    out: dict[str, str] = {}
    for prop in elem.findall("property"):
        name = prop.get("name")
        if name:
            out[name] = prop.get("value", "")
    return out


def _validate_object(
    obj_elem: ET.Element,
    group_name: str,
    maps_dir: Path,
    report: ValidationReport,
) -> None:
    obj_id = obj_elem.get("id", "?")
    obj_type = obj_elem.get("type", "")

    if group_name == "spawn":
        # spawn グループでは type が未指定でも許可（name が必須）
        if not obj_elem.get("name"):
            report.errors.append(f"spawn object id={obj_id}: name 必須")
        return

    # objects グループ
    if obj_type not in OBJECT_SCHEMA:
        report.errors.append(
            f"object id={obj_id}: type='{obj_type}' は辞書外 "
            f"(許可: {sorted(OBJECT_SCHEMA)})"
        )
        return

    props = _parse_properties(obj_elem.find("properties"))
    required = OBJECT_SCHEMA[obj_type]
    missing = required - props.keys()
    if missing:
        report.errors.append(
            f"object id={obj_id} type={obj_type}: 必須プロパティ欠如 {sorted(missing)}"
        )

    # door の参照整合性
    if obj_type == "door" and "target_map" in props:
        target = maps_dir / props["target_map"]
        if not target.exists():
            report.errors.append(
                f"door id={obj_id}: target_map '{props['target_map']}' が存在しない"
            )


# ---------------------------------------------------------------------------
# 公開API
# ---------------------------------------------------------------------------


def validate(path: str | Path) -> ValidationReport:
    """TMXを検証してレポートを返す. errorsが空ならOK."""
    p = Path(path)
    report = ValidationReport()

    if not p.exists():
        report.errors.append(f"ファイルが存在しない: {p}")
        return report

    try:
        tree = ET.parse(p)
    except ET.ParseError as exc:
        report.errors.append(f"XMLパース失敗: {exc}")
        return report

    root = tree.getroot()
    if root.tag != "map":
        report.errors.append(f"ルート要素が map ではない: {root.tag}")
        return report

    maps_dir = p.parent

    # タイルレイヤー名チェック
    tile_layer_names: set[str] = set()
    for layer in root.findall("layer"):
        name = layer.get("name", "")
        tile_layer_names.add(name)
        if name not in ALLOWED_TILE_LAYERS:
            report.errors.append(
                f"タイルレイヤー '{name}' は規約外 "
                f"(許可: {sorted(ALLOWED_TILE_LAYERS)})"
            )
        data_elem = layer.find("data")
        if data_elem is None:
            report.errors.append(f"layer '{name}': data 要素なし")
        elif data_elem.get("encoding") != "csv":
            report.errors.append(
                f"layer '{name}': encoding='csv' 必須 "
                f"(現在: {data_elem.get('encoding')!r})"
            )

    missing_layers = REQUIRED_LAYERS - tile_layer_names
    if missing_layers:
        report.errors.append(f"必須タイルレイヤー欠如: {sorted(missing_layers)}")

    # オブジェクトグループチェック
    group_names: set[str] = set()
    for group in root.findall("objectgroup"):
        gname = group.get("name", "")
        group_names.add(gname)
        if gname not in ALLOWED_OBJECT_GROUPS:
            report.errors.append(
                f"オブジェクトグループ '{gname}' は規約外 "
                f"(許可: {sorted(ALLOWED_OBJECT_GROUPS)})"
            )
            continue
        for obj_elem in group.findall("object"):
            _validate_object(obj_elem, gname, maps_dir, report)

    missing_groups = REQUIRED_OBJECT_GROUPS - group_names
    if missing_groups:
        report.errors.append(
            f"必須オブジェクトグループ欠如: {sorted(missing_groups)}"
        )

    return report


def validate_or_raise(path: str | Path) -> None:
    """検証に失敗したら ValidationError を送出する."""
    report = validate(path)
    if not report.ok:
        msg = f"TMX検証失敗: {path}\n  - " + "\n  - ".join(report.errors)
        raise ValidationError(msg)
