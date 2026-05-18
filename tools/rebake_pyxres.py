"""image bank layout 変更後に assets/blockquest.pyxres を再 bake する probe。

Problems:
    - image bank レイアウトを変えたあとは pyxres を再生成しないと
      Pyxel runtime 側と SSoT がずれる。手で確実に再生成する手段が要る。
    - 失敗したときに既存の pyxres を壊して終わると、リカバリ手順が増える。

Solutions:
    - 既存 pyxres を .bak に退避してから ImageBanks の setup を回し、
      pyxel.save が走った時点で新 pyxres を確定する CLI を提供する。
    - 失敗時は .bak を pyxres に戻して原状回復し、成功時のみ .bak を削除する。

xvfb-run 経由で headless 実行する想定:

    SDL_VIDEODRIVER=x11 xvfb-run -a python tools/rebake_pyxres.py

手順:
  1. 既存 assets/blockquest.pyxres を退避（.bak）
  2. pyxel.init で Pyxel runtime を起動
  3. ImageBanks.setup_image_banks() / setup_world_tilemap() を直接呼ぶ
     - pyxres 不在 → fallback で paint_*_bank
       → regenerate_*_tilemap_fallback → pyxel.save
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


# === Public API ===


def run_rebake() -> int:
    """既存 pyxres を退避してから再 bake し、exit code を返す。

    Returns:
        int: 0=成功 / 1=失敗（バックアップから復旧済み）。

    Policy:
        - backup → init → bake → cleanup の 4 ステップに private helper を順に委譲する。
    """
    _save_existing_to_backup()
    rc = _bake_with_pyxel()
    return rc


# === Internal helpers (private) ===


def _save_existing_to_backup() -> None:
    """既存 pyxres を .bak に退避する（無ければ告知だけ）。

    Policy:
        - すでに .bak がある場合は上書きする（最新の作業のみ残す）。
    """
    if PYXRES.exists():
        _move_to_backup()
        return
    print(f"[rebake] no existing {PYXRES}; will create fresh")


def _move_to_backup() -> None:
    """PYXRES を BACKUP にリネームする。

    Policy:
        - .bak が既存なら削除してから rename する。
    """
    if BACKUP.exists():
        BACKUP.unlink()
    PYXRES.rename(BACKUP)
    print(f"[rebake] backed up: {PYXRES} -> {BACKUP}")


def _restore_on_failure() -> None:
    """失敗時に .bak を pyxres に戻す。

    Policy:
        - pyxres が無く .bak がある場合だけ restore する（成功状態を踏まない）。
    """
    if _can_restore_backup():
        BACKUP.rename(PYXRES)
        print(f"[rebake] restored backup: {BACKUP} -> {PYXRES}")


def _can_restore_backup() -> bool:
    """.bak から restore できる状態かを判定する。

    Returns:
        bool: pyxres が無く .bak がある場合のみ True。

    Policy:
        - 成功直後（pyxres あり）に走らせても破壊しないようガードする。
    """
    if PYXRES.exists():
        return False
    return BACKUP.exists()


def _bake_with_pyxel() -> int:
    """pyxel.init を立ててから bake を実行し finally で quit する。

    Returns:
        int: 0=成功 / 1=失敗。

    Policy:
        - pyxel runtime のセットアップと teardown を 1 箇所に閉じる。
    """
    import pyxel
    pyxel.init(256, 256, title="rebake", fps=30)
    try:
        return _try_bake()
    finally:
        _quiet_pyxel_quit()


def _try_bake() -> int:
    """ImageBanks を回して pyxres を生成する。失敗時は .bak から復旧する。

    Returns:
        int: 0=成功 / 1=失敗。

    Policy:
        - 例外時は restore を呼んで原状に戻し、メッセージを出す。
    """
    try:
        _run_image_banks_setup()
        _ensure_pyxres_produced()
        _report_success()
        _remove_backup_if_any()
        return 0
    except Exception as exc:
        print(f"[rebake] FAIL: {exc}")
        _restore_on_failure()
        return 1


def _run_image_banks_setup() -> None:
    """ImageBanks を作って setup_image_banks / setup_world_tilemap を呼ぶ。

    Policy:
        - game は属性アクセスだけ通れば良いので SimpleNamespace で十分。
    """
    from src.shared.services.image_banks import ImageBanks

    game = types.SimpleNamespace()
    ib = ImageBanks(game=game)
    ib.setup_image_banks()
    ib.setup_world_tilemap()


def _ensure_pyxres_produced() -> None:
    """setup_world_tilemap が pyxres を生成したことを確認する。

    Policy:
        - 不在なら RuntimeError を投げ、_try_bake が .bak から復旧する。
    """
    if PYXRES.exists():
        return
    raise RuntimeError(
        f"setup_world_tilemap did not produce {PYXRES} "
        "(check pyxres_path resolution / fallback path)"
    )


def _report_success() -> None:
    """成功時のサイズ付きメッセージを出す。

    Policy:
        - 観測しやすいよう bytes 単位でサイズを併記する。
    """
    print(f"[rebake] success: {PYXRES} ({PYXRES.stat().st_size} bytes)")


def _remove_backup_if_any() -> None:
    """成功時の .bak を削除する。

    Policy:
        - 既に成功後の状態に依存するので、確認はせず unlink を試みる。
    """
    if not BACKUP.exists():
        return
    BACKUP.unlink()
    print(f"[rebake] removed backup: {BACKUP}")


def _quiet_pyxel_quit() -> None:
    """pyxel.quit を try/except で包む（既に quit 済みでも黙る）。

    Policy:
        - finally から呼ぶので失敗しても上位に伝えない。
    """
    try:
        import pyxel
        pyxel.quit()
    except Exception:
        pass


if __name__ == "__main__":
    sys.exit(run_rebake())
