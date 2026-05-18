"""source_trace_refs の coverage を source document ごとに集計する CLI。

このファイルに含まれる関数・クラス：

- 指定 source_document から stable_ref 集合と抽出エラーを返す
  public 関数 extract_stable_refs
- 全 source_document の coverage を集計して report dict を返す
  public 関数 build_report
- build_report の薄いブリッジで CLI と共有する public 関数 run_report
- 引数解析と JSON 出力と exit code 制御をする public 関数 main
- kind と payload を 1 つの error dict に組み立てる
  private 関数 _build_error_entry
- 追跡対象 status の trace_ref 使用箇所を yield する
  private 関数 _iter_tracked_source_trace_refs
- 1 巡で doc_id 別の referenced 集合とエラーを集める
  private 関数 _collect_referenced_refs
- 1 usage を解析して doc_id / stable_ref / error に分ける
  private 関数 _classify_usage
- trace_ref が doc_id:stable_ref 形式でないかを返す
  述語関数 _is_malformed_trace_ref
- 分解後の doc_id / stable_ref のどちらかが空かを返す
  述語関数 _is_blank_trace_ref_part
- extraction の regex/literals が list でないかを返す
  述語関数 _has_invalid_extraction_lists
- regex/literals がどちらも空かを返す
  述語関数 _has_no_extraction_target
- regex pattern が文字列でないか空白だけかを返す
  述語関数 _is_empty_regex_pattern
- literal ref が文字列でないか空白だけかを返す
  述語関数 _is_empty_literal_ref
- doc_path / extraction 契約を 2 段で検証する
  private 関数 _validate_extraction_contract
- doc_path 存在チェックだけを切り出した
  private 関数 _check_doc_path_exists
- extraction 契約チェックだけを切り出した
  private 関数 _check_extraction_contract
- invalid_extraction_contract の error dict 組み立て
  private 関数 _make_invalid_extraction_error
- 契約検証の結果から抽出を実行して未抽出ガードを足す
  private 関数 _extract_stable_refs_after_validation
- 本文に regex/literals 抽出を走らせて結果をマージする
  private 関数 _extract_refs_from_text
- regex pattern 群から stable_ref 集合とエラーを返す
  private 関数 _extract_refs_by_regex
- 1 regex pattern を処理して ref と error を返す
  private 関数 _process_regex_pattern
- invalid_regex_pattern の error dict 組み立て
  private 関数 _make_invalid_regex_error
- literal 群から stable_ref 集合とエラーを返す
  private 関数 _extract_refs_by_literals
- 1 literal を処理して ref と error を返す
  private 関数 _process_literal_ref
- 全 source_document の document entry を集計する
  private 関数 _build_document_entries
- 1 source_document の document entry を組み立てる
  private 関数 _build_document_entry
- 1 source_document の extracted/errors/差分を 1 回で算出する
  private 関数 _compute_doc_artifacts
- unexpected_referenced があれば referenced_ref_missing… エラーを足す
  private 関数 _append_unexpected_referenced_error
- document entry dict をフィールド順に組み立てる
  private 関数 _format_document_entry
- referenced と extracted から missing / unexpected の差分を返す
  private 関数 _compute_ref_diffs
- documents 集計から summary dict を組み立てる
  private 関数 _build_summary
- main 用の argparse parser を組み立てる
  private 関数 _build_arg_parser
- payload を stdout に出して exit code を返す
  private 関数 _emit_payload_and_exit_code

Problems:
    - source_trace_refs と source_document の対応関係が増えるたび、
      手動で「YAML 側の参照」と「docs 側の実体」を突き合わせるのが追いつかない。
    - public 関数に regex 抽出・literal 照合・report 整形を直書きすると、
      入口契約と実装詳細が混ざって読み下しの順序が崩れる。

Solutions:
    - 本 CLI を coverage 集計の入口に固定し、stakeholder_voices.yml と
      source documents の整合を 1 回の呼び出しで判定する。
    - public 関数は「述語呼び出し + private 委譲 + return」のステップ列に
      揃え、複合条件は is_/has_/can_ 述語に切り出して読み下しを揃える。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from . import check_stakeholder_voices


ROOT = Path(__file__).resolve().parents[2]
TRACKED_TRACE_STATUSES = {"active", "later", "wont"}


# === Public API ===

def extract_stable_refs(
    repo_root: Path,
    source_document: dict[str, Any],
) -> tuple[set[str], list[dict[str, Any]]]:
    """1 source_document を読み取り stable_ref 集合と抽出エラーを返す。

    Args:
        repo_root: リポジトリのルート（source_document["path"] の解決基点）。
        source_document: stakeholder_voices.yml の facts.source_documents 要素。
    Returns:
        (抽出した stable_ref の集合, 抽出時に出たエラー dict のリスト)。
    Policy:
        - public 関数はステップ列に揃え、契約検証と抽出を private helper に
          委ねて public 側から制御フローを取り除く。
    """
    validation_error = _validate_extraction_contract(
        repo_root, source_document)
    return _extract_stable_refs_after_validation(
        repo_root, source_document, validation_error)


def build_report(repo_root: Path, rules_path: Path) -> dict[str, Any]:
    """stakeholder_voices.yml と source documents から coverage report を組み立てる。

    Args:
        repo_root: リポジトリのルート。
        rules_path: stakeholder_voices.yml のパス。
    Returns:
        status / summary / documents / errors を含む report dict。
    Policy:
        - public 関数はステップ列に揃え、referenced 集計・document entry 構築・
          summary 構築を private helper に委ねる。
    """
    data = check_stakeholder_voices.load_rules(rules_path)
    referenced_refs, errors = _collect_referenced_refs(data)
    documents, broken_documents, doc_errors = _build_document_entries(
        repo_root, data, referenced_refs)
    errors.extend(doc_errors)
    summary = _build_summary(documents, broken_documents)
    return {
        "status": "BROKEN_TRACEABILITY" if errors else "OK",
        "summary": summary,
        "documents": documents,
        "errors": errors,
    }


def run_report(repo_root: Path, rules_path: Path) -> dict[str, Any]:
    """build_report の薄いブリッジ（CLI と外部呼び出しの共通入口）。

    Args:
        repo_root: リポジトリのルート。
        rules_path: stakeholder_voices.yml のパス。
    Returns:
        build_report と同じ report dict。
    Policy:
        - 既存の公開 API を維持するため、build_report への 1 ステップ委譲のみ。
    """
    return build_report(repo_root, rules_path)


def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """CLI 入口。引数解析と run_report 呼び出しと JSON 出力を束ねる。

    Args:
        argv: コマンドライン引数。None で sys.argv を使う。
    Returns:
        status=="OK" なら 0、それ以外は 1。
    Policy:
        - public 関数はステップ列に揃え、argparse 構築と stdout 出力は
          private helper に委ねる。
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    payload = run_report(ROOT, args.rules_path)
    return _emit_payload_and_exit_code(payload)


