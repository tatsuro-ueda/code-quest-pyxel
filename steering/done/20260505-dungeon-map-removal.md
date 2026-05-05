---
status: done
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:30:00+09:00
dateModified: 2026-05-05T17:30:00+09:00
tags:
  - task
  - ssot
  - dungeon
  - cleanup
  - archived
---

# 2026年5月5日 game.dungeon_map / GameState.dungeon_map 撤去

> 状態：① Journey 略式（フォロータスク起票のみ）

## 1) Journey

- **深層的目的**：状況をシンプルにして好循環を起こしたい

1. 💦 （開発者・AI）ダンジョンに関する機能を追加したりバグ修正したい（コードエディタ）
2. 💦 （開発者・AI）リポジトリを眺める（コードエディタ）
3. Before
  1. ❌ もう使っていないファイルや関数が残っている（コードエディタ）
  2. ❌ （開発者・AI）わかりにくい
4. After
  1. ✅ もう使っていないファイルや関数が残っていない（コードエディタ）
  1. ✅ すべてImageBankに移行済み（コードエディタ）
  1. ✅ 状況がシンプル（コードエディタ）
  2. ♥️ （開発者・AI）嬉しい

## 2) Gherkin

> **方針変更（2026-05-05）**：dungeon の Pyxel Code Maker 編集対応も本タスクに含める。world_map と対称に「pyxres を SSoT」「ExploreModel が tilemap[0] dungeon 領域を直読」「fallback bake は不在/破損時のみ」とする。

### シナリオ1：使っていない field の仕込みが src/ から消える
> 🧱 Given: 改修後の src/。`runtime/app.py:79` の `self.dungeon_map = None` 初期化と、title / ending / explore 3 シーンの `game.dungeon_map = None / [...]` 代入が撤去されている。🎬 When: `grep -rnE 'game\.dungeon_map\|self\.dungeon_map' src/ --include='*.py'` を実行。✅ Then: マッチ 0 件。読んだ開発者・AI が「dungeon 状態は別の場所にある」と誤認しなくなる。

### シナリオ2：GameState から dungeon_map フィールドが消える
> 🧱 Given: 改修後の `src/shared/services/game_state.py`。🎬 When: `dungeon_map` を grep。✅ Then: マッチ 0 件。GameState 目標形（framework-rule.md M4-3 改訂版）に揃う。

### シナリオ3：dungeon の tile 読み取りが ImageBank 直読に一本化される
> 🧱 Given: 改修後の Explore シーン。🎬 When: 子どもがダンジョン内を移動して描画／衝突判定が走る。✅ Then: `ExploreModel.get_tile(x, y, in_dungeon=True)` が `pyxel.tilemaps[0].pget` の Y オフセット領域 (`DUNGEON_TM_OFFSET_Y`) を読み、`image_banks.tile_id_by_pixel` で tile id を解決する経路だけで完結する。`shared/state` や `game.*` から dungeon タイル配列を読み取る経路は存在しない（Journey After「すべて ImageBank に移行済み」と整合）。

### シナリオ4：dungeon の入退出フローが `in_dungeon` フラグだけで完結する
> 🧱 Given: 改修後の repo。🎬 When: 子どもが洞窟に入る → ダンジョン内を歩く → 階段で脱出する → エンディング to dungeon 不在 になる、の一連を fake game で辿る。✅ Then: 各遷移で `player_model.in_dungeon` の True/False の切替と `dungeon_spawn` への直接アクセスだけで成立する。`game.dungeon_map` への代入が一度も発生しない。pytest が green。

### シナリオ5：Code Maker でダンジョンタイルを編集すると即反映される
> 🧱 Given: 子どもが Pyxel Code Maker のタイルマップエディタを開き、tilemap[0] の dungeon 領域（Y オフセット ≥ `DUNGEON_TM_OFFSET_Y` * 8 px）にあるタイルを書き換えて pyxres を保存する。🎬 When: Code Maker から Run する。✅ Then: ゲーム内のダンジョンを再訪問すると編集後のタイルがそのまま表示される。world_map と同様、「Code Maker で編集 → 即反映」が成立する（PRD-map CJG01 / CJG02 / 共通条件と整合）。

### シナリオ6：`bake_dungeon_to_tilemap` が「pyxres 不在/破損時の fallback 専用」に改訂される
> 🧱 Given: 改修後の `src/shared/services/image_banks.py`。🎬 When: `setup_world_tilemap` 経由でゲーム起動する。✅ Then: pyxres **読み込み済み** のときは `bake_dungeon_to_tilemap` が早期 return（no-op）になり、Code Maker で編集した dungeon tilemap を上書きしない。pyxres **不在/破損** のときだけ procedural に生成して tilemap[0] の dungeon 領域に焼き、`pyxel.save` で初回 pyxres を作る。`world_map` の `regenerate_world_tilemap_fallback`（仮）と対称な命名・挙動になっている。

