#!/usr/bin/env python3
"""G10 セーブデータ互換テスト CLI。

このファイルに含まれる関数：

- main.py の restore_snapshot を再現する public 関数 restore_snapshot
- CLI 入口の public 関数 main（fixture 読み込みと結果集計と exit code 制御）
- fixture ディレクトリから save_v*.json を列挙する内部関数 _collect_fixtures
- 1 件の fixture を検証して FAIL メッセージを stdout に出す内部関数 _check_one_fixture
- player の必須キー欠落を判定する述語関数 _has_missing_player_keys
- town_pos が tuple かつ長さ 2 でないかを判定する述語関数 _has_invalid_town_pos
- fixture リストを順に検証して fail フラグを返す内部関数 _verify_all_fixtures

Problems:
    - main.py を直接 import すると Game() が起動してしまい、CI で
      セーブデータ互換性だけを軽量に検証できない。
    - 検証ロジックを 1 つの main に直書きすると、必須キー検証と
      town_pos 検証と例外処理の責務が混ざって読み手に負荷をかける。

Solutions:
    - restore_snapshot ロジックをこの CLI に再現し、Game() を起動しない。
    - main は述語呼び出し + private 委譲 + return のステップ列に揃え、
      fixture 列挙・1 件検証・全件検証を private helper に切り出す。
"""
import json
import sys
import traceback
from pathlib import Path


# === Public API ===

def restore_snapshot(snapshot: dict) -> dict:
    """snapshot dict を main.py の restore_snapshot と同じ形式に再構築する。

    Args:
        snapshot: save_v*.json をロードした dict。
    Returns:
        player と town_pos を含む dict。
    Policy:
        - main.py 側の dict 操作と同じ最小ロジックに揃える。
    """
    raw_pos = snapshot["town_pos"]
    return {
        "player": dict(snapshot["player"]),
        "town_pos": (int(raw_pos[0]), int(raw_pos[1])),
    }


def main() -> int:  # noqa: CR100
    """CLI 入口。fixture を検証して exit code を返す。

    Returns:
        全件 OK なら 0、1 件でも FAIL なら 1。
    Policy:
        - public 関数はステップ列に揃え、fixture 列挙と全件検証は
          private helper に委ねる。
    """
    fixture_dir = Path("tests/fixtures")
    fixtures = _collect_fixtures(fixture_dir)
    return _run_compat_verification(fixture_dir, fixtures)


# === Internal helpers (private) ===

def _run_compat_verification(
        fixture_dir: Path, fixtures: list[Path]) -> int:
    """fixture 列挙結果を見て exit code を決める。

    Args:
        fixture_dir: fixture 探索ディレクトリ（エラーメッセージ用）。
        fixtures: _collect_fixtures の戻り値。
    Returns:
        全件 OK / 列挙失敗 / 検証失敗を 0 / 1 / 1 にマップした exit code。
    Policy:
        - 空 fixture 用の早期 return と全件検証分岐を main から引き取る。
    """
    if not fixtures:
        print(
            "FAIL: テスト用セーブデータが見つかりません: "
            f"{fixture_dir}/save_v*.json")
        return 1
    is_failed = _verify_all_fixtures(fixtures)
    return 1 if is_failed else 0


def _collect_fixtures(fixture_dir: Path) -> list[Path]:
    """fixture ディレクトリから save_v*.json をソート順に列挙する。

    Args:
        fixture_dir: fixture を探すディレクトリ。
    Returns:
        save_v*.json の Path リスト（ソート済み）。
    Policy:
        - ファイル名昇順で安定させ、後段の出力順序を再現可能にする。
    """
    return sorted(fixture_dir.glob("save_v*.json"))


def _has_missing_player_keys(player: dict) -> list[str]:
    """player dict に必須キーのうち欠落しているものがあれば列挙する。

    Args:
        player: restore_snapshot の戻り値の "player" 部分。
    Returns:
        欠落しているキーのリスト（無ければ空リスト）。
    Policy:
        - 必須キーは (hp, x, y, lv) に固定する。
    """
    required_keys = ("hp", "x", "y", "lv")
    return [k for k in required_keys if k not in player]


def _has_invalid_town_pos(town_pos: object) -> bool:
    """town_pos が tuple かつ長さ 2 でなければ True を返す述語。

    Args:
        town_pos: restore_snapshot の戻り値の "town_pos" 部分。
    Returns:
        不正なら True。
    Policy:
        - 形状チェックのみで、値の範囲には踏み込まない。
    """
    if not isinstance(town_pos, tuple):
        return True
    return len(town_pos) != 2


def _check_one_fixture(fixture_path: Path) -> bool:
    """fixture 1 件を検証し、FAIL かどうかを返す。

    Args:
        fixture_path: 検証対象の save_v*.json パス。
    Returns:
        FAIL なら True、OK なら False。
    Policy:
        - 例外は traceback を stdout に出し、FAIL 扱いに統一する。
    """
    try:
        return _verify_fixture_payload(fixture_path)
    except Exception:
        print(f"FAIL: {fixture_path.name} — 例外発生")
        traceback.print_exc()
        return True


def _verify_fixture_payload(fixture_path: Path) -> bool:
    """fixture を読み込み、player と town_pos を検証する。

    Args:
        fixture_path: 検証対象の save_v*.json パス。
    Returns:
        FAIL なら True、OK なら False。
    Policy:
        - 例外は呼び出し元（_check_one_fixture）に伝搬させて捕捉させる。
    """
    with open(fixture_path, encoding="utf-8") as f:
        snapshot = json.load(f)
    result = restore_snapshot(snapshot)
    player = result["player"]
    missing = _has_missing_player_keys(player)
    if missing:
        print(f"FAIL: {fixture_path.name} — 必須キー不足: {missing}")
        return True
    town_pos = result["town_pos"]
    if _has_invalid_town_pos(town_pos):
        print(f"FAIL: {fixture_path.name} — town_pos 不正: {town_pos}")
        return True
    print(
        f"OK: {fixture_path.name} — v{snapshot['save_version']} "
        f"ロード成功 (キー数: {len(player)})")
    return False


def _verify_all_fixtures(fixtures: list[Path]) -> bool:
    """fixture リストを順に検証し、1 件でも FAIL なら True を返す。

    Args:
        fixtures: 検証対象の Path リスト。
    Returns:
        いずれかが FAIL なら True、全件 OK なら False。
    Policy:
        - 失敗があっても残りを全件検証して結果を一度に出力する。
    """
    is_failed = False
    for fixture_path in fixtures:
        if _check_one_fixture(fixture_path):
            is_failed = True
    return is_failed


if __name__ == "__main__":
    sys.exit(main())
