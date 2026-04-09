from __future__ import annotations

import importlib.util
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
RELEASE_DIRS = (Path("src"),)


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

    # カスタムHTMLラッパー生成
    wrapper_path = generate_wrapper(work_dir, root)
    index_path = output_dir / "index.html"
    shutil.copy2(wrapper_path, index_path)

    return pyxapp_path, html_path, index_path


def main() -> None:
    build_web_release(ROOT)


if __name__ == "__main__":
    main()
