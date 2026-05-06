"""top_changes.json → index.html マーカー間 inject の純粋 render。

post-commit hook (`tools/update_top_changes.py`) と手動運用の両方から呼ぶ。
外部 API への依存はなく、ファイル I/O と文字列置換のみ。

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


def load_changes(top_changes_path: Path) -> list[str]:
    """top_changes.json の `changes` キー (list[str]) を返す。"""
    data = json.loads(top_changes_path.read_text(encoding="utf-8"))
    changes = data.get("changes", [])
    if not isinstance(changes, list):
        raise ValueError(
            f"{top_changes_path} must contain a JSON object with a 'changes' list"
        )
    return [str(c) for c in changes]


def render_block(changes: list[str], max_render: int = DEFAULT_MAX_RENDER) -> str:
    """マーカー間に挿入する `<ul class="changes">` ブロックを生成する。"""
    rendered = changes[:max_render]
    items = "\n".join(f"      <li>{c}</li>" for c in rendered)
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
    """index.html のマーカー間を `block` で置換する。`changed?` を返す。"""
    text = index_path.read_text(encoding="utf-8")
    if START_MARKER not in text or END_MARKER not in text:
        raise RuntimeError(
            f"{index_path} に {START_MARKER!r} / {END_MARKER!r} マーカーが見つからない"
        )
    new_text = _BLOCK_RE.sub(block, text, count=1)
    if new_text == text:
        return False
    index_path.write_text(new_text, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
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
    args = parser.parse_args(argv)

    changes = load_changes(args.top_changes)
    block = render_block(changes, max_render=args.max)
    changed = inject_into_index(args.index, block)
    if changed:
        print(f"[render-top-changes] updated {args.index} (top {min(args.max, len(changes))} entries)")
    else:
        print(f"[render-top-changes] no change ({args.index})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