### シナリオ7：dungeon 編集面が真実である（PRD-map 共通条件）
> 🧱 Given: 子どもが Code Maker で dungeon 領域のタイルを編集した。🎬 When: ゲーム起動して同じ場所を訪れる。✅ Then: ゲーム内の表示が編集面と一致する。実行時の procedural 上書きは発生しない（dungeon 編集面 = ゲーム世界の真実、`world_map` と同じ約束）。

### シナリオ8：再侵入を防ぐ静的ガード
> 🧱 Given: 改修完了後、将来的に新規コードで `game.dungeon_map` を復活させる懸念。🎬 When: `test_cjg_framework_rule_guards.py` に「src/ 配下に `game\.dungeon_map\|self\.dungeon_map` が侵入していないこと」を assert する grep ガードを 1 件追加する。✅ Then: 古いパターンの再侵入が pytest で即 fail。Journey After「状況がシンプル」が将来も保たれる。

### シナリオ9：既存テストへの影響は別タスクで吸収
> 🧱 Given: `test_dungeon_boss_trigger.py` 等が `game.dungeon_map = [[T_FLOOR]]` を仕込む箇所あり。🎬 When: 本タスク commit 直後の pytest。✅ Then: 動的属性として代入が通り pytest は green を維持する。test 群の物理書き換えは別タスク `20260505-rewrite-tests-for-imagebank-ssot.md` のスコープ。本タスクは「runtime が読まなくする」+「Code Maker 編集が即反映される」までを担当。

## 3) Design

### 事前計測（2026-05-05 grep 実測値）

| 対象 | 場所 | 件数 |
|---|---|---|
| `(game\|self)\.dungeon_map` 参照 | app.py:79, title/presenter.py:78, ending/presenter.py:21, explore/presenter.py:100,116,164 | **6 箇所** |
| `GameState.dungeon_map` field | `game_state.py:37 dungeon_map: list \| None = None` | 1 件 |
| `DUNGEON_TM_OFFSET_Y` | `image_banks.py:22 = 110`（**cell 単位**、`* 8` で px 換算） | 確定 |
| `dungeon_spawn` 所在 | `GameState.dungeon_spawn: tuple[int,int] \| None`（既存） | 既に GameState 上 |
| `dungeon_template` / `dungeon_template_rooms` | GameState（既存）+ `image_banks.bake/derive_dungeon_from_tilemap` が読み書き | Service 内部のみで完結（runtime/scene からの直読は無し） |
| `dungeon_rooms` | `app.py:80`、`explore/presenter.py:165` | **本タスクの対象外**。`game-class-shrink-m43.md` ループ5 で扱う |
| pyxres ロード済みフラグ | `image_banks.pyxres_loaded`（既存） | 流用 |
| dungeon 生成関数 | `src/shared/services/world_generation.py:223 def generate_dungeon(seed=99)` | fallback 内で直呼び可能 |

### runtime 改修内訳

| # | ファイル:行 | 変更前 | 変更後 |
|---|---|---|---|
| 1 | `runtime/app.py:79` | `self.dungeon_map = None` | **削除** |
| 2 | `scenes/title/presenter.py:78` | `game.dungeon_map = None` | **削除** |
| 3 | `scenes/ending/presenter.py:21` | `game.dungeon_map = None` | **削除** |
| 4 | `scenes/explore/presenter.py:100` | `game.dungeon_map = None`（dungeon edge exit） | **削除**（同行のみ、付随 messages.enter は残置） |
| 5 | `scenes/explore/presenter.py:116` | `game.dungeon_map = None`（stair_up exit） | **削除**（同上） |
| 6 | `scenes/explore/presenter.py:164` | `game.dungeon_map = [row[:] for row in game.dungeon_template]`（cave entry） | **削除**（in_dungeon フラグ + dungeon_spawn だけで完結） |
| 7 | `game_state.py:37` | `dungeon_map: list \| None = None` | **削除** |

### Code Maker 編集対応（world_map と対称化）

| # | 対象 | 変更 |
|---|---|---|
| 8 | `image_banks.py:184 def bake_dungeon_to_tilemap(self):` | **`def regenerate_dungeon_tilemap_fallback(self):`** にリネーム |
| 9 | 関数内 `dg = game.dungeon_template` | `dg = generate_dungeon()` 直呼び（game.dungeon_template に依存しない 1 次生成） |
| 10 | `image_banks.py:setup_world_tilemap` 内呼び出し | 旧名 → 新名に置換。**`if self.pyxres_loaded` 分岐の中では呼ばない**（既に world 側と同じ構造）。pyxres 不在経路でだけ fallback 呼び出し |
| 11 | `derive_dungeon_from_tilemap`（既存）| **据え置き**（pyxres ロード済み時に tilemap[0] dungeon 領域 → `game.dungeon_template` 復元、これは dungeon_template の所在を Service 内部に閉じる方針と整合） |

### `dungeon_template` の所在ポリシー（曖昧点解消）

