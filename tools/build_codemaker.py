#!/usr/bin/env python3
"""G12 / Phase 2: Code Maker 用 zip ビルド入口。

このファイルに含まれる関数:

- build_codemaker_main_text: bundler 出力をラップして Code Maker 用 main.py を返す
- build_codemaker_zip: main.py と pyxres を zip に梱包する
- run_main: CLI エントリ（dist/code-maker.zip を生成する）

Problems:
    - codemaker zip の組み立てを 1 関数に詰め込むと、core 抽出・hash 計算・
      テンプレート挿入が混在し CR202/CR204 のステップ列ポリシーを満たせない。
    - dist/code-maker.zip は ENTRY POINT marker と CORE_HASH に依存しており、
      テンプレート文字列を素朴に書くと line too long になりやすい。

Solutions:
    - core/entry 分割・正規化・hash 計算は private helper に閉じ込め、
      public 関数は「述語呼び出し + private 委譲 + return」のステップ列に揃える。
    - テンプレート文字列は配列で組み立てて join し、1 行 79 字以内に抑える。

使い方:
    python tools/build_codemaker.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from zipfile import ZipFile

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from codemaker_bundler import build_bundled_source  # noqa: E402


# === Public API ===

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist" / "code-maker.zip"
BUNDLE_DIR = "block-quest"
ENTRY_POINT_MARKER = (
    "# ====================================================================="
    "\n"
    "# ENTRY POINT\n"
    "# ====================================================================="
    "\n"
)
STUDENT_AREA_BLOCK = """# BEGIN STUDENT AREA
# ここだけ かいてよい
# たとえば:
# say("こんにちは")
# リソースファイルは リソースエディタで へんしゅうします
# END STUDENT AREA
"""


def build_codemaker_main_text(source_text: str | None = None) -> str:
    """bundler から source text を生成して Code Maker 用 main.py を返す。

    Args:
        source_text: 旧 P1 では呼び出し側から source を受け取っていたが、
            P2 以降は bundler が常に manifest から生成するため無視される。
            呼出し互換のため引数は残している。

    Returns:
        STUDENT AREA と CORE_HASH ガードを含む、Code Maker 教材版 main.py。

    Policy:
        - 引数 source_text は P2 以降 unused（互換のため残す）。
        - core_source/entrypoint_source は ENTRY POINT marker で分割する。
    """
    return _build_codemaker_main_from_bundler(source_text)


def build_codemaker_zip(
        main_py: Path | None = None,
        *,
        pyxres: Path,
        output: Path) -> Path:
    """bundler から main.py を生成し、pyxres と一緒に zip にする。

    Args:
        main_py: 旧 P1 で受け取っていた main.py パス。P2 以降は無視。
        pyxres: 同梱する .pyxres リソースファイル。
        output: 出力 zip のパス。

    Returns:
        生成された zip のパス（output と同値）。

    Raises:
        FileNotFoundError: pyxres が存在しない場合。

    Policy:
        - main_py は P2 以降 unused（互換のため残す）。
        - 出力先 dir が無ければ作成し、main.py と pyxres を BUNDLE_DIR 下に置く。
    """
    return _emit_codemaker_zip(main_py, Path(pyxres), Path(output))


def run_main() -> int:  # noqa: CR100
    """CLI エントリ：dist/code-maker.zip を生成して情報を出力する。

    Returns:
        成功で 0、入力エラーで 1。

    Policy:
        - 生成成功時はサイズ情報を stdout に出して 0 を返す。
    """
    return _run_cli()


# === Internal helpers (private) ===


def _compute_sha256_text(text: str) -> str:
    """テキストの SHA-256 hex digest を返す。

    Args:
        text: ハッシュ計算対象の文字列。

    Returns:
        utf-8 でエンコードした text の SHA-256 hex 文字列。

    Policy:
        - hashlib.sha256 にそのまま委譲する純関数。
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _split_core_and_entrypoint(source_text: str) -> tuple[str, str]:
    """ENTRY POINT marker で source_text を core と entry に分割する。

    Args:
        source_text: bundler が生成した連結後 source text。

    Returns:
        (core_source, entrypoint_source) のタプル。

    Raises:
        ValueError: ENTRY POINT marker が見つからない場合。

    Policy:
        - marker の最後の出現位置を境界とする。
    """
    marker_index = source_text.rfind(ENTRY_POINT_MARKER)
    if marker_index == -1:
        raise ValueError("ENTRY POINT が見つかりません")
    core_source = source_text[:marker_index].rstrip() + "\n"
    entrypoint_source = source_text[marker_index:].lstrip("\n")
    return core_source, entrypoint_source


def _normalize_entrypoint_source(entrypoint_source: str) -> str:
    """entry の末尾に `game = run()` を必要に応じて足す。

    Args:
        entrypoint_source: ENTRY POINT marker 以降の生 source。

    Returns:
        末尾に `game = run()` を補完した entry source。

    Policy:
        - bundler 生成では `game = run()` が含まれないため明示的に追加する。
    """
    normalized = entrypoint_source.rstrip() + "\n"
    if _has_missing_run_call_suffix(normalized):
        normalized += "\ngame = run()\n"
    return normalized


