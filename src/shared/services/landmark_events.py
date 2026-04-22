from __future__ import annotations

"""Landmark proximity checks for overworld interactions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LandmarkEvent:
    """ワールドマップ上の接触イベント（位置・半径・初回／再訪／エピローグのシーン名）を表す。"""

    scene_name: str
    flag_name: str
    x: int
    y: int
    radius: int = 3
    repeat_scene: str | None = None
    epilogue_scene: str | None = None
    epilogue_flag: str | None = None


LANDMARK_EVENTS = (
    LandmarkEvent(
        scene_name="landmark.tree.first",
        flag_name="landmarkTreeSeen",
        repeat_scene="landmark.tree.repeat",
        x=32,
        y=9,
    ),
    LandmarkEvent(
        scene_name="landmark.tower.first",
        flag_name="landmarkTowerSeen",
        repeat_scene="landmark.tower.repeat",
        epilogue_scene="landmark.tower.epilogue",
        epilogue_flag="towerEpilogueSeen",
        x=40,
        y=32,
    ),
)


def find_landmark_event(
    *,
    player_x: int,
    player_y: int,
    flags: dict[str, bool],
) -> LandmarkEvent | None:
    """未訪問ランドマークのうち、マンハッタン距離で接触範囲内のものを最初に返す。"""
    for event in LANDMARK_EVENTS:
        if flags.get(event.flag_name, False):
            continue
        distance = abs(player_x - event.x) + abs(player_y - event.y)
        if distance <= event.radius:
            return event
    return None


def find_landmark_at(player_x: int, player_y: int) -> LandmarkEvent | None:
    """訪問済みかどうかに関わらず、接触範囲内のランドマークを返す。"""
    for event in LANDMARK_EVENTS:
        distance = abs(player_x - event.x) + abs(player_y - event.y)
        if distance <= event.radius:
            return event
    return None


def resolve_scene(event: LandmarkEvent, flags: dict[str, bool], glitch_lord_defeated: bool) -> str:
    """プレイヤーの進行状況に応じて、該当ランドマークで流すべきシーン名を決める。"""
    if not flags.get(event.flag_name, False):
        return event.scene_name
    if (
        glitch_lord_defeated
        and event.epilogue_scene
        and event.epilogue_flag
        and not flags.get(event.epilogue_flag, False)
    ):
        return event.epilogue_scene
    return event.repeat_scene or event.scene_name
