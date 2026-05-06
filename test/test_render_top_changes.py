"""tools/render_top_changes.py の振る舞いテスト。

純粋 render を CC が安心して再実行できるよう、以下 3 ケースを担保：
  1. マーカー間が新しい block で置換される
  2. マーカー外（CSS / svg / 隣接 section）は無傷
  3. `--max N` で先頭 N 件のみ render（残りは捨てられる）
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.render_top_changes import (  # noqa: E402
    END_MARKER,
    START_MARKER,
    inject_into_index,
    load_changes,
    render_block,
)


class RenderTopChangesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path("/tmp/render_top_changes_test")
        self.tmp.mkdir(exist_ok=True)
        self.index = self.tmp / "index.html"
        self.json_path = self.tmp / "top_changes.json"

    def _write_index(self, body: str) -> None:
        self.index.write_text(body, encoding="utf-8")

    def _write_changes(self, changes: list[str]) -> None:
        self.json_path.write_text(
            json.dumps({"changes": changes}, ensure_ascii=False),
            encoding="utf-8",
        )

    def test_marker_block_is_replaced(self):
        """マーカー間が新しい block で置換される。"""
        self._write_index(
            "header\n"
            f"  {START_MARKER}\n"
            "  <ul><li>old</li></ul>\n"
            f"  {END_MARKER}\n"
            "footer\n"
        )
        block = render_block(["5/6: あたらしい でき事"], max_render=5)
        changed = inject_into_index(self.index, block)
        self.assertTrue(changed)
        text = self.index.read_text(encoding="utf-8")
        self.assertIn("5/6: あたらしい でき事", text)
        self.assertNotIn("<li>old</li>", text)

    def test_outside_markers_is_preserved(self):
        """マーカー外（CSS や section 枠）は無傷。"""
        outer = (
            "<head><style>.x{color:red}</style></head>\n"
            "<body>\n"
            "<svg><rect/></svg>\n"
            f"{START_MARKER}\n"
            "<ul><li>old</li></ul>\n"
            f"{END_MARKER}\n"
            "<section>next-card</section>\n"
            "</body>\n"
        )
        self._write_index(outer)
        block = render_block(["x"], max_render=5)
        inject_into_index(self.index, block)
        text = self.index.read_text(encoding="utf-8")
        self.assertIn(".x{color:red}", text)
        self.assertIn("<svg><rect/></svg>", text)
        self.assertIn("<section>next-card</section>", text)

    def test_max_render_truncates_to_top_n(self):
        """`--max N` で先頭 N 件のみ render。"""
        block = render_block(
            [f"line-{i}" for i in range(10)],
            max_render=3,
        )
        # block には先頭 3 件だけ
        self.assertIn("line-0", block)
        self.assertIn("line-1", block)
        self.assertIn("line-2", block)
        self.assertNotIn("line-3", block)
        self.assertNotIn("line-9", block)

    def test_load_changes_reads_changes_list(self):
        """top_changes.json から changes list を読み込む。"""
        self._write_changes(["a", "b", "c"])
        result = load_changes(self.json_path)
        self.assertEqual(result, ["a", "b", "c"])

    def test_inject_raises_when_marker_missing(self):
        """マーカーが無い index には inject しない（即 fail）。"""
        self._write_index("<html>no marker</html>")
        with self.assertRaises(RuntimeError):
            inject_into_index(self.index, render_block(["x"]))


if __name__ == "__main__":
    unittest.main()
