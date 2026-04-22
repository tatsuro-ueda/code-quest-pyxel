from __future__ import annotations

import base64
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def build_codemaker_zip_base64(*, resource_bytes: bytes = b"resource") -> str:
    payload = io.BytesIO()
    with ZipFile(payload, "w") as zf:
        zf.writestr("block-quest/main.py", "print('ignored code')\n")
        zf.writestr("block-quest/my_resource.pyxres", resource_bytes)
    return base64.b64encode(payload.getvalue()).decode("ascii")


class FakeLocalStorage:
    def __init__(self, items: dict[str, str] | None = None):
        self._items = dict(items or {})

    def getItem(self, key: str):
        return self._items.get(key)

    def setItem(self, key: str, value: str) -> None:
        self._items[key] = value


class BrowserResourceOverrideTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runtime_root = Path(self.tmp.name) / "runtime"
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        try:
            from src.shared.services.browser_resource_override import (
                BROWSER_IMPORT_META_KEY,
                BROWSER_IMPORT_ZIP_KEY,
                stage_browser_imported_resource,
            )
        except ImportError as exc:  # pragma: no cover - TDD red path
            raise AssertionError(f"browser resource override service is missing: {exc}") from exc

        self.BROWSER_IMPORT_META_KEY = BROWSER_IMPORT_META_KEY
        self.BROWSER_IMPORT_ZIP_KEY = BROWSER_IMPORT_ZIP_KEY
        self.stage_browser_imported_resource = stage_browser_imported_resource

    def tearDown(self):
        self.tmp.cleanup()

    def make_js_module(
        self,
        *,
        zip_payload: str | None = None,
        source_name: str = "code-maker.zip",
    ) -> SimpleNamespace:
        items: dict[str, str] = {}
        if zip_payload is not None:
            items[self.BROWSER_IMPORT_ZIP_KEY] = zip_payload
            items[self.BROWSER_IMPORT_META_KEY] = json.dumps(
                {
                    "source_name": source_name,
                    "stored_at": "2026-04-20T08:09:00+00:00",
                },
                ensure_ascii=False,
            )
        return SimpleNamespace(
            localStorage=FakeLocalStorage(items),
            window=SimpleNamespace(location=SimpleNamespace(pathname="/production/pyxel.html")),
        )

    def test_stages_browser_uploaded_resource_from_local_storage(self):
        js_module = self.make_js_module(
            zip_payload=build_codemaker_zip_base64(resource_bytes=b"edited-resource"),
        )

        staged_path = self.stage_browser_imported_resource(self.runtime_root, js_module=js_module)

        self.assertEqual(staged_path, self.runtime_root / "my_resource.pyxres")
        self.assertEqual(staged_path.read_bytes(), b"edited-resource")

    def test_returns_none_without_browser_zip_payload(self):
        js_module = self.make_js_module(zip_payload=None)

        staged_path = self.stage_browser_imported_resource(self.runtime_root, js_module=js_module)

        self.assertIsNone(staged_path)
        self.assertFalse((self.runtime_root / "my_resource.pyxres").exists())

    def test_ignores_invalid_browser_zip_payload(self):
        js_module = self.make_js_module(zip_payload="not-valid-base64")

        staged_path = self.stage_browser_imported_resource(self.runtime_root, js_module=js_module)

        self.assertIsNone(staged_path)
        self.assertFalse((self.runtime_root / "my_resource.pyxres").exists())


if __name__ == "__main__":
    unittest.main()
