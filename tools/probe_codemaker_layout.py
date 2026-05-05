"""Code Maker bundle layout を模擬して setup_image_banks の挙動を検証する probe。

確認したい挙動:
  1. resolve_pyxres_path が bundle_dir の my_resource.pyxres を返す
  2. setup_image_banks 後に self.pyxres_loaded == True
  3. bake_world_to_tilemap が早期リターン → tilemap が pyxres そのまま

これが全部 OK なら、Pyxel Code Maker の "Run" でも同じく pyxres が使われるはず。
ローカルで失敗するなら、Code Maker でも失敗している。
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pyxel  # noqa: E402

LOG_PATH = Path("/tmp/probe_codemaker_layout.log")
LOG = LOG_PATH.open("w", buffering=1)


def log(msg: str) -> None:
    LOG.write(msg + "\n")
    LOG.flush()


def main() -> int:
    # 1) bundle layout を tempdir に作る:
    #     <tmp>/block-quest/main.py
    #     <tmp>/block-quest/my_resource.pyxres
    tmp = tempfile.mkdtemp(prefix="probe_bundle_")
    bundle = Path(tmp) / "block-quest"
    bundle.mkdir()
    fake_main = bundle / "main.py"
    fake_main.write_text("# fake bundle main for probe\n", encoding="utf-8")
    bundle_pyxres = bundle / "my_resource.pyxres"
    shutil.copy(ROOT / "assets" / "blockquest.pyxres", bundle_pyxres)
    log(f"bundle layout: {bundle}")
    log(f"  main.py:           {fake_main} (size={fake_main.stat().st_size})")
    log(f"  my_resource.pyxres: {bundle_pyxres} (size={bundle_pyxres.stat().st_size})")

    # 2) resolve_pyxres_path が bundle 内 my_resource.pyxres を返すか
    from src.shared.services.image_banks import ImageBanks, resolve_pyxres_path

    resolved = resolve_pyxres_path(fake_main)
    log(f"\n[step 2] resolve_pyxres_path -> {resolved}")
    assert resolved == bundle_pyxres.resolve(), f"FAIL: {resolved=}"
    log("  OK: bundle_dir/my_resource.pyxres が選ばれる")

    # 3) setup_image_banks 経由で pyxres_loaded == True になるか
    pyxel.init(256, 256, title="probe", display_scale=1)

    import src.runtime.main_runtime as M

    original_file = M.__file__
    M.__file__ = str(fake_main)
    log(f"\n[step 3] M.__file__ を {M.__file__} に差し替えて setup_image_banks")

    class _FakeGame:
        pass

    game = _FakeGame()
    # bake_world_to_tilemap が触るフィールド（早期リターンするので未参照になるはず）
    game.world_map = None
    game.dungeon_map = None
    game.dungeon_template = None
    game.dungeon_template_rooms = None
    game.dungeon_spawn = None

    ib = ImageBanks(game=game)
    try:
        ib.setup_image_banks()
    finally:
        M.__file__ = original_file

    log(f"  pyxres_loaded: {ib.pyxres_loaded}")
    log(f"  pyxres_path:   {ib.pyxres_path}")
    if not ib.pyxres_loaded:
        log("  ★ FAIL: bundle layout でも pyxres_loaded が False のまま")
        log("    → setup_image_banks が pyxres を読めていない（pyxel.load が失敗 or path 不一致）")
        return 2
    log("  OK: bundle layout で pyxres_loaded == True")

    # 4) bake_world_to_tilemap が早期リターンするか
    log("\n[step 4] bake_world_to_tilemap を呼ぶ（pyxres_loaded=True なので早期リターン期待）")
    # tilemap の現状を記憶
    sample = (60, 42)  # 適当な座標
    before = pyxel.tilemaps[0].pget(*sample)
    ib.bake_world_to_tilemap()
    after = pyxel.tilemaps[0].pget(*sample)
    log(f"  tilemap[0].pget{sample}: before={before} after={after}")
    if before != after:
        log("  ★ FAIL: bake が早期リターンせず tilemap を書き換えた")
        return 3
    log("  OK: bake は no-op（pyxres = SSoT 守られている）")

    log("\n=== ALL PASS: ローカルでは bundle layout の SSoT が完全に機能 ===")
    log("  → Code Maker 上で反映されない原因は別箇所:")
    log("    - HP にデプロイされている zip が古い世代の可能性大")
    log("    - or Pyxel WASM 環境特有の挙動 (M.__file__ や仮想 FS)")
    return 0


if __name__ == "__main__":
    rc = main()
    LOG.close()
    sys.exit(rc)
