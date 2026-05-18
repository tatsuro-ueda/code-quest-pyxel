"""プレイセッションの開始・生存確認・終了を SQLite に記録するサービス。

このファイルに含まれる関数・クラス：

- start_session: 新しいプレイセッションを INSERT OR IGNORE で記録する public 関数
- heartbeat_session: 生存確認時刻と active_seconds を更新する public 関数
- end_session: セッション終了情報（ended_at / ended_cleanly）を保存する public 関数
- summarize_sessions_by_browser: ブラウザ種別ごとのセッション数と平均継続時間を返す public 関数
- summarize_sessions: 日付×ページ種別ごとの集計（短中長セッション数を含む）を返す public 関数
- _normalize_timestamp: naive/aware 混在 datetime を UTC aware に揃える内部 helper
- _serialize_timestamp: UTC 正規化した ISO8601 文字列を返す内部 helper
- _compute_active_seconds: 開始〜最終確認時刻の差を非負の秒数 int で返す内部 helper
- _connect: SQLite 接続を返し、未作成テーブルや欠落カラムを補う内部 helper
- _insert_new_session: play_sessions に INSERT OR IGNORE で 1 行追加する内部 helper
- _fetch_started_at: session_id から started_at の datetime を取り出す内部 helper
- _update_heartbeat: heartbeat 行を実 UPDATE する内部 helper
- _update_end_session: 終了行の各カラムを実 UPDATE する内部 helper
- _build_end_session_params: 終了 UPDATE の bind パラメータ tuple を組む内部 helper
- _query_browser_summary: ブラウザ別集計 SQL を実行し dict 列に整形する内部 helper
- _row_to_browser_dict: ブラウザ別集計 1 行を dict に詰め替える内部 helper
- _query_daily_summary: 日付×ページ種別集計 SQL を実行し dict 列に整形する内部 helper
- _row_to_daily_dict: 日付×ページ種別集計 1 行を dict に詰め替える内部 helper

Problems:
    - SQL 文字列とトランザクションを public 関数本体に書くと、入口契約（誰が何を
      渡す）と実装詳細（どの列をどう UPDATE するか）が同じ階層に混ざって読みづらく、
      行数も 20 行を簡単に超えてしまう。
    - heartbeat / end_session の「行が無ければ何もしない」ガード分岐を public 側に
      置くと、public 関数が制御フローを直接持ち、CR203/CR204 を満たさなくなる。

Solutions:
    - SQL とトランザクションは _update_xxx / _query_xxx / _fetch_xxx の private
      helper に切り出し、public 関数は「private 委譲 + return」のステップ列に揃える。
    - datetime まわりの正規化と差分計算も _normalize_timestamp /
      _serialize_timestamp / _compute_active_seconds に集約し、public 側からは
      呼ぶだけにする。
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


# === Public API ===


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


def start_session(
    db_path: Path,
    *,
    session_id: str,
    page_kind: str,
    started_at: datetime,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """新しいプレイセッションを記録する（既存 ID なら何もしない）。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
        session_id: セッションを一意に識別する文字列。
        page_kind: ページ種別（main / codemaker など）。
        started_at: セッション開始時刻。
        ip_address: 接続元 IP（任意）。
        user_agent: User-Agent 文字列（任意）。
    Policy:
        - INSERT OR IGNORE による冪等挿入は private helper に委ね、本関数は
          シリアライズと委譲のステップ列に揃える。
    """
    started = _serialize_timestamp(started_at)
    _insert_new_session(
        db_path,
        session_id=session_id,
        page_kind=page_kind,
        started=started,
        ip_address=ip_address,
        user_agent=user_agent,
    )


def heartbeat_session(  # noqa: CR100
    db_path: Path,
    *,
    session_id: str,
    seen_at: datetime,
) -> None:
    """セッションの生存確認を更新し、現時点までの active_seconds を算出する。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
        session_id: 対象のセッション ID。
        seen_at: 最終生存確認時刻。
    Policy:
        - 関数名 heartbeat_session は tools/web_runtime_server.py 等から固定参照
          されているため変更しない（# noqa: CR100）。
        - 実 UPDATE と「行が無ければ何もしない」分岐は private helper に委ねる。
    """
    seen = _normalize_timestamp(seen_at)
    _update_heartbeat(db_path, session_id=session_id, seen=seen)


def end_session(
    db_path: Path,
    *,
    session_id: str,
    ended_at: datetime,
    ended_cleanly: bool,
) -> None:
    """セッション終了を記録し、正常終了か否かも保存する。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
        session_id: 対象のセッション ID。
        ended_at: 終了時刻。
        ended_cleanly: 正常終了なら True、強制クローズ等なら False。
    Policy:
        - 実 UPDATE と「行が無ければ何もしない」分岐は private helper に委ねる。
    """
    ended = _normalize_timestamp(ended_at)
    _update_end_session(
        db_path,
        session_id=session_id,
        ended=ended,
        ended_cleanly=ended_cleanly,
    )


def summarize_sessions_by_browser(
    db_path: Path,
) -> list[dict[str, int | str]]:
    """ブラウザ種別ごとにセッション数と平均継続時間を返す。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
    Returns:
        {"browser", "session_count", "avg_active_seconds"} を持つ dict のリスト。
        session_count の降順、browser 名の昇順で並ぶ。
    Policy:
        - SQL と dict 整形は private helper に委ねる。
    """
    return _query_browser_summary(db_path)


def summarize_sessions(db_path: Path) -> list[dict[str, int | str]]:
    """日付×ページ種別ごとにセッション数と継続時間帯別の集計を返す。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
    Returns:
        日付 × page_kind ごとに集計した dict のリスト。各 dict は
        date / page_kind / session_count / avg_active_seconds /
        short_sessions / middle_sessions / long_sessions を持つ。
    Policy:
        - SQL と dict 整形は private helper に委ねる。
    """
    return _query_daily_summary(db_path)


# === Internal helpers (private) ===

_MIGRATIONS = (
    ("ip_address", "ALTER TABLE play_sessions ADD COLUMN ip_address TEXT"),
    ("user_agent", "ALTER TABLE play_sessions ADD COLUMN user_agent TEXT"),
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


def _normalize_timestamp(value: datetime) -> datetime:
    """naive/aware 混在の datetime を UTC aware に揃える。

    Args:
        value: 任意の datetime。
    Returns:
        tzinfo が UTC に揃った datetime。
    Policy:
        - tzinfo が無い naive は UTC とみなす（replace）。
        - tzinfo がある aware は UTC へ astimezone する。
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _serialize_timestamp(value: datetime) -> str:
    """UTC 正規化した ISO8601 文字列を返す。

    Args:
        value: 任意の datetime。
    Returns:
        UTC aware に揃えた datetime の isoformat 文字列。
    Policy:
        - 正規化は _normalize_timestamp に委ねる。
    """
    return _normalize_timestamp(value).isoformat()


