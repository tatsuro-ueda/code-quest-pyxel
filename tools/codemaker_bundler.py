"""Code Maker 用 bundler (Q4B: concat 生成型)。

`tools/codemaker_manifest.txt` に列挙した .py ファイルを順番に連結して、
Code Maker 環境（単一 main.py のみで動く）で動作する source text を作る。

方針:
- 各 .py の `from src.X ...` 行は除去（連結後は全 symbol が同一 module に入るため不要）
- `from __future__ import annotations` / `import pyxel` / `import random` /
  `from pathlib import Path` 等の標準系 import は dedup して最初の 1 回だけ残す
- ファイル間に区切りコメント（`# --- X.py ---`）を挿入して読みやすく
- `if __name__ == "__main__":` 以下は除去（main_runtime の entry ではない）

最終出力は `build_codemaker.py` の `build_codemaker_main_text()` が期待する
「CORE_BLOCK に埋め込む source_text」。末尾に `# ====... ENTRY POINT ...`
marker を置き、`run()` 関数を含めて返す。
"""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools" / "codemaker_manifest.txt"

# 連結時に除去する import パターン
# `from src.X import Y` / `from src.X.Y import *` / `import src.X.Y`
_LOCAL_IMPORT_RE = re.compile(r"^\s*from\s+src\.|^\s*import\s+src\.")

# 連結時に dedup する標準系 import（最初の 1 回だけ残す）
_STD_IMPORT_RE = re.compile(
    r"^(from\s+__future__\s+import\s+annotations|"
    r"import\s+(pyxel|random|sys|hashlib|json|typing|pathlib|io|os|re|math)(\s|$)|"
    r"from\s+(pathlib|typing|dataclasses|io|os|re|math|hashlib|json)\s+import\s+)"
)


def _read_manifest_paths() -> list[Path]:
    """codemaker_manifest.txt を読み、コメント/空行を除いたファイルパスのリストを返す。"""
    paths: list[Path] = []
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(ROOT / line)
    return paths


_IMPORT_AS_RE = re.compile(
    r"^\s*from\s+src\.[^\s]+\s+import\s+(\w+)\s+as\s+(\w+)\s*$"
)


def _strip_local_imports(source: str) -> str:
    """`from src.X import ...` / `import src.X` 行を除去する。

    ただし `from src.X import Y as Z` は `Z = Y` の alias 行に書き換える
    （bundler 環境では import は不要だが、別名参照は保持する必要がある）。

    複数行 import（`from src.X import (\\n  A,\\n  B,\\n)`）も閉じ括弧まで消す。
    """
    out_lines: list[str] = []
    lines = source.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = _IMPORT_AS_RE.match(line)
        if m:
            # `from src.X import Y as Z` → `Z = Y`
            indent = line[: len(line) - len(line.lstrip())]
            out_lines.append(f"{indent}{m.group(2)} = {m.group(1)}")
            i += 1
            continue
        if _LOCAL_IMPORT_RE.match(line):
            # 複数行 import かチェック：開き括弧が閉じているか
            buf = line
            while buf.count("(") > buf.count(")"):
                i += 1
                if i >= len(lines):
                    break
                buf += "\n" + lines[i]
            i += 1
            continue
        out_lines.append(line)
        i += 1
    return "\n".join(out_lines)


def _strip_main_guard(source: str) -> str:
    """`if __name__ == "__main__":` ブロックを末尾で除去する。"""
    lines = source.splitlines()
    # Find the line matching `if __name__ == "__main__":`
    for i, line in enumerate(lines):
        if re.match(r"^\s*if\s+__name__\s*==\s*[\"']__main__[\"']\s*:", line):
            # Drop this line and everything below it
            return "\n".join(lines[:i]).rstrip() + "\n"
    return source


def _strip_docstring_header(source: str) -> str:
    """先頭のモジュール docstring を除去する（dedup せず各ファイル分を除く）。

    理由: 連結すると module-level docstring が複数重なり、
    2 個目以降が意味不明な式文字列として残る。
    """
    # 先頭の空白行をスキップ
    lines = source.splitlines()
    idx = 0
    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1
    if idx >= len(lines):
        return source
    first = lines[idx].lstrip()
    if not (first.startswith('"""') or first.startswith("'''")):
        return source
    quote = '"""' if first.startswith('"""') else "'''"
    # 一行完結の docstring
    if first.count(quote) >= 2:
        return "\n".join(lines[idx + 1:])
    # 複数行 docstring: 終端を探す
    for j in range(idx + 1, len(lines)):
        if quote in lines[j]:
            return "\n".join(lines[j + 1:])
    return source  # 見つからなければ手を付けない


def _dedup_std_imports(combined: str) -> tuple[str, list[str]]:
    """標準系 import を dedup し、1 回だけ先頭にまとめる。

    Returns: (body 部分, 先頭に置く import 行のリスト)
    """
    std_imports: list[str] = []
    seen: set[str] = set()
    body_lines: list[str] = []
    for line in combined.splitlines():
        stripped = line.strip()
        if _STD_IMPORT_RE.match(stripped):
            if stripped not in seen:
                seen.add(stripped)
                std_imports.append(stripped)
            continue
        body_lines.append(line)
    return "\n".join(body_lines), std_imports


def build_bundled_source() -> str:
    """manifest に基づいて連結された source text を返す。

    末尾に ENTRY POINT marker と run() 関数を付加して、
    build_codemaker.py の `build_codemaker_main_text()` に渡せる形で返す。
    """
    paths = _read_manifest_paths()
    parts: list[str] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"manifest path not found: {path}")
        source = path.read_text(encoding="utf-8")
        source = _strip_local_imports(source)
        source = _strip_main_guard(source)
        source = _strip_docstring_header(source)
        rel = path.relative_to(ROOT)
        parts.append(f"\n# --- {rel} ---\n")
        parts.append(source)

    combined = "".join(parts)
    body, std_imports = _dedup_std_imports(combined)

    # scene/service が `import src.runtime.main_runtime as M` で参照していた部分を
    # 単一ファイル環境で動かすため、現モジュール自身を M として alias する
    m_alias = (
        "\n"
        "# bundled single-file では `M.X` は現モジュール自身を指す\n"
        "import sys as _sys\n"
        "M = _sys.modules[__name__]\n"
        "\n"
    )
    header = (
        '"""Block Quest — Code Maker single-file bundle (auto-generated by codemaker_bundler.py)."""\n'
        + "\n".join(std_imports)
        + "\n"
        + m_alias
    )

    # Entry point: run() を末尾に置く（app.py の run() と同義）
    entry = (
        "\n"
        "# =====================================================================\n"
        "# ENTRY POINT\n"
        "# =====================================================================\n"
        "def run():\n"
        "    global game\n"
        "    game = Game()\n"
        "    game.start()\n"
        "    return game\n"
    )

    return header + body.lstrip() + entry


def main() -> int:
    """動作確認用：bundle 出力を標準出力に印字する。"""
    print(build_bundled_source())
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
