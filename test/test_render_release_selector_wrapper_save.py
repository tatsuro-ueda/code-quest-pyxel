from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.render_release_selector import generate_wrapper


ROOT = Path(__file__).resolve().parent.parent


class WrapperSaveFlowRenderTest(unittest.TestCase):
    def test_generate_wrapper_includes_save_flow_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = generate_wrapper(Path(tmpdir), ROOT, "pyxel.html")
            html = output_path.read_text(encoding="utf-8")

        self.assertIn('id="save-image-btn"', html)
        self.assertIn('id="save-status"', html)
        self.assertIn("showSaveFilePicker", html)
        self.assertIn("suggestedName", html)
        self.assertIn("startIn: 'downloads'", html)
        self.assertIn("Downloads をみてね", html)


if __name__ == "__main__":
    unittest.main()
