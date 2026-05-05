---
status: open
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:45:00+09:00
dateModified: 2026-05-05T17:45:00+09:00
tags:
  - task
  - framework-rule
  - m4-3
  - m4-4
  - game-state
  - cleanup
---

# 2026年5月5日 Game クラス state 7 件の段階移行（M4-3 圧縮）

> 状態：① Journey 略式
> 分離元：`steering/20260425-autonomous-rule-compliance-loop.md` 判断待ち「2026-04-25 18:25 — `src/runtime/app.py` Game クラス state 7 件（M4-3 段階移行未完）」

---

## 1) Journey

- **深層的目的**：`Game` クラスを「`pyxel.run` につなぐだけのランタイム殻」へ縮小する（framework-rule.md M4-3）
- **やらないこと**：
  - 1 PR で 7 件全部移動する（scope 過大、選択肢 (A) は却下）
  - 新規 SceneManager / DebugService / ViewportService / WorldGenerationService の同時設計

## 2) Gherkin

- `Game` クラスから 7 fields（`state`, `prev_state`, `debug_mode`, `debug_seq`, `cam_x`, `cam_y`, `dungeon_rooms`, `current_town`）が段階的に消える
- 各 field の参照箇所が新移送先（SceneManager / DebugService / ViewportService / WorldGenerationService cache / GameState.current_town）に書き換わる
- `pytest` が各サブタスクの commit 単位で green
- framework-rule.md M4-3「Game は最終的にランタイム殻にする」が実装に追いついている

## 3) Design

### 移送先マトリクス
| Field | 移送先 | 性質 |
|---|---|---|
| `state`, `prev_state` | `SceneManager`（新設） | scene 切替メタ |
| `debug_mode`, `debug_seq` | `DebugService`（新設） | 補助情報 |
| `cam_x`, `cam_y` | `ExploreModel` か `ViewportService`（新設） | 画面アニメ途中値 |
| `dungeon_rooms` | `WorldGenerationService` の結果 cache | 生成時の中間物 |
| `current_town` | 既に `GameState.current_town` あり、Game の field を撤去するだけ | 一時 UI 状態 |

### 進め方（5 ループ案 = 選択肢 B）
- ループ1: `current_town` 撤去（Game field 削除、参照を `game_state.current_town` に統一）
- ループ2: `cam_x` / `cam_y` を `ExploreModel` か `ViewportService` へ
- ループ3: `state` / `prev_state` を `SceneManager` へ
- ループ4: `debug_mode` / `debug_seq` を `DebugService` へ
- ループ5: `dungeon_rooms` を `WorldGenerationService` cache へ

### 影響範囲計測（先行）
各ループ着手前に `grep -rn 'game\.<field>\|self\.<field>' src/` で参照箇所数を測り、scope を確定

### 委任度
🟡 中：1 ループあたり 1〜2 ファイル新設＋複数参照書換。ユーザー確認は新規 service の責務粒度

## 4) Tasklist

（着手時にループ別に詳細化）

## 5) Result / 6) Discussion

（着手時に追記）