def _compute_active_seconds(
    started_at: datetime,
    seen_at: datetime,
) -> int:
    """開始〜最終確認時刻の差を秒（非負整数）で返す。

    Args:
        started_at: セッション開始時刻。
        seen_at: 最終確認時刻。
    Returns:
        max(0, int((seen_at - started_at).total_seconds())) の秒数。
    Policy:
        - 引数は両方とも _normalize_timestamp で UTC aware に揃えてから差分を取る。
        - 負の値は 0 にクランプする。
    """
    delta = _normalize_timestamp(seen_at) - _normalize_timestamp(started_at)
    return max(0, int(delta.total_seconds()))


def _connect(db_path: Path) -> sqlite3.Connection:
    """SQLite に接続し、テーブルがなければ作成する。

    Args:
        db_path: 接続先 SQLite ファイルのパス（親ディレクトリも自動作成）。
    Returns:
        スキーマ適用済みの sqlite3.Connection。
    Policy:
        - 初回呼び出しでも play_sessions テーブルと欠落カラムを補う。
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    existing_columns = {row[1] for row in conn.execute(
        "PRAGMA table_info(play_sessions)")}
    for column, statement in _MIGRATIONS:
        if column not in existing_columns:
            conn.execute(statement)
    return conn


def _insert_new_session(
    db_path: Path,
    *,
    session_id: str,
    page_kind: str,
    started: str,
    ip_address: str | None,
    user_agent: str | None,
) -> None:
    """play_sessions に INSERT OR IGNORE で 1 行追加する。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
        session_id: セッション ID。
        page_kind: ページ種別。
        started: 開始時刻の ISO8601 文字列。
        ip_address: 接続元 IP（任意）。
        user_agent: User-Agent 文字列（任意）。
    Policy:
        - 既存 session_id は IGNORE（冪等）。
    """
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


def _fetch_started_at(
    conn: sqlite3.Connection,
    session_id: str,
) -> datetime | None:
    """session_id に対応する started_at を datetime で返す。

    Args:
        conn: open 済みの sqlite3.Connection。
        session_id: セッション ID。
    Returns:
        該当行があれば started_at の datetime、無ければ None。
    Policy:
        - 行が無いケースは None を返し、呼び出し側で早期 return させる。
    """
    row = conn.execute(
        "SELECT started_at FROM play_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if row is None:
        return None
    return datetime.fromisoformat(row[0])


_HEARTBEAT_UPDATE_SQL = """
UPDATE play_sessions
SET last_seen_at = ?, active_seconds = ?
WHERE session_id = ?
"""


_END_SESSION_UPDATE_SQL = """
UPDATE play_sessions
SET last_seen_at = ?,
    ended_at = ?,
    active_seconds = ?,
    ended_cleanly = ?
