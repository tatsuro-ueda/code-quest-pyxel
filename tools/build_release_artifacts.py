from __future__ import annotations

import shutil
from pathlib import Path

from tools.build_codemaker import build_codemaker_zip


RELEASE_FILES = (
    Path("main.py"),
    Path("assets/umplus_j10r.bdf"),
    Path("assets/blockquest.pyxres"),
)
RELEASE_DIRS = ()
PRODUCTION_DIR = Path("production")
DEVELOPMENT_DIR = Path("development")
PRODUCTION_PYXAPP_FILE = PRODUCTION_DIR / "pyxel.pyxapp"
PRODUCTION_HTML_FILE = PRODUCTION_DIR / "pyxel.html"
PRODUCTION_PLAY_FILE = PRODUCTION_DIR / "play.html"
PRODUCTION_INDEX_FILE = PRODUCTION_DIR / "index.html"
CODEMAKER_OUTPUT_FILE = PRODUCTION_DIR / "code-maker.zip"
DEVELOPMENT_PYXAPP_FILE = DEVELOPMENT_DIR / "pyxel.pyxapp"
DEVELOPMENT_HTML_FILE = DEVELOPMENT_DIR / "pyxel.html"
DEVELOPMENT_PLAY_FILE = DEVELOPMENT_DIR / "play.html"
DEVELOPMENT_INDEX_FILE = DEVELOPMENT_DIR / "index.html"
DEVELOPMENT_OUTPUT_FILES = (
    DEVELOPMENT_PLAY_FILE,
    DEVELOPMENT_INDEX_FILE,
    DEVELOPMENT_HTML_FILE,
    DEVELOPMENT_PYXAPP_FILE,
)
DEVELOPMENT_CODEMAKER_OUTPUT_FILE = DEVELOPMENT_DIR / "code-maker.zip"
DEVELOPMENT_ARTIFACT_FILES = DEVELOPMENT_OUTPUT_FILES + (DEVELOPMENT_CODEMAKER_OUTPUT_FILE,)
LEGACY_ROOT_ARTIFACTS = (
    Path("play.html"),
    Path("pyxel.html"),
    Path("pyxel.pyxapp"),
    Path("code-maker.zip"),
    Path("play-development.html"),
    Path("pyxel-development.html"),
    Path("code-maker-development.zip"),
    Path("pyxel-preview.pyxapp"),
)


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


def production_output_dir(output_dir: Path) -> Path:
    return output_dir / PRODUCTION_DIR


def development_output_dir(output_dir: Path) -> Path:
    return output_dir / DEVELOPMENT_DIR


def write_wrapper_outputs(wrapper_path: Path, target_dir: Path) -> tuple[Path, Path]:
    target_dir.mkdir(parents=True, exist_ok=True)
    play_path = target_dir / "play.html"
    index_path = target_dir / "index.html"
    shutil.copy2(wrapper_path, play_path)
    shutil.copy2(wrapper_path, index_path)
    return play_path, index_path


def prune_legacy_root_outputs(output_dir: Path) -> None:
    for rel_path in LEGACY_ROOT_ARTIFACTS:
        path = output_dir / rel_path
        if path.exists():
            path.unlink()


def prune_development_outputs(output_dir: Path) -> None:
    output_dir = output_dir.resolve()
    for rel_path in DEVELOPMENT_ARTIFACT_FILES:
        path = output_dir / rel_path
        if path.exists():
            path.unlink()
    development_root = development_output_dir(output_dir)
    if development_root.exists():
        try:
            development_root.rmdir()
        except OSError:
            pass


def apply_stage_overrides(
    stage_dir: Path,
    *,
    main_source: Path | None = None,
    resource_source: Path | None = None,
) -> None:
    if main_source is not None:
        shutil.copy2(main_source, stage_dir / "main.py")
    if resource_source is not None:
        resource_target = stage_dir / "assets" / "blockquest.pyxres"
        resource_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(resource_source, resource_target)


def build_codemaker_release(
    root: Path,
    *,
    main_source: Path,
    resource_source: Path,
    output_path: Path,
) -> Path:
    root = root.resolve()
    return build_codemaker_zip(
        main_source,
        pyxres=resource_source,
        output=output_path,
    )
