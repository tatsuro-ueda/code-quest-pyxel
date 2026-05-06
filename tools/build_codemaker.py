#!/usr/bin/env python3
"""G12 / Phase 2: Code Maker 用 zip ビルド.

codemaker_bundler.py が `codemaker_manifest.txt` 通りに全 .py を連結した
source text を生成し、本モジュールはそれを CORE_BLOCK にラップして
`dist/code-maker.zip` に main.py + my_resource.pyxres として梱包する。

生成される main.py は Code Maker 教材版としてラップされ、
STUDENT AREA（編集可能領域）とコア自己検査（CORE_HASH）を含む。

使い方:
    python tools/build_codemaker.py
"""
import hashlib
import sys
from pathlib import Path
from zipfile import ZipFile

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from codemaker_bundler import build_bundled_source

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist" / "code-maker.zip"
BUNDLE_DIR = "block-quest"
ENTRY_POINT_MARKER = """# =====================================================================
# ENTRY POINT
# =====================================================================
"""
STUDENT_AREA_BLOCK = """# BEGIN STUDENT AREA
# ここだけ かいてよい
# たとえば:
# say("こんにちは")
# リソースファイルは リソースエディタで へんしゅうします
# END STUDENT AREA
"""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _split_core_and_entrypoint(source_text: str) -> tuple[str, str]:
    """ENTRY POINT marker で core と entry に分割する。"""
    marker_index = source_text.rfind(ENTRY_POINT_MARKER)
    if marker_index == -1:
        raise ValueError("ENTRY POINT が見つかりません")
    core_source = source_text[:marker_index].rstrip() + "\n"
    entrypoint_source = source_text[marker_index:].lstrip("\n")
    return core_source, entrypoint_source


def _normalize_entrypoint_source(entrypoint_source: str) -> str:
    """entry の末尾に `game = run()` を足す（bundler 生成では含まれない）。"""
    normalized = entrypoint_source.rstrip() + "\n"
    if "def run(" in normalized and not normalized.rstrip().endswith("run()"):
        normalized += "\ngame = run()\n"
    return normalized


def build_codemaker_main_text(source_text: str | None = None) -> str:
    """bundler から source text を受け取り、Code Maker 用 main.py を生成する。

    `source_text` は P2 以降は無視される（bundler が常に manifest から
    生成するため）。呼出し互換のため引数は残している。
    """
    del source_text  # P2 以降 unused（引数は互換のため残している）
    source_text = build_bundled_source()
    core_source, entrypoint_source = _split_core_and_entrypoint(source_text)
    entrypoint_source = _normalize_entrypoint_source(entrypoint_source)
    core_hash = _sha256_text(core_source)
    return (
        "# Auto-generated Code Maker classroom bundle.\n"
        "import hashlib\n"
        "import pyxel\n\n"
        f"CORE_BLOCK = {core_source!r}\n"
        f'CORE_HASH = "{core_hash}"\n\n'
        "def _sha256_text(text):\n"
        '    return hashlib.sha256(text.encode("utf-8")).hexdigest()\n\n'
        "def _show_core_guard_message():\n"
        '    pyxel.init(256, 240, title="Block Quest")\n'
        "    def update():\n"
        "        pass\n\n"
        "    def draw():\n"
        "        pyxel.cls(0)\n"
        '        pyxel.text(24, 72, "コアを へんこうしています", 8)\n'
        '        pyxel.text(24, 92, "STUDENT AREA だけを", 7)\n'
        '        pyxel.text(24, 108, "へんしゅうしてください", 7)\n'
        '        pyxel.text(24, 140, "リソースファイルは", 6)\n'
        '        pyxel.text(24, 156, "リソースエディタで", 6)\n'
        '        pyxel.text(24, 172, "あつかいます", 6)\n\n'
        "    pyxel.run(update, draw)\n\n"
        "def verify_core():\n"
        "    if _sha256_text(CORE_BLOCK) != CORE_HASH:\n"
        "        _show_core_guard_message()\n"
        '        raise SystemExit("core block modified")\n\n'
        "verify_core()\n"
        "exec(CORE_BLOCK, globals())\n\n"
        f"{STUDENT_AREA_BLOCK}\n"
        f"{entrypoint_source}"
    )


def build_codemaker_zip(main_py: Path | None = None, *, pyxres: Path, output: Path) -> Path:
    """bundler から main.py を生成し、pyxres と一緒に zip にする。

    `main_py` は Phase 2 からは無視する（bundler は常に `codemaker_manifest.txt`
    に従って全 src を連結するため）。呼出し互換のため引数は残している。
    """
    del main_py  # Phase 2 以降 unused
    pyxres = Path(pyxres)
    output = Path(output)

    if not pyxres.exists():
        raise FileNotFoundError(f"{pyxres} が見つかりません")

    generated_main = build_codemaker_main_text()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w") as zf:
        zf.writestr(f"{BUNDLE_DIR}/main.py", generated_main)
        zf.write(pyxres, f"{BUNDLE_DIR}/my_resource.pyxres")
    return output


def main():
    pyxres = ROOT / "assets" / "blockquest.pyxres"

    try:
        build_codemaker_zip(pyxres=pyxres, output=OUTPUT)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"OK: {OUTPUT} を生成しました")
    main_bytes = (OUTPUT.stat().st_size)
    print(f"    zip: {main_bytes} bytes")
    print(f"    my_resource.pyxres: {pyxres.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
