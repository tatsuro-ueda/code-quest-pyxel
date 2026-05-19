"""top_changes.json → index.html マーカー間 inject の純粋 render。

このファイルに含まれる関数：

- top_changes.json から changes リストを取り出す public 関数 load_changes
- マーカー間に挿入する HTML ブロック文字列を組み立てる public 関数 render_block
- index.html のマーカー間を block で置換する public 関数 inject_into_index
- CLI 入口の public 関数 run_render（引数解析と stdout 出力と exit code 制御）
- top_changes.json をデコードして dict を返す内部関数 _decode_top_changes
- changes フィールドを取り出して list[str] に正規化する内部関数 _coerce_changes
- changes が list でなければ ValueError を投げる内部関数 _require_changes_list
- マーカー間 li 行を組み立てる内部関数 _render_change_items
- index.html にマーカー対が揃っているかを判定する述語関数 _has_marker_pair
- マーカー間置換と書き戻しを担う内部関数 _replace_marker_block
- argparse を構成して Namespace を返す内部関数 _build_arg_parser
- 出力ログ文字列を組み立てる内部関数 _format_render_log

Problems:
    - top_changes.json の整形と HTML マーカー置換を 1 つの main に直書きすると、
      JSON 入力検証と HTML 置換の責務が混ざって読み手に負荷をかける。
    - public 関数が制御フローを直接含むと、エラー文言や行数上限などの
      局所ルールを変更しづらくなる。

Solutions:
    - public 関数は「述語呼び出し + private 委譲 + return」のステップ列に
      揃え、JSON 整形・HTML 置換・ログ文字列組み立てを private に委ねる。
    - CLI 入口は run_render として main alias を維持する。

使用例:
    python3 tools/render_top_changes.py            # デフォルトで先頭 5 件
    python3 tools/render_top_changes.py --max 8    # 先頭 8 件
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_INDEX_PATH = ROOT / "index.html"
DEFAULT_TOP_CHANGES_PATH = ROOT / "top_changes.json"
DEFAULT_MAX_RENDER = 5

START_MARKER = "<!-- TOP_CHANGES_START -->"
END_MARKER = "<!-- TOP_CHANGES_END -->"

# DOTALL で改行を含む `.+?` 最短一致。マーカーの前後 indent は保持する。
_BLOCK_RE = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
    flags=re.DOTALL,
)


# === Public API ===

def load_changes(top_changes_path: Path) -> list[str]:
    """top_changes.json の `changes` キー (list[str]) を返す。

    Args:
        top_changes_path: top_changes.json のパス。
    Returns:
        changes フィールドを str リストに正規化したもの。
    Raises:
        ValueError: changes が list でないとき。
    Policy:
        - public 関数はステップ列に揃え、JSON デコードと list 化を
          private helper に委ねる。
    """
    data = _decode_top_changes(top_changes_path)
    return _coerce_changes(data, top_changes_path)


def render_block(
        changes: list[str],
        max_render: int = DEFAULT_MAX_RENDER) -> str:
    """マーカー間に挿入する `<ul class="changes">` ブロックを生成する。

    Args:
        changes: load_changes の戻り値。
        max_render: 先頭何件を render するか。
    Returns:
        マーカー対 + ul ブロックを連結した文字列。
    Policy:
        - public 関数はステップ列に揃え、li 行の組み立ては
          _render_change_items に委ねる。
    """
    items = _render_change_items(changes, max_render)
    return (
        f"{START_MARKER}\n"
        f'    <ul class="changes">\n'
        f"{items}\n"
        f"    </ul>\n"
        f"    {END_MARKER}"
    )


def inject_into_index(
    index_path: Path,
    block: str,
) -> bool:
    """index.html のマーカー間を `block` で置換する。`changed?` を返す。

    Args:
        index_path: 置換対象 index.html のパス。
        block: render_block の戻り値。
    Returns:
        実際に書き換えたら True。
    Raises:
        RuntimeError: マーカー対が見つからないとき。
    Policy:
        - public 関数はステップ列に揃え、マーカー検査と置換書き戻しは
          private helper に委ねる。
    """
    text = index_path.read_text(encoding="utf-8")
    has_markers = _has_marker_pair(text)
    return _apply_marker_replacement(
        index_path, text, block, has_markers=has_markers)


def run_render(argv: list[str] | None = None) -> int:
    """CLI 入口。引数解析と render 実行と stdout 出力を束ねる。

    Args:
        argv: コマンドライン引数。None で sys.argv を使う。
    Returns:
        正常終了で 0。
    Policy:
        - public 関数はステップ列に揃え、render 実行と log 整形は
          private helper に委ねる。
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    changes = load_changes(args.top_changes)
    block = render_block(changes, max_render=args.max)
    is_changed = inject_into_index(args.index, block)
    print(_format_render_log(args, changes, is_changed=is_changed))
    return 0


# main は CLI 入口の後方互換 alias として残す。
main = run_render


# === Internal helpers (private) ===

