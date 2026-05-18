"""Release ビルド共通ユーティリティ（dev/prod 単一化後の SSoT）。

このファイルに含まれる関数・クラス：

- collect_release_paths：ステージング対象のパス集合を root 相対で列挙する
- stage_release：root から stage_dir に release ファイル群をコピーする
- dist_output_dir：output_dir 直下の `dist/` パスを返す（薄いラッパ）
- write_wrapper_outputs：wrapper html を play.html / index.html に複製する
- prune_legacy_root_outputs：旧 root 直下 artifact を削除する後始末
- build_codemaker_release：codemaker zip を生成する薄い委譲
- _gather_release_paths：RELEASE_FILES / RELEASE_DIRS から相対パス集合を組み立てる
- _add_release_files：RELEASE_FILES の存在チェックと集合追加
- _add_release_dirs：RELEASE_DIRS 配下を rglob して候補を集合に追加
- _is_release_candidate：__pycache__ / .pyc を除外する述語
- _sort_release_paths：as_posix 順にソートして list へ
- _reset_stage_dir：stage_dir を空のディレクトリに作り直す
- _copy_release_paths：相対パス列を 1 件ずつコピーするループ
- _copy_one_release_path：1 件分の親ディレクトリ作成と copy2
- _resolve_wrapper_targets：play.html / index.html の出力先 Path を返す
- _copy_wrapper_to_targets：wrapper html を 2 ファイルへ複製
- _remove_legacy_artifacts：LEGACY_ROOT_ARTIFACTS を 1 件ずつ削除
- _remove_if_exists：存在するときだけ unlink する gate
- _discard_unused_codemaker_args：後方互換のための未使用引数 del

Problems:
    - dev/prod 二重生成の名残（root 直下 artifact / preview 等）が残ったまま
      release を再ビルドすると、配布物が二重化して原因切り分けが面倒になる。
    - ステージング・コピー・後始末を 1 関数に詰め込むと、build_web_release.py
      からの呼び出しが厚くなり、CR203/CR204 のステップ列ポリシーに反する。

Solutions:
    - 配布 artifact のパスを module 定数として SSoT 化し、CLI 側からは
      これだけを import すれば良い設計にする。
    - public 関数を「述語呼び出し + private 委譲 + return」に薄く揃え、
      ループ・条件分岐は private helper に閉じ込める。
"""
from __future__ import annotations

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


# === Public API ===


def collect_release_paths(root: Path) -> list[Path]:
    """release に含める相対パスを root 配下から列挙する。

    Args:
        root: プロジェクトルートの絶対 or 相対 Path。

    Returns:
        list[Path]: root に対する相対パス（POSIX 文字列順にソート済み）。

    Policy:
        - 個別ファイル / ディレクトリ走査 / ソートを private helper に分けて委譲する。
    """
    root = root.resolve()
    release_paths = _gather_release_paths(root)
    return _sort_release_paths(release_paths)


def stage_release(root: Path, stage_dir: Path) -> list[Path]:
    """root から stage_dir に release ファイル群をコピーする。

    Args:
        root: プロジェクトルート。
        stage_dir: 出力先ステージングディレクトリ（存在すれば作り直す）。

    Returns:
        list[Path]: コピーした相対パスのリスト。

    Policy:
        - クリーンアップ / 列挙 / コピーを private helper に分けて委譲する。
    """
    root = root.resolve()
    _reset_stage_dir(stage_dir)
    copied_paths = collect_release_paths(root)
    _copy_release_paths(root, stage_dir, copied_paths)
    return copied_paths


def dist_output_dir(output_dir: Path) -> Path:  # noqa: CR100
    """output_dir 直下の `dist/` パスを返す（既存 API 名を維持）。

    Args:
        output_dir: 配布物の親ディレクトリ。

    Returns:
        Path: `output_dir / DIST_DIR`。

    Policy:
        - 名前は build_web_release から import 済みのため固定する（CR100 は noqa）。
    """
    return output_dir / DIST_DIR


