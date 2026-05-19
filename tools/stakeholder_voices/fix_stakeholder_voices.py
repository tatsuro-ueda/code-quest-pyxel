"""stakeholder voice warning に対して一度だけ deterministic fix を適用する CLI。

このファイルに含まれる関数・クラス：

- YAML を人間向けに整形するための public クラス _ReadableYamlDumper
- YAML をロードする public 関数 load_yaml
- YAML を書き戻す public 関数 write_yaml
- requirements / requests のリスト系フィールドを正規化する public 関数
  normalize_requirement_lists
- check -> fix -> recheck を 1 回回す public 関数 run_fixer
- CLI 入口の public 関数 main（引数解析と JSON 出力と exit code 制御）
- YAML テキストを行単位で human friendly に整形する内部関数
  _format_yaml_for_humans
- 行ごとに空行 separator を入れるかの判定述語 _has_section_break
- requirements を 1 件だけ正規化する内部関数 _normalize_one_requirement
- requests を 1 件だけ正規化する内部関数 _normalize_one_request
- run_fixer の初期 check ステップを担う内部関数 _run_initial_fix_check
- 初期 check の clean 判定を反転して返す述語関数 _is_clean_check
- check の warning 結果に対応する fixer を当てて diff を集める内部関数
  _apply_fixers_to_data
- 1 件の result が修正対象かを判定する述語関数 _can_fix_result
- fix 適用後に YAML を書き戻すかを決める内部関数 _persist_if_fixes_applied
- post_check の結果と applied_fixes から status を決める内部関数
  _decide_fixer_status
- 初期 check が clean な場合の OK payload を組み立てる内部関数
  _build_clean_fixer_payload
- fix ループの最終 payload を組み立てる内部関数 _build_fixer_payload
- argparse を構成して Namespace を返す内部関数 _build_arg_parser
- Namespace から run_fixer を呼んで payload を得る内部関数
  _run_main_with_args
- payload を stdout に出力して exit code を返す内部関数
  _emit_payload_and_exit_code

Problems:
    - check と fix を別の CLI に分けて呼ぶと、運用側で順序を間違えやすい。
    - 1 つの run_fixer / main に分岐とループと履歴整形を直書きすると、
      入口契約と実装詳細が混ざって読み手の判断がブレる。

Solutions:
    - 本 CLI を deterministic fix 入口に固定し、check / 修正適用 /
      書き戻し / recheck を 1 回の呼び出しで束ねる。
    - public 関数は「述語呼び出し + private 委譲 + return」のステップ列に揃え、
      ループ・履歴整形・status 決定は private helper に切り出す。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from . import check_stakeholder_voices


ROOT = Path(__file__).resolve().parents[2]
REQUIREMENT_NORMALIZED_LIST_KEYS = (
    "derived_from_request_ids",
    "acceptance_ids",
    "stakeholder_ids",
    "source_trace_refs",
    "affected_paths",
    "verification_refs",
    "source_refs",
)
REQUEST_NORMALIZED_LIST_KEYS = (
    "source_trace_refs",
    "source_refs",
)
_SECTION_HEADER_LINES = frozenset({"facts:", "validation_rules:"})


# === Public API ===

class _ReadableYamlDumper(yaml.SafeDumper):
    """YAML を人間向けに整形するための SafeDumper サブクラス。

    Policy:
        - increase_indent を override してリスト要素のインデントを揃える。
    """

    # === Public API ===

    def increase_indent(  # noqa: CR204
            self,
            flow: bool = False,
            indentless: bool = False) -> Any:
        """super().increase_indent に indentless=False を強制する。

        Args:
            flow: 親クラス互換のフラグ。
            indentless: 受け取るが常に False で渡す。
        Returns:
            super().increase_indent の戻り値。
        Policy:
            - リスト要素の indent を人間向けに統一する。
        """
        del indentless
        return super().increase_indent(flow, False)


def load_yaml(path: Path) -> dict[str, Any]:
    """YAML ファイルをロードして dict を返す。

    Args:
        path: ロード対象 YAML のパス。
    Returns:
        yaml.safe_load の戻り値。
    Policy:
        - encoding は utf-8 に固定する。
    """
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    """data を人間向け整形して path に書き戻す。

    Args:
        path: 書き戻し対象 YAML のパス。
        data: 書き戻す dict。
    Returns:
        なし。
    Policy:
        - 整形ロジックは _format_yaml_for_humans に委ねる。
    """
    path.write_text(_format_yaml_for_humans(data), encoding="utf-8")


def normalize_requirement_lists(
        data: dict[str, Any]) -> list[dict[str, str]]:
    """requirements / requests のリスト系フィールドを正規化する。

    Args:
        data: load_yaml の戻り値（in-place で更新する）。
    Returns:
        applied_fixes に積む dict のリスト。
    Policy:
        - public 関数はステップ列に揃え、requirements と requests の
          1 件ずつの正規化を private helper に委ねる。
    """
    fixes: list[dict[str, str]] = []
    requirements = data.get("facts", {}).get("requirements", [])
    requests = data.get("facts", {}).get("requests", [])
    fixes.extend(_normalize_requirement_collection(requirements))
    fixes.extend(_normalize_request_collection(requests))
    return fixes


FIXER_REGISTRY = {
    "normalized_requirement_lists": normalize_requirement_lists,
}


def run_fixer(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    """check -> fix -> recheck を 1 回回して payload を返す。

    Args:
        repo_root: リポジトリのルート。
        rules_path: 検査対象 YAML のパス。
        rule_ids: 限定実行する rule id 集合（None で全件）。
    Returns:
        status / check / post_check / applied_fixes を含む payload。
    Policy:
        - public 関数はステップ列に揃え、clean 早期 return と fix 適用は
          private helper に委ねる。
    """
    check = _run_initial_fix_check(repo_root, rules_path, rule_ids)
    is_clean = _is_clean_check(check)
    return _run_fixer_after_initial_check(
        repo_root, rules_path, rule_ids, check, is_clean=is_clean)


def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """CLI 入口。引数解析と run_fixer 呼び出しと JSON 出力を束ねる。

    Args:
        argv: コマンドライン引数。None で sys.argv を使う。
    Returns:
        OK / FIXED は 0、それ以外は 1。
    Policy:
        - public 関数はステップ列に揃え、引数解析と payload 算出と
          stdout 出力は private helper に委ねる。
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    payload = _run_main_with_args(args)
    return _emit_payload_and_exit_code(payload)


