"""image bank layout 変更後に assets/blockquest.pyxres を再 bake する probe。

xvfb-run 経由で headless 実行する想定:

    SDL_VIDEODRIVER=x11 xvfb-run -a python tools/rebake_pyxres.py

手順:
  1. 既存 assets/blockquest.pyxres を退避（.bak）
  2. pyxel.init で Pyxel runtime を起動
  3. ImageBanks.setup_image_banks() / setup_world_tilemap() を直接呼ぶ
     - pyxres 不在 → fallback で paint_*_bank → regenerate_*_tilemap_fallback → pyxel.save
  4. pyxel.quit で終了

新 pyxres が崩れていないか目視確認は人作業（Pyxel Code Maker で開いて確認）。
"""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "x11")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

PYXRES = (ROOT / "assets" / "blockquest.pyxres").resolve()
BACKUP = (ROOT / "assets" / "blockquest.pyxres.bak").resolve()


def _backup_existing() -> None:
    if PYXRES.exists():
        if BACKUP.exists():
            BACKUP.unlink()
        PYXRES.rename(BACKUP)
        print(f"[rebake] backed up: {PYXRES} -> {BACKUP}")
    else:
        print(f"[rebake] no existing {PYXRES}; will create fresh")


def _restore_on_failure() -> None:
    if not PYXRES.exists() and BACKUP.exists():
        BACKUP.rename(PYXRES)
        print(f"[rebake] restored backup: {BACKUP} -> {PYXRES}")


def main() -> int:
    _backup_existing()

    import pyxel
    pyxel.init(256, 256, title="rebake", fps=30)

    try:
        from src.shared.services.image_banks import ImageBanks

        game = types.SimpleNamespace()
        ib = ImageBanks(game=game)
        ib.setup_image_banks()
        ib.setup_world_tilemap()
        if not PYXRES.exists():
            raise RuntimeError(
                f"setup_world_tilemap did not produce {PYXRES} "
                "(check pyxres_path resolution / fallback path)"
            )
        print(f"[rebake] success: {PYXRES} ({PYXRES.stat().st_size} bytes)")
        if BACKUP.exists():
            BACKUP.unlink()
            print(f"[rebake] removed backup: {BACKUP}")
    except Exception as exc:
        print(f"[rebake] FAIL: {exc}")
        _restore_on_failure()
        return 1
    finally:
        try:
            pyxel.quit()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
