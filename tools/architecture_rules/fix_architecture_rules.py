"""architecture rule warning に対して一度だけ deterministic fix を適用する。

このファイルに含まれる関数・クラス：

- load_yaml：rules YAML を dict にロードする入口関数
- write_yaml：人が読みやすい整形をかけて YAML を保存する公開関数
- ensure_tree_path：facts.tree の指定パスを正規化して該当ノードを返す公開関数
- run_fixer：rules path に対し autofix を 1 巡走らせる公開エントリ
- main：CLI 入口（argv を受けて run_fixer を呼び結果 JSON を stdout に出す）
- fix_generated_files_edit_policy：generated rule の facts 補正と再生成を担う fixer
- fix_dist_not_source：dist 直下の宣言と再 build だけで rule を直す fixer
- fix_build_runbook_paths：build runbook の path / outputs を canonical に揃える fixer
- fix_codemaker_manifest_non_scene_paths：codemaker manifest の不足 path を補う fixer
- fix_runtime_entry_chain：runtime wrapper -> shim -> Game を canonical 化する fixer
- FIXER_REGISTRY：rule_id -> fixer 関数の dispatch table（外部から名前で参照される）
- _ReadableYamlDumper：人間が diff を読む前提で indent を保つ SafeDumper サブクラス
- _format_yaml_for_humans：dump 結果に主要セクションの空行を挟む整形ヘルパ
- _is_yaml_section_header：行が主要セクションの先頭かを判定する述語
- _is_path_section_start：行が `- path:` 始まりかを判定する述語
- _is_top_id_or_label_start：行が浅い indent の `- id:` / `- label_ja:` かを判定する述語
- _has_separator_need：1 行がセパレータを必要とするかを束ねる述語
- _read_manifest_entries_with_lines：manifest をテキスト行のリストに分解するヘルパ
- _write_manifest_lines：行リストを末尾改行付きで書き戻すヘルパ
- _find_codemaker_bundle_contract：facts から指定 id の codemaker contract を取り出すヘルパ
- _manifest_entries：行リストからコメント除去済みの entry 集合を作るヘルパ
- _is_comment_or_blank：行が空行 / コメントかを判定する述語
- _manifest_insert_before_marker：marker 行の手前へ path を挿入する低レベル操作
- _insert_codemaker_manifest_path：path のカテゴリに応じて挿入位置を選ぶ振り分け
- _categorize_manifest_path：path を挿入カテゴリ + marker のタプルに分類する純粋関数
- _set_rule_internal_fields：rule dict に rules_path を内部フィールドとして注入するヘルパ
- _get_expected_source_for_generated_entry：generated path から source 文字列を作る
- _ensure_tree_path_root：path == "." 時に root へフィールドを上書きする private 委譲
- _ensure_tree_path_segments：path をセグメントごとに辿ってノードを補完する private 委譲
- _merge_runtime_entry_preserving_extras：runtime entry を canonical へ寄せる
- _build_merged_runtime_nodes：canonical と existing の nodes をペア合成する純粋関数
- _get_existing_node_at：nodes リストから index の dict を安全に取り出す純粋関数
- _normalize_generated_entry：1 entry を facts 側で canonical に揃える private 委譲
- _run_gen_data_if_present：tools/gen_data.py を存在チェック込みで実行するヘルパ
- _run_build_web_release_if_present：build_web_release.py を実行するヘルパ
- _ensure_dist_artifact_nodes：dist 直下の artifact ノードを一括で正規化するヘルパ
- _normalize_codemaker_zip_runbook：codemaker_zip runbook を canonical に揃える
- _normalize_release_runbook：release_artifacts runbook を canonical 化
- _normalize_runtime_main_wrapper：main.py wrapper を canonical 形に書き戻すヘルパ
- _normalize_runtime_shim：runtime shim ファイルの imports と tail を canonical 形に揃える
- _ensure_runtime_tree_nodes：runtime 系 4 path を facts.tree に補完するヘルパ
- _normalize_runtime_entry_points：runtime_entry_chain を canonical 化
- _has_existing_runtime_entry：runtime_entry_chain の有無を返す述語
- _has_pending_warnings：run_fixer 内で warnings が残っているかを判定する述語
- _apply_registered_fixers：FIXER_REGISTRY を走らせて applied_fixes を返す private 本体
- _build_run_fixer_payload：run_fixer の status / 結果 dict を組む純粋関数
- _build_run_fixer_error_payload：run_fixer 例外時の戻り値 dict を組む純粋関数
- _build_fix_arg_parser：fix CLI 用 argparse.ArgumentParser を組み立てる純粋関数

Problems:
    - 1 つの fixer に「Python 実体の書き換え」「facts YAML の補正」「外部
      コマンドの実行」を全部詰めると、20 行ルールも CR204 ステップ列ルールも
      満たせず、AI 補助のリファクタ判断もブレやすい。
    - bool フラグ `changed_yaml` / `changed` を多用する内部 helper は
      CR101 違反の温床になり、外側の rule 体系と整合が取れない。

Solutions:
    - 公開 fixer は「述語呼び出し + private 委譲 + return」のステップ列に
      固定し、副作用本体を private helper に切り出して 20 行ルールを満たす。
    - bool フラグの代わりに「変更を担う helper を呼ぶ -> その関数が
      内部で diff 判定する」形に揃え、CR101 を構造的に解消する。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from . import check_architecture_rules


ROOT = Path(__file__).resolve().parents[2]

CANONICAL_MAIN_WRAPPER = (
    "from pathlib import Path\n"
    "\n"
    "\n"
    "_RUNTIME_PATH = Path(__file__).resolve().parent / "
    "\"src\" / \"runtime\" / \"main_runtime.py\"\n"
    "exec(compile(_RUNTIME_PATH.read_text(encoding=\"utf-8\"), "
    "str(_RUNTIME_PATH), \"exec\"), globals())\n"
    "\n"
    "if __name__ == \"__main__\":\n"
    "    run()\n"
)

ENTRY_POINT_MARKER = (
    "# ====================================================================="
    "\n# ENTRY POINT\n"
    "# ====================================================================="
    "\n"
)
CANONICAL_RUNTIME_TAIL = (
    "# ====================================================================="
    "\n"
    "# ENTRY POINT\n"
    "# ====================================================================="
    "\n"
    "def run():\n"
    "    \"\"\"Block Quest の entry point。Game を生成して pyxel.run に入る。"
    "\"\"\"\n"
    "    return _run()\n"
)


# === Public API ===


def load_yaml(path: Path) -> dict[str, Any]:
    """architecture rules YAML を読み込んで dict に変換する。

    Args:
        path: 読み込み対象 YAML の Path。

    Returns:
        dict[str, Any]: yaml.safe_load の結果。

    Policy:
        - 入口 helper の責務はファイル -> dict だけに閉じる。
    """
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    """data dict を人間に読みやすい YAML として path に書き戻す。

    Args:
        path: 書き出し先 Path。
        data: rules YAML 全体を表す dict。

    Policy:
        - 整形ルールは _format_yaml_for_humans に閉じ、ここでは write のみ担う。
    """
    path.write_text(_format_yaml_for_humans(data), encoding="utf-8")


def ensure_tree_path(
    root: dict[str, Any], path_value: str,
    kind: str, **fields: Any,
) -> dict[str, Any]:
    """facts.tree の path_value ノードを kind と追加 fields で揃える。

    Args:
        root: facts.tree の root dict（in-place 更新される）。
        path_value: 揃えたい tree 上のパス。"." なら root 自体。
        kind: ノードの種別（"file" / "directory" / "root"）。
        **fields: ノードに追記する追加プロパティ。

    Returns:
        dict[str, Any]: 揃え終わった該当ノード。

    Policy:
        - 分岐は private helper _ensure_tree_path_dispatch に閉じる。
    """
    return _ensure_tree_path_dispatch(root, path_value, kind, fields)


def fix_generated_files_edit_policy(
    repo_root: Path,
    rules_path: Path,
    warning: dict[str, Any],
) -> list[dict[str, Any]]:
    """generated rule に対し facts 補正と再生成スクリプト実行を 1 巡だけ走らせる。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        warning: checker が報告した warning dict（ここでは未使用）。

    Returns:
        list[dict[str, Any]]: 適用した fix の説明リスト。

    Policy:
        - 「facts 正規化 -> 差分があれば write -> gen_data 再実行」を委譲する。
    """
    fixes: list[dict[str, Any]] = []
    _apply_generated_files_fix(repo_root, rules_path, fixes)
    return fixes


def fix_dist_not_source(
    repo_root: Path,
    rules_path: Path,
    warning: dict[str, Any],
) -> list[dict[str, Any]]:
    """dist 配下の facts 宣言を canonical に揃え、Web release を再 build する。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        warning: checker が報告した warning dict（ここでは未使用）。

    Returns:
        list[dict[str, Any]]: 適用した fix の説明リスト。

    Policy:
        - 副作用本体は _apply_dist_not_source_fix に閉じ込める。
    """
    fixes: list[dict[str, Any]] = []
    _apply_dist_not_source_fix(repo_root, rules_path, fixes)
    return fixes


def fix_build_runbook_paths(
    repo_root: Path,
    rules_path: Path,
    warning: dict[str, Any],
) -> list[dict[str, Any]]:
    """build 系 runbook の path / outputs / artifact ノードを canonical に揃える。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        warning: checker が報告した warning dict（ここでは未使用）。

    Returns:
        list[dict[str, Any]]: 適用した fix の説明リスト。

    Policy:
        - 副作用本体は _apply_build_runbook_paths_fix に閉じ込める。
    """
    fixes: list[dict[str, Any]] = []
    _apply_build_runbook_paths_fix(repo_root, rules_path, fixes)
    return fixes


def fix_codemaker_manifest_non_scene_paths(
    repo_root: Path,
    rules_path: Path,
    warning: dict[str, Any],
) -> list[dict[str, Any]]:
    """codemaker non-scene manifest に不足 path がある場合だけ補充する。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        warning: checker が報告した warning dict（ここでは未使用）。

    Returns:
        list[dict[str, Any]]: 適用した fix の説明リスト。

    Policy:
        - 前提条件と本体を _run_codemaker_manifest_fix にまとめて委譲する。
    """
    return _run_codemaker_manifest_fix(repo_root, rules_path)


def fix_runtime_entry_chain(
    repo_root: Path,
    rules_path: Path,
    warning: dict[str, Any],
) -> list[dict[str, Any]]:
    """runtime wrapper -> shim -> Game の鎖を canonical 形に揃える。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        warning: checker が報告した warning dict（ここでは未使用）。

    Returns:
        list[dict[str, Any]]: 適用した fix の説明リスト。

    Policy:
        - 実コード / facts.tree / entry_points の更新を 1 helper に委譲する。
    """
    fixes: list[dict[str, Any]] = []
    _apply_runtime_entry_chain_fix(repo_root, rules_path, fixes)
    return fixes


def run_fixer(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
    check: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """warnings を 1 巡だけ autofix し、結果 dict を返す。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        rule_ids: 対象 rule の絞り込み（None なら全 rule）。
        check: 直近の checker 結果。未指定なら走らせて取得する。

    Returns:
        dict[str, Any]: status / check / applied_fixes（または error）。

    Policy:
        - 例外処理だけここに残し、本体は _run_fixer_body に委譲する。
    """
    return _run_fixer_guarded(
        repo_root.resolve(), rules_path.resolve(),
        rule_ids=rule_ids, check=check,
    )


FIXER_REGISTRY = {
    "generated_files_edit_policy": fix_generated_files_edit_policy,
    "dist_not_source": fix_dist_not_source,
    "codemaker_manifest_non_scene_paths": (
        fix_codemaker_manifest_non_scene_paths
    ),
    "build_runbook_paths": fix_build_runbook_paths,
    "runtime_entry_chain": fix_runtime_entry_chain,
}


def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """CLI 入口。argv を解釈して run_fixer を呼び、結果 JSON を stdout に出す。

    Args:
        argv: コマンドライン引数。None なら sys.argv[1:] を使う。

    Returns:
        int: status が OK / FIXED なら 0、それ以外は 1。

    Policy:
        - parser 組み立ては _build_fix_arg_parser に切り出し、流れだけ残す。
    """
    parser = _build_fix_arg_parser()
    args = parser.parse_args(argv)
    result = run_fixer(
        args.repo_root,
        args.rules_path,
        rule_ids=set(args.rule_id) if args.rule_id else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"OK", "FIXED"} else 1


# === Internal helpers (private) ===


# === YAML formatting helpers ===


class _ReadableYamlDumper(yaml.SafeDumper):
    """diff レビュー用に nested list の indent を保つ SafeDumper。

    Policy:
        - increase_indent を override して indentless を常に False にする。
    """

    # === Public API ===

    def increase_indent(
        self,
        flow: bool = False,
        indentless: bool = False,
    ) -> Any:
        """yaml の indent を 1 段深くする際、indentless を強制的に False にする。

        Args:
            flow: 親 dumper から渡される flow 引数。
            indentless: 親 dumper から渡される indentless 引数（無視する）。

        Returns:
            Any: 親 dumper の increase_indent 戻り値。

        Policy:
            - 人が diff を読む前提なので、indentless によるブロック圧縮を避ける。
        """
        return super().increase_indent(flow, False)


_MAJOR_FACT_KEYS = {
    "  tree:",
    "  flows:",
    "  entry_points:",
    "  runbooks:",
    "  migration_notes:",
}


def _format_yaml_for_humans(data: dict[str, Any]) -> str:
    """data を _ReadableYamlDumper で dump し、主要セクションに空行を挟む。

    Args:
        data: rules YAML 全体を表す dict。

    Returns:
        str: 末尾改行付きの整形済み YAML 文字列。

    Policy:
        - 1 行ごとのセパレータ判定は _has_separator_need に委譲する。
    """
    dumped = yaml.dump(
        data,
        Dumper=_ReadableYamlDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=88,
    )
    formatted: list[str] = []
    for raw_line in dumped.splitlines():
        line = raw_line.rstrip()
        if _can_insert_separator_before(line, formatted):
            formatted.append("")
        formatted.append(line)
    return "\n".join(formatted).lstrip("\n") + "\n"


def _can_insert_separator_before(line: str, formatted: list[str]) -> bool:
    """formatted の末尾と line を見て、空行を挟めるかを返す。

    Args:
        line: 直前に rstrip した 1 行。
        formatted: 既に整形済みの行リスト。

    Returns:
        bool: 区切り空行を挟むのが妥当なら True。

    Policy:
        - 直前の空行と先頭行の二重挿入を避け、複合条件を 1 述語に閉じる。
    """
    if not _has_separator_need(line):
        return False
    if not formatted:
        return False
    return formatted[-1] != ""


def _is_yaml_section_header(line: str) -> bool:
    """line が facts / validation_rules / 主要 facts セクションの先頭かを返す。

    Args:
        line: 1 行の文字列（末尾改行除去済み）。

    Returns:
        bool: 主要セクションの先頭なら True。

    Policy:
        - リテラル比較だけで済む判定を 1 箇所に閉じる。
    """
    if line in {"facts:", "validation_rules:"}:
        return True
    return line in _MAJOR_FACT_KEYS


def _is_path_section_start(stripped: str) -> bool:
    """stripped が `- path:` 始まりかを返す述語。

    Args:
        stripped: lstrip 済みの 1 行。

    Returns:
        bool: `- path:` で始まるなら True。

    Policy:
        - dump 結果から path セクションの境目を機械的に検出する。
    """
    return stripped.startswith("- path:")


def _is_top_id_or_label_start(stripped: str, indent: int) -> bool:
    """stripped が浅い indent の `- id:` / `- label_ja:` かを返す述語。

    Args:
        stripped: lstrip 済みの 1 行。
        indent: その行の先頭空白数。

    Returns:
        bool: 浅い rule / entry の先頭なら True。

    Policy:
        - 深い nest にも同じ key は出てくるため indent <= 4 でガードする。
    """
    if indent > 4:
        return False
    return (
        stripped.startswith("- id:") or stripped.startswith("- label_ja:")
    )


def _has_separator_need(line: str) -> bool:
    """line がセパレータ空行を必要とするかを束ねた述語。

    Args:
        line: rstrip 済みの 1 行。

    Returns:
        bool: いずれかの述語に該当すれば True。

    Policy:
        - 個別判定を private 述語に分け、ここでは束ねるだけにする。
    """
    if _is_yaml_section_header(line):
        return True
    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    if _is_path_section_start(stripped):
        return True
    return _is_top_id_or_label_start(stripped, indent)


# === Manifest file helpers ===


def _read_manifest_entries_with_lines(path: Path) -> list[str]:
    """manifest ファイルを行リストとして読み込む。

    Args:
        path: 対象ファイル Path。

    Returns:
        list[str]: 1 行ごとに分割した文字列（改行は含まない）。

    Policy:
        - 入出力ヘルパは責務をテキスト分割だけに閉じる。
    """
    return path.read_text(encoding="utf-8").splitlines()


def _write_manifest_lines(path: Path, lines: list[str]) -> None:
    """行リストを末尾改行 1 つに揃えてファイルへ書き戻す。

    Args:
        path: 書き出し先 Path。
        lines: 書き戻す行リスト。

    Policy:
        - 末尾の余剰空白行を rstrip で 1 行に揃えてから書き出す。
    """
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _find_codemaker_bundle_contract(
    data: dict[str, Any], contract_id: str,
) -> dict[str, Any] | None:
    """facts.codemaker_bundle_contracts から指定 id の contract を取り出す。

    Args:
        data: rules YAML 全体を表す dict。
        contract_id: 取り出したい contract の id。

    Returns:
        dict[str, Any] | None: 該当 contract、無ければ None。

    Policy:
        - facts や key の有無に強い generator 走査で「無ければ None」を保つ。
    """
    contracts = data.get("facts", {}).get("codemaker_bundle_contracts", [])
    return next(
        (item for item in contracts if item.get("id") == contract_id),
        None,
    )


def _is_comment_or_blank(line: str) -> bool:
    """line が空 / コメント行かを返す述語。

    Args:
        line: lstrip 済みの 1 行。

    Returns:
        bool: 空文字 or `#` 始まりなら True。

    Policy:
        - manifest entry 判定で「無視すべき行」を 1 箇所に閉じる。
    """
    if not line:
        return True
    return line.startswith("#")


def _manifest_entries(lines: list[str]) -> set[str]:
    """manifest 行リストからコメント / 空行を除いた entry 集合を作る。

    Args:
        lines: manifest の行リスト。

    Returns:
        set[str]: コメントを除いた entry の集合。

    Policy:
        - 無視判定は _is_comment_or_blank に委譲し、ここでは集合化だけ担う。
    """
    entries: set[str] = set()
    for raw in lines:
        line = raw.strip()
        if _is_comment_or_blank(line):
            continue
        entries.add(line)
    return entries


def _manifest_insert_before_marker(
    lines: list[str], path: str, marker: str | None,
) -> None:
    """marker 行の手前に path を挿入する。marker が無ければ末尾に追加。

    Args:
        lines: 対象の manifest 行リスト（in-place 更新）。
        path: 挿入する path 文字列。
        marker: 挿入位置を決めるコメント行の prefix。None なら末尾に追加。

    Policy:
        - marker None の早期 return で append 経路を分岐させる。
    """
    if marker is None:
        lines.append(path)
        return
    for index, line in enumerate(lines):
        if line.startswith(marker):
            lines.insert(index, path)
            return
    lines.append(path)


_CODEMAKER_MANIFEST_RULES: list[tuple[str, str, str | None]] = [
    (
        "exact:src/shared/services/debug_service.py",
        "src/shared/services/debug_service.py",
        "# --- 10. src/runtime/app.py:",
    ),
    (
        "exact:src/shared/services/scene_manager.py",
        "src/shared/services/scene_manager.py",
        "# --- 10. src/runtime/app.py:",
    ),
    (
        "prefix:src/shared/assets/",
        "src/shared/assets/",
        "# --- 2. shared/constants:",
    ),
    (
        "prefix:src/shared/constants/",
        "src/shared/constants/",
        "# --- 3. src/generated:",
    ),
    (
        "prefix:src/generated/",
        "src/generated/",
        "# --- 4. src/game_data.py:",
    ),
    (
        "exact:src/game_data.py",
        "src/game_data.py",
        "# --- 5a. shared/state:",
    ),
    (
        "prefix:src/shared/state/",
        "src/shared/state/",
        "# --- 5. shared/services:",
    ),
    (
        "prefix:src/shared/services/",
        "src/shared/services/",
        "# --- 6. shared/ui:",
    ),
    (
        "prefix:src/shared/ui/",
        "src/shared/ui/",
        "# --- 7. scenes:",
    ),
    (
        "exact:src/runtime/app.py",
        "src/runtime/app.py",
        None,
    ),
]


def _categorize_manifest_path(path: str) -> str | None:
    """path がどの挿入カテゴリに当たるかを判定し marker 文字列を返す。

    Args:
        path: codemaker manifest に挿入したい path。

    Returns:
        str | None: 挿入直前 marker。マッチしなければ None（= 末尾）。

    Policy:
        - rule リストを順に評価し、kind ごとの述語呼び出しに分岐を閉じる。
    """
    for kind, key, marker in _CODEMAKER_MANIFEST_RULES:
        if _is_manifest_rule_match(kind, key, path):
            return marker
    return None


def _is_manifest_rule_match(kind: str, key: str, path: str) -> bool:
    """1 件の manifest rule が path に当てはまるかを返す述語。

    Args:
        kind: rule の種別キー（"exact:..." または "prefix:..."）。
        key: rule の照合対象文字列。
        path: 評価対象の path。

    Returns:
        bool: rule に該当するなら True。

    Policy:
        - exact / prefix の判定を 1 関数に閉じ、CR303 を避ける。
    """
    if kind.startswith("exact:"):
        return path == key
    if kind.startswith("prefix:"):
        return path.startswith(key)
    return False


def _insert_codemaker_manifest_path(lines: list[str], path: str) -> None:
    """path のカテゴリに応じて適切な marker の手前に挿入する。

    Args:
        lines: 対象の manifest 行リスト（in-place 更新）。
        path: 挿入したい path。

    Policy:
        - カテゴリ判定は _categorize_manifest_path に委譲し、ここでは挿入のみ。
    """
    marker = _categorize_manifest_path(path)
    _manifest_insert_before_marker(lines, path, marker)


def _validate_manifest_inputs(
    repo_root: Path,
    contract: dict[str, Any] | None,
) -> tuple[Path, list[str]] | None:
    """contract から manifest_path / required_paths を取り出し前提条件を検証する。

    Args:
        repo_root: リポジトリのルート Path。
        contract: codemaker contract dict（無ければ None）。

    Returns:
        tuple[Path, list[str]] | None: 検証済みの 2-tuple または None。

    Policy:
        - 前提が崩れていれば早期 None で fixer 側を no-op にする。
    """
    if contract is None:
        return None
    manifest_rel = contract.get("manifest_path")
    required_paths = contract.get("required_paths", [])
    if not _is_nonempty_str(manifest_rel):
        return None
    if not _is_nonempty_list(required_paths):
        return None
    manifest_path = repo_root / manifest_rel
    if not manifest_path.is_file():
        return None
    if not _are_all_required_paths_present(repo_root, required_paths):
        return None
    return manifest_path, list(required_paths)


def _is_nonempty_str(value: Any) -> bool:
    """value が空でない str かを返す述語。

    Args:
        value: 判定対象の任意値。

    Returns:
        bool: str かつ非空なら True。

    Policy:
        - 1 述語に閉じて CR303 を避ける。
    """
    if not isinstance(value, str):
        return False
    return bool(value)


def _is_nonempty_list(value: Any) -> bool:
    """value が空でない list かを返す述語。

    Args:
        value: 判定対象の任意値。

    Returns:
        bool: list かつ非空なら True。

    Policy:
        - 1 述語に閉じて CR303 を避ける。
    """
    if not isinstance(value, list):
        return False
    return bool(value)


def _are_all_required_paths_present(
    repo_root: Path, required_paths: list[str],
) -> bool:
    """required_paths の全 path が repo_root 配下のファイルかを返す述語。

    Args:
        repo_root: リポジトリのルート Path。
        required_paths: 必要 path のリスト。

    Returns:
        bool: 全ファイル存在なら True。

    Policy:
        - 早期 False で短絡する純粋関数。
    """
    for rel_path in required_paths:
        if not (repo_root / rel_path).is_file():
            return False
    return True


def _apply_codemaker_manifest_fix(
    manifest_path: Path, required_paths: list[str],
) -> list[dict[str, Any]]:
    """manifest に不足 path を挿入し、変更があれば書き戻して fix 履歴を返す。

    Args:
        manifest_path: 対象 manifest の Path。
        required_paths: 投入されるべき path 列。

    Returns:
        list[dict[str, Any]]: 挿入した path ごとの fix 説明。

    Policy:
        - 行リスト編集と書き戻しは private helper に分離する。
    """
    lines = _read_manifest_entries_with_lines(manifest_path)
    entries = _manifest_entries(lines)
    fixes: list[dict[str, Any]] = []
    has_change = _insert_missing_manifest_paths(
        lines, entries, required_paths, manifest_path, fixes,
    )
    _write_manifest_lines_if_changed(manifest_path, lines, has_change)
    return fixes


def _insert_missing_manifest_paths(
    lines: list[str],
    entries: set[str],
    required_paths: list[str],
    manifest_path: Path,
    fixes: list[dict[str, Any]],
) -> bool:
    """required_paths の中で entries に無いものを 1 件ずつ挿入する。

    Args:
        lines: manifest 行リスト（in-place 更新）。
        entries: 既存 entry の集合（in-place 更新）。
        required_paths: 投入されるべき path 列。
        manifest_path: 対象 manifest の Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Returns:
        bool: 1 件でも挿入したら True。

    Policy:
        - 1 path 分の挿入は _insert_one_missing_path に委譲し、本体はループだけにする。
    """
    has_change = False
    for rel_path in required_paths:
        if _insert_one_missing_path(
            lines, entries, rel_path, manifest_path, fixes,
        ):
            has_change = True
    return has_change


def _insert_one_missing_path(
    lines: list[str],
    entries: set[str],
    rel_path: str,
    manifest_path: Path,
    fixes: list[dict[str, Any]],
) -> bool:
    """1 つの rel_path が未挿入なら挿入し、fix 履歴を積む。

    Args:
        lines: manifest 行リスト（in-place 更新）。
        entries: 既存 entry の集合（in-place 更新）。
        rel_path: 投入されるべき 1 path。
        manifest_path: 対象 manifest の Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Returns:
        bool: 挿入を実行したら True。

    Policy:
        - 既存 entry なら no-op で False、それ以外は挿入と fix 追加を行う。
    """
    if rel_path in entries:
        return False
    _insert_codemaker_manifest_path(lines, rel_path)
    entries.add(rel_path)
    fixes.append({
        "kind": "code", "path": str(manifest_path),
        "detail": (
            "added missing codemaker manifest path: " + rel_path
        ),
    })
    return True


def _write_manifest_lines_if_changed(
    manifest_path: Path, lines: list[str], has_change: bool,
) -> None:
    """has_change が真のときだけ manifest を書き戻す。

    Args:
        manifest_path: 対象 manifest の Path。
        lines: 書き戻したい行リスト。
        has_change: write 必要性の述語結果。

    Policy:
        - 公開 fixer の本体から `if changed: write` を排除するための糖衣。
    """
    if has_change:
        _write_manifest_lines(manifest_path, lines)


# === Rule meta / tree helpers ===


def _set_rule_internal_fields(
    data: dict[str, Any], rules_path: Path,
) -> None:
    """validation_rules の各 rule に __rules_path を内部フィールドとして注入する。

    Args:
        data: rules YAML 全体を表す dict（in-place 更新）。
        rules_path: 注入したい rules YAML の Path。

    Policy:
        - rule に rules_path を保持させ、後段 helper から元 YAML を辿れるようにする。
    """
    for rule in data.get("validation_rules", []):
        rule["__rules_path"] = str(rules_path)


def _get_expected_source_for_generated_entry(entry_path: str) -> str:
    """generated entry の path から canonical な source 文字列を組む。

    Args:
        entry_path: generated されたファイルの path（例: src/generated/dialogue.py）。

    Returns:
        str: assets/<stem>.yaml の固定形。

    Policy:
        - stem -> assets/<stem>.yaml の 1 対 1 対応を 1 箇所に閉じる。
    """
    stem = Path(entry_path).stem
    return "assets/" + stem + ".yaml"


def _ensure_tree_path_dispatch(
    root: dict[str, Any], path_value: str,
    kind: str, fields: dict[str, Any],
) -> dict[str, Any]:
    """path_value が "." か否かで root / segments ヘルパへ振り分ける。

    Args:
        root: facts.tree の root dict（in-place 更新）。
        path_value: 揃えたい tree 上のパス。
        kind: ノードの種別。
        fields: 最終ノードに反映する field dict。

    Returns:
        dict[str, Any]: 該当ノード dict。

    Policy:
        - 公開 ensure_tree_path のステップ列を維持するため、分岐をここに閉じる。
    """
    if path_value == ".":
        return _ensure_tree_path_root(root, fields)
    return _ensure_tree_path_segments(root, path_value, kind, fields)


def _ensure_tree_path_root(
    root: dict[str, Any], fields: dict[str, Any],
) -> dict[str, Any]:
    """path == "." 時に root へ fields を上書き反映する。

    Args:
        root: facts.tree の root dict（in-place 更新）。
        fields: 上書きする field の dict。

    Returns:
        dict[str, Any]: root 自身。

    Policy:
        - 公開 ensure_tree_path のステップ列を保つため、root ケースだけ切り出す。
    """
    root.update(fields)
    return root


def _ensure_tree_path_segments(
    root: dict[str, Any], path_value: str,
    kind: str, fields: dict[str, Any],
) -> dict[str, Any]:
    """path_value をセグメントごとに辿ってノードを作り、最終ノードを返す。

    Args:
        root: facts.tree の root dict（in-place 更新）。
        path_value: "/" 区切りのパス。
        kind: 最終ノードの種別。
        fields: 最終ノードに反映する field dict。

    Returns:
        dict[str, Any]: 最終セグメントに該当するノード dict。

    Policy:
        - 親ディレクトリが無くても repair が進められるよう上から補完する。
    """
    segments = path_value.split("/")
    current = root
    for index, segment in enumerate(segments):
        current_path = "/".join(segments[: index + 1])
        is_last = index == len(segments) - 1
        wanted_kind = kind if is_last else "directory"
        current = _ensure_child_node(current, current_path, wanted_kind)
    current.update(fields)
    if current.get("kind") != "file":
        current.setdefault("children", [])
    return current


def _ensure_child_node(
    current: dict[str, Any], current_path: str, wanted_kind: str,
) -> dict[str, Any]:
    """current.children から current_path のノードを取り出し、無ければ作る。

    Args:
        current: 親ノード dict。
        current_path: 子ノードの path（root からの絶対パス相当）。
        wanted_kind: 子ノードに付けたい kind。

    Returns:
        dict[str, Any]: 該当する子ノード dict。

    Policy:
        - kind が違う場合は wanted_kind に揃えてから子ノードを返す。
    """
    children = current.setdefault("children", [])
    child = next(
        (item for item in children if item.get("path") == current_path),
        None,
    )
    if child is None:
        child = {"path": current_path, "kind": wanted_kind}
        if wanted_kind != "file":
            child["children"] = []
        children.append(child)
    elif child.get("kind") != wanted_kind:
        child["kind"] = wanted_kind
    return child


# === Runtime entry helpers ===


def _get_existing_node_at(
    nodes: Any, index: int,
) -> dict[str, Any]:
    """nodes リストから index 位置の dict を安全に取り出す。

    Args:
        nodes: 既存 nodes（list を期待するが他型にも備える）。
        index: 取り出したいインデックス。

    Returns:
        dict[str, Any]: 該当 dict、無ければ空 dict。

    Policy:
        - 不正型 / 範囲外を空 dict にフォールバックさせて安全に合成する。
    """
    if not isinstance(nodes, list):
        return {}
    if index >= len(nodes):
        return {}
    candidate = nodes[index]
    if not isinstance(candidate, dict):
        return {}
    return candidate


def _build_merged_runtime_nodes(
    existing_nodes: Any, canonical_nodes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """canonical の各 node を existing で覆い、上書き merge した nodes を返す。

    Args:
        existing_nodes: 既存 nodes（list 以外もあり得る）。
        canonical_nodes: canonical 側 nodes リスト。

    Returns:
        list[dict[str, Any]]: 合成済み nodes。

    Policy:
        - existing 側のメタデータを残しつつ canonical 側を最終 overlay する。
    """
    merged_nodes: list[dict[str, Any]] = []
    for index, canonical_node in enumerate(canonical_nodes):
        existing_node = _get_existing_node_at(existing_nodes, index)
        merged_node = dict(existing_node)
        merged_node.update(canonical_node)
        merged_nodes.append(merged_node)
    return merged_nodes


def _merge_runtime_entry_preserving_extras(
    current_entry: dict[str, Any],
    canonical_entry: dict[str, Any],
) -> dict[str, Any]:
    """current_entry を canonical_entry で overlay しつつ追加メタを保持する。

    Args:
        current_entry: 既存 entry dict。
        canonical_entry: canonical な entry dict。

    Returns:
        dict[str, Any]: 合成済み entry dict。

    Policy:
        - nodes は _build_merged_runtime_nodes に委譲、他 key は canonical で上書き。
    """
    merged_entry = dict(current_entry)
    merged_nodes = _build_merged_runtime_nodes(
        current_entry.get("nodes", []),
        canonical_entry.get("nodes", []),
    )
    for key, value in canonical_entry.items():
        if key == "nodes":
            merged_entry[key] = merged_nodes
            continue
        merged_entry[key] = value
    return merged_entry


_RUNTIME_CANONICAL_ENTRY_CHAIN: list[dict[str, Any]] = [
    {
        "id": "runtime_main_wrapper",
        "path": "main.py",
        "role": "wrapper",
        "status": "active",
        "summary": (
            "src/runtime/main_runtime.py を実行する 8 行 wrapper"
        ),
    },
    {
        "id": "runtime_shim",
        "path": "src/runtime/main_runtime.py",
        "role": "shim",
        "status": "active",
        "summary": (
            "test / Code Maker bundler 互換のための re-export shim"
        ),
    },
    {
        "id": "runtime_game",
        "path": "src/runtime/app.py",
        "symbol": "Game",
        "role": "application_root",
        "status": "active",
        "summary": (
            "pyxel 初期化、DI、scene/service 組み立て、"
            "update/draw dispatcher"
        ),
    },
]


def _build_runtime_canonical_entry_chain() -> list[dict[str, Any]]:
    """runtime entry chain の canonical な node リストを返す。

    Returns:
        list[dict[str, Any]]: wrapper / shim / Game の 3 node。

    Policy:
        - リテラルはモジュール定数に寄せ、関数は dispatch だけに閉じる。
    """
    return list(_RUNTIME_CANONICAL_ENTRY_CHAIN)


def _normalize_runtime_main_wrapper(
    repo_root: Path, fixes: list[dict[str, Any]],
) -> None:
    """main.py wrapper を canonical 形に書き戻す（必要時のみ）。

    Args:
        repo_root: リポジトリのルート Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - 既に canonical なら no-op、差があれば 1 度だけ書き戻す。
    """
    main_path = repo_root / "main.py"
    if not main_path.is_file():
        return
    if main_path.read_text(encoding="utf-8") == CANONICAL_MAIN_WRAPPER:
        return
    main_path.write_text(CANONICAL_MAIN_WRAPPER, encoding="utf-8")
    fixes.append({
        "kind": "code", "path": str(main_path),
        "detail": "normalized runtime main wrapper",
    })


def _normalize_runtime_shim(
    repo_root: Path, fixes: list[dict[str, Any]],
) -> None:
    """runtime shim ファイルの imports と tail を canonical 形に揃える。

    Args:
        repo_root: リポジトリのルート Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - 各補正は private helper に分け、最後に diff があれば 1 度だけ書き戻す。
    """
    shim_path = repo_root / "src" / "runtime" / "main_runtime.py"
    if not shim_path.is_file():
        return
    original = shim_path.read_text(encoding="utf-8")
    text = _ensure_shim_imports(original)
    text = _ensure_shim_tail(text)
    if text == original:
        return
    shim_path.write_text(text, encoding="utf-8")
    fixes.append({
        "kind": "code", "path": str(shim_path),
        "detail": "normalized runtime shim tail",
    })


def _ensure_shim_imports(text: str) -> str:
    """shim の text に必要 import が欠けていれば末尾に追記する。

    Args:
        text: 元の shim ファイル本文。

    Returns:
        str: 必要 import を補った本文。

    Policy:
        - import 行は重複しないようリテラル一致で判定する。
    """
    if "from src.runtime.app import Game" not in text:
        text = (
            text.rstrip()
            + "\nfrom src.runtime.app import Game, say, say_clear\n"
        )
    if "from src.runtime.app import run as _run" not in text:
        text = (
            text.rstrip()
            + "\nfrom src.runtime.app import run as _run\n"
        )
    return text


def _ensure_shim_tail(text: str) -> str:
    """shim の tail（ENTRY POINT セクション）を canonical に差し替える。

    Args:
        text: 元の shim ファイル本文。

    Returns:
        str: tail を canonical 化した本文。マーカ無しなら text そのまま。

    Policy:
        - ENTRY_POINT_MARKER 以前を保ったまま、以降を canonical 文字列で置換する。
    """
    if ENTRY_POINT_MARKER not in text:
        return text
    prefix, _, _ = text.partition(ENTRY_POINT_MARKER)
    return prefix.rstrip() + "\n" + CANONICAL_RUNTIME_TAIL


_RUNTIME_TREE_NODE_SPECS: list[dict[str, Any]] = [
    {
        "path": "main.py",
        "kind": "file",
        "fields": {
            "role": "runtime_wrapper",
            "status": "active",
            "source_of_truth": False,
            "summary": "src/runtime/main_runtime.py を呼ぶ薄い wrapper",
        },
    },
    {
        "path": "src/runtime",
        "kind": "directory",
        "fields": {
            "role": "runtime_container",
            "status": "active",
            "source_of_truth": True,
            "summary": "Pyxel 単一入口の受け皿",
        },
    },
    {
        "path": "src/runtime/main_runtime.py",
        "kind": "file",
        "fields": {
            "role": "shim",
            "status": "active",
            "source_of_truth": False,
            "summary": (
                "test / Code Maker bundler 互換のための re-export shim"
            ),
        },
    },
    {
        "path": "src/runtime/app.py",
        "kind": "file",
        "fields": {
            "role": "application_root",
            "status": "active",
            "source_of_truth": True,
            "symbol": "Game",
            "summary": (
                "pyxel 初期化、DI、scene/service 組み立て、"
                "update/draw dispatcher"
            ),
        },
    },
]


def _ensure_runtime_tree_nodes(tree: dict[str, Any]) -> None:
    """runtime 系 4 path を facts.tree に補完する。

    Args:
        tree: facts.tree の root dict（in-place 更新）。

    Policy:
        - spec はモジュール定数に寄せ、関数はループだけに閉じる。
    """
    for spec in _RUNTIME_TREE_NODE_SPECS:
        ensure_tree_path(
            tree, spec["path"], spec["kind"], **spec["fields"],
        )


def _has_existing_runtime_entry(
    entry_points: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """facts.entry_points から runtime_entry_chain を取り出す。

    Args:
        entry_points: facts.entry_points のリスト。

    Returns:
        dict[str, Any] | None: 該当 entry、無ければ None。

    Policy:
        - 単純 lookup を 1 関数に閉じ、戻り値の type を呼び出し側で扱いやすくする。
    """
    return next(
        (
            item for item in entry_points
            if item.get("id") == "runtime_entry_chain"
        ),
        None,
    )


def _normalize_runtime_entry_points(data: dict[str, Any]) -> bool:
    """facts.entry_points の runtime_entry_chain を canonical 化し変更有無を返す。

    Args:
        data: rules YAML 全体を表す dict（in-place 更新）。

    Returns:
        bool: yaml に差分が出たら True。

    Policy:
        - 既存 entry の有無で append / merge を private helper に振り分ける。
    """
    entry_points = data.setdefault("facts", {}).setdefault(
        "entry_points", [],
    )
    canonical_entry = _build_canonical_runtime_entry()
    current_entry = _has_existing_runtime_entry(entry_points)
    if current_entry is None:
        entry_points.append(canonical_entry)
        return True
    return _update_runtime_entry_if_diff(current_entry, canonical_entry)


def _build_canonical_runtime_entry() -> dict[str, Any]:
    """runtime_entry_chain の canonical な entry dict を組み立てる。

    Returns:
        dict[str, Any]: id / summary / paths / nodes を持つ canonical entry。

    Policy:
        - chain ノード列は _build_runtime_canonical_entry_chain に閉じる。
    """
    chain = _build_runtime_canonical_entry_chain()
    return {
        "id": "runtime_entry_chain",
        "summary": (
            "runtime の入口は wrapper -> shim -> Game の流れを保つ"
        ),
        "paths": [item["path"] for item in chain],
        "nodes": chain,
    }


def _update_runtime_entry_if_diff(
    current_entry: dict[str, Any],
    canonical_entry: dict[str, Any],
) -> bool:
    """current と canonical を merge し、差があれば current を上書きする。

    Args:
        current_entry: 既存の entry dict（in-place 更新）。
        canonical_entry: canonical な entry dict。

    Returns:
        bool: 差分があり current を更新したら True。

    Policy:
        - merge は _merge_runtime_entry_preserving_extras に委譲する。
    """
    merged_entry = _merge_runtime_entry_preserving_extras(
        current_entry, canonical_entry,
    )
    if current_entry == merged_entry:
        return False
    current_entry.clear()
    current_entry.update(merged_entry)
    return True


# === Generated rule helpers ===


def _apply_generated_files_fix(
    repo_root: Path,
    rules_path: Path,
    fixes: list[dict[str, Any]],
) -> None:
    """generated rule の facts 補正と再生成を一括で実行する。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - 「facts 正規化 -> write -> gen_data」のステップ列を 1 関数に閉じる。
    """
    data = load_yaml(rules_path)
    entries = check_architecture_rules.generated_file_nodes(data)
    has_yaml_change = _normalize_generated_entries(entries, rules_path, fixes)
    _write_yaml_if_changed(rules_path, data, has_yaml_change)
    _run_gen_data_if_present(repo_root, fixes)


def _normalize_generated_entries(
    entries: list[dict[str, Any]],
    rules_path: Path,
    fixes: list[dict[str, Any]],
) -> bool:
    """generated entries 全体を順に canonical 化し、変更有無を返す。

    Args:
        entries: facts.tree から抽出した generated エントリの列。
        rules_path: rules YAML の Path（fix 記録用）。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Returns:
        bool: いずれかの entry を更新したら True。

    Policy:
        - bool フラグの累積を any() に置換して CR101 を回避する。
    """
    return any(
        _normalize_generated_entry(entry, rules_path, fixes)
        for entry in entries
    )


def _write_yaml_if_changed(
    rules_path: Path, data: dict[str, Any], has_change: bool,
) -> None:
    """has_change が真のときだけ data を rules_path に書き戻す。

    Args:
        rules_path: rules YAML の Path。
        data: rules YAML 全体を表す dict。
        has_change: write 必要性の述語結果。

    Policy:
        - 公開 fixer の本体から `if changed: write_yaml` を排除するための糖衣。
    """
    if has_change:
        write_yaml(rules_path, data)


def _normalize_generated_entry(
    entry: dict[str, Any],
    rules_path: Path,
    fixes: list[dict[str, Any]],
) -> bool:
    """1 つの generated entry を facts 側で canonical 形に揃える。

    Args:
        entry: facts.tree 内の generated エントリ dict（in-place 更新）。
        rules_path: rules YAML の Path（fix 記録用）。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Returns:
        bool: entry を更新したら True。

    Policy:
        - hand_editable / generated_from の検査を private helper に分割する。
    """
    has_hand_editable_change = _normalize_hand_editable_field(
        entry, rules_path, fixes,
    )
    has_generated_from_change = _normalize_generated_from_field(
        entry, rules_path, fixes,
    )
    return has_hand_editable_change or has_generated_from_change


def _normalize_hand_editable_field(
    entry: dict[str, Any],
    rules_path: Path,
    fixes: list[dict[str, Any]],
) -> bool:
    """entry.hand_editable を False に揃え、変更時に fix を積む。

    Args:
        entry: generated エントリ dict（in-place 更新）。
        rules_path: rules YAML の Path（fix 記録用）。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Returns:
        bool: 値を書き換えたら True。

    Policy:
        - 既に False ならスキップ、それ以外は False で上書きする。
    """
    if entry.get("hand_editable") is False:
        return False
    entry["hand_editable"] = False
    fixes.append({
        "kind": "yaml", "path": str(rules_path),
        "detail": (
            "set hand_editable false for " + str(entry.get("id"))
        ),
    })
    return True


def _normalize_generated_from_field(
    entry: dict[str, Any],
    rules_path: Path,
    fixes: list[dict[str, Any]],
) -> bool:
    """entry.generated_from を canonical な 1 要素 list に揃える。

    Args:
        entry: generated エントリ dict（in-place 更新）。
        rules_path: rules YAML の Path（fix 記録用）。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Returns:
        bool: 値を書き換えたら True。

    Policy:
        - 期待値は _get_expected_source_for_generated_entry が一意に決める。
    """
    expected_source = _get_expected_source_for_generated_entry(entry["path"])
    generated_from = list(entry.get("generated_from", []))
    if generated_from == [expected_source]:
        return False
    entry["generated_from"] = [expected_source]
    fixes.append({
        "kind": "yaml", "path": str(rules_path),
        "detail": (
            "normalized generated_from for " + str(entry.get("id"))
        ),
    })
    return True


def _run_gen_data_if_present(
    repo_root: Path, fixes: list[dict[str, Any]],
) -> None:
    """tools/gen_data.py が存在する場合だけ実行し、fix 履歴に積む。

    Args:
        repo_root: リポジトリのルート Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - 不在ならスキップし、存在時は同期実行で再生成を強制する。
    """
    gen_script = repo_root / "tools" / "gen_data.py"
    if not gen_script.is_file():
        return
    subprocess.run(
        [sys.executable, str(gen_script)],
        cwd=repo_root, check=True,
    )
    fixes.append({
        "kind": "command", "path": str(gen_script),
        "detail": "ran gen_data.py",
    })


def _run_build_web_release_if_present(
    repo_root: Path,
    fixes: list[dict[str, Any]],
    *,
    detail: str,
) -> None:
    """tools/build_web_release.py が存在する場合だけ実行し、fix 履歴に積む。

    Args:
        repo_root: リポジトリのルート Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。
        detail: fix dict に詰める detail 文字列。

    Policy:
        - dist / release rule のどちらでも使うため detail を呼び出し側で渡す。
    """
    build_script = repo_root / "tools" / "build_web_release.py"
    if not build_script.is_file():
        return
    subprocess.run(
        [sys.executable, str(build_script)],
        cwd=repo_root, check=True,
    )
    fixes.append({
        "kind": "command", "path": str(build_script),
        "detail": detail,
    })


# === Build runbook helpers ===


_RELEASE_ARTIFACT_SPECS: list[dict[str, str]] = [
    {
        "id": "codemaker_zip",
        "path": "dist/code-maker.zip",
        "status": "distribution",
        "summary": (
            "block-quest/main.py + my_resource.pyxres を梱包した"
            "教材版 zip"
        ),
    },
    {
        "id": "pyxel_html",
        "path": "dist/pyxel.html",
        "status": "distribution",
        "summary": "Web 配布用 HTML",
    },
    {
        "id": "pyxel_pyxapp",
        "path": "dist/pyxel.pyxapp",
        "status": "distribution",
        "summary": "Pyxel app 配布物",
    },
    {
        "id": "play_html",
        "path": "dist/play.html",
        "status": "distribution",
        "summary": "プレイページ",
    },
    {
        "id": "top_index_html",
        "path": "dist/index.html",
        "status": "distribution",
        "summary": "play.html と同内容の wrapper alias",
    },
]


def _build_release_artifact_specs() -> list[dict[str, str]]:
    """release artifact の canonical spec リストを返す。

    Returns:
        list[dict[str, str]]: id / path / status / summary を持つ dict の列。

    Policy:
        - リテラルはモジュール定数に寄せ、関数は copy だけに閉じる。
    """
    return list(_RELEASE_ARTIFACT_SPECS)


def _ensure_dist_artifact_nodes(
    tree: dict[str, Any],
    artifacts: list[dict[str, str]],
) -> None:
    """artifacts の各 path を facts.tree に file ノードとして補完する。

    Args:
        tree: facts.tree の root dict（in-place 更新）。
        artifacts: _build_release_artifact_specs() の戻り値。

    Policy:
        - 並列 ensure_tree_path 呼び出しを 1 ループにまとめて読みやすくする。
    """
    for artifact in artifacts:
        ensure_tree_path(
            tree, artifact["path"], "file",
            id=artifact["id"],
            status=artifact["status"],
            summary=artifact["summary"],
        )


def _normalize_codemaker_zip_runbook(runbook: dict[str, Any]) -> None:
    """codemaker_zip runbook の command / outputs を canonical に揃える。

    Args:
        runbook: 対象 runbook dict（in-place 更新）。

    Policy:
        - 既存 step を尊重しつつ command / outputs だけ canonical で上書き。
    """
    step = runbook.setdefault("steps", [{}])[0]
    if step.get("command") != "python tools/build_codemaker.py":
        step["command"] = "python tools/build_codemaker.py"
    if step.get("outputs") != ["dist/code-maker.zip"]:
        step["outputs"] = ["dist/code-maker.zip"]


def _normalize_release_runbook(
    runbook: dict[str, Any],
    artifacts: list[dict[str, str]],
) -> None:
    """build_all_release_artifacts runbook を canonical に揃える。

    Args:
        runbook: 対象 runbook dict（in-place 更新）。
        artifacts: dist artifact の spec リスト。

    Policy:
        - outputs の正解は artifacts.path をそのまま列にしたもの。
    """
    step = runbook.setdefault("steps", [{}])[0]
    desired_outputs = [item["path"] for item in artifacts]
    if step.get("command") != "python tools/build_web_release.py":
        step["command"] = "python tools/build_web_release.py"
    if step.get("outputs") != desired_outputs:
        step["outputs"] = desired_outputs


def _normalize_release_runbooks(
    data: dict[str, Any],
    artifacts: list[dict[str, str]],
) -> None:
    """facts.runbooks の build 系 runbook を id ごとに canonical に揃える。

    Args:
        data: rules YAML 全体を表す dict（in-place 更新）。
        artifacts: dist artifact の spec リスト。

    Policy:
        - id 判定はここで集中させ、個別 normalize は private helper に委ねる。
    """
    runbooks = data.setdefault("facts", {}).setdefault("runbooks", [])
    for runbook in runbooks:
        _dispatch_release_runbook(runbook, artifacts)


def _dispatch_release_runbook(
    runbook: dict[str, Any],
    artifacts: list[dict[str, str]],
) -> None:
    """1 つの runbook を id に応じた canonical 化 helper へ振り分ける。

    Args:
        runbook: 対象 runbook dict（in-place 更新）。
        artifacts: dist artifact の spec リスト。

    Policy:
        - id ごとの分岐は早期 return で並列に保ち、bool 累積は使わない。
    """
    if runbook.get("id") == "build_codemaker_zip":
        _normalize_codemaker_zip_runbook(runbook)
        return
    if runbook.get("id") == "build_all_release_artifacts":
        _normalize_release_runbook(runbook, artifacts)


# === Fix orchestration helpers ===


def _apply_dist_not_source_fix(
    repo_root: Path,
    rules_path: Path,
    fixes: list[dict[str, Any]],
) -> None:
    """dist rule 用の副作用本体を 1 関数にまとめる。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - tree 正規化と build 再実行を private helper に振り分ける。
    """
    data = load_yaml(rules_path)
    _normalize_dist_root_node(data, rules_path, fixes)
    _run_build_web_release_if_present(
        repo_root, fixes, detail="rebuilt dist artifacts",
    )
    write_yaml(rules_path, data)


def _normalize_dist_root_node(
    data: dict[str, Any],
    rules_path: Path,
    fixes: list[dict[str, Any]],
) -> None:
    """facts.tree の dist ディレクトリノードを canonical に揃える。

    Args:
        data: rules YAML 全体を表す dict（in-place 更新）。
        rules_path: rules YAML の Path（fix 記録用）。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - 公開 fixer から tree 操作の塊を切り出して 20 行制限を守る。
    """
    tree = data.setdefault("facts", {}).setdefault(
        "tree", {"path": ".", "kind": "root", "children": []},
    )
    ensure_tree_path(
        tree, "dist", "directory",
        role="distribution_root", status="distribution",
        source_of_truth=False,
        summary="承認済み配布物の出力先",
    )
    fixes.append({
        "kind": "yaml", "path": str(rules_path),
        "detail": "normalized dist root node",
    })


def _apply_build_runbook_paths_fix(
    repo_root: Path,
    rules_path: Path,
    fixes: list[dict[str, Any]],
) -> None:
    """build runbook rule 用の副作用本体を 1 関数にまとめる。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - artifact 補完 / runbook 正規化 / 書き戻し / build を private に分割する。
    """
    data = load_yaml(rules_path)
    artifacts = _build_release_artifact_specs()
    _normalize_build_artifact_tree(data, rules_path, artifacts, fixes)
    _normalize_release_runbooks(data, artifacts)
    write_yaml(rules_path, data)
    fixes.append({
        "kind": "yaml", "path": str(rules_path),
        "detail": "normalized runbook outputs",
    })
    _run_build_web_release_if_present(
        repo_root, fixes, detail="rebuilt release artifacts",
    )


def _normalize_build_artifact_tree(
    data: dict[str, Any],
    rules_path: Path,
    artifacts: list[dict[str, str]],
    fixes: list[dict[str, Any]],
) -> None:
    """facts.tree に artifact ノードを補完し、fix 履歴に 1 件積む。

    Args:
        data: rules YAML 全体を表す dict（in-place 更新）。
        rules_path: rules YAML の Path（fix 記録用）。
        artifacts: dist artifact の spec リスト。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - 公開 fixer 本体から tree 操作の塊を切り出して 20 行制限を守る。
    """
    tree = data.setdefault("facts", {}).setdefault(
        "tree", {"path": ".", "kind": "root", "children": []},
    )
    _ensure_dist_artifact_nodes(tree, artifacts)
    fixes.append({
        "kind": "yaml", "path": str(rules_path),
        "detail": "normalized distribution artifact nodes",
    })


def _run_codemaker_manifest_fix(
    repo_root: Path,
    rules_path: Path,
) -> list[dict[str, Any]]:
    """codemaker manifest rule の前提検証と本体実行をステップ列で行う。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。

    Returns:
        list[dict[str, Any]]: 適用した fix の説明リスト。

    Policy:
        - 前提 None を early-return、合致時は _apply_codemaker_manifest_fix へ。
    """
    data = load_yaml(rules_path)
    contract = _find_codemaker_bundle_contract(
        data, "codemaker_non_scene_bundle",
    )
    inputs = _validate_manifest_inputs(repo_root, contract)
    if inputs is None:
        return []
    return _apply_codemaker_manifest_fix(*inputs)


def _apply_runtime_entry_chain_fix(
    repo_root: Path,
    rules_path: Path,
    fixes: list[dict[str, Any]],
) -> None:
    """runtime entry chain rule の副作用本体を 1 関数にまとめる。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: rules YAML の Path。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - code / tree / entry_points の正規化を 3 つの private helper に委ねる。
    """
    data = load_yaml(rules_path)
    _normalize_runtime_main_wrapper(repo_root, fixes)
    _normalize_runtime_shim(repo_root, fixes)
    tree = data.setdefault("facts", {}).setdefault(
        "tree", {"path": ".", "kind": "root", "children": []},
    )
    _ensure_runtime_tree_nodes(tree)
    has_yaml_change = _normalize_runtime_entry_points(data)
    _persist_runtime_entry_chain_yaml(
        rules_path, data, has_yaml_change, fixes,
    )


def _persist_runtime_entry_chain_yaml(
    rules_path: Path,
    data: dict[str, Any],
    has_yaml_change: bool,
    fixes: list[dict[str, Any]],
) -> None:
    """has_yaml_change が真のときだけ書き戻し、fix を 1 件積む。

    Args:
        rules_path: rules YAML の Path。
        data: rules YAML 全体を表す dict。
        has_yaml_change: write 必要性の述語結果。
        fixes: 適用 fix の累積リスト（in-place 更新）。

    Policy:
        - public fixer の本体から `if changed: ...` を排除するための糖衣。
    """
    if not has_yaml_change:
        return
    write_yaml(rules_path, data)
    fixes.append({
        "kind": "yaml", "path": str(rules_path),
        "detail": (
            "normalized runtime entry tree nodes and entry_points"
        ),
    })


# === run_fixer helpers ===


def _run_fixer_guarded(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None,
    check: dict[str, Any] | None,
) -> dict[str, Any]:
    """run_fixer の try/except 外殻を担う private 委譲。

    Args:
        repo_root: 解決済みのリポジトリルート。
        rules_path: 解決済みの rules YAML パス。
        rule_ids: 対象 rule の絞り込み（None なら全 rule）。
        check: 直近の checker 結果（未指定なら走らせて取得する）。

    Returns:
        dict[str, Any]: run_fixer と同形式の戻り値。

    Policy:
        - 例外捕捉のみここに残し、本体は _run_fixer_body に閉じる。
    """
    try:
        return _run_fixer_body(
            repo_root, rules_path,
            rule_ids=rule_ids, check=check,
        )
    except Exception as exc:
        return _build_run_fixer_error_payload(check, exc)


def _run_fixer_body(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None,
    check: dict[str, Any] | None,
) -> dict[str, Any]:
    """run_fixer の正常系本体を担う private 委譲。

    Args:
        repo_root: 解決済みのリポジトリルート。
        rules_path: 解決済みの rules YAML パス。
        rule_ids: 対象 rule の絞り込み（None なら全 rule）。
        check: 直近の checker 結果（未指定なら走らせて取得する）。

    Returns:
        dict[str, Any]: run_fixer と同形式の戻り値。

    Policy:
        - clean 経路と FIXED/NEEDS_HUMAN 経路を early-return で並列に保つ。
    """
    current_check = _resolve_check(repo_root, rules_path, rule_ids, check)
    if not _has_pending_warnings(current_check):
        return _build_run_fixer_payload("OK", current_check, [])
    applied_fixes = _apply_registered_fixers(
        repo_root, rules_path, current_check,
    )
    status = "FIXED" if applied_fixes else "NEEDS_HUMAN"
    return _build_run_fixer_payload(status, current_check, applied_fixes)


def _resolve_check(
    repo_root: Path,
    rules_path: Path,
    rule_ids: set[str] | None,
    check: dict[str, Any] | None,
) -> dict[str, Any]:
    """既存 check があればそれを返し、無ければ checker を 1 度走らせる。

    Args:
        repo_root: 解決済みのリポジトリルート。
        rules_path: 解決済みの rules YAML パス。
        rule_ids: 対象 rule の絞り込み（None なら全 rule）。
        check: 直近の checker 結果（None なら走らせる）。

    Returns:
        dict[str, Any]: checker 結果 dict。

    Policy:
        - bool or を関数本体から排除し、CR101 を構造的に避ける。
    """
    if check is not None:
        return check
    return check_architecture_rules.run_checker(
        repo_root, rules_path, rule_ids=rule_ids,
    )


def _has_pending_warnings(check_result: dict[str, Any]) -> bool:
    """checker 結果に未解消 warning が残っているかを返す述語。

    Args:
        check_result: checker の戻り値 dict。

    Returns:
        bool: has_warnings が真なら True。

    Policy:
        - run_fixer のステップ列で「先に進むか」を 1 行で判定するために切り出す。
    """
    return bool(check_result.get("has_warnings"))


def _apply_registered_fixers(
    repo_root: Path,
    rules_path: Path,
    check_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """FIXER_REGISTRY に登録された rule の warning に fixer を順に当てる。

    Args:
        repo_root: 解決済みのリポジトリルート。
        rules_path: 解決済みの rules YAML パス。
        check_result: 直近の checker 結果。

    Returns:
        list[dict[str, Any]]: 適用 fix の累積。

    Policy:
        - 未登録 rule は silent success にせず scan を継続するだけにする。
    """
    warnings = [
        item for item in check_result["results"]
        if item["status"] == "warning"
    ]
    applied_fixes: list[dict[str, Any]] = []
    for warning in warnings:
        fixer = FIXER_REGISTRY.get(warning["rule_id"])
        if fixer is None:
            continue
        fixes = fixer(repo_root, rules_path, warning)
        if fixes:
            applied_fixes.extend(fixes)
    return applied_fixes


def _build_run_fixer_payload(
    status: str,
    check_result: dict[str, Any],
    applied_fixes: list[dict[str, Any]],
) -> dict[str, Any]:
    """run_fixer の通常パス戻り値を組み立てる純粋関数。

    Args:
        status: "OK" / "FIXED" / "NEEDS_HUMAN" のいずれか。
        check_result: 直近の checker 結果。
        applied_fixes: 適用 fix のリスト。

    Returns:
        dict[str, Any]: run_fixer の戻り値形式。

    Policy:
        - 戻り値の構造を 1 箇所に集約して呼び出し側を簡潔に保つ。
    """
    return {
        "status": status,
        "check": check_result,
        "applied_fixes": applied_fixes,
    }


def _build_run_fixer_error_payload(
    check_result: dict[str, Any] | None,
    exc: Exception,
) -> dict[str, Any]:
    """run_fixer 例外パスの戻り値を組み立てる純粋関数。

    Args:
        check_result: 直近の checker 結果（None もあり得る）。
        exc: 捕捉した例外。

    Returns:
        dict[str, Any]: status="ERROR" の戻り値。

    Policy:
        - exception の str 表現だけを露出し、トレースは呼び出し側に任せる。
    """
    return {
        "status": "ERROR",
        "check": check_result,
        "applied_fixes": [],
        "error": str(exc),
    }


# === CLI helpers ===


def _build_fix_arg_parser() -> argparse.ArgumentParser:
    """fix CLI 用 argparse.ArgumentParser を組み立てる。

    Returns:
        argparse.ArgumentParser: 3 つの引数を受ける parser。

    Policy:
        - 既存 CLI の引数定義を 1 関数に閉じ、main から呼び出すだけにする。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=ROOT / "docs" / "architecture_rules.yml",
    )
    parser.add_argument("--rule-id", action="append", default=[])
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
