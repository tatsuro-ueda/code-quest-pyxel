"""Landmark proximity checks for one-shot overworld messages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LandmarkEvent:
    scene_name: str
    flag_name: str
    x: int
    y: int
    radius: int = 3


LANDMARK_EVENTS = (
    LandmarkEvent(
        scene_name="landmark.tree.first",
        flag_name="landmarkTreeSeen",
        x=32,
        y=9,
    ),
    LandmarkEvent(
        scene_name="landmark.tower.first",
        flag_name="landmarkTowerSeen",
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
    """Return the first unseen landmark event within Manhattan distance."""
    for event in LANDMARK_EVENTS:
        if flags.get(event.flag_name, False):
            continue
        distance = abs(player_x - event.x) + abs(player_y - event.y)
        if distance <= event.radius:
            return event
    return None
