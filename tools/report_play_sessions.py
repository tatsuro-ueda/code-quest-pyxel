from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.play_session_logging import summarize_sessions


def render_summary(rows: list[dict[str, int | str]]) -> str:
    if not rows:
        return "No play sessions recorded."

    lines: list[str] = []
    for row in rows:
        lines.append(
            (
                f"{row['date']} {row['page_kind']}: "
                f"sessions={row['session_count']} "
                f"avg={row['avg_active_seconds']}s "
                f"short={row['short_sessions']} "
                f"middle={row['middle_sessions']} "
                f"long={row['long_sessions']}"
            )
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report Block Quest play session durations")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / ".runtime" / "play_sessions.sqlite3"),
        help="SQLite path used by the internal play session logger",
    )
    args = parser.parse_args(argv)

    print(render_summary(summarize_sessions(Path(args.db_path))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