# === Internal helpers (private) ===

def _build_error_entry(kind: str, **payload: Any) -> dict[str, Any]:
    """kind と追加 payload を 1 つの error dict に組み立てる。

    Args:
        kind: エラー種別キー。
        **payload: 任意の追加フィールド。
    Returns:
        kind + payload をマージした dict。
    Policy:
        - report["errors"] の形式を 1 か所に閉じ込め、フィールドのブレを防ぐ。
    """
    data = {"kind": kind}
    data.update(payload)
    return data


def _iter_tracked_source_trace_refs(
        data: dict[str, Any]) -> list[dict[str, str]]:
    """追跡対象 status の trace_ref 使用箇所だけを列挙する。

    Args:
        data: load_rules の戻り値。
    Returns:
        section / item_id / trace_ref を持つ dict のリスト。
    Policy:
        - status が active/later/wont 以外は追跡対象外として除外する。
    """
    trace_refs: list[dict[str, str]] = []
    for section_name in ("requests", "requirements", "acceptance"):
        for item in data["facts"][section_name]:
            if item.get("status", "active") not in TRACKED_TRACE_STATUSES:
                continue
            for trace_ref in item.get("source_trace_refs", []):
                trace_refs.append(
                    {
                        "section": section_name,
                        "item_id": item["id"],
                        "trace_ref": trace_ref,
                    }
                )
    return trace_refs


