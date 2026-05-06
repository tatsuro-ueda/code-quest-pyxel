from __future__ import annotations

"""Release ビルドで使う共通ユーティリティ（P3-D で dev 関連を削除）。"""

import shutil
from pathlib import Path

from tools.build_codemaker import build_codemaker_zip


RELEASE_FILES = (
    Path("main.py"),
    Path("assets/umplus_j10r.bdf"),
    Path("assets/blockquest.pyxres"),
)
RELEASE_DIRS = (Path("src"),)
DIST_DIR = Path("dist")
DIST_PYXAPP_FILE = DIST_DIR / "pyxel.pyxapp"
DIST_HTML_FILE = DIST_DIR / "pyxel.html"
DIST_PLAY_FILE = DIST_DIR / "play.html"
DIST_INDEX_FILE = DIST_DIR / "index.html"
CODEMAKER_OUTPUT_FILE = DIST_DIR / "code-maker.zip"
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


def dist_output_dir(output_dir: Path) -> Path:
    return output_dir / DIST_DIR


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


def build_codemaker_release(
    root: Path,
    *,
    main_source: Path,
    resource_source: Path,
    output_path: Path,
) -> Path:
    """codemaker_bundler ベースの zip を生成する。main_source は P2 以降 無視される。"""
    del root, main_source  # P2 以降 bundler は常に manifest を使うため未使用
    return build_codemaker_zip(
        pyxres=resource_source,
        output=output_path,
    )
