"""stakeholder voice rule を check -> fix -> recheck で収束させる repair CLI。

このファイルに含まれる関数・クラス：

- check -> fix -> recheck ループを束ねる public 関数 run_repair
- CLI 入口の public 関数 main（引数解析と JSON 出力と exit code 制御）
- 1 回目の checker を実行して履歴の初期値を返す内部関数 _run_initial_check
- 初期 check を見て早期 return か fix ループに分岐する内部関数 _run_repair_after_initial_check
- check 結果が warning 無しかを判定する述語関数 _is_clean_check
- warnings が無い初期 check 用の OK payload を組み立てる内部関数 _build_initial_ok_payload
- max_cycles まで fix -> recheck を繰り返して history を返す内部関数 _run_fix_cycles
- fix_result を history 1 エントリ分に整形する内部関数 _build_history_entry
- 最終 check 結果から status を決める内部関数 _decide_final_status
- ループ終了後の最終 check と最終 payload を組み立てる内部関数 _build_final_payload
- argparse を構成して Namespace を返す内部関数 _build_arg_parser
- Namespace から run_repair 引数を組み立てて payload を得る内部関数 _run_main_with_args
- payload を stdout に出力して exit code を返す内部関数 _emit_payload_and_exit_code

Problems:
    - check と fix と再 check を別々に呼ぶと、運用側で順序を間違えやすく、
      result code (`OK` / `AUTOFIXED` / `NEEDS_HUMAN`) も統一しにくい。
    - 1 つの public 関数にループ・分岐・履歴整形を直書きすると、入口契約と
      実装詳細が混ざって読み手の判断がブレる。

Solutions:
    - 本 CLI を orchestration の入口に固定し、check / fix / recheck を
      1 回の呼び出しで束ねる。
    - public 関数は「述語呼び出し + private 委譲 + return」のステップ列に揃え、
      ループ・履歴整形・status 決定は private helper に切り出す。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import check_stakeholder_voices, fix_stakeholder_voices


ROOT = Path(__file__).resolve().parents[2]


# === Public API ===

def run_repair(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
    max_cycles: int = 5,
) -> dict:
    """stakeholder voice rule を check -> fix -> recheck で収束させる。

    Args:
        repo_root: リポジトリのルート。
        rules_path: 検査対象 YAML のパス。
        rule_ids: 限定実行する rule id 集合（None で全件）。
        max_cycles: fix -> recheck の最大反復回数。
    Returns:
        status / cycles / history / final_check を含む payload。
    Policy:
        - public 関数は「述語呼び出し + private 委譲 + return」のステップ列に
          揃え、初期 OK の早期 return と最終 payload 組み立てを private に委ねる。
    """
    initial_check = _run_initial_check(repo_root, rules_path, rule_ids)
    return _run_repair_after_initial_check(
        repo_root, rules_path, rule_ids, max_cycles, initial_check)


def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """CLI 入口。引数解析と run_repair 呼び出しと JSON 出力を束ねる。

    Args:
        argv: コマンドライン引数。None で sys.argv を使う。
    Returns:
        OK / AUTOFIXED は 0、それ以外は 1。
    Policy:
        - public 関数はステップ列に揃え、引数解析と payload 算出と
          stdout 出力は private helper に委ねる。
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    payload = _run_main_with_args(args)
    return _emit_payload_and_exit_code(payload)


# === Internal helpers (private) ===

def _run_initial_check(
    repo_root: Path,
    rules_path: Path,
    rule_ids: set[str] | None,
) -> dict[str, Any]:
    """check_stakeholder_voices を 1 回実行して結果を返す。

    Args:
        repo_root: リポジトリのルート。
        rules_path: 検査対象 YAML のパス。
        rule_ids: 限定実行する rule id 集合。
    Returns:
        run_checker の戻り値。
    Policy:
        - 初期チェックと最終チェックで共有する薄いブリッジに留める。
    """
    return check_stakeholder_voices.run_checker(
        repo_root, rules_path, rule_ids=rule_ids)


def _run_repair_after_initial_check(
    repo_root: Path,
    rules_path: Path,
    rule_ids: set[str] | None,
    max_cycles: int,
    initial_check: dict[str, Any],
) -> dict[str, Any]:
    """初期 check の結果を踏まえて OK 早期 return または fix ループへ分岐する。

    Args:
        repo_root: リポジトリのルート。
        rules_path: 検査対象 YAML のパス。
        rule_ids: 限定実行する rule id 集合。
        max_cycles: fix ループの上限。
        initial_check: 1 回目の run_checker 結果。
    Returns:
        OK / AUTOFIXED / NEEDS_HUMAN のいずれかの payload。
    Policy:
        - 制御フローを public 関数から引き取り、初期 OK 用と fix ループ用の
          private helper に委ねる。
    """
    if _is_clean_check(initial_check):
        return _build_initial_ok_payload(initial_check)
    history, last_check = _run_fix_cycles(
        repo_root, rules_path, rule_ids, max_cycles, initial_check)
    return _build_final_payload(
        repo_root, rules_path, rule_ids, history, last_check)


def _is_clean_check(check: dict[str, Any]) -> bool:
    """check の warning 有無を反転して clean 判定を返す述語。

    Args:
        check: run_checker の戻り値。
    Returns:
        warning が 0 件なら True。
    Policy:
        - run_repair の早期 return ガードでのみ使う薄い述語に留める。
    """
    return not check["has_warnings"]