WHERE session_id = ?
"""


def _update_heartbeat(
    db_path: Path,
    *,
    session_id: str,
    seen: datetime,
) -> None:
    """heartbeat 行の last_seen_at / active_seconds を UPDATE する。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
        session_id: セッション ID。
        seen: UTC 正規化済みの最終確認時刻。
    Policy:
        - 行が無ければ何もしない（早期 return）。
        - active_seconds は started_at との差分から再計算する。
    """
    with _connect(db_path) as conn:
        started_at = _fetch_started_at(conn, session_id)
        if started_at is None:
            return
        params = (
            _serialize_timestamp(seen),
            _compute_active_seconds(started_at, seen),
            session_id,
        )
        conn.execute(_HEARTBEAT_UPDATE_SQL, params)


def _update_end_session(
    db_path: Path,
    *,
    session_id: str,
    ended: datetime,
    ended_cleanly: bool,
) -> None:
    """終了行の各カラムを UPDATE する。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
        session_id: セッション ID。
        ended: UTC 正規化済みの終了時刻。
        ended_cleanly: 正常終了なら True。
    Policy:
        - 行が無ければ何もしない（早期 return）。
        - ended_cleanly は 1/0 に変換して保存する。
    """
    with _connect(db_path) as conn:
        started_at = _fetch_started_at(conn, session_id)
        if started_at is None:
            return
        params = _build_end_session_params(
            started_at=started_at,
            ended=ended,
            ended_cleanly=ended_cleanly,
            session_id=session_id,
        )
        conn.execute(_END_SESSION_UPDATE_SQL, params)


def _build_end_session_params(
    *,
    started_at: datetime,
    ended: datetime,
    ended_cleanly: bool,
    session_id: str,
) -> tuple:
    """終了 UPDATE の bind パラメータ tuple を組み立てる。

    Args:
        started_at: セッション開始時刻。
        ended: UTC 正規化済みの終了時刻。
        ended_cleanly: 正常終了なら True。
        session_id: セッション ID。
    Returns:
        (last_seen, ended, active_seconds, cleanly_flag, session_id)
        の 5 要素 tuple。
    Policy:
        - ended_cleanly は 1/0 に変換する。
    """
    ended_iso = _serialize_timestamp(ended)
    return (
        ended_iso,
        ended_iso,
        _compute_active_seconds(started_at, ended),
        1 if ended_cleanly else 0,
        session_id,
    )


_BROWSER_SUMMARY_SQL = f"""
SELECT
    {_BROWSER_CASE_SQL} AS browser,
    COUNT(*) AS session_count,
    CAST(AVG(active_seconds) AS INTEGER) AS avg_active_seconds
