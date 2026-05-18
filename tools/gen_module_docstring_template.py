"""対象ファイルの AST から、モジュール docstring の箇条書き雛形を生成する CLI。

Problems:
    - 新規モジュールごとに「箇条書き docstring」を手書きすると、関数定義との
      件数ズレや表記揺れが起きやすく、verify_module_docstrings の警告源になる。
    - AST と手書き docstring の整合を取り直す作業が、AI 補助のリファクタ
      サイクルの足を引っ張る。

Solutions:
    - 対象ファイルを AST 解析して、トップレベル定義とクラス内メソッドを
      階層構造で集める純粋関数を提供する。
    - 構造リストから箇条書き雛形を組み立てる純粋関数を提供する。
    - CLI 入口 run_template_cli を用意し、引数解析と出力制御を 1 か所に集約する。

このファイルに含まれる関数・クラス：

- AST を解析して、トップレベル定義とクラス内メソッドを階層構造で集める純粋関数
- 集めた構造から箇条書き docstring の文字列を組み立てる純粋関数
- 引数解析と出力制御を担う CLI 入口
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


# === Public API ===


def collect_structure(
        mod: ast.Module) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """module.body から (kind, name, children) のリストを返す。

    Args:
        mod: 解析済みのモジュール AST。

    Returns:
        list: 要素は (kind, name, children)。kind は "function" または "class"。
            children はクラスの場合のみ非空で、要素は (kind, name)。

    Policy:
        - 純粋関数として AST のトップレベル順を保ったままタプル列を返す。
    """
    return _walk_top_level(mod)


def build_template(structure: list[tuple[str, str, list[tuple[str, str]]]],
                   include_names: bool) -> str:
    """構造リストから箇条書き docstring 文字列を組み立てる。

    Args:
        structure: collect_structure() の戻り値。
        include_names: True のとき、各箇条書きの末尾に元の識別子を
            `# <name>` として残す（後で人が役割文に書き換える際の手がかり）。

    Returns:
        str: 末尾改行付きの docstring 雛形（"\"\"\"" で開閉済み）。

    Policy:
        - 文字列組み立てだけを行い、I/O や AST 解析は呼ばない。
    """
    return _format_template_lines(structure, include_names)


def run_template_cli(argv: list[str] | None = None) -> int:
    """CLI 入口。引数を解釈して雛形を生成し exit code を返す。

    Args:
        argv: argparse に渡す引数列（None で sys.argv[1:] を使う）。

    Returns:
        int: 0=成功 / 2=ファイル不在もしくは parse error。

    Policy:
        - 引数解析 / 検証 / 解析 / 既存検出 / 雛形出力の各ステップを
          private helper に委譲し、ステップ列のみを維持する。
    """
    args = _parse_args(argv)
    src = _read_source_or_exit(args.path)
    mod = _parse_module_or_exit(src)
    return _emit_or_skip(mod, args)


# === Internal helpers (private) ===


def _walk_top_level(
        mod: ast.Module) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """module.body を 1 度走査して (kind, name, children) のリストを作る。

    Args:
        mod: 解析済みのモジュール AST。

    Returns:
        list: トップレベル順の (kind, name, children) タプル列。

    Policy:
        - 関数 / async 関数 / クラスのみ拾い、それ以外のトップレベル文は無視する。
    """
    out: list[tuple[str, str, list[tuple[str, str]]]] = []
    for node in mod.body:
        entry = _build_entry_for_node(node)
        if entry is not None:
            out.append(entry)
    return out


def _build_entry_for_node(
        node: ast.stmt) -> tuple[str, str, list[tuple[str, str]]] | None:
    """1 つのトップレベル文を (kind, name, children) に変換する。

    Args:
        node: モジュール本体の AST 文。

    Returns:
        tuple | None: 関数 / クラスなら 3 タプル、それ以外は None。

    Policy:
        - 関数 / async 関数は children=[]、クラスは _class_children() に委譲。
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ("function", node.name, [])
    if isinstance(node, ast.ClassDef):
        return ("class", node.name, _class_children(node))
    return None


