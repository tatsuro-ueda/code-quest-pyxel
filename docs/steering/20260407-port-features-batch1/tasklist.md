# Batch1 (#1-#11) Implementation Plan

> **For agentic workers:** Use TDD. Each task: write test → run (red) → implement → run (green) → commit. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** JS版 (`/home/exedev/game/index.html`) の game data と関連機能を Pyxel版へ移植する。データは `assets/*.yaml` として外部化し、ローダ経由で読む。

**Architecture:**
- 既存 `src/simple_yaml.py` の `safe_load` を流用してYAMLを読む
- 新規 `src/game_data.py` が各種データの load 関数を提供する
- 新規 `src/player_factory.py` が初期プレイヤー生成を担う
- 既存 `main.py` のハードコードデータを段階的に load 関数呼び出しに置換する

**Tech Stack:** Python 3.12 / Pyxel 2.8.10 / pytest 8.x / 既存 simple_yaml

**Reference:** JS版の正解実装は `/home/exedev/game/index.html` 行番号で参照する。

---

## File Structure

新規/変更ファイル一覧:

- **新規**: `src/game_data.py` — 全YAMLローダ
- **新規**: `src/player_factory.py` — `create_initial_player`, `reset_game_state`, `stats_for_level`, `exp_for_level`
- **新規**: `assets/enemies.yaml` — JS `ENEMIES` 相当
- **新規**: `assets/items.yaml` — JS `ITEMS` 相当
- **新規**: `assets/weapons.yaml` — JS `WEAPONS` 相当
- **新規**: `assets/armors.yaml` — JS `ARMORS` 相当
- **新規**: `assets/spells.yaml` — JS `SPELLS` 相当
- **新規**: `assets/shops.yaml` — JS `SHOPS` + `INN_PRICES` 相当
- **新規**: `test/test_game_data.py`
- **新規**: `test/test_player_factory.py`
- **変更**: `main.py` — ハードコード除去、ローダ呼び出し、ショップ・魔法・多段ボス・ランドマーク追加

---

## Task #1: YAMLローダ＋データスキーマ実装

**Files:**
- Create: `src/game_data.py`
- Create: `test/test_game_data.py`
- Create: `assets/_smoke.yaml`（後続テスト用ダミー）

- [ ] **#1.1** `test/test_game_data.py` を作成し、`load_yaml(path)` がdictを返すことを最低限テスト
- [ ] **#1.2** `src/game_data.py` に `load_yaml(path)` を実装（`simple_yaml.safe_load` 経由）
- [ ] **#1.3** `pytest test/test_game_data.py -v` がパス
- [ ] **#1.4** ASSETS_DIR 定数と `_load(name)` ヘルパ追加
- [ ] **#1.5** `load_enemies/load_items/load_weapons/load_armors/load_spells/load_shops` のスタブ追加（後続タスクで中身を埋める）
- [ ] **#1.6** Commit: `feat: add game_data YAML loader skeleton`

---

## Task #2: 敵データを `assets/enemies.yaml` に移植

JS参照: `/home/exedev/game/index.html` 行737-769（`const ENEMIES`）

YAML スキーマ:

```yaml
- name: 10ほスライム
  sprite: slime
  hp: 8
  atk: 4
  def: 2
  agi: 3
  exp: 5
  gold: 10
  zone: 0
  category: sequential
  spells: []
  desc: 「10ほうごかす」が暴走中！
```

ボス系の追加キー: `is_boss: true`, `is_professor: true`, `post_clear_only: true`

- [ ] **#2.1** `assets/enemies.yaml` を作成しJSの12種を全部転記
- [ ] **#2.2** `test/test_game_data.py` に `test_load_enemies_returns_12_with_required_keys` を追加（件数=12, 必須キー存在）
- [ ] **#2.3** `src/game_data.py:load_enemies()` 実装
- [ ] **#2.4** pytest パス
- [ ] **#2.5** `main.py` の `ZONE_ENEMIES`/`BOSS_DATA` を `load_enemies()` から zone別に再構築するコードに置換
- [ ] **#2.6** 既存56テスト + 新テストが全部パス
- [ ] **#2.7** Commit: `feat: externalize enemy data to assets/enemies.yaml (12 enemies)`

---

## Task #3: 武器・防具を YAML 化

JS参照: `/home/exedev/game/index.html` 行717-735（`const WEAPONS` / `const ARMORS`）

YAML スキーマ:

```yaml
# weapons.yaml
- name: マウス
  atk: 2
  price: 10
  buy_msg: マウスを手に入れた。クリックで世界が動く。
```

- [ ] **#3.1** `assets/weapons.yaml` 作成（7種、JSのまま）
- [ ] **#3.2** `assets/armors.yaml` 作成（7種、JSのまま）
- [ ] **#3.3** test: `test_load_weapons_returns_7` / `test_load_armors_returns_7`
- [ ] **#3.4** `load_weapons() / load_armors()` 実装
- [ ] **#3.5** `main.py` の `WEAPONS / ARMORS` リテラル削除、`load_weapons() / load_armors()` を `Game.__init__` で呼び出して保持
- [ ] **#3.6** 「素手」「普段着」相当の素武器エントリは weapons.yaml/armors.yaml の先頭に保持（既存装備インデックスを壊さないため）
- [ ] **#3.7** pytest 全パス
- [ ] **#3.8** Commit: `feat: externalize weapons/armors to YAML (7 each + base)`

