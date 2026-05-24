---
source: raw/tasknotes/steering/done/20260413-j38-dungeon-boss-trigger.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月13日 J38 ダンジョン最奥でボス戦が始まるようにする Summary Draft

## summary

この tasknote は、ダンジョン最奥まで進んでも `BOSS_DATA` に遭遇できない幽霊状態を解消するために、最奥部屋へ explicit boss trigger を置いた記録です。中心は `zone` や通常エンカウントを広くいじらず、`generate_dungeon()` と `_check_tile_events()` と `draw_map()` の 3 点で終点イベントを成立させたことでした。

## key_points

- 問題の本体はボスデータ不足ではなく、最奥到達をボス戦へ変換する接続が欠けていたことだった。
- 方針は `zone 5` 化やランダム遭遇追加ではなく、最奥部屋に 1 つだけ置く explicit trigger だった。
- `main.py` に `T_BOSS_TRIGGER` を追加し、`generate_dungeon()` で `rooms[-1]` の代表マスへ配置した。
- `Game._check_tile_events()` は、`boss_defeated=False` のときだけ `_start_battle(BOSS_DATA, is_boss=True)` を呼ぶようになった。
- `draw_map()` には主人公スプライトを使う目印キャラを重ね、子どもが終点を見た目で見つけやすくした。
- `test/test_dungeon_boss_trigger.py` で配置、起動、再発火防止、目印の表示 / 非表示まで固定した。

## important_quotes

- "遭遇導線がない"
- "ボスはランダム遭遇ではなく、ダンジョン最奥の部屋に置く明示トリガーとして扱う"
- "主人公と同じ見た目の目印で終点が見て分かる"

## open_questions

- `python tools/test_headless.py` の補助検証を audio / Pyxel 制約のない環境で再確認するか。
- ボス撃破後の追加演出や報酬拡張を別タスクで切り出すか。
- 目印キャラの仮実装を将来 resource 側の専用表現へ寄せるか。
