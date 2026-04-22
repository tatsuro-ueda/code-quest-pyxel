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
    ended_cleanly INTEGER NOT NULL DEFAULT 0,
    ip_address TEXT,
    user_agent TEXT
)
"""

_MIGRATIONS = (
    ("ip_address", "ALTER TABLE play_sessions ADD COLUMN ip_address TEXT"),
    ("user_agent", "ALTER TABLE play_sessions ADD COLUMN user_agent TEXT"),
)


def _normalize_timestamp(value: datetime) -> datetime:
    """naive/aware 混在の datetime を UTC aware に揃える。"""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _serialize_timestamp(value: datetime) -> str:
    """UTC 正規化した ISO8601 文字列を返す。"""
    return _normalize_timestamp(value).isoformat()


def _active_seconds(started_at: datetime, seen_at: datetime) -> int:
    """開始〜最終確認時刻の差を秒（非負整数）で返す。"""
    delta = _normalize_timestamp(seen_at) - _normalize_timestamp(started_at)
    return max(0, int(delta.total_seconds()))


def _connect(db_path: Path) -> sqlite3.Connection:
    """SQLite に接続し、テーブルがなければ作成する。"""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    existing_columns = {row[1] for row in conn.execute("PRAGMA table_info(play_sessions)")}
    for column, statement in _MIGRATIONS:
        if column not in existing_columns:
            conn.execute(statement)
    return conn


def start_session(
    db_path: Path,
    *,
    session_id: str,
    page_kind: str,
    started_at: datetime,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """新しいプレイセッションを記録する（既存IDなら何もしない）。"""
    started = _serialize_timestamp(started_at)
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO play_sessions (
                session_id, page_kind, started_at, last_seen_at, ended_at,
                active_seconds, ended_cleanly, ip_address, user_agent
            ) VALUES (?, ?, ?, ?, NULL, 0, 0, ?, ?)
            """,
            (session_id, page_kind, started, started, ip_address, user_agent),
        )


def heartbeat_session(db_path: Path, *, session_id: str, seen_at: datetime) -> None:
    """セッションの生存確認を更新し、現時点までの active_seconds を算出する。"""
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
    """セッション終了を記録し、正常終了か否かも保存する。"""
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


_BROWSER_CASE_SQL = """
CASE
    WHEN user_agent IS NULL OR user_agent = '' THEN 'Unknown'
    WHEN user_agent LIKE '%Edg/%'     THEN 'Edge'
    WHEN user_agent LIKE '%OPR/%'     THEN 'Opera'
    WHEN user_agent LIKE '%Chrome/%'  THEN 'Chrome'
    WHEN user_agent LIKE '%Firefox/%' THEN 'Firefox'
    WHEN user_agent LIKE '%Safari/%'  THEN 'Safari'
    ELSE 'Other'
END
"""


def summarize_sessions_by_browser(db_path: Path) -> list[dict[str, int | str]]:
    """ブラウザ種別ごとにセッション数と平均継続時間を返す。"""
    with _connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT
                {_BROWSER_CASE_SQL} AS browser,
                COUNT(*) AS session_count,
                CAST(AVG(active_seconds) AS INTEGER) AS avg_active_seconds
            FROM play_sessions
            GROUP BY browser
            ORDER BY session_count DESC, browser
            """
        ).fetchall()
    return [
        {"browser": row[0], "session_count": row[1], "avg_active_seconds": row[2]}
        for row in rows
    ]


def summarize_sessions(db_path: Path) -> list[dict[str, int | str]]:
    """日付×ページ種別ごとにセッション数と継続時間帯別の集計を返す。"""
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