FROM play_sessions
GROUP BY browser
ORDER BY session_count DESC, browser
"""


_DAILY_SUMMARY_SQL = """
SELECT
    substr(started_at, 1, 10) AS session_date,
    page_kind,
    COUNT(*) AS session_count,
    CAST(AVG(active_seconds) AS INTEGER) AS avg_active_seconds,
    SUM(CASE WHEN active_seconds < 60 THEN 1 ELSE 0 END)
        AS short_sessions,
    SUM(CASE WHEN active_seconds >= 60 AND active_seconds < 300
        THEN 1 ELSE 0 END) AS middle_sessions,
    SUM(CASE WHEN active_seconds >= 300 THEN 1 ELSE 0 END)
        AS long_sessions
FROM play_sessions
GROUP BY session_date, page_kind
ORDER BY session_date, page_kind
"""


def _query_browser_summary(
    db_path: Path,
) -> list[dict[str, int | str]]:
    """ブラウザ別集計 SQL を実行し dict のリストに整形する。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
    Returns:
        browser / session_count / avg_active_seconds を持つ dict のリスト。
    Policy:
        - 並び順は session_count 降順、browser 昇順。
    """
    with _connect(db_path) as conn:
        rows = conn.execute(_BROWSER_SUMMARY_SQL).fetchall()
    return [_row_to_browser_dict(row) for row in rows]


def _row_to_browser_dict(row: tuple) -> dict[str, int | str]:
    """ブラウザ別集計 1 行を dict に詰め替える。

    Args:
        row: (browser, session_count, avg_active_seconds) の tuple。
    Returns:
        browser / session_count / avg_active_seconds を持つ dict。
    Policy:
        - 列順は _BROWSER_SUMMARY_SQL の SELECT 順に従う。
    """
    return {
        "browser": row[0],
        "session_count": row[1],
        "avg_active_seconds": row[2],
    }


def _query_daily_summary(
    db_path: Path,
) -> list[dict[str, int | str]]:
    """日付×ページ種別集計 SQL を実行し dict のリストに整形する。

    Args:
        db_path: 接続先 SQLite ファイルのパス。
    Returns:
        date / page_kind / session_count / avg_active_seconds /
        short_sessions / middle_sessions / long_sessions を持つ dict のリスト。
    Policy:
        - 短中長セッションの閾値は 60 秒 / 300 秒。
        - 並び順は session_date, page_kind の昇順。
    """
    with _connect(db_path) as conn:
        rows = conn.execute(_DAILY_SUMMARY_SQL).fetchall()
    return [_row_to_daily_dict(row) for row in rows]


def _row_to_daily_dict(row: tuple) -> dict[str, int | str]:
    """日付×ページ種別集計 1 行を dict に詰め替える。

    Args:
        row: SQL SELECT の 7 列 tuple。
    Returns:
        date / page_kind / session_count / avg_active_seconds /
        short_sessions / middle_sessions / long_sessions を持つ dict。
    Policy:
        - 列順は _DAILY_SUMMARY_SQL の SELECT 順に従う。
    """
    return {
        "date": row[0],
        "page_kind": row[1],
        "session_count": row[2],
        "avg_active_seconds": row[3],
        "short_sessions": row[4],
        "middle_sessions": row[5],
        "long_sessions": row[6],
    }
