---
status: open
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:30:00+09:00
dateModified: 2026-05-05T17:30:00+09:00
tags:
  - task
  - testing
  - ssot
  - imagebank
  - cleanup
---

# 2026年5月5日 imagebank SSoT 化に伴う test 群の書き換え

> 状態：① Journey 略式（フォロータスク起票のみ）

## 1) Journey

- **深層的目的**：`game.world_map` / `game.dungeon_map` 撤去後、test 群が「runtime が読まなくなった field」を仕込み続ける状態を解消する

1. 💦 （開発者）機能を追加したりバグ修正したい（コードエディタ）
2. 💦 （開発者）リポジトリを眺める（コードエディタ）
3. Before
  1. ❌ もう使っていないファイルや関数が残っている（コードエディタ）
  2. ❌ （開発者）わかりにくい
4. After
  1. ✅ もう使っていないファイルや関数が残っていない（コードエディタ）
  2. ♥️ （開発者）嬉しい

## 2) Gherkin

### シナリオ1：使っていない field 仕込みが test/ から消える
> 🧱 Given: 改修後の test/ ディレクトリ。runtime 側では既に `game.world_map` / `game.dungeon_map` が撤去済（フォロータスク `imagebank-direct-cleanup.md` / `dungeon-map-removal.md` 完了後）。🎬 When: `grep -rnE 'game\.world_map\s*=|game\.dungeon_map\s*=' test/ --include='*.py'` を実行。✅ Then: マッチ 0 件。死んだ field を仕込む test がリポジトリ内に残っていない。

### シナリオ2：新仕様（pyxel.tilemaps 直読）と整合した test 仕込みになる
> 🧱 Given: 改修後の test ファイルを開発者が開く。🎬 When: 「マップにこのタイルを置く」セットアップ箇所を読む。✅ Then: `pyxel.tilemaps[0].pget = MagicMock(side_effect=...)` と `image_banks.tile_id_by_pixel = {...}` のパターンで書かれている。古い「`game.world_map = [...]` と `tile_bank` を二重に仕込む」パターンが消えている。読んだ開発者が「DB（pyxres）を直読する」というプロダクトの実装方針と test の仕込みが一致していると一目で分かる。

### シナリオ3：既存テスト観点を破壊せず書き換える
> 🧱 Given: 改修前の各 test ファイルが固定していた検証観点（例：`test_world_map_ssot.py` は pyxres pget = 起動後 pget の一致、`test_dungeon_boss_trigger.py` は dungeon (1,1) の trigger 解決、等）。🎬 When: 各 test を新仕様で書き換える。✅ Then: 観点（assert の対象）は同じか強化されているのみ。観点を削るだけの「書き換え」は本タスクで実施しない（観点削除は別タスクの判断に委ねる）。pytest は全件 green。

### シナリオ4：再仕込みパターンの共通化（重複削減）
> 🧱 Given: 14 ファイルで個別に「pget モック + tile_id_by_pixel 仕込み」を書くと冗長。🎬 When: 共通 helper（例：`test/_helpers/imagebank_stub.py` の `set_world_tile(model, x, y, tile_id, image_banks)`）を導入する。✅ Then: 各 test の冒頭が 1〜3 行で済み、開発者がコードを読むときに「マップに何を置いたか」が直感的に追える。

### シナリオ5：撤去漏れの再侵入を防ぐ静的ガード
> 🧱 Given: 改修完了後、将来的に新規 test を追加する開発者が古いパターンを真似してしまう懸念。🎬 When: `test_cjg_framework_rule_guards.py` などに「test/ 配下に `game\.world_map\s*=` が侵入していないこと」を assert する grep ガードを 1 件追加する。✅ Then: 古いパターンの再侵入が pytest で即 fail。「使っていないファイルや関数が残っていない」状態を将来も維持できる（Journey「After」の永続化）。

## 3) Design

### 関連スキル・MCP
- 標準ツール：Bash / Read / Edit / Grep / pytest（追加 MCP 不要）
- 流用：`test/test_dungeon_boss_trigger.py` で本日 (2026-05-05) 実装済みの「pyxel.tilemaps[0].pget モック + tile_id_by_pixel 仕込み」パターンを参考実装とする

### 対象ファイル一覧（14 件）と書き換えパターン分類

| 分類 | ファイル | 性質 |
|---|---|---|
| **A. world_map 直接 assert 系** | `test_world_map_ssot.py`, `test_setup_world_tilemap_preserves_user_edits.py`, `test_world_map_contract.py`, `test_world_generation.py`, `test_tilemap_editor_truth.py` | pyxres SSoT 化を保証する根幹 test 群。書き換えで観点が薄まらないよう個別検討 |
| **B. game セットアップで world_map 仕込み系** | `test_dungeon_boss_trigger.py` ✅、`test_cjg_ending_scene_behavior.py`, `test_cjg_title_scene_behavior.py`, `test_cjg_map_tile_transitions.py`, `test_cjg_town_entry_sets_current_town.py` | `make_*_game` 内で world_map / dungeon_map を仕込んでいる。helper でパターン共通化 |
| **C. 構造 / 互換系** | `test_architecture_layout.py`, `test_runtime_shim.py`, `test_cj24_sound_editor_truth.py` | shim / レイアウト規約 / sound editor 系。`world_map` field の field 名そのものを参照していたら撤去 |
| **D. 既に新仕様** | `test_cjg_explore_model_imagebank_read.py` | 本日新規作成。書き換え不要。helper を使う形に統一するなら書き直し |

### 共通 helper 設計
```python
# test/_helpers/imagebank_stub.py
def set_world_tile(image_banks, x, y, tile_id, *, in_dungeon=False):
    """ExploreModel の DB 直読が指定マスで tile_id を返すように pyxel.tilemaps と
    image_banks を同時に仕込む。重複ロジックを 1 行で書けるようにする。"""
    ...

def set_world_tiles(image_banks, mapping):
    """{(x, y): tile_id, ...} を一括で仕込む。"""
    ...
```

### 進め方
1 ファイル 1 commit を原則。1 commit 内で：
1. helper 導入（1 commit 目だけ。共通 helper の新設）
2. 該当 test を新仕様に書き換え
3. `pytest test/<該当ファイル> -v` が green
4. `pytest test/ -q` が全 green

撤去漏れガード（シナリオ5）は最後の commit で追加。

### 進める順序（依存関係考慮）
1. helper 新設
2. 分類 D の確認（書き換え不要なら skip、helper 化するなら最初に）
3. 分類 B（make_*_game の置換、5 ファイル）— 既に 1 件 (`test_dungeon_boss_trigger.py`) は完了済
4. 分類 A（観点維持に注意、5 ファイル）
5. 分類 C（field 名参照の撤去、3 ファイル）
6. 撤去漏れガード追加 + 全 green 確認

### 委任度
🟡 中：
- 共通 helper 設計と分類 A の観点維持判断はユーザー確認が望ましい
- 分類 B / C は機械的書き換えで CC 自走可能
- 全 14 ファイル × 平均 5〜10 行書き換え = 完走見込みあり、ただし 1 セッションでは厳しい量

## 4) Tasklist

（着手時に 14 ファイル分の小タスクに分解）

## 5) Result / 6) Discussion

（着手時に追記）
