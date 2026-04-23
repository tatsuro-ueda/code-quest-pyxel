from __future__ import annotations

import json
from pathlib import Path

from tools.resolve_release_source_of_truth import validate_change_list_freshness


TOP_CHANGES_FILE = Path("top_changes.json")
NORMAL_CHANGE_LIST_DEPENDENCIES = (
    Path("main.py"),
    Path("src/runtime/main_runtime.py"),
    Path("assets/umplus_j10r.bdf"),
    Path("templates/wrapper.html"),
    Path("templates/selector.html"),
    Path("templates/codemaker_import_ui.js"),
)
TOP_CHANGE_LIST_FRESHNESS_DEPENDENCIES = (
    Path("src/runtime/main_runtime.py"),
    Path("assets/umplus_j10r.bdf"),
    Path("templates/wrapper.html"),
    Path("templates/selector.html"),
    Path("templates/codemaker_import_ui.js"),
)
PRODUCTION_SELECTOR_LABEL = "本番"
PYXEL_CODEMAKER_URL = "https://kitao.github.io/pyxel/wasm/code-maker/"
CURRENT_CODEMAKER_ZIP_PATH = "production/code-maker.zip"


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


def generate_selector(
    build_dir: Path,
    project_root: Path,
    *,
    current_wrapper_name: str = "play.html",
    current_changes: list[str] | None = None,
    current_codemaker_zip: str | None = CURRENT_CODEMAKER_ZIP_PATH,
) -> Path:
    """本番 1 カードの selector を生成する（P3-C で dev/preview 関連を削除済み）。"""
    template_path = project_root / "templates" / "selector.html"
    template = template_path.read_text(encoding="utf-8")
    import_script = (project_root / "templates" / "codemaker_import_ui.js").read_text(encoding="utf-8")
    if current_changes:
        current_card_body = (
            '    <ul class="changes">\n'
            + "\n".join(f"      <li>{c}</li>" for c in current_changes)
            + "\n    </ul>\n"
        )
    else:
        current_card_body = '    <p class="desc">いままでと おなじ</p>\n'

    # 本番カード下部のサブリンク（リソースファイル DL + Pyxel Code Maker を開く）
    if current_codemaker_zip:
        current_card_sub_links = (
            '    <div class="sub-links">\n'
            f'      <a class="sub-link" id="codemaker-download-link" href="{current_codemaker_zip}" download>'
            "リソースファイルをダウンロード</a>\n"
            f'      <a class="sub-link" href="{PYXEL_CODEMAKER_URL}" target="_blank" '
            'rel="noopener noreferrer">リソースエディタを開く</a>\n'
            "    </div>"
        )
    else:
        current_card_sub_links = ""

    html = (
        template
        .replace("{{PREVIEW_CARD}}", "")
        .replace("{{HINT_BLOCK}}", "")
        .replace("{{CURRENT_CARD_BODY}}", current_card_body.rstrip())
        .replace("{{CURRENT_CARD_SUB_LINKS}}", current_card_sub_links)
        .replace("{{CURRENT_WRAPPER_SRC}}", current_wrapper_name)
        .replace("{{CODEMAKER_IMPORT_SCRIPT}}", import_script)
    )
    output_path = build_dir / "index.html"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def load_top_page_changes(root: Path) -> list[str]:
    root = root.resolve()
    changes_path = root / TOP_CHANGES_FILE
    if not changes_path.is_file():
        return []
    validate_change_list_freshness(
        root,
        changes_rel_path=TOP_CHANGES_FILE,
        dependency_paths=TOP_CHANGE_LIST_FRESHNESS_DEPENDENCIES,
    )
    data = json.loads(changes_path.read_text(encoding="utf-8"))
    changes = data.get("changes", [])
    if not isinstance(changes, list):
        raise ValueError(f"{changes_path} must contain a JSON object with a 'changes' list")
    return [str(change) for change in changes]


def generate_top_selector(
    build_dir: Path,
    project_root: Path,
    *,
    current_wrapper_name: str = "play.html",
    current_codemaker_zip: str | None = CURRENT_CODEMAKER_ZIP_PATH,
) -> Path:
    """本番 1 カードの selector を生成する（P3-C で dev/preview 引数を削除）。"""
    current_changes = load_top_page_changes(project_root)
    return generate_selector(
        build_dir,
        project_root,
        current_wrapper_name=current_wrapper_name,
        current_changes=current_changes,
        current_codemaker_zip=current_codemaker_zip,
    )