---

## Task #4: アイテム YAML 化＋効果ロジック

JS参照: 行710-715

YAML スキーマ:

```yaml
- name: バグレポート
  type: heal
  value: 30
  price: 1
  desc: HPを30回復
```

types: `heal`, `mp_heal`, `cure_poison`, `warp`

- [ ] **#4.1** `assets/items.yaml` 作成（JS 4種）
- [ ] **#4.2** test: `test_load_items_returns_4_with_types`
- [ ] **#4.3** `load_items()` 実装
- [ ] **#4.4** `main.py` の `ITEMS` リテラル削除、`load_items()` で初期化
- [ ] **#4.5** `_use_item(item_data)` ヘルパを `Game` に追加（heal/mp_heal/cure_poison/warp 分岐）
- [ ] **#4.6** 戦闘の `update_battle` の item_select 分岐を `_use_item` 呼び出しに統一
- [ ] **#4.7** メニューの items 分岐も `_use_item` に統一
- [ ] **#4.8** 毒状態 `player["poisoned"]` の継続ダメージを `update_map` で適用（数歩ごとに HP -2）
- [ ] **#4.9** test: `test_use_item_heal` / `test_use_item_cure_poison` / `test_use_item_warp`
- [ ] **#4.10** Commit: `feat: externalize items to YAML and add cure_poison/warp effects`

---

## Task #5: EXPテーブル / `stats_for_level` 実装

> **方針**: 純粋関数として `src/player_factory.py` に置く。係数だけ `assets/level_curve.yaml` に外出ししてもよいが、初回は関数で十分。

- [ ] **#5.1** `src/player_factory.py` 新規作成
- [ ] **#5.2** `MAX_LEVEL = 100`, `exp_for_level(lv)`, `stats_for_level(lv)` を JS式そのまま実装
- [ ] **#5.3** `test/test_player_factory.py` に test_exp_for_level (lv2=26, lv3=58 など), test_stats_for_level (lv1の値を確認)
- [ ] **#5.4** `Game._check_level_up` を `exp_for_level` 呼び出しに置換し、ステータス更新を `stats_for_level` に基づくものへ置換（既存ロジックがあればそれを比較）
- [ ] **#5.5** pytest 全パス
- [ ] **#5.6** Commit: `feat: add player_factory with exp_for_level and stats_for_level`

---

## Task #6: `create_initial_player / reset_game_state` リファクタ

- [ ] **#6.1** `src/player_factory.py` に `create_initial_player()` 追加（`Game.__init__` のリテラルを抽出、初期 stats は `stats_for_level(1)` を使う）
- [ ] **#6.2** test: `test_create_initial_player_has_required_keys` / `test_initial_stats_match_level_1`
- [ ] **#6.3** `Game.__init__` でリテラルの代わりに `create_initial_player()` を呼ぶ
- [ ] **#6.4** `reset_game_state(self)` を `Game` メソッドとして切り出す（タイトルから「はじめから」選択時に呼ぶ）
- [ ] **#6.5** pytest 全パス（既存56本＋追加分）
- [ ] **#6.6** Commit: `refactor: extract create_initial_player and reset_game_state`

---

## Task #7: ショップ実装

JS参照: 行782-786（`const SHOPS`）, `tryPurchase`, `drawShop`, `processTownInput` のショップ関連分岐

YAML スキーマ:

```yaml
shops:
  - town: はじめの村
    items: [0, 2, 3]
    weapons: [0, 1]
    armors: [0, 1]
inn_prices: [5, 15, 40]
```

- [ ] **#7.1** `assets/shops.yaml` 作成（3町分＋宿代）
- [ ] **#7.2** test: `test_load_shops_returns_3_towns`
- [ ] **#7.3** `load_shops()` 実装（戻り値: `{"shops": [...], "inn_prices": [...]}`)
- [ ] **#7.4** `main.py` の `INN_COST` を町別 `inn_prices` に置換
- [ ] **#7.5** 町メニューに「ぶきや」「ぼうぐや」「どうぐや」を追加（ラベルだけ先に）
- [ ] **#7.6** `update_shop()` 実装: ショップ種別×カーソル×購入・キャンセル
- [ ] **#7.7** `draw_shop()` 実装: 在庫リスト＋価格＋所持gold＋現在装備
- [ ] **#7.8** 購入処理: gold チェック→不足ならエラーメッセージ→十分なら gold-= price, 装備更新 or items追加
- [ ] **#7.9** `SHOP_WIP_MSG` 削除
- [ ] **#7.10** test: `test_purchase_weapon_deducts_gold_and_equips` / `test_purchase_fail_insufficient_gold`
- [ ] **#7.11** Commit: `feat: implement weapon/armor/item shops`