def _collect_referenced_refs(
    data: dict[str, Any],
) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    """追跡対象 trace_ref を doc_id 別 referenced 集合と format エラーに分ける。

    Args:
        data: load_rules の戻り値。
    Returns:
        ({doc_id: stable_ref 集合}, format/unknown_doc_id エラーのリスト)。
    Policy:
        - 1 usage の判定は _classify_usage に切り出し、ここではループと
          結果の積み上げだけを担う。
    """
    source_documents = {
        source_document["id"]: source_document
        for source_document in data["facts"]["source_documents"]
    }
    referenced_refs: dict[str, set[str]] = {}
    errors: list[dict[str, Any]] = []
    for usage in _iter_tracked_source_trace_refs(data):
        doc_id, stable_ref, error = _classify_usage(usage, source_documents)
        if error is not None:
            errors.append(error)
            continue
        referenced_refs.setdefault(doc_id, set()).add(stable_ref)
    return referenced_refs, errors


def _classify_usage(
    usage: dict[str, str],
    source_documents: dict[str, dict[str, Any]],
) -> tuple[str, str, dict[str, Any] | None]:
    """1 usage を解析し (doc_id, stable_ref, error) を返す。

    Args:
        usage: _iter_tracked_source_trace_refs の 1 エントリ。
        source_documents: doc_id → source_document の辞書。
    Returns:
        (doc_id, stable_ref, error)。error が None なら成功。
    Policy:
        - 失敗時の doc_id/stable_ref は空文字を返し、呼び出し側は error の
          None 判定だけで成否を見るようにする。
    """
    trace_ref = usage["trace_ref"]
    if _is_malformed_trace_ref(trace_ref):
        return "", "", _build_error_entry(
            "invalid_trace_ref_format", **usage)
    doc_id, stable_ref = trace_ref.split(":", 1)
    if _is_blank_trace_ref_part(doc_id, stable_ref):
        return "", "", _build_error_entry(
            "invalid_trace_ref_format", **usage)
    if doc_id not in source_documents:
        return "", "", _build_error_entry(
            "unknown_doc_id",
            doc_id=doc_id,
            stable_ref=stable_ref,
            **usage,
        )
    return doc_id, stable_ref, None


def _is_malformed_trace_ref(trace_ref: Any) -> bool:
    """trace_ref が `doc_id:stable_ref` 形式でないかを返す述語。

    Args:
        trace_ref: stakeholder_voices.yml に書かれた trace_ref 値。
    Returns:
        str でない or `:` を含まないなら True。
    Policy:
        - _classify_usage のループ内ガードでのみ使う薄い述語に留める。
    """
    return not isinstance(trace_ref, str) or ":" not in trace_ref


def _is_blank_trace_ref_part(doc_id: str, stable_ref: str) -> bool:
    """split 後の doc_id / stable_ref のどちらかが空かを返す述語。

    Args:
        doc_id: split 後の左側。
        stable_ref: split 後の右側。
    Returns:
        どちらかが空文字なら True。
    Policy:
        - _classify_usage の format 検証で使う薄い述語に留める。
    """
    return not doc_id or not stable_ref


def _has_invalid_extraction_lists(
        regex_patterns: Any, literal_refs: Any) -> bool:
    """extraction の regex / literals がどちらか list 型でないかを返す述語。

    Args:
        regex_patterns: extraction["regex"]（任意の型）。
        literal_refs: extraction["literals"]（任意の型）。
    Returns:
        どちらかが list でなければ True。
    Policy:
        - _check_extraction_contract の早期 return ガードに留める。
    """
    return not isinstance(regex_patterns, list) or not isinstance(
        literal_refs, list)


def _has_no_extraction_target(
        regex_patterns: list[Any], literal_refs: list[Any]) -> bool:
    """regex / literals のどちらにも要素が無いかを返す述語。

    Args:
        regex_patterns: extraction["regex"]。
        literal_refs: extraction["literals"]。
    Returns:
        どちらも空なら True。
    Policy:
        - _check_extraction_contract の早期 return ガードに留める。
    """
    return not regex_patterns and not literal_refs


def _is_empty_regex_pattern(pattern: Any) -> bool:
    """regex pattern が文字列でないか空白だけかを返す述語。

    Args:
        pattern: extraction["regex"] の 1 要素。
    Returns:
        str でない or strip 後が空なら True。
    Policy:
        - _process_regex_pattern のループガードに留める。
    """
    return not isinstance(pattern, str) or not pattern.strip()


def _is_empty_literal_ref(literal: Any) -> bool:
    """literal ref が文字列でないか空白だけかを返す述語。

    Args:
        literal: extraction["literals"] の 1 要素。
    Returns:
        str でない or strip 後が空なら True。
    Policy:
        - _process_literal_ref のループガードに留める。
    """
    return not isinstance(literal, str) or not literal.strip()


