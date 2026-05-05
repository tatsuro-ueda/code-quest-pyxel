---
status: in-progress
priority: high
scheduled: 2026-05-05T17:30:00+09:00
dateCreated: 2026-05-05T17:30:00+09:00
dateModified: 2026-05-05T17:30:00+09:00
tags:
  - task
  - ssot
  - pyxres
  - imagebank
  - cleanup
---

# 2026年5月5日 imagebank 直読の中間スナップショット撤去（world_map / bake リネーム）

> 状態：③ Design 略式（前タスク `20260505-imagebank-as-scene-model.md` の Step 5/6 の縮小分を本タスクで実施）
> 次のゲート：実行 → done

---

## 1) Journey

- **深層的目的**：pyxres を SSoT、Model 直読を真の経路にし、中間スナップショットを物理撤去して「2 つの真実が並走」する状態を消す
- **方針変更（2026-05-05）**：本タスクに **world_map 関連の test 書き換えも含める**。「runtime 撤去 + test 書き換え」を 1 セットで完了させ、別タスク `20260505-rewrite-tests-for-imagebank-ssot.md` のスコープは「dungeon_map 系 test の書き換え + 共通 helper の整備」に縮小する
- **やらないこと**：
  - `game.dungeon_map` 撤去（→ 別タスク `20260505-dungeon-map-removal.md`）
  - dungeon_map 関連 test の書き換え（→ 別タスク `20260505-rewrite-tests-for-imagebank-ssot.md`）

1. 💦 （開発者・AI）機能を追加したりバグ修正したい（コードエディタ／AI 起動時 context）
2. 💦 （開発者・AI）どの規約文書を最初に読むか考える（コードエディタ／AI 起動時 context）
3. Before
  1. 💦 中間スナップショット等が残っている
  2. ❌ 見通しが悪い、修正しづらい
2. After
  1. ✅ 中間スナップショット等を物理撤去済み
  2. ✅ 見通しが良い、修正しやすい
  3. ♥️ 好循環が起きる

## 2) Gherkin

### シナリオ1：`game.world_map` が src 全域から消える
> 🧱 Given: 改修後の repo。🎬 When: `grep -nE 'game\.world_map\|self\.world_map' src/ -r --include='*.py'` を実行。✅ Then: マッチ 0 件。

### シナリオ2：`GameState.world_map` フィールドが消える
> 🧱 Given: 改修後の `src/shared/services/game_state.py`。🎬 When: `world_map` を grep。✅ Then: マッチ 0 件。

### シナリオ3：`bake_world_to_tilemap` の名称が「fallback 専用」に変わる
> 🧱 Given: 改修後の `src/shared/services/image_banks.py`。🎬 When: 関数定義を確認。✅ Then: 元の名前は消え、`regenerate_world_tilemap_fallback`（仮）等の「fallback 専用」を示す名称になっている。pyxres 不在 / load 失敗時の初回生成 + `pyxel.save` 経路は維持されている。

### シナリオ4：pyxres 不在 / 破損時の fallback が機能する
> 🧱 Given: pyxres ファイルが不在 or 破損。🎬 When: `setup_image_banks` 経由でゲーム起動。✅ Then: `regenerate_world_tilemap_fallback` が procedural に world を生成して tilemap[0] に焼き、`pyxel.save` で pyxres を作る（既存挙動の温存）。

### シナリオ5：world_map 関連 test が新仕様で書き換わる
> 🧱 Given: 改修前の test 群（`test_world_map_ssot.py`, `test_setup_world_tilemap_preserves_user_edits.py`, `test_world_map_contract.py`, `test_world_generation.py`, `test_tilemap_editor_truth.py`, `test_runtime_shim.py`, `test_architecture_layout.py`, `test_cj24_sound_editor_truth.py`, `test_cjg_ending_scene_behavior.py`, `test_cjg_title_scene_behavior.py`, `test_cjg_map_tile_transitions.py`, `test_cjg_town_entry_sets_current_town.py` など）が `game.world_map = [...]` を仕込んでいる。🎬 When: 各 test を新仕様（`pyxel.tilemaps[0].pget` モック + `image_banks.tile_id_by_pixel` 仕込み）に書き換える。✅ Then: pytest 全 green、`grep -rnE 'game\.world_map\s*=' test/` がマッチ 0 件、観点（assert の対象）は維持または強化。SKIP_TESTS=1 を使わず pre-commit hook を素直に通せる。

