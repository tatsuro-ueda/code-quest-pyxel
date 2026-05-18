"""architecture rule を check -> fix -> recheck で収束させる repair CLI。

このファイルに含まれる関数・クラス：

- run_repair：rules を最大 N 回まで check->fix->recheck し result dict を返す入口
- run_main：CLI 入口（argv を受けて run_repair を呼び、JSON を stdout に出す）
- _run_repair：repair ループ本体の外殻（try/except のみを担う）
- _run_repair_loop：cycle 走査を担い、上限到達時は _finalize_after_cycles へ委譲
- _finalize_after_cycles：上限到達後の最終 check を 1 回実行して戻り値を組む
- _run_one_cycle：1 サイクルの check -> fix を実行し、早期終了 dict か None を返す
- _apply_fix_step：fixer を呼び、結果に応じて早期終了 dict か None を返す
- _build_clean_payload：1 サイクル目で warnings が無いときの戻り値を組む純粋関数
- _build_error_payload：fixer が ERROR を返したときの戻り値を組む純粋関数
- _build_needs_human_payload：fixer が FIXED 以外を返したときの戻り値を組む純粋関数
- _build_final_payload：上限回数到達後の最終 check を踏まえた戻り値を組む純粋関数
- _build_exception_payload：try ループ全体で例外が出たときの戻り値を組む純粋関数
- _extend_applied_fixes：fixer 戻り値の applied_fixes に cycle 番号を畳み込むヘルパ
- _run_main：CLI 本体（parser 構築・run_repair 呼び出し・JSON 出力・exit code 算出）
- _build_arg_parser：argparse.ArgumentParser を組み立てる純粋関数

Problems:
    - check と fix と再 check を別々に呼ぶと、収束判定や result code
      （`OK` / `AUTOFIXED` / `NEEDS_HUMAN` / `ERROR`）の決め方が呼び出し側に
      漏れて、運用ごとに微妙に違う挙動になりやすい。
    - public 関数 1 個に try/for/早期 return を全部詰めると、テストで
      条件分岐を網羅しづらく、AI 補助のリファクタ判断もブレる。

Solutions:
    - 入口 `run_repair` を「述語呼び出し + private 委譲 + return」のステップ列に
      固定し、ループ本体・各分岐の戻り値組み立て・例外捕捉を private helper に分ける。
    - CLI 入口 `run_main` も同じ形に揃え、parser 構築と本体処理を分離する。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import check_architecture_rules, fix_architecture_rules


ROOT = Path(__file__).resolve().parents[2]


# === Public API ===


def run_repair(
    repo_root: Path,
    rules_path: Path,
    *,
    max_cycles: int = 5,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    """architecture rule を最大 N 回まで check -> fix -> recheck で収束させる。

    Args:
        repo_root: リポジトリのルート Path。
        rules_path: architecture rules YAML の Path。
        max_cycles: 1 回の repair で許容する最大サイクル数。
        rule_ids: 対象 rule の絞り込み集合（None なら全 rule）。

    Returns:
        dict: status / cycles / history / applied_fixes / final_check
        （または error）。

    Policy:
        - 本体はステップ列のみとし、ループ本体は private helper に委譲する。
    """
    return _run_repair(
        repo_root.resolve(),
        rules_path.resolve(),
        max_cycles=max_cycles,
        rule_ids=rule_ids,
    )


def run_main(argv: list[str] | None = None) -> int:
    """CLI 入口。argv を解釈して run_repair を呼び、結果 JSON を stdout に出す。

    Args:
        argv: コマンドライン引数。None なら sys.argv[1:] を使う。

    Returns:
        int: status が OK / AUTOFIXED なら 0、それ以外は 1。

    Policy:
        - 本体はステップ列のみとし、引数解析や I/O は private helper に委譲する。
    """
    return _run_main(argv)


# 既存 shim (tools/repair_architecture_rules.py) が `main` をインポートしている
# ため後方互換のためのエイリアスを残す。
main = run_main


# === Internal helpers (private) ===


def _run_repair(
    repo_root: Path,
    rules_path: Path,
    *,
    max_cycles: int,
    rule_ids: set[str] | None,
) -> dict[str, Any]:
    """repair ループ本体（try/except の外殻）。

    Args:
        repo_root: 解決済みのリポジトリルート。
        rules_path: 解決済みの rules YAML パス。
        max_cycles: 最大サイクル数。
        rule_ids: 対象 rule 絞り込み（None なら全 rule）。

    Returns:
        dict: run_repair の戻り値と同形式。

    Policy:
        - try/except だけここに残し、ループ本体は _run_repair_loop に委譲する。
    """
    history: list[dict[str, Any]] = []
    applied_fixes: list[dict[str, Any]] = []
    try:
        return _run_repair_loop(
            repo_root, rules_path,
            max_cycles=max_cycles, rule_ids=rule_ids,
            history=history, applied_fixes=applied_fixes,
        )
    except Exception as exc:
        return _build_exception_payload(history, applied_fixes, exc)


def _run_repair_loop(
    repo_root: Path, rules_path: Path, *,
    max_cycles: int, rule_ids: set[str] | None,
    history: list[dict[str, Any]], applied_fixes: list[dict[str, Any]],
) -> dict[str, Any]:
    """cycle 走査と上限到達後の最終 check を担う。

    Args:
        repo_root: 解決済みのリポジトリルート。
        rules_path: 解決済みの rules YAML パス。
        max_cycles: 最大サイクル数。
        rule_ids: 対象 rule 絞り込み（None なら全 rule）。
        history: in-place で積み上げる check 履歴。
        applied_fixes: in-place で積み上げる fix 履歴。

    Returns:
        dict: 早期終了したサイクルの戻り値、または上限到達時の最終戻り値。

    Policy:
        - 1 サイクルの early-return 判定は _run_one_cycle が dict | None で返す。
        - 上限到達後の最終 check は _finalize_after_cycles に委譲する。
    """
    has_autofix = False
    for cycle in range(1, max_cycles + 1):
        outcome = _run_one_cycle(
            repo_root, rules_path,
            rule_ids=rule_ids, cycle=cycle,
            history=history, applied_fixes=applied_fixes,
            has_autofix=has_autofix)
        if outcome is not None:
            return outcome
        has_autofix = True
    return _finalize_after_cycles(
        repo_root, rules_path,
        rule_ids=rule_ids, max_cycles=max_cycles,
        history=history, applied_fixes=applied_fixes,
        has_autofix=has_autofix)


def _finalize_after_cycles(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None,
    max_cycles: int,
    history: list[dict[str, Any]],
    applied_fixes: list[dict[str, Any]],
    has_autofix: bool,
) -> dict[str, Any]:
    """上限回数到達後に最終 check を実行し、戻り値を組む。

    Args:
        repo_root: 解決済みのリポジトリルート。
        rules_path: 解決済みの rules YAML パス。
        rule_ids: 対象 rule 絞り込み（None なら全 rule）。
        max_cycles: 最大サイクル数。
        history: in-place で積み上げる check 履歴。
        applied_fixes: in-place で積み上げる fix 履歴。
        has_autofix: ループ中に 1 回でも fix を適用したか。

    Returns:
        dict: 上限到達後の AUTOFIXED / NEEDS_HUMAN 戻り値。

    Policy:
        - 直り切ったのか未収束なのかを最終 check 1 回で確定させる。
    """
    final_check = check_architecture_rules.run_checker(
        repo_root, rules_path, rule_ids=rule_ids)
    history.append({"cycle": max_cycles + 1, "check": final_check})
    return _build_final_payload(
        max_cycles, history, applied_fixes, final_check,
        has_autofix=has_autofix,
    )


def _run_one_cycle(
    repo_root: Path, rules_path: Path, *,
    rule_ids: set[str] | None, cycle: int,
    history: list[dict[str, Any]], applied_fixes: list[dict[str, Any]],
    has_autofix: bool,
) -> dict[str, Any] | None:
    """1 サイクルの check -> fix を実行し、早期終了する場合は戻り値 dict を返す。

    Args:
        repo_root: 解決済みのリポジトリルート。
        rules_path: 解決済みの rules YAML パス。
        rule_ids: 対象 rule 絞り込み（None なら全 rule）。
        cycle: そのサイクル番号。
        history: in-place で積み上げる check 履歴。
        applied_fixes: in-place で積み上げる fix 履歴。
        has_autofix: これまでに 1 回でも fix を適用したか。

    Returns:
        dict | None: 早期終了する場合はその戻り値、次サイクルへ進む場合は None。

    Policy:
        - check は history に積んでから clean 判定を行い、その後の fix 分岐は
          _apply_fix_step に委譲する。
    """
    # 毎サイクルの最初に checker の生結果を history へ積み、
    # 「何を見てどこで止まったか」を後から追えるようにする。
    check = check_architecture_rules.run_checker(
        repo_root, rules_path, rule_ids=rule_ids)
    history.append({"cycle": cycle, "check": check})
    if not check["has_warnings"]:
        return _build_clean_payload(
            cycle, history, applied_fixes, check, has_autofix=has_autofix)
    return _apply_fix_step(
        repo_root, rules_path,
        rule_ids=rule_ids, cycle=cycle, check=check,
        history=history, applied_fixes=applied_fixes)


def _apply_fix_step(
    repo_root: Path, rules_path: Path, *,
    rule_ids: set[str] | None, cycle: int, check: dict[str, Any],
    history: list[dict[str, Any]], applied_fixes: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """fixer を呼び、結果に応じて早期終了 dict か None を返す。

    Args:
        repo_root: 解決済みのリポジトリルート。
        rules_path: 解決済みの rules YAML パス。
        rule_ids: 対象 rule 絞り込み（None なら全 rule）。
        cycle: そのサイクル番号。
        check: 直近の checker 結果（NEEDS_HUMAN ペイロードで使う）。
        history: in-place で積み上げる check 履歴。
        applied_fixes: in-place で積み上げる fix 履歴。

    Returns:
        dict | None: 早期終了 dict、または次サイクルへ進む None。

    Policy:
        - fixer が ERROR / FIXED 以外なら即終了し、FIXED のときだけ累積する。
    """
    fix_result = fix_architecture_rules.run_fixer(
        repo_root, rules_path, rule_ids=rule_ids, check=check)
    # fixer が内部例外を返した場合は再試行しても改善しないので即終了。
    if fix_result["status"] == "ERROR":
        return _build_error_payload(
            cycle, history, applied_fixes, fix_result["error"])
    # 「直せる rule が残っていない」状態なので、人手判断に切り替える。
    if fix_result["status"] != "FIXED":
        return _build_needs_human_payload(
            cycle, history, applied_fixes, check)
    _extend_applied_fixes(applied_fixes, cycle, fix_result)
    return None


def _build_clean_payload(
    cycle: int,
    history: list[dict[str, Any]],
    applied_fixes: list[dict[str, Any]],
    check: dict[str, Any],
    *,
    has_autofix: bool,
) -> dict[str, Any]:
    """warnings が無いと判明したサイクルの戻り値を組む。

    Args:
        cycle: そのサイクル番号。
        history: ここまでの check 履歴。
        applied_fixes: ここまでに適用した fix の累積。
        check: 直近の checker 結果。
        has_autofix: これまでに 1 回でも fix を適用したか。

    Returns:
        dict: status="OK" または "AUTOFIXED" の戻り値。

    Policy:
        - 戻り値の形を 1 箇所に集約し、呼び出し側の早期 return を簡潔にする。
    """
    return {
        "status": "AUTOFIXED" if has_autofix else "OK",
        "cycles": cycle,
        "history": history,
        "applied_fixes": applied_fixes,
        "final_check": check,
    }


def _build_error_payload(
    cycle: int,
    history: list[dict[str, Any]],
    applied_fixes: list[dict[str, Any]],
    error: str,
) -> dict[str, Any]:
    """fixer が ERROR を返した場合の戻り値を組む。

    Args:
        cycle: そのサイクル番号。
        history: ここまでの check 履歴。
        applied_fixes: ここまでに適用した fix の累積。
        error: fixer が返したエラーメッセージ。

    Returns:
        dict: status="ERROR" の戻り値。

    Policy:
        - 再試行しても改善しないので、その時点で確定した状態を返す。
    """
    return {
        "status": "ERROR",
        "cycles": cycle,
        "history": history,
        "applied_fixes": applied_fixes,
        "error": error,
    }


def _build_needs_human_payload(
    cycle: int,
    history: list[dict[str, Any]],
    applied_fixes: list[dict[str, Any]],
    check: dict[str, Any],
) -> dict[str, Any]:
    """fixer が FIXED 以外（NOOP など）を返した場合の戻り値を組む。

    Args:
        cycle: そのサイクル番号。
        history: ここまでの check 履歴。
        applied_fixes: ここまでに適用した fix の累積。
        check: 直近の checker 結果。

    Returns:
        dict: status="NEEDS_HUMAN" の戻り値。

    Policy:
        - 直せる rule が残っていない状態を人手判断に引き渡すための形に揃える。
    """
    return {
        "status": "NEEDS_HUMAN",
        "cycles": cycle,
        "history": history,
        "applied_fixes": applied_fixes,
        "final_check": check,
    }


def _build_final_payload(
    max_cycles: int,
    history: list[dict[str, Any]],
    applied_fixes: list[dict[str, Any]],
    final_check: dict[str, Any],
    *,
    has_autofix: bool,
) -> dict[str, Any]:
    """上限回数到達後の最終 check を踏まえた戻り値を組む。

    Args:
        max_cycles: 上限サイクル数。
        history: ここまでの check 履歴。
        applied_fixes: ここまでに適用した fix の累積。
        final_check: 上限回数後の最終 checker 結果。
        has_autofix: ループ中に 1 回でも fix を適用したか。

    Returns:
        dict: status="AUTOFIXED" または "NEEDS_HUMAN" の戻り値。

    Policy:
        - autofix が走ったうえで最終 check が clean なときだけ AUTOFIXED とする。
    """
    is_autofixed_clean = has_autofix and not final_check["has_warnings"]
    return {
        "status": "AUTOFIXED" if is_autofixed_clean else "NEEDS_HUMAN",
        "cycles": max_cycles,
        "history": history,
        "applied_fixes": applied_fixes,
        "final_check": final_check,
    }


def _build_exception_payload(
    history: list[dict[str, Any]],
    applied_fixes: list[dict[str, Any]],
    exc: Exception,
) -> dict[str, Any]:
    """try ループ全体で例外が出た場合の戻り値を組む。

    Args:
        history: 例外発生時点までの check 履歴。
        applied_fixes: 例外発生時点までの fix 累積。
        exc: 捕捉した例外。

    Returns:
        dict: status="ERROR" の戻り値（cycles は history 長で代用）。

    Policy:
        - 例外の str 表現だけを露出し、トレースは呼び出し側に任せる。
    """
    return {
        "status": "ERROR",
        "cycles": len(history),
        "history": history,
        "applied_fixes": applied_fixes,
        "error": str(exc),
    }


def _extend_applied_fixes(
    applied_fixes: list[dict[str, Any]],
    cycle: int,
    fix_result: dict[str, Any],
) -> None:
    """fix_result.applied_fixes を cycle 番号付きで applied_fixes に積む。

    Args:
        applied_fixes: 蓄積先のリスト（in-place 更新）。
        cycle: 現在のサイクル番号。
        fix_result: fixer の戻り値。

    Policy:
        - 元実装と同じく cycle を最初のキーに付け足してから fix dict を展開する。
    """
    applied_fixes.extend({"cycle": cycle, **fix}
                         for fix in fix_result["applied_fixes"])


def _run_main(argv: list[str] | None) -> int:
    """CLI 本体。parser を組み立てて run_repair を呼び、結果 JSON を stdout に出す。

    Args:
        argv: コマンドライン引数。None なら sys.argv[1:] を使う。

    Returns:
        int: status が OK / AUTOFIXED なら 0、それ以外は 1。

    Policy:
        - parser 組み立ては _build_arg_parser に切り出し、ここでは流れだけ残す。
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    result = run_repair(
        args.repo_root,
        args.rules_path,
        max_cycles=args.max_cycles,
        rule_ids=set(args.rule_id) if args.rule_id else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"OK", "AUTOFIXED"} else 1


def _build_arg_parser() -> argparse.ArgumentParser:
    """CLI 用 argparse.ArgumentParser を組み立てる。

    Returns:
        argparse.ArgumentParser: --repo-root / --rules-path / --max-cycles /
        --rule-id を受ける parser。

    Policy:
        - 既存 CLI の引数定義をそのまま 1 関数に閉じ込め、_run_main から呼び出す。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=ROOT /
        "docs" /
        "architecture_rules.yml")
    parser.add_argument("--max-cycles", type=int, default=5)
    parser.add_argument("--rule-id", action="append", default=[])
    return parser


if __name__ == "__main__":
    raise SystemExit(run_main())
