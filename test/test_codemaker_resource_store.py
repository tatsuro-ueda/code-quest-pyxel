from __future__ import annotations

import io
import json
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
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project_root = Path(self.tmp.name) / "project"
        (self.project_root / "assets").mkdir(parents=True, exist_ok=True)
        (self.project_root / "assets" / "blockquest.pyxres").write_bytes(b"base-resource")
        try:
            from src.shared.services.codemaker_resource_store import (
                clear_imported_resource,
                get_imported_resource_path,
                import_codemaker_resource_zip,
                load_imported_resource_manifest,
            )
        except ImportError as exc:  # pragma: no cover - TDD red path
            raise AssertionError(f"codemaker resource store module is missing: {exc}") from exc

        self.clear_imported_resource = clear_imported_resource
        self.get_imported_resource_path = get_imported_resource_path
        self.import_codemaker_resource_zip = import_codemaker_resource_zip
        self.load_imported_resource_manifest = load_imported_resource_manifest

    def tearDown(self):
        self.tmp.cleanup()

    def test_imports_only_resource_and_records_ignored_code(self):
        result = self.import_codemaker_resource_zip(
            self.project_root,
            build_codemaker_zip_bytes(resource_bytes=b"edited-resource"),
            source_name="code-maker.zip",
        )

        imported_path = self.get_imported_resource_path(self.project_root)
        manifest = self.load_imported_resource_manifest(self.project_root)

        self.assertIsNotNone(imported_path)
        self.assertEqual(imported_path.read_bytes(), b"edited-resource")
        self.assertEqual(result["resource_path"], str(imported_path))
        self.assertEqual(result["ignored_code_entries"], ["block-quest/main.py"])
        self.assertTrue(result["changed_from_base"])
        self.assertIsInstance(manifest, dict)
        self.assertEqual(manifest["source_name"], "code-maker.zip")
        self.assertEqual(manifest["ignored_code_entries"], ["block-quest/main.py"])
        self.assertTrue(manifest["changed_from_base"])

    def test_rejects_zip_without_resource_entry(self):
        payload = io.BytesIO()
        with ZipFile(payload, "w") as zf:
            zf.writestr("block-quest/main.py", "print('missing resource')\n")

        with self.assertRaises(ValueError):
            self.import_codemaker_resource_zip(
                self.project_root,
                payload.getvalue(),
                source_name="code-maker.zip",
            )

    def test_clear_imported_resource_removes_blob_and_manifest(self):
        self.import_codemaker_resource_zip(
            self.project_root,
            build_codemaker_zip_bytes(resource_bytes=b"edited-resource"),
            source_name="code-maker.zip",
        )

        self.clear_imported_resource(self.project_root)

        self.assertIsNone(self.get_imported_resource_path(self.project_root))
        self.assertIsNone(self.load_imported_resource_manifest(self.project_root))


if __name__ == "__main__":
    unittest.main()
