from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# P3-E: browser_resource_override 削除済み。localStorage key はテスト内で使わない。
# storedZip / storedMeta は常に False になる（fallback 削除後）。
_LEGACY_ZIP_KEY = "blockquest_codemaker_zip_v1"
_LEGACY_META_KEY = "blockquest_codemaker_zip_meta_v1"


def render_import_script() -> str:
    # codemaker_import_ui.js は P3-C で placeholder を削除済み
    return (ROOT / "templates" / "codemaker_import_ui.js").read_text(encoding="utf-8")


def build_node_harness(*, server_ok: bool) -> str:
    import_script = render_import_script()
    upload_block = ""
    if server_ok:
        upload_block = textwrap.dedent(
            """
            if (url === "/internal/codemaker-resource-import") {
              return new Response(
                JSON.stringify({
                  development_available: true,
                  development_play_url: "/development/play.html"
                }),
                {
                  status: 200,
                  headers: { "Content-Type": "application/json" }
                }
              );
            }
            """
        )

    return textwrap.dedent(
        f"""
        const storage = new Map();
        const fetchCalls = [];
        const uploadFile = {{
          name: "code-maker.zip",
          async arrayBuffer() {{
            return Uint8Array.from([1, 2, 3, 4]).buffer;
          }},
        }};

        function makeElement(id) {{
          return {{
            id,
            textContent: "",
            disabled: false,
            files: [],
            _listeners: new Map(),
            addEventListener(type, handler) {{
              this._listeners.set(type, handler);
            }},
            dispatch(type, event) {{
              const handler = this._listeners.get(type);
              if (!handler) {{
                return undefined;
              }}
              return handler(event);
            }},
          }};
        }}

        const importInput = makeElement("codemaker-import-input");
        importInput.files = [uploadFile];
        const importButton = makeElement("codemaker-import-button");
        const importStatus = makeElement("codemaker-import-status");
        const elements = {{
          "codemaker-import-input": importInput,
          "codemaker-import-button": importButton,
          "codemaker-import-status": importStatus,
          "codemaker-download-link": null,
        }};

        globalThis.document = {{
          getElementById(id) {{
            return elements[id] || null;
          }},
        }};

        globalThis.fetch = async function (url, options = {{}}) {{
          fetchCalls.push({{
            url: String(url),
            method: options.method || "GET",
            hasBody: Boolean(options.body),
            headers: Object.assign({{}}, options.headers || {{}}),
          }});
          {upload_block}
          throw new Error("server unavailable");
        }};

        const windowObject = {{
          localStorage: {{
            getItem(key) {{
              return storage.has(key) ? storage.get(key) : null;
            }},
            setItem(key, value) {{
              storage.set(key, String(value));
            }},
            removeItem(key) {{
              storage.delete(key);
            }},
          }},
          location: {{
            protocol: "https:",
            hostname: "example.com",
            pathname: "/index.html",
          }},
          btoa(value) {{
            return Buffer.from(value, "binary").toString("base64");
          }},
          atob(value) {{
            return Buffer.from(value, "base64").toString("binary");
          }},
        }};
        windowObject.window = windowObject;
        globalThis.window = windowObject;
        globalThis.Response = Response;

        {import_script}

        await importButton.dispatch("click", {{}});

        console.log(JSON.stringify({{
          fetchCalls,
          status: importStatus.textContent,
          storedZip: storage.has("{_LEGACY_ZIP_KEY}"),
          storedMeta: storage.has("{_LEGACY_META_KEY}"),
        }}));
        """
    )


def run_node_harness(*, server_ok: bool) -> dict[str, object]:
    script = build_node_harness(server_ok=server_ok)
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        completed = subprocess.run(
            ["node", str(script_path)],
            capture_output=True,
            check=False,
            text=True,
        )
    finally:
        script_path.unlink(missing_ok=True)

    if completed.returncode != 0:
        raise AssertionError(
            "Node harness failed:\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


class CodeMakerImportUiServerImportTest(unittest.TestCase):
    def test_import_button_prefers_server_side_import_when_available(self):
        result = run_node_harness(server_ok=True)

        self.assertEqual(
            result["fetchCalls"],
            [
                {
                    "url": "/internal/codemaker-resource-import",
                    "method": "POST",
                    "hasBody": True,
                    "headers": {
                        "Content-Type": "application/zip",
                        "X-Filename": "code-maker.zip",
                    },
                }
            ],
        )
        self.assertFalse(result["storedZip"])
        self.assertFalse(result["storedMeta"])
        self.assertIn("server", result["status"])

    def test_import_button_shows_error_when_server_is_unavailable(self):
        # P3-C: localStorage fallback を削除。server エラー時はメッセージ表示のみ
        result = run_node_harness(server_ok=False)

        self.assertEqual(
            result["fetchCalls"],
            [
                {
                    "url": "/internal/codemaker-resource-import",
                    "method": "POST",
                    "hasBody": True,
                    "headers": {
                        "Content-Type": "application/zip",
                        "X-Filename": "code-maker.zip",
                    },
                }
            ],
        )
        self.assertFalse(result["storedZip"])
        self.assertFalse(result["storedMeta"])
        self.assertIn("しばらくたってから", result["status"])


if __name__ == "__main__":
    unittest.main()
