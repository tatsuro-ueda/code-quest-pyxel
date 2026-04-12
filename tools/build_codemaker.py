#!/usr/bin/env python3
"""G12: Code Maker 用 zip ビルド

main.py + blockquest.pyxres を code-maker.zip にパッケージする。
pyxres は Code Maker 互換の my_resource.pyxres にリネー���して同梱。

使い方:
    python tools/build_codemaker.py
"""
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "code-maker.zip"
BUNDLE_DIR = "block-quest"


def main():
    main_py = ROOT / "main.py"
    pyxres = ROOT / "assets" / "blockquest.pyxres"

    if not main_py.exists():
        print(f"ERROR: {main_py} が見つかりません")
        return 1
    if not pyxres.exists():
        print(f"ERROR: {pyxres} が見つかりません")
        return 1

    with ZipFile(OUTPUT, "w") as zf:
        zf.write(main_py, f"{BUNDLE_DIR}/main.py")
        zf.write(pyxres, f"{BUNDLE_DIR}/my_resource.pyxres")

    print(f"OK: {OUTPUT} を生成しました")
    print(f"    main.py: {main_py.stat().st_size} bytes")
    print(f"    my_resource.pyxres: {pyxres.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
