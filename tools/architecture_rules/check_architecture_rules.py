"""architecture_rules.yml の deterministic rule を warning 形式で検証する CLI。

- CheckContext / CheckOutcome: rule 走行の入力束と結果束を定義する dataclass。
- load_rules: YAML を読み込み、骨格スキーマを検証して dict を返す。
- validate_rules_schema: rule 単位の必須キーと値域を検査する。
- iter_tree_nodes / find_tree_node: facts.tree を再帰探索する helper。
- find_entry_point / find_codemaker_bundle_contract: facts 内 id 引きを行う。
- generated_file_nodes / distribution_artifact_nodes: 既知の facts 部分木を抜き出す。
- scene_static_boundary_checks: scene 配下の構造と pyxel/input 境界を点検する。
- shared_directory_role_checks: shared/services と shared/state の role を点検する。
- wrapper_chain_present: runtime の入口チェーンが facts と一致するかを点検する。
- distribution_paths_marked_non_source: dist 配下が非ソースに揃っているかを点検する。
- generated_entries_mark_non_hand_editable_and_sources:
  generated/* の facts を点検する。
- codemaker_manifest_includes_required_paths: codemaker bundle manifest を点検する。
- compare_runbook_commands_and_artifact_defs: runbook と artifact の対応を点検する。
- run_deterministic_rule / run_checker: rule 走行と CLI 入口の本体。
- build_coverage_review / build_output: 結果の集計と JSON 整形を行う。
- result_record: 1 rule ぶんの結果 dict を組み立てる。
- main: argparse 経由の CLI エントリ。

Problems:
    - architecture_rules.yml の rule 増減に対し、手動レビューだけでは
      deterministic に書ける rule を見落とし、CI が壊れた時に何が違反かが
      JSON で取り出せない。
    - 各 rule の checker が散在し、共通の warning 形式や coverage 集計を
      取りまとめる入口が無いと、結果を機械処理で受けられない。

Solutions:
    - YAML を入口で schema 検証し、deterministic rule だけ個別 checker に
      委譲して `warning / ok / skipped` の 3 値で JSON を返す。
    - CHECK_REGISTRY 経由で rule.evidence.checks から関数を解決し、
      新しい deterministic rule を追加する際の登録点を 1 箇所に集める。
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
VALID_DETERMINISTIC_REVIEWS = {
    "implemented",
    "candidate",
    "keep_llm_assisted",
    "keep_manual",
}
VALID_REPAIR_AUTOFIX = {
    "implemented",
    "candidate",
    "not_recommended",
}
PRIMARY_AUTOFIX_KEY = "guardian_autofix"
LEGACY_AUTOFIX_KEYS = (PRIMARY_AUTOFIX_KEY, "repair_autofix")

SCENE_ALLOWED_FILES = {
    "__init__.py",
    "scene.py",
    "model.py",
    "presenter.py",
    "view.py",
    "view_model.py",
}
SCENE_DRAW_CALL = re.compile(
    r"(?:^|[^_a-zA-Z])pyxel\."
    r"(blt|bltm|text|line|rect|rectb|circ|circb"
    r"|cls|pset|tri|trib|clip|camera)\b"
)
SCENE_INPUT_CALL = re.compile(
    r"(pyxel\.btnp|pyxel\.btn[^_]"
    r"|input_state\.btnp|input_state\.btn[^_])"
)
PYXEL_ANY_CALL = re.compile(r"(?:^|[^_a-zA-Z])pyxel\.")
PLAYER_STATE_IMPORT = re.compile(
    r"from\s+src\.shared\.services\.player_state\s+import"
    r"|import\s+src\.shared\.services\.player_state"
)
ITEM_USE_IMPORT = re.compile(
    r"from\s+src\.shared\.services\.item_use\s+import"
    r"|import\s+src\.shared\.services\.item_use"
)
SHARED_SERVICE_PYXEL_EXEMPT = {"audio_system.py", "image_banks.py"}

REQUIRED_RULE_KEYS = {
    "id",
    "summary",
    "severity",
    "enforcement",
    "scope",
    "evidence",
    "message",
    "suggested_actions",
    "coverage",
}
REQUIRED_COVERAGE_KEYS = (
    "deterministic_review",
    "next_checker_unit",
    "rationale",
)


@dataclass
class CheckContext:
    """rule 走行に共通で渡す入力束。

    Policy:
        - repo_root と rules_path は resolve 済みの絶対パスにする。
    """

    # === Public API ===

    repo_root: Path
    rules_path: Path
    data: dict[str, Any]


@dataclass
class CheckOutcome:
    """1 つの check 関数の結果束。

    Policy:
        - status は ok/warning/skipped/error のいずれか。
        - failed_checks は最初の警告だけを 1 件入れる運用にする。
    """

    # === Public API ===

    status: str
    checked_paths: list[str]
    failed_checks: list[str] = field(default_factory=list)
    message: str | None = None
    suggested_actions: list[str] = field(default_factory=list)
    reason: str | None = None
    expected: dict[str, Any] | None = None
    observed: dict[str, Any] | None = None


# === Public API ===


def load_rules(path: Path) -> dict[str, Any]:
    """architecture_rules.yml を読み込み、骨格を検証して返す。

    Args:
        path: YAML ファイルへの絶対 / 相対パス。

    Returns:
        dict[str, Any]: 検証済みの rules dict。

    Policy:
        - 入口で YAML の骨格を先に落として異常系を早期に止める。
        - 個別 rule の検査は validate_rules_schema に委譲する。
    """
    data = _read_rules_yaml(path)
    validate_rules_schema(data)
    return data


def validate_rules_schema(data: dict[str, Any]) -> None:
    """rules YAML の必須キーと値域を検証する。

    Args:
        data: load_rules 経由でパース済みの dict。

    Raises:
        KeyError: 必須キーが欠けている場合。
        TypeError: 型が想定外の場合。
        ValueError: 値が想定外の場合。

    Policy:
        - tree / contracts / rule の 3 系列を順に検査する。
    """
    _validate_tree_root(data)
    _validate_contracts(data)
    _validate_rules_list(data)


def iter_tree_nodes(node: dict[str, Any]):
    """facts.tree のノードを深さ優先で yield する。

    Args:
        node: 起点となる tree ノード。

    Returns:
        Generator: 自分自身と全 children を順に返す generator。

    Policy:
        - 呼び出し側で順序に依存する場合に備え、自身を先に返す。
    """
    return _iter_tree_nodes_impl(node)


def find_tree_node(
    data: dict[str, Any],
    path_value: str,
) -> dict[str, Any] | None:
    """指定 path の tree ノードを 1 件取得する。

    Args:
        data: rules YAML の dict。
        path_value: 探したいノードの path 文字列。

    Returns:
        dict[str, Any] | None: 見つかったノード。無ければ None。

    Policy:
        - 最初に一致したノードのみを返す。
    """
    return _find_tree_node_impl(data, path_value)


def find_entry_point(
    data: dict[str, Any],
    entry_id: str,
) -> dict[str, Any] | None:
    """facts.entry_points から id 一致の dict を返す。

    Args:
        data: rules YAML の dict。
        entry_id: 探したい entry の id。

    Returns:
        dict[str, Any] | None: 見つかった entry。無ければ None。

    Policy:
        - 1 件目を優先し、重複は呼び出し側で別途検査する想定。
    """
    return _find_entry_point_impl(data, entry_id)


def generated_file_nodes(  # noqa: CR100
    data: dict[str, Any],
) -> list[dict[str, Any]]:
    """src/generated/ 配下の file ノード列を返す。

    Args:
        data: rules YAML の dict。

    Returns:
        list[dict[str, Any]]: src/generated/ 直下と再帰の file ノード列。

    Policy:
        - kind == "file" かつ path が src/generated/ で始まるノードに限定する。
    """
    return _generated_file_nodes_impl(data)


def distribution_artifact_nodes(  # noqa: CR100
    data: dict[str, Any],
) -> list[dict[str, Any]]:
    """dist 配下の artifact file ノード列を返す。

    Args:
        data: rules YAML の dict。

    Returns:
        list[dict[str, Any]]: dist 直下の file ノード列。

    Policy:
        - dist ノードが見つからないときは空リストを返す。
    """
    return _distribution_artifact_nodes_impl(data)


def find_codemaker_bundle_contract(
    data: dict[str, Any],
    contract_id: str,
) -> dict[str, Any] | None:
    """codemaker_bundle_contracts から id 一致の contract を返す。

    Args:
        data: rules YAML の dict。
        contract_id: 探したい contract の id。

    Returns:
        dict[str, Any] | None: 見つかった contract。無ければ None。

    Policy:
        - facts.codemaker_bundle_contracts が無いときも None を返す。
    """
    return _find_codemaker_bundle_contract_impl(data, contract_id)


def scene_static_boundary_checks(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """scene 配下の構造と pyxel/input 境界を点検する。

    Args:
        context: CheckContext。
        rule: 検査対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - 構造違反 → 描画違反 → 入力違反の順で短絡する。
    """
    return _scene_static_boundary_checks_impl(context, rule)


def shared_directory_role_checks(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """shared/services と shared/state の role 整合を点検する。

    Args:
        context: CheckContext。
        rule: 検査対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - facts 上の role を先に見てから grep の二重確認に進む。
    """
    return _shared_directory_role_checks_impl(context, rule)


def wrapper_chain_present(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """runtime の入口チェーンが facts と実コードで一致するかを点検する。

    Args:
        context: CheckContext。
        rule: 検査対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - facts 経路と実ファイルの両方を見て初めて ok とする。
    """
    return _wrapper_chain_present_impl(context, rule)


def distribution_paths_marked_non_source(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """dist 配下が非ソースに揃っているかを点検する。

    Args:
        context: CheckContext。
        rule: 検査対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - facts.tree 上の status / source_of_truth を主に見る。
    """
    return _distribution_paths_marked_non_source_impl(context, rule)


def generated_entries_mark_non_hand_editable_and_sources(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """generated/* の facts と実ファイルの整合を点検する。

    Args:
        context: CheckContext。
        rule: 検査対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - hand_editable と generated_from の prefix を厳密に検査する。
    """
    return _generated_entries_check_impl(context, rule)


def codemaker_manifest_includes_required_paths(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """codemaker bundle manifest と contract の対応を点検する。

    Args:
        context: CheckContext。
        rule: 検査対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - 1 contract id（codemaker_non_scene_bundle）に固定して検査する。
    """
    return _codemaker_manifest_check_impl(context, rule)


def compare_runbook_commands_and_artifact_defs(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """runbook と artifact 定義の対応を点検する。

    Args:
        context: CheckContext。
        rule: 検査対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - 各 step の command と outputs を artifact_paths と照合する。
    """
    return _compare_runbook_commands_impl(context, rule)


def run_deterministic_rule(
    context: CheckContext,
    rule: dict[str, Any],
) -> dict[str, Any]:
    """1 つの deterministic rule を走らせて結果 dict を返す。

    Args:
        context: CheckContext。
        rule: 検査対象 rule。

    Returns:
        dict[str, Any]: result_record と同じ形の dict。

    Raises:
        KeyError: evidence.checks が空 / 未登録 check 名のとき。

    Policy:
        - 最初に ok 以外を返した check で短絡する。
    """
    return _run_deterministic_rule_impl(context, rule)


def result_record(
    rule: dict[str, Any],
    outcome: CheckOutcome,
) -> dict[str, Any]:
    """rule と outcome から 1 件分の結果 dict を組み立てる。

    Args:
        rule: 対象 rule。
        outcome: rule 走行で得た CheckOutcome。

    Returns:
        dict[str, Any]: rule_id を含む結果 dict。

    Policy:
        - JSON 出力でそのまま扱える素朴な dict に揃える。
    """
    return _result_record_impl(rule, outcome)


def build_coverage_review(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """rule 群の自動化レビュー結果を組み立てる。

    Args:
        results: 各 rule の結果 dict 列。

    Returns:
        dict[str, Any]: mode 集計と autofix 状況をまとめた dict。

    Policy:
        - 検査結果の要約ではなく、自動化棚卸しのメタレポートを返す。
    """
    return _build_coverage_review_impl(results)


def build_output(results: list[dict[str, Any]]) -> dict[str, Any]:
    """全 rule の結果から JSON 出力 dict を組み立てる。

    Args:
        results: 各 rule の結果 dict 列。

    Returns:
        dict[str, Any]: CLI 出力に使う最終 dict。

    Policy:
        - summary と coverage_review を必ず同梱する。
    """
    return _build_output_impl(results)


def run_checker(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    """CLI 用のメイン処理。rules を走らせて output dict を返す。

    Args:
        repo_root: リポジトリルート。
        rules_path: rules YAML へのパス。
        rule_ids: 走らせたい rule id の集合。None なら全件。

    Returns:
        dict[str, Any]: build_output 形式の dict。

    Policy:
        - 非 deterministic は skipped で残し、coverage_review で集計可能にする。
    """
    return _run_checker_impl(repo_root, rules_path, rule_ids=rule_ids)


def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """argparse 経由の CLI エントリポイント。

    Args:
        argv: 引数列。None なら sys.argv を使う。

    Returns:
        int: 正常終了 0、エラー時 1。

    Policy:
        - --fail-on-warning 指定時のみ warning 残存で 1 を返す。
    """
    return _main_impl(argv)


# === Internal helpers (private) ===


def _read_rules_yaml(path: Path) -> dict[str, Any]:
    """YAML を読み込み、dict であることを確認する。

    Args:
        path: YAML ファイルパス。

    Returns:
        dict[str, Any]: パース結果。

    Raises:
        ValueError: dict にパースされなかったとき。

    Policy:
        - 入口で dict 化を強制し、後続の検査を単純化する。
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("architecture rules YAML must parse to a dict")
    for key in ("meta", "facts", "validation_rules"):
        if key not in data:
            raise KeyError(f"missing top-level key: {key}")
    return data


def _coverage_autofix_key(  # noqa: CR100
    coverage: dict[str, Any],
) -> str | None:
    """coverage dict から autofix キーを取得する。

    Args:
        coverage: rule.coverage dict。

    Returns:
        str | None: 見つかったキー。無ければ None。

    Policy:
        - PRIMARY → legacy の順に走査し、最初に存在したキーを返す。
    """
    for key in LEGACY_AUTOFIX_KEYS:
        if key in coverage:
            return key
    return None


def _validate_tree_root(data: dict[str, Any]) -> None:
    """facts.tree の root 形状を検証する。

    Args:
        data: rules dict。

    Raises:
        KeyError: facts.tree が無いとき。
        ValueError: root の path/kind が想定外のとき。

    Policy:
        - root が崩れたら以降のノイズを増やさず早期 raise する。
    """
    tree = data.get("facts", {}).get("tree")
    if not isinstance(tree, dict):
        raise KeyError("facts.tree must be present")
    if _is_invalid_tree_root(tree):
        raise ValueError(
            "facts.tree must start with path='.' and kind='root'")


def _is_invalid_tree_root(tree: dict[str, Any]) -> bool:
    """tree root の path / kind が想定外かを判定する。

    Args:
        tree: facts.tree dict。

    Returns:
        bool: 想定外なら True。

    Policy:
        - path == "." かつ kind == "root" のみを正常とみなす。
    """
    return tree.get("path") != "." or tree.get("kind") != "root"


def _validate_contracts(data: dict[str, Any]) -> None:
    """facts.codemaker_bundle_contracts の構造を検証する。

    Args:
        data: rules dict。

    Policy:
        - None / list / 各 contract dict をそれぞれ検査する。
    """
    contracts = data.get("facts", {}).get("codemaker_bundle_contracts", [])
    if contracts is None:
        return
    if not isinstance(contracts, list):
        raise TypeError("facts.codemaker_bundle_contracts must be a list")
    for contract in contracts:
        _validate_single_contract(contract)


def _validate_single_contract(contract: Any) -> None:
    """1 件の contract dict を検証する。

    Args:
        contract: 検証対象。

    Policy:
        - dict / 必須キー / required_paths の非空 list を確認する。
    """
    if not isinstance(contract, dict):
        raise TypeError("each codemaker bundle contract must be a dict")
    for key in ("id", "manifest_path", "required_paths"):
        if key not in contract:
            raise KeyError(f"codemaker bundle contract missing key: {key}")
    required_paths = contract["required_paths"]
    if _is_invalid_required_paths(required_paths):
        raise TypeError(
            "codemaker bundle contract required_paths "
            "must be a non-empty list"
        )


def _is_invalid_required_paths(required_paths: Any) -> bool:
    """required_paths が list で非空でないかを判定する。

    Args:
        required_paths: 検査対象。

    Returns:
        bool: list でない、または空のとき True。

    Policy:
        - None も list でない扱いで True を返す。
    """
    if not isinstance(required_paths, list):
        return True
    return not required_paths


def _validate_rules_list(data: dict[str, Any]) -> None:
    """validation_rules の各 rule を順に検証する。

    Args:
        data: rules dict。

    Policy:
        - rule ごとに必須キー / coverage / deterministic check を検査する。
    """
    for rule in data["validation_rules"]:
        _validate_single_rule(rule)


def _validate_single_rule(rule: dict[str, Any]) -> None:
    """1 件の rule dict を検証する。

    Args:
        rule: 検査対象 rule。

    Policy:
        - 構造 → enforcement → scope → evidence → coverage の順で検査する。
    """
    _check_rule_required_keys(rule)
    _check_rule_suggested_actions(rule)
    _check_rule_enforcement(rule)
    _check_rule_scope_paths(rule)
    _check_rule_evidence(rule)
    _check_rule_coverage(rule)
    _check_rule_deterministic_checks(rule)


def _check_rule_required_keys(rule: dict[str, Any]) -> None:
    """rule の必須キー欠落を検査する。

    Args:
        rule: rule dict。

    Policy:
        - REQUIRED_RULE_KEYS との差集合が空であることを要求する。
    """
    missing = REQUIRED_RULE_KEYS - set(rule)
    if not missing:
        return
    rule_id = rule.get("id", "<unknown>")
    raise KeyError(
        f"rule {rule_id} missing keys: {sorted(missing)}"
    )


def _check_rule_suggested_actions(rule: dict[str, Any]) -> None:
    """rule.suggested_actions が list かを検査する。

    Args:
        rule: rule dict。

    Policy:
        - list 以外なら TypeError とする。
    """
    if isinstance(rule["suggested_actions"], list):
        return
    raise TypeError(
        f"rule {rule['id']} suggested_actions must be a list"
    )


def _check_rule_enforcement(rule: dict[str, Any]) -> None:
    """rule.enforcement の mode 存在を検査する。

    Args:
        rule: rule dict。

    Policy:
        - mode キーが無いと走行モードが決まらないので raise する。
    """
    if "mode" in rule["enforcement"]:
        return
    raise KeyError(f"rule {rule['id']} missing enforcement.mode")


def _check_rule_scope_paths(rule: dict[str, Any]) -> None:
    """rule.scope.paths が list かを検査する。

    Args:
        rule: rule dict。

    Policy:
        - list 以外なら TypeError とする。
    """
    if isinstance(rule.get("scope", {}).get("paths"), list):
        return
    raise TypeError(f"rule {rule['id']} scope.paths must be a list")


def _check_rule_evidence(rule: dict[str, Any]) -> None:
    """rule.evidence.checks が非空 list かを検査する。

    Args:
        rule: rule dict。

    Policy:
        - 非空 list 以外は TypeError として扱う。
    """
    checks = rule.get("evidence", {}).get("checks")
    if _is_valid_checks(checks):
        return
    raise TypeError(
        f"rule {rule['id']} evidence.checks must be a non-empty list"
    )


def _is_valid_checks(checks: Any) -> bool:
    """evidence.checks が非空 list かを判定する。

    Args:
        checks: 検査対象。

    Returns:
        bool: list で非空なら True。

    Policy:
        - 型 → 非空 の順で判定する。
    """
    if not isinstance(checks, list):
        return False
    return bool(checks)


def _check_rule_coverage(rule: dict[str, Any]) -> None:
    """rule.coverage の構造と値域を検査する。

    Args:
        rule: rule dict。

    Policy:
        - dict / 必須キー / autofix キー / 値域を順に検査する。
    """
    coverage = rule.get("coverage")
    _check_coverage_is_dict(rule, coverage)
    _check_coverage_required_keys(rule, coverage)
    _check_coverage_autofix(rule, coverage)
    _check_coverage_deterministic_review(rule, coverage)
    _check_coverage_next_checker_unit(rule, coverage)
    _check_coverage_rationale(rule, coverage)


def _check_coverage_is_dict(
    rule: dict[str, Any],
    coverage: Any,
) -> None:
    """coverage が dict かを検査する。

    Args:
        rule: rule dict。
        coverage: 検査対象 coverage。

    Policy:
        - dict 以外は TypeError とする。
    """
    if isinstance(coverage, dict):
        return
    raise TypeError(f"rule {rule['id']} coverage must be a dict")


def _check_coverage_required_keys(
    rule: dict[str, Any],
    coverage: dict[str, Any],
) -> None:
    """coverage の必須キーを検査する。

    Args:
        rule: rule dict。
        coverage: rule.coverage。

    Policy:
        - REQUIRED_COVERAGE_KEYS が全て存在することを要求する。
    """
    for key in REQUIRED_COVERAGE_KEYS:
        if key in coverage:
            continue
        raise KeyError(
            f"rule {rule['id']} coverage missing key: {key}"
        )


def _check_coverage_autofix(
    rule: dict[str, Any],
    coverage: dict[str, Any],
) -> None:
    """autofix キーの存在と値域を検査する。

    Args:
        rule: rule dict。
        coverage: rule.coverage。

    Policy:
        - PRIMARY or legacy の片方は必須で、値も VALID_REPAIR_AUTOFIX に限る。
    """
    autofix_key = _coverage_autofix_key(coverage)
    if autofix_key is None:
        raise KeyError(
            f"rule {rule['id']} coverage missing key: "
            f"{PRIMARY_AUTOFIX_KEY} (or legacy repair_autofix)"
        )
    autofix_value = coverage[autofix_key]
    if autofix_value in VALID_REPAIR_AUTOFIX:
        return
    raise ValueError(
        f"rule {rule['id']} coverage.{autofix_key} must be one of "
        f"{sorted(VALID_REPAIR_AUTOFIX)}"
    )


def _check_coverage_deterministic_review(
    rule: dict[str, Any],
    coverage: dict[str, Any],
) -> None:
    """deterministic_review の値域を検査する。

    Args:
        rule: rule dict。
        coverage: rule.coverage。

    Policy:
        - VALID_DETERMINISTIC_REVIEWS のいずれかであることを要求する。
    """
    if coverage["deterministic_review"] in VALID_DETERMINISTIC_REVIEWS:
        return
    raise ValueError(
        f"rule {rule['id']} coverage.deterministic_review must be one of "
        f"{sorted(VALID_DETERMINISTIC_REVIEWS)}"
    )


def _check_coverage_next_checker_unit(
    rule: dict[str, Any],
    coverage: dict[str, Any],
) -> None:
    """next_checker_unit の型を検査する。

    Args:
        rule: rule dict。
        coverage: rule.coverage。

    Policy:
        - None または str を許容する。
    """
    next_checker_unit = coverage["next_checker_unit"]
    if _is_valid_next_checker_unit(next_checker_unit):
        return
    raise TypeError(
        f"rule {rule['id']} coverage.next_checker_unit "
        "must be a string or null"
    )


def _is_valid_next_checker_unit(value: Any) -> bool:
    """next_checker_unit の値が許容範囲かを判定する。

    Args:
        value: 検査対象。

    Returns:
        bool: None または str なら True。

    Policy:
        - 既存仕様に合わせて None も許容する。
    """
    if value is None:
        return True
    return isinstance(value, str)


def _check_coverage_rationale(
    rule: dict[str, Any],
    coverage: dict[str, Any],
) -> None:
    """rationale が非空 str かを検査する。

    Args:
        rule: rule dict。
        coverage: rule.coverage。

    Policy:
        - 空白のみの文字列も無効として扱う。
    """
    rationale = coverage["rationale"]
    if _is_invalid_rationale(rationale):
        raise TypeError(
            f"rule {rule['id']} coverage.rationale "
            "must be a non-empty string"
        )


def _is_invalid_rationale(value: Any) -> bool:
    """rationale が空 / 非 str かを判定する。

    Args:
        value: 検査対象。

    Returns:
        bool: 無効なら True。

    Policy:
        - 空白のみも非空とは見なさない。
    """
    if not isinstance(value, str):
        return True
    return not value.strip()


def _check_rule_deterministic_checks(rule: dict[str, Any]) -> None:
    """deterministic rule の checks が REGISTRY 登録済みかを検査する。

    Args:
        rule: rule dict。

    Policy:
        - deterministic 以外は検査しない。
    """
    if rule["enforcement"]["mode"] != "deterministic":
        return
    for check_name in rule["evidence"]["checks"]:
        _check_check_name_registered(rule, check_name)


def _check_check_name_registered(
    rule: dict[str, Any],
    check_name: str,
) -> None:
    """check 名が CHECK_REGISTRY にあるかを検査する。

    Args:
        rule: rule dict。
        check_name: 1 件の check 名。

    Policy:
        - 未登録なら KeyError として早期 raise する。
    """
    if check_name in CHECK_REGISTRY:
        return
    raise KeyError(
        f"rule {rule['id']} references unknown "
        f"deterministic check: {check_name}"
    )


def _scope_paths(rule: dict[str, Any]) -> list[str]:  # noqa: CR100
    """rule.scope.paths を list にコピーして返す。

    Args:
        rule: rule dict。

    Returns:
        list[str]: scope.paths の浅いコピー。

    Policy:
        - 呼び出し側で副作用を持たせないよう毎回新しい list を返す。
    """
    return list(rule.get("scope", {}).get("paths", []))


def _iter_tree_nodes_impl(node: dict[str, Any]):
    """iter_tree_nodes の実装本体。

    Args:
        node: 起点ノード。

    Returns:
        Generator: 自身→children を順に返す generator。

    Policy:
        - public 入口の generator 委譲先として再帰実装を分離する。
    """
    yield node
    for child in node.get("children", []):
        yield from _iter_tree_nodes_impl(child)


def _find_tree_node_impl(
    data: dict[str, Any],
    path_value: str,
) -> dict[str, Any] | None:
    """find_tree_node の実装本体。

    Args:
        data: rules dict。
        path_value: 探索対象 path。

    Returns:
        dict[str, Any] | None: 該当ノード。

    Policy:
        - 最初に一致したノードのみ返す。
    """
    for node in _iter_tree_nodes_impl(data["facts"]["tree"]):
        if node.get("path") == path_value:
            return node
    return None


def _find_entry_point_impl(
    data: dict[str, Any],
    entry_id: str,
) -> dict[str, Any] | None:
    """find_entry_point の実装本体。

    Args:
        data: rules dict。
        entry_id: 探索対象 id。

    Returns:
        dict[str, Any] | None: 該当 entry。

    Policy:
        - facts.entry_points を順に走査する。
    """
    entries = data.get("facts", {}).get("entry_points", [])
    return next(
        (item for item in entries if item.get("id") == entry_id),
        None,
    )


def _generated_file_nodes_impl(  # noqa: CR100
    data: dict[str, Any],
) -> list[dict[str, Any]]:
    """generated_file_nodes の実装本体。

    Args:
        data: rules dict。

    Returns:
        list[dict[str, Any]]: 生成物 file ノード列。

    Policy:
        - tree 全体を走査して条件で絞り込む。
    """
    nodes: list[dict[str, Any]] = []
    for node in _iter_tree_nodes_impl(data["facts"]["tree"]):
        if _is_generated_file_node(node):
            nodes.append(node)
    return nodes


def _is_generated_file_node(node: dict[str, Any]) -> bool:
    """src/generated/ 配下の file ノードかを判定する。

    Args:
        node: 判定対象ノード。

    Returns:
        bool: 条件を満たせば True。

    Policy:
        - kind と path 接頭辞の両方を満たすときだけ True を返す。
    """
    if node.get("kind") != "file":
        return False
    path_value = node.get("path", "")
    return path_value.startswith("src/generated/")


def _distribution_artifact_nodes_impl(  # noqa: CR100
    data: dict[str, Any],
) -> list[dict[str, Any]]:
    """distribution_artifact_nodes の実装本体。

    Args:
        data: rules dict。

    Returns:
        list[dict[str, Any]]: dist 直下の file ノード列。

    Policy:
        - dist ノード不在時は空 list を返す。
    """
    dist_node = _find_tree_node_impl(data, "dist")
    if dist_node is None:
        return []
    return [
        child
        for child in dist_node.get("children", [])
        if child.get("kind") == "file"
    ]


def _find_codemaker_bundle_contract_impl(
    data: dict[str, Any],
    contract_id: str,
) -> dict[str, Any] | None:
    """find_codemaker_bundle_contract の実装本体。

    Args:
        data: rules dict。
        contract_id: 探索対象 id。

    Returns:
        dict[str, Any] | None: 該当 contract。

    Policy:
        - facts.codemaker_bundle_contracts を順に走査する。
    """
    contracts = data.get("facts", {}).get("codemaker_bundle_contracts", [])
    return next(
        (item for item in contracts if item.get("id") == contract_id),
        None,
    )


def _fallback_tree_node(  # noqa: CR100
    node: dict[str, Any] | None,
) -> dict[str, Any]:
    """tree ノードが None のとき空ノードを返す。

    Args:
        node: 検査対象ノード。

    Returns:
        dict[str, Any]: ノードまたは {"children": []}。

    Policy:
        - 不在時の代替を呼び出し側でも統一する。
    """
    if node is None:
        return {"children": []}
    return node


def _warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    failed_check: str,
    *,
    reason: str | None = None,
    expected: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
) -> CheckOutcome:
    """warning 形式の CheckOutcome を組み立てる。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        failed_check: 失敗 check 名。
        reason: 補足理由。
        expected: 期待値 dict。
        observed: 観測値 dict。

    Returns:
        CheckOutcome: status=warning の outcome。

    Policy:
        - rule.message と reason を結合してメッセージ化する。
    """
    message = _compose_warning_message(rule, reason)
    return CheckOutcome(
        status="warning",
        checked_paths=checked_paths,
        failed_checks=[failed_check],
        message=message,
        suggested_actions=list(rule.get("suggested_actions", [])),
        expected=expected,
        observed=observed,
    )


def _compose_warning_message(
    rule: dict[str, Any],
    reason: str | None,
) -> str | None:
    """rule.message と reason を結合して warning メッセージを返す。

    Args:
        rule: 対象 rule。
        reason: 追加理由。

    Returns:
        str | None: 結合後メッセージ。両方無ければ None。

    Policy:
        - reason が空のときは rule.message をそのまま使う。
    """
    message = rule.get("message")
    if not reason:
        return message
    if message:
        return f"{message}: {reason}"
    return reason


def _ok(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
) -> CheckOutcome:
    """status=ok の CheckOutcome を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。

    Returns:
        CheckOutcome: status=ok の outcome。

    Policy:
        - rule 引数は将来の拡張用に残す。
    """
    return CheckOutcome(status="ok", checked_paths=checked_paths)


def _skipped(rule: dict[str, Any]) -> CheckOutcome:
    """非 deterministic rule 用の skipped outcome を返す。

    Args:
        rule: 対象 rule。

    Returns:
        CheckOutcome: status=skipped の outcome。

    Policy:
        - 理由を固定文言で残し、coverage_review 集計に使えるようにする。
    """
    return CheckOutcome(
        status="skipped",
        checked_paths=_scope_paths(rule),
        reason="初版では deterministic rule のみ実行する",
    )


def _file_contains(path: Path, needle: str) -> bool:
    """指定ファイルに needle 文字列があるかを判定する。

    Args:
        path: 検査対象ファイル。
        needle: 検索する文字列。

    Returns:
        bool: 含まれていれば True。

    Policy:
        - UTF-8 で読み、部分一致のみ確認する。
    """
    return needle in path.read_text(encoding="utf-8")


def _manifest_entries(path: Path) -> list[str]:
    """manifest ファイルの有効行を返す。

    Args:
        path: manifest ファイル。

    Returns:
        list[str]: コメント・空行を除いた行列。

    Policy:
        - 行頭 `#` をコメントとして除外する。
    """
    entries: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if _is_skipped_manifest_line(line):
            continue
        entries.append(line)
    return entries


def _is_skipped_manifest_line(line: str) -> bool:
    """manifest 行をスキップすべきかを判定する。

    Args:
        line: strip 済みの 1 行。

    Returns:
        bool: 空行またはコメントなら True。

    Policy:
        - "#" 始まりとブランクのみを除外する。
    """
    if not line:
        return True
    return line.startswith("#")


def _iter_py_files(base: Path):
    """指定ディレクトリ配下の .py ファイルを yield する。

    Args:
        base: 探索起点ディレクトリ。

    Returns:
        Generator: __pycache__ を除いた .py パス列。

    Policy:
        - base が存在しないときは何も返さない。
    """
    return _iter_py_files_impl(base)


def _iter_py_files_impl(base: Path):
    """_iter_py_files の generator 本体。

    Args:
        base: 探索起点ディレクトリ。

    Returns:
        Generator: .py パス列。

    Policy:
        - rglob で再帰する。
    """
    if not base.exists():
        return
    for path in base.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _grep(  # noqa: CR100
    pattern: re.Pattern[str],
    files: list[Path],
) -> list[tuple[Path, int, str]]:
    """pattern に当たる行を全ファイルから収集する。

    Args:
        pattern: 検索する正規表現。
        files: 検索対象ファイル列。

    Returns:
        list[tuple[Path, int, str]]: (path, lineno, line) の hit 列。

    Policy:
        - 読み込み失敗は静かに無視する。
    """
    hits: list[tuple[Path, int, str]] = []
    for path in files:
        text = _read_text_safely(path)
        if text is None:
            continue
        _collect_pattern_hits(pattern, path, text, hits)
    return hits


def _read_text_safely(path: Path) -> str | None:
    """ファイルを UTF-8 で読む。失敗時は None を返す。

    Args:
        path: 読み込み対象。

    Returns:
        str | None: 内容。OS/Decode エラー時は None。

    Policy:
        - 例外を握りつぶしても grep 全体は続行できるようにする。
    """
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _collect_pattern_hits(
    pattern: re.Pattern[str],
    path: Path,
    text: str,
    hits: list[tuple[Path, int, str]],
) -> None:
    """1 ファイル分の hit を hits に追加する。

    Args:
        pattern: 検索する正規表現。
        path: 対象パス。
        text: ファイル内容。
        hits: 追記対象の list。

    Policy:
        - 行番号は 1 始まり。
    """
    for lineno, line in enumerate(text.splitlines(), 1):
        if pattern.search(line):
            hits.append((path, lineno, line))


def _rel_hit(  # noqa: CR100
    repo_root: Path,
    hit: tuple[Path, int, str],
) -> str:
    """grep hit を `path:line: text` の表示形式に整える。

    Args:
        repo_root: リポジトリルート。
        hit: (path, lineno, line) タプル。

    Returns:
        str: 整形済み文字列。

    Policy:
        - path は repo_root 相対に変換する。
    """
    path, lineno, line = hit
    return f"{path.relative_to(repo_root)}:{lineno}: {line.strip()}"


def _scene_static_boundary_checks_impl(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """scene_static_boundary_checks の本体。

    Args:
        context: CheckContext。
        rule: 対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - 構造 / draw / input の順に短絡する。
    """
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    scene_root = repo_root / "src" / "scenes"
    structure_outcome = _scene_structure_outcome(
        rule, checked_paths, scene_root)
    if structure_outcome is not None:
        return structure_outcome
    scene_dirs = _list_scene_dirs(scene_root)
    boundary_outcome = _scene_boundary_outcome(
        rule, checked_paths, repo_root, scene_dirs)
    if boundary_outcome is not None:
        return boundary_outcome
    return _ok(rule, checked_paths)


def _scene_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    reason: str,
) -> CheckOutcome:
    """scene_static_boundary_checks 用の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        reason: 警告理由。

    Returns:
        CheckOutcome: failed_check 固定の warning。

    Policy:
        - failed_check を 1 か所に固定する。
    """
    return _warning(
        rule, checked_paths, "scene_static_boundary_checks", reason=reason)


def _scene_structure_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    scene_root: Path,
) -> CheckOutcome | None:
    """scene 構造に関する warning を返す。なければ None。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        scene_root: src/scenes パス。

    Returns:
        CheckOutcome | None: 該当時のみ warning。

    Policy:
        - scene 構造が壊れた状態で他検査に進まない。
    """
    if not scene_root.is_dir():
        return _scene_warning(
            rule, checked_paths, "missing path: src/scenes")
    scene_dirs = _list_scene_dirs(scene_root)
    if not scene_dirs:
        return _scene_warning(
            rule, checked_paths,
            "src/scenes has no scene directories")
    return _iter_scene_dir_structure_outcome(
        rule, checked_paths, scene_dirs)


def _iter_scene_dir_structure_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    scene_dirs: list[Path],
) -> CheckOutcome | None:
    """各 scene_dir 構造を走査して最初の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        scene_dirs: scene ディレクトリ列。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - 1 件目で短絡する。
    """
    for scene_dir in scene_dirs:
        outcome = _scene_dir_structure_outcome(
            rule, checked_paths, scene_dir)
        if outcome is not None:
            return outcome
    return None


def _list_scene_dirs(scene_root: Path) -> list[Path]:
    """scene_root 直下の scene ディレクトリを返す。

    Args:
        scene_root: src/scenes パス。

    Returns:
        list[Path]: __ 始まりを除いた直下サブディレクトリ。

    Policy:
        - scene_root が存在しないときは呼び出し側で空判定する。
    """
    if not scene_root.is_dir():
        return []
    return sorted(
        p for p in scene_root.iterdir()
        if p.is_dir() and not p.name.startswith("__")
    )


def _scene_dir_structure_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    scene_dir: Path,
) -> CheckOutcome | None:
    """1 つの scene_dir 構造の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        scene_dir: scene ディレクトリ。

    Returns:
        CheckOutcome | None: 該当時のみ warning。

    Policy:
        - 必須ファイル → scene.py 規約 → 余剰ファイルの順に検査する。
    """
    required_outcome = _scene_required_files_outcome(
        rule, checked_paths, scene_dir)
    if required_outcome is not None:
        return required_outcome
    scene_py_outcome = _scene_py_outcome(rule, checked_paths, scene_dir)
    if scene_py_outcome is not None:
        return scene_py_outcome
    return _scene_unexpected_files_outcome(rule, checked_paths, scene_dir)


def _scene_required_files_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    scene_dir: Path,
) -> CheckOutcome | None:
    """必須 model/presenter/view ファイル欠落の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        scene_dir: scene ディレクトリ。

    Returns:
        CheckOutcome | None: 欠落時の warning。

    Policy:
        - 最初に欠けた 1 件だけ報告する。
    """
    for required in ("model.py", "presenter.py", "view.py"):
        rel = f"src/scenes/{scene_dir.name}/{required}"
        if (scene_dir / required).is_file():
            continue
        return _scene_warning(
            rule, checked_paths,
            f"missing required scene file: {rel}")
    return None


def _scene_py_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    scene_dir: Path,
) -> CheckOutcome | None:
    """scene.py の在/不在規約違反の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        scene_dir: scene ディレクトリ。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - town は存在 NG、それ以外は必須。
    """
    if scene_dir.name == "town":
        return _town_scene_py_outcome(rule, checked_paths, scene_dir)
    if (scene_dir / "scene.py").is_file():
        return None
    rel = f"src/scenes/{scene_dir.name}/scene.py"
    return _scene_warning(
        rule, checked_paths, f"missing required scene file: {rel}")


def _town_scene_py_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    scene_dir: Path,
) -> CheckOutcome | None:
    """town/scene.py の存在を許さない warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        scene_dir: scene ディレクトリ。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - town は presenter ベースで scene.py を持たない。
    """
    if not (scene_dir / "scene.py").exists():
        return None
    return _scene_warning(
        rule, checked_paths, "town/scene.py must not exist")


def _scene_unexpected_files_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    scene_dir: Path,
) -> CheckOutcome | None:
    """SCENE_ALLOWED_FILES 外の .py がある場合の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        scene_dir: scene ディレクトリ。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - .py だけを検査対象とする。
    """
    unexpected = sorted(
        child.name
        for child in scene_dir.iterdir()
        if _is_unexpected_scene_file(child)
    )
    if not unexpected:
        return None
    reason = (
        f"unexpected python files in src/scenes/{scene_dir.name}: "
        f"{unexpected}"
    )
    return _scene_warning(rule, checked_paths, reason)


def _is_unexpected_scene_file(child: Path) -> bool:
    """SCENE_ALLOWED_FILES 外の .py かを判定する。

    Args:
        child: scene_dir 直下の Path。

    Returns:
        bool: .py ファイルかつ許可外なら True。

    Policy:
        - SCENE_ALLOWED_FILES と完全一致するファイル名は許容する。
    """
    if not child.is_file():
        return False
    if child.suffix != ".py":
        return False
    return child.name not in SCENE_ALLOWED_FILES


def _scene_boundary_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    scene_dirs: list[Path],
) -> CheckOutcome | None:
    """pyxel と input の境界違反の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        scene_dirs: scene ディレクトリ列。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - model → presenter → view の順で最初の違反だけ報告する。
    """
    layer_specs = (
        (["model.py"], "pyxel draw call in scene model"),
        (["presenter.py"], "pyxel draw call in scene presenter"),
    )
    layer_outcome = _scene_draw_layer_outcome(
        rule, checked_paths, repo_root, scene_dirs, layer_specs)
    if layer_outcome is not None:
        return layer_outcome
    return _scene_view_input_outcome(
        rule, checked_paths, repo_root, scene_dirs)


def _scene_draw_layer_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    scene_dirs: list[Path],
    layer_specs: tuple,
) -> CheckOutcome | None:
    """指定した複数 layer の draw 違反を順に検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        scene_dirs: scene ディレクトリ列。
        layer_specs: (layer_files, reason_prefix) のタプル列。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - 1 件目で短絡する。
    """
    for layer_files, reason_prefix in layer_specs:
        outcome = _scene_layer_grep_outcome(
            rule, checked_paths, repo_root, scene_dirs,
            layer_files=layer_files,
            pattern=SCENE_DRAW_CALL,
            reason_prefix=reason_prefix,
        )
        if outcome is not None:
            return outcome
    return None


def _scene_layer_grep_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    scene_dirs: list[Path],
    *,
    layer_files: list[str],
    pattern: re.Pattern[str],
    reason_prefix: str,
) -> CheckOutcome | None:
    """指定 layer の grep hit に対する warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        scene_dirs: scene ディレクトリ列。
        layer_files: layer 内の対象ファイル名列。
        pattern: 検索する正規表現。
        reason_prefix: warning reason の接頭辞。

    Returns:
        CheckOutcome | None: hit があれば warning。

    Policy:
        - 1 件目の hit だけを reason に含める。
    """
    files = _collect_layer_files(scene_dirs, layer_files)
    hits = _grep(pattern, files)
    if not hits:
        return None
    return _scene_warning(
        rule, checked_paths,
        f"{reason_prefix}: {_rel_hit(repo_root, hits[0])}")


def _collect_layer_files(
    scene_dirs: list[Path],
    layer_files: list[str],
) -> list[Path]:
    """scene_dirs × layer_files の存在パスを集める。

    Args:
        scene_dirs: scene ディレクトリ列。
        layer_files: layer ファイル名列。

    Returns:
        list[Path]: 実在するファイルパス列。

    Policy:
        - 存在しないファイルは結果から除外する。
    """
    files: list[Path] = []
    for scene_dir in scene_dirs:
        for name in layer_files:
            path = scene_dir / name
            if path.is_file():
                files.append(path)
    return files


def _scene_view_input_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    scene_dirs: list[Path],
) -> CheckOutcome | None:
    """view 層の入力読みに対する warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        scene_dirs: scene ディレクトリ列。

    Returns:
        CheckOutcome | None: hit があれば warning。

    Policy:
        - view.py と view_model.py の両方を対象にする。
    """
    view_like_files = _collect_layer_files(
        scene_dirs, ["view.py", "view_model.py"])
    input_hits = _grep(SCENE_INPUT_CALL, view_like_files)
    if not input_hits:
        return None
    reason = (
        "input read in scene view layer: "
        f"{_rel_hit(repo_root, input_hits[0])}"
    )
    return _scene_warning(rule, checked_paths, reason)


def _shared_directory_role_checks_impl(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """shared_directory_role_checks の本体。

    Args:
        context: CheckContext。
        rule: 対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - 必須ディレクトリ → role 整合 → grep の順で短絡する。
    """
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    dirs_outcome = _shared_required_dirs_outcome(
        rule, checked_paths, repo_root)
    if dirs_outcome is not None:
        return dirs_outcome
    facts_outcome = _shared_facts_role_outcome(
        rule, checked_paths, context)
    if facts_outcome is not None:
        return facts_outcome
    grep_outcome = _shared_grep_outcome(
        rule, checked_paths, context, repo_root)
    if grep_outcome is not None:
        return grep_outcome
    return _ok(rule, checked_paths)


def _shared_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    reason: str,
    *,
    expected: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
) -> CheckOutcome:
    """shared_directory_role_checks 用の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        reason: 警告理由。
        expected: 期待値 dict。
        observed: 観測値 dict。

    Returns:
        CheckOutcome: failed_check 固定の warning。

    Policy:
        - expected / observed もこの helper を経由させる。
    """
    return _warning(
        rule, checked_paths, "shared_directory_role_checks",
        reason=reason, expected=expected, observed=observed)


def _shared_required_dirs_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
) -> CheckOutcome | None:
    """src/shared/services と src/shared/state の存在を確認する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。

    Returns:
        CheckOutcome | None: 欠落時の warning。

    Policy:
        - どちらも必須なので、欠けた方を 1 件で報告する。
    """
    services_root = repo_root / "src" / "shared" / "services"
    state_root = repo_root / "src" / "shared" / "state"
    if not services_root.is_dir():
        return _shared_warning(
            rule, checked_paths, "missing path: src/shared/services")
    if not state_root.is_dir():
        return _shared_warning(
            rule, checked_paths, "missing path: src/shared/state")
    return None


def _shared_facts_role_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    context: CheckContext,
) -> CheckOutcome | None:
    """facts 上の player_model と legacy bridge role を点検する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        context: CheckContext。

    Returns:
        CheckOutcome | None: 整合違反時の warning。

    Policy:
        - player_model 系 → legacy bridge 系の順に検査する。
    """
    player_outcome = _shared_player_model_outcome(
        rule, checked_paths, context)
    if player_outcome is not None:
        return player_outcome
    return _shared_legacy_bridge_outcome(rule, checked_paths, context)


def _shared_player_model_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    context: CheckContext,
) -> CheckOutcome | None:
    """player_model.py の role/status 整合の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        context: CheckContext。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - facts に該当 node が無いときは None を返す。
    """
    node = _find_tree_node_impl(
        context.data, "src/shared/state/player_model.py")
    if node is None:
        return None
    if not _is_invalid_player_model_node(node):
        return None
    return _shared_warning(
        rule, checked_paths,
        "player_model.py facts are not aligned "
        "with source-of-truth role",
        expected=_player_model_expected(),
        observed=_role_status_observed(node),
    )


def _player_model_expected() -> dict[str, Any]:  # noqa: CR100
    """player_model 違反の expected dict を返す。

    Returns:
        dict[str, Any]: path/role/status を含む dict。

    Policy:
        - 定数値を 1 か所に集めて差分を減らす。
    """
    return {
        "path": "src/shared/state/player_model.py",
        "role": "player_source_of_truth",
        "status": "active",
    }


def _role_status_observed(  # noqa: CR100
    node: dict[str, Any],
) -> dict[str, Any]:
    """ノードの role / status を観測 dict にまとめる。

    Args:
        node: facts ノード。

    Returns:
        dict[str, Any]: role / status のみを抜き出した dict。

    Policy:
        - 報告フォーマットを共有して整合を保つ。
    """
    return {
        "role": node.get("role"),
        "status": node.get("status"),
    }


def _is_invalid_player_model_node(node: dict[str, Any]) -> bool:
    """player_model node の role/status が想定外かを判定する。

    Args:
        node: facts ノード。

    Returns:
        bool: 想定外なら True。

    Policy:
        - role == player_source_of_truth かつ status == active を正常とする。
    """
    if node.get("role") != "player_source_of_truth":
        return True
    return node.get("status") != "active"


def _shared_legacy_bridge_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    context: CheckContext,
) -> CheckOutcome | None:
    """legacy bridge ファイルの role/status 整合 warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        context: CheckContext。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - 既知の 2 ファイル（player_state / item_use）を順に確認する。
    """
    legacy_targets = (
        ("src/shared/services/player_state.py", "legacy_player_snapshot"),
        ("src/shared/services/item_use.py", "legacy_item_use_bridge"),
    )
    for rel_path, expected_role in legacy_targets:
        outcome = _legacy_bridge_target_outcome(
            rule, checked_paths, context, rel_path, expected_role)
        if outcome is not None:
            return outcome
    return None


def _legacy_bridge_target_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    context: CheckContext,
    rel_path: str,
    expected_role: str,
) -> CheckOutcome | None:
    """1 件の legacy bridge target を確認する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        context: CheckContext。
        rel_path: 対象 path。
        expected_role: 期待 role。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - facts に存在しないときは None を返す。
    """
    node = _find_tree_node_impl(context.data, rel_path)
    if node is None:
        return None
    if not _is_invalid_legacy_bridge_node(node, expected_role):
        return None
    return _build_legacy_bridge_warning(
        rule, checked_paths, rel_path, expected_role, node)


def _build_legacy_bridge_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    rel_path: str,
    expected_role: str,
    node: dict[str, Any],
) -> CheckOutcome:
    """legacy bridge 違反の warning を組み立てる。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        rel_path: 対象 path。
        expected_role: 期待 role。
        node: facts ノード。

    Returns:
        CheckOutcome: shared 用 warning。

    Policy:
        - reason / expected / observed をまとめて作る。
    """
    file_name = Path(rel_path).name
    reason = (
        f"{file_name} facts are not aligned "
        "with legacy bridge status"
    )
    return _shared_warning(
        rule, checked_paths, reason,
        expected=_legacy_bridge_expected(rel_path, expected_role),
        observed=_role_status_observed(node),
    )


def _legacy_bridge_expected(  # noqa: CR100
    rel_path: str,
    expected_role: str,
) -> dict[str, Any]:
    """legacy bridge 違反の expected dict を返す。

    Args:
        rel_path: 対象 path。
        expected_role: 期待 role。

    Returns:
        dict[str, Any]: path/role/status を含む dict。

    Policy:
        - 期待 status を legacy で固定する。
    """
    return {
        "path": rel_path,
        "role": expected_role,
        "status": "legacy",
    }


def _is_invalid_legacy_bridge_node(
    node: dict[str, Any],
    expected_role: str,
) -> bool:
    """legacy bridge node の整合性が崩れているかを判定する。

    Args:
        node: facts ノード。
        expected_role: 期待 role。

    Returns:
        bool: status != legacy または role 不一致なら True。

    Policy:
        - 2 条件のいずれか不一致で違反扱いとする。
    """
    if node.get("status") != "legacy":
        return True
    return node.get("role") != expected_role


def _shared_grep_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    context: CheckContext,
    repo_root: Path,
) -> CheckOutcome | None:
    """facts 後段の grep 二重確認を行う。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        context: CheckContext。
        repo_root: リポジトリルート。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - role 違反 → pyxel 違反 → import 違反の順に検査する。
    """
    services_outcome = _shared_services_role_outcome(
        rule, checked_paths, context)
    if services_outcome is not None:
        return services_outcome
    state_role_outcome = _shared_state_role_outcome(
        rule, checked_paths, context)
    if state_role_outcome is not None:
        return state_role_outcome
    pyxel_outcome = _shared_pyxel_outcome(
        rule, checked_paths, repo_root)
    if pyxel_outcome is not None:
        return pyxel_outcome
    return _shared_import_outcome(rule, checked_paths, repo_root)


def _shared_services_role_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    context: CheckContext,
) -> CheckOutcome | None:
    """services 配下の source_of_truth role を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        context: CheckContext。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - role が _source_of_truth で終わっていたら NG。
    """
    found_node = _find_tree_node_impl(
        context.data, "src/shared/services")
    services_root_node = _fallback_tree_node(found_node)
    for node in _iter_tree_nodes_impl(services_root_node):
        if node.get("kind") != "file":
            continue
        role = str(node.get("role", ""))
        if not role.endswith("_source_of_truth"):
            continue
        reason = (
            "service file keeps source-of-truth role: "
            f"{node.get('path')}"
        )
        return _shared_warning(rule, checked_paths, reason)
    return None


def _shared_state_role_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    context: CheckContext,
) -> CheckOutcome | None:
    """state 配下のサービス系 role を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        context: CheckContext。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - role が _bridge / _state_holder で終わっていたら NG。
    """
    found_node = _find_tree_node_impl(
        context.data, "src/shared/state")
    state_root_node = _fallback_tree_node(found_node)
    for node in _iter_tree_nodes_impl(state_root_node):
        if node.get("kind") != "file":
            continue
        if not _has_service_like_role(node):
            continue
        reason = (
            "state file has service-like role: "
            f"{node.get('path')}"
        )
        return _shared_warning(rule, checked_paths, reason)
    return None


def _has_service_like_role(node: dict[str, Any]) -> bool:
    """サービス系 role かを判定する。

    Args:
        node: facts ノード。

    Returns:
        bool: _bridge / _state_holder で終われば True。

    Policy:
        - service / state holder 系の suffix を一括判定する。
    """
    role = str(node.get("role", ""))
    if role.endswith("_bridge"):
        return True
    return role.endswith("_state_holder")


def _shared_pyxel_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
) -> CheckOutcome | None:
    """state / services の pyxel 直接利用を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - state は pyxel.* を一切禁止、services は draw だけ禁止。
    """
    state_outcome = _shared_state_pyxel_outcome(
        rule, checked_paths, repo_root)
    if state_outcome is not None:
        return state_outcome
    return _shared_services_pyxel_outcome(
        rule, checked_paths, repo_root)


def _shared_state_pyxel_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
) -> CheckOutcome | None:
    """state 配下の pyxel 利用 hit に対する warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。

    Returns:
        CheckOutcome | None: hit があれば warning。

    Policy:
        - 1 件目の hit だけ報告する。
    """
    state_root = repo_root / "src" / "shared" / "state"
    state_hits = _grep(
        PYXEL_ANY_CALL, list(_iter_py_files_impl(state_root)))
    if not state_hits:
        return None
    reason = (
        "pyxel access in shared/state file: "
        f"{_rel_hit(repo_root, state_hits[0])}"
    )
    return _shared_warning(rule, checked_paths, reason)


def _shared_services_pyxel_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
) -> CheckOutcome | None:
    """services 配下の draw 利用 hit に対する warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。

    Returns:
        CheckOutcome | None: hit があれば warning。

    Policy:
        - SHARED_SERVICE_PYXEL_EXEMPT を除外して走査する。
    """
    services_root = repo_root / "src" / "shared" / "services"
    service_files = _list_service_files(services_root)
    service_hits = _grep(SCENE_DRAW_CALL, service_files)
    if not service_hits:
        return None
    reason = (
        "pyxel draw call in shared/services file: "
        f"{_rel_hit(repo_root, service_hits[0])}"
    )
    return _shared_warning(rule, checked_paths, reason)


def _list_service_files(services_root: Path) -> list[Path]:
    """services 直下の .py から除外対象を引いた list を返す。

    Args:
        services_root: src/shared/services。

    Returns:
        list[Path]: 検査対象 .py ファイル。

    Policy:
        - SHARED_SERVICE_PYXEL_EXEMPT は除く。
    """
    return [
        path for path in services_root.glob("*.py")
        if path.name not in SHARED_SERVICE_PYXEL_EXEMPT
    ]


def _shared_import_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
) -> CheckOutcome | None:
    """runtime/scenes からの legacy import を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - player_state shim → item_use bridge の順に検査する。
    """
    dependency_targets = _collect_runtime_scene_files(repo_root)
    player_outcome = _legacy_import_hit_outcome(
        rule, checked_paths, repo_root, dependency_targets,
        PLAYER_STATE_IMPORT,
        "runtime/scenes import legacy player_state shim",
    )
    if player_outcome is not None:
        return player_outcome
    return _legacy_import_hit_outcome(
        rule, checked_paths, repo_root, dependency_targets,
        ITEM_USE_IMPORT,
        "runtime/scenes import legacy item_use bridge",
    )


def _legacy_import_hit_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    files: list[Path],
    pattern: re.Pattern[str],
    reason_prefix: str,
) -> CheckOutcome | None:
    """指定パターンの hit 1 件目を warning として返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        files: 検査対象ファイル列。
        pattern: 検索する正規表現。
        reason_prefix: warning reason の接頭辞。

    Returns:
        CheckOutcome | None: hit があれば warning。

    Policy:
        - 1 件目で短絡する。
    """
    hits = _grep(pattern, files)
    if not hits:
        return None
    reason = f"{reason_prefix}: {_rel_hit(repo_root, hits[0])}"
    return _shared_warning(rule, checked_paths, reason)


def _collect_runtime_scene_files(repo_root: Path) -> list[Path]:
    """src/runtime と src/scenes 配下の .py を集める。

    Args:
        repo_root: リポジトリルート。

    Returns:
        list[Path]: 走査対象 .py パス列。

    Policy:
        - runtime → scenes の順で連結する。
    """
    files = list(_iter_py_files_impl(repo_root / "src" / "runtime"))
    files.extend(_iter_py_files_impl(repo_root / "src" / "scenes"))
    return files


def _wrapper_chain_present_impl(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """wrapper_chain_present の本体。

    Args:
        context: CheckContext。
        rule: 対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - scope 存在 → facts 一致 → 実コード一致の順に短絡する。
    """
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    scope_outcome = _scope_paths_exist_outcome(
        rule, checked_paths, repo_root, "wrapper_chain_present")
    if scope_outcome is not None:
        return scope_outcome
    facts_outcome = _wrapper_facts_outcome(
        rule, checked_paths, context)
    if facts_outcome is not None:
        return facts_outcome
    return _wrapper_files_outcome(rule, checked_paths, repo_root)


def _scope_paths_exist_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    failed_check: str,
) -> CheckOutcome | None:
    """checked_paths が全て存在することを確認する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        failed_check: warning に載せる check 名。

    Returns:
        CheckOutcome | None: 欠落時のみ warning。

    Policy:
        - 最初に欠けた 1 件を warning にする。
    """
    for rel_path in checked_paths:
        if (repo_root / rel_path).exists():
            continue
        return _warning(
            rule,
            checked_paths,
            failed_check,
            reason=f"missing path: {rel_path}",
        )
    return None


def _wrapper_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    reason: str,
    *,
    expected: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
) -> CheckOutcome:
    """wrapper_chain_present 用の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        reason: 警告理由。
        expected: 期待値 dict。
        observed: 観測値 dict。

    Returns:
        CheckOutcome: failed_check 固定の warning。

    Policy:
        - failed_check を 1 か所に固定する。
    """
    return _warning(
        rule, checked_paths, "wrapper_chain_present",
        reason=reason, expected=expected, observed=observed)


def _wrapper_facts_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    context: CheckContext,
) -> CheckOutcome | None:
    """facts.entry_points.runtime_entry_chain との一致を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        context: CheckContext。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - entry 存在 → paths 一致 → 末尾 symbol の順に検査する。
    """
    entry = _find_entry_point_impl(context.data, "runtime_entry_chain")
    if entry is None:
        return _wrapper_warning(
            rule, checked_paths,
            "facts.entry_points.runtime_entry_chain is missing")
    entry_chain = list(entry.get("nodes", []))
    paths_outcome = _wrapper_entry_paths_outcome(
        rule, checked_paths, entry_chain)
    if paths_outcome is not None:
        return paths_outcome
    return _wrapper_entry_symbol_outcome(
        rule, checked_paths, entry_chain)


def _wrapper_entry_paths_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    entry_chain: list[Any],
) -> CheckOutcome | None:
    """entry_chain の path が scope と一致するかを検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        entry_chain: facts の entry_chain。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - list 一致を厳密判定する。
    """
    entry_paths = [item.get("path") for item in entry_chain]
    if entry_paths == checked_paths:
        return None
    reason = (
        "facts.entry_points.runtime_entry_chain paths "
        "do not match scope"
    )
    return _wrapper_warning(
        rule, checked_paths, reason,
        expected={"scope_paths": checked_paths},
        observed={"entry_chain_paths": entry_paths},
    )


def _wrapper_entry_symbol_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    entry_chain: list[Any],
) -> CheckOutcome | None:
    """entry_chain 末尾の symbol が Game かを検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        entry_chain: facts の entry_chain。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - 末尾 1 要素だけ symbol を見る。
    """
    if entry_chain[-1].get("symbol") == "Game":
        return None
    return _wrapper_warning(
        rule, checked_paths,
        "runtime_game symbol is not Game",
        expected={"runtime_game_symbol": "Game"},
        observed={
            "runtime_game_symbol": entry_chain[-1].get("symbol"),
        },
    )


def _wrapper_files_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
) -> CheckOutcome:
    """main / shim / app の中身を grep で確認する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - main → shim → app の順に固定する。
    """
    main_path = repo_root / "main.py"
    shim_path = repo_root / "src/runtime/main_runtime.py"
    app_path = repo_root / "src/runtime/app.py"
    main_outcome = _wrapper_main_outcome(rule, checked_paths, main_path)
    if main_outcome is not None:
        return main_outcome
    shim_outcome = _wrapper_shim_outcome(rule, checked_paths, shim_path)
    if shim_outcome is not None:
        return shim_outcome
    app_outcome = _wrapper_app_outcome(rule, checked_paths, app_path)
    if app_outcome is not None:
        return app_outcome
    return _ok(rule, checked_paths)


def _wrapper_main_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    main_path: Path,
) -> CheckOutcome | None:
    """main.py の必須行を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        main_path: main.py パス。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - shim を指していて run() を呼ぶことを必須にする。
    """
    if not _file_contains(main_path, "main_runtime.py"):
        return _wrapper_warning(
            rule, checked_paths,
            "main.py does not point at runtime shim")
    if _file_contains(main_path, "run()"):
        return None
    return _wrapper_warning(
        rule, checked_paths, "main.py does not call run()")


def _wrapper_shim_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    shim_path: Path,
) -> CheckOutcome | None:
    """runtime shim の必須行を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        shim_path: main_runtime.py パス。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - Game 再エクスポート、run の import、run 公開を確認する。
    """
    if not _file_contains(shim_path, "from src.runtime.app import Game"):
        return _wrapper_warning(
            rule, checked_paths,
            "runtime shim does not re-export Game")
    if not _file_contains(
            shim_path, "from src.runtime.app import run as _run"):
        return _wrapper_warning(
            rule, checked_paths,
            "runtime shim does not import run() from app")
    if _file_contains(shim_path, "def run()"):
        return None
    return _wrapper_warning(
        rule, checked_paths, "runtime shim does not expose run()")


def _wrapper_app_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    app_path: Path,
) -> CheckOutcome | None:
    """runtime app の必須行を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        app_path: app.py パス。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - class Game と def run() の両方を必須にする。
    """
    if not _file_contains(app_path, "class Game"):
        return _wrapper_warning(
            rule, checked_paths,
            "runtime app does not define Game")
    if _file_contains(app_path, "def run()"):
        return None
    return _wrapper_warning(
        rule, checked_paths, "runtime app does not define run()")


def _distribution_paths_marked_non_source_impl(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """distribution_paths_marked_non_source の本体。

    Args:
        context: CheckContext。
        rule: 対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - facts root の status / source_of_truth → 実ディレクトリの順に短絡する。
    """
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    dist_root = _find_tree_node_impl(context.data, "dist")
    facts_outcome = _dist_facts_outcome(
        rule, checked_paths, dist_root)
    if facts_outcome is not None:
        return facts_outcome
    if not (repo_root / "dist").exists():
        return _dist_warning(
            rule, checked_paths, "dist directory does not exist")
    return _ok(rule, checked_paths)


def _dist_facts_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    dist_root: dict[str, Any] | None,
) -> CheckOutcome | None:
    """dist root の facts 整合を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        dist_root: facts.tree の dist ノード。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - 存在 → status → source_of_truth の順に短絡する。
    """
    if dist_root is None:
        return _dist_warning(
            rule, checked_paths,
            "dist root is missing from facts.tree")
    status_outcome = _dist_status_outcome(
        rule, checked_paths, dist_root)
    if status_outcome is not None:
        return status_outcome
    return _dist_source_of_truth_outcome(
        rule, checked_paths, dist_root)


def _dist_status_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    dist_root: dict[str, Any],
) -> CheckOutcome | None:
    """dist root の status を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        dist_root: facts dist ノード。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - "distribution" 以外は違反扱い。
    """
    if dist_root.get("status") == "distribution":
        return None
    return _dist_warning(
        rule, checked_paths,
        "dist root status is not distribution",
        expected={"status": "distribution"},
        observed={"status": dist_root.get("status")},
    )


def _dist_source_of_truth_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    dist_root: dict[str, Any],
) -> CheckOutcome | None:
    """dist root の source_of_truth を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        dist_root: facts dist ノード。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - False 以外は違反扱い。
    """
    if dist_root.get("source_of_truth") is False:
        return None
    return _dist_warning(
        rule, checked_paths,
        "dist root source_of_truth is not false",
        expected={"source_of_truth": False},
        observed={"source_of_truth": dist_root.get("source_of_truth")},
    )


def _dist_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    reason: str,
    *,
    expected: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
) -> CheckOutcome:
    """distribution_paths_marked_non_source 用の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        reason: 警告理由。
        expected: 期待値 dict。
        observed: 観測値 dict。

    Returns:
        CheckOutcome: failed_check 固定の warning。

    Policy:
        - failed_check を 1 か所に固定する。
    """
    return _warning(
        rule, checked_paths,
        "distribution_paths_marked_non_source",
        reason=reason, expected=expected, observed=observed)


def _generated_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    reason: str,
    *,
    expected: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
) -> CheckOutcome:
    """generated entries 用の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        reason: 警告理由。
        expected: 期待値 dict。
        observed: 観測値 dict。

    Returns:
        CheckOutcome: failed_check 固定の warning。

    Policy:
        - failed_check を 1 か所に固定する。
    """
    return _warning(
        rule, checked_paths,
        "generated_entries_mark_non_hand_editable_and_sources",
        reason=reason, expected=expected, observed=observed)


def _generated_entries_check_impl(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """generated_entries_mark_non_hand_editable_and_sources の本体。

    Args:
        context: CheckContext。
        rule: 対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - gen_data.py 存在 → 各 entry の点検の順に短絡する。
    """
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    entries = _generated_file_nodes_impl(context.data)
    if not (repo_root / "tools/gen_data.py").is_file():
        return _generated_warning(
            rule, checked_paths, "tools/gen_data.py is missing")
    entries_outcome = _generated_entries_iter_outcome(
        rule, checked_paths, repo_root, entries)
    if entries_outcome is not None:
        return entries_outcome
    return _ok(rule, checked_paths)


def _generated_entries_iter_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    entries: list[dict[str, Any]],
) -> CheckOutcome | None:
    """各 entry を順に検査して最初の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        entries: generated entry ノード列。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - 1 件目の違反で短絡する。
    """
    for entry in entries:
        outcome = _generated_entry_outcome(
            rule, checked_paths, repo_root, entry)
        if outcome is not None:
            return outcome
    return None


def _generated_entry_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    entry: dict[str, Any],
) -> CheckOutcome | None:
    """1 件の generated entry を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        entry: 単一 entry ノード。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - target 実在 → hand_editable → sources の順に短絡する。
    """
    rel_path = entry.get("path")
    if not _is_existing_generated_target(repo_root, rel_path):
        return _generated_warning(
            rule, checked_paths,
            f"generated target is missing: {rel_path}")
    hand_editable_outcome = _generated_hand_editable_outcome(
        rule, checked_paths, entry)
    if hand_editable_outcome is not None:
        return hand_editable_outcome
    return _generated_sources_outcome(
        rule, checked_paths, repo_root, entry)


def _is_existing_generated_target(
    repo_root: Path,
    rel_path: Any,
) -> bool:
    """generated target が存在ファイルかを判定する。

    Args:
        repo_root: リポジトリルート。
        rel_path: 対象 path。

    Returns:
        bool: 実ファイルなら True。

    Policy:
        - None / 空文字も無効として扱う。
    """
    if not rel_path:
        return False
    return (repo_root / rel_path).is_file()


def _generated_hand_editable_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    entry: dict[str, Any],
) -> CheckOutcome | None:
    """hand_editable == False かを検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        entry: generated entry。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - False 以外（True / None など）はすべて違反とする。
    """
    if entry.get("hand_editable") is False:
        return None
    return _generated_warning(
        rule, checked_paths,
        f"hand_editable must be false for {entry.get('id')}",
        expected={
            "hand_editable": False,
            "generated_from_prefix": "assets/",
        },
        observed={
            "entry_id": entry.get("id"),
            "hand_editable": entry.get("hand_editable"),
        },
    )


def _generated_sources_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    entry: dict[str, Any],
) -> CheckOutcome | None:
    """generated_from の prefix と実在を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        entry: generated entry。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - sources が空 / list 外なら欠落として扱う。
    """
    sources = entry.get("generated_from")
    if _is_invalid_generated_sources(sources):
        return _generated_warning(
            rule, checked_paths,
            f"generated_from is missing for {entry.get('id')}")
    for source in sources:
        outcome = _generated_source_outcome(
            rule, checked_paths, repo_root, entry, source, sources)
        if outcome is not None:
            return outcome
    return None


def _is_invalid_generated_sources(sources: Any) -> bool:
    """sources が list で非空でないかを判定する。

    Args:
        sources: 検査対象。

    Returns:
        bool: list でない、または空のとき True。

    Policy:
        - None も list でない扱いで True。
    """
    if not isinstance(sources, list):
        return True
    return not sources


def _generated_source_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    entry: dict[str, Any],
    source: Any,
    sources: list[Any],
) -> CheckOutcome | None:
    """1 件の source を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        entry: generated entry。
        source: 検査対象 source。
        sources: source 一覧（observed 用）。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - assets/ prefix → 実在の順に検査する。
    """
    if not str(source).startswith("assets/"):
        return _build_generated_prefix_warning(
            rule, checked_paths, entry, sources)
    if (repo_root / source).is_file():
        return None
    return _generated_warning(
        rule, checked_paths,
        f"generated source is missing: {source}")


def _build_generated_prefix_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    entry: dict[str, Any],
    sources: list[Any],
) -> CheckOutcome:
    """generated_from の prefix 違反 warning を組み立てる。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        entry: generated entry。
        sources: source 一覧。

    Returns:
        CheckOutcome: 警告。

    Policy:
        - expected / observed を毎回同じ形で添える。
    """
    reason = (
        "generated_from must point to assets/* "
        f"for {entry.get('id')}"
    )
    return _generated_warning(
        rule, checked_paths, reason,
        expected=_generated_prefix_expected(),
        observed=_generated_prefix_observed(entry, sources),
    )


def _generated_prefix_expected() -> dict[str, Any]:  # noqa: CR100
    """generated prefix 違反の expected dict を返す。

    Returns:
        dict[str, Any]: 期待値。

    Policy:
        - 定数値を 1 か所に集める。
    """
    return {
        "hand_editable": False,
        "generated_from_prefix": "assets/",
    }


def _generated_prefix_observed(  # noqa: CR100
    entry: dict[str, Any],
    sources: list[Any],
) -> dict[str, Any]:
    """generated prefix 違反の observed dict を返す。

    Args:
        entry: generated entry。
        sources: source 一覧。

    Returns:
        dict[str, Any]: 観測値。

    Policy:
        - entry_id と sources をそのまま添える。
    """
    return {
        "entry_id": entry.get("id"),
        "generated_from": sources,
    }


def _codemaker_manifest_check_impl(  # noqa: CR100
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """codemaker_manifest_includes_required_paths の本体。

    Args:
        context: CheckContext。
        rule: 対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - contract 取得 → manifest 整合 → 必須 path の順で短絡する。
    """
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    contract = _find_codemaker_bundle_contract_impl(
        context.data, "codemaker_non_scene_bundle")
    contract_outcome = _codemaker_contract_outcome(
        rule, checked_paths, contract)
    if contract_outcome is not None:
        return contract_outcome
    manifest_outcome = _codemaker_manifest_outcome(
        rule, checked_paths, repo_root, contract)
    if manifest_outcome is not None:
        return manifest_outcome
    return _codemaker_required_paths_outcome(
        rule, checked_paths, repo_root, contract)


def _codemaker_contract_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    contract: dict[str, Any] | None,
) -> CheckOutcome | None:
    """contract 存在の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        contract: 取得済み contract。

    Returns:
        CheckOutcome | None: 不在時のみ warning。

    Policy:
        - 後段検査の前提として contract 存在を保証する。
    """
    if contract is not None:
        return None
    return _codemaker_warning(
        rule, checked_paths,
        "facts.codemaker_bundle_contracts."
        "codemaker_non_scene_bundle is missing",
    )


def _codemaker_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    reason: str,
    *,
    expected: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
) -> CheckOutcome:
    """codemaker bundle 用の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        reason: 警告理由。
        expected: 期待値 dict。
        observed: 観測値 dict。

    Returns:
        CheckOutcome: failed_check 固定の warning。

    Policy:
        - failed_check を 1 か所に固定する。
    """
    return _warning(
        rule, checked_paths,
        "codemaker_manifest_includes_required_paths",
        reason=reason, expected=expected, observed=observed)


def _codemaker_manifest_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    contract: dict[str, Any],
) -> CheckOutcome | None:
    """manifest_path の取得と実在の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        contract: bundle contract。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - 型 → 実在の順に短絡する。
    """
    manifest_rel = contract.get("manifest_path")
    if _is_invalid_manifest_rel(manifest_rel):
        return _codemaker_warning(
            rule, checked_paths,
            "manifest_path is missing from "
            "codemaker bundle contract")
    manifest_path = repo_root / manifest_rel
    if manifest_path.is_file():
        return None
    return _codemaker_warning(
        rule, checked_paths,
        f"manifest file is missing: {manifest_rel}")


def _is_invalid_manifest_rel(manifest_rel: Any) -> bool:
    """manifest_rel が str で非空でないかを判定する。

    Args:
        manifest_rel: 検査対象。

    Returns:
        bool: str でない、または空のとき True。

    Policy:
        - None と空文字を同等に扱う。
    """
    if not isinstance(manifest_rel, str):
        return True
    return not manifest_rel


def _codemaker_required_paths_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    contract: dict[str, Any],
) -> CheckOutcome:
    """required_paths と manifest 内容の整合を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        contract: bundle contract。

    Returns:
        CheckOutcome: ok または warning。

    Policy:
        - non-empty 検査 → 実在検査 → manifest 同梱検査の順に短絡する。
    """
    required_paths = contract.get("required_paths", [])
    if _is_invalid_required_paths(required_paths):
        return _codemaker_warning(
            rule, checked_paths,
            "required_paths is empty in "
            "codemaker bundle contract")
    disk_outcome = _codemaker_disk_outcome(
        rule, checked_paths, repo_root, required_paths)
    if disk_outcome is not None:
        return disk_outcome
    return _codemaker_manifest_entries_outcome(
        rule, checked_paths, repo_root, contract, required_paths)


def _codemaker_disk_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    required_paths: list[Any],
) -> CheckOutcome | None:
    """required_paths がディスク上に揃っているかを返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        required_paths: contract.required_paths。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - 最初の欠落 1 件で短絡する。
    """
    for rel_path in required_paths:
        if (repo_root / rel_path).is_file():
            continue
        return _codemaker_warning(
            rule, checked_paths,
            f"required bundle path is missing on disk: {rel_path}")
    return None


def _codemaker_manifest_entries_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    contract: dict[str, Any],
    required_paths: list[Any],
) -> CheckOutcome:
    """manifest entries が required_paths を網羅しているかを返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        contract: bundle contract。
        required_paths: 必須 path 列。

    Returns:
        CheckOutcome: ok または warning。

    Policy:
        - 集合差で missing を抽出して 1 度だけ報告する。
    """
    missing_paths = _compute_missing_manifest_paths(
        repo_root, contract, required_paths)
    if not missing_paths:
        return _ok(rule, checked_paths)
    return _codemaker_warning(
        rule, checked_paths,
        "required non-scene bundle paths are missing "
        "from manifest",
        expected={"required_paths": required_paths},
        observed={"missing_paths": missing_paths},
    )


def _compute_missing_manifest_paths(  # noqa: CR100
    repo_root: Path,
    contract: dict[str, Any],
    required_paths: list[Any],
) -> list[Any]:
    """manifest 内に無い required path を返す。

    Args:
        repo_root: リポジトリルート。
        contract: bundle contract。
        required_paths: 必須 path 列。

    Returns:
        list[Any]: 不足 path 列。

    Policy:
        - manifest_path を contract から引き、entries を 1 度だけ読む。
    """
    manifest_rel = contract["manifest_path"]
    manifest_path = repo_root / manifest_rel
    entries = set(_manifest_entries(manifest_path))
    return [path for path in required_paths if path not in entries]


def _command_script_paths(command: str) -> list[str]:
    """command 文字列から .py スクリプトパスを取り出す。

    Args:
        command: shell command 文字列。

    Returns:
        list[str]: .py で終わる token の list。

    Policy:
        - `-c` を含む inline コマンドは対象外として空 list を返す。
    """
    tokens = shlex.split(command)
    if "-c" in tokens:
        return []
    return [token for token in tokens if token.endswith(".py")]


def _compare_runbook_commands_impl(
    context: CheckContext,
    rule: dict[str, Any],
) -> CheckOutcome:
    """compare_runbook_commands_and_artifact_defs の本体。

    Args:
        context: CheckContext。
        rule: 対象 rule。

    Returns:
        CheckOutcome: ok または最初の warning。

    Policy:
        - scope 存在 → runbook 走査の順に短絡する。
    """
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    artifact_paths = {
        item["path"]
        for item in _distribution_artifact_nodes_impl(context.data)
    }
    runbooks = context.data["facts"].get("runbooks", [])
    scope_outcome = _runbook_scope_outcome(
        rule, checked_paths, repo_root)
    if scope_outcome is not None:
        return scope_outcome
    runbook_outcome = _runbook_iter_outcome(
        rule, checked_paths, repo_root, runbooks, artifact_paths)
    if runbook_outcome is not None:
        return runbook_outcome
    return _ok(rule, checked_paths)


def _runbook_scope_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
) -> CheckOutcome | None:
    """scope の各 path が存在するかを検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。

    Returns:
        CheckOutcome | None: 不在時のみ warning。

    Policy:
        - 最初に欠けた 1 件だけ報告する。
    """
    return _scope_paths_exist_outcome(
        rule,
        checked_paths,
        repo_root,
        "compare_runbook_commands_and_artifact_defs",
    )


def _runbook_iter_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    runbooks: list[Any],
    artifact_paths: set[str],
) -> CheckOutcome | None:
    """runbook 列の step を順に検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        runbooks: facts.runbooks。
        artifact_paths: 既知 artifact path 集合。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - runbook × step を二重ループする。
    """
    for runbook in runbooks:
        for step in runbook.get("steps", []):
            outcome = _runbook_step_outcome(
                rule, checked_paths, repo_root, step, artifact_paths)
            if outcome is not None:
                return outcome
    return None


def _runbook_step_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    step: dict[str, Any],
    artifact_paths: set[str],
) -> CheckOutcome | None:
    """1 つの step を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        step: runbook 1 step。
        artifact_paths: 既知 artifact path 集合。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - スクリプト実在 → 出力検査の順で短絡する。
    """
    command = step.get("command", "")
    script_outcome = _runbook_script_outcome(
        rule, checked_paths, repo_root, command)
    if script_outcome is not None:
        return script_outcome
    return _runbook_outputs_outcome(
        rule, checked_paths, repo_root, step, artifact_paths)


def _runbook_script_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    command: str,
) -> CheckOutcome | None:
    """command が参照するスクリプトの実在を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        command: step.command。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - inline `-c` 形式は対象外。
    """
    for script_path in _command_script_paths(command):
        if (repo_root / script_path).exists():
            continue
        return _runbook_warning(
            rule, checked_paths,
            "runbook command references missing script: "
            f"{script_path}")
    return None


def _runbook_outputs_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    step: dict[str, Any],
    artifact_paths: set[str],
) -> CheckOutcome | None:
    """step.outputs と artifact_paths の対応を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        step: 1 step。
        artifact_paths: 既知 artifact path 集合。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - 各 output を順に検査する。
    """
    for output_path in step.get("outputs", []):
        outcome = _runbook_single_output_outcome(
            rule, checked_paths, repo_root, output_path, artifact_paths)
        if outcome is not None:
            return outcome
    return None


def _runbook_single_output_outcome(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    repo_root: Path,
    output_path: str,
    artifact_paths: set[str],
) -> CheckOutcome | None:
    """1 件の output_path を検査する。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        repo_root: リポジトリルート。
        output_path: 検査対象 path。
        artifact_paths: 既知 artifact path 集合。

    Returns:
        CheckOutcome | None: 違反時のみ warning。

    Policy:
        - artifact 宣言 → 実在の順に短絡する。
    """
    if output_path not in artifact_paths:
        return _build_runbook_undeclared_warning(
            rule, checked_paths, output_path, artifact_paths)
    if (repo_root / output_path).exists():
        return None
    return _runbook_warning(
        rule, checked_paths,
        f"distribution artifact path is missing: {output_path}")


def _runbook_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    reason: str,
    *,
    expected: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
) -> CheckOutcome:
    """compare_runbook_commands_and_artifact_defs 用の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        reason: 警告理由。
        expected: 期待値 dict。
        observed: 観測値 dict。

    Returns:
        CheckOutcome: failed_check 固定の warning。

    Policy:
        - failed_check を 1 か所に固定する。
    """
    return _warning(
        rule, checked_paths,
        "compare_runbook_commands_and_artifact_defs",
        reason=reason, expected=expected, observed=observed)


def _build_runbook_undeclared_warning(  # noqa: CR100
    rule: dict[str, Any],
    checked_paths: list[str],
    output_path: str,
    artifact_paths: set[str],
) -> CheckOutcome:
    """runbook output 未宣言の warning を返す。

    Args:
        rule: 対象 rule。
        checked_paths: 検査対象パス列。
        output_path: 違反 path。
        artifact_paths: 既知 artifact path 集合。

    Returns:
        CheckOutcome: warning。

    Policy:
        - artifact_paths は sort して expected に入れる。
    """
    reason = (
        "runbook output not declared as distribution "
        f"artifact: {output_path}"
    )
    return _runbook_warning(
        rule, checked_paths, reason,
        expected={"artifact_paths": sorted(artifact_paths)},
        observed={"missing_output": output_path},
    )


CHECK_REGISTRY = {
    "wrapper_chain_present": wrapper_chain_present,
    "distribution_paths_marked_non_source":
        distribution_paths_marked_non_source,
    "generated_entries_mark_non_hand_editable_and_sources":
        generated_entries_mark_non_hand_editable_and_sources,
    "scene_static_boundary_checks": scene_static_boundary_checks,
    "codemaker_manifest_includes_required_paths":
        codemaker_manifest_includes_required_paths,
    "shared_directory_role_checks": shared_directory_role_checks,
    "compare_runbook_commands_and_artifact_defs":
        compare_runbook_commands_and_artifact_defs,
}


def _run_deterministic_rule_impl(
    context: CheckContext,
    rule: dict[str, Any],
) -> dict[str, Any]:
    """run_deterministic_rule の本体。

    Args:
        context: CheckContext。
        rule: 対象 rule。

    Returns:
        dict[str, Any]: result_record の dict。

    Policy:
        - 順に走らせて ok 以外で短絡する。
    """
    checks = list(rule.get("evidence", {}).get("checks", []))
    if not checks:
        raise KeyError(f"rule {rule.get('id')} has no evidence.checks")
    outcome = _ok(rule, _scope_paths(rule))
    for check_name in checks:
        outcome = _invoke_check(context, rule, check_name)
        if outcome.status != "ok":
            break
    return _result_record_impl(rule, outcome)


def _invoke_check(
    context: CheckContext,
    rule: dict[str, Any],
    check_name: str,
) -> CheckOutcome:
    """check_name に対応する関数を CHECK_REGISTRY から引いて呼ぶ。

    Args:
        context: CheckContext。
        rule: 対象 rule。
        check_name: check 名。

    Returns:
        CheckOutcome: check 関数の戻り値。

    Raises:
        KeyError: 未登録 check 名のとき。

    Policy:
        - 未登録なら早期 raise する。
    """
    fn = CHECK_REGISTRY.get(check_name)
    if fn is None:
        raise KeyError(f"no check function registered for {check_name}")
    return fn(context, rule)


def _result_record_impl(
    rule: dict[str, Any],
    outcome: CheckOutcome,
) -> dict[str, Any]:
    """result_record の本体。

    Args:
        rule: 対象 rule。
        outcome: rule 走行結果。

    Returns:
        dict[str, Any]: 結果 dict。

    Policy:
        - rule.__rules_path はそのまま str 化して保持する。
    """
    return {
        "rule_id": rule["id"],
        "status": outcome.status,
        "severity": rule.get("severity"),
        "mode": rule["enforcement"]["mode"],
        "coverage": dict(rule.get("coverage", {})),
        "checked_paths": outcome.checked_paths,
        "failed_checks": outcome.failed_checks,
        "message": outcome.message,
        "suggested_actions": outcome.suggested_actions,
        "reason": outcome.reason,
        "expected": outcome.expected,
        "observed": outcome.observed,
        "rule_source": str(rule.get("__rules_path", "")),
    }


def _build_coverage_review_impl(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """build_coverage_review の本体。

    Args:
        results: 各 rule の結果 dict 列。

    Returns:
        dict[str, Any]: 自動化レビュー dict。

    Policy:
        - 集計内部状態はローカル dict で初期化して順に埋める。
    """
    state = _new_coverage_state()
    for item in results:
        _accumulate_coverage_item(state, item)
    return _coverage_state_to_dict(state)


def _new_coverage_state() -> dict[str, Any]:  # noqa: CR100
    """coverage review の集計用 state を初期化する。

    Returns:
        dict[str, Any]: 初期化済み state。

    Policy:
        - mode_counts はキーを固定して欠落分を 0 で始める。
    """
    return {
        "mode_counts": {
            "deterministic": 0,
            "llm_assisted": 0,
            "manual": 0,
        },
        "deterministic_candidate_rule_ids": [],
        "next_checker_units": [],
        "repair_candidate_rule_ids": [],
        "repair_implemented_rule_ids": [],
        "keep_non_deterministic_rule_ids": [],
    }


def _accumulate_coverage_item(
    state: dict[str, Any],
    item: dict[str, Any],
) -> None:
    """1 件の result item を state に積む。

    Args:
        state: coverage 集計 state。
        item: 1 件の result dict。

    Policy:
        - mode → deterministic_review → autofix の順に処理する。
    """
    _accumulate_mode_count(state, item)
    _accumulate_deterministic_review(state, item)
    _accumulate_autofix(state, item)


def _accumulate_mode_count(
    state: dict[str, Any],
    item: dict[str, Any],
) -> None:
    """mode_counts を更新する。

    Args:
        state: coverage state。
        item: result item。

    Policy:
        - mode_counts に無い mode は無視する。
    """
    mode = item["mode"]
    if mode not in state["mode_counts"]:
        return
    state["mode_counts"][mode] += 1


def _accumulate_deterministic_review(
    state: dict[str, Any],
    item: dict[str, Any],
) -> None:
    """deterministic_review に応じて state を更新する。

    Args:
        state: coverage state。
        item: result item。

    Policy:
        - candidate と keep 系で分岐する。
    """
    coverage = item.get("coverage", {})
    deterministic_review = coverage.get("deterministic_review")
    if deterministic_review == "candidate":
        _append_candidate_review(state, item, coverage)
        return
    if deterministic_review in {"keep_llm_assisted", "keep_manual"}:
        state["keep_non_deterministic_rule_ids"].append(item["rule_id"])


def _append_candidate_review(
    state: dict[str, Any],
    item: dict[str, Any],
    coverage: dict[str, Any],
) -> None:
    """candidate な review を state に追記する。

    Args:
        state: coverage state。
        item: result item。
        coverage: item.coverage。

    Policy:
        - next_checker_unit があれば対応行も加える。
    """
    state["deterministic_candidate_rule_ids"].append(item["rule_id"])
    next_checker_unit = coverage.get("next_checker_unit")
    if not next_checker_unit:
        return
    state["next_checker_units"].append({
        "rule_id": item["rule_id"],
        "unit": next_checker_unit,
    })


def _accumulate_autofix(
    state: dict[str, Any],
    item: dict[str, Any],
) -> None:
    """autofix 値に応じて candidate/implemented の rule_id 列を更新する。

    Args:
        state: coverage state。
        item: result item。

    Policy:
        - 値が無いときや想定外のときは無視する。
    """
    coverage = item.get("coverage", {})
    autofix_key = _coverage_autofix_key(coverage)
    if autofix_key is None:
        return
    repair_autofix = coverage.get(autofix_key)
    if repair_autofix == "candidate":
        state["repair_candidate_rule_ids"].append(item["rule_id"])
        return
    if repair_autofix == "implemented":
        state["repair_implemented_rule_ids"].append(item["rule_id"])


def _coverage_state_to_dict(  # noqa: CR100
    state: dict[str, Any],
) -> dict[str, Any]:
    """coverage state を出力 dict に整える。

    Args:
        state: 集計 state。

    Returns:
        dict[str, Any]: 出力 dict。

    Policy:
        - キー順を仕様で固定する。
    """
    return {
        "mode_counts": state["mode_counts"],
        "deterministic_candidate_rule_ids":
            state["deterministic_candidate_rule_ids"],
        "next_checker_units": state["next_checker_units"],
        "repair_candidate_rule_ids":
            state["repair_candidate_rule_ids"],
        "repair_implemented_rule_ids":
            state["repair_implemented_rule_ids"],
        "keep_non_deterministic_rule_ids":
            state["keep_non_deterministic_rule_ids"],
    }


def _build_output_impl(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """build_output の本体。

    Args:
        results: 各 rule の結果 dict 列。

    Returns:
        dict[str, Any]: CLI 出力 dict。

    Policy:
        - summary 計算と coverage_review を 1 か所で組み立てる。
    """
    summary = _build_summary(results)
    return {
        "run_ok": summary["error_rules"] == 0,
        "has_warnings": summary["warning_rules"] > 0,
        "summary": summary,
        "coverage_review": _build_coverage_review_impl(results),
        "results": results,
    }


def _build_summary(results: list[dict[str, Any]]) -> dict[str, int]:
    """summary 用の集計 dict を組み立てる。

    Args:
        results: 各 rule の結果 dict 列。

    Returns:
        dict[str, int]: status ごとの件数。

    Policy:
        - executed は ok + warning とし、skipped/error と分ける。
    """
    return {
        "total_rules": len(results),
        "executed_rules": _count_statuses(results, {"ok", "warning"}),
        "warning_rules": _count_statuses(results, {"warning"}),
        "skipped_rules": _count_statuses(results, {"skipped"}),
        "error_rules": _count_statuses(results, {"error"}),
    }


def _count_statuses(
    results: list[dict[str, Any]],
    statuses: set[str],
) -> int:
    """指定 status の件数を返す。

    Args:
        results: 結果 dict 列。
        statuses: カウント対象 status 集合。

    Returns:
        int: 該当件数。

    Policy:
        - 集合判定で複数 status を 1 度に数える。
    """
    return sum(1 for item in results if item["status"] in statuses)


def _run_checker_impl(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    """run_checker の本体。

    Args:
        repo_root: リポジトリルート。
        rules_path: rules YAML。
        rule_ids: 走らせたい id 集合。

    Returns:
        dict[str, Any]: build_output dict。

    Policy:
        - 非 deterministic は skipped で残し、coverage_review に集計させる。
    """
    repo_root = repo_root.resolve()
    rules_path = rules_path.resolve()
    data = load_rules(rules_path)
    context = CheckContext(
        repo_root=repo_root,
        rules_path=rules_path,
        data=data,
    )
    results = _collect_rule_results(context, data, rules_path, rule_ids)
    return _build_output_impl(results)


def _collect_rule_results(
    context: CheckContext,
    data: dict[str, Any],
    rules_path: Path,
    rule_ids: set[str] | None,
) -> list[dict[str, Any]]:
    """validation_rules を走らせて結果 dict 列を返す。

    Args:
        context: CheckContext。
        data: rules dict。
        rules_path: rules YAML パス。
        rule_ids: フィルタ集合。

    Returns:
        list[dict[str, Any]]: 結果 dict 列。

    Policy:
        - rule_ids が None なら全件、そうでなければ集合で絞る。
    """
    results: list[dict[str, Any]] = []
    for rule in data["validation_rules"]:
        rule["__rules_path"] = str(rules_path)
        if _is_filtered_out(rule, rule_ids):
            continue
        results.append(_evaluate_single_rule(context, rule))
    return results


def _is_filtered_out(
    rule: dict[str, Any],
    rule_ids: set[str] | None,
) -> bool:
    """rule_ids フィルタで除外すべきかを判定する。

    Args:
        rule: rule dict。
        rule_ids: フィルタ集合または None。

    Returns:
        bool: 除外なら True。

    Policy:
        - None は全件通すために False を返す。
    """
    if rule_ids is None:
        return False
    return rule["id"] not in rule_ids


def _evaluate_single_rule(
    context: CheckContext,
    rule: dict[str, Any],
) -> dict[str, Any]:
    """1 件の rule を mode に応じて評価する。

    Args:
        context: CheckContext。
        rule: rule dict。

    Returns:
        dict[str, Any]: 結果 dict。

    Policy:
        - deterministic 以外は skipped にする。
    """
    mode = rule["enforcement"]["mode"]
    if mode != "deterministic":
        return _result_record_impl(rule, _skipped(rule))
    return _run_deterministic_rule_impl(context, rule)


def _main_impl(argv: list[str] | None) -> int:  # noqa: CR100
    """main の本体。

    Args:
        argv: 引数列。

    Returns:
        int: 終了コード。

    Policy:
        - 例外は str 化して stderr に流し、1 で終了する。
    """
    args = _parse_main_args(argv)
    result = _run_checker_from_args(args)
    if result is None:
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return _exit_code_for_result(args, result)


def _parse_main_args(argv: list[str] | None) -> argparse.Namespace:
    """argparse で main の引数を解析する。

    Args:
        argv: 引数列。

    Returns:
        argparse.Namespace: 解析済み引数。

    Policy:
        - 既存 CLI と完全に同じ option を維持する。
    """
    parser = _build_main_parser()
    return parser.parse_args(argv)


def _build_main_parser() -> argparse.ArgumentParser:
    """main 用の argparse パーサを組み立てる。

    Returns:
        argparse.ArgumentParser: 設定済みパーサ。

    Policy:
        - option 定義は path / rule / flag に分けて helper に委譲する。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    _add_path_args(parser)
    _add_rule_filter_args(parser)
    _add_flag_args(parser)
    return parser


def _add_path_args(parser: argparse.ArgumentParser) -> None:
    """repo-root / rules-path の引数を登録する。

    Args:
        parser: 設定対象 parser。

    Policy:
        - 既定値を ROOT 起点で固定する。
    """
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=ROOT / "docs" / "architecture_rules.yml",
        help="path to architecture rules YAML",
    )


def _add_rule_filter_args(parser: argparse.ArgumentParser) -> None:
    """--rule-id を登録する。

    Args:
        parser: 設定対象 parser。

    Policy:
        - repeatable な append オプションにする。
    """
    parser.add_argument(
        "--rule-id",
        action="append",
        default=[],
        help="run only the specified rule id (repeatable)",
    )


def _add_flag_args(parser: argparse.ArgumentParser) -> None:
    """--fail-on-warning を登録する。

    Args:
        parser: 設定対象 parser。

    Policy:
        - store_true で従来挙動を維持する。
    """
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="return exit 1 when warnings remain",
    )


def _run_checker_from_args(
    args: argparse.Namespace,
) -> dict[str, Any] | None:
    """args に従って run_checker を呼ぶ。失敗時は None。

    Args:
        args: argparse 結果。

    Returns:
        dict[str, Any] | None: 結果 dict。失敗時 None。

    Policy:
        - 例外は str 化して stderr に流す。
    """
    try:
        return run_checker(
            args.repo_root,
            args.rules_path,
            rule_ids=set(args.rule_id) if args.rule_id else None,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return None


def _exit_code_for_result(
    args: argparse.Namespace,
    result: dict[str, Any],
) -> int:
    """結果に基づく終了コードを返す。

    Args:
        args: argparse 結果。
        result: build_output dict。

    Returns:
        int: 終了コード。

    Policy:
        - --fail-on-warning と has_warnings の AND のみで 1 を返す。
    """
    if _should_fail_on_warning(args, result):
        return 1
    return 0


def _should_fail_on_warning(  # noqa: CR100
    args: argparse.Namespace,
    result: dict[str, Any],
) -> bool:
    """--fail-on-warning 指定 + warning 残存かを判定する。

    Args:
        args: argparse 結果。
        result: build_output dict。

    Returns:
        bool: 両方真なら True。

    Policy:
        - 単独条件で短絡判定する。
    """
    if not args.fail_on_warning:
        return False
    return bool(result["has_warnings"])


if __name__ == "__main__":
    raise SystemExit(main())
