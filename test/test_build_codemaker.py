from __future__ import annotations

import re
import shutil
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_codemaker import build_codemaker_zip  # noqa: E402


ENTRY_POINT = """# =====================================================================
# ENTRY POINT
# =====================================================================
game = Game()
game.start()
"""

SAMPLE_MAIN = f"""import pyxel


def say(message):
    return message


class Game:
    def __init__(self):
        self.started = False

    def start(self):
        self.started = True


{ENTRY_POINT}
"""


class _FakePyxel:
    def __init__(self):
        self.init_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.run_calls = 0

    def init(self, *args, **kwargs):
        self.init_calls.append((args, kwargs))

    def run(self, update, draw):
        self.run_calls += 1
        self.update = update
        self.draw = draw

    def cls(self, *args, **kwargs):
        return None

    def text(self, *args, **kwargs):
        return None


class BuildCodeMakerZipTest(unittest.TestCase):
    def setUp(self):
        self.work_dir = ROOT / ".build" / "test_build_codemaker"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.main_path = self.work_dir / "main.py"
        self.main_path.write_text(SAMPLE_MAIN, encoding="utf-8")
        self.pyxres_path = self.work_dir / "resource.pyxres"
        self.pyxres_path.write_bytes(b"pyxres")
        self.output_path = self.work_dir / "code-maker.zip"

    def tearDown(self):
        shutil.rmtree(self.work_dir, ignore_errors=True)

    def _read_generated_main(self) -> str:
        build_codemaker_zip(self.main_path, pyxres=self.pyxres_path, output=self.output_path)
        with zipfile.ZipFile(self.output_path) as zf:
            return zf.read("block-quest/main.py").decode("utf-8")

    def test_build_codemaker_zip_wraps_generated_main_with_student_area_and_guard(self):
        generated = self._read_generated_main()

        self.assertIn("# BEGIN STUDENT AREA", generated)
        self.assertIn("# END STUDENT AREA", generated)
        self.assertIn('CORE_HASH = "', generated)
        self.assertIn("verify_core()", generated)
        self.assertIn("リソースファイル", generated)
        self.assertIn("game = Game()", generated)

    def test_generated_main_shows_guard_message_and_stops_on_core_hash_mismatch(self):
        generated = self._read_generated_main()
        self.assertIn('CORE_HASH = "', generated)
        tampered = re.sub(r'CORE_HASH = "[^"]+"', 'CORE_HASH = "broken"', generated, count=1)

        fake_pyxel = _FakePyxel()
        original_pyxel = sys.modules.get("pyxel")
        sys.modules["pyxel"] = fake_pyxel
        try:
            with self.assertRaises(SystemExit):
                exec(tampered, {"__name__": "__main__"})
        finally:
            if original_pyxel is None:
                del sys.modules["pyxel"]
            else:
                sys.modules["pyxel"] = original_pyxel

        self.assertEqual(fake_pyxel.run_calls, 1)
        self.assertTrue(fake_pyxel.init_calls)

    def test_generated_main_allows_student_area_edits_without_triggering_guard(self):
        generated = self._read_generated_main()
        edited = generated.replace(
            '# say("こんにちは")',
            'STUDENT_VALUE = say("こんにちは")',
            1,
        )

        fake_pyxel = _FakePyxel()
        original_pyxel = sys.modules.get("pyxel")
        sys.modules["pyxel"] = fake_pyxel
        namespace = {"__name__": "__main__"}
        try:
            exec(edited, namespace)
        finally:
            if original_pyxel is None:
                del sys.modules["pyxel"]
            else:
                sys.modules["pyxel"] = original_pyxel

        self.assertEqual(namespace["STUDENT_VALUE"], "こんにちは")
        self.assertTrue(namespace["game"].started)
        self.assertEqual(fake_pyxel.run_calls, 0)

if __name__ == "__main__":
    unittest.main()
