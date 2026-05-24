---
status: done
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:30:00+09:00
dateModified: 2026-05-05T22:30:00+09:00
tags:
  - task
  - testing
  - ssot
  - imagebank
  - cleanup
  - archived
---

# 2026年5月5日 imagebank SSoT 化に伴う test 群の書き換え

> 状態：⑥ Discussion 完了（done）。commit `cb5daad`。

## 1) Journey

- **深層的目的**：`game.world_map` / `game.dungeon_map` 撤去後、test 群が「runtime が読まなくなった field」を仕込み続ける状態を解消する

1. 💦 （開発者）機能を追加したりバグ修正したい（コードエディタ）
2. 💦 （開発者）リポジトリを眺める（コードエディタ、あなめる）
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

| 分類 | ファイル | 性質 |っっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっっｄ
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


## 4) Tasklist

> 着手時 (2026-05-05 22:00) に状況を再 grep したところ、Journey 起票時 (17:30) からの間に
> `imagebank-direct-cleanup.md` / `dungeon-map-removal.md` の自走実装で
> `game.world_map = ...` / `game.dungeon_map = ...` 代入は **すべて test/ から消えていた**。
> シナリオ1（assignment 0 件）とシナリオ5（src/ 側静的 guard）は既達成。
> 残課題は **シナリオ4（共通 helper による重複削減）** とシナリオ5の test/ 側 guard 強化。

- [x] 14 ファイルの現状確認（grep + 個別読み込み）→ 残作業を helper 集約に絞り込み
- [x] `test/_helpers/imagebank_stub.py` 新設（FakeTilemap / install_fake_tilemap / snapshot_tilemaps / restore_tilemaps / stub_explore_tilemap_read）
- [x] `test/conftest.py` に `test/` を sys.path 追加（`_helpers` パッケージ import 用）
- [x] `test_dungeon_boss_trigger.py::make_draw_game()` の手動 pget mock + tile_bank 仕込み 35 行を helper 1 呼び出しに置換
- [x] `test_world_map_ssot.py` の重複 `_FakeTilemap` class と setUp/tearDown を helper に集約
- [x] `test_tilemap_editor_truth.py` も同様に helper 集約
- [x] `test_cjg_framework_rule_guards.py` に `test_no_dungeon_map_field_assignment_in_tests` 追加（既存 world_map 側と対称）
- [x] `pytest test/ -q` で 717 → 718 passed 確認
- [x] commit `cb5daad`
- [x] Result / Discussion 記入 + done 化

---

## 5) Result（成果物）

### 変更ファイル

| ファイル | 内容 |
|---|---|
| `test/_helpers/__init__.py`（新規） | パッケージマーカー |
| `test/_helpers/imagebank_stub.py`（新規 / 100 行） | `FakeTilemap` / `install_fake_tilemap` / `snapshot_tilemaps` / `restore_tilemaps` / `stub_explore_tilemap_read` を提供 |
| `test/conftest.py` | `test/` を sys.path に追加（`_helpers` を `from _helpers.imagebank_stub import ...` で読めるように） |
| `test/test_dungeon_boss_trigger.py` | `make_draw_game()` の 35 行手動仕込みを helper 1 呼び出しに |
| `test/test_world_map_ssot.py` | 重複 `_FakeTilemap` / setUp tilemaps バックアップを helper に集約 |
| `test/test_tilemap_editor_truth.py` | 同上 |
| `test/test_cjg_framework_rule_guards.py` | `test_no_dungeon_map_field_assignment_in_tests` 追加（test/ 側 guard） |

### Gherkin CoVe

