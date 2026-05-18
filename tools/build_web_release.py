"""Block Quest Web release builder (P3-D で dev/prod 単一化)。

このファイルに含まれる関数・クラス：

- resolve_pyxel_command: pyxel CLI を解決する（venv > module > system PATH の順）
- build_web_release: 本番 1 本を output_dir にビルドする
- run_build: argparse 経由で build_web_release を呼ぶ CLI 入口

Problems:
    - dev/prod を分けてビルドする旧フローのままだと、artifacts が二重化して
      「どちらが本物か」を毎回確認する手間が増える（P3-D で単一化済み）。
    - pyxel CLI の在りかは環境ごとに違い（venv / module / system PATH）、
      ベタ書きすると CI と手元で挙動がズレる。
    - kid-pixel `index.html` を build から触ると、post-commit hook で
      自動更新する手書き正本との整合が崩れる。

Solutions:
    - build_web_release を「stage → package → 配置 → wrapper」のステップ列に
      揃え、各ステップは private helper に閉じ込める。
    - resolve_pyxel_command は判定ロジックを private に委譲し、本体は薄い
      ステップ列のみに保つ。
    - root index.html には触らず、dist/ 配下のみを生成対象とする。
"""
from __future__ import annotations

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
    DIST_HTML_FILE,
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


# === Public API ===


def resolve_pyxel_command(root: Path) -> list[str]:
    """pyxel CLI を解決する（venv > module > system PATH の順）。

    Args:
        root: プロジェクトルート。venv の探索基点として使う。

    Returns:
        list[str]: subprocess に渡せる pyxel コマンド配列。

    Raises:
        FileNotFoundError: 解決できる pyxel が一つもないとき。

    Policy:
        - 判定ロジックは private helper に閉じ込め、本体は委譲のみ。
    """
    return _resolve_pyxel_command(root.resolve())


def build_web_release(
    root: Path,
    *,
    output_dir: Path | None = None,
    work_dir: Path | None = None,
) -> tuple[Path, Path, Path]:
    """本番 1 本を output_dir にビルドする。

    Args:
        root: プロジェクトルート。staging / pyxel CLI 解決の起点。
        output_dir: 成果物の出力ディレクトリ（既定は root）。
        work_dir: 作業ディレクトリ（既定は root/.build/web_release）。

    Returns:
        tuple[Path, Path, Path]: (pyxapp_path, html_path, play_path)。

    Policy:
        - 本体は「context 解決 → 実行委譲」のステップ列に揃える。
        - 各 step は private helper に閉じ込め、root index.html は触らない。
    """
    context = _build_release_context(root, output_dir, work_dir)
    return _execute_release_steps(context)


def run_build() -> None:
    """argparse 経由で build_web_release を呼ぶ CLI 入口。

    Policy:
        - 引数なしの最小 CLI を維持し、build_web_release(ROOT) だけ呼ぶ。
        - 既存の `python tools/build_web_release.py` 起動と互換にする。
    """
    _parse_run_build_args()
    build_web_release(ROOT)


# === Internal helpers (private) ===


def _parse_run_build_args() -> argparse.Namespace:
    """`build_web_release` CLI の argparse を実行して Namespace を返す。

    Returns:
        argparse.Namespace: 解析済みの引数（現状は中身を使わない）。

    Policy:
        - 既存 CLI 互換のため引数なしのまま固定する。
    """
    parser = argparse.ArgumentParser(
        description="Build Block Quest Web release")
    return parser.parse_args()


def _resolve_pyxel_command(root: Path) -> list[str]:
    """venv → module spec → import 実行 → which の順に pyxel CLI を解決する。

    Args:
        root: 解決済み（絶対パス）プロジェクトルート。

    Returns:
        list[str]: subprocess に渡せる pyxel コマンド配列。

    Raises:
        FileNotFoundError: どの候補でも解決できないとき。

    Policy:
        - 各候補は専用の private helper で取得し、None なら次の候補へ進む。
    """
    for resolver in (
        lambda: _resolve_from_venv(root),
        _resolve_from_module_spec,
        lambda: _resolve_via_import_check(root),
        _resolve_from_path,
    ):
        candidate = resolver()
        if candidate is not None:
            return candidate
    raise FileNotFoundError(
        "Unable to find a Pyxel CLI or Python environment with Pyxel")


def _resolve_from_venv(root: Path) -> list[str] | None:
    """root/.venv/bin/python があればそれで -m pyxel を返す。

    Args:
        root: プロジェクトルート。

    Returns:
        list[str] | None: venv 経由のコマンド、なければ None。

    Policy:
        - 存在チェックだけで判定し、import の成否までは見ない。
    """
    venv_python = root / ".venv" / "bin" / "python"
    if venv_python.exists():
        return [str(venv_python), "-m", "pyxel"]
    return None


