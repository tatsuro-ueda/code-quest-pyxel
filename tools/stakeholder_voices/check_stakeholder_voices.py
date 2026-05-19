"""stakeholder_voices.yml の deterministic rule を warning 形式で検証する CLI。

このファイルに含まれる関数・クラス：

- CLI 入口の public 関数 main（引数解析と JSON 出力と exit code 制御）
- 1 回ぶん rule 群を回して payload を組み立てる public 関数 run_checker
- YAML を読んで骨格 schema を点検する public 関数 load_rules
- load_rules から呼ばれる骨格 schema validator の public 関数 validate_rules_schema
- 1 つの rule に紐づく checks を順に回す public 関数 run_rule
- check 名と関数を結ぶ public dict CHECK_REGISTRY
- 10 種類の deterministic check 関数（check_* 公開 API、本体は private helper に委譲）
- CheckContext / CheckOutcome の値オブジェクト dataclass

Problems:
    - YAML ベースの rule 検査を 1 関数で書くと、骨格 schema 点検と個別 check
      が混ざり、どこを直せばよいか読み手の判断がブレる。
    - public 関数に for/if を直接書くと、入口契約と実装詳細が同じ高度で並び、
      AI 補助のリファクタ判断で迷いの原因になる。

Solutions:
    - 本 CLI を deterministic 検査の入口に固定し、骨格 schema 点検と
      個別 check を別レイヤとして並べる。
    - public 関数は「述語呼び出し + private 委譲 + return」のステップ列に揃え、
      ループや分岐は private helper に切り出す。
"""
from __future__ import annotations

import argparse
import json
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
VALID_ACCEPTANCE_VERIFICATION_MODES = {"deterministic", "manual"}
TRACKED_TRACE_STATUSES = {"active", "later", "wont"}


# === Public API ===


@dataclass
class CheckContext:

    # === Public API ===

    repo_root: Path
    rules_path: Path
    data: dict[str, Any]


@dataclass
class CheckOutcome:

    # === Public API ===

    status: str
    checked_paths: list[str]
    failed_checks: list[str] = field(default_factory=list)
    message: str | None = None
    suggested_actions: list[str] = field(default_factory=list)
    expected: dict[str, Any] | None = None
    observed: dict[str, Any] | None = None


def load_rules(path: Path) -> dict[str, Any]:
    """YAML を読み込み骨格 schema を点検した dict を返す。

    Args:
        path: 検査対象 YAML のパス。
    Returns:
        骨格 schema を満たした dict。
    Policy:
        - public 関数はステップ列に揃え、YAML 解析と骨格 schema 点検は
          private helper に委ねる。
    """
    data = _load_yaml_dict(path)
    _require_top_level_keys(data)
    validate_rules_schema(data)
    return data


def validate_rules_schema(data: dict[str, Any]) -> None:
    """rule YAML の骨格を点検する。

    Args:
        data: 解析済みの YAML dict。
    Policy:
        - public 関数はステップ列に揃え、facts / tasknote_contracts /
          validation_rules の検査は private helper に切り出す。
    """
    _validate_facts_section(data)
    _validate_tasknote_contracts(data)
    _validate_validation_rules(data)


