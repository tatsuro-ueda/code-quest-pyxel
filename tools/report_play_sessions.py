"""Block Quest プレイセッションの集計サマリを表示する CLI。

Problems:
    - SQLite に蓄積された play_sessions を眺めるだけでは、日付別 / browser 別の
      傾向（short/middle/long の比率や平均値）が即座に読み取れない。
    - 集計結果のフォーマットを毎回手書きすると、運用者ごとに表記が揺れる。

Solutions:
    - summarize_sessions / summarize_sessions_by_browser を呼び、整形済み行を
      標準出力に流す薄い CLI レイヤを提供する。
    - render 系を純粋関数として切り出し、テストと再利用の両方を可能にする。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.play_session_logging import (  # noqa: E402
    summarize_sessions,
    summarize_sessions_by_browser,
)


# === Public API ===


def render_summary(rows: list[dict[str, int | str]]) -> str:
    """日付 × page_kind ごとのサマリを 1 ブロックの文字列に整形する。

    Args:
        rows: summarize_sessions が返した 1 行 1 dict のリスト。

    Returns:
        str: 1 行 1 セッション群の整形済み文字列。空入力なら案内文字列。

    Policy:
        - 空判定と整形は private helper に閉じ込め、ここは委譲のみにする。
    """
    return _render_or_empty(rows, _empty_summary_message, _format_summary_rows)


def render_browser_summary(rows: list[dict[str, int | str]]) -> str:
    """browser 別サマリを 1 ブロックの文字列に整形する。

    Args:
        rows: summarize_sessions_by_browser が返した 1 行 1 dict のリスト。

    Returns:
        str: 1 行 1 browser の整形済み文字列。空入力なら案内文字列。

    Policy:
        - 空判定と整形は private helper に閉じ込め、ここは委譲のみにする。
    """
    return _render_or_empty(rows, _empty_browser_message, _format_browser_rows)


def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """CLI エントリポイント。--db-path で SQLite を指定して両サマリを出す。

    Args:
        argv: argparse に渡す引数列。None なら sys.argv[1:] を使う。

    Returns:
        int: 常に 0（失敗は例外を上に伝搬させる）。

    Policy:
        - 引数解析 → 集計 → 整形 → print を private helper に委譲する。
    """
    args = _parse_args(argv)
    db_path = Path(args.db_path)
    _print_reports(db_path)
    return 0


# === Internal helpers (private) ===


def _render_or_empty(
    rows: list[dict[str, int | str]],
    empty_fn,
    format_fn,
) -> str:
    """空ならガイダンス文、そうでなければ整形結果を返す共通テンプレ。

    Args:
        rows: 集計済み行のリスト。
        empty_fn: 空のとき呼ぶ案内文ファクトリ。
        format_fn: 非空のとき呼ぶ整形関数（rows を受ける）。

    Returns:
        str: 案内文または整形済み文字列。

    Policy:
        - public renderer 群の空チェックと委譲を 1 箇所に集約する。
    """
    if not rows:
        return empty_fn()
    return format_fn(rows)


def _empty_summary_message() -> str:
    """サマリ行が無いときの案内文を返す。

    Returns:
        str: 「No play sessions recorded.」固定文。

    Policy:
        - 表示文の SSoT として 1 箇所に集約する。
    """
    return "No play sessions recorded."


def _empty_browser_message() -> str:
    """browser 行が無いときの案内文を返す。

    Returns:
        str: 「No browser data.」固定文。

    Policy:
        - 表示文の SSoT として 1 箇所に集約する。
    """
    return "No browser data."


def _format_summary_rows(rows: list[dict[str, int | str]]) -> str:
    """日付 × page_kind サマリ行を改行連結文字列に整形する。

    Args:
        rows: 1 行 1 dict のリスト。

    Returns:
        str: 改行で連結された整形済み文字列。

    Policy:
        - 1 行ごとに _format_summary_row に委譲する。
    """
    lines = [_format_summary_row(row) for row in rows]
    return "\n".join(lines)


def _format_summary_row(row: dict[str, int | str]) -> str:
    """日付 × page_kind サマリ 1 行を整形する。

    Args:
        row: 1 行ぶんの dict。

    Returns:
        str: 1 行分の整形済み文字列。

    Policy:
        - row の各キーを 1 行のスペース区切りに展開する。
    """
    return (
        f"{row['date']} {row['page_kind']}: "
        f"sessions={row['session_count']} "
        f"avg={row['avg_active_seconds']}s "
        f"short={row['short_sessions']} "
        f"middle={row['middle_sessions']} "
        f"long={row['long_sessions']}"
    )


def _format_browser_rows(rows: list[dict[str, int | str]]) -> str:
    """browser サマリ行を改行連結文字列に整形する。

    Args:
        rows: 1 行 1 dict のリスト。

    Returns:
        str: 改行で連結された整形済み文字列。

    Policy:
        - 1 行ごとに _format_browser_row に委譲する。
    """
    lines = [_format_browser_row(row) for row in rows]
    return "\n".join(lines)


def _format_browser_row(row: dict[str, int | str]) -> str:
    """browser サマリ 1 行を整形する。

    Args:
        row: 1 行ぶんの dict。

    Returns:
        str: 1 行分の整形済み文字列。

    Policy:
        - browser / session_count / avg_active_seconds の 3 列に展開する。
    """
    return (
        f"{row['browser']}: "
        f"sessions={row['session_count']} "
        f"avg={row['avg_active_seconds']}s"
    )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """CLI 引数を解析する。

    Args:
        argv: argparse に渡す引数列。

    Returns:
        argparse.Namespace: 解析済みの引数オブジェクト。

    Policy:
        - --db-path のデフォルトは .runtime/play_sessions.sqlite3。
    """
    parser = argparse.ArgumentParser(
        description="Report Block Quest play session durations")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / ".runtime" / "play_sessions.sqlite3"),
        help="SQLite path used by the internal play session logger",
    )
    return parser.parse_args(argv)


def _print_reports(db_path: Path) -> None:
    """両サマリを順に標準出力へ流す。

    Args:
        db_path: SQLite ファイルパス。

    Policy:
        - 日付サマリ → 空行 → browser サマリの順で固定する。
    """
    print(render_summary(summarize_sessions(db_path)))
    print()
    print("-- browser --")
    print(render_browser_summary(summarize_sessions_by_browser(db_path)))


if __name__ == "__main__":
    raise SystemExit(main())
