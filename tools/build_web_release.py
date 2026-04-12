from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


RELEASE_FILES = (
    Path("main.py"),
    Path("assets/umplus_j10r.bdf"),
    Path("assets/blockquest.pyxres"),
)
RELEASE_DIRS = ()


def collect_release_paths(root: Path) -> list[Path]:
    root = root.resolve()
    release_paths: set[Path] = set()

    for rel_path in RELEASE_FILES:
        if (root / rel_path).is_file():
            release_paths.add(rel_path)

    for rel_path in RELEASE_DIRS:
        for path in (root / rel_path).rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            release_paths.add(path.relative_to(root))

    return sorted(release_paths, key=lambda path: path.as_posix())


def stage_release(root: Path, stage_dir: Path) -> list[Path]:
    root = root.resolve()
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)

    copied_paths = collect_release_paths(root)
    for rel_path in copied_paths:
        src = root / rel_path
        dst = stage_dir / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return copied_paths


def resolve_pyxel_command(root: Path) -> list[str]:
    root = root.resolve()
    venv_python = root / ".venv" / "bin" / "python"
    if venv_python.exists():
        return [str(venv_python), "-m", "pyxel"]
    if importlib.util.find_spec("pyxel") is not None:
        return [sys.executable, "-m", "pyxel"]
    pyxel_cli = shutil.which("pyxel")
    if pyxel_cli:
        return [pyxel_cli]
    raise FileNotFoundError("Unable to find a Pyxel CLI or Python environment with Pyxel")


def generate_wrapper(build_dir: Path, project_root: Path, pyxel_html_name: str = "pyxel.html") -> Path:
    """カスタムHTMLラッパーを生成する"""
    template_path = project_root / "templates" / "wrapper.html"
    template = template_path.read_text(encoding="utf-8")
    wrapper_html = template.replace("{{PYXEL_HTML_SRC}}", pyxel_html_name)
    output_path = build_dir / "index.html"
    output_path.write_text(wrapper_html, encoding="utf-8")
    return output_path


def build_web_release(
    root: Path,
    *,
    output_dir: Path | None = None,
    work_dir: Path | None = None,
) -> tuple[Path, Path, Path]:
    root = root.resolve()
    output_dir = output_dir.resolve() if output_dir else root
    work_dir = work_dir.resolve() if work_dir else (root / ".build" / "web_release")
    app_dir = work_dir / "app"
    app_name = app_dir.name
    pyxel_command = resolve_pyxel_command(root)

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
    pyxapp_path = output_dir / "pyxel.pyxapp"
    html_path = output_dir / "pyxel.html"
    shutil.copy2(work_dir / f"{app_name}.pyxapp", pyxapp_path)
    shutil.copy2(work_dir / f"{app_name}.html", html_path)

    # カスタムHTMLラッパー生成 → play.html に保存
    wrapper_path = generate_wrapper(work_dir, root)
    play_path = output_dir / "play.html"
    shutil.copy2(wrapper_path, play_path)

    # index.html が既に存在する場合（選択ページ等）は上書きしない
    index_path = output_dir / "index.html"
    if not index_path.exists():
        shutil.copy2(wrapper_path, index_path)

    return pyxapp_path, html_path, play_path


def generate_selector(
    build_dir: Path,
    project_root: Path,
    *,
    current_wrapper_name: str = "play.html",
    preview_wrapper_name: str = "play-preview.html",
    changes: list[str] | None = None,
) -> Path:
    """選択ページ（selector.html）を生成する"""
    template_path = project_root / "templates" / "selector.html"
    template = template_path.read_text(encoding="utf-8")
    if changes:
        change_list = "\n".join(f"      <li>{c}</li>" for c in changes)
    else:
        change_list = ""
    html = (
        template
        .replace("{{CHANGE_LIST}}", change_list)
        .replace("{{CURRENT_WRAPPER_SRC}}", current_wrapper_name)
        .replace("{{PREVIEW_WRAPPER_SRC}}", preview_wrapper_name)
    )
    output_path = build_dir / "index.html"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def validate_preview_files(root: Path) -> tuple[Path, list[str]]:
    """--preview に必要なファイルを検証し、変更リストを返す"""
    root = root.resolve()
    preview_py = root / "main_preview.py"
    if not preview_py.is_file():
        raise FileNotFoundError(
            f"main_preview.py not found at {preview_py}. "
            "Create it before running --preview."
        )
    meta_path = root / "preview_meta.json"
    changes: list[str] = []
    if meta_path.is_file():
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        changes = data.get("changes", [])
    return preview_py, changes