def write_wrapper_outputs(
        wrapper_path: Path, target_dir: Path) -> tuple[Path, Path]:
    """wrapper html を play.html / index.html として target_dir に複製する。

    Args:
        wrapper_path: 元になる wrapper html ファイル。
        target_dir: コピー先ディレクトリ（無ければ作成）。

    Returns:
        tuple[Path, Path]: (play.html のパス, index.html のパス)。

    Policy:
        - 親ディレクトリ作成と 2 ファイルコピーを private helper に委譲する。
    """
    play_path, index_path = _resolve_wrapper_targets(target_dir)
    _copy_wrapper_to_targets(wrapper_path, play_path, index_path)
    return play_path, index_path


def prune_legacy_root_outputs(output_dir: Path) -> None:
    """旧 root 直下に残った legacy artifact を削除する。

    Args:
        output_dir: 削除対象を探す出力ディレクトリ。

    Policy:
        - 削除対象のループは private helper に閉じ込め、ここは委譲のみ。
    """
    _remove_legacy_artifacts(output_dir)


def build_codemaker_release(
    root: Path,
    *,
    main_source: Path,
    resource_source: Path,
    output_path: Path,
) -> Path:
    """codemaker_bundler ベースの zip を生成する薄い委譲。

    Args:
        root: プロジェクトルート（P2 以降は未使用、後方互換のため残置）。
        main_source: 旧 entrypoint のソース（P2 以降は未使用）。
        resource_source: bundler に渡す pyxres ファイル。
        output_path: 生成する code-maker.zip の出力パス。

    Returns:
        Path: 生成された zip のパス（build_codemaker_zip の返り値）。

    Policy:
        - P2 以降 bundler は manifest を使うため、root / main_source は捨てる。
    """
    _discard_unused_codemaker_args(root, main_source)
    return build_codemaker_zip(
        pyxres=resource_source,
        output=output_path,
    )


# === Internal helpers (private) ===


def _gather_release_paths(root: Path) -> set[Path]:
    """RELEASE_FILES / RELEASE_DIRS から release 対象パスの集合を組み立てる。

    Args:
        root: 解決済みプロジェクトルート（絶対パス）。

    Returns:
        set[Path]: root に対する相対パスの集合。

    Policy:
        - file 群と dir 群でループを分け、対象判定は private helper に委ねる。
    """
    release_paths: set[Path] = set()
    _add_release_files(root, release_paths)
    _add_release_dirs(root, release_paths)
    return release_paths


def _add_release_files(root: Path, release_paths: set[Path]) -> None:
    """RELEASE_FILES の各エントリを存在チェックして集合に積む。

    Args:
        root: 解決済みプロジェクトルート。
        release_paths: 積み上げ対象の集合（破壊的更新）。

    Policy:
        - 単純な for ループの責務を public から外に出す。
    """
    for rel_path in RELEASE_FILES:
        if (root / rel_path).is_file():
            release_paths.add(rel_path)


def _add_release_dirs(root: Path, release_paths: set[Path]) -> None:
    """RELEASE_DIRS 配下を rglob して除外条件をかけつつ集合に積む。

    Args:
        root: 解決済みプロジェクトルート。
        release_paths: 積み上げ対象の集合（破壊的更新）。

    Policy:
        - 除外判定 (`__pycache__` / `.pyc`) は _is_release_candidate に集約する。
    """
    for rel_path in RELEASE_DIRS:
        for path in (root / rel_path).rglob("*"):
            if not _is_release_candidate(path):
                continue
            release_paths.add(path.relative_to(root))


def _is_release_candidate(path: Path) -> bool:
    """release に含めて良いファイルかを判定する。

    Args:
        path: rglob で取れた絶対パス。

    Returns:
        bool: ファイルかつ `__pycache__` / `.pyc` を含まなければ True。

    Policy:
        - 複合条件を 1 つの述語に押し込み、CR303 を回避する。
    """
    if not path.is_file():
        return False
    if "__pycache__" in path.parts:
        return False
    return path.suffix != ".pyc"


