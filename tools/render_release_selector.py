"""リリース版 wrapper.html を生成する小さなヘルパ。

このファイルに含まれる関数:

- build_versioned_asset_url: cache busting 用に URL に ?v=token を付与する
- generate_wrapper: templates/wrapper.html から index.html を build_dir に書き出す
- versioned_asset_url: 後方互換のため build_versioned_asset_url を呼ぶ shim

Problems:
    - 旧 dev/prod 二重生成の名残で wrapper 生成が build_web_release から
      複数経路で呼ばれており、文字列置換のテンプレート差分が見えにくい。
    - 関数名が `versioned_asset_url` のように名詞接頭辞のままだと CR100 を
      満たさず、CLI 表面の読み取りで責務がぼやける。

Solutions:
    - 公開関数を「述語呼び出し + private 委譲 + return」のステップ列に揃え、
      テンプレート読み込みと wrapper 出力は private helper に切り出す。
    - 新名 build_versioned_asset_url と shim versioned_asset_url の両方を
      export して、呼出し互換を保つ。
"""
from __future__ import annotations

from pathlib import Path


# === Public API ===

NORMAL_CHANGE_LIST_DEPENDENCIES = (
    Path("main.py"),
    Path("src/runtime/main_runtime.py"),
    Path("assets/umplus_j10r.bdf"),
    Path("templates/wrapper.html"),
    Path("templates/codemaker_import_ui.js"),
)
PRODUCTION_SELECTOR_LABEL = "本番"
PYXEL_CODEMAKER_URL = "https://kitao.github.io/pyxel/wasm/code-maker/"
CURRENT_CODEMAKER_ZIP_PATH = "dist/code-maker.zip"


def build_versioned_asset_url(path: str, token: str) -> str:
    """URL に ?v=token を付加して cache-busting 用 URL を返す。

    Args:
        path: 元アセットの URL 文字列。
        token: バージョントークン（空文字なら付加しない）。

    Returns:
        token が非空なら "path?v=token"、空なら path そのまま。

    Policy:
        - token の空判定だけで分岐する純関数。
    """
    return _format_versioned_url(path, token)


def versioned_asset_url(path: str, token: str) -> str:  # noqa: CR100
    """build_versioned_asset_url の後方互換 shim。

    Args:
        path: 元アセットの URL 文字列。
        token: バージョントークン。

    Returns:
        build_versioned_asset_url と同じ文字列。

    Policy:
        - 旧 import パスを壊さないため、実体は build_versioned_asset_url に委譲する。
    """
    return build_versioned_asset_url(path, token)


def generate_wrapper(
    build_dir: Path,
    project_root: Path,
    pyxel_html_name: str = "pyxel.html",
    *,
    page_kind: str = "production",
    session_api_base: str = "/internal/play-sessions",
) -> Path:
    """templates/wrapper.html から index.html を build_dir に書き出す。

    Args:
        build_dir: 出力先ディレクトリ。
        project_root: プロジェクトルート（templates 解決に使う）。
        pyxel_html_name: 埋め込む pyxel html のファイル名。
        page_kind: ページ種別（"production" など）。
        session_api_base: セッション API のベース URL。

    Returns:
        書き出した index.html の絶対パス。

    Policy:
        - テンプレートの 3 placeholder を順に置換し、build_dir/index.html に書く。
    """
    return _emit_wrapper_html(
        build_dir, project_root, pyxel_html_name,
        page_kind, session_api_base,
    )


# === Internal helpers (private) ===


def _format_versioned_url(path: str, token: str) -> str:
    """build_versioned_asset_url の本体（条件分岐 + return）。

    Args:
        path: 元アセットの URL。
        token: バージョントークン。

    Returns:
        token 有無に応じた URL。

    Policy:
        - token が truthy なら "?v=token" を付与する。
    """
    if token:
        return f"{path}?v={token}"
    return path


def _emit_wrapper_html(
    build_dir: Path,
    project_root: Path,
    pyxel_html_name: str,
    page_kind: str,
    session_api_base: str,
) -> Path:
    """generate_wrapper の本体（テンプレ読み → 置換 → 書き出し）。

    Args:
        build_dir: 出力先ディレクトリ。
        project_root: プロジェクトルート。
        pyxel_html_name: 埋め込む pyxel html のファイル名。
        page_kind: ページ種別。
        session_api_base: セッション API のベース URL。

    Returns:
        書き出した index.html の絶対パス。

    Policy:
        - templates/wrapper.html を読み、3 placeholder を置換して書く。
    """
    template = _read_wrapper_template(project_root)
    wrapper_html = _apply_wrapper_placeholders(
        template, pyxel_html_name, page_kind, session_api_base,
    )
    output_path = build_dir / "index.html"
    output_path.write_text(wrapper_html, encoding="utf-8")
    return output_path


def _read_wrapper_template(project_root: Path) -> str:
    """templates/wrapper.html の中身を utf-8 文字列で返す。

    Args:
        project_root: プロジェクトルート。

    Returns:
        wrapper.html の生テンプレート文字列。

    Policy:
        - 単純なファイル読み込みのみ。
    """
    template_path = project_root / "templates" / "wrapper.html"
    return template_path.read_text(encoding="utf-8")


def _apply_wrapper_placeholders(
    template: str,
    pyxel_html_name: str,
    page_kind: str,
    session_api_base: str,
) -> str:
    """wrapper.html の 3 placeholder を順に置換する。

    Args:
        template: テンプレートの生文字列。
        pyxel_html_name: 埋め込む pyxel html のファイル名。
        page_kind: ページ種別。
        session_api_base: セッション API のベース URL。

    Returns:
        置換済みの wrapper html 文字列。

    Policy:
        - 既存実装と同じ順序で str.replace を適用する。
    """
    return (
        template
        .replace("{{PYXEL_HTML_SRC}}", pyxel_html_name)
        .replace("{{PAGE_KIND}}", page_kind)
        .replace("{{SESSION_API_BASE}}", session_api_base)
    )


# 2026-05-06: index.html は build パイプラインから切り離した。
#   旧 `generate_top_selector / generate_selector / load_top_page_changes /
#   TOP_CHANGES_FILE / TOP_CHANGE_LIST_FRESHNESS_DEPENDENCIES` を削除。
#   トップページの「あたらしくなったこと」は post-commit hook
#   (tools/update_top_changes.py) が top_changes.json に追記し、
#   tools/render_top_changes.py が kid-pixel index.html のマーカー間を更新する。
#   templates/selector.html も併せて削除。
