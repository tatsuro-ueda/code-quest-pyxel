"""PWA アイコン（icons/*.png）を HERO_DOWN スプライトから生成する。

このファイルに含まれる関数:

- build_pwa_icons: icons/ 配下の 192 / 512 / maskable-512 PNG を書き出す
- run_main: 引数なし CLI 入口（`python tools/gen_pwa_icons.py`）

Problems:
    - ホーム画面アイコンだけのために、由来の分からない PNG を repo へ置くと、
      色やスプライトを変えたときに誰も追随できない。

Solutions:
    - 正本は `src/shared/constants/sprite_data.HERO_DOWN`（16x16）と
      `index.html` の配色（--bg-deep）。ここから nearest-neighbor で焼き直す。
    - 外部ライブラリを足さない。PNG は標準 library の zlib + struct で書く。
"""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.shared.constants.sprite_data import HERO_DOWN  # noqa: E402

# === Public API ===

# index.html の :root --bg-deep と揃える。
BACKGROUND_RGB = (0x1A, 0x14, 0x66)
# Pyxel 既定パレット（sprite_data の色番号はこれを指す）。
PYXEL_PALETTE = (
    (0x00, 0x00, 0x00), (0x2B, 0x33, 0x5F), (0x7E, 0x20, 0x72),
    (0x19, 0x95, 0x9C), (0x8B, 0x48, 0x52), (0x39, 0x5C, 0x98),
    (0xA9, 0xC1, 0xFF), (0xEE, 0xEE, 0xEE), (0xD4, 0x18, 0x6C),
    (0xD3, 0x84, 0x41), (0xE9, 0xC3, 0x5B), (0x70, 0xC6, 0xA9),
    (0x76, 0x96, 0xDE), (0xA3, 0xA3, 0xA3), (0xFF, 0x97, 0x98),
    (0xED, 0xC7, 0xB0),
)
TRANSPARENT_INDEX = 0
# (出力ファイル名, 一辺px, スプライトが占める割合)
ICON_SPECS = (
    ("icon-192.png", 192, 0.80),
    ("icon-512.png", 512, 0.80),
    ("icon-maskable-512.png", 512, 0.56),
)


def build_pwa_icons(output_dir: Path) -> list[Path]:
    """ICON_SPECS の PNG を output_dir へ書き出す。

    Args:
        output_dir: `icons/` ディレクトリ（無ければ作成）。

    Returns:
        書き出した PNG の Path 一覧。

    Policy:
        - スプライトの描画とファイル書き出しを private helper へ委譲する。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, size, sprite_ratio in ICON_SPECS:
        pixels = _render_icon_pixels(size, sprite_ratio)
        path = output_dir / name
        path.write_bytes(_encode_png(pixels, size, size))
        written.append(path)
    return written


def run_main() -> None:
    """`python tools/gen_pwa_icons.py` の入口。

    Policy:
        - repo root の icons/ へ書き、生成したパスを表示するだけ。
    """
    for path in build_pwa_icons(ROOT / "icons"):
        print(f"[gen_pwa_icons] wrote {path.relative_to(ROOT)}")


# === Internal helpers (private) ===


def _render_icon_pixels(size: int, sprite_ratio: float) -> list[list[tuple[int, int, int]]]:
    """背景色で塗った正方形の中央に HERO_DOWN を拡大配置する。

    Args:
        size: 出力する一辺の px。
        sprite_ratio: 一辺に対してスプライトが占める割合。

    Returns:
        size 行 x size 列の RGB tuple 配列。

    Policy:
        - 拡大は nearest-neighbor（scale は整数）。ドット絵をぼかさない。
    """
    sprite = _crop_to_drawn_area(HERO_DOWN)
    canvas = [[BACKGROUND_RGB] * size for _ in range(size)]
    longest_side = max(len(sprite), len(sprite[0]))
    scale = max(1, int(size * sprite_ratio) // longest_side)
    left_offset = (size - scale * len(sprite[0])) // 2
    top_offset = (size - scale * len(sprite)) // 2
    for row_index, row in enumerate(sprite):
        for col_index, color_index in enumerate(row):
            if color_index == TRANSPARENT_INDEX:
                continue
            rgb = PYXEL_PALETTE[color_index % len(PYXEL_PALETTE)]
            _fill_block(canvas, left_offset + col_index * scale,
                        top_offset + row_index * scale, scale, rgb)
    return canvas


def _crop_to_drawn_area(sprite: list[list[int]]) -> list[list[int]]:
    """スプライトの透明な余白を落として bounding box だけ返す。

    Args:
        sprite: 色番号の 2 次元配列。

    Returns:
        透明でない画素を囲む最小の 2 次元配列。

    Policy:
        - 16x16 の中で絵が左寄りでも、アイコン中央に置けるようにするため。
    """
    drawn = [(y, x) for y, row in enumerate(sprite)
             for x, color_index in enumerate(row)
             if color_index != TRANSPARENT_INDEX]
    if not drawn:
        return sprite
    top = min(y for y, _ in drawn)
    bottom = max(y for y, _ in drawn)
    left = min(x for _, x in drawn)
    right = max(x for _, x in drawn)
    return [row[left:right + 1] for row in sprite[top:bottom + 1]]


def _fill_block(canvas: list[list[tuple[int, int, int]]],
                left: int, top: int, scale: int,
                rgb: tuple[int, int, int]) -> None:
    """canvas の (left, top) から scale x scale を rgb で塗る。

    Args:
        canvas: 書き込み先の RGB 配列。
        left: 左端 x。
        top: 上端 y。
        scale: 一辺の px。
        rgb: 塗る色。

    Policy:
        - canvas 外にはみ出す分は無視する。
    """
    for y in range(top, min(top + scale, len(canvas))):
        row = canvas[y]
        for x in range(left, min(left + scale, len(row))):
            row[x] = rgb


def _encode_png(pixels: list[list[tuple[int, int, int]]],
                width: int, height: int) -> bytes:
    """RGB 配列を 8bit truecolor PNG のバイト列へ変換する。

    Args:
        pixels: height 行 x width 列の RGB tuple 配列。
        width: 画像幅。
        height: 画像高さ。

    Returns:
        PNG ファイルのバイト列。

    Policy:
        - filter type 0（None）固定。外部 library を足さないための最小実装。
    """
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for red, green, blue in row:
            raw += bytes((red, green, blue))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _png_chunk(b"IHDR", header)
            + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _png_chunk(b"IEND", b""))


def _png_chunk(tag: bytes, payload: bytes) -> bytes:
    """PNG チャンク（length + tag + payload + CRC）を組み立てる。

    Args:
        tag: 4 byte のチャンク名。
        payload: チャンク本体。

    Returns:
        チャンク 1 個分のバイト列。

    Policy:
        - CRC は tag + payload に対して計算する（PNG 仕様どおり）。
    """
    return (struct.pack(">I", len(payload)) + tag + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))


if __name__ == "__main__":
    run_main()
