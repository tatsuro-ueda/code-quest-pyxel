"""src/ 配下のモジュール docstring と実コードの整合を検証する CLI。

このファイルに含まれる関数・クラス：

- 対象ファイルを列挙する純粋関数（src/ 配下から __init__.py / generated/ を除外）
- 1 ファイルの docstring 件数 == AST 件数を判定する純粋関数
- 不整合内容を整形して stderr に出すヘルパ
- main：引数解析と全件走査と exit code 制御
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path


def iter_target_files(root: Path) -> list[Path]:
    """検証対象の .py ファイルを返す（__init__.py と generated/ 配下は除外）。"""
    out: list[Path] = []
    for p in sorted(root.rglob("*.py")):
        if p.name == "__init__.py":
            continue
        if any(part == "generated" for part in p.parts):
            continue
        if any(part == "__pycache__" for part in p.parts):
            continue
        out.append(p)
    return out


def check_one(path: Path, skip_missing: bool) -> tuple[bool, list[str]]:
    """1 ファイルを検証して (ok, messages) を返す。

    skip_missing=True のとき、docstring が無い／箇条書き docstring が無いファイルは検査をスキップ。
    定数定義のみのファイル（top_defs == 0）は件数比較の対象外（箇条書きで定数の役割を説明できる）。
    """
    try:
        src = path.read_text(encoding="utf-8")
        mod = ast.parse(src)
    except (SyntaxError, UnicodeDecodeError) as e:
        return False, [f"{path}: parse error ({e!r})"]

    docstring = ast.get_docstring(mod)
    top_defs = [n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    classes = [n for n in mod.body if isinstance(n, ast.ClassDef)]
    methods_total = sum(
        len([b for b in c.body if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef))])
        for c in classes
    )

    if docstring is None:
        if skip_missing:
            return True, []
        if not top_defs:
            return True, []
        return False, [f"{path}: missing module docstring (top defs: {len(top_defs)})"]

    lines = docstring.splitlines()
    bullets_top = [l for l in lines if re.match(r"^- .+", l)]
    bullets_nest = [l for l in lines if re.match(r"^  - .+", l)]

    if not bullets_top and skip_missing:
        return True, []

    if not top_defs:
        return True, []

    msgs: list[str] = []
    if len(top_defs) != len(bullets_top):
        msgs.append(
            f"{path}: top mismatch (AST defs={len(top_defs)}, docstring bullets={len(bullets_top)})"
        )
    if methods_total != len(bullets_nest):
        msgs.append(
            f"{path}: method mismatch (AST methods={methods_total}, docstring nests={len(bullets_nest)})"
        )
    return (not msgs), msgs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", type=Path, help="検査対象のルートディレクトリ（例: src/）")
    parser.add_argument(
        "--skip-missing-docstring",
        action="store_true",
        help="docstring が無いファイルをスキップする（段階移行モード）",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="docstring 未整備ファイルもエラーにする（横展開完了後の運用モード）",
    )
    args = parser.parse_args(argv)

    if args.strict:
        skip_missing = False
    else:
        skip_missing = args.skip_missing_docstring

    targets = iter_target_files(args.root)
    fail_count = 0
    checked = 0
    for p in targets:
        ok, msgs = check_one(p, skip_missing=skip_missing)
        checked += 1
        if not ok:
            fail_count += 1
            for m in msgs:
                print(m, file=sys.stderr)

    if fail_count == 0:
        print(f"{checked} files OK", file=sys.stdout)
        return 0
    print(f"FAIL: {fail_count}/{checked} files have docstring drift", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