def promote(root: Path, *, choice: str) -> None:
    """おためし版を昇格、またはもとのまま版を維持する"""
    root = root.resolve()
    main_py = root / "main.py"
    preview_py = root / "main_preview.py"
    meta_json = root / "preview_meta.json"

    if choice == "preview":
        if preview_py.is_file():
            shutil.copy2(preview_py, main_py)
            preview_py.unlink()
    elif choice == "current":
        pass  # main.py はそのまま
    else:
        raise ValueError(f"Unknown promote choice: {choice!r}. Use 'preview' or 'current'.")

    # クリーンアップ
    if preview_py.is_file():
        preview_py.unlink()
    if meta_json.is_file():
        meta_json.unlink()


def build_preview_release(
    root: Path,
    *,
    output_dir: Path | None = None,
    work_dir: Path | None = None,
) -> tuple[Path, Path, Path, Path]:
    """2版ビルド: もとのまま版 + おためし版 + 選択ページ"""
    root = root.resolve()
    preview_py, changes = validate_preview_files(root)
    output_dir = output_dir.resolve() if output_dir else root
    work_dir = work_dir.resolve() if work_dir else (root / ".build" / "web_release")
    pyxel_command = resolve_pyxel_command(root)

    # --- もとのまま版 ---
    app_dir = work_dir / "app"
    stage_release(root, app_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    app_name = app_dir.name
    subprocess.run(
        [*pyxel_command, "package", app_name, f"{app_name}/main.py"],
        cwd=work_dir, check=True,
    )
    subprocess.run(
        [*pyxel_command, "app2html", f"{app_name}.pyxapp"],
        cwd=work_dir, check=True,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "pyxel.html"
    shutil.copy2(work_dir / f"{app_name}.html", html_path)

    # --- おためし版 ---
    preview_app_dir = work_dir / "app_preview"
    stage_release(root, preview_app_dir)
    # main.py をおためし版で上書き
    shutil.copy2(preview_py, preview_app_dir / "main.py")
    preview_app_name = preview_app_dir.name
    subprocess.run(
        [*pyxel_command, "package", preview_app_name, f"{preview_app_name}/main.py"],
        cwd=work_dir, check=True,
    )
    subprocess.run(
        [*pyxel_command, "app2html", f"{preview_app_name}.pyxapp"],
        cwd=work_dir, check=True,
    )
    preview_html_path = output_dir / "pyxel-preview.html"
    shutil.copy2(work_dir / f"{preview_app_name}.html", preview_html_path)

    # --- ラッパーHTML（iframe + 全画面ボタン）を2つ生成 ---
    current_wrapper = generate_wrapper(work_dir, root, pyxel_html_name="pyxel.html")
    play_path = output_dir / "play.html"
    shutil.copy2(current_wrapper, play_path)

    preview_wrapper_dir = work_dir / "preview_wrapper"
    preview_wrapper_dir.mkdir(parents=True, exist_ok=True)
    preview_wrapper = generate_wrapper(
        preview_wrapper_dir, root, pyxel_html_name="pyxel-preview.html"
    )
    play_preview_path = output_dir / "play-preview.html"
    shutil.copy2(preview_wrapper, play_preview_path)

    # --- 選択ページ ---
    selector_path = generate_selector(
        work_dir, root,
        current_wrapper_name="play.html",
        preview_wrapper_name="play-preview.html",
        changes=changes,
    )
    index_path = output_dir / "index.html"
    shutil.copy2(selector_path, index_path)

    return html_path, preview_html_path, index_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Block Quest web release")
    parser.add_argument("--preview", action="store_true",
                        help="Build 2-version preview (requires main_preview.py)")
    parser.add_argument("--promote", choices=["preview", "current"],
                        help="Promote preview or keep current, then clean up")
    args = parser.parse_args()

    if args.promote:
        promote(ROOT, choice=args.promote)
        print(f"Promoted '{args.promote}'. Running normal build...")
        build_web_release(ROOT)
    elif args.preview:
        html, preview_html, index = build_preview_release(ROOT)
        print(f"Preview build complete:\n  {html}\n  {preview_html}\n  {index}")
    else:
        build_web_release(ROOT)


if __name__ == "__main__":
    main()