### シナリオ6：runtime 撤去と test 書き換えが時系列で整合する
> 🧱 Given: 本タスク内で「runtime 撤去」commit と「test 書き換え」commit の順序を扱う。🎬 When: 先に test を新仕様に書き換え（runtime 旧仕様でも green）、次に runtime を撤去する順で commit する。✅ Then: 各 commit が独立して green。「runtime 撤去 → test red → 別 commit で書き換え」のような中途 red を残さない。

### シナリオ7：再侵入を防ぐ静的ガード
> 🧱 Given: 改修完了後、将来「`game.world_map` 仕込み」が test に再侵入する懸念。🎬 When: `test_cjg_framework_rule_guards.py` に「test/ 配下に `game\.world_map\s*=` が侵入していないこと」を assert する grep ガードを 1 件追加する。✅ Then: 再侵入が pytest で即 fail。Journey「2 つの真実が並走しない状態」が将来も保たれる。

## 3) Design

### 事前計測（2026-05-05 grep 実測値）

| 対象 | 場所 | 件数 |
|---|---|---|
| `(game\|self)\.world_map` 参照 | `image_banks.py:231,243,271,289` / `runtime/app.py:76` | 5 件 |
| `GameState.world_map` field | `game_state.py:36` | 1 件 |
| pyxres ロード済みフラグ | `image_banks.pyxres_loaded: bool`（既存、61 行） | 流用 |
| test 内 `game.world_map\s*=` 仕込み | `test_world_map_ssot.py` / `test_dungeon_boss_trigger.py` / `test_tilemap_editor_truth.py` | **3 ファイル**（Gherkin シナリオ5 の事前見積もりは過剰） |

### runtime 改修内訳

| # | ファイル:行 | 変更前 | 変更後 |
|---|---|---|---|
| 1 | `image_banks.py:230` `def bake_world_to_tilemap(self):` | 関数名 | **`def regenerate_world_tilemap_fallback(self):`** にリネーム |
| 2 | `image_banks.py:243` `wm = game.world_map` | game 経由 | **`wm = generate_world_map()` 直呼び**（game.world_map に依存しない） |
| 3 | `image_banks.py:289` `game.world_map = derived` | 副作用代入 | **削除**（`derive_world_from_tilemap` の戻り値も呼び元未使用なので signature は維持して内部代入だけ消す） |
| 4 | `image_banks.py:setup_world_tilemap` 内 `self.bake_world_to_tilemap()` 呼び出し（2 箇所） | 旧名 | 新名 `self.regenerate_world_tilemap_fallback()` に置換 |
| 5 | `runtime/app.py:76` `self.world_map = generate_world_map()` | 初期化 | **削除** |
| 6 | `game_state.py:36` `world_map: list = field(default_factory=list)` | field | **削除** |

### test 書き換え方針（3 ファイル）

| ファイル | 観点 | 書き換えパターン |
|---|---|---|
| `test_world_map_ssot.py` | pyxres pget = 起動後 pget の一致 | 旧：`game.world_map = [...]` → 新：`pyxel.tilemaps[0].pget` を `MagicMock(side_effect=...)` で仕込み + `image_banks.tile_id_by_pixel = {...}` |
| `test_dungeon_boss_trigger.py` | dungeon (1,1) trigger 解決 | 既に partial 改修済（`make_draw_game` で `pyxel.tilemaps[0].pget` モック導入済み）。残存 `game.world_map = ...` 行を撤去 |
| `test_tilemap_editor_truth.py` | Code Maker 編集面 = SSoT | 同上パターン。観点は維持または強化のみ |

判断ルール：「迷ったら聞く、聞かなければ観点維持」。assert 対象を削るだけの書き換えは本タスクで行わない（観点削除は別判断）。

### Code Maker 編集が即反映される根拠

- `setup_world_tilemap` 内では既に `if self.pyxres_loaded: ...` 分岐があり、ロード済み経路では `bake_world_to_tilemap` の呼び出しはユーザー編集を上書きしない動作（コメント済み：「pyxres が読み込み済みのときは tilemap が SSoT なのでスキップする」）
- 本タスクのリネームは挙動を変えない（fallback 経路は `pyxres_loaded == False` のときだけ通る）
- runtime 側は `generate_world_map()` 結果を保持しなくなるため、「2 つの真実が並走」構造そのものが消える