def _build_initial_ok_payload(initial_check: dict[str, Any]) -> dict[str, Any]:
    """初期 check に warning が無い場合の OK payload を返す。

    Args:
        initial_check: run_checker の戻り値。
    Returns:
        status="OK" の payload。
    Policy:
        - history を 1 エントリだけ持たせ、後段 history との形式を揃える。
    """
    history = [
        {"cycle": 1, "check": initial_check, "applied_fixes": []},
    ]
    return {
        "status": "OK",
        "cycles": 1,
        "history": history,
        "final_check": initial_check,
    }


def _run_fix_cycles(
    repo_root: Path,
    rules_path: Path,
    rule_ids: set[str] | None,
    max_cycles: int,
    initial_check: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """fix -> recheck を max_cycles まで繰り返す。

    Args:
        repo_root: リポジトリのルート。
        rules_path: 検査対象 YAML のパス。
        rule_ids: 限定実行する rule id 集合。
        max_cycles: 反復の上限。
        initial_check: 初期 check 結果（warning ありが前提）。
    Returns:
        (history, 最終 post_check)。
    Policy:
        - fix が空の cycle で早期離脱し、上限到達でも履歴を保持する。
    """
    history: list[dict[str, Any]] = []
    check = initial_check
    cycle = 0
    while cycle < max_cycles and check["has_warnings"]:
        cycle += 1
        fix_result = fix_stakeholder_voices.run_fixer(
            repo_root, rules_path, rule_ids=rule_ids)
        history.append(_build_history_entry(cycle, fix_result))
        check = fix_result["post_check"]
        if not fix_result["applied_fixes"]:
            break
    return history, check


def _build_history_entry(
    cycle: int,
    fix_result: dict[str, Any],
) -> dict[str, Any]:
    """fix_result を 1 cycle 分の history エントリに整形する。

    Args:
        cycle: 反復番号。
        fix_result: run_fixer の戻り値。
    Returns:
        history に積む dict。
    Policy:
        - フィールド名と並びを既存呼び出し元の期待値に合わせる。
    """
    return {
        "cycle": cycle,
        "check": fix_result["check"],
        "applied_fixes": fix_result["applied_fixes"],
        "post_check": fix_result["post_check"],
        "fix_status": fix_result["status"],
    }


def _decide_final_status(final_check: dict[str, Any]) -> str:
    """最終 check の warning 有無で status を決める。

    Args:
        final_check: 最終 run_checker の戻り値。
    Returns:
        "AUTOFIXED" または "NEEDS_HUMAN"。
    Policy:
        - 初期 OK は呼び出し元で別 payload に分けるため、ここでは扱わない。
    """
    if not final_check["has_warnings"]:
        return "AUTOFIXED"
    return "NEEDS_HUMAN"


def _build_final_payload(
    repo_root: Path,
    rules_path: Path,
    rule_ids: set[str] | None,
    history: list[dict[str, Any]],
    last_check: dict[str, Any],
) -> dict[str, Any]:
    """ループ後の最終 check を実行して payload を組み立てる。

    Args:
        repo_root: リポジトリのルート。
        rules_path: 検査対象 YAML のパス。
        rule_ids: 限定実行する rule id 集合。
        history: 累積 history。
        last_check: ループ最後の post_check（互換のため受け取るが未使用）。
    Returns:
        status / cycles / history / final_check を含む payload。
    Policy:
        - cycles は最低 1 を保証し、最終 check は再実行して確定させる。
    """
    del last_check
    final_check = _run_initial_check(repo_root, rules_path, rule_ids)
    status = _decide_final_status(final_check)
    cycles = max(len(history), 1)
    return {
        "status": status,
        "cycles": cycles,
        "history": history,
        "final_check": final_check,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    """main 用の argparse を構成して返す。

    Returns:
        --rules-path / --rule-id / --max-cycles を持つ parser。
    Policy:
        - default は ROOT/docs/stakeholder_voices.yml に固定する。
    """
    parser = argparse.ArgumentParser(
        description="stakeholder voices repair loop")
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=ROOT / "docs" / "stakeholder_voices.yml",
    )
    parser.add_argument("--rule-id", action="append", default=None)
    parser.add_argument("--max-cycles", type=int, default=5)
    return parser


def _run_main_with_args(args: argparse.Namespace) -> dict[str, Any]:
    """argparse Namespace から run_repair を呼び出して payload を返す。

    Args:
        args: parser.parse_args の戻り値。
    Returns:
        run_repair の戻り値。
    Policy:
        - rule_id は list でも未指定でも set | None に正規化する。
    """
    rule_ids = set(args.rule_id) if args.rule_id else None
    return run_repair(
        ROOT,
        args.rules_path,
        rule_ids=rule_ids,
        max_cycles=args.max_cycles,
    )


def _emit_payload_and_exit_code(payload: dict[str, Any]) -> int:
    """payload を stdout に JSON 出力し exit code を返す。

    Args:
        payload: run_repair の戻り値。
    Returns:
        status が OK / AUTOFIXED なら 0、それ以外は 1。
    Policy:
        - 終了コードの判定は status 集合との照合のみで行う。
    """
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if payload["status"] in {"OK", "AUTOFIXED"}:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