---

## Task #8: 魔法システム

JS参照: 行702-708（`const SPELLS`）, `applySpellEffect`, `useSelectedMenuSpell`

YAML スキーマ:

```yaml
- name: デバッグ
  mp: 6
  type: heal
  power: 60
  desc: バグを修正しHP60回復
  learn_lv: 3
```

- [ ] **#8.1** `assets/spells.yaml` 作成（JS 5呪文）
- [ ] **#8.2** test: `test_load_spells_returns_5_with_required_keys`
- [ ] **#8.3** `load_spells()` 実装
- [ ] **#8.4** `_check_level_up` で `learn_lv` を満たした呪文を `player["spells"]` に追加
- [ ] **#8.5** test: `test_level_up_learns_spell_at_correct_level`
- [ ] **#8.6** 戦闘メニューに「じゅもん」項目を追加（`menu` フェーズに spell select を1つ加える）
- [ ] **#8.7** spell_select フェーズ実装: 上下で呪文選択、決定で `_apply_spell_effect`
- [ ] **#8.8** `_apply_spell_effect(spell, target)`: heal なら HP回復、attack なら enemy_hp 減算
- [ ] **#8.9** MP不足ならエラーメッセージ
- [ ] **#8.10** フィールドメニューにも「じゅもん」タブ追加（heal系のみ）
- [ ] **#8.11** test: `test_apply_spell_heal_recovers_hp` / `test_apply_spell_attack_damages_enemy`
- [ ] **#8.12** Commit: `feat: implement 5-spell system with level-based learning`

---

## Task #9: 多段階ボス

JS参照: `getBossPhases` 関数

`getBossPhases` の典型: HP > 60% → phase1, 30% < HP ≤ 60% → phase2, ≤ 30% → phase3, それぞれフェーズ移行時に専用メッセージ。

- [ ] **#9.1** `src/game_data.py` に `boss_phase(enemy_data, hp_ratio) -> str` を追加（ラベルだけ返す）
- [ ] **#9.2** test: `test_boss_phase_thresholds`（4境界）
- [ ] **#9.3** 敵 YAML に `phases:` キー（任意）を追加し、ボス3体に phase ラベル＋メッセージを設定
- [ ] **#9.4** `Game.update_battle` で HP変化時に phase 移行を検知し、メッセージを差し込む
- [ ] **#9.5** test: `test_boss_phase_transition_inserts_message`
- [ ] **#9.6** Commit: `feat: add multi-phase boss behavior`

---

## Task #10: 世界樹インタラクション

JS参照: `interactWorldTree`（行1550付近）

- [ ] **#10.1** JS `interactWorldTree` を読んで挙動を要約
- [ ] **#10.2** 世界樹の座標を `main.py` に定数として追加（JS と一致させる）
- [ ] **#10.3** `_check_landmark_events` に世界樹分岐を追加
- [ ] **#10.4** 専用ダイアログを `assets/dialogue.yaml` の `landmark.tree.first` / `landmark.tree.repeat` に追加
- [ ] **#10.5** `player["landmarkTreeSeen"]` を立てる
- [ ] **#10.6** test: `test_world_tree_first_visit_sets_flag` / `test_world_tree_repeat_uses_short_message`
- [ ] **#10.7** Commit: `feat: add world tree interaction`

---

## Task #11: 通信塔インタラクション + 塔エピローグ

JS参照: `interactTower` (行1605), `queueTowerEpilogue` (行1620)

- [ ] **#11.1** JS の挙動を要約（条件分岐＋エピローグキュー）
- [ ] **#11.2** 通信塔座標を `main.py` 定数化
- [ ] **#11.3** `_check_landmark_events` に塔分岐を追加
- [ ] **#11.4** 専用ダイアログを `dialogue.yaml` に `landmark.tower.first` / `landmark.tower.epilogue`
- [ ] **#11.5** `player["landmarkTowerSeen"]` を立てる
- [ ] **#11.6** クリア後 (`boss_defeated`) のエピローグ起動条件を実装
- [ ] **#11.7** test: `test_tower_first_visit_sets_flag` / `test_tower_epilogue_after_boss`
- [ ] **#11.8** Commit: `feat: add signal tower interaction with post-clear epilogue`

---

## Final Verification

- [ ] **#F.1** `pytest test/ -q` 全パス
- [ ] **#F.2** `python -c "import ast; ast.parse(open('main.py').read())"` パス
- [ ] **#F.3** todolist.md の #1〜#11 を ✅ にマーク
- [ ] **#F.4** Push to origin

---

## Notes for the executor

- JS版 `/home/exedev/game/index.html` は `Read` ツールで該当行を読みながら正確に転記する
- YAML はインデント2スペース固定、リスト先頭は `- ` を使う（`src/simple_yaml.py` の制約に注意）
- 既存テスト 56本 + 2 subtests を壊さないこと
- 各タスク終了時に commit して push しない（最後にまとめて push）
- 失敗テストが出たらその場で原因調査・修正してから次へ