def _validate_extraction_contract(
    repo_root: Path,
    source_document: dict[str, Any],
) -> dict[str, Any] | None:
    """doc_path 存在と extraction 契約を 2 段で検証する。

    Args:
        repo_root: リポジトリのルート。
        source_document: stakeholder_voices.yml の source_documents 要素。
    Returns:
        最初に見つけた違反を表す error dict。違反が無ければ None。
    Policy:
        - doc_path 存在チェックと extraction 契約チェックを 2 つの helper に
          委ね、最初に見つけた 1 件を返す。
    """
    path_error = _check_doc_path_exists(repo_root, source_document)
    if path_error is not None:
        return path_error
    return _check_extraction_contract(source_document)


def _check_doc_path_exists(
    repo_root: Path,
    source_document: dict[str, Any],
) -> dict[str, Any] | None:
    """doc_path が存在しなければ missing_source_document_path エラーを返す。

    Args:
        repo_root: リポジトリのルート。
        source_document: stakeholder_voices.yml の source_documents 要素。
    Returns:
        存在しなければ error dict、存在すれば None。
    Policy:
        - extract_stable_refs の早期 return 用に違反 1 件だけ返す。
    """
    doc_path = repo_root / source_document["path"]
    if not doc_path.exists():
        return _build_error_entry(
            "missing_source_document_path",
            doc_id=source_document["id"],
            path=source_document["path"],
        )
    return None


def _check_extraction_contract(
    source_document: dict[str, Any],
) -> dict[str, Any] | None:
    """extraction が dict か / regex・literals が list か / 1 件以上あるかを判定。

    Args:
        source_document: stakeholder_voices.yml の source_documents 要素。
    Returns:
        違反 1 件分の error dict、契約 OK なら None。
    Policy:
        - 違反は invalid_extraction_contract に統一し、reason 文だけ変える。
    """
    extraction = source_document.get("extraction")
    if not isinstance(extraction, dict):
        return _make_invalid_extraction_error(
            source_document, "missing extraction dict")
    regex_patterns = extraction.get("regex", [])
    literal_refs = extraction.get("literals", [])
    if _has_invalid_extraction_lists(regex_patterns, literal_refs):
        return _make_invalid_extraction_error(
            source_document, "regex and literals must be lists")
    if _has_no_extraction_target(regex_patterns, literal_refs):
        return _make_invalid_extraction_error(
            source_document, "at least one regex or literal is required")
    return None


