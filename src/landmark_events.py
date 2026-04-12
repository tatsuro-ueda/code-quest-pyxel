from __future__ import annotations

"""Landmark proximity checks for overworld interactions.

世界樹と通信塔を「初訪問 / 再訪問 / クリア後エピローグ」の3状態で扱う。
JS版 `interactWorldTree` / `interactTower` / `queueTowerEpilogue` の簡易ポート。
"""


from dataclasses import dataclass


@dataclass(frozen=True)
class LandmarkEvent:
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
    """Return the first unseen landmark event within Manhattan distance.

    互換用: 初訪問専用。再訪問やエピローグを扱いたい場合は
    find_landmark_at + resolve_scene を使う。
    """
    for event in LANDMARK_EVENTS:
        if flags.get(event.flag_name, False):
            continue
        distance = abs(player_x - event.x) + abs(player_y - event.y)
        if distance <= event.radius:
            return event
    return None


def find_landmark_at(player_x: int, player_y: int) -> LandmarkEvent | None:
    """Return any landmark within range, regardless of visit flags."""
    for event in LANDMARK_EVENTS:
        distance = abs(player_x - event.x) + abs(player_y - event.y)
        if distance <= event.radius:
            return event
    return None


def resolve_scene(event: LandmarkEvent, flags: dict[str, bool], boss_defeated: bool) -> str:
    """Decide which scene to play for an event based on player flags."""
    # First visit
    if not flags.get(event.flag_name, False):
        return event.scene_name
    # Boss defeated and epilogue not yet played
    if (
        boss_defeated
        and event.epilogue_scene
        and event.epilogue_flag
        and not flags.get(event.epilogue_flag, False)
    ):
        return event.epilogue_scene
    # Otherwise, repeat scene (or first scene if no repeat defined)
    return event.repeat_scene or event.scene_name
