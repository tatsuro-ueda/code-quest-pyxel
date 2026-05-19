#!/usr/bin/env python3
"""SSoT YAML から src/generated/*.py を生成する CLI。

このファイルに含まれる関数:

- generate_one: 1 ターゲットを assets/<name>.yaml から生成する
- run_main: CLI エントリ（全/指定ターゲットを生成し exit code を返す）

Problems:
    - YAML を毎回手書きで src/generated に転記すると、SSoT 違反と
      フォーマット揺れが起きやすい。
    - 生成ロジックを 1 関数に詰め込むと 50 行を超え、CR202/CR203/CR204
      のステップ列ポリシーに反する。

Solutions:
    - 整形・書き出し・dialogue 専用ロジックを private helper に切り出し、
      public 関数は「述語呼び出し + private 委譲 + return」のステップ列に揃える。
    - 出力経路は GENERATED 配下のみとし、書き込み後は read-only 属性に戻す。

Usage:
    python tools/gen_data.py          # generate all
    python tools/gen_data.py enemies  # generate one
"""
from __future__ import annotations

import stat
import sys
from pathlib import Path
from typing import Any

import yaml


# === Public API ===

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
GENERATED = ROOT / "src" / "generated"


HEADER = "# GENERATED - DO NOT EDIT  (source: assets/{yaml})\n"

# registry: yaml_name -> (variable_name, type_hint)
TARGETS: dict[str, tuple[str, str]] = {
    "enemies": ("ENEMIES", "list[dict[str, Any]]"),
    "items": ("ITEMS", "list[dict[str, Any]]"),
    "weapons": ("WEAPONS", "list[dict[str, Any]]"),
    "armors": ("ARMORS", "list[dict[str, Any]]"),
    "spells": ("SPELLS", "list[dict[str, Any]]"),
    "shops": ("SHOPS", "dict[str, Any]"),
    "dialogue": ("DIALOGUE_JA", "dict[str, Any]"),
}


def generate_one(name: str) -> bool:
    """src/generated/{name}.py を assets/{name}.yaml から生成する。

    Args:
        name: TARGETS のキー（"enemies" など）。

    Returns:
        生成に成功すれば True、入力欠落・YAML エラーなら False。

    Policy:
        - 不明なターゲットや欠落 yaml は stderr に出して False を返す。
        - 出力は GENERATED 配下のみで、書き込み後は read-only に戻す。
    """
    return _run_generate_one(name)


def run_main() -> int:  # noqa: CR100
    """CLI エントリ：引数を target 名として generate_one を回す。

    Returns:
        全件成功で 0、いずれか失敗で 1。

    Policy:
        - 引数が空のときは TARGETS 全件を対象にする。
    """
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(TARGETS)
    return _run_all_targets(targets)


# === Internal helpers (private) ===


_LOAD_ERROR: Any = object()


def _run_generate_one(name: str) -> bool:
    """generate_one の本体（述語チェック + 委譲のステップ列）。

    Args:
        name: TARGETS のキー。

    Returns:
        生成に成功すれば True、失敗なら False。

    Policy:
        - 述語で早期 return、最後に委譲して返すステップ列に統一する。
    """
    if not _is_known_target(name):
        return False
    yaml_path = ASSETS / f"{name}.yaml"
    if not _has_yaml_source(yaml_path):
        return False
    data = _load_yaml_data(yaml_path)
    if data is _LOAD_ERROR:
        return False
    return _emit_generated_module(name, yaml_path, data)


def _format_literal(obj: Any, indent: int = 0) -> str:
    """Python リテラルを indent 付きで整形して返す。

    Args:
        obj: dict/list/str/bool/None/数値などのプレーンな値。
        indent: 現在のネスト深さ。

    Returns:
        生成モジュールに貼り付け可能な文字列表現。

    Policy:
        - dict/list/scalar の各 helper に委譲するだけのディスパッチ。
    """
    pad = "    " * indent
    inner = "    " * (indent + 1)
    if isinstance(obj, dict):
        return _format_dict(obj, indent, pad, inner)
    if isinstance(obj, list):
        return _format_list(obj, indent, pad, inner)
    return _format_scalar(obj)


