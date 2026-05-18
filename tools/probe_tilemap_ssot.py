"""pyxres を world_map の SSoT として尊重しているか headless で検証する probe。

Problems:
    - setup_world_tilemap が pyxres の値を踏み倒していないか、Pyxel runtime を
      手で立ち上げてタイル値を見比べないと確認できない。
    - 手動確認は CI / hook で回せず、SSoT 退行を CR / レビュー後まで見逃す。

Solutions:
    - pyxel.init → load → 直読みサンプル → setup → 再サンプル → 差分判定の
      パイプラインを headless 実行する probe CLI を提供する。
    - 差分が出れば exit 1、無ければ exit 0 として CI から呼べる防壁にする。

このファイルに含まれる関数・クラス：

- 経過ログをファイルに 1 行ずつ書き出すヘルパ
- 指定タイル座標の 2x2 サブタイル値をサンプリングする純粋関数
- probe パイプライン全体を起動して exit code を返す CLI 入口

manage-pyxel スキル「タイルマップ SSoT 検証」雛形に基づく。

実行:
    xvfb-run -a env SDL_AUDIODRIVER=dummy \\
        .venv/bin/python tools/probe_tilemap_ssot.py

期待:
    setup_world_tilemap 後の (30,21) と (28,20) が
    pyxres 直読み時の値と完全一致すること。
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pyxel  # noqa: E402

LOG_PATH = Path("/tmp/probe_tilemap.log")
LOG = LOG_PATH.open("w", buffering=1)
TARGETS = [(30, 21), (28, 20)]


# === Public API ===


def log(msg: str) -> None:
    """1 行を LOG ファイルに書き出して即フラッシュする。

    Args:
        msg: 書き出す本文（末尾改行は不要）。

    Policy:
        - probe の途中で SIGTERM されても直前まで残るよう常に flush する。
    """
    LOG.write(msg + "\n")
    LOG.flush()


def sample(x: int, y: int) -> list[tuple[int, int]]:
    """タイル座標 (x, y) の 2x2 サブタイル値を 4 要素で返す。

    Args:
        x: 8x8 タイル単位の x 座標。
        y: 8x8 タイル単位の y 座標。

    Returns:
        list[tuple[int, int]]: pyxel.tilemaps[0].pget の戻り値 4 件。

    Policy:
        - Pyxel の 16x16 タイルが内部 8x8 タイル 4 枚で表される前提に揃える。
    """
    return [
        pyxel.tilemaps[0].pget(2 * x + dx, 2 * y + dy)
        for dy in range(2)
        for dx in range(2)
    ]


def run_ssot_probe() -> int:
    """SSoT probe を実行して exit code を返す。

    Returns:
        int: 0=SSoT OK / 1=差分あり。

    Policy:
        - pyxel 初期化 / 直読み / setup / 再読み / 差分判定の各ステップを
          private helper に委譲し、ステップ列のみを維持する。
    """
    _initialize_pyxel_runtime()
    before = _capture_targets("=== pyxres 直読み (BEFORE) ===")
    _run_setup_world_tilemap()
    after = _capture_targets("=== setup_world_tilemap 後 (AFTER) ===")
    return _report_violation(before, after)


# === Internal helpers (private) ===


def _initialize_pyxel_runtime() -> None:
    """pyxel を初期化し、pyxres を直読みする。

    Policy:
        - probe 用の固定サイズで init し、assets/blockquest.pyxres を load する。
    """
    pyxel.init(256, 256, title="probe", display_scale=1)
    pyxres_path = ROOT / "assets" / "blockquest.pyxres"
    pyxel.load(str(pyxres_path))


def _capture_targets(
        header: str) -> dict[tuple[int, int], list[tuple[int, int]]]:
    """TARGETS の現在値をログに残しつつ dict として返す。

    Args:
        header: ログの見出し行。

    Returns:
        dict: (x, y) -> sample(x, y) の戻り値の辞書。

    Policy:
        - ログ出力と戻り値生成を 1 度の走査でまとめる。
    """
    log(header)
    snapshot = {(x, y): sample(x, y) for (x, y) in TARGETS}
    for (x, y), pixels in snapshot.items():
        log(f"  ({x},{y}): {pixels}")
    return snapshot


def _run_setup_world_tilemap() -> None:
    """ImageBanks.setup_world_tilemap を headless で 1 度走らせる。

    Policy:
        - world_generation 由来の world_map と dungeon 系 None 属性を持つ
          SimpleNamespace を game 代理として渡す（既存挙動と同一）。
    """
    from src.shared.services.image_banks import ImageBanks
    from src.shared.services.world_generation import generate_world_map

    game_stub = SimpleNamespace(
        world_map=generate_world_map(),
        dungeon_map=None,
        dungeon_template=None,
        dungeon_template_rooms=None,
        dungeon_spawn=None,
    )
    image_banks = ImageBanks(game=game_stub)
    image_banks.setup_image_banks()
    image_banks.setup_world_tilemap()


def _report_violation(
        before: dict[tuple[int, int], list[tuple[int, int]]],
        after: dict[tuple[int, int], list[tuple[int, int]]]) -> int:
    """BEFORE / AFTER の差分をログに書き、違反有無で exit code を返す。

    Args:
        before: 直読みサンプル。
        after: setup 後サンプル。

    Returns:
        int: 差分があれば 1、無ければ 0。

    Policy:
        - 1 件でも差分があれば SSoT 違反として 1 を返す。
    """
    log("=== 差分 ===")
    has_violation = _log_diffs(before, after)
    if not has_violation:
        log("  なし（SSoT OK）")
    LOG.close()
    return _exit_code_for(has_violation)


def _log_diffs(
        before: dict[tuple[int, int], list[tuple[int, int]]],
        after: dict[tuple[int, int], list[tuple[int, int]]]) -> bool:
    """BEFORE / AFTER を 1 件ずつ突き合わせ、差分行をログに書く。

    Args:
        before: 直読みサンプル。
        after: setup 後サンプル。

    Returns:
        bool: 1 件でも差分があれば True。

    Policy:
        - TARGETS の並び順に従って差分行を残し、boolean を集約して返す。
    """
    has_violation = False
    for key in TARGETS:
        if before[key] == after[key]:
            continue
        log(
            f"  ★ ({key[0]},{key[1]})"
            f" BEFORE={before[key]} AFTER={after[key]}"
        )
        has_violation = True
    return has_violation


def _exit_code_for(has_violation: bool) -> int:
    """違反有無から CLI exit code を導く。

    Args:
        has_violation: 1 件でも差分があれば True。

    Returns:
        int: True なら 1、False なら 0。

    Policy:
        - bool → int の変換責務をここに集約してステップ列を保つ。
    """
    if has_violation:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run_ssot_probe())