def _class_children(cls: ast.ClassDef) -> list[tuple[str, str]]:
    """クラス本体からメソッド名一覧を抽出する。

    Args:
        cls: クラス定義 AST。

    Returns:
        list: (kind, name) のタプル列。kind は固定で "method"。

    Policy:
        - メソッド（関数 / async 関数）のみを拾い、ネスト class は対象外。
    """
    children: list[tuple[str, str]] = []
    for body_node in cls.body:
        if isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            children.append(("method", body_node.name))
    return children


def _format_template_lines(
        structure: list[tuple[str, str, list[tuple[str, str]]]],
        include_names: bool) -> str:
    """構造リストを箇条書き docstring 文字列に整形する。

    Args:
        structure: collect_structure() の戻り値。
        include_names: True なら箇条書き末尾に元の識別子を残す。

    Returns:
        str: 末尾改行付きの docstring 文字列。

    Policy:
        - ヘッダ / 箇条書き本体 / 終端の 3 ブロックに分けて連結する。
    """
    lines: list[str] = _build_template_header()
    lines.extend(_build_template_bullets(structure, include_names))
    lines.append('"""')
    return "\n".join(lines) + "\n"


def _build_template_header() -> list[str]:
    """雛形 docstring の先頭固定行を返す。

    Returns:
        list[str]: 開きクオートから「このファイルに含まれる関数・クラス：」までの行列。

    Policy:
        - 文言は verify_module_docstrings.py が期待するフォーマットに合わせる。
    """
    return [
        '"""<モジュール概要を1行で>。',
        "",
        "このファイルに含まれる関数・クラス：",
        "",
    ]


def _build_template_bullets(
        structure: list[tuple[str, str, list[tuple[str, str]]]],
        include_names: bool) -> list[str]:
    """構造リストを箇条書き行に変換する。

    Args:
        structure: (kind, name, children) のタプル列。
        include_names: True なら末尾に `  # <name>` を付ける。

    Returns:
        list[str]: 箇条書き行列。

    Policy:
        - 関数 / クラスとも先頭は同じ `- <役割を1行で>` 形式、
          クラスのメソッドのみ 2 段インデントで続ける。
    """
    lines: list[str] = []
    for _kind, name, children in structure:
        lines.append(_format_bullet_line(name, include_names, indent=False))
        for _ckind, cname in children:
            lines.append(
                _format_bullet_line(cname, include_names, indent=True))
    return lines