def _sort_release_paths(release_paths: set[Path]) -> list[Path]:
    """release パス集合を POSIX 文字列でソートした list に変換する。

    Args:
        release_paths: 相対パスの集合。

    Returns:
        list[Path]: as_posix() 順のソート済みリスト。

    Policy:
        - OS 依存のパス比較を避けるため as_posix() で揃える。
    """
    return sorted(release_paths, key=lambda path: path.as_posix())


def _reset_stage_dir(stage_dir: Path) -> None:
    """ステージング先を空のディレクトリ状態に作り直す。

    Args:
        stage_dir: ステージング先ディレクトリ。

    Policy:
        - 既存内容は確実に消して、コピー結果の純度を担保する。
    """
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)


def _copy_release_paths(
        root: Path, stage_dir: Path, copied_paths: list[Path]) -> None:
    """相対パスのリストを 1 件ずつ stage_dir にコピーする。

    Args:
        root: コピー元のルート。
        stage_dir: コピー先のステージングディレクトリ。
        copied_paths: コピー対象の相対パスのリスト。

    Policy:
        - 1 件ごとの親ディレクトリ作成と copy2 を private helper に閉じ込める。
    """
    for rel_path in copied_paths:
        _copy_one_release_path(root, stage_dir, rel_path)


def _copy_one_release_path(
        root: Path, stage_dir: Path, rel_path: Path) -> None:
    """1 件の相対パスを root から stage_dir にコピーする。

    Args:
        root: コピー元ルート。
        stage_dir: コピー先ルート。
        rel_path: コピー対象の相対パス。

    Policy:
        - 親ディレクトリを必要に応じて作成し、copy2 でメタデータごとコピーする。
    """
    src = root / rel_path
    dst = stage_dir / rel_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _resolve_wrapper_targets(target_dir: Path) -> tuple[Path, Path]:
    """target_dir 配下の play.html / index.html パスを用意する。

    Args:
        target_dir: 出力先ディレクトリ（無ければ作成）。

    Returns:
        tuple[Path, Path]: (play.html のパス, index.html のパス)。

    Policy:
        - mkdir とパス計算をここに集約し、public は委譲だけにする。
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    play_path = target_dir / "play.html"
    index_path = target_dir / "index.html"
    return play_path, index_path


def _copy_wrapper_to_targets(
        wrapper_path: Path, play_path: Path, index_path: Path) -> None:
    """wrapper html を play.html / index.html に複製する。

    Args:
        wrapper_path: コピー元 wrapper html。
        play_path: コピー先 play.html。
        index_path: コピー先 index.html。

    Policy:
        - 2 ファイル分の copy2 を 1 箇所に揃える。
    """
    shutil.copy2(wrapper_path, play_path)
    shutil.copy2(wrapper_path, index_path)


def _remove_legacy_artifacts(output_dir: Path) -> None:
    """LEGACY_ROOT_ARTIFACTS を 1 件ずつ存在チェックして削除する。

    Args:
        output_dir: 削除対象を探すルート。

    Policy:
        - 単純な for ループの責務を public から外に出す。
    """
    for rel_path in LEGACY_ROOT_ARTIFACTS:
        _remove_if_exists(output_dir / rel_path)


def _remove_if_exists(path: Path) -> None:
    """path が存在するときだけ unlink する。

    Args:
        path: 削除候補の絶対 or 相対パス。

    Policy:
        - 存在チェックと unlink を 1 箇所に集約する。
    """
    if path.exists():
        path.unlink()


def _discard_unused_codemaker_args(root: Path, main_source: Path) -> None:
    """build_codemaker_release が後方互換のために受け取る未使用引数を捨てる。

    Args:
        root: 旧 API 互換のため受け取るだけのプロジェクトルート。
        main_source: 旧 API 互換のため受け取るだけの entrypoint パス。

    Policy:
        - public 関数を「述語/委譲/return」のステップ列に保つため、
          `del` の責務を private に閉じ込める。
    """
    del root, main_source