| シナリオ | 結果 | 根拠 |
|---|---|---|
| 1. test/ から旧 field 代入消去 | ✅ | `grep -rnE 'game\\.world_map\\s*=|game\\.dungeon_map\\s*=' test/ --include='*.py'` = 0 件（着手前から既達成、guard で永続化） |
| 2. 新仕様 pget 直読 pattern | ✅ | helper `stub_explore_tilemap_read` 経由で 3 file（test_dungeon_boss_trigger / test_world_map_ssot / test_tilemap_editor_truth）が 直読 mock を入れる |
| 3. 観点維持 | ✅ | test_dungeon_boss_trigger は dungeon (1,1) trigger 解決の assert そのまま、test_world_map_ssot は pyxres SSoT 不変性 assert そのまま、test_tilemap_editor_truth は path/shore variant の tilemap pget assert そのまま。717 → 718 passed（新 guard +1） |
| 4. 共通 helper | ✅ | `test/_helpers/imagebank_stub.py` 1 module 提供、3 file が import |
| 5. 静的 guard 永続化 | ✅ | 既存 `test_no_world_map_field_assignment_in_tests` に対し、対称な `test_no_dungeon_map_field_assignment_in_tests` を追加。今後の test 新規追加で `game.dungeon_map = ...` を書くと即 fail |

### コミット

```
cb5daad test(ssot): test_helpers/imagebank_stub を導入し、3 file の重複 _FakeTilemap / pget mock 仕込みを集約
        7 files changed, 176 insertions(+), 64 deletions(-)
```

---

## 6) Discussion（反省）

### 要約

Journey 起票（2026-05-05 17:30）から着手（22:00）までの 4.5 時間で、別タスク `imagebank-direct-cleanup` / `dungeon-map-removal` の自走実装が走っており、シナリオ1（test 内の旧 field 代入 0 件）とシナリオ5（src/ 側 guard）は **着手前に既達成**。残課題は重複コードの helper 集約に絞れた。差分は 176 insertions / 64 deletions（重複 64 行を削り、helper 100 行を新設）。

### 結論

- **依存タスクが先に走るとスコープが半分以上消える**：本タスクの当初想定 14 ファイル書き換えは、関連する SSoT 移行タスクの完了で 4 ファイルに縮小した。タスク開始時に **Journey 起票時のスコープを再検証する** のが正しい手順。今回はそれをやって正解だった。
- **重複削減の費用対効果**：3 file × 35 行（test_dungeon_boss_trigger 1 箇所と _FakeTilemap class 2 箇所）の重複を 100 行 helper に集約したのは「行数だけ見ると損」だが、新規 test を書く人が 35 行コピペせずに済む & 仕様変更時の修正点が 1 箇所に集中する効果が大きい。
- **conftest.py への sys.path 注入** は test 全体の import 方針に影響する。`from _helpers.imagebank_stub import ...` という呼び方が他 helper にも波及できるよう、命名と置き場を意識的に選んだ。

### 保留点（今後の指針）

| 保留 | 指針 |
|---|---|
| 分類 B の残り 4 file（test_cjg_ending / title / map_tile_transitions / town_entry）| 既に world_map / dungeon_map 仕込みは無く、新仕様 pget 直読も使っていない（背景タイル想定で pget の return value を見ない test）。helper 適用すべきかは「将来 dungeon タイル依存の assert を足したくなったら helper を入れる」という当面 dormant 扱い |
| 分類 C（test_architecture_layout / test_runtime_shim / test_cj24_sound_editor_truth） | grep で `world_map` / `dungeon_map` 参照ゼロ確認済。書き換え不要 |
| 分類 D（test_cjg_explore_model_imagebank_read） | 既に新仕様（AST 解析で「ExploreModel が world_map / dungeon_map に触れていない」を検証）。helper を使う方向に書き直す価値は薄い（test の性質が「触っていないこと」の確認だから） |
| `set_world_tile` を 1 マス毎に呼ぶ API | 当初設計案 `set_world_tile(model, x, y, tile_id)` から変更し、`stub_explore_tilemap_read` でステージ全体 tile_ids + overrides を一括指定する API に統合。1 test 1 ステージの仕込みなので一括化のほうが自然だった |

### 反省とルール化

- 記入先：feedback memory 候補
- ルール候補：「依存タスクが並走中なら、着手時に **stale 検出 grep** から始める」（今回はやって 14 → 4 ファイルに縮小できた）。次回 SSoT 系タスクで feedback memory に保存するか検討
- 次にやること：
  - `services-ui-pyxel-policy` タスクの Gherkin/Design 書き直し（pyxel violation の現状再カウント、Q1〜Q4 の判断確認）
  - `rename-production-to-dist` の実装（ユーザー承認待ち）

---