def _write_generated_module(out_path: Path, lines: list[str]) -> None:
    """生成モジュールを書き、read-only 属性に戻す。

    Args:
        out_path: 出力先 .py ファイル。
        lines: 書き出す行のリスト（改行で join される）。

    Policy:
        - 既存ファイルがあれば一旦書き込み可にしてから上書きする。
    """
    if out_path.exists():
        out_path.chmod(stat.S_IRUSR | stat.S_IWUSR |
                       stat.S_IRGRP | stat.S_IROTH)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    out_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def _build_dialogue_lines(data: Any) -> list[str]:
    """dialogue.yaml 用の生成モジュール行列を構築する。

    Args:
        data: dialogue.yaml をロードした結果（ja/en mapping を期待）。

    Returns:
        生成モジュールの行リスト。

    Raises:
        TypeError: data または data["ja"]/data["en"] が dict でない場合。

    Policy:
        - ja/en それぞれを別の DIALOGUE_* 定数として出力する。
    """
    _ensure_dialogue_shape(data)
    return [
        HEADER.format(yaml="dialogue.yaml"),
        "from __future__ import annotations\n",
        "from typing import Any\n",
        "",
        f"DIALOGUE_JA: dict[str, Any] = {_format_literal(data['ja'])}\n",
        "",
        f"DIALOGUE_EN: dict[str, Any] = {_format_literal(data['en'])}\n",
    ]


def _format_dict(obj: dict, indent: int, pad: str, inner: str) -> str:
    """dict を複数行 indent 付きで整形する。

    Args:
        obj: 対象 dict。
        indent: 現在のネスト深さ。
        pad: 閉じ括弧側 indent 文字列。
        inner: 中身行 indent 文字列。

    Returns:
        整形済み Python リテラル文字列。

    Policy:
        - 空 dict は "{}" を返し、それ以外は key/value を再帰整形する。
    """
    if not obj:
        return "{}"
    items = []
    for k, v in obj.items():
        items.append(
            f"{inner}{_format_literal(k)}: "
            f"{_format_literal(v, indent + 1)}"
        )
    return "{\n" + ",\n".join(items) + f",\n{pad}" + "}"


def _format_list(obj: list, indent: int, pad: str, inner: str) -> str:
    """list を整形する（scalar のみなら 1 行、それ以外は複数行）。

    Args:
        obj: 対象 list。
        indent: 現在のネスト深さ。
        pad: 閉じ括弧側 indent 文字列。
        inner: 中身行 indent 文字列。

    Returns:
        整形済み Python リテラル文字列。

    Policy:
        - 全要素が非コンテナならインライン、そうでなければ複数行に展開。
    """
    if not obj:
        return "[]"
    if all(not isinstance(e, (dict, list)) for e in obj):
        return "[" + ", ".join(_format_literal(e) for e in obj) + "]"
    items = [f"{inner}{_format_literal(e, indent + 1)}" for e in obj]
    return "[\n" + ",\n".join(items) + f",\n{pad}]"


def _format_scalar(obj: Any) -> str:
    """str/bool/None/数値などのスカラを repr で整形する。

    Args:
        obj: 整形対象のスカラ値。

    Returns:
        Python リテラル文字列。

    Policy:
        - None は "None"、それ以外は repr に委ねる。
    """
    if isinstance(obj, str):
        return repr(obj)
    if isinstance(obj, bool):
        return repr(obj)
    if obj is None:
        return "None"
    return repr(obj)


def _ensure_dialogue_shape(data: Any) -> None:
    """dialogue.yaml の構造を検証し、不正なら TypeError を投げる。

    Args:
        data: dialogue.yaml をロードした結果。

    Raises:
        TypeError: data または data["ja"]/data["en"] が dict でない場合。

    Policy:
        - data 全体と ja/en それぞれが dict であることを要求する。
    """
    if not isinstance(data, dict):
        raise TypeError(
            "dialogue.yaml must be a mapping with 'ja' and 'en' keys")
    if not isinstance(data.get("ja"), dict):
        raise TypeError("dialogue.yaml: 'ja' must be a mapping")
    if not isinstance(data.get("en"), dict):
        raise TypeError("dialogue.yaml: 'en' must be a mapping")