def _decode_top_changes(top_changes_path: Path) -> dict[str, Any]:
    """top_changes.json を読み込んで dict を返す。

    Args:
        top_changes_path: top_changes.json のパス。
    Returns:
        json.loads の戻り値。
    Policy:
        - encoding は utf-8 に固定し、I/O は単発に絞る。
    """
    return json.loads(top_changes_path.read_text(encoding="utf-8"))


def _require_changes_list(
        changes: Any, top_changes_path: Path) -> list[Any]:
    """changes が list でなければ ValueError を投げる。

    Args:
        changes: data.get("changes") の戻り値。
        top_changes_path: エラーメッセージに含めるパス。
    Returns:
        list として確定した changes。
    Raises:
        ValueError: list でないとき。
    Policy:
        - 既存メッセージと互換性を保つ。
    """
    if not isinstance(changes, list):
        raise ValueError(
            f"{top_changes_path} must contain a JSON object "
            "with a 'changes' list")
    return changes


def _coerce_changes(
        data: dict[str, Any], top_changes_path: Path) -> list[str]:
    """data["changes"] を list[str] に正規化する。

    Args:
        data: _decode_top_changes の戻り値。
        top_changes_path: エラーメッセージに含めるパス。
    Returns:
        各要素を str 化した list。
    Policy:
        - 不正型は _require_changes_list で例外化する。
    """
    raw = data.get("changes", [])
    items = _require_changes_list(raw, top_changes_path)
    return [str(c) for c in items]


def _render_change_items(changes: list[str], max_render: int) -> str:
    """先頭 max_render 件を li 行として連結する。

    Args:
        changes: load_changes の戻り値。
        max_render: 出力する最大件数。
    Returns:
        改行区切りの "      <li>...</li>" 文字列。
    Policy:
        - インデントを既存出力と揃え、空 list でも空文字列を返す。
    """
    rendered = changes[:max_render]
    return "\n".join(f"      <li>{c}</li>" for c in rendered)


def _apply_marker_replacement(
        index_path: Path,
        text: str,
        block: str,
        *,
        has_markers: bool) -> bool:
    """マーカー有無を見て置換書き戻しか例外送出かを決める。

    Args:
        index_path: 書き戻し先の index.html。
        text: 既存テキスト。
        block: render_block の戻り値。
        has_markers: _has_marker_pair の結果。
    Returns:
        書き戻したら True。
    Raises:
        RuntimeError: マーカー対が見つからないとき。
    Policy:
        - inject_into_index から制御フローを引き取る。
    """
    if not has_markers:
        raise RuntimeError(
            f"{index_path} に {START_MARKER!r} / {END_MARKER!r} "
            "マーカーが見つからない"
        )
    return _replace_marker_block(index_path, text, block)


def _has_marker_pair(text: str) -> bool:
    """index.html に START / END マーカーが両方含まれるかの述語。

    Args:
        text: index.html のテキスト。
    Returns:
        両方含まれていれば True。
    Policy:
        - 部分文字列の有無のみで判定する。
    """
    if START_MARKER not in text:
        return False
    return END_MARKER in text


def _replace_marker_block(
        index_path: Path, text: str, block: str) -> bool:
    """マーカー間を block で置換し、差分があれば書き戻す。

    Args:
        index_path: 書き戻し先の index.html。
        text: 既存テキスト。
        block: 新しいマーカー対ブロック。
    Returns:
        書き戻したら True。
    Policy:
        - 差分が無い場合は I/O を起こさない。
    """
    new_text = _BLOCK_RE.sub(block, text, count=1)
    if new_text == text:
        return False
    index_path.write_text(new_text, encoding="utf-8")
    return True


def _build_arg_parser() -> argparse.ArgumentParser:
    """run_render 用の argparse を構成して返す。

    Returns:
        --max / --index / --top-changes を持つ parser。
    Policy:
        - default 値はモジュール定数に揃える。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max", type=int, default=DEFAULT_MAX_RENDER,
        help=f"先頭 N 件のみ render (default: {DEFAULT_MAX_RENDER})",
    )
    parser.add_argument(
        "--index", type=Path, default=DEFAULT_INDEX_PATH,
        help="挿入先 index.html",
    )
    parser.add_argument(
        "--top-changes", type=Path, default=DEFAULT_TOP_CHANGES_PATH,
        help="入力 top_changes.json",
    )
    return parser


def _format_render_log(
        args: argparse.Namespace,
        changes: list[str],
        *,
        is_changed: bool) -> str:
    """render 結果の stdout ログ文字列を組み立てる。

    Args:
        args: parser.parse_args の戻り値。
        changes: load_changes の戻り値。
        is_changed: inject_into_index の戻り値。
    Returns:
        既存 CLI と同じ書式の 1 行ログ。
    Policy:
        - 出力文言は既存テストと互換性を保つ。
    """
    if is_changed:
        count = min(args.max, len(changes))
        return (
            f"[render-top-changes] updated {args.index} "
            f"(top {count} entries)"
        )
    return f"[render-top-changes] no change ({args.index})"


if __name__ == "__main__":
    sys.exit(run_render())
