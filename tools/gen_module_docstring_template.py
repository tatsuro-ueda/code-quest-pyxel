"""対象ファイルの AST から、モジュール docstring の箇条書き雛形を生成する CLI。

このファイルに含まれる関数・クラス：

- AST を解析して、トップレベル定義とクラス内メソッドを階層構造で集める純粋関数
- 集めた構造から箇条書き docstring の文字列を組み立てる純粋関数
- main：引数解析と出力制御
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


def collect_structure(mod: ast.Module) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """module.body から (kind, name, children) のリストを返す。

    kind: "function" | "class"
    children: クラスの場合のみ非空。要素は (kind, name)
    """
    out: list[tuple[str, str, list[tuple[str, str]]]] = []
    for n in mod.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(("function", n.name, []))
        elif isinstance(n, ast.ClassDef):
            children: list[tuple[str, str]] = []
            for b in n.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    children.append(("method", b.name))
            out.append(("class", n.name, children))
    return out


def build_template(structure: list[tuple[str, str, list[tuple[str, str]]]],
                   include_names: bool) -> str:
    """構造リストから箇条書き docstring 文字列を組み立てる。

    include_names=True のとき、各箇条書きの末尾に元の識別子を `# <name>` として残す
    （後で人が役割文に書き換える際の手がかり）。
    """
    lines: list[str] = []
    lines.append('"""<モジュール概要を1行で>。')
    lines.append("")
    lines.append("このファイルに含まれる関数・クラス：")
    lines.append("")
    for kind, name, children in structure:
        suffix = f"  # {name}" if include_names else ""
        if kind == "function":
            lines.append(f"- <役割を1行で>{suffix}")
        else:
            lines.append(f"- <役割を1行で>{suffix}")
            for ckind, cname in children:
                csuffix = f"  # {cname}" if include_names else ""
                lines.append(f"  - <役割を1行で>{csuffix}")
    lines.append('"""')
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
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
    args = parser.parse_args(argv)

    if not args.path.is_file():
        print(f"file not found: {args.path}", file=sys.stderr)
        return 2
    src = args.path.read_text(encoding="utf-8")
    try:
        mod = ast.parse(src)
    except SyntaxError as e:
        print(f"parse error: {e!r}", file=sys.stderr)
        return 2

    if not args.force:
        existing = ast.get_docstring(mod) or ""
        # 既に "- " で始まる行を含む docstring があれば「整備済」扱い
        for line in existing.splitlines():
            if line.startswith("- "):
                print(f"already has bullet docstring: {args.path} (use --force to regenerate)",
                      file=sys.stderr)
                return 0

    structure = collect_structure(mod)
    if not structure:
        print(f"no top-level def / class: {args.path}", file=sys.stderr)
        return 0

    out = build_template(structure, include_names=not args.no_names)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