def _has_missing_run_call_suffix(normalized: str) -> bool:
    """`game = run()` を末尾に追加すべきかを判定する。

    Args:
        normalized: 末尾を rstrip + 改行で揃えた entry source。

    Returns:
        run() 定義があって末尾が "run()" で終わっていなければ True。

    Policy:
        - 純粋な述語（True/False）。
    """
    has_run_def = "def run(" in normalized
    has_run_call_tail = normalized.rstrip().endswith("run()")
    return has_run_def and not has_run_call_tail


def _build_codemaker_main_from_bundler(_unused: str | None) -> str:
    """bundler から source を生成し Code Maker 用 main.py を組み立てる。

    Args:
        _unused: P1 互換のため受け取る旧 source_text。常に無視する。

    Returns:
        STUDENT AREA と CORE_HASH ガードを含む完成済み main.py 文字列。

    Policy:
        - 分割・正規化・hash 計算を順に呼び、最後にテンプレート挿入で返す。
    """
    del _unused  # P2 以降は bundler を常に呼ぶ
    source_text = build_bundled_source()
    core_source, entrypoint_source = _split_core_and_entrypoint(source_text)
    entrypoint_source = _normalize_entrypoint_source(entrypoint_source)
    core_hash = _compute_sha256_text(core_source)
    return _render_codemaker_template(
        core_source, entrypoint_source, core_hash,
    )


_GUARD_MESSAGE_BODY = (
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
)

_VERIFY_AND_EXEC_BLOCK = (
    "def verify_core():\n"
    "    if _sha256_text(CORE_BLOCK) != CORE_HASH:\n"
    "        _show_core_guard_message()\n"
    '        raise SystemExit("core block modified")\n\n'
    "verify_core()\n"
    "exec(CORE_BLOCK, globals())\n\n"
)


def _render_codemaker_template(
    core_source: str,
    entrypoint_source: str,
    core_hash: str,
) -> str:
    """ガード付きテンプレートに core/entry/hash を差し込む。

    Args:
        core_source: ENTRY POINT より前の core 部 source。
        entrypoint_source: ENTRY POINT 以降の entry 部 source。
        core_hash: core_source の SHA-256 hex digest。

    Returns:
        完成済みの Code Maker 用 main.py 文字列。

    Policy:
        - 行リストを join して 79 字制限と整形性を両立する。
    """
    header = _render_template_header(core_source, core_hash)
    return header + _VERIFY_AND_EXEC_BLOCK + f"{STUDENT_AREA_BLOCK}\n" + (
        entrypoint_source
    )


def _render_template_header(core_source: str, core_hash: str) -> str:
    """テンプレート前段（import / 定数 / guard 関数）を文字列で返す。

    Args:
        core_source: ENTRY POINT より前の core 部 source。
        core_hash: core_source の SHA-256 hex digest。

    Returns:
        Code Maker main.py のヘッダ部分文字列。

    Policy:
        - guard 表示ロジックは _GUARD_MESSAGE_BODY 定数を埋め込むだけ。
    """
    return (
        "# Auto-generated Code Maker classroom bundle.\n"
        "import hashlib\n"
        "import pyxel\n\n"
        f"CORE_BLOCK = {core_source!r}\n"
        f'CORE_HASH = "{core_hash}"\n\n'
        "def _sha256_text(text):\n"
        '    return hashlib.sha256(text.encode("utf-8")).hexdigest()\n\n'
        "def _show_core_guard_message():\n"
        + _GUARD_MESSAGE_BODY
    )


def _emit_codemaker_zip(
    _unused_main_py: Path | None,
    pyxres: Path,
    output: Path,
) -> Path:
    """pyxres を検証し、main.py と一緒に zip 出力する。

    Args:
        _unused_main_py: P1 互換のため受け取る旧 main.py パス。常に無視する。
        pyxres: 同梱する .pyxres リソースファイル。
        output: 出力 zip のパス。

    Returns:
        書き出した output パス。

    Raises:
        FileNotFoundError: pyxres が無い場合。

    Policy:
        - 出力 dir を作り、ZipFile に main.py と pyxres を書き出す。
    """
    del _unused_main_py  # P2 以降 unused
    if not pyxres.exists():
        raise FileNotFoundError(f"{pyxres} が見つかりません")
    generated_main = build_codemaker_main_text()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w") as zf:
        zf.writestr(f"{BUNDLE_DIR}/main.py", generated_main)
        zf.write(pyxres, f"{BUNDLE_DIR}/my_resource.pyxres")
    return output


def _run_cli() -> int:
    """CLI 実行本体（zip 生成 + 結果報告）。

    Returns:
        成功で 0、FileNotFoundError/ValueError で 1。

    Policy:
        - 失敗時は ERROR 行を 1 行出して 1 を返す。
    """
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
    sys.exit(run_main())
