from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS play_sessions (
    session_id TEXT PRIMARY KEY,
    page_kind TEXT NOT NULL,
    started_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    ended_at TEXT,
    active_seconds INTEGER NOT NULL DEFAULT 0,
    ended_cleanly INTEGER NOT NULL DEFAULT 0
)
"""


def _normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _serialize_timestamp(value: datetime) -> str:
    return _normalize_timestamp(value).isoformat()


def _active_seconds(started_at: datetime, seen_at: datetime) -> int:
    delta = _normalize_timestamp(seen_at) - _normalize_timestamp(started_at)
    return max(0, int(delta.total_seconds()))


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    return conn


def start_session(
    db_path: Path,
    *,
    session_id: str,
    page_kind: str,
    started_at: datetime,
) -> None:
    started = _serialize_timestamp(started_at)
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO play_sessions (
                session_id, page_kind, started_at, last_seen_at, ended_at, active_seconds, ended_cleanly
            ) VALUES (?, ?, ?, ?, NULL, 0, 0)
            """,
            (session_id, page_kind, started, started),
        )


def heartbeat_session(
    db_path: Path,
    *,
    session_id: str,
    seen_at: datetime,
) -> None:
    seen = _normalize_timestamp(seen_at)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT started_at FROM play_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return
        started_at = datetime.fromisoformat(row[0])
        conn.execute(
            """
            UPDATE play_sessions
            SET last_seen_at = ?, active_seconds = ?
            WHERE session_id = ?
            """,
            (_serialize_timestamp(seen), _active_seconds(started_at, seen), session_id),
        )


def end_session(
    db_path: Path,
    *,
    session_id: str,
    ended_at: datetime,
    ended_cleanly: bool,
) -> None:
    ended = _normalize_timestamp(ended_at)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT started_at FROM play_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return
        started_at = datetime.fromisoformat(row[0])
        conn.execute(
            """
            UPDATE play_sessions
            SET last_seen_at = ?,
                ended_at = ?,
                active_seconds = ?,
                ended_cleanly = ?
            WHERE session_id = ?
            """,
            (
                _serialize_timestamp(ended),
                _serialize_timestamp(ended),
                _active_seconds(started_at, ended),
                1 if ended_cleanly else 0,
                session_id,
            ),
        )


def summarize_sessions(db_path: Path) -> list[dict[str, int | str]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                substr(started_at, 1, 10) AS session_date,
                page_kind,
                COUNT(*) AS session_count,
                CAST(AVG(active_seconds) AS INTEGER) AS avg_active_seconds,
                SUM(CASE WHEN active_seconds < 60 THEN 1 ELSE 0 END) AS short_sessions,
                SUM(CASE WHEN active_seconds >= 60 AND active_seconds < 300 THEN 1 ELSE 0 END) AS middle_sessions,
                SUM(CASE WHEN active_seconds >= 300 THEN 1 ELSE 0 END) AS long_sessions
            FROM play_sessions
            GROUP BY session_date, page_kind
            ORDER BY session_date, page_kind
            """
        ).fetchall()
    return [
        {
            "date": row[0],
            "page_kind": row[1],
            "session_count": row[2],
            "avg_active_seconds": row[3],
            "short_sessions": row[4],
            "middle_sessions": row[5],
            "long_sessions": row[6],
        }
        for row in rows
    ]