def _resolve_from_module_spec() -> list[str] | None:
    """importlib で pyxel が見つかれば sys.executable -m pyxel を返す。

    Returns:
        list[str] | None: 解決できたコマンド、なければ None。

    Policy:
        - find_spec の ValueError は None として扱う（spec 不在と同義）。
    """
    try:
        pyxel_spec = importlib.util.find_spec("pyxel")
    except ValueError:
        pyxel_spec = None
    if pyxel_spec is not None:
        return [sys.executable, "-m", "pyxel"]
    return None


def _resolve_via_import_check(root: Path) -> list[str] | None:
    """subprocess で `python -c "import pyxel"` を試し、成功なら -m pyxel を返す。

    Args:
        root: subprocess の cwd に使うプロジェクトルート。

    Returns:
        list[str] | None: 解決できたコマンド、なければ None。

    Policy:
        - 標準出力・標準エラーは捨て、returncode だけで判定する。
    """
    import_check = subprocess.run(
        [sys.executable, "-c", "import pyxel"],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if import_check.returncode == 0:
        return [sys.executable, "-m", "pyxel"]
    return None


def _resolve_from_path() -> list[str] | None:
    """shutil.which で pyxel CLI を探し、見つかればそのパスを単体コマンドで返す。

    Returns:
        list[str] | None: 解決できたコマンド、なければ None。

    Policy:
        - system PATH 上の pyxel を最後の手段として使う。
    """
    pyxel_cli = shutil.which("pyxel")
    if pyxel_cli:
        return [pyxel_cli]
    return None


def _build_release_context(
    root: Path,
    output_dir: Path | None,
    work_dir: Path | None,
) -> dict:
    """build_web_release の入力を絶対パスに正規化して context dict を返す。

    Args:
        root: プロジェクトルート。
        output_dir: 成果物出力ディレクトリ（None なら root）。
        work_dir: 作業ディレクトリ（None なら root/.build/web_release）。

    Returns:
        dict: root / output_dir / work_dir / dist_dir / app_dir / pyxel_command
        / current_token を含む変更不可前提の dict。

    Policy:
        - パス解決と外部依存解決（pyxel CLI / cache token）を private helper に
          委譲し、ここは合成のみに留める。
    """
    paths = _resolve_release_paths(root, output_dir, work_dir)
    paths["pyxel_command"] = resolve_pyxel_command(paths["root"])
    paths["current_token"] = build_cache_token(
        paths["root"], NORMAL_CHANGE_LIST_DEPENDENCIES)
    return paths


def _resolve_release_paths(
    root: Path,
    output_dir: Path | None,
    work_dir: Path | None,
) -> dict:
    """root / output_dir / work_dir を絶対パスに揃え、派生パスも返す。

    Args:
        root: プロジェクトルート。
        output_dir: 出力先（None なら root）。
        work_dir: 作業ディレクトリ（None なら root/.build/web_release）。

    Returns:
        dict: root / output_dir / work_dir / dist_dir / app_dir を持つ dict。

    Policy:
        - resolve() と既定値の補完のみを担当し、外部依存は呼ばない。
    """
    resolved_root = root.resolve()
    resolved_output_dir = (
        output_dir.resolve() if output_dir else resolved_root)
    resolved_work_dir = (
        work_dir.resolve() if work_dir
        else (resolved_root / ".build" / "web_release"))
    return {
        "root": resolved_root,
        "output_dir": resolved_output_dir,
        "work_dir": resolved_work_dir,
        "dist_dir": dist_output_dir(resolved_output_dir),
        "app_dir": resolved_work_dir / "app",
    }


def _execute_release_steps(context: dict) -> tuple[Path, Path, Path]:
    """context を受けて stage→package→配置→wrapper を順に実行する。

    Args:
        context: _build_release_context が組み立てた dict。

    Returns:
        tuple[Path, Path, Path]: (pyxapp_path, html_path, play_path)。

    Policy:
        - 各ステップは private helper に委譲し、ここは順序のみ表現する。
    """
    _stage_and_package(context)
    pyxapp_path, html_path = _place_release_artifacts(context)
    play_path = _generate_play_wrapper(context)
    return pyxapp_path, html_path, play_path


def _stage_and_package(context: dict) -> None:
    """staging → pyxel package → pyxel app2html までを実行する。

    Args:
        context: _build_release_context が組み立てた dict。

    Policy:
        - stage_release と subprocess.run を順に呼ぶだけのステップ列。
    """
    root = context["root"]
    work_dir = context["work_dir"]
    app_dir = context["app_dir"]
    pyxel_command = context["pyxel_command"]
    stage_release(root, app_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    _run_pyxel_package(pyxel_command, work_dir, app_dir.name)
    _run_pyxel_app2html(pyxel_command, work_dir, app_dir.name)


def _run_pyxel_package(
    pyxel_command: list[str],
    work_dir: Path,
    app_name: str,
) -> None:
    """pyxel package を work_dir 配下で実行する。

    Args:
        pyxel_command: 解決済みの pyxel コマンド配列。
        work_dir: 作業ディレクトリ。
        app_name: staged app のディレクトリ名。

    Policy:
        - subprocess.run の引数組み立てをここに閉じ込める。
    """
    subprocess.run(
        [*pyxel_command, "package", app_name, f"{app_name}/main.py"],
        cwd=work_dir,
        check=True,
    )


def _run_pyxel_app2html(
    pyxel_command: list[str],
    work_dir: Path,
    app_name: str,
) -> None:
    """pyxel app2html を work_dir 配下で実行する。

    Args:
        pyxel_command: 解決済みの pyxel コマンド配列。
        work_dir: 作業ディレクトリ。
        app_name: staged app のディレクトリ名（pyxapp ファイル名のベース）。

    Policy:
        - subprocess.run の引数組み立てをここに閉じ込める。
    """
    subprocess.run(
        [*pyxel_command, "app2html", f"{app_name}.pyxapp"],
        cwd=work_dir,
        check=True,
    )


def _place_release_artifacts(context: dict) -> tuple[Path, Path]:
    """output_dir / dist_dir を整備し pyxapp / html / code-maker を配置する。

    Args:
        context: _build_release_context が組み立てた dict。

    Returns:
        tuple[Path, Path]: (pyxapp_path, html_path)。

    Policy:
        - prune → copy → codemaker の各ステップを private helper に委譲する。
    """
    _ensure_output_dirs(context["output_dir"], context["dist_dir"])
    pyxapp_path, html_path = _copy_pyxel_outputs(
        context["work_dir"],
        context["app_dir"].name,
        context["output_dir"],
    )
    _build_codemaker_artifact(context["root"], context["output_dir"])
    return pyxapp_path, html_path


def _ensure_output_dirs(output_dir: Path, dist_dir: Path) -> None:
    """output_dir / dist_dir を作成し、root 直下の旧 artifact を掃除する。

    Args:
        output_dir: 配布物の出力先。
        dist_dir: dist サブディレクトリ。

    Policy:
        - mkdir(parents=True, exist_ok=True) と prune を順に呼ぶだけ。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)
    prune_legacy_root_outputs(output_dir)


def _copy_pyxel_outputs(
    work_dir: Path,
    app_name: str,
    output_dir: Path,
) -> tuple[Path, Path]:
    """pyxel package が出力した pyxapp / html を output_dir にコピーする。

    Args:
        work_dir: pyxel package の作業ディレクトリ。
        app_name: staged app 名（成果物のベース名）。
        output_dir: 出力先（dist 親）。

    Returns:
        tuple[Path, Path]: (pyxapp_path, html_path)。

    Policy:
        - shutil.copy2 を 2 回呼ぶだけの薄いステップ列。
    """
    pyxapp_path = output_dir / DIST_PYXAPP_FILE
    html_path = output_dir / DIST_HTML_FILE
    shutil.copy2(work_dir / f"{app_name}.pyxapp", pyxapp_path)
    shutil.copy2(work_dir / f"{app_name}.html", html_path)
    return pyxapp_path, html_path


def _build_codemaker_artifact(root: Path, output_dir: Path) -> Path:
    """code-maker.zip を生成し、生成先 Path を返す。

    Args:
        root: プロジェクトルート（main.py / pyxres の探索元）。
        output_dir: 出力先 dist 親ディレクトリ。

    Returns:
        Path: 生成された code-maker.zip のパス。

    Policy:
        - build_codemaker_release への薄い委譲のみ。
    """
    return build_codemaker_release(
        root,
        main_source=root / "main.py",
        resource_source=root / "assets" / "blockquest.pyxres",
        output_path=output_dir / CODEMAKER_OUTPUT_FILE,
    )


def _generate_play_wrapper(context: dict) -> Path:
    """play.html wrapper を生成し dist_dir に書き出す。

    Args:
        context: _build_release_context が組み立てた dict。

    Returns:
        Path: 生成された play.html のパス。

    Policy:
        - generate_wrapper → write_wrapper_outputs の 2 ステップ。
        - kid-pixel `index.html` には触らない（手書き正本を保護）。
    """
    wrapper_path = generate_wrapper(
        context["work_dir"],
        context["root"],
        pyxel_html_name=versioned_asset_url(
            "pyxel.html", context["current_token"]),
        page_kind="production",
    )
    play_path, _ = write_wrapper_outputs(wrapper_path, context["dist_dir"])
    return play_path


if __name__ == "__main__":
    run_build()
