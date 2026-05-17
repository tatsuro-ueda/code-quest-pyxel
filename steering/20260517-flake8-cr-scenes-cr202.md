---
status: open
priority: normal
scheduled: 2026-05-17T00:00:00.000+09:00
dateCreated: 2026-05-17T00:00:00.000+09:00
dateModified: 2026-05-17T00:00:00.000+09:00
tags:
  - task
  - lint
  - scenes
---

# 2026年5月17日 src/scenes の CR202（関数 20 行超）残課題を片付ける

> 状態：① Journey
> 次のゲート：（ユーザー）Journey を確認して承認するか直しの希望を伝える

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 src/scenes のすべての関数を 20 行以下に保ち、責務が読み取れる単位まで分割する
> 補足：やらないこと 挙動を変える書き換え、他種別の警告対応
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 `steering/20260517-flake8-cr-scenes.md` で CR202 以外のすべての警告は解消済み
   2. 💦 残 30 件はすべて関数 20 行超（CR202）で、リファクタが必要

2. Before
   1. 💦 大きい関数（30〜90 行）が `_check_tile_events` / `_run_build_view_model` / `_run_update` などに残る
   2. ❌ もどかしい

3. After
   1. ✅ `flake8-cr src/scenes/` が 0 件
   2. ✅ pytest / make verify / make build がすべて緑
   3. ❤️ スッキリ

4. 例外
   1. 線形なロジック（プレイヤー攻撃計算など）で分割が不自然になる場合は別途相談する

5. 境界条件
   1. 修正対象は CR202 のみ
   2. 挙動は変えない（テスト緑を維持）

6. 委任度
   1. 🟡 全体としては一部判断要（分割境界の判断は人と擦り合わせる）
   2. 🟢 dispatch dict / 早期 return への変換は CC のみで可
   3. 🔴 ロジックの本質を変える分割は人の判断が要る

---

## 2) ユーザーストーリーマップ

（Journey 承認後に記入）

---

## 3) Gherkin（完了条件）

（USM 承認後に記入）

---

## 4) Design（どうやるか）

（Gherkin 承認後に記入）

---

## 5) Tasklist

（Design 承認後に記入）

---

## 6) Result（成果物）

### 残対象（30 件）

| ファイル | 関数 | 行数 |
|---|---|---|
| `src/scenes/battle/presenter.py` | `_build_full_view_model` | 27 |
| `src/scenes/battle/presenter.py` | `_handle_phase_menu` | 23 |
| `src/scenes/battle/presenter.py` | `_handle_phase_spell_select` | 32 |
| `src/scenes/battle/presenter.py` | `_handle_phase_item_select` | 40 |
| `src/scenes/battle/scene.py` | `_run_check_noise_guardian_phase` | 21 |
| `src/scenes/battle/scene.py` | `_run_do_player_attack` | 25 |
| `src/scenes/battle/scene.py` | `_run_check_glitch_lord_phase_transition` | 33 |
| `src/scenes/battle/scene.py` | `_run_do_enemy_attack` | 32 |
| `src/scenes/battle/scene.py` | `_run_apply_victory` | 25 |
| `src/scenes/battle/scene.py` | `_run_check_level_up` | 25 |
| `src/scenes/battle/view.py` | `_run_draw` | 72 |
| `src/scenes/explore/presenter.py` | `_run_update` | 79 |
| `src/scenes/explore/presenter.py` | `_run_build_view_model` | 89 |
| `src/scenes/explore/presenter.py` | `_check_tile_events` | 92 |
| `src/scenes/explore/presenter.py` | `_check_landmark_events` | 37 |
| `src/scenes/explore/presenter.py` | `_resolve_landmark_scene` | 40 |
| `src/scenes/explore/view.py` | `_run_draw` | 39 |
| `src/scenes/menu/presenter.py` | `_handle_sub_items` | 23 |
| `src/scenes/menu/presenter.py` | `_use_selected_item` | 27 |
| `src/scenes/menu/presenter.py` | `_build_items_panel` | 25 |
| `src/scenes/menu/view.py` | `_run_draw` | 26 |
| `src/scenes/professor/presenter.py` | `_run_update_intro` | 28 |
| `src/scenes/professor/presenter.py` | `_run_build_intro_view_model` | 31 |
| `src/scenes/shop/presenter.py` | `_run_update` | 27 |
| `src/scenes/shop/presenter.py` | `_run_try_purchase` | 36 |
| `src/scenes/shop/presenter.py` | `_run_build_view_model` | 43 |
| `src/scenes/title/presenter.py` | `_run_update` | 24 |
| `src/scenes/title/presenter.py` | `_run_build_view_model` | 26 |

---

## 7) Discussion（残課題の起票）

なし

---

## 8) 参考文献

- 親タスクノート: `steering/20260517-flake8-cr-scenes.md`
- 初回スキャン: `/tmp/flake8-cr-scenes-initial.txt`
