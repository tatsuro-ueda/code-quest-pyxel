from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def build_codemaker_zip_bytes(*, main_text: str = "print('ignored')\n", resource_bytes: bytes = b"resource") -> bytes:
    payload = io.BytesIO()
    with ZipFile(payload, "w") as zf:
        zf.writestr("block-quest/main.py", main_text)
        zf.writestr("block-quest/my_resource.pyxres", resource_bytes)
    return payload.getvalue()


class CodeMakerResourceStoreTest(unittest.TestCase):
    """P3-E: staging 廃止後は apply_imported_resource が assets/blockquest.pyxres を直接上書きする。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project_root = Path(self.tmp.name) / "project"
        (self.project_root / "assets").mkdir(parents=True, exist_ok=True)
        (self.project_root / "assets" / "blockquest.pyxres").write_bytes(b"base-resource")
        from src.shared.services.codemaker_resource_store import apply_imported_resource

        self.apply_imported_resource = apply_imported_resource

    def tearDown(self):
        self.tmp.cleanup()

    def test_apply_imported_resource_overwrites_canonical_pyxres(self):
        result = self.apply_imported_resource(
            self.project_root,
            build_codemaker_zip_bytes(resource_bytes=b"edited-resource"),
            source_name="code-maker.zip",
        )

        canonical = self.project_root / "assets" / "blockquest.pyxres"
        self.assertEqual(canonical.read_bytes(), b"edited-resource")
        self.assertEqual(result["resource_path"], str(canonical))
        self.assertEqual(result["ignored_code_entries"], ["block-quest/main.py"])
        self.assertEqual(result["source_name"], "code-maker.zip")

    def test_rejects_zip_without_resource_entry(self):
        payload = io.BytesIO()
        with ZipFile(payload, "w") as zf:
            zf.writestr("block-quest/main.py", "print('missing resource')\n")

        with self.assertRaises(ValueError):
            self.apply_imported_resource(
                self.project_root,
                payload.getvalue(),
                source_name="code-maker.zip",
            )


if __name__ == "__main__":
    unittest.main()
