from __future__ import annotations

import json
from pathlib import Path

from src.shared.services.browser_resource_override import (
    BROWSER_IMPORT_META_KEY,
    BROWSER_IMPORT_ZIP_KEY,
)
from tools.resolve_release_source_of_truth import load_development_meta, validate_change_list_freshness


TOP_CHANGES_FILE = Path("top_changes.json")
NORMAL_CHANGE_LIST_DEPENDENCIES = (
    Path("main.py"),
    Path("assets/umplus_j10r.bdf"),
    Path("assets/blockquest.pyxres"),
    Path("templates/wrapper.html"),
    Path("templates/selector.html"),
    Path("templates/codemaker_import_ui.js"),
)
DEVELOPMENT_SELECTOR_LABEL = "開発版"
PRODUCTION_SELECTOR_LABEL = "本番"
PYXEL_CODEMAKER_URL = "https://kitao.github.io/pyxel/wasm/code-maker/"


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
    preview_wrapper_name: str = "play-development.html",
    preview_zip_name: str = "",
    changes: list[str] | None = None,
    current_changes: list[str] | None = None,
) -> Path:
    template_path = project_root / "templates" / "selector.html"
    template = template_path.read_text(encoding="utf-8")
    import_script = (project_root / "templates" / "codemaker_import_ui.js").read_text(encoding="utf-8")
    import_script = (
        import_script
        .replace("{{BROWSER_IMPORT_ZIP_KEY}}", BROWSER_IMPORT_ZIP_KEY)
        .replace("{{BROWSER_IMPORT_META_KEY}}", BROWSER_IMPORT_META_KEY)
    )
    if preview_wrapper_name:
        if changes:
            change_list = "\n".join(f"      <li>{c}</li>" for c in changes)
        else:
            change_list = ""
        preview_links = ""
        if preview_zip_name:
            preview_links = (
                '    <div class="sub-links">\n'
                f'      <a class="sub-link" id="codemaker-download-link" href="{preview_zip_name}" download>'
                "リソースファイルをダウンロード</a>\n"
                f'      <a class="sub-link" href="{PYXEL_CODEMAKER_URL}" target="_blank" '
                'rel="noopener noreferrer">リソースエディタを開く</a>\n'
                "    </div>\n"
            )
        preview_card = (
            '  <div class="version-card">\n'
            f"    <h2>{DEVELOPMENT_SELECTOR_LABEL}</h2>\n"
            '    <ul class="changes">\n'
            f"{change_list}\n"
            '    </ul>\n'
            f'    <a class="play-btn" href="{preview_wrapper_name}">あそんでみる</a>\n'
            f"{preview_links}"
            "  </div>"
        )
        hint_block = (
            '  <p class="hint">\n'
            "    りょうほう あそんだら<br>\n"
            "    おとうさんに おしえてね！<br>\n"
            '    「こっちが いい！」って\n'
            "  </p>"
        )
    else:
        preview_card = ""
        hint_block = ""
    if current_changes:
        current_card_body = (
            '    <ul class="changes">\n'
            + "\n".join(f"      <li>{c}</li>" for c in current_changes)
            + "\n    </ul>\n"
        )
    else:
        current_card_body = '    <p class="desc">いままでと おなじ</p>\n'
    html = (
        template
        .replace("{{PREVIEW_CARD}}", preview_card)
        .replace("{{HINT_BLOCK}}", hint_block)
        .replace("{{CURRENT_CARD_BODY}}", current_card_body.rstrip())
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
        dependency_paths=NORMAL_CHANGE_LIST_DEPENDENCIES,
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
    preview_wrapper_name: str = "play-development.html",
    preview_zip_name: str = "",
) -> Path:
    current_changes = load_top_page_changes(project_root)
    changes = load_development_meta(project_root) if preview_wrapper_name else []
    return generate_selector(
        build_dir,
        project_root,
        current_wrapper_name=current_wrapper_name,
        preview_wrapper_name=preview_wrapper_name,
        preview_zip_name=preview_zip_name,
        changes=changes,
        current_changes=current_changes,
    )