### commit 戦略（3 commit、シナリオ6 の中途 red 回避）

1. **A**: `test(ssot): world_map test 3 件を pyxres 直読パターンに書き換え`
   - 旧仕様 runtime 下でも green、新仕様 runtime 下でも green になるよう **両対応** で書き換える
   - 具体：`pyxel.tilemaps[0].pget` モック + `image_banks.tile_id_by_pixel` 仕込みを **追加**（既存 `game.world_map = [...]` 行は削除しないか、削除しても新実装と整合する形にする）
2. **B**: `refactor(ssot): drop world_map snapshot, rename bake to fallback`
   - runtime 改修内訳 #1〜#6 を 1 commit で実施
   - pre-commit pytest が green（A の書き換えにより）
3. **C**: `test(framework-rule): test/ 配下に game.world_map 仕込みが侵入しない static guard`
   - `test_cjg_framework_rule_guards.py` に 1 ケース追加

### 関連スキル・MCP
- 標準ツール：Bash / Edit / Grep / pytest（追加 MCP 不要）
- pre-commit hook（pytest）: 各 commit 直前に `pytest -q` 全 green 確認

### 委任度
🟢 高：影響範囲が事前 grep で確定済み（runtime 6 箇所、test 3 ファイル）。`test_dungeon_boss_trigger.py` は partial 既改修なので残作業はトリビアル。中途 red 回避のため commit 順序を A→B→C で固定。

## 4) Tasklist

### commit A: test 3 ファイル書き換え（pyxel.tilemaps[0].pget モック方式）
- [ ] `test/test_world_map_ssot.py`：`game.world_map = ...` 仕込みを `pyxel.tilemaps[0].pget` モック + `image_banks.tile_id_by_pixel` 仕込みに置換、assert 対象は「pyxres pget == 起動後 pget」を `pyxel.tilemaps[0].pget` 同士の比較に変更
- [ ] `test/test_dungeon_boss_trigger.py`：残存する `game.world_map = ...` 行を撤去（`make_draw_game` は既に partial 改修済）
- [ ] `test/test_tilemap_editor_truth.py`：同パターンで書き換え、Code Maker 編集面 = SSoT の観点を維持
- [ ] `pytest -q test/test_world_map_ssot.py test/test_dungeon_boss_trigger.py test/test_tilemap_editor_truth.py` green
- [ ] `pytest -q` 全 green
- [ ] commit `test(ssot): world_map test 3 件を pyxres 直読パターンに書き換え`

### commit B: runtime 撤去 + bake リネーム
- [ ] `src/shared/services/image_banks.py:230` `def bake_world_to_tilemap` → `def regenerate_world_tilemap_fallback` リネーム
- [ ] 同関数内 `wm = game.world_map` → `wm = generate_world_map()` 直呼び (import 追加)
- [ ] `src/shared/services/image_banks.py:289` `game.world_map = derived` 行削除
- [ ] `derive_world_from_tilemap` の戻り値・signature が呼び元未使用なら据え置き
- [ ] `setup_world_tilemap` 内 `self.bake_world_to_tilemap()` 呼び出し 2 箇所を新名に置換
- [ ] `src/runtime/app.py:76` `self.world_map = generate_world_map()` 削除（unused になった import も整理）
- [ ] `src/shared/services/game_state.py:36` `world_map: list = field(default_factory=list)` 削除
- [ ] `pytest -q` 全 green
- [ ] commit `refactor(ssot): drop world_map snapshot, rename bake to fallback`

### commit C: 再侵入ガード
- [ ] `test/test_cjg_framework_rule_guards.py` に「`(game|self)\.world_map\s*=` が `src/` および `test/` 配下に侵入していないこと」を assert する 1 ケース追加
- [ ] `pytest -q test/test_cjg_framework_rule_guards.py` green
- [ ] commit `test(framework-rule): world_map 再侵入を防ぐ static guard 追加`

### 仕上げ
- [ ] tasknote status `done`、`archived` タグ追加、`steering/done/` へ移動
- [ ] Discussion に test side `game.world_map` 読み取り箇所の grep 結果記録

### 作業記録

（実行時に追記）

## 5) Result

（実行時に追記）

## 6) Discussion

（実行時に追記）

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：フォロータスク 2 本の Tasklist 進行