- **GameState.dungeon_template に持つが、scene/runtime からは直読しない**（読むのは `image_banks.regenerate_dungeon_tilemap_fallback` / `derive_dungeon_from_tilemap` の Service 内部のみ）
- `bake_dungeon_to_tilemap` を fallback 専用にしたあとは、**`game.dungeon_template` は derive 側でのみ更新**される（pyxres 経路のみ）
- 「`dungeon_template` の Service 外読み取り」を防ぐ static guard はオーバーキル。本タスクではガード追加せず、`dungeon_map` 再侵入ガード（シナリオ8）のみ追加

### test 影響（GameState frozen 前提）

- `GameState` は `@dataclass`（既定 `frozen=False`）。**動的属性代入は通る**ため、test の `game.dungeon_map = ...` セットアップは field 削除後も silent に通る（attribute は dataclass 外で生える）
- ただし test 側の **読み取り** が `game.dungeon_map` を参照していたら、削除後も None ではなく古い仕込みが返るため検証観点が壊れる可能性がある → 着手時に test 側の読み取り箇所を grep して確認（書き換えは別タスク `rewrite-tests-for-imagebank-ssot.md` のスコープ）

### commit 戦略（3 commit、revert 独立）

1. **A**: `feat(ssot): bake_dungeon_to_tilemap を fallback 専用に改訂（Code Maker 編集即反映）`
   - 改修内訳 #8〜#10。pyxres ロード済み経路で dungeon tilemap が procedural 上書きされなくなる
2. **B**: `refactor(ssot): drop dungeon_map snapshot, in_dungeon フラグだけで完結`
   - 改修内訳 #1〜#7。6 箇所撤去 + GameState.dungeon_map field 削除
3. **C**: `test(framework-rule): src/ 配下 (game|self).dungeon_map 再侵入を防ぐ static guard`
   - `test_cjg_framework_rule_guards.py` に 1 ケース追加

### 関連スキル・MCP
- 標準ツール：Bash / Edit / Grep / pytest

### 委任度
🟡 中：撤去対象は機械的だが、commit B の前に test 側の `game.dungeon_map` **読み取り** 箇所を grep して silent fail を回避する必要あり（書き換えは別タスク委譲、本タスクでは Discussion に件数を記録）。Code Maker 経路の手動検証は `pyxel pyxapp` 実機 or `tools/probe_codemaker_layout.py` で確認。

## 4) Tasklist

### commit A: bake_dungeon_to_tilemap を fallback 専用に改訂
- [ ] `src/shared/services/image_banks.py:184` `def bake_dungeon_to_tilemap` → `def regenerate_dungeon_tilemap_fallback` リネーム
- [ ] 同関数内 `dg = game.dungeon_template` → `dg = generate_dungeon()` 直呼びに置換（import 追加：`from src.shared.services.world_generation import generate_dungeon`）
- [ ] 関数冒頭に防衛的早期 return：`if self.pyxres_loaded: return`
- [ ] `setup_world_tilemap` 内 `self.bake_dungeon_to_tilemap()` 2 箇所を新名に置換
- [ ] `pytest -q` 全 green
- [ ] commit `feat(ssot): bake_dungeon_to_tilemap を fallback 専用に改訂（Code Maker 編集即反映）`

### commit B: dungeon_map snapshot 撤去
- [ ] `src/runtime/app.py:79` `self.dungeon_map = None` 削除
- [ ] `src/scenes/title/presenter.py:78` `game.dungeon_map = None` 削除
- [ ] `src/scenes/ending/presenter.py:21` `game.dungeon_map = None` 削除
- [ ] `src/scenes/explore/presenter.py:100` `game.dungeon_map = None` 削除（messages.enter は残置）
- [ ] `src/scenes/explore/presenter.py:116` `game.dungeon_map = None` 削除（同上）
- [ ] `src/scenes/explore/presenter.py:164` `game.dungeon_map = [row[:] for row in game.dungeon_template]` 削除（in_dungeon フラグ + dungeon_spawn だけで完結）
- [ ] `src/shared/services/game_state.py:37` `dungeon_map: list | None = None` 削除
- [ ] `_dungeon_exit_callback` 内部に `game.dungeon_map` 読み取りが残っていないか grep
- [ ] test 側 `game.dungeon_map` 読み取り箇所を grep して件数を Discussion に記録（書き換えは別タスク）
- [ ] `pytest -q` 全 green（dataclass 外動的代入で test 仕込みは silent に通る前提）
- [ ] commit `refactor(ssot): drop dungeon_map snapshot, in_dungeon フラグだけで完結`

### commit C: 再侵入ガード
- [ ] `test/test_cjg_framework_rule_guards.py` に「`src/` 配下に `(game|self)\.dungeon_map\b` が侵入していないこと」を assert する 1 ケース追加
- [ ] `pytest -q test/test_cjg_framework_rule_guards.py` green
- [ ] commit `test(framework-rule): dungeon_map 再侵入を防ぐ static guard 追加`

### 仕上げ
- [ ] tasknote status `done`、`archived` タグ追加、`steering/done/` へ移動
- [ ] bundle 再ビルド（`pyxel package`）が必要かを判定、必要なら再ビルド commit

## 5) Result / 6) Discussion

（着手時に追記）
