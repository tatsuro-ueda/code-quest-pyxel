from __future__ import annotations

"""Release ビルドの依存解決 / 変更リスト鮮度検証ヘルパ（P3-D で DevelopmentCandidate 系を削除）。

Phase 3 で dev/prod 単一化したため、本番 1 本のビルドに必要な最小機能のみ残す:
- file_sha256 / is_git_dirty / revision_timestamp
- validate_change_list_freshness（top_changes.json の鮮度チェック）
- build_cache_token（URL バスティング用トークン）
"""

import hashlib
import subprocess
from pathlib import Path


PRODUCTION_RUNTIME_FILE = Path("src/runtime/main_runtime.py")


def file_sha256(path: Path) -> str:
    """ファイルの SHA256 hex digest を返す。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_git_dirty(root: Path, rel_path: Path) -> bool:
    """指定ファイルが git 的に dirty（未 commit or untracked）なら True。"""
    git_dir = root / ".git"
    if not git_dir.exists():
        return False

    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", rel_path.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if tracked.returncode != 0:
        return True

    dirty = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", rel_path.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return dirty.returncode == 1


def revision_timestamp(root: Path, rel_path: Path) -> float:
    """git で追跡されていれば最新 commit の timestamp、そうでなければ mtime。"""
    path = root / rel_path
    if not path.exists():
        return 0.0

    git_dir = root / ".git"
    if git_dir.exists():
        if is_git_dirty(root, rel_path):
            return path.stat().st_mtime
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", rel_path.as_posix()],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if tracked.returncode != 0:
            return path.stat().st_mtime

        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", rel_path.as_posix()],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())

    return path.stat().st_mtime


def validate_change_list_freshness(
    root: Path,
    *,
    changes_rel_path: Path,
    dependency_paths: tuple[Path, ...],
) -> None:
    """top_changes.json が依存ファイルより古い場合に ValueError を投げる。"""
    root = root.resolve()
    changes_path = root / changes_rel_path
    if not changes_path.exists():
        return
    if is_git_dirty(root, changes_rel_path):
        return

    changes_timestamp = revision_timestamp(root, changes_rel_path)
    for dependency in dependency_paths:
        dependency_path = root / dependency
        if not dependency_path.exists():
            continue
        dependency_timestamp = revision_timestamp(root, dependency)
        if dependency_timestamp > changes_timestamp:
            raise ValueError(
                f"{changes_rel_path} is older than {dependency}. "
                "Update the change list so selector text matches the shipped content."
            )


def build_cache_token(root: Path, dependency_paths: tuple[Path, ...]) -> str:
    """URL cache-busting 用のトークン（依存ファイル群の最新 timestamp）。"""
    root = root.resolve()
    timestamps = [
        revision_timestamp(root, dependency)
        for dependency in dependency_paths
        if (root / dependency).exists()
    ]
    if not timestamps:
        return "0"
    return str(int(max(timestamps)))
