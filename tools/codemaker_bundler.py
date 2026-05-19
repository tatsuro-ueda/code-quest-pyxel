"""Code Maker 用 bundler (Q4B: concat 生成型)。

このファイルに含まれる関数:

- build_bundled_source: manifest に基づき連結された source text を返す
- run_main: 動作確認用に bundle 出力を標準出力に印字する

Problems:
    - Code Maker 環境は単一 main.py のみで動くため、`from src.X` 系の import を
      そのまま残すと未定義参照になる。`as` alias を見落とすと過去に
      `_stats_for_level_defense is not defined` のような実行時クラッシュが起きた。
    - 連結処理を 1 関数に詰め込むと CR202/CR203/CR204 のステップ列ポリシーを
      満たせず、ローカル import 除去・main guard 切り取り・docstring 除去・
      標準 import dedup の各責務が混ざる。

Solutions:
    - 各処理を private helper に切り出し、build_bundled_source は
      「述語呼び出し + private 委譲 + return」のステップ列に揃える。
    - 多行 `as` alias の抽出と単行 `as` alias の書き換えを専用 helper で扱い、
      過去バグの再発を防ぐ。

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


# === Public API ===

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools" / "codemaker_manifest.txt"

# 連結時に除去する import パターン
# `from src.X import Y` / `from src.X.Y import *` / `import src.X.Y`
_LOCAL_IMPORT_RE = re.compile(r"^\s*from\s+src\.|^\s*import\s+src\.")

# 連結時に dedup する標準系 import（最初の 1 回だけ残す）
_STD_IMPORT_RE = re.compile(
    r"^(from\s+__future__\s+import\s+annotations|"
    r"import\s+"
    r"(pyxel|random|sys|hashlib|json|typing|pathlib|io|os|re|math)(\s|$)|"
    r"from\s+"
    r"(pathlib|typing|dataclasses|io|os|re|math|hashlib|json)\s+import\s+)"
)


def build_bundled_source() -> str:
    """manifest に基づいて連結された source text を返す。

    Returns:
        ENTRY POINT marker と run() 関数を末尾に持つ単一 source text。

    Raises:
        FileNotFoundError: manifest に列挙されたパスが見つからない場合。

    Policy:
        - manifest の各 .py を読み、ローカル import / main guard /
          docstring を private helper で除去して連結する。
        - 末尾に ENTRY POINT marker を付与し build_codemaker.py に渡せる形にする。
    """
    return _assemble_bundled_source()


def run_main() -> int:  # noqa: CR100
    """動作確認用：bundle 出力を標準出力に印字する。

    Returns:
        常に 0。

    Policy:
        - bundle 生成は build_bundled_source に委譲し、stdout に流す。
    """
    print(build_bundled_source())
    return 0


# === Internal helpers (private) ===


_IMPORT_AS_RE = re.compile(
    r"^\s*from\s+src\.[^\s]+\s+import\s+(\w+)\s+as\s+(\w+)\s*$"
)


def _read_manifest_paths() -> list[Path]:
    """codemaker_manifest.txt をパース可能なパスのリストに変換する。

    Returns:
        コメント/空行を除いた絶対パス（ROOT 配下）のリスト。

    Policy:
        - 先頭 `#` 行と空行はスキップする。
    """
    paths: list[Path] = []
    for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if _is_skippable_manifest_line(line):
            continue
        paths.append(ROOT / line)
    return paths


def _is_skippable_manifest_line(line: str) -> bool:
    """manifest 行をスキップすべきかを判定する。

    Args:
        line: strip 済みの 1 行。

    Returns:
        空行またはコメント行なら True。

    Policy:
        - 純粋な述語（True/False）。
    """
    if not line:
        return True
    return line.startswith("#")


def _strip_local_imports(source: str) -> str:
    """`from src.X import ...` / `import src.X` 行を除去する。

    ただし `from src.X import Y as Z`（単行・多行どちらも）は `Z = Y` の
    alias 行に書き換える（bundler 環境では import は不要だが、別名参照は保持する必要がある）。

    複数行 import（`from src.X import (\\n  A,\\n  B as C,\\n)`）も閉じ括弧まで
    消すが、内部の `as` エイリアスだけは抽出して alias 行を残す。

    Args:
        source: 1 ファイル分の source 文字列。

    Returns:
        ローカル import を除去し alias 行に置き換えた source。

    Policy:
        - `from src.X import Y as Z` は単行/多行ともに `Z = Y` 行を残す。
        - `import src.X.Y` は alias を出さずに削除のみ。
    """
    out_lines: list[str] = []
    lines = source.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        i = _consume_one_import_line(lines, i, out_lines, line)
    return "\n".join(out_lines)


def _consume_one_import_line(
    lines: list[str],
    cursor: int,
    out_lines: list[str],
    line: str,
) -> int:
    """1 行を読み、判定結果に応じて out_lines に書き込み次の cursor を返す。

    Args:
        lines: 全行リスト。
        cursor: 現在の行インデックス。
        out_lines: 出力先（in-place 更新）。
        line: 現在行（lines[cursor]）。

    Returns:
        次に処理すべき行インデックス。

    Policy:
        - 単行 `as` alias は書き換え、ローカル import なら丸ごと消して
          内部 alias を抽出、それ以外はそのまま追加する。
    """
    single_match = _IMPORT_AS_RE.match(line)
    if single_match is not None:
        _emit_single_as_alias(out_lines, line, single_match)
        return cursor + 1
    if _LOCAL_IMPORT_RE.match(line):
        return _consume_local_import_block(lines, cursor, out_lines, line)
    out_lines.append(line)
    return cursor + 1


def _emit_single_as_alias(
    out_lines: list[str],
    line: str,
    match: re.Match,
) -> None:
    """単行 `from src.X import Y as Z` を `Z = Y` 行で書き出す。

    Args:
        out_lines: 出力先（in-place 更新）。
        line: 元の import 行（indent 抽出に使う）。
        match: _IMPORT_AS_RE のマッチオブジェクト。

    Policy:
        - 元行の indent を保ったまま alias 文を 1 行追加する。
    """
    indent = line[: len(line) - len(line.lstrip())]
    out_lines.append(f"{indent}{match.group(2)} = {match.group(1)}")


def _consume_local_import_block(
    lines: list[str],
    cursor: int,
    out_lines: list[str],
    line: str,
) -> int:
    """複数行に渡るローカル import を消費して alias 行だけ残す。

    Args:
        lines: 全行リスト。
        cursor: 開き行のインデックス。
        out_lines: 出力先（in-place 更新）。
        line: 現在行。

    Returns:
        閉じ括弧の次の行インデックス。

    Policy:
        - 開き括弧と閉じ括弧の数が揃うまで buf に集約し、内部 `as` alias を抽出する。
    """
    buf = line
    indent = line[: len(line) - len(line.lstrip())]
    next_cursor = cursor
    while buf.count("(") > buf.count(")"):
        next_cursor += 1
        if next_cursor >= len(lines):
            break
        buf += "\n" + lines[next_cursor]
    _emit_block_as_aliases(out_lines, buf, indent)
    return next_cursor + 1


def _emit_block_as_aliases(
    out_lines: list[str],
    buf: str,
    indent: str,
) -> None:
    """複数行 import 内の `Y as Z` を全て alias 行に書き出す。

    Args:
        out_lines: 出力先（in-place 更新）。
        buf: 連結された import ブロック文字列。
        indent: 出力時に保つ indent。

    Policy:
        - `from src.X import (..., Y as Z, ...)` のみ対象。
          `import src.X.Y as Z`（モジュール import）は対象外。
    """
    if not re.match(r"\s*from\s+src\.", buf):
        return
    inner = buf.split("import", 1)[1] if "import" in buf else ""
    for alias_match in re.finditer(r"\b(\w+)\s+as\s+(\w+)\b", inner):
        out_lines.append(
            f"{indent}{alias_match.group(2)} = {alias_match.group(1)}"
        )


def _strip_main_guard(source: str) -> str:
    """`if __name__ == "__main__":` ブロックを末尾で除去する。

    Args:
        source: 1 ファイル分の source 文字列。

    Returns:
        main guard 以降を取り除いた source。

    Policy:
        - main guard の出現位置を境界に切り取り、改行で正規化する。
    """
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^\s*if\s+__name__\s*==\s*[\"']__main__[\"']\s*:", line):
            return "\n".join(lines[:i]).rstrip() + "\n"
    return source


def _strip_docstring_header(source: str) -> str:
    """先頭のモジュール docstring を除去する（dedup せず各ファイル分を除く）。

    Args:
        source: 1 ファイル分の source 文字列。

    Returns:
        モジュール docstring を取り除いた source。

    Policy:
        - 連結すると module-level docstring が複数重なり、2 個目以降が
          意味不明な式文字列として残るため除去する。
        - 三重引用符の単行/複数行のいずれにも対応する。
    """
    lines = source.splitlines()
    cursor = _skip_leading_blank_lines(lines)
    if cursor >= len(lines):
        return source
    first = lines[cursor].lstrip()
    if not _has_docstring_opener(first):
        return source
    quote = '"""' if first.startswith('"""') else "'''"
    return _drop_docstring_block(lines, cursor, first, quote, source)


def _skip_leading_blank_lines(lines: list[str]) -> int:
    """空行を読み飛ばし、最初の非空行インデックスを返す。

    Args:
        lines: 行リスト。

    Returns:
        最初の非空行のインデックス（全部空なら len(lines)）。

    Policy:
        - strip() で空判定する。
    """
    cursor = 0
    while cursor < len(lines) and lines[cursor].strip() == "":
        cursor += 1
    return cursor


def _has_docstring_opener(line: str) -> bool:
    '''行が三重引用符で始まるかを判定する。

    Args:
        line: lstrip 済みの行。

    Returns:
        三重ダブル/シングルの引用符いずれかで始まるなら True。

    Policy:
        - 純粋な述語（True/False）。
    '''
    if line.startswith('"""'):
        return True
    return line.startswith("'''")


