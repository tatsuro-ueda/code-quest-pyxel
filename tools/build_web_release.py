from __future__ import annotations

"""Block Quest Web release builder (P3-D で dev/prod 単一化)。

本番 1 本の artifacts を output_dir/production/ と output_dir/index.html に
書き出す。開発版ビルドや preview 承認フローは全て削除済み。
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
    PRODUCTION_DIR,
    PRODUCTION_HTML_FILE,
    PRODUCTION_INDEX_FILE,
    PRODUCTION_PLAY_FILE,
    PRODUCTION_PYXAPP_FILE,
    build_codemaker_release,
    production_output_dir,
    prune_legacy_root_outputs,
    stage_release,
    write_wrapper_outputs,
)
from tools.render_release_selector import (  # noqa: E402
    NORMAL_CHANGE_LIST_DEPENDENCIES,
    generate_top_selector,
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
    production_dir = production_output_dir(output_dir)
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
    production_dir.mkdir(parents=True, exist_ok=True)
    prune_legacy_root_outputs(output_dir)
    pyxapp_path = output_dir / PRODUCTION_PYXAPP_FILE
    html_path = output_dir / PRODUCTION_HTML_FILE
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
    play_path, _ = write_wrapper_outputs(wrapper_path, production_dir)

    index_path = output_dir / "index.html"
    selector_path = generate_top_selector(
        work_dir,
        root,
        current_wrapper_name=versioned_asset_url("production/play.html", current_token),
        current_codemaker_zip=versioned_asset_url("production/code-maker.zip", current_token),
    )
    shutil.copy2(selector_path, index_path)

    return pyxapp_path, html_path, play_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Block Quest Web release")
    parser.parse_args()
    build_web_release(ROOT)


if __name__ == "__main__":
    main()