# === Internal helpers (private) ===

def _format_yaml_for_humans(data: dict[str, Any]) -> str:
    """yaml.dump 結果に空行 separator を入れて返す。

    Args:
        data: ダンプ対象 dict。
    Returns:
        末尾改行を保証した整形済み YAML 文字列。
    Policy:
        - section 境界と top-level list 要素の前に空行を入れる。
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
        if _has_section_break(line, formatted):
            formatted.append("")
        formatted.append(line)
    return "\n".join(formatted).lstrip("\n") + "\n"


def _has_section_break(line: str, formatted: list[str]) -> bool:
    """整形中の行の前に空行 separator を入れるべきかの述語。

    Args:
        line: 整形対象の行（rstrip 済み）。
        formatted: これまで積んだ整形済み行リスト。
    Returns:
        separator を入れるべきとき True、そうでなければ False。
    Policy:
        - section header と top-level list 要素のみ separator 対象。
    """
    is_break_line = _is_section_break_line(line)
    if not is_break_line:
        return False
    if not formatted:
        return False
    return formatted[-1] != ""


def _is_section_break_line(line: str) -> bool:
    """行が section 区切りを起こす行かの述語。

    Args:
        line: 整形対象の行（rstrip 済み）。
    Returns:
        section header か top-level list 要素なら True。
    Policy:
        - 判定基準を CR302 を踏まないように 2 述語の論理和に分解する。
    """
    if line in _SECTION_HEADER_LINES:
        return True
    return _is_top_level_id_item(line)


def _is_top_level_id_item(line: str) -> bool:
    """line が top-level の `- id:` リスト要素かの述語。

    Args:
        line: 整形対象の行（rstrip 済み）。
    Returns:
        該当すれば True。
    Policy:
        - indent <= 4 かつ "- id:" 始まりを判定する。
    """
    stripped = line.lstrip()
    if not stripped.startswith("- id:"):
        return False
    indent = len(line) - len(stripped)
    return indent <= 4


def _normalize_requirement_collection(
        requirements: list[dict[str, Any]]) -> list[dict[str, str]]:
    """requirements 全件を 1 件ずつ正規化して fixes を集める。

    Args:
        requirements: facts.requirements リスト（in-place で更新）。
    Returns:
        applied_fixes 相当の dict リスト。
    Policy:
        - 1 件ずつの正規化は _normalize_one_requirement に委ねる。
    """
    fixes: list[dict[str, str]] = []
    for requirement in requirements:
        fixes.extend(_normalize_one_requirement(requirement))
    return fixes


def _normalize_request_collection(
        requests: list[dict[str, Any]]) -> list[dict[str, str]]:
    """requests 全件を 1 件ずつ正規化して fixes を集める。

    Args:
        requests: facts.requests リスト（in-place で更新）。
    Returns:
        applied_fixes 相当の dict リスト。
    Policy:
        - 1 件ずつの正規化は _normalize_one_request に委ねる。
    """
    fixes: list[dict[str, str]] = []
    for request in requests:
        fixes.extend(_normalize_one_request(request))
    return fixes


def _normalize_one_requirement(
        requirement: dict[str, Any]) -> list[dict[str, str]]:
    """requirement 1 件のリスト系フィールドを正規化する。

    Args:
        requirement: facts.requirements の 1 要素（in-place で更新）。
    Returns:
        applied_fixes 相当の dict リスト。
    Policy:
        - 対象 key 列は REQUIREMENT_NORMALIZED_LIST_KEYS に従う。
    """
    requirement_id = requirement.get("id", "<unknown>")
    return _normalize_list_keys(
        requirement,
        REQUIREMENT_NORMALIZED_LIST_KEYS,
        owner_id=requirement_id,
        owner_path="facts.requirements",
    )


def _normalize_one_request(
        request: dict[str, Any]) -> list[dict[str, str]]:
    """request 1 件のリスト系フィールドを正規化する。

    Args:
        request: facts.requests の 1 要素（in-place で更新）。
    Returns:
        applied_fixes 相当の dict リスト。
    Policy:
        - 対象 key 列は REQUEST_NORMALIZED_LIST_KEYS に従う。
    """
    request_id = request.get("id", "<unknown>")
    return _normalize_list_keys(
        request,
        REQUEST_NORMALIZED_LIST_KEYS,
        owner_id=request_id,
        owner_path="facts.requests",
    )


def _normalize_list_keys(
        owner: dict[str, Any],
        keys: tuple[str, ...],
        *,
        owner_id: str,
        owner_path: str) -> list[dict[str, str]]:
    """owner["key"] を sorted unique に揃え、差分を fixes に積む。

    Args:
        owner: 正規化対象 dict（in-place で更新）。
        keys: 対象キー集合。
        owner_id: ログ用 id。
        owner_path: 出力 detail の path 文字列。
    Returns:
        applied_fixes 相当の dict リスト。
    Policy:
        - dict.fromkeys + sorted の組み合わせで dedup + sort を行う。
    """
    fixes: list[dict[str, str]] = []
    for key in keys:
        current = list(owner.get(key, []))
        normalized = sorted(dict.fromkeys(current))
        if current == normalized:
            continue
        owner[key] = normalized
        fixes.append({
            "kind": "yaml",
            "path": owner_path,
            "detail": f"normalized {owner_id}:{key}",
        })
    return fixes


def _run_initial_fix_check(
        repo_root: Path,
        rules_path: Path,
        rule_ids: set[str] | None) -> dict[str, Any]:
    """run_fixer の初期 check を実行して結果を返す。

    Args:
        repo_root: リポジトリのルート。
        rules_path: 検査対象 YAML のパス。
        rule_ids: 限定実行する rule id 集合。
    Returns:
        run_checker の戻り値。
    Policy:
        - check_stakeholder_voices.run_checker への薄いブリッジに留める。
    """
    return check_stakeholder_voices.run_checker(
        repo_root, rules_path, rule_ids=rule_ids)


def _is_clean_check(check: dict[str, Any]) -> bool:
    """check に warning が無ければ True を返す述語。

    Args:
        check: run_checker の戻り値。
    Returns:
        warning が 0 件なら True。
    Policy:
        - has_warnings の反転だけを担う薄い述語に留める。
    """
    return not check["has_warnings"]


def _run_fixer_after_initial_check(
        repo_root: Path,
        rules_path: Path,
        rule_ids: set[str] | None,
        check: dict[str, Any],
        *,
        is_clean: bool) -> dict[str, Any]:
    """初期 check の結果を踏まえて clean 早期 return か fix 適用へ分岐する。

    Args:
        repo_root: リポジトリのルート。
        rules_path: 検査対象 YAML のパス。
        rule_ids: 限定実行する rule id 集合。
        check: 初期 run_checker の戻り値。
        is_clean: warning 無しなら True。
    Returns:
        run_fixer の payload。
    Policy:
        - 制御フローを run_fixer から引き取る。
    """
    if is_clean:
        return _build_clean_fixer_payload(check)
    data = load_yaml(rules_path)
    applied_fixes = _apply_fixers_to_data(check, data)
    _persist_if_fixes_applied(rules_path, data, applied_fixes)
    post_check = check_stakeholder_voices.run_checker(
        repo_root, rules_path, rule_ids=rule_ids)
    return _build_fixer_payload(check, post_check, applied_fixes)


def _can_fix_result(result: dict[str, Any]) -> bool:
    """result が deterministic fix の対象かの述語。

    Args:
        result: run_checker の 1 結果。
    Returns:
        status が warning かつ FIXER_REGISTRY に登録済みなら True。
    Policy:
        - registry に無い rule は静かに skip する。
    """
    if result["status"] != "warning":
        return False
    return result["rule_id"] in FIXER_REGISTRY


def _apply_fixers_to_data(
        check: dict[str, Any],
        data: dict[str, Any]) -> list[dict[str, str]]:
    """check["results"] に対応する fixer を当てて applied_fixes を返す。

    Args:
        check: run_checker の戻り値。
        data: load_yaml の戻り値（in-place で更新する）。
    Returns:
        applied_fixes リスト。
    Policy:
        - 1 件ずつの fix 適用は FIXER_REGISTRY 経由で行う。
    """
    applied_fixes: list[dict[str, str]] = []
    for result in check["results"]:
        if not _can_fix_result(result):
            continue
        applied_fixes.extend(FIXER_REGISTRY[result["rule_id"]](data))
    return applied_fixes


def _persist_if_fixes_applied(
        rules_path: Path,
        data: dict[str, Any],
        applied_fixes: list[dict[str, str]]) -> None:
    """applied_fixes があるときだけ YAML を書き戻す。

    Args:
        rules_path: 書き戻し対象 YAML のパス。
        data: 書き戻す dict。
        applied_fixes: _apply_fixers_to_data の戻り値。
    Returns:
        なし。
    Policy:
        - I/O は applied_fixes が空のとき避ける。
    """
    if applied_fixes:
        write_yaml(rules_path, data)


def _decide_fixer_status(
        check: dict[str, Any],
        post_check: dict[str, Any],
        applied_fixes: list[dict[str, str]]) -> str:
    """run_fixer の最終 status を決める。

    Args:
        check: 初期 run_checker の戻り値。
        post_check: 修正後 run_checker の戻り値。
        applied_fixes: _apply_fixers_to_data の戻り値。
    Returns:
        OK / FIXED / NEEDS_HUMAN のいずれか。
    Policy:
        - 早期 return で if/elif チェーンを避ける。
    """
    if _is_clean_check(post_check):
        if applied_fixes:
            return "FIXED"
        return "OK"
    return "NEEDS_HUMAN"


def _build_clean_fixer_payload(
        check: dict[str, Any]) -> dict[str, Any]:
    """初期 check が clean な場合の OK payload を組み立てる。

    Args:
        check: run_checker の戻り値。
    Returns:
        status="OK" の payload。
    Policy:
        - post_check には初期 check をそのまま流用する。
    """
    return {
        "status": "OK",
        "check": check,
        "post_check": check,
        "applied_fixes": [],
    }


def _build_fixer_payload(
        check: dict[str, Any],
        post_check: dict[str, Any],
        applied_fixes: list[dict[str, str]]) -> dict[str, Any]:
    """fix 適用後の payload を組み立てる。

    Args:
        check: 初期 run_checker の戻り値。
        post_check: 修正後 run_checker の戻り値。
        applied_fixes: _apply_fixers_to_data の戻り値。
    Returns:
        run_fixer の最終 payload。
    Policy:
        - status の決定は _decide_fixer_status に委ねる。
    """
    return {
        "status": _decide_fixer_status(check, post_check, applied_fixes),
        "check": check,
        "post_check": post_check,
        "applied_fixes": applied_fixes,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    """main 用の argparse を構成して返す。

    Returns:
        --rules-path / --rule-id を持つ parser。
    Policy:
        - default rules-path は ROOT/docs/stakeholder_voices.yml に固定する。
    """
    parser = argparse.ArgumentParser(
        description="stakeholder voices deterministic fixer")
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=ROOT / "docs" / "stakeholder_voices.yml",
    )
    parser.add_argument("--rule-id", action="append", default=None)
    return parser


def _run_main_with_args(args: argparse.Namespace) -> dict[str, Any]:
    """argparse Namespace から run_fixer を呼び出して payload を返す。

    Args:
        args: parser.parse_args の戻り値。
    Returns:
        run_fixer の戻り値。
    Policy:
        - rule_id は list でも未指定でも set | None に正規化する。
    """
    rule_ids = set(args.rule_id) if args.rule_id else None
    return run_fixer(ROOT, args.rules_path, rule_ids=rule_ids)


def _emit_payload_and_exit_code(payload: dict[str, Any]) -> int:
    """payload を stdout に JSON 出力し exit code を返す。

    Args:
        payload: run_fixer の戻り値。
    Returns:
        status が OK / FIXED なら 0、それ以外は 1。
    Policy:
        - 終了コードの判定は status 集合との照合のみで行う。
    """
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if payload["status"] in {"OK", "FIXED"}:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