def _make_invalid_extraction_error(
    source_document: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    """invalid_extraction_contract の error dict を組み立てる。

    Args:
        source_document: stakeholder_voices.yml の source_documents 要素。
        reason: 違反理由の説明文。
    Returns:
        kind=invalid_extraction_contract の error dict。
    Policy:
        - _check_extraction_contract から繰り返しの dict 組み立てを抜き、
          reason だけ差し替える 1 行 helper にする。
    """
    return _build_error_entry(
        "invalid_extraction_contract",
        doc_id=source_document["id"],
        path=source_document["path"],
        reason=reason,
    )


def _extract_stable_refs_after_validation(
    repo_root: Path,
    source_document: dict[str, Any],
    validation_error: dict[str, Any] | None,
) -> tuple[set[str], list[dict[str, Any]]]:
    """契約検証の結果を踏まえて本文読み込みと regex/literal 抽出を走らせる。

    Args:
        repo_root: リポジトリのルート。
        source_document: stakeholder_voices.yml の source_documents 要素。
        validation_error: _validate_extraction_contract の戻り値。
    Returns:
        (抽出した ref 集合, エラー dict のリスト)。
    Policy:
        - validation_error があれば早期 return、無ければ _extract_refs_from_text
          に委ねて未抽出ガードだけ最後に足す。
    """
    if validation_error is not None:
        return set(), [validation_error]
    text = (repo_root / source_document["path"]).read_text(encoding="utf-8")
    extracted_refs, errors = _extract_refs_from_text(text, source_document)
    if not extracted_refs:
        errors.append(_build_error_entry(
            "no_refs_extracted",
            doc_id=source_document["id"],
            path=source_document["path"],
        ))
    return extracted_refs, errors


def _extract_refs_from_text(
    text: str,
    source_document: dict[str, Any],
) -> tuple[set[str], list[dict[str, Any]]]:
    """本文に対して regex/literals 抽出を走らせて (refs, errors) を返す。

    Args:
        text: source document の本文。
        source_document: stakeholder_voices.yml の source_documents 要素。
    Returns:
        (regex/literals から取れた ref 集合の合流, 抽出時エラーの結合)。
    Policy:
        - regex 結果と literal 結果のマージを 1 か所に閉じ込め、
          _extract_stable_refs_after_validation を短く保つ。
    """
    extraction = source_document["extraction"]
    regex_refs, regex_errors = _extract_refs_by_regex(
        text, extraction.get("regex", []), source_document)
    literal_refs, literal_errors = _extract_refs_by_literals(
        text, extraction.get("literals", []), source_document)
    return regex_refs | literal_refs, regex_errors + literal_errors


def _extract_refs_by_regex(
    text: str,
    regex_patterns: list[Any],
    source_document: dict[str, Any],
) -> tuple[set[str], list[dict[str, Any]]]:
    """regex pattern 群から stable_ref 集合と pattern エラーを返す。

    Args:
        text: source document の本文。
        regex_patterns: extraction["regex"]。
        source_document: エラー出力で doc_id/path を使う。
    Returns:
        (抽出した ref 集合, 不正 pattern のエラーのリスト)。
    Policy:
        - 1 pattern の処理は _process_regex_pattern に委ね、ここでは
          集合の合流とエラーの積み上げだけを行う。
    """
    extracted_refs: set[str] = set()
    errors: list[dict[str, Any]] = []
    for pattern in regex_patterns:
        refs, error = _process_regex_pattern(pattern, text, source_document)
        extracted_refs.update(refs)
        if error is not None:
            errors.append(error)
    return extracted_refs, errors


def _process_regex_pattern(
    pattern: Any,
    text: str,
    source_document: dict[str, Any],
) -> tuple[set[str], dict[str, Any] | None]:
    """1 regex pattern を処理し (matched ref 集合, error or None) を返す。

    Args:
        pattern: extraction["regex"] の 1 要素。
        text: source document の本文。
        source_document: エラー出力で doc_id/path を使う。
    Returns:
        (本文中で match した文字列の集合, 不正なら error、正常なら None)。
    Policy:
        - 空 pattern と compile 失敗は invalid_regex_pattern にまとめる。
    """
    if _is_empty_regex_pattern(pattern):
        return set(), _make_invalid_regex_error(
            source_document, pattern, reason=None)
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        return set(), _make_invalid_regex_error(
            source_document, pattern, reason=str(exc))
    return {match.group(0) for match in compiled.finditer(text)}, None


def _make_invalid_regex_error(
    source_document: dict[str, Any],
    pattern: Any,
    *,
    reason: str | None,
) -> dict[str, Any]:
    """invalid_regex_pattern の error dict を組み立てる。

    Args:
        source_document: stakeholder_voices.yml の source_documents 要素。
        pattern: 違反 pattern の生値。
        reason: re.error 由来の説明文（空 pattern では None で省略）。
    Returns:
        kind=invalid_regex_pattern の error dict。
    Policy:
        - 空 pattern と compile 失敗の両ルートで同一 kind のエラーに揃え、
          reason の有無だけで差をつける。
    """
    payload: dict[str, Any] = {
        "doc_id": source_document["id"],
        "path": source_document["path"],
        "pattern": pattern,
    }
    if reason is not None:
        payload["reason"] = reason
    return _build_error_entry("invalid_regex_pattern", **payload)


def _extract_refs_by_literals(
    text: str,
    literal_refs: list[Any],
    source_document: dict[str, Any],
) -> tuple[set[str], list[dict[str, Any]]]:
    """literal 群から stable_ref 集合と literal エラーを返す。

    Args:
        text: source document の本文。
        literal_refs: extraction["literals"]。
        source_document: エラー出力で doc_id/path を使う。
    Returns:
        (抽出した ref 集合, 不正 / 未出現 literal のエラーのリスト)。
    Policy:
        - 1 literal の処理は _process_literal_ref に委ね、ここでは
          集合の合流とエラーの積み上げだけを行う。
    """
    extracted_refs: set[str] = set()
    errors: list[dict[str, Any]] = []
    for literal in literal_refs:
        ref, error = _process_literal_ref(literal, text, source_document)
        if ref is not None:
            extracted_refs.add(ref)
        if error is not None:
            errors.append(error)
    return extracted_refs, errors


def _process_literal_ref(
    literal: Any,
    text: str,
    source_document: dict[str, Any],
) -> tuple[str | None, dict[str, Any] | None]:
    """1 literal を処理し (ref or None, error or None) を返す。

    Args:
        literal: extraction["literals"] の 1 要素。
        text: source document の本文。
        source_document: エラー出力で doc_id/path を使う。
    Returns:
        (取り込む ref or None, 不正なら error or None)。
    Policy:
        - 空 literal は invalid_literal_ref、本文に無ければ
          missing_literal_in_source_document として分類する。
    """
    doc_id = source_document["id"]
    path = source_document["path"]
    if _is_empty_literal_ref(literal):
        return None, _build_error_entry(
            "invalid_literal_ref",
            doc_id=doc_id, path=path, literal=literal,
        )
    if literal not in text:
        return None, _build_error_entry(
            "missing_literal_in_source_document",
            doc_id=doc_id, path=path, literal=literal,
        )
    return literal, None


def _build_document_entries(
    repo_root: Path,
    data: dict[str, Any],
    referenced_refs: dict[str, set[str]],
) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]]]:
    """全 source_document の entry / broken 件数 / 追加エラーを返す。

    Args:
        repo_root: リポジトリのルート。
        data: load_rules の戻り値。
        referenced_refs: doc_id 別の referenced 集合。
    Returns:
        (documents, broken_documents, 追加エラー)。
    Policy:
        - build_report からループを引き取り、entry 構築を _build_document_entry
          に委ねて 1 source あたりの判断を 1 か所に集める。
    """
    documents: list[dict[str, Any]] = []
    extra_errors: list[dict[str, Any]] = []
    broken_documents = 0
    for source_document in data["facts"]["source_documents"]:
        entry, doc_errors = _build_document_entry(
            repo_root, source_document, referenced_refs)
        documents.append(entry)
        if doc_errors:
            broken_documents += 1
            extra_errors.extend(doc_errors)
    return documents, broken_documents, extra_errors