def _is_known_target(name: str) -> bool:
    """name が TARGETS に存在するかを返し、無ければ stderr に出す。

    Args:
        name: チェック対象の target 名。

    Returns:
        TARGETS に含まれていれば True、そうでなければ False。

    Policy:
        - 純粋な述語（True/False のみ）。未知時の通知は副作用として stderr 出力。
    """
    if name in TARGETS:
        return True
    print(f"error: unknown target '{name}' (known: {', '.join(TARGETS)})",
          file=sys.stderr)
    return False


def _has_yaml_source(yaml_path: Path) -> bool:
    """yaml_path が存在するかを返し、無ければ stderr に出す。

    Args:
        yaml_path: 検証する yaml ファイルのパス。

    Returns:
        ファイルが存在すれば True、無ければ False。

    Policy:
        - 純粋な述語（True/False のみ）。
    """
    if yaml_path.exists():
        return True
    print(f"error: {yaml_path} not found", file=sys.stderr)
    return False


def _load_yaml_data(yaml_path: Path) -> Any:
    """yaml をロードする。失敗時は _LOAD_ERROR sentinel を返す。

    Args:
        yaml_path: ロードする yaml ファイルのパス。

    Returns:
        ロード成功時はパース結果、失敗時は _LOAD_ERROR sentinel。

    Policy:
        - YAMLError/OSError のみ補足して上位に sentinel で伝える。
    """
    try:
        return yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"error: {yaml_path}: {e}", file=sys.stderr)
        return _LOAD_ERROR
    except OSError as e:
        print(f"error: {yaml_path}: {e}", file=sys.stderr)
        return _LOAD_ERROR


def _emit_generated_module(name: str, yaml_path: Path, data: Any) -> bool:
    """1 ターゲットの生成モジュールを実際に書き出す。

    Args:
        name: target 名。
        yaml_path: ソース yaml のパス（エラー時の文脈出力に使う）。
        data: yaml をロードしたパース結果。

    Returns:
        生成に成功すれば True、行リスト構築に失敗すれば False。

    Policy:
        - 出力先ディレクトリを作り、行列を構築し、_write_generated_module に委譲。
    """
    var_name, type_hint = TARGETS[name]
    out_path = GENERATED / f"{name}.py"
    GENERATED.mkdir(parents=True, exist_ok=True)
    lines = _build_module_lines(name, var_name, type_hint, data, yaml_path)
    if lines is None:
        return False
    _write_generated_module(out_path, lines)
    _ensure_generated_init()
    print(f"  generated: {out_path.relative_to(ROOT)}")
    return True


def _build_module_lines(
    name: str,
    var_name: str,
    type_hint: str,
    data: Any,
    yaml_path: Path,
) -> list[str] | None:
    """ターゲット種別に応じた生成モジュールの行リストを構築する。

    Args:
        name: target 名。
        var_name: 出力モジュールに置く変数名。
        type_hint: 変数の型ヒント文字列。
        data: yaml パース結果。
        yaml_path: エラー時の文脈出力用 yaml パス。

    Returns:
        行リスト、または dialogue 構造不正なら None。

    Policy:
        - dialogue は専用 helper、それ以外は単一定数モジュールを返す。
    """
    if name == "dialogue":
        try:
            return _build_dialogue_lines(data)
        except TypeError as e:
            print(f"error: {yaml_path}: {e}", file=sys.stderr)
            return None
    return [
        HEADER.format(yaml=f"{name}.yaml"),
        "from __future__ import annotations\n",
        "from typing import Any\n",
        "",
        f"{var_name}: {type_hint} = {_format_literal(data)}\n",
    ]


def _ensure_generated_init() -> None:
    """src/generated/__init__.py が無いとき作成し read-only にする。

    Policy:
        - 既存ファイルがあれば触らない（存在チェックで分岐）。
    """
    init = GENERATED / "__init__.py"
    if not init.exists():
        init.write_text("", encoding="utf-8")
        init.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def _run_all_targets(targets: list[str]) -> int:
    """指定された target を順次 generate_one で生成し exit code を返す。

    Args:
        targets: 生成する target 名のリスト。

    Returns:
        全件成功で 0、いずれか失敗で 1。

    Policy:
        - 1 件でも失敗したら 1 を返す。
    """
    has_all_ok = True
    for name in targets:
        if not generate_one(name):
            has_all_ok = False
    return 0 if has_all_ok else 1


if __name__ == "__main__":
    sys.exit(run_main())
