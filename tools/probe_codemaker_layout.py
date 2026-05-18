"""Code Maker bundle layout を模擬して setup_image_banks の挙動を検証する probe。

Problems:
    - Pyxel Code Maker の bundle layout (bundle_dir/my_resource.pyxres) で
      ローカルと同じく SSoT が機能しているか手元で確認できないと、
      Code Maker で反映されない原因を絞り込めない。

Solutions:
    - 一時ディレクトリに bundle layout を再現し、
      resolve_pyxres_path / setup_image_banks / bake_world_to_tilemap を
      順に呼んで期待挙動 (pyxres_loaded == True、bake 早期リターン) を確認する。
    - 失敗時は exit code 2 / 3 で原因を切り分け、Code Maker 上の問題か
      zip 世代か Pyxel WASM 環境特有かの判断材料を返す。

確認したい挙動:
  1. resolve_pyxres_path が bundle_dir の my_resource.pyxres を返す
  2. setup_image_banks 後に self.pyxres_loaded == True
  3. bake_world_to_tilemap が早期リターン → tilemap が pyxres そのまま
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pyxel  # noqa: E402

LOG_PATH = Path("/tmp/probe_codemaker_layout.log")
LOG = LOG_PATH.open("w", buffering=1)


# === Public API ===


def log(msg: str) -> None:
    """probe のログを /tmp とコンソールに残す。

    Args:
        msg: 1 行分のメッセージ。

    Policy:
        - append + flush で途中失敗でも痕跡を残す。
    """
    LOG.write(msg + "\n")
    LOG.flush()


def run_probe() -> int:
    """probe 全体を実行し exit code を返す。

    Returns:
        int: 0=成功 / 2=pyxres_loaded False / 3=bake が tilemap を破壊。

    Policy:
        - 4 ステップ (bundle 作成 / resolve / setup / bake) を private helper に委譲する。
    """
    bundle_paths = _create_fake_bundle()
    _verify_resolve(bundle_paths)
    rc = _verify_setup_and_bake(bundle_paths)
    return rc


# === Internal helpers (private) ===


def _create_fake_bundle() -> tuple[Path, Path, Path]:
    """tempdir に Code Maker bundle layout を作って 3 パスを返す。

    Returns:
        tuple[Path, Path, Path]: (bundle, fake_main, bundle_pyxres) の絶対パス。

    Policy:
        - assets/blockquest.pyxres をコピーして my_resource.pyxres として置く。
    """
    work_dir = tempfile.mkdtemp(prefix="probe_bundle_")
    bundle = Path(work_dir) / "block-quest"
    bundle.mkdir()
    fake_main = bundle / "main.py"
    fake_main.write_text("# fake bundle main for probe\n", encoding="utf-8")
    bundle_pyxres = bundle / "my_resource.pyxres"
    shutil.copy(ROOT / "assets" / "blockquest.pyxres", bundle_pyxres)
    log(f"bundle layout: {bundle}")
    log(
        f"  main.py:           {fake_main} "
        f"(size={fake_main.stat().st_size})"
    )
    log(
        f"  my_resource.pyxres: {bundle_pyxres} "
        f"(size={bundle_pyxres.stat().st_size})"
    )
    return bundle, fake_main, bundle_pyxres


def _verify_resolve(bundle_paths: tuple[Path, Path, Path]) -> None:
    """resolve_pyxres_path が bundle 内 my_resource.pyxres を返すか確認する。

    Args:
        bundle_paths: _create_fake_bundle が返した 3 パス。

    Policy:
        - 一致しなければ AssertionError で停止する（exit 1 相当）。
    """
    _bundle, fake_main, bundle_pyxres = bundle_paths
    from src.shared.services.image_banks import resolve_pyxres_path

    resolved = resolve_pyxres_path(fake_main)
    log(f"\n[step 2] resolve_pyxres_path -> {resolved}")
    assert resolved == bundle_pyxres.resolve(), f"FAIL: {resolved=}"
    log("  OK: bundle_dir/my_resource.pyxres が選ばれる")


def _verify_setup_and_bake(bundle_paths: tuple[Path, Path, Path]) -> int:
    """setup_image_banks 後の pyxres_loaded と bake 早期リターンを確認する。

    Args:
        bundle_paths: _create_fake_bundle が返した 3 パス。

    Returns:
        int: 0=成功 / 2=pyxres_loaded False / 3=bake が tilemap を破壊。

    Policy:
        - pyxel.init → setup_image_banks → 2 つのチェック helper に委譲する。
    """
    _bundle, fake_main, _bundle_pyxres = bundle_paths
    pyxel.init(256, 256, title="probe", display_scale=1)
    ib = _run_setup_image_banks(fake_main)
    rc_loaded = _check_pyxres_loaded(ib)
    if rc_loaded != 0:
        return rc_loaded
    rc_bake = _check_bake_is_noop(ib)
    if rc_bake != 0:
        return rc_bake
    _log_final_message()
    return 0


def _run_setup_image_banks(fake_main: Path) -> Any:
    """M.__file__ を差し替えた上で ImageBanks.setup_image_banks を実行する。

    Args:
        fake_main: bundle layout 内の main.py パス。

    Returns:
        ImageBanks: setup_image_banks 後のインスタンス。

    Policy:
        - 副作用を抑えるため finally で M.__file__ を必ず戻す。
    """
    from src.shared.services.image_banks import ImageBanks
    import src.runtime.main_runtime as M

    original_file = M.__file__
    M.__file__ = str(fake_main)
    log(f"\n[step 3] M.__file__ を {M.__file__} に差し替えて setup_image_banks")
    game = _make_fake_game()
    ib = ImageBanks(game=game)
    try:
        ib.setup_image_banks()
    finally:
        M.__file__ = original_file
    return ib


def _make_fake_game() -> Any:
    """bake_world_to_tilemap が触る最小フィールドを持つダミー game を返す。

    Returns:
        object: world_map など 5 属性を None にした SimpleNamespace 相当。

    Policy:
        - pyxres_loaded=True で早期リターンする想定なので値は全部 None で十分。
    """
    import types
    game = types.SimpleNamespace()
    game.world_map = None
    game.dungeon_map = None
    game.dungeon_template = None
    game.dungeon_template_rooms = None
    game.dungeon_spawn = None
    return game


def _check_pyxres_loaded(ib: Any) -> int:
    """pyxres_loaded == True かを確認し、失敗時は 2 を返す。

    Args:
        ib: setup_image_banks 済みの ImageBanks。

    Returns:
        int: 0=loaded / 2=False のまま。

    Policy:
        - 失敗時はログだけ残し、外側で exit code を取り扱う。
    """
    log(f"  pyxres_loaded: {ib.pyxres_loaded}")
    log(f"  pyxres_path:   {ib.pyxres_path}")
    if not ib.pyxres_loaded:
        log("  ★ FAIL: bundle layout でも pyxres_loaded が False のまま")
        log(
            "    → setup_image_banks が pyxres を読めていない"
            "（pyxel.load が失敗 or path 不一致）"
        )
        return 2
    log("  OK: bundle layout で pyxres_loaded == True")
    return 0


def _check_bake_is_noop(ib: Any) -> int:
    """bake_world_to_tilemap が tilemap を書き換えないことを確認し、失敗時は 3 を返す。

    Args:
        ib: setup_image_banks 済みの ImageBanks。

    Returns:
        int: 0=no-op / 3=書き換えあり。

    Policy:
        - 特定座標 (60, 42) を before/after で比較し、変化があれば破壊とみなす。
    """
    log(
        "\n[step 4] bake_world_to_tilemap を呼ぶ"
        "（pyxres_loaded=True なので早期リターン期待）"
    )
    sample = (60, 42)
    before = pyxel.tilemaps[0].pget(*sample)
    ib.bake_world_to_tilemap()
    after = pyxel.tilemaps[0].pget(*sample)
    log(f"  tilemap[0].pget{sample}: before={before} after={after}")
    if before != after:
        log("  ★ FAIL: bake が早期リターンせず tilemap を書き換えた")
        return 3
    log("  OK: bake は no-op（pyxres = SSoT 守られている）")
    return 0


def _log_final_message() -> None:
    """全パス時の最終メッセージを出す。

    Policy:
        - ローカル成功 → Code Maker 上の不一致は別箇所が原因と読み手に伝える。
    """
    log("\n=== ALL PASS: ローカルでは bundle layout の SSoT が完全に機能 ===")
    log("  → Code Maker 上で反映されない原因は別箇所:")
    log("    - HP にデプロイされている zip が古い世代の可能性大")
    log("    - or Pyxel WASM 環境特有の挙動 (M.__file__ や仮想 FS)")


if __name__ == "__main__":
    rc = run_probe()
    LOG.close()
    sys.exit(rc)