def _build_document_entry(
    repo_root: Path,
    source_document: dict[str, Any],
    referenced_refs: dict[str, set[str]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """1 source_document の entry dict とその source 由来のエラーを返す。

    Args:
        repo_root: リポジトリのルート。
        source_document: stakeholder_voices.yml の source_documents 要素。
        referenced_refs: doc_id 別の referenced 集合。
    Returns:
        (document entry dict, この source のエラー dict のリスト)。
    Policy:
        - 抽出・差分計算・エラー追加・entry 整形は private helper に委ね、
          ここはステップ列だけにする。
    """
    extracted_refs, doc_errors, refs = _compute_doc_artifacts(
        repo_root, source_document, referenced_refs)
    entry = _format_document_entry(
        source_document=source_document,
        extracted_refs=extracted_refs,
        referenced=refs[0],
        missing_refs=refs[1],
        unexpected_referenced=refs[2],
        has_errors=bool(doc_errors),
    )
    return entry, doc_errors


def _compute_doc_artifacts(
    repo_root: Path,
    source_document: dict[str, Any],
    referenced_refs: dict[str, set[str]],
) -> tuple[
    set[str],
    list[dict[str, Any]],
    tuple[list[str], list[str], list[str]],
]:
    """1 source_document から extracted / errors / 差分 3 種を返す。

    Args:
        repo_root: リポジトリのルート。
        source_document: stakeholder_voices.yml の source_documents 要素。
        referenced_refs: doc_id 別の referenced 集合。
    Returns:
        (extracted_refs, doc_errors,
        (referenced, missing_refs, unexpected_referenced))。
    Policy:
        - 抽出と差分計算と unexpected エラー追加を 1 か所にまとめ、
          _build_document_entry を entry 整形のステップ列に絞らせる。
    """
    extracted_refs, extraction_errors = extract_stable_refs(
        repo_root, source_document)
    referenced = sorted(referenced_refs.get(source_document["id"], set()))
    missing_refs, unexpected_referenced = _compute_ref_diffs(
        extracted_refs, referenced)
    doc_errors = _append_unexpected_referenced_error(
        list(extraction_errors), source_document, unexpected_referenced)
    return extracted_refs, doc_errors, (
        referenced, missing_refs, unexpected_referenced)


def _append_unexpected_referenced_error(
    doc_errors: list[dict[str, Any]],
    source_document: dict[str, Any],
    unexpected_referenced: list[str],
) -> list[dict[str, Any]]:
    """unexpected_referenced があれば referenced_ref_missing… エラーを足して返す。

    Args:
        doc_errors: これまでに溜まったエラーリスト（書き換えて返す）。
        source_document: stakeholder_voices.yml の source_documents 要素。
        unexpected_referenced: extracted に含まれない referenced ref。
    Returns:
        unexpected_referenced が空でなければ 1 件追加後の doc_errors、
        空なら引数そのままの doc_errors。
    Policy:
        - エラーの種類と payload を 1 か所に閉じ込め、build 側を細く保つ。
    """
    if unexpected_referenced:
        doc_errors.append(_build_error_entry(
            "referenced_ref_missing_from_source_document",
            doc_id=source_document["id"],
            path=source_document["path"],
            refs=unexpected_referenced,
        ))
    return doc_errors


def _format_document_entry(
    *,
    source_document: dict[str, Any],
    extracted_refs: set[str],
    referenced: list[str],
    missing_refs: list[str],
    unexpected_referenced: list[str],
    has_errors: bool,
) -> dict[str, Any]:
    """document entry dict をフィールド順に組み立てて返す。

    Args:
        source_document: stakeholder_voices.yml の source_documents 要素。
        extracted_refs: 抽出した ref 集合。
        referenced: 参照済み ref のソート済みリスト。
        missing_refs: 未参照の ref。
        unexpected_referenced: 抽出に無い referenced。
        has_errors: status を broken/ok に分けるフラグ。
    Returns:
        report["documents"] の 1 要素になる dict。
    Policy:
        - キー名と並びを report 出力と同一に保ち、フォーマットを変えない。
    """
    return {
        "doc_id": source_document["id"],
        "path": source_document["path"],
        "status": "broken" if has_errors else "ok",
        "total_refs": len(extracted_refs),
        "extracted_refs": sorted(extracted_refs),
        "referenced_refs": referenced,
        "missing_refs": missing_refs,
        "unexpected_referenced_refs": unexpected_referenced,
    }


def _compute_ref_diffs(
    extracted_refs: set[str],
    referenced: list[str],
) -> tuple[list[str], list[str]]:
    """extracted と referenced から (missing, unexpected) の差分リストを返す。

    Args:
        extracted_refs: source document から抽出した ref 集合。
        referenced: YAML 側で参照されている ref のソート済みリスト。
    Returns:
        (missing_refs, unexpected_referenced_refs) のソート済みタプル。
    Policy:
        - 差分計算を 1 か所に閉じ込め、_build_document_entry の責務を
          entry 整形だけに保つ。
    """
    referenced_set = set(referenced)
    missing_refs = sorted(
        ref for ref in extracted_refs if ref not in referenced_set)
    unexpected_referenced = sorted(
        ref for ref in referenced if ref not in extracted_refs)
    return missing_refs, unexpected_referenced


def _build_summary(
    documents: list[dict[str, Any]],
    broken_documents: int,
) -> dict[str, Any]:
    """documents 集計から summary dict を組み立てる。

    Args:
        documents: _build_document_entries の entry リスト。
        broken_documents: status=="broken" の件数。
    Returns:
        report["summary"] になる dict。
    Policy:
        - キー名 / 集計式を report 出力と同一に保ち、フォーマットを変えない。
    """
    return {
        "total_documents": len(documents),
        "broken_documents": broken_documents,
        "total_extracted_refs": sum(
            document["total_refs"] for document in documents),
        "total_referenced_refs": sum(
            len(document["referenced_refs"]) for document in documents),
        "total_missing_refs": sum(
            len(document["missing_refs"]) for document in documents),
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    """main 用の argparse parser を組み立てて返す。

    Returns:
        --rules-path だけを受ける ArgumentParser。
    Policy:
        - parser 構築を 1 か所に閉じ込め、main をステップ列に保つ。
    """
    parser = argparse.ArgumentParser(
        description="stakeholder voices source-trace coverage")
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=ROOT / "docs" / "stakeholder_voices.yml",
    )
    return parser


def _emit_payload_and_exit_code(payload: dict[str, Any]) -> int:
    """payload を stdout に書き出して exit code を返す。

    Args:
        payload: run_report の戻り値。
    Returns:
        status=="OK" なら 0、それ以外は 1。
    Policy:
        - 表示と exit code を 1 か所に閉じ込め、CLI 入口の本体を細く保つ。
    """
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