def _format_bullet_line(name: str, include_names: bool, indent: bool) -> str:
    """1 行分の箇条書き文字列を組み立てる。

    Args:
        name: 元の関数 / クラス / メソッド名。
        include_names: True なら末尾に `  # name` を残す。
        indent: True ならメソッド向けに 2 スペースインデントする。

    Returns:
        str: `- <役割を1行で>` 形式の 1 行。

    Policy:
        - インデント有無と suffix 有無の 4 パタンを 1 行で表現する。
    """
    prefix = "  - " if indent else "- "
    suffix = f"  # {name}" if include_names else ""
    return f"{prefix}<役割を1行で>{suffix}"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """CLI 引数を argparse で解釈する。

    Args:
        argv: argparse に渡す引数列。

    Returns:
        argparse.Namespace: path / no_names / force を持つ名前空間。

    Policy:
        - 既存の CLI 引数体系 (path, --no-names, --force) を保持する。
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path, help="対象 .py ファイル")
    parser.add_argument(
        "--no-names",
        action="store_true",
        help="箇条書きに元の識別子コメントを付けない",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="既に箇条書き docstring を持つファイルでも雛形を生成する",
    )
    return parser.parse_args(argv)


def _read_source_or_exit(path: Path) -> str:
    """対象ファイルを読み、無ければ exit 2 で離脱する。

    Args:
        path: 対象 .py ファイルのパス。

    Returns:
        str: ファイル内容 (UTF-8)。

    Raises:
        SystemExit: ファイルが存在しないとき exit code 2 で終了する。

    Policy:
        - I/O エラーは CLI のエラー出口として stderr + exit 2 に集約する。
    """
    if not path.is_file():
        print(f"file not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    return path.read_text(encoding="utf-8")


def _parse_module_or_exit(src: str) -> ast.Module:
    """ソース文字列を AST に解析し、SyntaxError なら exit 2 で離脱する。

    Args:
        src: Python ソースコード文字列。

    Returns:
        ast.Module: 解析結果。

    Raises:
        SystemExit: SyntaxError のとき exit code 2 で終了する。

    Policy:
        - parse error はメッセージを stderr に出し、CLI 全体を exit 2 にする。
    """
    try:
        return ast.parse(src)
    except SyntaxError as exc:
        print(f"parse error: {exc!r}", file=sys.stderr)
        raise SystemExit(2)


def _emit_or_skip(mod: ast.Module, args: argparse.Namespace) -> int:
    """既存箇条書きを検出して skip するか、雛形を出力する。

    Args:
        mod: 解析済みのモジュール AST。
        args: 解析済みの CLI 引数。

    Returns:
        int: 常に 0（整備済 / 構造空 / 出力成功のいずれでも 0）。

    Policy:
        - --force でなければ箇条書き済みかを判定し、整備済なら警告のみ。
        - そうでなければ collect_structure → build_template の本処理に進む。
    """
    if _has_existing_bullet_docstring(mod, args.force, args.path):
        return 0
    return _emit_template(mod, args)


def _has_existing_bullet_docstring(
        mod: ast.Module, force: bool, path: Path) -> bool:
    """既に箇条書き docstring を持つかを判定する。

    Args:
        mod: 解析済みのモジュール AST。
        force: --force 指定時は常に False を返す。
        path: メッセージ用の対象ファイルパス。

    Returns:
        bool: 整備済として早期 return すべきなら True。

    Policy:
        - --force があれば判定をスキップ、無ければ `- ` 始まり行の有無で判定。
    """
    if force:
        return False
    if not _has_bullets_in_docstring(_read_module_docstring(mod)):
        return False
    print(
        f"already has bullet docstring: {path} (use --force to regenerate)",
        file=sys.stderr,
    )
    return True


def _read_module_docstring(mod: ast.Module) -> str:
    """モジュール docstring を空文字フォールバック付きで返す。

    Args:
        mod: 解析済みのモジュール AST。

    Returns:
        str: docstring 本文（無ければ空文字列）。

    Policy:
        - None を返さず空文字に丸めることで、後段の splitlines を安全に保つ。
    """
    docstring = ast.get_docstring(mod)
    if docstring is None:
        return ""
    return docstring


def _has_bullets_in_docstring(docstring: str) -> bool:
    """docstring に箇条書き行が含まれるかを判定する。

    Args:
        docstring: 既存 module docstring。

    Returns:
        bool: `- ` で始まる行があれば True。

    Policy:
        - 1 行でも箇条書きがあれば「整備済」とみなす。
    """
    for line in docstring.splitlines():
        if line.startswith("- "):
            return True
    return False


def _emit_template(mod: ast.Module, args: argparse.Namespace) -> int:
    """構造を抽出し、雛形を stdout に書き出して exit code を返す。

    Args:
        mod: 解析済みのモジュール AST。
        args: 解析済みの CLI 引数。

    Returns:
        int: 常に 0（構造が空なら警告を出して 0）。

    Policy:
        - 構造が空のときは何も書き出さず警告のみ、0 を返す。
    """
    structure = collect_structure(mod)
    if not structure:
        print(f"no top-level def / class: {args.path}", file=sys.stderr)
        return 0
    out = build_template(structure, include_names=not args.no_names)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_template_cli())
