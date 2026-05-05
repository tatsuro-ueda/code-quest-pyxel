---
status: open
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:45:00+09:00
dateModified: 2026-05-05T17:45:00+09:00
tags:
  - task
  - framework-rule
  - m4-4
  - player-model
  - cleanup
---

# 2026年5月5日 player_state.py 旧 API shim 群の撤去（M4-4 完成）

> 状態：① Journey 略式
> 分離元：`steering/20260425-autonomous-rule-compliance-loop.md` 判断待ち「2026-04-25 17:55 — `src/shared/services/player_state.py` 旧 API shim 群（M4-4 段階移行未完）」

---

## 1) Journey

- **深層的目的**：`PlayerModel` 化（framework-rule.md M4-4 Level 2）の最終段として、`player_state.py` 残存 shim 5 関数を撤去 or PlayerModel メソッド化する
- **やらないこと**：
  - bundle / セーブ互換性の破壊（`from_snapshot` の互換は維持）
  - `tools/test_save_compat.py` の独自再現関数の書き換え（別物）

## 2) Gherkin

- `src/shared/services/player_state.py` から `restore_snapshot` / `create_initial_player` / `dump_snapshot` / `player_model_to_dict` が消える、または PlayerModel のメソッドへ吸収される
- `stats_for_level` は `PlayerModel.stats_for_level` 等のクラスメソッド化
- `test_player_snapshot.py` 5 ケースが `PlayerModel.from_snapshot` ベースに書き換わる
- `test_architecture_layout.py` の `hasattr(M, "restore_snapshot")` assert が新仕様に合わせて更新
- bundle 内 `main_runtime` の再エクスポート確認、save 互換維持
- pytest 全 green

## 3) Design

### 残存 shim
1. `stats_for_level(lv)` — PlayerModel 内部から利用 → クラスメソッド化が筋
2. `create_initial_player(start_x, start_y)` — `PlayerModel.new_game(...)` shim → 直呼びに置換
3. `dump_snapshot(player: dict, town_pos)` — dict 引数の旧 API → 削除候補
4. `restore_snapshot(snapshot)` — test_player_snapshot 5 ケース + architecture_layout 1 件で利用 → test 書換 + 削除
5. `player_model_to_dict(pm)` — PlayerModel → dict 変換 shim → 削除候補

### 進め方（選択肢 A + B 折衷）
- ループ1: `stats_for_level` を PlayerModel.stats_for_level に移動（M4-4 Level 2 の本筋）
- ループ2: `restore_snapshot` 経由の test 5 ケースを `PlayerModel.from_snapshot` 直呼びに書換
- ループ3: 残 shim 4 関数を削除、`hasattr` assert を更新

### 影響確認の事前タスク
- bundle で `main_runtime` が `restore_snapshot` を再エクスポートしているか grep 確認
- セーブファイル互換性は `PlayerModel.from_snapshot` で吸収されているはずだが念のため `tools/test_save_compat.py` で実機検証

### 委任度
🟢 高：test の書換が中心、ロジック変更は薄い。bundle 検証は必須

## 4) Tasklist

（着手時にループ別に詳細化）

## 5) Result / 6) Discussion

（着手時に追記）
