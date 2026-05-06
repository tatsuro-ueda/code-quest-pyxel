from __future__ import annotations

from pathlib import Path


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


def versioned_asset_url(path: str, token: str) -> str:
    return f"{path}?v={token}" if token else path


def generate_wrapper(
    build_dir: Path,
    project_root: Path,
    pyxel_html_name: str = "pyxel.html",
    *,
    page_kind: str = "production",
    session_api_base: str = "/internal/play-sessions",
) -> Path:
    template_path = project_root / "templates" / "wrapper.html"
    template = template_path.read_text(encoding="utf-8")
    wrapper_html = (
        template
        .replace("{{PYXEL_HTML_SRC}}", pyxel_html_name)
        .replace("{{PAGE_KIND}}", page_kind)
        .replace("{{SESSION_API_BASE}}", session_api_base)
    )
    output_path = build_dir / "index.html"
    output_path.write_text(wrapper_html, encoding="utf-8")
    return output_path


# 2026-05-06: index.html は build パイプラインから切り離した。
#   旧 `generate_top_selector / generate_selector / load_top_page_changes /
#   TOP_CHANGES_FILE / TOP_CHANGE_LIST_FRESHNESS_DEPENDENCIES` を削除。
#   トップページの「あたらしくなったこと」は post-commit hook
#   (tools/update_top_changes.py) が top_changes.json に追記し、
#   tools/render_top_changes.py が kid-pixel index.html のマーカー間を更新する。
#   templates/selector.html も併せて削除。
