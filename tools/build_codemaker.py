#!/usr/bin/env python3
"""G12: Code Maker 用 zip ビルド.

main.py + blockquest.pyxres を production/code-maker.zip にパッケージする。
pyxres は Code Maker 互換の my_resource.pyxres にリネームして同梱。

生成される main.py は Code Maker 教材版としてラップされ、
編集可能領域とコア自己検査を含む。

使い方:
    python tools/build_codemaker.py
"""
import hashlib
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "production" / "code-maker.zip"
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
    marker_index = source_text.rfind(ENTRY_POINT_MARKER)
    if marker_index == -1:
        raise ValueError("ENTRY POINT が見つかりません")
    core_source = source_text[:marker_index].rstrip() + "\n"
    entrypoint_source = source_text[marker_index:].lstrip("\n")
    return core_source, entrypoint_source


def build_codemaker_main_text(source_text: str) -> str:
    core_source, entrypoint_source = _split_core_and_entrypoint(source_text)
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


def build_codemaker_zip(main_py: Path, *, pyxres: Path, output: Path) -> Path:
    main_py = Path(main_py)
    pyxres = Path(pyxres)
    output = Path(output)

    if not main_py.exists():
        raise FileNotFoundError(f"{main_py} が見つかりません")
    if not pyxres.exists():
        raise FileNotFoundError(f"{pyxres} が見つかりません")

    source_text = main_py.read_text(encoding="utf-8")
    generated_main = build_codemaker_main_text(source_text)
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w") as zf:
        zf.writestr(f"{BUNDLE_DIR}/main.py", generated_main)
        zf.write(pyxres, f"{BUNDLE_DIR}/my_resource.pyxres")
    return output


def main():
    main_py = ROOT / "main.py"
    pyxres = ROOT / "assets" / "blockquest.pyxres"

    try:
        build_codemaker_zip(main_py, pyxres=pyxres, output=OUTPUT)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"OK: {OUTPUT} を生成しました")
    print(f"    main.py: {main_py.stat().st_size} bytes")
    print(f"    my_resource.pyxres: {pyxres.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
