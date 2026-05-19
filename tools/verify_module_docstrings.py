"""src/ 配下のモジュール docstring と実コードの整合を検証する CLI。

このファイルに含まれる関数:

- iter_target_files: 対象 .py ファイルを列挙する純粋関数
- check_one: 1 ファイルの docstring 件数 == AST 件数を判定する
- run_main: 引数解析と全件走査と exit code 制御

Problems:
    - module docstring に書いた箇条書きと AST 定義件数がズレると、
      AI 補助の読み書き時に「どこに何が書いてあるか」の前提が崩れる。
    - 検査ロジックを 1 関数に詰め込むと CR202/CR203/CR204 のステップ列
      ポリシーを満たせず、bullets 抽出・比較・出力の責務が混ざる。

Solutions:
    - bullets 抽出・件数比較・パース・出力を private helper に切り出し、
      public 関数は「述語呼び出し + private 委譲 + return」のステップ列に揃える。
    - --skip-missing-docstring と --strict は段階移行モードとして残し、
      docstring 検証ロジックを変更しない。
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path


# === Public API ===


def iter_target_files(root: Path) -> list[Path]:
    """検証対象の .py ファイルを返す（__init__.py / generated / __pycache__ 除外）。

    Args:
        root: 走査ルートディレクトリ（例: src/）。

    Returns:
        ソート済みの対象 .py ファイルのパスリスト。

    Policy:
        - __init__.py、generated 配下、__pycache__ 配下は除外する。
    """
    return _list_target_files(root)


def check_one(path: Path, skip_missing: bool) -> tuple[bool, list[str]]:
    """1 ファイルを検証して (ok, messages) を返す。

    Args:
        path: 検査対象の .py ファイル。
        skip_missing: True なら docstring 無し／箇条書き無しを skip する。

    Returns:
        (ok, messages) のタプル。ok=False のとき messages に詳細を入れる。

    Policy:
        - skip_missing=True のとき、docstring が無い／箇条書き docstring が
          無いファイルは検査をスキップ。
        - 定数定義のみのファイル（top_defs == 0）は件数比較の対象外。
    """
    return _run_check_one(path, skip_missing)


def run_main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """CLI エントリ：引数解析と全件走査と exit code 制御を行う。

    Args:
        argv: argparse に渡す引数列（None なら sys.argv[1:] 相当）。

    Returns:
        全件 OK で 0、いずれか不整合で 1。

    Policy:
        - --strict が指定されたら skip_missing=False、それ以外は引数に従う。
    """
    args = _parse_args(argv)
    skip_missing = _resolve_skip_missing(args)
    return _run_check_all(args.root, skip_missing)


# === Internal helpers (private) ===


def _list_target_files(root: Path) -> list[Path]:
    """iter_target_files 本体。__init__.py / generated / __pycache__ を除外する。

    Args:
        root: 走査ルートディレクトリ。

    Returns:
        対象 .py ファイルのソート済みパスリスト。

    Policy:
        - 除外条件は _is_skippable_target で判定する。
    """
    out: list[Path] = []
    for path in sorted(root.rglob("*.py")):
        if _is_skippable_target(path):
            continue
        out.append(path)
    return out


def _is_skippable_target(path: Path) -> bool:
    """検査対象から除外すべきファイルかを判定する。

    Args:
        path: 候補ファイルのパス。

    Returns:
        除外対象なら True。

    Policy:
        - __init__.py、generated 配下、__pycache__ 配下を弾く。
    """
    if path.name == "__init__.py":
        return True
    if any(part == "generated" for part in path.parts):
        return True
    return any(part == "__pycache__" for part in path.parts)


def _run_check_one(
    path: Path,
    skip_missing: bool,
) -> tuple[bool, list[str]]:
    """check_one の本体（パース → docstring 判定 → 件数比較）。

    Args:
        path: 検査対象 .py ファイル。
        skip_missing: 段階移行モードのフラグ。

    Returns:
        (ok, messages) のタプル。

    Policy:
        - parse 失敗は False を即返し、それ以外は docstring 判定 → 件数比較。
    """
    parse_result = _parse_module_safely(path)
    if parse_result is None:
        return False, [_format_parse_error_message(path)]
    mod = parse_result
    docstring = ast.get_docstring(mod)
    top_defs = _collect_top_defs(mod)
    methods_total = _count_class_methods(mod)
    if docstring is None:
        return _handle_missing_docstring(path, skip_missing, top_defs)
    return _compare_bullets_with_defs(
        path, docstring, skip_missing, top_defs, methods_total,
    )


def _parse_module_safely(path: Path) -> ast.Module | None:
    """ファイルを読み込み AST.Module にパースする。失敗時は None。

    Args:
        path: 検査対象 .py ファイル。

    Returns:
        パース成功時は AST.Module、失敗時は None。

    Policy:
        - SyntaxError / UnicodeDecodeError のみを捕捉する。
    """
    try:
        src = path.read_text(encoding="utf-8")
        return ast.parse(src)
    except (SyntaxError, UnicodeDecodeError):
        return None


def _format_parse_error_message(path: Path) -> str:
    """parse 失敗時のメッセージを 1 行で返す。

    Args:
        path: 検査対象ファイル。

    Returns:
        ユーザ向けの parse error 行。

    Policy:
        - 元実装と同形式（{path}: parse error ({exc!r})）を維持する。
    """
    try:
        path.read_text(encoding="utf-8")
        ast.parse(path.read_text(encoding="utf-8"))
        return f"{path}: parse error (None)"
    except (SyntaxError, UnicodeDecodeError) as exc:
        return f"{path}: parse error ({exc!r})"


def _collect_top_defs(mod: ast.Module) -> list[ast.stmt]:
    """モジュール直下の関数/クラス定義をリストで返す。

    Args:
        mod: パース済み AST.Module。

    Returns:
        FunctionDef / AsyncFunctionDef / ClassDef のリスト。

    Policy:
        - top-level のみを対象にし、ネスト定義は数えない。
    """
    return [
        node
        for node in mod.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        )
    ]


def _count_class_methods(mod: ast.Module) -> int:
    """モジュール内の全クラスのメソッド数を合計する。

    Args:
        mod: パース済み AST.Module。

    Returns:
        各クラスの FunctionDef/AsyncFunctionDef 件数の合計。

    Policy:
        - ネストクラスは扱わない（top-level クラスのみ）。
    """
    classes = [n for n in mod.body if isinstance(n, ast.ClassDef)]
    total = 0
    for cls in classes:
        for body_node in cls.body:
            if isinstance(
                body_node, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                total += 1
    return total


def _handle_missing_docstring(
    path: Path,
    skip_missing: bool,
    top_defs: list[ast.stmt],
) -> tuple[bool, list[str]]:
    """docstring が存在しない場合の判定を返す。

    Args:
        path: 検査対象ファイル。
        skip_missing: True なら無条件で OK 扱い。
        top_defs: top-level 定義のリスト。

    Returns:
        (ok, messages) のタプル。

    Policy:
        - skip_missing なら OK、top_defs が空でも OK、それ以外は不整合。
    """
    if skip_missing:
        return True, []
    if not top_defs:
        return True, []
    return False, [
        f"{path}: missing module docstring (top defs: {len(top_defs)})"
    ]


def _compare_bullets_with_defs(
    path: Path,
    docstring: str,
    skip_missing: bool,
    top_defs: list[ast.stmt],
    methods_total: int,
) -> tuple[bool, list[str]]:
    """docstring の箇条書きと AST 件数を比較して結果を返す。

    Args:
        path: 検査対象ファイル。
        docstring: モジュール docstring。
        skip_missing: True かつ top bullets 無しなら skip。
        top_defs: top-level 定義のリスト。
        methods_total: 全クラスのメソッド数合計。

    Returns:
        (ok, messages) のタプル。

    Policy:
        - top bullets と top_defs、nest bullets と methods_total を比較する。
    """
    bullets_top, bullets_nest = _extract_bullets(docstring)
    if _can_skip_for_missing_bullets(bullets_top, skip_missing):
        return True, []
    if not top_defs:
        return True, []
    msgs = _build_mismatch_messages(
        path, top_defs, bullets_top, methods_total, bullets_nest,
    )
    return (not msgs), msgs


def _can_skip_for_missing_bullets(
    bullets_top: list[str],
    skip_missing: bool,
) -> bool:
    """top bullets が無く skip_missing が True なら検査をスキップしてよい。

    Args:
        bullets_top: 抽出した top 箇条書き行。
        skip_missing: 段階移行モードのフラグ。

    Returns:
        skip 可能なら True。

    Policy:
        - 純粋な述語（True/False）。
    """
    if bullets_top:
        return False
    return skip_missing


def _extract_bullets(docstring: str) -> tuple[list[str], list[str]]:
    """docstring から top/nest の箇条書き行を抽出する。

    Args:
        docstring: モジュール docstring。

    Returns:
        (top bullets, nest bullets) のタプル。

    Policy:
        - top は `- ` で始まる行、nest は `  - ` で始まる行（2 スペース indent）。
    """
    lines = docstring.splitlines()
    bullets_top = [ln for ln in lines if re.match(r"^- .+", ln)]
    bullets_nest = [ln for ln in lines if re.match(r"^  - .+", ln)]
    return bullets_top, bullets_nest


def _build_mismatch_messages(
    path: Path,
    top_defs: list[ast.stmt],
    bullets_top: list[str],
    methods_total: int,
    bullets_nest: list[str],
) -> list[str]:
    """件数差分があれば対応するエラーメッセージを並べて返す。

    Args:
        path: 検査対象ファイル。
        top_defs: top-level 定義のリスト。
        bullets_top: top 箇条書きの行。
        methods_total: クラスメソッドの総数。
        bullets_nest: nest 箇条書きの行。

    Returns:
        差分メッセージ（無ければ空）。

    Policy:
        - top 不一致と method 不一致を独立に出力する。
    """
    msgs: list[str] = []
    if len(top_defs) != len(bullets_top):
        msgs.append(
            f"{path}: top mismatch (AST defs={len(top_defs)},"
            f" docstring bullets={len(bullets_top)})"
        )
    if methods_total != len(bullets_nest):
        msgs.append(
            f"{path}: method mismatch (AST methods={methods_total},"
            f" docstring nests={len(bullets_nest)})"
        )
    return msgs


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """argparse で CLI 引数を解析する。

    Args:
        argv: argparse に渡す引数列。

    Returns:
        argparse.Namespace。

    Policy:
        - --skip-missing-docstring と --strict の両方を受け付ける。
    """
    module_doc = __doc__ if isinstance(__doc__, str) else ""
    description = module_doc.splitlines()[0] if module_doc else ""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "root", type=Path,
        help="検査対象のルートディレクトリ（例: src/）",
    )
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
    return parser.parse_args(argv)


def _resolve_skip_missing(args: argparse.Namespace) -> bool:
    """skip_missing の最終値を判定する。

    Args:
        args: argparse 結果。

    Returns:
        skip_missing として使うべき bool。

    Policy:
        - --strict が指定されたら False に強制する。
    """
    if args.strict:
        return False
    return bool(args.skip_missing_docstring)


def _run_check_all(root: Path, skip_missing: bool) -> int:
    """全 target に対して check_one を回し exit code を返す。

    Args:
        root: 走査ルートディレクトリ。
        skip_missing: 段階移行モードのフラグ。

    Returns:
        全件 OK で 0、いずれか不整合で 1。

    Policy:
        - 不整合があれば fail を集計して FAIL 行を 1 行 stderr に出す。
    """
    targets = iter_target_files(root)
    fail_count, checked = _count_check_results(targets, skip_missing)
    if fail_count == 0:
        print(f"{checked} files OK", file=sys.stdout)
        return 0
    print(
        f"FAIL: {fail_count}/{checked} files have docstring drift",
        file=sys.stderr,
    )
    return 1


def _count_check_results(
    targets: list[Path],
    skip_missing: bool,
) -> tuple[int, int]:
    """各 target を検査し (fail_count, checked) を返す。

    Args:
        targets: 検査対象のパスリスト。
        skip_missing: 段階移行モードのフラグ。

    Returns:
        (fail_count, checked) のタプル。

    Policy:
        - 失敗時はメッセージを stderr に出す。
    """
    fail_count = 0
    checked = 0
    for path in targets:
        is_ok, msgs = check_one(path, skip_missing=skip_missing)
        checked += 1
        if not is_ok:
            fail_count += 1
            for message in msgs:
                print(message, file=sys.stderr)
    return fail_count, checked


if __name__ == "__main__":
    raise SystemExit(run_main())
