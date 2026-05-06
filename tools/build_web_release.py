from __future__ import annotations

"""Block Quest Web release builder (P3-D で dev/prod 単一化)。

本番 1 本の artifacts を `output_dir/dist/` 配下に書き出す（`pyxel.html` /
`pyxel.pyxapp` / `play.html` / `code-maker.zip`）。開発版ビルドや preview
承認フローは全て削除済み。kid-pixel `index.html` は build から切り離し済
（2026-05-06）。
"""

import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_release_artifacts import (  # noqa: E402
    CODEMAKER_OUTPUT_FILE,
    DIST_DIR,
    DIST_HTML_FILE,
    DIST_INDEX_FILE,
    DIST_PLAY_FILE,
    DIST_PYXAPP_FILE,
    build_codemaker_release,
    dist_output_dir,
    prune_legacy_root_outputs,
    stage_release,
    write_wrapper_outputs,
)
from tools.render_release_selector import (  # noqa: E402
    NORMAL_CHANGE_LIST_DEPENDENCIES,
    generate_wrapper,
    versioned_asset_url,
)
from tools.resolve_release_source_of_truth import (  # noqa: E402
    build_cache_token,
)


def resolve_pyxel_command(root: Path) -> list[str]:
    """pyxel CLI を解決する（venv > module > system PATH の順）。"""
    root = root.resolve()
    venv_python = root / ".venv" / "bin" / "python"
    if venv_python.exists():
        return [str(venv_python), "-m", "pyxel"]
    try:
        pyxel_spec = importlib.util.find_spec("pyxel")
    except ValueError:
        pyxel_spec = None
    if pyxel_spec is not None:
        return [sys.executable, "-m", "pyxel"]
    import_check = subprocess.run(
        [sys.executable, "-c", "import pyxel"],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if import_check.returncode == 0:
        return [sys.executable, "-m", "pyxel"]
    pyxel_cli = shutil.which("pyxel")
    if pyxel_cli:
        return [pyxel_cli]
    raise FileNotFoundError("Unable to find a Pyxel CLI or Python environment with Pyxel")


def build_web_release(
    root: Path,
    *,
    output_dir: Path | None = None,
    work_dir: Path | None = None,
) -> tuple[Path, Path, Path]:
    """本番 1 本を output_dir にビルドする。"""
    root = root.resolve()
    output_dir = output_dir.resolve() if output_dir else root
    dist_dir = dist_output_dir(output_dir)
    work_dir = work_dir.resolve() if work_dir else (root / ".build" / "web_release")
    app_dir = work_dir / "app"
    app_name = app_dir.name
    pyxel_command = resolve_pyxel_command(root)
    current_token = build_cache_token(root, NORMAL_CHANGE_LIST_DEPENDENCIES)

    stage_release(root, app_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [*pyxel_command, "package", app_dir.name, f"{app_dir.name}/main.py"],
        cwd=work_dir,
        check=True,
    )
    subprocess.run(
        [*pyxel_command, "app2html", f"{app_name}.pyxapp"],
        cwd=work_dir,
        check=True,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)
    prune_legacy_root_outputs(output_dir)
    pyxapp_path = output_dir / DIST_PYXAPP_FILE
    html_path = output_dir / DIST_HTML_FILE
    shutil.copy2(work_dir / f"{app_name}.pyxapp", pyxapp_path)
    shutil.copy2(work_dir / f"{app_name}.html", html_path)
    build_codemaker_release(
        root,
        main_source=root / "main.py",
        resource_source=root / "assets" / "blockquest.pyxres",
        output_path=output_dir / CODEMAKER_OUTPUT_FILE,
    )

    wrapper_path = generate_wrapper(
        work_dir,
        root,
        pyxel_html_name=versioned_asset_url("pyxel.html", current_token),
        page_kind="production",
    )
    play_path, _ = write_wrapper_outputs(wrapper_path, dist_dir)

    # NOTE (2026-05-06): kid-pixel `index.html` は手書き正本 + post-commit hook
    # による自動更新で管理する (tools/update_top_changes.py + render_top_changes.py)。
    # `make build` は dist/ 配下のみを生成し、root index.html には触らない。

    return pyxapp_path, html_path, play_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Block Quest Web release")
    parser.parse_args()
    build_web_release(ROOT)


if __name__ == "__main__":
    main()
