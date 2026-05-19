"""Release ビルドの依存解決ヘルパ（P3-D で DevelopmentCandidate 系を削除）。

このファイルに含まれる関数：

- ファイルの SHA256 hex digest を返す public 関数 file_sha256
- git 的に dirty かを判定する public 関数 is_git_dirty
- git の最新 commit timestamp か mtime を返す public 関数 revision_timestamp
- URL バスティング用トークンを組み立てる public 関数 build_cache_token
- .git ディレクトリの有無を判定する述語関数 _has_git_dir
- 指定 rel_path が git で tracked かを判定する述語関数 _is_path_tracked
- HEAD と差分があるかを判定する述語関数 _has_diff_against_head
- git ls-files で tracked 状態を取得する内部関数 _run_git_ls_files
- git log で最新 commit timestamp を取得する内部関数 _read_git_commit_timestamp
- revision_timestamp の git 経由 timestamp 算出を担う内部関数 _resolve_git_timestamp
- 依存パス群から有効な timestamp 集合を集める内部関数 _collect_dependency_timestamps

Problems:
    - Phase 3 で dev/prod 単一化したあと、build pipeline が必要とする最小
      ヘルパが膨らんで分岐ロジックを直書きしてしまうと、release 入口の
      契約がぼやけて変更速度が落ちる。
    - is_git_dirty / revision_timestamp が制御フローを直接含むと、
      git 不在環境と tracked 不在ケースの分岐が読み解きにくい。

Solutions:
    - public 関数は「述語呼び出し + private 委譲 + return」のステップ列に
      揃え、git サブプロセス呼び出しは private helper に切り出す。
    - build_cache_token は依存パス集計のみを担い、timestamp 算出は委譲する。

2026-05-06: validate_change_list_freshness を削除（top_changes.json は
post-commit hook 経由で更新され、build パイプラインからは独立）。
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


PRODUCTION_RUNTIME_FILE = Path("src/runtime/main_runtime.py")


# === Public API ===

def file_sha256(path: Path) -> str:
    """ファイルの SHA256 hex digest を返す。

    Args:
        path: 対象ファイルのパス。
    Returns:
        16 進文字列の SHA256 digest。
    Policy:
        - 全バイトをメモリに読み込む単発計算に限定する。
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_git_dirty(root: Path, rel_path: Path) -> bool:
    """指定ファイルが git 的に dirty（未 commit or untracked）なら True。

    Args:
        root: リポジトリのルート。
        rel_path: root からの相対パス。
    Returns:
        dirty なら True、git 不在や tracked かつ clean なら False。
    Policy:
        - public 関数はステップ列に揃え、git 不在判定 + dirty 解決を
          private helper に委ねる。
    """
    has_git = _has_git_dir(root)
    return _resolve_git_dirty(root, rel_path, has_git=has_git)


def revision_timestamp(  # noqa: CR100
        root: Path, rel_path: Path) -> float:
    """git で追跡されていれば最新 commit の timestamp、そうでなければ mtime。

    Args:
        root: リポジトリのルート。
        rel_path: root からの相対パス。
    Returns:
        epoch 秒。ファイルが存在しなければ 0.0。
    Policy:
        - public 関数はステップ列に揃え、git 経由 timestamp は
          _resolve_git_timestamp に委ねる。
    """
    path = root / rel_path
    is_present = path.exists()
    return _resolve_revision_timestamp(
        root, rel_path, path, is_present=is_present)


def build_cache_token(root: Path, dependency_paths: tuple[Path, ...]) -> str:
    """URL cache-busting 用のトークン（依存ファイル群の最新 timestamp）。

    Args:
        root: リポジトリのルート。
        dependency_paths: 依存ファイル群（root 相対）。
    Returns:
        最新 timestamp の int 表現、依存無しなら "0"。
    Policy:
        - public 関数はステップ列に揃え、timestamp 収集と token 整形を
          private helper に委ねる。
    """
    resolved_root = root.resolve()
    timestamps = _collect_dependency_timestamps(
        resolved_root, dependency_paths)
    return _format_cache_token(timestamps)


# === Internal helpers (private) ===

def _resolve_git_dirty(
        root: Path, rel_path: Path, *, has_git: bool) -> bool:
    """git 不在 / untracked / diff の各分岐で dirty 判定を返す。

    Args:
        root: リポジトリのルート。
        rel_path: 検査対象の相対パス。
        has_git: .git の存在を示すフラグ。
    Returns:
        dirty なら True。
    Policy:
        - is_git_dirty から制御フローを引き取り、述語呼び出しだけで決める。
    """
    if not has_git:
        return False
    if not _is_path_tracked(root, rel_path):
        return True
    return _has_diff_against_head(root, rel_path)


