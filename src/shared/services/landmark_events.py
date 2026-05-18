"""ワールドマップ上のランドマーク接触判定とシーン解決。

このファイルに含まれる関数・クラス：

- ランドマーク 1 件分の座標・半径・初回／再訪／エピローグのシーン名を持つデータクラス LandmarkEvent
- 未訪問ランドマークのうち接触範囲内のものを最初に返す public 関数 find_landmark_event
- 訪問済みかどうかに関わらず接触範囲内のランドマークを返す public 関数 find_landmark_at
- プレイヤーの進行状況に応じて、該当ランドマークで流すべきシーン名を決める public 関数 resolve_scene
- 未訪問かつ接触範囲内の最初の event を返す内部関数 _find_first_unvisited_landmark
- LANDMARK_EVENTS を走査して接触範囲内の最初の event を返す内部関数 _find_first_landmark_at
- 初回／再訪／エピローグ／再訪の優先順位で event のシーン名を組み立てる内部関数 _resolve_landmark_scene
- glitch_lord 撃破後でエピローグ未視聴ならエピローグへ進めて良いかを返す述語 _is_epilogue_due

Problems:
    - public 関数に for ループと if/elif を直書きすると、入口契約と探索ルールが
      同じ階層に混ざって読みにくくなる。
    - resolve_scene の「撃破済 and エピローグあり and フラグ and 未視聴」のような
      多項 and 条件を public 関数に置くと、新しい進行状況を追加するたびに
      公開シグネチャ周辺を触ることになる。

Solutions:
    - 接触判定の探索ループは private helper（_find_first_unvisited_landmark /
      _find_first_landmark_at）に切り出し、public 関数は「private 委譲 + return」
      のステップ列に揃える。
    - エピローグ遷移可否は述語 _is_epilogue_due にまとめ、resolve_scene 側は
      初回／エピローグ／再訪の順に private helper へ委譲するだけにする。
"""
from __future__ import annotations

from dataclasses import dataclass


# === Public API ===

@dataclass(frozen=True)
class LandmarkEvent:
    """ワールドマップ上の接触イベント 1 件分（位置・半径・各シーン名）を表す。"""

    # === Public API ===

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
    """未訪問ランドマークのうち、マンハッタン距離で接触範囲内のものを最初に返す。

    Args:
        player_x: プレイヤーのワールドマップ X 座標。
        player_y: プレイヤーのワールドマップ Y 座標。
        flags: シナリオフラグ辞書（event.flag_name で訪問済み判定に使う）。
    Returns:
        最初に見つかった未訪問の LandmarkEvent。該当無しなら None。
    Policy:
        - 探索ループ自体は private helper に委譲し、本関数はステップ列に揃える。
    """
    return _find_first_unvisited_landmark(player_x, player_y, flags)


def find_landmark_at(player_x: int, player_y: int) -> LandmarkEvent | None:
    """訪問済みかどうかに関わらず、接触範囲内のランドマークを返す。

    Args:
        player_x: プレイヤーのワールドマップ X 座標。
        player_y: プレイヤーのワールドマップ Y 座標。
    Returns:
        接触範囲内にある最初の LandmarkEvent。該当無しなら None。
    Policy:
        - flags を見ずに座標だけで判定する。探索ループは private helper に委ねる。
    """
    return _find_first_landmark_at(player_x, player_y)


def resolve_scene(
    event: LandmarkEvent,
    flags: dict[str, bool],
    glitch_lord_defeated: bool,
) -> str:
    """プレイヤーの進行状況に応じて、該当ランドマークで流すべきシーン名を決める。

    Args:
        event: 対象の LandmarkEvent。
        flags: シナリオフラグ辞書（訪問済み／エピローグ視聴済みの判定に使う）。
        glitch_lord_defeated: GlitchLord 撃破済みなら True。
    Returns:
        当該シチュエーションで再生すべきシーン名。
    Policy:
        - 初回／エピローグ／再訪の優先順位は private helper に委ねる。
    """
    return _resolve_landmark_scene(event, flags, glitch_lord_defeated)


# === Internal helpers (private) ===

def _find_first_unvisited_landmark(
    player_x: int,
    player_y: int,
    flags: dict[str, bool],
) -> LandmarkEvent | None:
    """LANDMARK_EVENTS を走査して flags 未訪問かつ接触範囲内の最初の event を返す。

    Args:
        player_x: プレイヤーのワールドマップ X 座標。
        player_y: プレイヤーのワールドマップ Y 座標。
        flags: シナリオフラグ辞書（event.flag_name で訪問済み判定）。
    Returns:
        最初に見つかった未訪問の LandmarkEvent。該当無しなら None。
    Policy:
        - flags.get(flag_name, False) が True の event は飛ばす。
    """
    for event in LANDMARK_EVENTS:
        if flags.get(event.flag_name, False):
            continue
        distance = abs(player_x - event.x) + abs(player_y - event.y)
        if distance <= event.radius:
            return event
    return None


def _find_first_landmark_at(
    player_x: int,
    player_y: int,
) -> LandmarkEvent | None:
    """LANDMARK_EVENTS を走査して接触範囲内の最初の event を返す。

    Args:
        player_x: プレイヤーのワールドマップ X 座標。
        player_y: プレイヤーのワールドマップ Y 座標。
    Returns:
        接触範囲内にある最初の LandmarkEvent。該当無しなら None。
    Policy:
        - flags は見ない（訪問済みでも返す）。
    """
    for event in LANDMARK_EVENTS:
        distance = abs(player_x - event.x) + abs(player_y - event.y)
        if distance <= event.radius:
            return event
    return None


def _resolve_landmark_scene(
    event: LandmarkEvent,
    flags: dict[str, bool],
    glitch_lord_defeated: bool,
) -> str:
    """初回／再訪／エピローグ／再訪の優先順位で event のシーン名を組み立てる。

    Args:
        event: 対象の LandmarkEvent。
        flags: シナリオフラグ辞書。
        glitch_lord_defeated: GlitchLord 撃破済みなら True。
    Returns:
        当該シチュエーションで再生すべきシーン名。
    Policy:
        - 初回 → エピローグ → 再訪 の順に評価し、エピローグ条件は述語に委ねる。
    """
    if not flags.get(event.flag_name, False):
        return event.scene_name
    if _is_epilogue_due(event, flags, glitch_lord_defeated):
        return event.epilogue_scene
    return event.repeat_scene or event.scene_name


def _is_epilogue_due(
    event: LandmarkEvent,
    flags: dict[str, bool],
    glitch_lord_defeated: bool,
) -> bool:
    """glitch_lord 撃破後でエピローグ未視聴ならエピローグへ進めて良いかを返す。

    Args:
        event: 対象の LandmarkEvent（epilogue_scene / epilogue_flag を参照）。
        flags: シナリオフラグ辞書（エピローグ視聴フラグを判定）。
        glitch_lord_defeated: GlitchLord 撃破済みなら True。
    Returns:
        エピローグシーンを返すべきなら True。
    Policy:
        - epilogue_scene と epilogue_flag が両方ある event だけ True になり得る。
        - エピローグ視聴済みなら False。
    """
    if not glitch_lord_defeated:
        return False
    if not event.epilogue_scene:
        return False
    if not event.epilogue_flag:
        return False
    return not flags.get(event.epilogue_flag, False)