def _drop_docstring_block(
    lines: list[str],
    cursor: int,
    first: str,
    quote: str,
    fallback: str,
) -> str:
    '''先頭 docstring ブロックを除去した残りを返す。

    Args:
        lines: 全行リスト。
        cursor: docstring の先頭行インデックス。
        first: lstrip 済みの先頭行（一行 docstring の判定に使う）。
        quote: 三重引用符の種類（三重ダブル or 三重シングル）。
        fallback: docstring 終端が見つからないときに返す元の source。

    Returns:
        docstring を取り除いた残りの source。

    Policy:
        - 同じ行に閉じ三重引用符があれば一行 docstring として扱う。
    '''
    if first.count(quote) >= 2:
        return "\n".join(lines[cursor + 1:])
    for j in range(cursor + 1, len(lines)):
        if quote in lines[j]:
            return "\n".join(lines[j + 1:])
    return fallback


def _collect_dedup_std_imports(combined: str) -> tuple[str, list[str]]:
    """標準系 import を dedup し、1 回だけ先頭にまとめる。

    Args:
        combined: 連結後の source 全文。

    Returns:
        (body 部分, 先頭に置く import 行のリスト) のタプル。

    Policy:
        - _STD_IMPORT_RE にマッチする行は body から外し、seen 集合で重複排除する。
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


def _assemble_bundled_source() -> str:
    """build_bundled_source の本体（連結 + header + entry のステップ列）。

    Returns:
        ENTRY POINT marker と run() を末尾に含む完成済み source。

    Raises:
        FileNotFoundError: manifest 内のパスが存在しない場合。

    Policy:
        - manifest を読み、各 .py を順に変換・連結してから header/entry を足す。
    """
    paths = _read_manifest_paths()
    combined = _build_concat_manifest_files(paths)
    body, std_imports = _collect_dedup_std_imports(combined)
    header = _render_bundle_header(std_imports)
    entry = _render_entry_point()
    return header + body.lstrip() + entry


def _build_concat_manifest_files(paths: list[Path]) -> str:
    """manifest のファイルを順に読み、変換しつつ連結する。

    Args:
        paths: manifest が指す絶対パスのリスト。

    Returns:
        連結後の生 source（dedup 前）。

    Raises:
        FileNotFoundError: いずれかのパスが見つからない場合。

    Policy:
        - ローカル import 除去 / main guard 除去 / docstring 除去を順に適用する。
    """
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
    return "".join(parts)


def _render_bundle_header(std_imports: list[str]) -> str:
    """bundle 先頭の docstring + 標準 import + M alias を返す。

    Args:
        std_imports: dedup 済みの標準 import 行リスト。

    Returns:
        先頭ヘッダー文字列。

    Policy:
        - scene/service が `import src.runtime.main_runtime as M` で参照していた
          部分を、bundled 環境では現モジュール自身を M として alias する。
    """
    m_alias = (
        "\n"
        "# bundled single-file では `M.X` は現モジュール自身を指す\n"
        "import sys as _sys\n"
        "M = _sys.modules[__name__]\n"
        "\n"
    )
    doc_line = (
        '"""Block Quest — Code Maker single-file bundle '
        '(auto-generated by codemaker_bundler.py)."""\n'
    )
    return (
        doc_line
        + "\n".join(std_imports)
        + "\n"
        + m_alias
    )


def _render_entry_point() -> str:
    """末尾の ENTRY POINT marker と run() 関数を返す。

    Returns:
        bundle 末尾に貼り付ける entry point ブロック。

    Policy:
        - app.py の run() と同義の最小実装にする。
    """
    bar = (
        "# ==================================================================="
        "=="
    )
    return (
        "\n"
        f"{bar}\n"
        "# ENTRY POINT\n"
        f"{bar}\n"
        "def run():\n"
        "    global game\n"
        "    game = Game()\n"
        "    game.start()\n"
        "    return game\n"
    )


if __name__ == "__main__":
    import sys
    sys.exit(run_main())
