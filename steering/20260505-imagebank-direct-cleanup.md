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
- **やらないこと**：
  - `game.dungeon_map` 撤去（→ 別タスク `20260505-dungeon-map-removal.md`）
  - test 群の `world_map = [...]` 仕込みを pyxel.tilemaps モックに書き換える大規模リファクタ（→ 別タスク `20260505-rewrite-tests-for-imagebank-ssot.md`）

## 2) Gherkin

### シナリオ1：`game.world_map` が src 全域から消える
> 🧱 Given: 改修後の repo。🎬 When: `grep -nE 'game\.world_map\|self\.world_map' src/ -r --include='*.py'` を実行。✅ Then: マッチ 0 件。

### シナリオ2：`GameState.world_map` フィールドが消える
> 🧱 Given: 改修後の `src/shared/services/game_state.py`。🎬 When: `world_map` を grep。✅ Then: マッチ 0 件。

### シナリオ3：`bake_world_to_tilemap` の名称が「fallback 専用」に変わる
> 🧱 Given: 改修後の `src/shared/services/image_banks.py`。🎬 When: 関数定義を確認。✅ Then: 元の名前は消え、`regenerate_world_tilemap_fallback`（仮）等の「fallback 専用」を示す名称になっている。pyxres 不在 / load 失敗時の初回生成 + `pyxel.save` 経路は維持されている。

### シナリオ4：pyxres 不在 / 破損時の fallback が機能する
> 🧱 Given: pyxres ファイルが不在 or 破損。🎬 When: `setup_image_banks` 経由でゲーム起動。✅ Then: `regenerate_world_tilemap_fallback` が procedural に world を生成して tilemap[0] に焼き、`pyxel.save` で pyxres を作る（既存挙動の温存）。

### シナリオ5：既存テストへの最低限の補修
> 🧱 Given: 改修後の repo + pre-commit hook が pytest を走らせる。🎬 When: 全テスト実行。✅ Then: red になった test は「dynamic 属性で `game.world_map` を仕込んでいるだけ／derive 結果を assert している」のいずれかで、本タスクでは「runtime が読まなくなる」ことだけ確認し、test の書き換えは別タスクへ移送（red のまま残さず、最低限 SKIP マーク or skipif で対応 / もしくは別タスクが完了するまで pre-commit を SKIP_TESTS=1 で通す）。

## 3) Design

### 変更
1. `image_banks.bake_world_to_tilemap` → **`regenerate_world_tilemap_fallback`** にリネーム。中の `wm = game.world_map` を `wm = generate_world_map()` 直呼びに置換
2. `image_banks.derive_world_from_tilemap` の `game.world_map = derived` 行を撤去（戻り値も呼び元で使われていなければ整理）
3. `image_banks.setup_world_tilemap` 内の呼び出し名を新名称に更新
4. `runtime/app.py:76` の `self.world_map = generate_world_map()` を撤去
5. `GameState.world_map: list = field(default_factory=list)` を撤去

### 関連 commit 単位
- 1 commit に集約（`refactor(ssot): drop world_map snapshot, rename bake to fallback`）

### 委任度
🟡 中：test 群への影響が広いが、本タスクは「runtime が読まなくする」ところまで。test 書き換えは別タスクへ移送する設計。

## 4) Tasklist

- [ ] image_banks.py: bake をリネーム + 内部 generate_world_map 直呼び
- [ ] image_banks.py: derive の `game.world_map = derived` 撤去
- [ ] image_banks.py: setup_world_tilemap の呼び出し名を更新
- [ ] runtime/app.py: `self.world_map = generate_world_map()` 撤去
- [ ] game_state.py: world_map field 撤去
- [ ] pytest 走行 → 壊れた test を集計（書き換えはせず、結果を Discussion に記録）
- [ ] フォロータスク 2 本（dungeon_map 削除 / test 書き換え）の起票完了確認
- [ ] commit（test red を許容するか SKIP_TESTS=1 で通すかは結果次第）

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