def _resolve_revision_timestamp(
        root: Path,
        rel_path: Path,
        path: Path,
        *,
        is_present: bool) -> float:
    """ファイル存在分岐と git timestamp 解決を担う。

    Args:
        root: リポジトリのルート。
        rel_path: root 相対のパス。
        path: root / rel_path（既に算出済み）。
        is_present: path.exists() の結果。
    Returns:
        epoch 秒、存在しなければ 0.0。
    Policy:
        - revision_timestamp から制御フローを引き取り、git 経由分岐は
          _resolve_git_timestamp に委ねる。
    """
    if not is_present:
        return 0.0
    return _resolve_git_timestamp(root, rel_path, path)


def _format_cache_token(timestamps: list[float]) -> str:
    """timestamp 集合を cache-busting token 文字列に整形する。

    Args:
        timestamps: revision_timestamp 集合（空ならゼロ token）。
    Returns:
        最新 timestamp の int 表現、空なら "0"。
    Policy:
        - build_cache_token から空判定と max 抽出を引き取る。
    """
    if not timestamps:
        return "0"
    return str(int(max(timestamps)))


def _has_git_dir(root: Path) -> bool:
    """root に .git ディレクトリが存在するかの述語。

    Args:
        root: リポジトリのルート。
    Returns:
        .git が存在すれば True。
    Policy:
        - 存在チェックのみで、内部の整合性は問わない。
    """
    return (root / ".git").exists()


def _run_git_ls_files(
        root: Path, rel_path: Path) -> subprocess.CompletedProcess:
    """git ls-files --error-unmatch を実行する。

    Args:
        root: リポジトリのルート。
        rel_path: 検査対象の相対パス。
    Returns:
        CompletedProcess（returncode のみを後段で見る）。
    Policy:
        - 失敗をエラーにせず、呼び出し元の述語に判定を委ねる。
    """
    return subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", rel_path.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def _is_path_tracked(root: Path, rel_path: Path) -> bool:
    """git で tracked なら True を返す述語。

    Args:
        root: リポジトリのルート。
        rel_path: 検査対象の相対パス。
    Returns:
        tracked なら True。
    Policy:
        - git ls-files の returncode == 0 を単一の判定基準にする。
    """
    return _run_git_ls_files(root, rel_path).returncode == 0


def _has_diff_against_head(root: Path, rel_path: Path) -> bool:
    """git diff --quiet HEAD で差分があれば True を返す述語。

    Args:
        root: リポジトリのルート。
        rel_path: 検査対象の相対パス。
    Returns:
        差分があれば True。
    Policy:
        - returncode == 1 を差分ありの判定基準にする。
    """
    dirty = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", rel_path.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return dirty.returncode == 1


def _read_git_commit_timestamp(root: Path, rel_path: Path) -> float | None:
    """git log -1 --format=%ct で最新 commit timestamp を取得する。

    Args:
        root: リポジトリのルート。
        rel_path: 取得対象の相対パス。
    Returns:
        timestamp。失敗や空応答なら None。
    Policy:
        - 失敗時は None を返し、呼び出し元の fallback に委ねる。
    """
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", rel_path.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    return float(raw)


def _resolve_git_timestamp(
        root: Path, rel_path: Path, path: Path) -> float:
    """revision_timestamp の git 経由 timestamp 算出を担う。

    Args:
        root: リポジトリのルート。
        rel_path: root 相対のパス。
    Returns:
        最新 commit timestamp か mtime。
    Policy:
        - git 不在 / dirty / untracked / log 失敗の各分岐で
          mtime を fallback に揃える。
    """
    if not _has_git_dir(root):
        return path.stat().st_mtime
    if is_git_dirty(root, rel_path):
        return path.stat().st_mtime
    if not _is_path_tracked(root, rel_path):
        return path.stat().st_mtime
    commit_ts = _read_git_commit_timestamp(root, rel_path)
    if commit_ts is None:
        return path.stat().st_mtime
    return commit_ts


def _collect_dependency_timestamps(
        root: Path, dependency_paths: tuple[Path, ...]) -> list[float]:
    """root 配下に存在する依存パスの revision_timestamp を集める。

    Args:
        root: 解決済みのリポジトリ root。
        dependency_paths: 依存ファイル群（root 相対）。
    Returns:
        timestamp の list（存在しない依存は除外）。
    Policy:
        - 順序は dependency_paths のまま保つ。
    """
    return [
        revision_timestamp(root, dependency)
        for dependency in dependency_paths
        if (root / dependency).exists()
    ]