def run_rule(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """1 つの rule に紐づく checks を順に回す。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        最初に warning を返した check の CheckOutcome。全て ok なら ok。
    Policy:
        - public 関数はステップ列に揃え、CHECK_REGISTRY との照合と
          ループは private helper に委ねる。
    """
    return _run_rule_checks(ctx, rule)


def run_checker(
    repo_root: Path,
    rules_path: Path,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    """1 回ぶん rule 群を回して payload を組み立てる。

    Args:
        repo_root: リポジトリのルート。
        rules_path: 検査対象 YAML のパス。
        rule_ids: 限定実行する rule id 集合（None で全件）。
    Returns:
        run_ok / has_warnings / summary / results を含む payload。
    Policy:
        - public 関数はステップ列に揃え、rule 選定・実行ループ・payload
          整形は private helper に委ねる。
    """
    data = load_rules(rules_path)
    ctx = CheckContext(repo_root=repo_root, rules_path=rules_path, data=data)
    selected_rules = _select_rules(data, rule_ids)
    results, warning_count = _run_selected_rules(ctx, selected_rules)
    return _build_run_payload(selected_rules, results, warning_count)


def check_id_uniqueness(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """id の重複を検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        重複が無ければ ok、あれば warning。
    Policy:
        - public 関数はステップ列に揃え、id 収集と重複判定は private
          helper に委ねる。
    """
    return _run_id_uniqueness_check(ctx, rule)


def check_stakeholder_reference_integrity(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """request / requirement が参照する stakeholder の存在を検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        全 stakeholder が存在すれば ok、欠落があれば warning。
    Policy:
        - public 関数はステップ列に揃え、欠落抽出と warning 組み立ては
          private helper に委ねる。
    """
    return _run_stakeholder_reference_check(ctx, rule)


def check_request_reference_integrity(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """requirement.derived_from_request_ids の参照先存在を検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        全 request id が解決できれば ok、未解決があれば warning。
    Policy:
        - public 関数はステップ列に揃え、参照先解決は private helper に委ねる。
    """
    return _run_request_reference_check(ctx, rule)


def check_requirement_has_code_hints(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """active な requirement が code hint を持つかを検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        affected_paths / verification_refs / source_refs が揃えば ok、
        欠落があれば warning。
    Policy:
        - public 関数はステップ列に揃え、欠落集計は private helper に委ねる。
    """
    return _run_requirement_code_hints_check(ctx, rule)


def check_requirement_acceptance_integrity(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """requirement と acceptance の双方向リンクを検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        link / 必須項目が揃えば ok、欠落があれば warning。
    Policy:
        - public 関数はステップ列に揃え、link 検査と warning 組み立ては
          private helper に委ねる。
    """
    return _run_requirement_acceptance_check(ctx, rule)


def check_acceptance_has_verification(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """active な acceptance が verification を持つかを検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        mode と refs が揃えば ok、欠落があれば warning。
    Policy:
        - public 関数はステップ列に揃え、verification 検査は private
          helper に委ねる。
    """
    return _run_acceptance_verification_check(ctx, rule)


def check_source_traceability_integrity(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """request / requirement / acceptance の source_trace_refs を検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        trace_refs が全て解決できれば ok、欠落があれば warning。
    Policy:
        - public 関数はステップ列に揃え、ref 解決は private helper に委ねる。
    """
    return _run_source_traceability_check(ctx, rule)


def check_referenced_paths_exist(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """requirement / acceptance が参照する path の存在を検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        path が全て存在すれば ok、欠落があれば warning。
    Policy:
        - public 関数はステップ列に揃え、path 集計と存在確認は private
          helper に委ねる。
    """
    return _run_referenced_paths_check(ctx, rule)


def check_tasknote_frontmatter_integrity(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """opt-in タスクノートの frontmatter 整合性を検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        必須キーと参照が揃えば ok、欠落があれば warning。
    Policy:
        - public 関数はステップ列に揃え、ノート単位の検査は private
          helper に委ねる。
    """
    return _run_tasknote_frontmatter_check(ctx, rule)


def check_normalized_requirement_lists(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """requirement / request の list が正規形（ソート + 重複なし）かを検査する。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        正規形なら ok、ドリフトがあれば warning。
    Policy:
        - public 関数はステップ列に揃え、ドリフト集計は private helper に委ねる。
    """
    return _run_normalized_lists_check(ctx, rule)


def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """CLI 入口。引数解析と run_checker 呼び出しと JSON 出力を束ねる。

    Args:
        argv: コマンドライン引数。None で sys.argv を使う。
    Returns:
        常に 0。
    Policy:
        - public 関数はステップ列に揃え、引数解析と payload 算出と
          stdout 出力は private helper に委ねる。
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    payload = _run_main_with_args(args)
    return _emit_payload_and_exit_code(payload)


# === Internal helpers (private) ===


def _load_yaml_dict(path: Path) -> dict[str, Any]:
    """YAML を読み、dict であることを保証して返す。

    Args:
        path: 検査対象 YAML のパス。
    Returns:
        解析済みの dict。
    Raises:
        ValueError: dict 以外に解析された場合。
    Policy:
        - 入口で dict であることを担保し、後段が型分岐しないで済むようにする。
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("stakeholder voices YAML must parse to a dict")
    return data


def _require_top_level_keys(data: dict[str, Any]) -> None:
    """top-level の必須キーがあることを点検する。

    Args:
        data: 解析済みの YAML dict。
    Raises:
        KeyError: meta / facts / validation_rules が欠けている場合。
    Policy:
        - 必須キーの欠落は入口で早期に止め、後段の検査が空 dict を触らないようにする。
    """
    for key in ("meta", "facts", "validation_rules"):
        if key not in data:
            raise KeyError(f"missing top-level key: {key}")


def _validate_facts_section(data: dict[str, Any]) -> None:
    """facts ブロックの構造を点検する。

    Args:
        data: 解析済みの YAML dict。
    Policy:
        - facts 直下の必須キーと list 型制約をまとめて検査する。
    """
    facts = data.get("facts")
    _require_facts_is_dict(facts)
    _require_facts_keys(facts)
    _require_facts_list_shapes(facts)
    _require_source_document_items(facts["source_documents"])


def _require_facts_is_dict(facts: Any) -> None:
    """facts が dict であることを点検する。

    Args:
        facts: facts ブロックの値。
    Raises:
        KeyError: dict でなければ KeyError を出して入口で止める。
    Policy:
        - facts が無い / 型違いの YAML は後段検査の前提を破るので即停止する。
    """
    if not isinstance(facts, dict):
        raise KeyError("facts must be present")


def _require_facts_keys(facts: dict[str, Any]) -> None:
    """facts 直下の必須キー欠落を点検する。

    Args:
        facts: facts dict。
    Raises:
        KeyError: 必須キーが欠けている場合。
    Policy:
        - 後段の list 取り出しが KeyError を出さないよう、ここでまとめて点検する。
    """
    for key in (
        "stakeholders",
        "requests",
        "requirements",
        "acceptance",
        "source_documents",
        "tasknote_contracts",
    ):
        if key not in facts:
            raise KeyError(f"facts missing key: {key}")


def _require_facts_list_shapes(facts: dict[str, Any]) -> None:
    """facts 内の list 型キーを点検する。

    Args:
        facts: facts dict。
    Raises:
        TypeError: list 期待のキーが list でない場合。
    Policy:
        - 後段の for ループが安全に回るよう、list 型を入口で担保する。
    """
    for key in (
        "stakeholders",
        "requests",
        "requirements",
        "acceptance",
        "source_documents",
    ):
        if not isinstance(facts[key], list):
            raise TypeError(f"facts.{key} must be a list")


def _require_source_document_items(source_documents: list[Any]) -> None:
    """source_documents の各要素を点検する。

    Args:
        source_documents: facts.source_documents の list。
    Raises:
        TypeError: dict 以外の要素がある場合。
        KeyError: id / path キーが欠けている場合。
    Policy:
        - trace 検査が source_documents を index 引きするので、ここで形状を揃える。
    """
    for source_document in source_documents:
        if not isinstance(source_document, dict):
            raise TypeError("facts.source_documents items must be dicts")
        for key in ("id", "path"):
            if key not in source_document:
                raise KeyError(f"source document missing key: {key}")


def _validate_tasknote_contracts(data: dict[str, Any]) -> None:
    """tasknote_contracts ブロックを点検する。

    Args:
        data: 解析済みの YAML dict。
    Policy:
        - contract dict と required list の両方を private helper に委ねる。
    """
    contracts = data["facts"]["tasknote_contracts"]
    _require_contracts_is_dict(contracts)
    _require_contracts_keys(contracts)
    _require_contracts_required_keys_list(contracts)


def _require_contracts_is_dict(contracts: Any) -> None:
    """tasknote_contracts が dict であることを点検する。

    Args:
        contracts: facts.tasknote_contracts の値。
    Raises:
        TypeError: dict でない場合。
    Policy:
        - 後段の key アクセスが KeyError を出さないよう先に型を点検する。
    """
    if not isinstance(contracts, dict):
        raise TypeError("facts.tasknote_contracts must be a dict")


def _require_contracts_keys(contracts: dict[str, Any]) -> None:
    """tasknote_contracts の必須キーを点検する。

    Args:
        contracts: tasknote_contracts dict。
    Raises:
        KeyError: 必須キーが欠けている場合。
    Policy:
        - note_glob と frontmatter 関連キーをまとめて点検する。
    """
    for key in (
        "note_glob",
        "opt_in_frontmatter_key",
            "required_frontmatter_keys"):
        if key not in contracts:
            raise KeyError(f"tasknote_contracts missing key: {key}")


def _require_contracts_required_keys_list(contracts: dict[str, Any]) -> None:
    """required_frontmatter_keys が list か点検する。

    Args:
        contracts: tasknote_contracts dict。
    Raises:
        TypeError: list でない場合。
    Policy:
        - frontmatter 検査が list を for で回すため、入口で型を担保する。
    """
    if not isinstance(contracts["required_frontmatter_keys"], list):
        raise TypeError(
            "tasknote_contracts.required_frontmatter_keys must be a list")


def _validate_validation_rules(data: dict[str, Any]) -> None:
    """validation_rules の各 rule を点検する。

    Args:
        data: 解析済みの YAML dict。
    Policy:
        - rule 1 件ぶんの検査は private helper に切り出してループから呼ぶ。
    """
    for rule in data["validation_rules"]:
        _validate_single_rule(rule)


def _validate_single_rule(rule: dict[str, Any]) -> None:
    """1 件の rule の骨格を点検する。

    Args:
        rule: validation_rules の 1 件。
    Policy:
        - 必須キー、enforcement、scope、evidence、coverage を順に検査する。
    """
    _require_rule_required_keys(rule)
    _require_rule_suggested_actions(rule)
    _require_rule_enforcement(rule)
    _require_rule_scope(rule)
    _require_rule_checks(rule)
    _require_rule_coverage(rule)
    _require_rule_check_registry(rule)


def _require_rule_required_keys(rule: dict[str, Any]) -> None:
    """rule の必須キー欠落を点検する。

    Args:
        rule: validation_rules の 1 件。
    Raises:
        KeyError: 必須キーが欠けている場合。
    Policy:
        - 必須キーをまとめて確認し、後段の dict 取り出しを安全にする。
    """
    required_rule_keys = {
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
    missing = required_rule_keys - set(rule)
    if missing:
        rule_id = rule.get("id", "<unknown>")
        raise KeyError(
            f"rule {rule_id} missing keys: {sorted(missing)}")


def _require_rule_suggested_actions(rule: dict[str, Any]) -> None:
    """rule.suggested_actions が list か点検する。

    Args:
        rule: validation_rules の 1 件。
    Raises:
        TypeError: list でない場合。
    Policy:
        - 後段で warning の suggested_actions に流すため、list 型を入口で揃える。
    """
    if not isinstance(rule["suggested_actions"], list):
        raise TypeError(
            f"rule {rule['id']} suggested_actions must be a list")


def _require_rule_enforcement(rule: dict[str, Any]) -> None:
    """rule.enforcement.mode を点検する。

    Args:
        rule: validation_rules の 1 件。
    Raises:
        KeyError: enforcement.mode が無い場合。
        ValueError: deterministic 以外の mode が指定された場合。
    Policy:
        - 本 CLI は deterministic mode のみ動かす契約をここで宣言する。
    """
    if "mode" not in rule["enforcement"]:
        raise KeyError(f"rule {rule['id']} missing enforcement.mode")
    if rule["enforcement"]["mode"] != "deterministic":
        raise ValueError(
            f"rule {rule['id']} only deterministic mode is supported")


def _require_rule_scope(rule: dict[str, Any]) -> None:
    """rule.scope.paths が list か点検する。

    Args:
        rule: validation_rules の 1 件。
    Raises:
        TypeError: list でない場合。
    Policy:
        - 後段の scope 取り出しが TypeError を出さないようにする。
    """
    if not isinstance(rule.get("scope", {}).get("paths"), list):
        raise TypeError(f"rule {rule['id']} scope.paths must be a list")


def _require_rule_checks(rule: dict[str, Any]) -> None:
    """rule.evidence.checks が non-empty list か点検する。

    Args:
        rule: validation_rules の 1 件。
    Raises:
        TypeError: list でない / 空である場合。
    Policy:
        - check 名が 1 つ以上あることを入口で担保する。
    """
    checks = rule.get("evidence", {}).get("checks")
    if _is_invalid_checks_list(checks):
        raise TypeError(
            f"rule {rule['id']} evidence.checks must be a non-empty list")


def _is_invalid_checks_list(checks: Any) -> bool:
    """checks 値が list でない / 空かを判定する。

    Args:
        checks: rule.evidence.checks の値。
    Returns:
        list でない、または空 list なら True。
    Policy:
        - 複合 if を述語に閉じ、CR303 を回避する。
    """
    if not isinstance(checks, list):
        return True
    return not checks


def _require_rule_coverage(rule: dict[str, Any]) -> None:
    """rule.coverage の構造を点検する。

    Args:
        rule: validation_rules の 1 件。
    Policy:
        - 型、必須キー、値域を順に private helper で検査する。
    """
    coverage = rule.get("coverage")
    _require_coverage_is_dict(rule, coverage)
    _require_coverage_keys(rule, coverage)
    _require_coverage_deterministic_review(rule, coverage)
    _require_coverage_repair_autofix(rule, coverage)
    _require_coverage_next_checker_unit(rule, coverage)
    _require_coverage_rationale(rule, coverage)


def _require_coverage_is_dict(
        rule: dict[str, Any], coverage: Any) -> None:
    """coverage が dict か点検する。

    Args:
        rule: validation_rules の 1 件。
        coverage: rule.coverage の値。
    Raises:
        TypeError: dict でない場合。
    Policy:
        - 後段の dict アクセスを安全にする。
    """
    if not isinstance(coverage, dict):
        raise TypeError(f"rule {rule['id']} coverage must be a dict")


def _require_coverage_keys(
        rule: dict[str, Any], coverage: dict[str, Any]) -> None:
    """coverage 必須キーの欠落を点検する。

    Args:
        rule: validation_rules の 1 件。
        coverage: rule.coverage dict。
    Raises:
        KeyError: 必須キーが欠けている場合。
    Policy:
        - 棚卸し系メタキーが必ず揃っていることをここで担保する。
    """
    for key in (
        "deterministic_review",
        "next_checker_unit",
        "repair_autofix",
            "rationale"):
        if key not in coverage:
            raise KeyError(
                f"rule {rule['id']} coverage missing key: {key}")


def _require_coverage_deterministic_review(
        rule: dict[str, Any], coverage: dict[str, Any]) -> None:
    """deterministic_review の値域を点検する。

    Args:
        rule: validation_rules の 1 件。
        coverage: rule.coverage dict。
    Raises:
        ValueError: 値域外の場合。
    Policy:
        - 棚卸し画面で集計可能な値だけを許可する。
    """
    if coverage["deterministic_review"] in VALID_DETERMINISTIC_REVIEWS:
        return
    raise ValueError(
        f"rule {rule['id']} coverage.deterministic_review must be one of "
        f"{sorted(VALID_DETERMINISTIC_REVIEWS)}")


def _require_coverage_repair_autofix(
        rule: dict[str, Any], coverage: dict[str, Any]) -> None:
    """repair_autofix の値域を点検する。

    Args:
        rule: validation_rules の 1 件。
        coverage: rule.coverage dict。
    Raises:
        ValueError: 値域外の場合。
    Policy:
        - fix の自動化進捗を集計するため、許可 token に限定する。
    """
    if coverage["repair_autofix"] in VALID_REPAIR_AUTOFIX:
        return
    raise ValueError(
        f"rule {rule['id']} coverage.repair_autofix must be one of "
        f"{sorted(VALID_REPAIR_AUTOFIX)}"
    )


def _require_coverage_next_checker_unit(
        rule: dict[str, Any], coverage: dict[str, Any]) -> None:
    """next_checker_unit の型を点検する。

    Args:
        rule: validation_rules の 1 件。
        coverage: rule.coverage dict。
    Raises:
        TypeError: None でも str でもない場合。
    Policy:
        - 棚卸し画面で「次に書く checker 名」を文字列で扱う前提を守る。
    """
    value = coverage["next_checker_unit"]
    if _is_str_or_none(value):
        return
    raise TypeError(
        f"rule {rule['id']} coverage.next_checker_unit "
        "must be a string or null")


def _is_str_or_none(value: Any) -> bool:
    """値が None または str かを判定する。

    Args:
        value: 判定対象の値。
    Returns:
        None または str なら True。
    Policy:
        - 複合 if を述語に閉じ、CR303 を回避する。
    """
    if value is None:
        return True
    return isinstance(value, str)


def _require_coverage_rationale(
        rule: dict[str, Any], coverage: dict[str, Any]) -> None:
    """rationale が非空文字列か点検する。

    Args:
        rule: validation_rules の 1 件。
        coverage: rule.coverage dict。
    Raises:
        TypeError: 非空文字列でない場合。
    Policy:
        - 棚卸し画面で必ず根拠が読めるよう、空文字列を拒否する。
    """
    value = coverage["rationale"]
    if _is_non_empty_string(value):
        return
    raise TypeError(
        f"rule {rule['id']} coverage.rationale must be a non-empty string")


def _is_non_empty_string(value: Any) -> bool:
    """値が strip 後に非空の str かを判定する。

    Args:
        value: 判定対象の値。
    Returns:
        str かつ strip 後に空でなければ True。
    Policy:
        - 複合 if を述語に閉じ、CR303 を回避する。
    """
    if not isinstance(value, str):
        return False
    return bool(value.strip())


def _require_rule_check_registry(rule: dict[str, Any]) -> None:
    """rule の checks が registry に登録済みか点検する。

    Args:
        rule: validation_rules の 1 件。
    Raises:
        KeyError: 未登録の check 名がある場合。
    Policy:
        - YAML 上では deterministic なのに実行不能、という事故を入口で止める。
    """
    checks = rule.get("evidence", {}).get("checks", [])
    for check_name in checks:
        if check_name not in CHECK_REGISTRY:
            raise KeyError(
                f"rule {rule['id']} references unknown deterministic check: "
                f"{check_name}")


def _get_scope_paths(rule: dict[str, Any]) -> list[str]:
    """rule.scope.paths を list で返す。

    Args:
        rule: validation_rules の 1 件。
    Returns:
        scope.paths の浅いコピー。
    Policy:
        - 後段が破壊的に触っても rule を巻き込まない。
    """
    return list(rule.get("scope", {}).get("paths", []))


def _build_id_map(
        entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """id をキーにした dict を組み立てる。

    Args:
        entries: id を持つ dict の list。
    Returns:
        id -> entry の dict。
    Policy:
        - 入口で list を dict に変換し、後段で線形探索しないで済むようにする。
    """
    return {entry["id"]: entry for entry in entries}


def _list_duplicates(values: list[str]) -> list[str]:
    """list の重複値だけを順序維持で返す。

    Args:
        values: 検査対象の list。
    Returns:
        重複した値を初出順に並べた list。
    Policy:
        - 単一スキャンで O(n) に抑え、出力順を入力順に合わせて読みやすくする。
    """
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if _is_new_duplicate(value, seen, duplicates):
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _is_new_duplicate(
        value: str, seen: set[str], duplicates: list[str]) -> bool:
    """値が「既出かつ未収集の重複」かを判定する。

    Args:
        value: 検査対象の値。
        seen: これまでに見た値の集合。
        duplicates: これまでに収集した重複 list。
    Returns:
        bool: 既出かつ未収集なら True。
    Policy:
        - _list_duplicates の if 条件を述語として切り出し、CR303 を回避する。
    """
    if value not in seen:
        return False
    return value not in duplicates


def _load_frontmatter(path: Path) -> dict[str, Any] | None:
    """ノート先頭の YAML frontmatter を dict で返す。

    Args:
        path: 対象ノートのパス。
    Returns:
        frontmatter dict。frontmatter が無い / dict でなければ None。
    Policy:
        - `---` ブロックの読み取りを 1 箇所に閉じ、呼び出し側を簡潔にする。
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None
    raw = yaml.safe_load(parts[1])
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        return None
    return raw


def _warning(
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
        rule: validation_rules の 1 件。
        checked_paths: 検査対象 path の list。
        failed_check: 失敗した check 名。
        reason: 補足理由（任意）。
        expected: 期待値（任意）。
        observed: 観測値（任意）。
    Returns:
        warning 状態の CheckOutcome。
    Policy:
        - message 組み立てと suggested_actions の取り出しを 1 箇所に閉じる。
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
        rule: dict[str, Any], reason: str | None) -> str | None:
    """warning 用の message 文字列を組み立てる。

    Args:
        rule: validation_rules の 1 件。
        reason: 補足理由（任意）。
    Returns:
        rule.message + ": " + reason の連結。reason が無ければ rule.message。
    Policy:
        - if 連鎖を 1 つの述語に閉じ、_warning の本体をステップ列に保つ。
    """
    message = rule.get("message")
    if not reason:
        return message
    if not message:
        return reason
    return f"{message}: {reason}"


def _build_ok_outcome(
        rule: dict[str, Any], checked_paths: list[str]) -> CheckOutcome:
    """ok の CheckOutcome を組み立てる。

    Args:
        rule: validation_rules の 1 件（現状は使用しないが互換用）。
        checked_paths: 検査対象 path の list。
    Returns:
        ok 状態の CheckOutcome。
    Policy:
        - 後で metadata を増やす拡張点を 1 箇所に集める。
    """
    return CheckOutcome(status="ok", checked_paths=checked_paths)


def _run_rule_checks(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """rule.evidence.checks を順に回し、最初の non-ok を返す。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。全て ok なら ok。
    Policy:
        - public 関数 run_rule から呼ばれる委譲点として、ループはここに閉じる。
    """
    checks = rule.get("evidence", {}).get("checks", [])
    for check_name in checks:
        outcome = CHECK_REGISTRY[check_name](ctx, rule)
        if outcome.status != "ok":
            return outcome
    return _build_ok_outcome(rule, _get_scope_paths(rule))


def _select_rules(
    data: dict[str, Any],
    rule_ids: set[str] | None,
) -> list[dict[str, Any]]:
    """rule_ids 指定を適用した validation_rules を返す。

    Args:
        data: 解析済みの YAML dict。
        rule_ids: 限定実行する rule id 集合（None で全件）。
    Returns:
        絞り込み後の rule list。
    Policy:
        - 全件パスと絞り込みパスをこの関数に閉じ、run_checker をステップ列に保つ。
    """
    selected_rules = data["validation_rules"]
    if rule_ids is None:
        return selected_rules
    return [rule for rule in selected_rules if rule["id"] in rule_ids]


def _run_selected_rules(
    ctx: CheckContext,
    selected_rules: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """選定された rule を順に実行し、results と warning 件数を返す。

    Args:
        ctx: 検査文脈。
        selected_rules: 実行対象の rule list。
    Returns:
        (results list, warning_count) のタプル。
    Policy:
        - results 整形と warning 集計を 1 つのループに閉じる。
    """
    results: list[dict[str, Any]] = []
    warning_count = 0
    for rule in selected_rules:
        outcome = run_rule(ctx, rule)
        if outcome.status == "warning":
            warning_count += 1
        results.append(_build_result_record(rule, outcome))
    return results, warning_count


def _build_result_record(
        rule: dict[str, Any], outcome: CheckOutcome) -> dict[str, Any]:
    """1 件ぶんの results エントリを組み立てる。

    Args:
        rule: validation_rules の 1 件。
        outcome: 評価結果。
    Returns:
        rule_id / status / coverage などを含む dict。
    Policy:
        - payload の JSON スキーマをこの関数に閉じる。
    """
    return {
        "rule_id": rule["id"],
        "status": outcome.status,
        "checked_paths": outcome.checked_paths,
        "failed_checks": outcome.failed_checks,
        "message": outcome.message,
        "suggested_actions": outcome.suggested_actions,
        "expected": outcome.expected,
        "observed": outcome.observed,
        "coverage": rule["coverage"],
    }


def _build_run_payload(
    selected_rules: list[dict[str, Any]],
    results: list[dict[str, Any]],
    warning_count: int,
) -> dict[str, Any]:
    """run_checker の最終 payload を組み立てる。

    Args:
        selected_rules: 実行対象の rule list。
        results: results 整形済みエントリの list。
        warning_count: warning 件数。
    Returns:
        run_ok / has_warnings / summary / results を含む payload。
    Policy:
        - summary 計算と payload 整形をこの helper に閉じる。
    """
    total_rules = len(selected_rules)
    return {
        "run_ok": True,
        "has_warnings": warning_count > 0,
        "summary": {
            "total_rules": total_rules,
            "executed_rules": total_rules,
            "skipped_rules": 0,
            "warning_rules": warning_count,
        },
        "results": results,
    }


def _run_id_uniqueness_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """id 重複検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - id 収集 → 重複抽出 → warning 組み立てを順に呼ぶ。
    """
    checked_paths = _get_scope_paths(rule)
    id_sources = _collect_id_sources(ctx.data)
    duplicates = _collect_duplicate_groups(id_sources)
    if not duplicates:
        return _build_ok_outcome(rule, checked_paths)
    return _warning(
        rule,
        checked_paths,
        "id_uniqueness",
        reason="duplicate ids detected",
        expected={"unique_id_groups": list(id_sources)},
        observed={"duplicates": duplicates},
    )


def _collect_id_sources(data: dict[str, Any]) -> dict[str, list[str]]:
    """6 種類の id list を section 名にひもづけて返す。

    Args:
        data: 解析済みの YAML dict。
    Returns:
        section 名 -> id list の dict。
    Policy:
        - 検査対象の section をここで一括宣言する。
    """
    facts = data["facts"]
    return {
        "stakeholders": [item["id"] for item in facts["stakeholders"]],
        "requests": [item["id"] for item in facts["requests"]],
        "requirements": [item["id"] for item in facts["requirements"]],
        "acceptance": [item["id"] for item in facts["acceptance"]],
        "source_documents": [
            item["id"] for item in facts["source_documents"]],
        "validation_rules": [
            item["id"] for item in data["validation_rules"]],
    }


def _collect_duplicate_groups(
        id_sources: dict[str, list[str]]) -> dict[str, list[str]]:
    """section ごとの重複 id だけを残した dict を返す。

    Args:
        id_sources: section 名 -> id list の dict。
    Returns:
        重複があった section のみ含む dict。
    Policy:
        - 出力 dict を section 単位に整形し、warning 観測値を読みやすくする。
    """
    grouped = {
        name: _list_duplicates(values) for name, values in id_sources.items()}
    return {name: values for name, values in grouped.items() if values}


def _run_stakeholder_reference_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """stakeholder 参照整合性検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - 既知 id 収集 → request / requirement の欠落抽出 → warning。
    """
    checked_paths = _get_scope_paths(rule)
    facts = ctx.data["facts"]
    stakeholder_ids = set(_build_id_map(facts["stakeholders"]))
    missing_requests = _collect_requests_with_missing_stakeholders(
        facts["requests"], stakeholder_ids)
    missing_requirements = _collect_requirements_with_missing_stakeholders(
        facts["requirements"], stakeholder_ids)
    if _has_no_stakeholder_drift(missing_requests, missing_requirements):
        return _build_ok_outcome(rule, checked_paths)
    return _build_stakeholder_reference_warning(
        rule,
        checked_paths,
        stakeholder_ids,
        missing_requests,
        missing_requirements,
    )


def _build_stakeholder_reference_warning(
    rule: dict[str, Any],
    checked_paths: list[str],
    stakeholder_ids: set[str],
    missing_requests: list[str],
    missing_requirements: dict[str, list[str]],
) -> CheckOutcome:
    """stakeholder 参照欠落の warning を組み立てる。

    Args:
        rule: validation_rules の 1 件。
        checked_paths: 検査対象 path の list。
        stakeholder_ids: 既知 stakeholder id 集合。
        missing_requests: stakeholder 不在の request id list。
        missing_requirements: requirement id -> 欠落 stakeholder list。
    Returns:
        warning 状態の CheckOutcome。
    Policy:
        - observed / expected を組み立てる長い式をここに閉じる。
    """
    return _warning(
        rule,
        checked_paths,
        "stakeholder_reference_integrity",
        reason="missing stakeholder definitions",
        expected={"known_stakeholder_ids": sorted(stakeholder_ids)},
        observed={
            "request_ids_with_missing_stakeholders": missing_requests,
            "requirement_ids_with_missing_stakeholders": missing_requirements,
        },
    )


def _has_no_stakeholder_drift(
    missing_requests: list[str],
    missing_requirements: dict[str, list[str]],
) -> bool:
    """stakeholder 参照に欠落が無いかを判定する。

    Args:
        missing_requests: stakeholder 不在の request id list。
        missing_requirements: requirement id -> 欠落 stakeholder list。
    Returns:
        欠落が無ければ True。
    Policy:
        - public 関数の述語ガードを 1 つの呼び出しに閉じる。
    """
    if missing_requests:
        return False
    return not missing_requirements


def _collect_requests_with_missing_stakeholders(
    requests: list[dict[str, Any]],
    stakeholder_ids: set[str],
) -> list[str]:
    """stakeholder_id が未解決の request id を返す。

    Args:
        requests: facts.requests の list。
        stakeholder_ids: 既知 stakeholder id 集合。
    Returns:
        欠落のある request id の list。
    Policy:
        - 述語と内包表記をここに閉じ、呼び出し側を簡潔に保つ。
    """
    return [
        item["id"]
        for item in requests
        if item.get("stakeholder_id") not in stakeholder_ids
    ]


def _collect_requirements_with_missing_stakeholders(
    requirements: list[dict[str, Any]],
    stakeholder_ids: set[str],
) -> dict[str, list[str]]:
    """欠落 stakeholder を持つ requirement id -> 欠落 list を返す。

    Args:
        requirements: facts.requirements の list。
        stakeholder_ids: 既知 stakeholder id 集合。
    Returns:
        requirement id -> 欠落 stakeholder list の dict（空は除外）。
    Policy:
        - 欠落 0 件の requirement は出力から除外する。
    """
    missing = {
        item["id"]: [
            sid for sid in item.get("stakeholder_ids", [])
            if sid not in stakeholder_ids
        ]
        for item in requirements
    }
    return {key: value for key, value in missing.items() if value}


def _run_request_reference_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """request 参照整合性検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - request id 集合化 → 未解決抽出 → warning の順に進める。
    """
    checked_paths = _get_scope_paths(rule)
    facts = ctx.data["facts"]
    request_ids = set(_build_id_map(facts["requests"]))
    missing = _collect_missing_request_refs(
        facts["requirements"], request_ids)
    if not missing:
        return _build_ok_outcome(rule, checked_paths)
    return _warning(
        rule,
        checked_paths,
        "request_reference_integrity",
        reason="derived_from_request_ids contains unknown ids",
        expected={"known_request_ids": sorted(request_ids)},
        observed={"missing_request_refs": missing},
    )


def _collect_missing_request_refs(
    requirements: list[dict[str, Any]],
    request_ids: set[str],
) -> dict[str, list[str]]:
    """requirement id -> 未解決 request id list を返す。

    Args:
        requirements: facts.requirements の list。
        request_ids: 既知 request id 集合。
    Returns:
        欠落のある requirement id だけ含む dict。
    Policy:
        - derived_from_request_ids の dict 整形をここに閉じる。
    """
    missing = {
        item["id"]: [
            request_id
            for request_id in item.get("derived_from_request_ids", [])
            if request_id not in request_ids
        ]
        for item in requirements
    }
    return {key: value for key, value in missing.items() if value}


def _run_requirement_code_hints_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """requirement code hint 検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - active な requirement のみ対象に欠落集計し、warning を組み立てる。
    """
    checked_paths = _get_scope_paths(rule)
    missing = _collect_missing_code_hints(ctx.data["facts"]["requirements"])
    if not missing:
        return _build_ok_outcome(rule, checked_paths)
    return _warning(
        rule,
        checked_paths,
        "requirement_has_code_hints",
        reason="active requirements are missing code hint fields",
        expected={
            "required_keys": [
                "affected_paths",
                "verification_refs",
                "source_refs"]},
        observed={"missing_keys_by_requirement": missing},
    )


def _collect_missing_code_hints(
        requirements: list[dict[str, Any]]) -> dict[str, list[str]]:
    """active requirement の欠落 code hint key を返す。

    Args:
        requirements: facts.requirements の list。
    Returns:
        requirement id -> 欠落 key list の dict。
    Policy:
        - active 以外は対象外、欠落 0 件も結果から外す。
    """
    missing: dict[str, list[str]] = {}
    for requirement in requirements:
        if requirement.get("status") != "active":
            continue
        requirement_missing = _collect_missing_code_hint_keys(requirement)
        if requirement_missing:
            missing[requirement["id"]] = requirement_missing
    return missing


def _collect_missing_code_hint_keys(
        requirement: dict[str, Any]) -> list[str]:
    """1 件の requirement で欠落している code hint key を返す。

    Args:
        requirement: 1 件の requirement dict。
    Returns:
        欠落 key の list。
    Policy:
        - 必須 key リストをこの関数に閉じる。
    """
    return [
        key
        for key in ("affected_paths", "verification_refs", "source_refs")
        if not requirement.get(key)
    ]


def _run_requirement_acceptance_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """requirement と acceptance の双方向リンク検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - requirement 側エラーと acceptance 側 orphan を private helper で抽出する。
    """
    checked_paths = _get_scope_paths(rule)
    tracked_priorities = {"p0", "p1"}
    missing, orphan_acceptance = _collect_acceptance_drift(
        ctx, tracked_priorities)
    if _has_no_acceptance_drift(missing, orphan_acceptance):
        return _build_ok_outcome(rule, checked_paths)
    return _build_requirement_acceptance_warning(
        rule,
        checked_paths,
        tracked_priorities,
        missing,
        orphan_acceptance,
    )


def _collect_acceptance_drift(
    ctx: CheckContext,
    tracked_priorities: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, str | None]]:
    """requirement 側エラーと acceptance 側 orphan をまとめて返す。

    Args:
        ctx: 検査文脈。
        tracked_priorities: 監視対象の priority 集合。
    Returns:
        (missing, orphan_acceptance) のタプル。
    Policy:
        - 同じ facts を 2 度引かないよう、入口で 1 回ぶんに束ねる。
    """
    facts = ctx.data["facts"]
    acceptance_map = _build_id_map(facts["acceptance"])
    requirement_ids = set(_build_id_map(facts["requirements"]))
    missing = _collect_requirement_acceptance_errors(
        facts["requirements"], acceptance_map, tracked_priorities)
    orphan_acceptance = _collect_orphan_acceptance(
        facts["acceptance"], requirement_ids)
    return missing, orphan_acceptance


def _build_requirement_acceptance_warning(
    rule: dict[str, Any],
    checked_paths: list[str],
    tracked_priorities: set[str],
    missing: dict[str, dict[str, Any]],
    orphan_acceptance: dict[str, str | None],
) -> CheckOutcome:
    """requirement-acceptance 整合性 warning を組み立てる。

    Args:
        rule: validation_rules の 1 件。
        checked_paths: 検査対象 path の list。
        tracked_priorities: 監視対象の priority 集合。
        missing: requirement id -> error dict。
        orphan_acceptance: 親不明の acceptance dict。
    Returns:
        warning 状態の CheckOutcome。
    Policy:
        - observed / expected を組み立てる長い式をここに閉じる。
    """
    return _warning(
        rule,
        checked_paths,
        "requirement_acceptance_integrity",
        reason=(
            "acceptance linkage is incomplete or "
            "points at the wrong requirement"),
        expected={"tracked_priorities": sorted(tracked_priorities)},
        observed={
            "acceptance_errors_by_requirement": missing,
            "acceptance_with_unknown_requirement": orphan_acceptance,
        },
    )


def _has_no_acceptance_drift(
    missing: dict[str, dict[str, Any]],
    orphan_acceptance: dict[str, str | None],
) -> bool:
    """acceptance 周りに欠落が無いかを判定する。

    Args:
        missing: requirement id -> error の dict。
        orphan_acceptance: 親 requirement 不明の acceptance dict。
    Returns:
        欠落が無ければ True。
    Policy:
        - public 関数の述語ガードを 1 つの呼び出しに閉じる。
    """
    if missing:
        return False
    return not orphan_acceptance


def _collect_requirement_acceptance_errors(
    requirements: list[dict[str, Any]],
    acceptance_map: dict[str, dict[str, Any]],
    tracked_priorities: set[str],
) -> dict[str, dict[str, Any]]:
    """requirement 単位に acceptance リンクエラーを集める。

    Args:
        requirements: facts.requirements の list。
        acceptance_map: acceptance id -> acceptance dict。
        tracked_priorities: 監視対象の priority 集合。
    Returns:
        requirement id -> error dict（空は除外）。
    Policy:
        - active かつ tracked priority のみを検査対象にする。
    """
    missing: dict[str, dict[str, Any]] = {}
    for requirement in requirements:
        if not _is_requirement_tracked(requirement, tracked_priorities):
            continue
        requirement_errors = _collect_single_requirement_acceptance_errors(
            requirement, acceptance_map)
        if requirement_errors:
            missing[requirement["id"]] = requirement_errors
    return missing


def _is_requirement_tracked(
    requirement: dict[str, Any],
    tracked_priorities: set[str],
) -> bool:
    """requirement が acceptance リンク検査の対象かを判定する。

    Args:
        requirement: 1 件の requirement dict。
        tracked_priorities: 監視対象の priority 集合。
    Returns:
        active かつ priority が tracked なら True。
    Policy:
        - 複合条件を述語に閉じ、呼び出し側のループを簡潔に保つ。
    """
    if requirement.get("status") != "active":
        return False
    return requirement.get("priority") in tracked_priorities


def _collect_single_requirement_acceptance_errors(
    requirement: dict[str, Any],
    acceptance_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """1 件の requirement に対する acceptance リンクエラーを返す。

    Args:
        requirement: 1 件の requirement dict。
        acceptance_map: acceptance id -> acceptance dict。
    Returns:
        error 種別 -> 値の dict。
    Policy:
        - missing / unknown / mismatched / 必須項目欠落を private helper でまとめる。
    """
    acceptance_ids = list(requirement.get("acceptance_ids", []))
    requirement_errors: dict[str, Any] = {}
    if not acceptance_ids:
        requirement_errors["missing_acceptance_ids"] = True
    unresolved = [
        item for item in acceptance_ids if item not in acceptance_map]
    if unresolved:
        requirement_errors["unknown_acceptance_ids"] = unresolved
    mismatched_links, missing_fields = _collect_link_errors(
        requirement, acceptance_ids, acceptance_map)
    if mismatched_links:
        requirement_errors[
            "mismatched_acceptance_requirement_id"] = mismatched_links
    if missing_fields:
        requirement_errors["acceptance_missing_fields"] = missing_fields
    return requirement_errors


def _collect_link_errors(
    requirement: dict[str, Any],
    acceptance_ids: list[str],
    acceptance_map: dict[str, dict[str, Any]],
) -> tuple[dict[str, str | None], dict[str, list[str]]]:
    """acceptance 側の逆リンクと必須項目欠落をまとめて返す。

    Args:
        requirement: 1 件の requirement dict。
        acceptance_ids: 対象 acceptance id list。
        acceptance_map: acceptance id -> acceptance dict。
    Returns:
        (mismatched_links, missing_fields) のタプル。
    Policy:
        - 1 ループで 2 つの結果を埋め、二重走査を避ける。
    """
    mismatched_links: dict[str, str | None] = {}
    missing_fields: dict[str, list[str]] = {}
    for acceptance_id in acceptance_ids:
        acceptance = acceptance_map.get(acceptance_id)
        if acceptance is None:
            continue
        _record_link_mismatch(
            acceptance_id, acceptance, requirement, mismatched_links)
        _record_acceptance_missing_fields(
            acceptance_id, acceptance, missing_fields)
    return mismatched_links, missing_fields


def _record_link_mismatch(
    acceptance_id: str,
    acceptance: dict[str, Any],
    requirement: dict[str, Any],
    mismatched_links: dict[str, str | None],
) -> None:
    """acceptance.requirement_id が requirement.id と違えば記録する。

    Args:
        acceptance_id: 検査対象 acceptance id。
        acceptance: 検査対象 acceptance dict。
        requirement: 親 requirement dict。
        mismatched_links: 出力先 dict。
    Policy:
        - 出力先 dict への書き込みをこの helper に閉じる。
    """
    if acceptance.get("requirement_id") == requirement["id"]:
        return
    mismatched_links[acceptance_id] = acceptance.get("requirement_id")


def _record_acceptance_missing_fields(
    acceptance_id: str,
    acceptance: dict[str, Any],
    missing_fields: dict[str, list[str]],
) -> None:
    """acceptance に given/when/then 欠落があれば記録する。

    Args:
        acceptance_id: 検査対象 acceptance id。
        acceptance: 検査対象 acceptance dict。
        missing_fields: 出力先 dict。
    Policy:
        - 必須 3 項目の点検をこの helper に閉じる。
    """
    acceptance_missing = [
        key for key in ("given", "when", "then")
        if not acceptance.get(key)
    ]
    if acceptance_missing:
        missing_fields[acceptance_id] = acceptance_missing


def _collect_orphan_acceptance(
    acceptance: list[dict[str, Any]],
    requirement_ids: set[str],
) -> dict[str, str | None]:
    """requirement_id が未解決の acceptance を返す。

    Args:
        acceptance: facts.acceptance の list。
        requirement_ids: 既知 requirement id 集合。
    Returns:
        acceptance id -> 不明な requirement_id の dict。
    Policy:
        - 親不明の acceptance を 1 箇所で抽出する。
    """
    return {
        item["id"]: item.get("requirement_id")
        for item in acceptance
        if item.get("requirement_id") not in requirement_ids
    }


def _run_acceptance_verification_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """acceptance verification 検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - active な acceptance の verification 欠落を集計して warning を組む。
    """
    checked_paths = _get_scope_paths(rule)
    missing = _collect_acceptance_verification_errors(
        ctx.data["facts"]["acceptance"])
    if not missing:
        return _build_ok_outcome(rule, checked_paths)
    return _warning(
        rule,
        checked_paths,
        "acceptance_has_verification",
        reason="acceptance scenarios must declare verification mode and refs",
        expected={
            "valid_modes": sorted(VALID_ACCEPTANCE_VERIFICATION_MODES)},
        observed={"acceptance_verification_errors": missing},
    )


def _collect_acceptance_verification_errors(
        acceptances: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """acceptance verification の欠落を集計する。

    Args:
        acceptances: facts.acceptance の list。
    Returns:
        acceptance id -> error dict。
    Policy:
        - active 以外は対象外、欠落 0 件は結果から外す。
    """
    missing: dict[str, dict[str, Any]] = {}
    for acceptance in acceptances:
        if acceptance.get("status", "active") != "active":
            continue
        acceptance_errors = _collect_single_verification_errors(acceptance)
        if acceptance_errors:
            missing[acceptance["id"]] = acceptance_errors
    return missing


def _collect_single_verification_errors(
        acceptance: dict[str, Any]) -> dict[str, Any]:
    """1 件の acceptance の verification 欠落を返す。

    Args:
        acceptance: 1 件の acceptance dict。
    Returns:
        error 種別 -> 値の dict。
    Policy:
        - verification dict 欠落と mode / refs 欠落を 1 箇所で扱う。
    """
    verification = acceptance.get("verification")
    acceptance_errors: dict[str, Any] = {}
    if not isinstance(verification, dict):
        acceptance_errors["missing_verification"] = True
        return acceptance_errors
    mode = verification.get("mode")
    refs = verification.get("refs")
    if mode not in VALID_ACCEPTANCE_VERIFICATION_MODES:
        acceptance_errors["invalid_mode"] = mode
    if _is_missing_refs(refs):
        acceptance_errors["missing_refs"] = refs
    return acceptance_errors


def _is_missing_refs(refs: Any) -> bool:
    """verification.refs が欠落値かを判定する。

    Args:
        refs: 検査対象の値。
    Returns:
        list でない / 空の list なら True。
    Policy:
        - 複合 if を述語に閉じ、CR303 を回避する。
    """
    if not isinstance(refs, list):
        return True
    return not refs


def _run_source_traceability_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """source_trace_refs 整合性検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - section ごとの欠落を集計し、warning を組み立てる。
    """
    checked_paths = _get_scope_paths(rule)
    source_documents = _build_id_map(ctx.data["facts"]["source_documents"])
    text_cache: dict[str, str] = {}
    observed = _collect_source_traceability_errors(
        ctx, source_documents, text_cache)
    if not observed:
        return _build_ok_outcome(rule, checked_paths)
    return _warning(
        rule,
        checked_paths,
        "source_traceability_integrity",
        reason="tracked items must keep live source_trace_refs",
        expected={
            "source_documents": sorted(source_documents),
            "trace_format": "doc_id:stable_ref",
        },
        observed=observed,
    )


def _collect_source_traceability_errors(
    ctx: CheckContext,
    source_documents: dict[str, dict[str, Any]],
    text_cache: dict[str, str],
) -> dict[str, dict[str, Any]]:
    """section ごとに source_trace_refs エラーを集める。

    Args:
        ctx: 検査文脈。
        source_documents: source_document id -> dict。
        text_cache: doc_path -> 読み込み済み文字列のキャッシュ。
    Returns:
        section 名 -> item id -> error dict。
    Policy:
        - request / requirement / acceptance を 1 つのループで扱う。
    """
    observed: dict[str, dict[str, Any]] = {}
    for section_name in ("requests", "requirements", "acceptance"):
        section_errors = _collect_section_traceability_errors(
            ctx, section_name, source_documents, text_cache)
        if section_errors:
            observed[section_name] = section_errors
    return observed


def _collect_section_traceability_errors(
    ctx: CheckContext,
    section_name: str,
    source_documents: dict[str, dict[str, Any]],
    text_cache: dict[str, str],
) -> dict[str, dict[str, Any]]:
    """1 つの section に対する source_trace_refs エラーを集める。

    Args:
        ctx: 検査文脈。
        section_name: facts のキー名。
        source_documents: source_document id -> dict。
        text_cache: doc_path -> 読み込み済み文字列のキャッシュ。
    Returns:
        item id -> error dict。
    Policy:
        - 追跡対象 status のみ検査し、欠落 0 件 item は除外する。
    """
    section_errors: dict[str, Any] = {}
    for item in ctx.data["facts"][section_name]:
        if item.get("status", "active") not in TRACKED_TRACE_STATUSES:
            continue
        item_errors = _collect_item_traceability_errors(
            ctx, item, source_documents, text_cache)
        if item_errors:
            section_errors[item["id"]] = item_errors
    return section_errors


def _collect_item_traceability_errors(
    ctx: CheckContext,
    item: dict[str, Any],
    source_documents: dict[str, dict[str, Any]],
    text_cache: dict[str, str],
) -> dict[str, Any]:
    """1 件の item に対する source_trace_refs エラーを返す。

    Args:
        ctx: 検査文脈。
        item: facts セクションの 1 件。
        source_documents: source_document id -> dict。
        text_cache: doc_path -> 読み込み済み文字列のキャッシュ。
    Returns:
        error 種別 -> 値の dict。
    Policy:
        - 空 trace_refs と 1 件ごとの解決を分けて扱う。
    """
    trace_refs = list(item.get("source_trace_refs", []))
    item_errors: dict[str, Any] = {}
    if not trace_refs:
        item_errors["missing_source_trace_refs"] = True
        return item_errors
    buckets = _resolve_trace_refs(
        ctx, trace_refs, source_documents, text_cache)
    _fill_trace_errors(item_errors, buckets)
    return item_errors


def _resolve_trace_refs(
    ctx: CheckContext,
    trace_refs: list[Any],
    source_documents: dict[str, dict[str, Any]],
    text_cache: dict[str, str],
) -> dict[str, list[str]]:
    """trace_refs を 4 種類のエラーバケットに振り分ける。

    Args:
        ctx: 検査文脈。
        trace_refs: 検査対象の trace_ref list。
        source_documents: source_document id -> dict。
        text_cache: doc_path -> 読み込み済み文字列のキャッシュ。
    Returns:
        invalid_format / unknown_doc_ids / missing_doc_paths /
        missing_trace_tokens を含む dict。
    Policy:
        - 1 つの trace_ref に対する判定を private helper に委ね、ここはバケット組み立てに集中する。
    """
    buckets: dict[str, list[str]] = {
        "invalid_format": [],
        "unknown_doc_ids": [],
        "missing_doc_paths": [],
        "missing_trace_tokens": [],
    }
    for trace_ref in trace_refs:
        _classify_trace_ref(
            ctx, trace_ref, source_documents, text_cache, buckets)
    return buckets


def _classify_trace_ref(
    ctx: CheckContext,
    trace_ref: Any,
    source_documents: dict[str, dict[str, Any]],
    text_cache: dict[str, str],
    buckets: dict[str, list[str]],
) -> None:
    """1 つの trace_ref をエラーバケットに振り分ける。

    Args:
        ctx: 検査文脈。
        trace_ref: 検査対象の trace_ref。
        source_documents: source_document id -> dict。
        text_cache: doc_path -> 読み込み済み文字列のキャッシュ。
        buckets: 4 種類のエラーバケット dict。
    Policy:
        - 形式 → doc id → path → token の順に振り分け、最初に該当した時点で return する。
    """
    if _classify_invalid_format(trace_ref, buckets):
        return
    doc_id, trace_token = trace_ref.split(":", 1)
    source_document = _classify_doc_id(
        trace_ref, doc_id, trace_token, source_documents, buckets)
    if source_document is None:
        return
    _classify_doc_path_and_token(
        ctx, trace_ref, trace_token, source_document, text_cache, buckets)


def _classify_invalid_format(
    trace_ref: Any,
    buckets: dict[str, list[str]],
) -> bool:
    """trace_ref の基本形式が無効なら invalid_format に振り分ける。

    Args:
        trace_ref: 検査対象の trace_ref。
        buckets: 4 種類のエラーバケット dict。
    Returns:
        無効として記録したら True。
    Policy:
        - 形式不正の検出を 1 箇所に閉じる。
    """
    if not _is_invalid_trace_ref(trace_ref):
        return False
    buckets["invalid_format"].append(trace_ref)
    return True


def _classify_doc_id(
    trace_ref: str,
    doc_id: str,
    trace_token: str,
    source_documents: dict[str, dict[str, Any]],
    buckets: dict[str, list[str]],
) -> dict[str, Any] | None:
    """doc_id を解決して source_document を返す。

    Args:
        trace_ref: 検査対象の trace_ref。
        doc_id: 分割後の doc_id 部。
        trace_token: 分割後の trace_token 部。
        source_documents: source_document id -> dict。
        buckets: 4 種類のエラーバケット dict。
    Returns:
        解決済みの source_document dict。解決失敗時は None。
    Policy:
        - 空 part と未登録 doc_id をここで振り分ける。
    """
    if _is_empty_trace_part(doc_id, trace_token):
        buckets["invalid_format"].append(trace_ref)
        return None
    source_document = source_documents.get(doc_id)
    if source_document is None:
        buckets["unknown_doc_ids"].append(trace_ref)
        return None
    return source_document


def _classify_doc_path_and_token(
    ctx: CheckContext,
    trace_ref: str,
    trace_token: str,
    source_document: dict[str, Any],
    text_cache: dict[str, str],
    buckets: dict[str, list[str]],
) -> None:
    """doc_path 存在と trace_token の含有を点検する。

    Args:
        ctx: 検査文脈。
        trace_ref: 検査対象の trace_ref。
        trace_token: 分割後の trace_token 部。
        source_document: 解決済みの source_document dict。
        text_cache: doc_path -> 読み込み済み文字列のキャッシュ。
        buckets: 4 種類のエラーバケット dict。
    Policy:
        - path 存在と token 含有を 1 箇所で扱う。
    """
    doc_path_str = source_document["path"]
    doc_path = ctx.repo_root / doc_path_str
    if not doc_path.exists():
        buckets["missing_doc_paths"].append(doc_path_str)
        return
    if doc_path_str not in text_cache:
        text_cache[doc_path_str] = doc_path.read_text(encoding="utf-8")
    if trace_token not in text_cache[doc_path_str]:
        buckets["missing_trace_tokens"].append(trace_ref)


def _is_invalid_trace_ref(trace_ref: Any) -> bool:
    """trace_ref の基本形式が無効かを判定する。

    Args:
        trace_ref: 検査対象の trace_ref。
    Returns:
        str でない / ":" を含まないなら True。
    Policy:
        - 複合 if を述語に閉じ、CR303 を回避する。
    """
    if not isinstance(trace_ref, str):
        return True
    return ":" not in trace_ref


def _is_empty_trace_part(doc_id: str, trace_token: str) -> bool:
    """doc_id / trace_token の片方でも空かを判定する。

    Args:
        doc_id: 分割後の doc_id 部。
        trace_token: 分割後の trace_token 部。
    Returns:
        どちらかが空なら True。
    Policy:
        - 複合 if を述語に閉じ、CR303 を回避する。
    """
    if not doc_id:
        return True
    return not trace_token


def _fill_trace_errors(
    item_errors: dict[str, Any],
    buckets: dict[str, list[str]],
) -> None:
    """trace_ref バケットを item_errors に書き戻す。

    Args:
        item_errors: 出力先 dict。
        buckets: _resolve_trace_refs の結果。
    Policy:
        - 重複を除いた上でソートして観測値の安定性を担保する。
    """
    if buckets["invalid_format"]:
        item_errors["invalid_format"] = buckets["invalid_format"]
    if buckets["unknown_doc_ids"]:
        item_errors["unknown_doc_ids"] = sorted(
            dict.fromkeys(buckets["unknown_doc_ids"]))
    if buckets["missing_doc_paths"]:
        item_errors["missing_doc_paths"] = sorted(
            dict.fromkeys(buckets["missing_doc_paths"]))
    if buckets["missing_trace_tokens"]:
        item_errors["missing_trace_tokens"] = sorted(
            dict.fromkeys(buckets["missing_trace_tokens"]))


def _run_referenced_paths_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """referenced path 存在検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - requirement / acceptance の欠落 path をそれぞれ集計する。
    """
    checked_paths = _get_scope_paths(rule)
    missing_requirements = _collect_missing_paths_from_requirements(
        ctx.repo_root, ctx.data["facts"]["requirements"])
    missing_acceptance = _collect_missing_paths_from_acceptance(
        ctx.repo_root, ctx.data["facts"]["acceptance"])
    if _has_no_path_drift(missing_requirements, missing_acceptance):
        return _build_ok_outcome(rule, checked_paths)
    return _warning(
        rule,
        checked_paths,
        "referenced_paths_exist",
        reason="one or more referenced paths do not exist",
        expected={"repo_root": str(ctx.repo_root)},
        observed={
            "missing_paths_by_requirement": missing_requirements,
            "missing_paths_by_acceptance": missing_acceptance,
        },
    )


def _has_no_path_drift(
    missing_requirements: dict[str, list[str]],
    missing_acceptance: dict[str, list[str]],
) -> bool:
    """referenced path の欠落が無いかを判定する。

    Args:
        missing_requirements: requirement id -> 欠落 path list。
        missing_acceptance: acceptance id -> 欠落 path list。
    Returns:
        欠落が無ければ True。
    Policy:
        - public 関数の述語ガードを 1 つの呼び出しに閉じる。
    """
    if missing_requirements:
        return False
    return not missing_acceptance


def _collect_missing_paths_from_requirements(
    repo_root: Path,
    requirements: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """active な requirement の欠落 path を集める。

    Args:
        repo_root: リポジトリのルート。
        requirements: facts.requirements の list。
    Returns:
        requirement id -> 欠落 path list の dict。
    Policy:
        - affected_paths / verification_refs / source_refs を結合して点検する。
    """
    missing: dict[str, list[str]] = {}
    for requirement in requirements:
        if requirement.get("status") != "active":
            continue
        paths_to_check = (
            list(requirement.get("affected_paths", []))
            + list(requirement.get("verification_refs", []))
            + list(requirement.get("source_refs", []))
        )
        stale = _collect_stale_paths(repo_root, paths_to_check)
        if stale:
            missing[requirement["id"]] = stale
    return missing


def _collect_missing_paths_from_acceptance(
    repo_root: Path,
    acceptances: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """active な acceptance の verification.refs を点検する。

    Args:
        repo_root: リポジトリのルート。
        acceptances: facts.acceptance の list。
    Returns:
        acceptance id -> 欠落 path list の dict。
    Policy:
        - verification dict 以外は空 list として扱う。
    """
    missing: dict[str, list[str]] = {}
    for acceptance in acceptances:
        if acceptance.get("status", "active") != "active":
            continue
        verification = acceptance.get("verification", {})
        refs = _extract_verification_refs(verification)
        stale = _collect_stale_paths(repo_root, refs)
        if stale:
            missing[acceptance["id"]] = stale
    return missing


def _extract_verification_refs(verification: Any) -> list[str]:
    """verification dict から refs list を取り出す。

    Args:
        verification: acceptance.verification の値。
    Returns:
        refs の list。dict 以外なら空 list。
    Policy:
        - 後段で path 走査するため、必ず list を返す。
    """
    if not isinstance(verification, dict):
        return []
    return verification.get("refs", [])


def _collect_stale_paths(
        repo_root: Path, paths: list[str]) -> list[str]:
    """存在しない path だけを残して返す。

    Args:
        repo_root: リポジトリのルート。
        paths: 検査対象 path の list。
    Returns:
        存在しない path の list。
    Policy:
        - 内包表記をこの helper に閉じ、呼び出し側を簡潔に保つ。
    """
    return [
        path_value
        for path_value in paths
        if not (repo_root / path_value).exists()
    ]


def _run_tasknote_frontmatter_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """タスクノート frontmatter 整合性検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - ノートの探索と検査を private helper に委ね、warning を組み立てる。
    """
    checked_paths = _get_scope_paths(rule)
    contracts = ctx.data["facts"]["tasknote_contracts"]
    errors = _collect_tasknote_errors(ctx, contracts)
    if not errors:
        return _build_ok_outcome(rule, checked_paths)
    return _warning(
        rule,
        checked_paths,
        "tasknote_frontmatter_integrity",
        reason="one or more opt-in task notes have invalid frontmatter",
        expected={
            "required_frontmatter_keys":
                contracts["required_frontmatter_keys"]},
        observed={"tasknote_errors": errors},
    )


def _collect_tasknote_errors(
    ctx: CheckContext,
    contracts: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """opt-in ノート全件の frontmatter エラーを集める。

    Args:
        ctx: 検査文脈。
        contracts: tasknote_contracts dict。
    Returns:
        相対 path -> note error dict の dict。
    Policy:
        - 検査素材（id 集合と note glob）をここで一括用意し、private helper に渡す。
    """
    facts = ctx.data["facts"]
    materials = _build_tasknote_materials(facts)
    errors: dict[str, dict[str, Any]] = {}
    for note_path in sorted(ctx.repo_root.glob(contracts["note_glob"])):
        frontmatter = _load_frontmatter(note_path)
        if not _is_opt_in_frontmatter(frontmatter, contracts):
            continue
        note_errors = _collect_single_tasknote_errors(
            frontmatter, contracts, materials)
        if note_errors:
            rel = str(note_path.relative_to(ctx.repo_root))
            errors[rel] = note_errors
    return errors


def _build_tasknote_materials(
        facts: dict[str, Any]) -> dict[str, Any]:
    """tasknote 検査で使う id 集合と map を 1 つの dict にまとめる。

    Args:
        facts: 解析済みの facts dict。
    Returns:
        requirement / stakeholder / acceptance の id と map を含む dict。
    Policy:
        - 同じ素材を複数の helper で使うため、入口でまとめて作る。
    """
    requirement_map = _build_id_map(facts["requirements"])
    acceptance_map = _build_id_map(facts["acceptance"])
    return {
        "requirement_ids": set(requirement_map),
        "stakeholder_ids": set(_build_id_map(facts["stakeholders"])),
        "acceptance_map": acceptance_map,
        "acceptance_ids": set(acceptance_map),
    }


def _is_opt_in_frontmatter(
    frontmatter: dict[str, Any] | None,
    contracts: dict[str, Any],
) -> bool:
    """frontmatter が opt-in 対象かを判定する。

    Args:
        frontmatter: ノートから読み取った dict。
        contracts: tasknote_contracts dict。
    Returns:
        opt-in キーを含むなら True。
    Policy:
        - 複合 if を述語に閉じ、CR303 を回避する。
    """
    if not frontmatter:
        return False
    return contracts["opt_in_frontmatter_key"] in frontmatter


def _collect_single_tasknote_errors(
    frontmatter: dict[str, Any],
    contracts: dict[str, Any],
    materials: dict[str, Any],
) -> dict[str, Any]:
    """1 ノートぶんの frontmatter エラーを返す。

    Args:
        frontmatter: ノートから読み取った dict。
        contracts: tasknote_contracts dict。
        materials: _build_tasknote_materials の戻り値。
    Returns:
        error 種別 -> 値の dict。
    Policy:
        - 必須キー欠落、未解決 id、リンク不整合を private helper でまとめる。
    """
    note_errors: dict[str, Any] = {}
    _fill_missing_keys(note_errors, frontmatter, contracts)
    _fill_unknown_ids(note_errors, frontmatter, materials)
    _fill_linkage_errors(note_errors, frontmatter, materials)
    _fill_done_checks_type(note_errors, frontmatter)
    return note_errors


def _fill_missing_keys(
    note_errors: dict[str, Any],
    frontmatter: dict[str, Any],
    contracts: dict[str, Any],
) -> None:
    """frontmatter に必須キーが揃うかを点検する。

    Args:
        note_errors: 出力先 dict。
        frontmatter: ノートから読み取った dict。
        contracts: tasknote_contracts dict。
    Policy:
        - 欠落キーがあれば missing_keys として記録する。
    """
    missing_keys = [
        key for key in contracts["required_frontmatter_keys"]
        if key not in frontmatter
    ]
    if missing_keys:
        note_errors["missing_keys"] = missing_keys


_UNKNOWN_ID_SPECS = (
    ("requirement_ids", "requirement_ids", "unknown_requirement_ids"),
    ("stakeholder_ids", "stakeholder_ids", "unknown_stakeholder_ids"),
    ("acceptance_ids", "acceptance_ids", "unknown_acceptance_ids"),
)


def _fill_unknown_ids(
    note_errors: dict[str, Any],
    frontmatter: dict[str, Any],
    materials: dict[str, Any],
) -> None:
    """3 種の id list について未解決値を点検する。

    Args:
        note_errors: 出力先 dict。
        frontmatter: ノートから読み取った dict。
        materials: id 集合と map を含む dict。
    Policy:
        - requirement / stakeholder / acceptance の未解決をまとめて記録する。
    """
    for frontmatter_key, materials_key, error_key in _UNKNOWN_ID_SPECS:
        _record_unknown_ids_for_key(
            note_errors,
            frontmatter,
            frontmatter_key,
            materials[materials_key],
            error_key,
        )


def _record_unknown_ids_for_key(
    note_errors: dict[str, Any],
    frontmatter: dict[str, Any],
    frontmatter_key: str,
    known_ids: set[str],
    error_key: str,
) -> None:
    """1 つの frontmatter id list の未解決値を記録する。

    Args:
        note_errors: 出力先 dict。
        frontmatter: ノートから読み取った dict。
        frontmatter_key: frontmatter 側のキー名。
        known_ids: 既知 id 集合。
        error_key: note_errors に書き込むキー名。
    Policy:
        - 1 種 id list の点検と書き込みをこの helper に閉じる。
    """
    unresolved = [
        item for item in frontmatter.get(frontmatter_key, [])
        if item not in known_ids
    ]
    if unresolved:
        note_errors[error_key] = unresolved


def _fill_linkage_errors(
    note_errors: dict[str, Any],
    frontmatter: dict[str, Any],
    materials: dict[str, Any],
) -> None:
    """acceptance_ids と requirement_ids の整合性を点検する。

    Args:
        note_errors: 出力先 dict。
        frontmatter: ノートから読み取った dict。
        materials: id 集合と map を含む dict。
    Policy:
        - 双方が list で揃ったときのみ整合検査する。
    """
    if not _has_both_id_lists(frontmatter):
        return
    accepted_requirement_ids = set(frontmatter["requirement_ids"])
    acceptance_map = materials["acceptance_map"]
    mismatched_acceptance = [
        item
        for item in frontmatter["acceptance_ids"]
        if _is_acceptance_unlinked(
            item, acceptance_map, accepted_requirement_ids)
    ]
    if mismatched_acceptance:
        note_errors[
            "acceptance_ids_not_linked_to_requirement_ids"
        ] = mismatched_acceptance


def _has_both_id_lists(frontmatter: dict[str, Any]) -> bool:
    """acceptance_ids と requirement_ids が共に list 形か判定する。

    Args:
        frontmatter: ノートから読み取った dict。
    Returns:
        両方が list なら True。
    Policy:
        - 複合 if を述語に閉じ、CR302 / CR303 を回避する。
    """
    if "acceptance_ids" not in frontmatter:
        return False
    if "requirement_ids" not in frontmatter:
        return False
    if not isinstance(frontmatter["acceptance_ids"], list):
        return False
    return isinstance(frontmatter["requirement_ids"], list)


def _is_acceptance_unlinked(
    item: str,
    acceptance_map: dict[str, dict[str, Any]],
    accepted_requirement_ids: set[str],
) -> bool:
    """acceptance が requirement_ids に紐づいていないかを判定する。

    Args:
        item: acceptance id。
        acceptance_map: acceptance id -> dict。
        accepted_requirement_ids: ノートで宣言された requirement id 集合。
    Returns:
        紐づかないなら True。
    Policy:
        - 複合 if を述語に閉じ、CR303 を回避する。
    """
    if item not in acceptance_map:
        return False
    parent = acceptance_map[item].get("requirement_id")
    return parent not in accepted_requirement_ids


def _fill_done_checks_type(
    note_errors: dict[str, Any],
    frontmatter: dict[str, Any],
) -> None:
    """done_checks が list 形かを点検する。

    Args:
        note_errors: 出力先 dict。
        frontmatter: ノートから読み取った dict。
    Policy:
        - list でなければ done_checks_not_list を立てる。
    """
    if "done_checks" not in frontmatter:
        return
    if isinstance(frontmatter["done_checks"], list):
        return
    note_errors["done_checks_not_list"] = True


def _run_normalized_lists_check(
        ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    """正規化 list ドリフト検査の本体。

    Args:
        ctx: 検査文脈。
        rule: 評価対象の rule dict。
    Returns:
        CheckOutcome。
    Policy:
        - requirement / request それぞれの list を private helper で点検する。
    """
    checked_paths = _get_scope_paths(rule)
    requirement_drift = _collect_requirement_list_drift(
        ctx.data["facts"]["requirements"])
    request_drift = _collect_request_list_drift(
        ctx.data["facts"]["requests"])
    if _has_no_normalized_drift(requirement_drift, request_drift):
        return _build_ok_outcome(rule, checked_paths)
    return _build_normalized_lists_warning(
        rule, checked_paths, requirement_drift, request_drift)


def _build_normalized_lists_warning(
    rule: dict[str, Any],
    checked_paths: list[str],
    requirement_drift: dict[str, dict[str, dict[str, list[str]]]],
    request_drift: dict[str, dict[str, dict[str, list[str]]]],
) -> CheckOutcome:
    """正規化 list ドリフトの warning を組み立てる。

    Args:
        rule: validation_rules の 1 件。
        checked_paths: 検査対象 path の list。
        requirement_drift: requirement 側ドリフト dict。
        request_drift: request 側ドリフト dict。
    Returns:
        warning 状態の CheckOutcome。
    Policy:
        - observed 組み立てをこの helper に閉じる。
    """
    return _warning(
        rule,
        checked_paths,
        "normalized_requirement_lists",
        reason=(
            "request or requirement list ordering or duplicates differ "
            "from normalized form"),
        observed={
            "requirement_list_drift": requirement_drift,
            "request_list_drift": request_drift,
        },
    )


def _has_no_normalized_drift(
    requirement_drift: dict[str, dict[str, dict[str, list[str]]]],
    request_drift: dict[str, dict[str, dict[str, list[str]]]],
) -> bool:
    """正規化ドリフトが無いかを判定する。

    Args:
        requirement_drift: requirement id -> drift dict。
        request_drift: request id -> drift dict。
    Returns:
        ドリフトが無ければ True。
    Policy:
        - public 関数の述語ガードを 1 つの呼び出しに閉じる。
    """
    if requirement_drift:
        return False
    return not request_drift


def _collect_requirement_list_drift(
    requirements: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, list[str]]]]:
    """requirement の list キーをまとめて正規化点検する。

    Args:
        requirements: facts.requirements の list。
    Returns:
        requirement id -> key -> {current, normalized} の dict。
    Policy:
        - 監視対象キーをこの helper に閉じる。
    """
    requirement_list_keys = (
        "derived_from_request_ids",
        "stakeholder_ids",
        "acceptance_ids",
        "source_trace_refs",
        "affected_paths",
        "verification_refs",
        "source_refs",
    )
    drift: dict[str, dict[str, dict[str, list[str]]]] = {}
    for requirement in requirements:
        item_drift = _collect_item_drift(requirement, requirement_list_keys)
        if item_drift:
            drift[requirement["id"]] = item_drift
    return drift


def _collect_request_list_drift(
    requests: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, list[str]]]]:
    """request の list キーを正規化点検する。

    Args:
        requests: facts.requests の list。
    Returns:
        request id -> key -> {current, normalized} の dict。
    Policy:
        - source_trace_refs と source_refs だけを対象にする。
    """
    request_list_keys = ("source_trace_refs", "source_refs")
    drift: dict[str, dict[str, dict[str, list[str]]]] = {}
    for request in requests:
        item_drift = _collect_item_drift(request, request_list_keys)
        if item_drift:
            drift[request["id"]] = item_drift
    return drift


def _collect_item_drift(
    item: dict[str, Any],
    list_keys: tuple[str, ...],
) -> dict[str, dict[str, list[str]]]:
    """1 件の item に対する list ドリフトを返す。

    Args:
        item: facts セクションの 1 件。
        list_keys: 検査対象 key のタプル。
    Returns:
        key -> {current, normalized} の dict。
    Policy:
        - 「現状」と「正規化済み」を 1 つの dict にまとめて出力する。
    """
    item_drift: dict[str, dict[str, list[str]]] = {}
    for key in list_keys:
        current = list(item.get(key, []))
        normalized = sorted(dict.fromkeys(current))
        if current != normalized:
            item_drift[key] = {
                "current": current,
                "normalized": normalized,
            }
    return item_drift


CHECK_REGISTRY = {
    "id_uniqueness": check_id_uniqueness,
    "stakeholder_reference_integrity": check_stakeholder_reference_integrity,
    "request_reference_integrity": check_request_reference_integrity,
    "requirement_has_code_hints": check_requirement_has_code_hints,
    "requirement_acceptance_integrity": check_requirement_acceptance_integrity,
    "acceptance_has_verification": check_acceptance_has_verification,
    "source_traceability_integrity": check_source_traceability_integrity,
    "referenced_paths_exist": check_referenced_paths_exist,
    "tasknote_frontmatter_integrity": check_tasknote_frontmatter_integrity,
    "normalized_requirement_lists": check_normalized_requirement_lists,
}


def _build_arg_parser() -> argparse.ArgumentParser:
    """CLI 用の argparse を組み立てる。

    Returns:
        --rules-path / --rule-id を持つ ArgumentParser。
    Policy:
        - description は本モジュールの docstring 1 行目を使う。
    """
    description = "stakeholder voices deterministic checker"
    if __doc__:
        description = __doc__.splitlines()[0]
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=ROOT / "docs" / "stakeholder_voices.yml")
    parser.add_argument("--rule-id", action="append", default=None)
    return parser


def _run_main_with_args(args: argparse.Namespace) -> dict[str, Any]:
    """parse 済み args から payload を組み立てる。

    Args:
        args: argparse の Namespace。
    Returns:
        run_checker の payload。
    Policy:
        - rule-id 指定を set 化する分岐をこの helper に閉じる。
    """
    rule_ids = set(args.rule_id) if args.rule_id else None
    return run_checker(ROOT, args.rules_path, rule_ids=rule_ids)


def _emit_payload_and_exit_code(payload: dict[str, Any]) -> int:
    """payload を stdout に書き、exit code を返す。

    Args:
        payload: run_checker の出力。
    Returns:
        常に 0。
    Policy:
        - 出力先と exit code 決定を 1 箇所に閉じる。
    """
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
