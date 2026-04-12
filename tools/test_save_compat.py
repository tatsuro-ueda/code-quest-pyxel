#!/usr/bin/env python3
"""G10: セーブデータ互換テスト

テスト用セーブデータ (tests/fixtures/save_v1.json) を
restore_snapshot() 相当のロジックでロードし、互換性を検証する。

main.py を直接importすると Game() が起動してしまうため、
restore_snapshot のロジックをここに再現する（シンプルな dict 操作のみ）。

使い方:
    python tools/test_save_compat.py

exit 0 = テスト通過、exit 1 = テスト失敗
"""
import json
import sys
import traceback
from pathlib import Path


def restore_snapshot(snapshot: dict) -> dict:
    """main.py の restore_snapshot() と同じロジック。"""
    raw_pos = snapshot["town_pos"]
    return {
        "player": dict(snapshot["player"]),
        "town_pos": (int(raw_pos[0]), int(raw_pos[1])),
    }


def main():
    fixture_dir = Path("tests/fixtures")
    fixtures = sorted(fixture_dir.glob("save_v*.json"))

    if not fixtures:
        print(f"FAIL: テスト用セーブデータが見つかりません: {fixture_dir}/save_v*.json")
        return 1

    failed = False
    for fixture_path in fixtures:
        try:
            with open(fixture_path, encoding="utf-8") as f:
                snapshot = json.load(f)

            result = restore_snapshot(snapshot)

            # 必須キーの検証
            player = result["player"]
            required_keys = ("hp", "x", "y", "lv")
            missing = [k for k in required_keys if k not in player]
            if missing:
                print(f"FAIL: {fixture_path.name} — 必須キー不足: {missing}")
                failed = True
                continue

            # town_pos の検証
            town_pos = result["town_pos"]
            if not isinstance(town_pos, tuple) or len(town_pos) != 2:
                print(f"FAIL: {fixture_path.name} — town_pos 不正: {town_pos}")
                failed = True
                continue

            print(f"OK: {fixture_path.name} — v{snapshot['save_version']} ロード成功 (キー数: {len(player)})")

        except Exception:
            print(f"FAIL: {fixture_path.name} — 例外発生")
            traceback.print_exc()
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
