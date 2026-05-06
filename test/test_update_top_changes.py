"""tools/update_top_changes.py の振る舞いテスト（Anthropic API は mock）。

post-commit hook が次の 4 ケースを正しく扱うことを保証：
  1. AUTO_MARKER のある commit → 即 exit 0、無変更（再帰防止）
  2. ANTHROPIC_API_KEY 不在 → silent skip、無変更
  3. Claude が「関係なし」 → 無変更
  4. Claude が「関係あり」 → top_changes.json の先頭に prepend
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import update_top_changes as utc  # noqa: E402


class UpdateTopChangesTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path("/tmp/utc_test")
        self.tmpdir.mkdir(exist_ok=True)
        self.json_path = self.tmpdir / "top_changes.json"
        self.json_path.write_text(
            json.dumps({"changes": ["existing"]}, ensure_ascii=False),
            encoding="utf-8",
        )
        self._orig_top = utc.TOP_CHANGES_PATH
        utc.TOP_CHANGES_PATH = self.json_path

    def tearDown(self):
        utc.TOP_CHANGES_PATH = self._orig_top

    def _read_changes(self) -> list[str]:
        return json.loads(self.json_path.read_text(encoding="utf-8"))["changes"]

    def test_auto_marker_short_circuits(self):
        """AUTO_MARKER のある commit に対しては何もしない。"""
        with mock.patch.object(utc, "_git", side_effect=["subject body", utc.AUTO_MARKER]):
            with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake"}, clear=False):
                with mock.patch.object(utc, "call_claude") as claude:
                    rc = utc.main([])
        self.assertEqual(rc, 0)
        claude.assert_not_called()
        self.assertEqual(self._read_changes(), ["existing"])

    def test_missing_api_key_silently_skips(self):
        """ANTHROPIC_API_KEY 不在で silent skip、changes 無変更。"""
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(utc, "_git", side_effect=["feat: x", "body"]):
                with mock.patch.object(utc, "call_claude") as claude:
                    rc = utc.main([])
        self.assertEqual(rc, 0)
        claude.assert_not_called()
        self.assertEqual(self._read_changes(), ["existing"])

    def test_claude_says_not_relevant_no_change(self):
        """Claude が `include: false` を返したら無変更。"""
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake"}, clear=False):
            with mock.patch.object(utc, "_git", side_effect=["refactor: x", "internal"]):
                with mock.patch.object(utc, "call_claude", return_value={"include": False}):
                    rc = utc.main([])
        self.assertEqual(rc, 0)
        self.assertEqual(self._read_changes(), ["existing"])

    def test_claude_says_relevant_prepends_and_amends(self):
        """Claude が `include: true, line: ...` を返したら prepend → render → amend。"""
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake"}, clear=False):
            with mock.patch.object(utc, "_git", side_effect=["feat: ぶき", "body"]):
                with mock.patch.object(
                    utc, "call_claude",
                    return_value={"include": True, "line": "5/6: あたらしい でき事"},
                ):
                    with mock.patch.object(utc, "render_index") as render:
                        with mock.patch.object(utc, "amend_with_marker") as amend:
                            rc = utc.main([])
        self.assertEqual(rc, 0)
        render.assert_called_once()
        amend.assert_called_once()
        changes = self._read_changes()
        self.assertEqual(changes[0], "5/6: あたらしい でき事")
        self.assertIn("existing", changes)

    def test_dry_run_prints_prompt_only(self):
        """`--dry-run` は prompt を表示するだけで API 呼ばず、changes 無変更。"""
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake"}, clear=False):
            with mock.patch.object(utc, "_git", side_effect=["feat: x", "body"]):
                with mock.patch.object(utc, "call_claude") as claude:
                    rc = utc.main(["--dry-run"])
        self.assertEqual(rc, 0)
        claude.assert_not_called()
        self.assertEqual(self._read_changes(), ["existing"])

    def test_prepend_change_no_duplicate_top(self):
        """同じ行を 2 回 prepend しても先頭重複しない。"""
        utc.prepend_change("line A")
        utc.prepend_change("line A")  # 連続重複
        changes = self._read_changes()
        self.assertEqual(changes[0], "line A")
        # 重複していないこと
        self.assertEqual(changes.count("line A"), 1)


if __name__ == "__main__":
    unittest.main()
