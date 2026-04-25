"""pyxres を world_map の SSoT として尊重しているか headless で検証する probe。

manage-pyxel スキル「タイルマップ SSoT 検証」雛形に基づく。

実行:
    xvfb-run -a env SDL_AUDIODRIVER=dummy .venv/bin/python tools/probe_tilemap_ssot.py

期待:
    setup_world_tilemap 後の (30,21) と (28,20) が
    pyxres 直読み時の値と完全一致すること。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pyxel  # noqa: E402

LOG_PATH = Path("/tmp/probe_tilemap.log")
LOG = LOG_PATH.open("w", buffering=1)


def log(msg: str) -> None:
    LOG.write(msg + "\n")
    LOG.flush()


TARGETS = [(30, 21), (28, 20)]


def sample(x: int, y: int) -> list[tuple[int, int]]:
    return [
        pyxel.tilemaps[0].pget(2 * x + dx, 2 * y + dy)
        for dy in range(2)
        for dx in range(2)
    ]


def main() -> int:
    pyxel.init(256, 256, title="probe", display_scale=1)
    pyxres_path = ROOT / "assets" / "blockquest.pyxres"
    pyxel.load(str(pyxres_path))

    log("=== pyxres 直読み (BEFORE) ===")
    before = {(x, y): sample(x, y) for (x, y) in TARGETS}
    for (x, y), s in before.items():
        log(f"  ({x},{y}): {s}")

    from src.shared.services.image_banks import ImageBanks
    from src.shared.services.world_generation import generate_world_map

    class _G:
        pass

    g = _G()
    g.world_map = generate_world_map()
    g.dungeon_map = None
    g.dungeon_template = None
    g.dungeon_template_rooms = None
    g.dungeon_spawn = None

    ib = ImageBanks(game=g)
    ib.setup_image_banks()
    ib.setup_world_tilemap()

    log("=== setup_world_tilemap 後 (AFTER) ===")
    after = {(x, y): sample(x, y) for (x, y) in TARGETS}
    for (x, y), s in after.items():
        log(f"  ({x},{y}): {s}")

    log("=== 差分 ===")
    violated = False
    for key in TARGETS:
        if before[key] != after[key]:
            log(f"  ★ ({key[0]},{key[1]}) BEFORE={before[key]} AFTER={after[key]}")
            violated = True
    if not violated:
        log("  なし（SSoT OK）")

    LOG.close()
    return 1 if violated else 0


if __name__ == "__main__":
    sys.exit(main())
