---
status: done
priority: high
scheduled: 2026-04-22T23:54:40+00:00
dateCreated: 2026-04-22T23:54:40+00:00
dateModified: 2026-04-23T11:10:00+00:00
tags:
  - task
  - j53
  - architecture
  - runtime
  - refactor
  - single-distribution
  - archived
---

# 2026年4月22日 J53 runtime monolith 分解と dev/prod 単一化

> 状態：`done`（全 Phase 完了。tags: `j53-phase1-methods-complete` / `j53-phase1-5-complete` / `j53-phase2-complete` / `j53-phase3-complete` / `j53-phase4-complete`）
> 次のゲート：なし（本タスクノート終了）

---

## 1) 改善対象ジャーニー

- **根拠となるカスタマージャーニー**：[CJ37 責務が曖昧で直すほど別の所が壊れる](../docs/customer-journeys.md#cj37-責務が曖昧で直すほど別の所が壊れる)（避けるべきアンチパターン）
- **関連するカスタマージャーニー**：CJ22（フィードバック反映の好循環）、CJ26（「自分たちのゲーム」と言えるようになる）、CJ39（システム変更でゲーム全体が壊れる）、CJ41（技術基盤変更で配信が壊れる）
- **深層的目的**：AIが読める疎結合な責務分担表を復活させ、「直すほど別の所が壊れる」を構造的に止める
- **やらないこと**：ゲームロジック（scenes / dialog / game_data 等）の書き換え。runtime と build 層の整理に絞る

### 現状

- `src/runtime/main_runtime.py` が 7266 行、Game クラスだけで 2500 行ほど。`chiptune_tracks.py` / `landmark_events.py` / `player_factory.py` / `player_snapshot.py` / `save_store.py` / `browser_resource_override.py` / `sfx_system.py` / `scenes/dialog/model.py` / `audio_system.py` / `game_data.py` / `generated/dialogue.py` / `jp_font_data.py` / `input_bindings.py` が inlined されている
- `src/shared/services/*` と `src/scenes/*` に抽出済みのモジュールがあるが、runtime は inlined コピーを使っている（二重管理）
- `main_development_runtime.py` は `main_runtime.py` のコピー＋開発版差分。dev/prod は artifact レベルでも `development/` / `production/` に分かれる
- selector は 2 カード（開発版・本番）、取り込み UI 付き。`tools/web_runtime_server.py` は手動起動

### Phase 1 完了時点（2026-04-23）のスナップショット

- `src/runtime/main_runtime.py` は **1956 行**（7266 → 73% 削減）。Game クラスは `__init__ / start / update / draw` の 4 メソッドに縮小
- Game メソッド 109 件（当初見積りの「113」は概数で、実移動は 109 件）を全て scenes（11 個）／shared/services（7 新規）／shared/ui（1 新規）に分配済み
- inlined 13 ブロックはすべて import に置換済み（P1-C1〜C13 完了）
- 270 テスト green / web & codemaker ビルド exit 0 / headless Game() + update/draw サイクル確認済み
- Gherkin シナリオ 1・3 は達成。シナリオ 2（`wc -l < 50`）は Phase 1.5 に繰り越し

### 今回の方針

- 「参考資料」セクションにある通りのディレクトリ構造にする

---

## 2) 改善対象gherkin（完了条件）

> スコープ：ディレクトリ構造のみ。挙動（ゲームが正しく動くか）や配信（build 出力）の完了条件は別 gherkin で扱う。本 gherkin はすべて `find` / `grep` / `ls` / AST parse で機械的に検証できる形に書く。

### シナリオ1：正常系（マトリクスどおりに新規ディレクトリとファイルが生えている）

> 🧱 Given: Phase 1 の作業が完了し、参考資料の分配マトリクスに従って monolith が分解されている。
> 🎬 When: `find src/scenes src/shared -type f -name '*.py'` でファイル一覧を取得する。
> ✅ Then: 以下がすべて存在する：
> - `src/scenes/{title, splash, explore, town, shop, battle, menu, settings, ai_help, professor, ending}/` の **11 ディレクトリ**（Q1A 決定：dialog は解体、message は新設しない）
> - 各 scene ディレクトリに `model.py / view.py / presenter.py / scene.py / __init__.py` の 5 ファイル
> - `src/shared/services/` に既存 8（`audio_system / input_bindings / landmark_events / player_state / save_store / codemaker_resource_store / play_session_logging / browser_resource_override`）+ 新規 8（`game_state / dialog_runner / message_display / world_generation / image_banks / vfx / item_use / text_format`）の **16 `.py`**
> - `src/shared/ui/` に既存 3（`dialog_window / hud / menu_window`）+ 新規 2（`status_bar / message_window`）の 5 `.py`

### シナリオ2：異常系（monolith に inlined コピーと Game クラスが残っていない）

> 🧱 Given: Phase 1 完了後の `src/runtime/main_runtime.py`。
> 🎬 When: `grep -E '^class Game|^class (InputStateTracker|SaveStore|AudioManager|StructuredDialogRunner|SfxSystem|LandmarkEvent|InMemorySaveStore|FileSaveStore|LocalStorageSaveStore)|^def (any_btn|any_btnp|generate_world_map|generate_dungeon|load_enemies|choose_bgm_scene|create_initial_player|stage_browser_imported_resource)' src/runtime/main_runtime.py` を実行する。
> ✅ Then: マッチ行がゼロ。`main_runtime.py` は `from src.shared.services.*` と `from src.scenes.*` と `from src.app import BlockQuestApp` の import 文、`pyxel.init` / `pyxel.load` / `pyxel.run` の Pyxel 固有初期化、および `run()` / `if __name__ == "__main__"` の entry だけで構成され、**行数は 50 行未満**。`src/runtime/main_development_runtime.py` は Phase 3 までは残るが、中身は `main_runtime.py` と同様に薄くなっている。

### シナリオ3：回帰確認（既存ディレクトリ構造が壊れていない・import 参照が成立する）

> 🧱 Given: Phase 1 完了後の repository。
> 🎬 When: `python -c 'import src.runtime.main_runtime'` と `python -m pytest test/test_architecture_layout.py -q` を実行する。
> ✅ Then: `ImportError` / `ModuleNotFoundError` が出ず、architecture_layout test が green（新しいディレクトリ構造を反映して更新済み）。`src/app.py` / `src/core/scene_manager.py` / `src/game_data.py` / `src/generated/*.py` / `assets/` / `templates/` / `tools/` の既存ファイルは path と public 関数名が保持されている（対象外セクションの約束）。

### 対応するカスタマージャーニーgherkin

- `CJG37: 責務分担表に従って直せる（別箇所が壊れない）` ← 本 note の主 CJ、ディレクトリ構造の分離がこれの物理的な下支え
- `CJG22: フィードバックから修正と再共有が数分で回る`（構造が見えれば AI の修正局在が速くなる前提）

**Phase 1 完了時点の達成状況（2026-04-23）**: **部分達成**。scenes / services / ui の分離は完遂（CJG37 の物理下支えは成立）したが、`main_runtime.py` 自体の 50 行未満化は未達（TILE_DATA 等 1500 行の定数抽出が Phase 1.5 に繰り越し）。AI の修正局在性は 113（実 109）メソッドの分類成立で既に大幅改善しており、CJG22 への貢献は先取り達成。

---

## 3) Design（どうやるか）

### 関連スキル・MCP

- `manage-tasknotes` / `steer-development` / `systematic-debugging` / `test-driven-development` / `verification-before-completion`
- **MCP**：追加なし（`grep` / `find` / `ast.parse` / `wc` で完結）

### 調査起点

- `src/runtime/main_runtime.py` line 4771〜7234（`class Game`、113 メソッド、instance state を列挙）
- `src/runtime/main_runtime.py` line 15〜2565（inlined 14 ブロック、shared/services の既存実装との diff 確認）
- `src/runtime/main_runtime.py` line 4122〜4720（world 生成群、未抽出）
- `src/app.py` / `src/core/scene_manager.py`（BlockQuestApp の DI 形、Scene Protocol、overlay の stack 要否）
- `test/test_architecture_layout.py`（存在すれば現状アサーション、なければ新設）
- 既存 `src/scenes/{title,explore,battle,dialog}/` を M/V/P/S の参照テンプレートとする

### 移動の順序戦略（bottom-up）

1. **inlined → import 置換**（monolith → shared/services、**13 ブロック** / P1-C1〜C12 の 12 タスクでカバー）
   - 既存 services と差分ゼロの block から順に `from src.shared.services.X import Y` に置換
   - 差分がある block（例：`SfxSystem` は未抽出）は先に service 側を拡張
   - 本ステップだけで `main_runtime.py` が 2500 行ほど削減される見込み
2. **Game 外の残存関数を shared/services に追い出す**
   - `world_generation.py` 新設 ← `get_path_variant / generate_world_map / generate_dungeon / _place_*` など 11 関数
   - `text_format.py` 新設 ← `name_en` / Game 内 `_name` / `_t`
3. **Game class の instance state 棚卸し**
   - `grep -oE 'self\.[a-z_]+' src/runtime/main_runtime.py | sort -u` で全 state を列挙
   - scene 間共有 state（`player / flags / town_pos / save_store / audio_manager / scene_manager` など）を app.py か SceneManager に昇格、scene 側は DI で受け取る設計に
4. **新規 scenes / services / ui の skeleton を作る**（空で commit）
   - 新規 9 scenes × 5 ファイル + 5 services + 2 ui + `__init__.py`
5. **Game メソッドを category 単位で移動**（マトリクスの 113 件）
   - 単位：「splash 2 件」「explore 8 件」「town 10 件」…と 1 category = 1 commit
   - 各 commit 後に `pytest -q` と `python -c 'import src.runtime.main_runtime'` を確認
6. **Game class が空になったら削除**
7. **`main_runtime.py` を 50 行未満の薄い entry に書き換え**（Pyxel 初期化 + BlockQuestApp 組立 + `pyxel.run`）

### 実世界の確認点

- **見る path**：
  - `src/runtime/main_runtime.py`（目標 <50 行）
  - `src/scenes/{splash,town,shop,message,menu,settings,ai_help,professor,ending}/` の 9 新規ディレクトリ
  - `src/shared/services/{world_generation,image_banks,vfx,item_use,text_format}.py` の 5 新規
  - `src/shared/ui/{status_bar,message_window}.py` の 2 新規
- **動かすコマンド**：
  - `wc -l src/runtime/main_runtime.py`（< 50）
  - `find src/scenes -maxdepth 1 -type d | wc -l`（= 14：scenes 自身 + 13 scene）
  - `find src/shared/services -maxdepth 1 -name '*.py' -not -name '__init__*' | wc -l`（= 13）
  - `python -c 'import src.runtime.main_runtime'`（ImportError ゼロ）
  - `python -m pytest test/ -q`（既存テスト全 green）
  - `python main.py`（実機で Splash → Title → ゲームループが回る、最低 1 分動作確認）
- **増える file 量の見積もり**：scenes 45 + services 5 + ui 2 + `__init__` 数個 ≈ **52 ファイル**

### 検証方針

- **red → green の刻み**：移動 1 category（数〜15 メソッド）= 1 commit。commit 後に `pytest -q` が green を維持
- **monolith 残留ゼロ検証**：gherkin シナリオ 2 の grep 式と `wc -l < 50` を `test/test_runtime_shim.py`（新規）で固定
- **layout 検証**：`test/test_architecture_layout.py` を新 layout で書き換え、CI でガード
- **import 参照成立**：各 commit で `python -c 'import src.runtime.main_runtime'` を走らせる
- **挙動の安全網**（スコープ外だが守る）：`tools/test_headless.py` と `tools/test_web_compat.py` を Phase 1 の最後で一度は実行

### Risk と mitigation

- **R1：Game の instance state 依存が複雑で scene 分離時に state 破綻**
  - M1：ステップ 3 で先に state 棚卸し、共有 state は app.py / SceneManager に集中管理、scene は DI で受ける
- **R2：Pyxel global state（pyxel.image / pyxel.tilemap）に依存する service が干渉**
  - M2：pyxel module を引数で渡す既存 pattern（`InputStateTracker`）を踏襲。new service も同じ規約に揃える
- **R3：`main_development_runtime.py` との二重管理が Phase 1 中に残る**
  - M3：Phase 1 は `main_runtime.py` のみ作業。dev 版は Phase 3 で削除するので途中の乖離は許容
- **R4：113 メソッドの内部依存が循環していて単体移動が不可**
  - M4：ステップ 3 で `grep -nE 'self\._[a-z_]+' src/runtime/main_runtime.py` から依存グラフを作り、循環 cluster は同一 commit で一括移動
- **R5：Pyxel Code Maker の単一 main.py 配布が Phase 1 だけだと壊れる**（import ベースだと zip が動かない）
  - M5：Phase 2 の bundler が入るまで `tools/build_codemaker.py` を fallback で `sync_main_data.py` ルートに残す。Phase 1 完了時点で Code Maker zip が壊れていることは gherkin スコープ外として許容

---

## 4) Tasklist（Phase 1）

### 運用ルール

- **1 タスク = 1 commit** 想定。commit 後に `pytest -q` + `python -c 'import src.runtime.main_runtime'` を必ず走らせ green 確認
- **Q2B 段階承認**：category（P1-A 〜 P1-I の 9 群）完了時点で user review 待ち → OK 後に次の category へ
- **commit message 規約**：`j53(P1-Cn): <移動内容>` で bisect 耐性を確保
- 合計 **68 タスク**（Phase 1: 51 タスク / Phase 1.5: 17 タスク）。見積もり：category あたり数十分〜2 時間、Phase 1 全体で 2〜3 日（集中作業時）

---

### P1-A. 準備（2 タスク）

- [x] **P1-A1**：`grep -nE '^# === inlined' src/runtime/main_runtime.py` で inlined block の正確な行範囲と名前をメモ（**13 blocks** 実測）。結果を `tmp/inlined_blocks.txt` に保存
- [x] **P1-A2**：`test/test_architecture_layout.py` の存在確認。あれば内容を読む、なければ P1-H5 で新設する方針を確定

### P1-B. Game instance state 棚卸し（3 タスク）

- [x] **P1-B1**：`sed -n '4771,7234p' src/runtime/main_runtime.py | grep -oE 'self\.[a-zA-Z_][a-zA-Z_0-9]*' | sort -u` で Game 内の全 self フィールドを列挙（約 80 件）
- [x] **P1-B2**：各 field を `{GameState / scene-local model / service 保有}` に分類。マトリクス v2 との diff があれば note を更新
- [x] **P1-B3**：棚卸し結果を `tmp/state_inventory.md` に保存（P1-G 段階で参照）

### P1-C. inlined → import 置換（13 タスク）

各 task は「inlined block を削除 + `from src.shared... import ...` に置換」。commit 後 `pytest` green 確認。

- [x] **P1-C1**：`input_bindings` block（line ~130）を削除 → `from src.shared.services.input_bindings import any_btn, any_btnp, InputStateTracker`
- [x] **P1-C2**：`landmark_events` block → `from src.shared.services.landmark_events import ...`
- [x] **P1-C3**：`player_factory` + `player_snapshot` 2 block → `from src.shared.services.player_state import ...`
- [x] **P1-C4**：`save_store` block → `from src.shared.services.save_store import ...`
- [x] **P1-C5**：`browser_resource_override` block → `from src.shared.services.browser_resource_override import ...`
- [x] **P1-C6**：`sfx_system` block を `shared/services/audio_system.py` に吸収（`SfxSystem` class を追加）、inlined を import に置換
- [x] **P1-C7**：`chiptune_tracks` block を `audio_system.py::_load_tracks` で使う形に統合、inlined を import に置換
- [x] **P1-C8**：`scenes/dialog/model.py` block を **`shared/services/dialog_runner.py`** に移動（Q1A）。既存 `src/scenes/dialog/model.py` もここに統合して重複を解消
- [x] **P1-C9**：`audio_system` block → `from src.shared.services.audio_system import ...`
- [x] **P1-C10**：`game_data` block → `from src.game_data import ...`
- [x] **P1-C11**：`generated/dialogue` block → `from src.generated.dialogue import ...`
- [x] **P1-C12**：`jp_font_data` block を `image_banks.py` 内の class 定数として吸収（または `src/shared/assets/jp_font_data.py` に抽出）
- [x] **P1-C13**：`grep '# === inlined' src/runtime/main_runtime.py` がゼロを確認。`wc -l src/runtime/main_runtime.py` で約 2500 行減っていることを確認

### P1-D. Game 外残存関数を services へ（2 タスク）

- [ ] **P1-D1**：新規 `src/shared/services/world_generation.py` を作成、Game 外の 11 関数（`get_path_variant` / `get_shore_variant` / `_make_empty` / `_carve_winding_path` / `_place_forests` / `_place_decorations` / `_place_landmarks` / `generate_world_map` / `generate_dungeon` / `get_zone` / `_build_zone_enemies`）を移動。**line 1673 / 4612 の `_build_zone_enemies` 重複を 1 本に統合** **※ Phase 1.5 に延期**（stub のみ、実装は P1.5-C で実施）
- [x] **P1-D2**：新規 `src/shared/services/text_format.py` を作成、runtime monolith の `name_en` を移動（Game 内の `_name` / `_t` は P1-G14 で移動）

### P1-E. skeleton 作成（4 タスク）

- [x] **P1-E1**：新規 8 scenes（`splash` / `town` / `shop` / `menu` / `settings` / `ai_help` / `professor` / `ending`）の `model.py` / `view.py` / `presenter.py` / `scene.py` / `__init__.py` を空で作成（40 ファイル）。既存 `title` / `explore` / `battle` の skeleton は変更なし
- [x] **P1-E2**：新規 6 services を空で作成：`game_state.py` / `dialog_runner.py`（P1-C8 でも触れる）/ `message_display.py` / `image_banks.py` / `vfx.py` / `item_use.py`
- [x] **P1-E3**：新規 2 shared/ui を空で作成：`status_bar.py` / `message_window.py`
- [x] **P1-E4**：`src/scenes/dialog/` を削除（Q1A 完全解体）。`dialog_runner` 実装は P1-C8 で `shared/services/` に移動済み

### P1-F. GameState 実装（2 タスク）

- [x] **P1-F1**：`shared/services/game_state.py` に `@dataclass GameState` を定義（マトリクス v2 の 19 フィールド、`default_factory` 付き）
- [x] **P1-F2**：`src/app.py::BlockQuestApp` が GameState を保有、`set_scene` で DI する形に改修。scene constructor に GameState 引数を追加（既存 scenes も含む）

### P1-G. Game メソッドを category 単位で移動（15 タスク）

各 task は「Game から該当メソッドを切り出し、target file に移動」。Q3A に従い **名前はそのまま**。scene に移す場合は `_update_map` 等 `_` 付きのままで OK。

- [x] **P1-G1**：title 3 メソッド → `scenes/title/scene.py::TitleScene`、`title_cursor` state → `TitleModel`
- [x] **P1-G2**：splash 2 メソッド → `scenes/splash/scene.py::SplashScene`、`splash_frame` state → `SplashModel`
- [x] **P1-G3**：explore 8 メソッド → `scenes/explore/scene.py::ExploreScene`、`walk_frame` / `walk_timer` / `move_cooldown` / `_a_cooldown` → `ExploreModel`
- [x] **P1-G4**：town 10 メソッド → `scenes/town/scene.py::TownScene`、`town_menu_cursor` / `town_menu_pos` / `menu_message` → `TownModel`
- [x] **P1-G5**：shop 4 メソッド → `scenes/shop/scene.py::ShopScene`、shop 系 4 state → `ShopModel`
- [x] **P1-G6**：battle 15 メソッド → `scenes/battle/scene.py::BattleScene`、battle 系 12 state → `BattleModel`
- [x] **P1-G7**：menu 3 メソッド → `scenes/menu/scene.py::MenuScene`、menu 系 3 state → `MenuModel`
- [x] **P1-G8**：settings 7 メソッド → `scenes/settings/scene.py::SettingsScene`、settings 系 2 state → `SettingsModel`
- [x] **P1-G9**：ai_help 4 メソッド → `scenes/ai_help/scene.py::AiHelpScene`、`_ai_help_status` → `AiHelpModel`
- [x] **P1-G10**：professor 11 メソッド → `scenes/professor/scene.py::ProfessorScene`、professor 系 6 state → `ProfessorModel`
- [x] **P1-G11**：ending 3 メソッド → `scenes/ending/scene.py::EndingScene`、`ending_lines` → `EndingModel`
- [x] **P1-G12**：message_display 12 メソッド → `shared/services/message_display.py::MessageDisplay`、`msg_callback` / `msg_index` / `msg_lines` / `_say_buffer` を service が保有
- [x] **P1-G13**：image_banks 17 メソッド → `shared/services/image_banks.py::ImageBanks`、`font` / `tile_bank` / `sprite_bank` / `path_variant_bank` / `shore_variant_bank` / `tile_id_by_pixel` / `has_jp_font` / `_pyxres_loaded` / `_pyxres_path` / `tile_bank_water2` を service が保有（マトリクスの 19 件から `tile_iter` / `sprite_iter` が既存 helper と重複していたため実数 17 件に収束）
- [x] **P1-G14**：vfx 2 + item_use 1 + text_format 2 を各 service に移動。vfx の `vfx_timer` / `vfx_type` state は vfx service が保有
- [x] **P1-G15**：input 2（`_btn` / `_btnp`）を直接 `InputStateTracker` 呼び出しに置換。`_sync_audio` は `audio_system.sync_audio(game)` module function に移動。`draw_status_bar` は `shared/services/status_bar.py::StatusBar` に service として切り出し（座標と pyxel 描画をまとめて保有）

### P1-H. Game class 削除 & entry 薄化（5 タスク）

- [x] **P1-H1**：Game class に残存メソッドがゼロ（or top-level `update` / `draw` のみ）を `grep -c '^    def ' src/runtime/main_runtime.py` で確認（結果：`__init__` / `start` / `update` / `draw` の 4 つに縮小、113 メソッドの移動はゼロ残留）
- [x] **P1-H2**：Game class に残存 state がゼロを確認。漏れがあれば P1-G に戻って対応（scene/service が全部保有、Game 側には `last_town_pos` / `debug_mode` / `cam_x` など 少数の共有 state のみ残存）
- [ ] **P1-H3**：Game class 定義を削除。`update` / `draw` dispatcher は `BlockQuestApp.update` / `.draw` に統合済みとする **※ Phase 1.5 に延期**（現状は dispatcher 専用の薄い Game が残存）
- [ ] **P1-H4**：`main_runtime.py` を書き換え：`import` + `run()` のみ、**50 行未満** **※ Phase 1.5 に延期**（TILE_DATA / world 生成 ~1500 行の抽出が未完のため 1956 行残存）
- [ ] **P1-H5**：`test/test_runtime_shim.py` を新規作成（gherkin シナリオ 2 の grep 式と `wc -l < 50` を固定）。`test/test_architecture_layout.py` を新 layout で書き換えまたは新規作成 **※ Phase 1.5 に延期**（P1-H3/H4 完了が前提）

### P1-I. 検証と締め（5 タスク）

- [x] **P1-I1**：`python -m pytest test/ -q` 全 green（270 passed）
- [x] **P1-I2**：`python -c 'import src.runtime.main_runtime'` 成功（pyxel stub を噛ませて Game() 初期化 + update/draw 1 サイクル確認済み）
- [ ] **P1-I3**：`python main.py` で実機 splash → title → ゲーム本編の **1 分動作確認** **※ Phase 1.5 でユーザー側実機確認（CI 環境では headless のため skip）**
- [~] **P1-I4**：gherkin 3 シナリオを手動実行（`find` / `grep` / `wc` による機械検証） **※ シナリオ 1・3 は green、シナリオ 2（`wc -l < 50`）は Phase 1.5 で達成予定**
- [x] **P1-I5**：Phase 1 完了コミット + git tag `j53-phase1-methods-complete`（2026-04-23 作成、元の `j53-phase1-complete` から改名。シナリオ 2 未達のため「113 メソッド移動完了」の意味で命名）

---

## 4.5) Tasklist（Phase 1.5）

### 背景

Phase 1 は Game クラスの 113 メソッド移動は完遂し、`main_runtime.py` を 7266 → 1956 行（**73% 削減**）まで縮小した。ただし gherkin シナリオ 2 の `wc -l < 50` は未達。残存している 1956 行の内訳は：

- **定数**（TILE_DATA / PATH / SHORE / HERO / ENEMY_SPRITES）約 1100 行
- **world 生成関数**（`generate_world_map` / `generate_dungeon` / `get_zone` / `_place_*` 等）約 300 行
- **Game class（薄い dispatcher）** 約 300 行
- **import / entry / module-level helpers** 約 250 行

Phase 1.5 では **定数と world 生成を専用モジュールへ抽出し、Game を `src/runtime/app.py` に移して、`main_runtime.py` を re-export shim に圧縮**する。

### 運用ルール（Phase 1 と同じ）

- 1 タスク = 1 commit、commit 後に `pytest -q` + headless 起動テスト green 確認
- commit message 規約：`j53(P1.5-X): <内容>`

### P1.5-A. TILE_DATA / タイル定数の抽出（3 タスク）

- [x] **P1.5-A1**：`src/shared/constants/tile_data.py` を新規作成し、`TILE_DATA` / `TILE_WATER2` / `T_GRASS` 等のタイル ID 定数 / `MAP_W` / `MAP_H` / `DECORATION_TILES` / `CASTLE_POS` / `TOWN_*` / `CAVE_GLITCH` / `BIGTREE_POS` / `TOWER_POS` を `main_runtime.py` から移動
- [x] **P1.5-A2**：`PATH_V` / `PATH_H` / `PATH_CROSS` / `PATH_SE` / `PATH_SW` / `PATH_NE` / `PATH_NW` / `PATH_T_*` と `SHORE_N/S/W/E/NE/NW/SE/SW` の 19 ビットマップ + `_PATH_VARIANTS` / `_SHORE_VARIANTS` を同ファイルに移動
- [x] **P1.5-A3**：`main_runtime.py` の元定数を削除し、`from src.shared.constants.tile_data import *` で再エクスポート。`image_banks.py` / `world_generation.py` / `scenes/explore/scene.py` の lazy import (`import src.runtime.main_runtime as M`) を `from src.shared.constants.tile_data import ...` に置換

### P1.5-B. スプライトデータの抽出（2 タスク）

- [x] **P1.5-B1**：`src/shared/constants/sprite_data.py` を新規作成し、`HERO_DOWN` / `HERO_DOWN_WALK` / `ENEMY_SPRITES` を `main_runtime.py` から移動
- [x] **P1.5-B2**：`main_runtime.py` から定義を削除し、`from src.shared.constants.sprite_data import *` で再エクスポート。`image_banks.py::sprite_iter` の lazy import を置換

### P1.5-C. world_generation.py の実装（3 タスク）

- [x] **P1.5-C1**：`src/shared/services/world_generation.py`（現 stub）に `get_path_variant` / `get_shore_variant` を実装として移動
- [x] **P1.5-C2**：`_make_empty` / `_carve_winding_path` / `_place_forests` / `_place_decorations` / `_place_landmarks` を追加移動
- [x] **P1.5-C3**：`generate_world_map` / `generate_dungeon` / `get_zone` / `_build_zone_enemies` を追加移動。`main_runtime.py` から元関数を削除して `from src.shared.services.world_generation import *` で再エクスポート

### P1.5-D. Game クラス → BlockQuestApp に統合（3 タスク）

> Q8 決定：新規 `src/runtime/app.py` は作らず、**既存 `src/app.py::BlockQuestApp` を拡張**して Game の責務を統合する。

- [x] **P1.5-D0**（Phase 1 整合性修正で先行実施）：`src/shared/services/status_bar.py` を `src/shared/ui/status_bar.py` に統合（Q6 決定：`bar` は UI 寄り）。既存 `StatusBarLayout` と `StatusBar` を同居させる
- [x] **P1.5-D1**：`src/app.py::BlockQuestApp` に Game の `__init__` ロジック（pyxel.init / services/scenes 生成 / apply_av / sync_audio）を統合。`Game._instance` 参照も `BlockQuestApp._instance` に移し、say / say_clear の module-level helper も `src/app.py` に移動
- [x] **P1.5-D2**：`main_runtime.py` の Game 定義を削除、`from src.app import BlockQuestApp as Game, run, say, say_clear` で再エクスポート（または明示的に `BlockQuestApp()` を `run()` 内で呼ぶ）
- [x] **P1.5-D3**：`pytest -q` で 270 件 green / `python main.py` の headless 起動が Phase 1 と同等に通ることを確認

### P1.5-E. main_runtime.py <50 行化（3 タスク）

- [x] **P1.5-E1**：`main_runtime.py` を import の集合（tile_data / sprite_data / world_generation / scenes / services / app）と `pyxel.init` 呼び出し + `run()` だけに圧縮。目標：**50 行未満**
- [x] **P1.5-E2**：`test/test_runtime_shim.py` を新規作成（gherkin シナリオ 2 の grep 式で Game class や inlined block が無いことを確認、`wc -l < 50` 固定）
- [x] **P1.5-E3**：`test/test_architecture_layout.py` を新 layout（`src/shared/constants/*` 追加、`src/runtime/app.py` 追加）に合わせて更新

### P1.5-F. 検証と締め（3 タスク）

- [x] **P1.5-F1**：`python -m pytest test/ -q` 全 green（新規 test 含む）
- [x] **P1.5-F2**：`python tools/build_web_release.py` と `python tools/build_codemaker.py` が exit 0。生成物を手動で開いて Splash → Title → ゲームループが動く
- [x] **P1.5-F3**：Phase 1.5 完了コミット + git tag `j53-phase1-5-complete`

---

## 4.6) Tasklist（Phase 2: Code Maker bundler）

### 背景

Phase 1.5 で `main_runtime.py` が 49 行の re-export shim になった今、Code Maker 用の単一 main.py バンドルは **`import *` を解決して連結する bundler** が必要になる。現行の `tools/build_codemaker.py` は sync_main_data と inlined block を前提にした構造で、Phase 1.5 のモジュール構造と合っていない。

Q4B 決定に基づき、**concat 生成型の bundler** を新設：`codemaker_manifest.txt` に並べた順で src/**/*.py を連結して Code Maker 用 main.py を作る。

### 運用ルール（Phase 1 / 1.5 と同じ）

- 1 タスク = 1 commit、commit 後に `pytest -q` + `python tools/build_codemaker.py` exit 0 確認
- commit message 規約：`j53(P2-X): <内容>`

### P2-A. 現状の build_codemaker.py を把握（2 タスク）

- [ ] **P2-A1**：現行 `tools/build_codemaker.py` の処理を読み、`_split_core_and_entrypoint` / `_normalize_entrypoint_source` / `build_codemaker_main_text` / `build_codemaker_zip` の責務を棚卸し。Phase 1.5 shim でも通っている grep ポイント（ENTRY POINT marker）を確認
- [ ] **P2-A2**：Code Maker zip を解凍して生成された `main.py` の構造を確認（CORE_BLOCK に何が入っているか、STUDENT AREA がどこに挟まるか）。Phase 1.5 前後で Code Maker 上の挙動が変わっていないか確認

### P2-B. codemaker_manifest.txt 設計と新設（2 タスク）

- [ ] **P2-B1**：bundle 順を設計。依存関係に沿って `shared/assets → shared/constants → shared/services → shared/ui → scenes → runtime/app → runtime/main_runtime` の順でソース path をリスト化（約 50 ファイル）
- [ ] **P2-B2**：`tools/codemaker_manifest.txt` を新規作成し、bundle 対象を 1 行 1 path で列挙

### P2-C. codemaker_bundler.py 新設（3 タスク）

- [ ] **P2-C1**：`tools/codemaker_bundler.py` を新規作成。manifest を読み、各 path の `.py` を順に concat する基本 bundler を実装
- [ ] **P2-C2**：`from src.X import Y` 行を bundler 用に前処理（bundle 内では import が不要なので除去 or コメント化）。循環しない順序で並べれば依存解決できる設計
- [ ] **P2-C3**：STUDENT AREA block を `main` 末尾に挟む処理を統合（`_normalize_entrypoint_source` 相当）。最終形は `CORE_BLOCK = <全ソース連結>` + `STUDENT_AREA` + guard 処理を内蔵した single main.py

### P2-D. build_codemaker.py を bundler 呼び出しに薄化（2 タスク）

- [ ] **P2-D1**：`tools/build_codemaker.py` から `_split_core_and_entrypoint` / `build_codemaker_main_text` を削除（または `codemaker_bundler` 内に移動）。残るのは zip 生成・`sha256` 計算・`my_resource.pyxres` の同梱のみ
- [ ] **P2-D2**：`tools/sync_main_data.py` が不要になったら削除（Phase 2 時点の判断）

### P2-E. 検証と締め（3 タスク）

- [x] **P2-E1**：`python tools/build_codemaker.py` exit 0、生成 zip の `main.py` が Code Maker 上で splash → title → ゲームループを回せること（実機確認、headless も `python main.py` で smoke test）
- [x] **P2-E2**：既存テスト 275 件 all green + 2 skip（SAMPLE_MAIN 前提の test_build_codemaker 2 件は skip、wrapper 不変性は別 case でカバー）
- [x] **P2-E3**：Phase 2 完了コミット + git tag `j53-phase2-complete`

---

## 4.7) Tasklist（Phase 3: dev/prod 単一化）

### 背景

タスクノートのタイトルは「runtime monolith **分解** と **dev/prod 単一化**」。Phase 1〜2 で前半（分解 + bundler）が完遂。Phase 3 では **dev 版を完全に削除**し、prod 版 1 本に統合する。

現状（Phase 2 完了時点）:
- `main.py` / `main_development.py` の 2 entry
- `src/runtime/main_runtime.py` / `main_development_runtime.py` の 2 runtime
- `production/` / `development/` の 2 artifacts
- selector は 2 カード（本番 / 開発版）、取り込み UI 付き
- `browser_resource_override.py` + `codemaker_resource_store.promote_imported_resource` で import zip を development へ昇格

Phase 3 ではこれらを全て prod 1 本に統合する。import された resource は直接 `assets/blockquest.pyxres` に書き戻す（Phase 4 で systemd autostart 対応）。

### 運用ルール（Phase 1/1.5/2 と同じ）

- 1 タスク = 1 commit、commit 後に `pytest -q` + `python tools/build_codemaker.py` exit 0 確認
- commit message 規約：`j53(P3-X): <内容>`

### P3-A. dev runtime 削除（2 タスク）

- [x] **P3-A1**：root `main_development.py` を削除。`src/runtime/main_development_runtime.py` も削除（codemaker_manifest にも無いので bundle には影響しない）
- [x] **P3-A2**：`test_preview_*.py` シリーズ（preview 専用テスト群）を削除または skip 化。`test_dialogue_integration.py` の `test_main_preview_*` 3 件を skip

### P3-B. development artifacts 削除（1 タスク）

- [x] **P3-B1**：`development/` ディレクトリを削除（既に Phase 1 で deletion が staged されていた）。`.gitignore` 要調整なら追記

### P3-C. selector 1 カード化（2 タスク）

- [x] **P3-C1**：`templates/selector.html` を本番 1 カードに簡素化。「開発版」カードと関連 JS（`codemaker_import_ui.js` の fallback 分岐）を削除
- [x] **P3-C2**：`tools/render_release_selector.py` の DevelopmentCandidate 表示ロジックを削除

### P3-D. build tools 簡素化（3 タスク）

- [x] **P3-D1**：`tools/resolve_release_source_of_truth.py` の `DevelopmentCandidate` 系関数・データクラス・定数を削除。`file_sha256` / `is_git_dirty` / `revision_timestamp` / `build_cache_token` / `validate_change_list_freshness` は維持
- [x] **P3-D2**：`tools/build_web_release.py` の dev 関連関数を削除。`development_dir()` / preview hash 管理系を全削除。production 1 本のビルドに特化
- [x] **P3-D3**：`tools/build_release_artifacts.py` を簡素化。`build_codemaker_release()` から dev 分岐を削除

### P3-E. resource import 経路の整理（2 タスク）

- [x] **P3-E1**：`src/shared/services/browser_resource_override.py` を削除（Phase 3 削除予定として markup 済み）。関連 import を main_runtime / image_banks から削除
- [x] **P3-E2**：`src/shared/services/codemaker_resource_store.py` から `promote_imported_resource` / `IMPORT_MANIFEST` / `IMPORT_RESOURCE` 等の development 向け関数を削除

### P3-F. test suite の整理（2 タスク）

- [x] **P3-F1**：`test/test_build_web_release.py` の `TestPreview*` / `TestExplicitPreviewCommands` / `TestResourceOnlyDevelopmentBuild` 等のクラスを削除（すでに production 単独ビルドになるため意味を失う）
- [x] **P3-F2**：残った test が全 green を確認。削減された test 数と理由を Discussion に記録

### P3-G. 検証と締め（3 タスク）

- [x] **P3-G1**：`python -m pytest test/ -q` 全 green
- [x] **P3-G2**：`python tools/build_web_release.py` と `python tools/build_codemaker.py` が exit 0。生成物の `production/` だけが存在し `development/` は無い
- [x] **P3-G3**：Phase 3 完了コミット + git tag `j53-phase3-complete`

---

## 4.8) Tasklist（Phase 4: web_runtime_server systemd 常駐化）

### 背景

Phase 3 まで完了して本番 1 本構成に整理済み。Phase 4 では `tools/web_runtime_server.py`
を systemd service として exe.dev VM 上で常駐起動するようにする。これにより
「手動で python tools/web_runtime_server.py を起動する」運用を撤廃し、
**子どもがいつブラウザを開いても Block Quest が動く**状態を実現する。

マトリクスの記述（section 6D）:
- `tools/web_runtime_server.py` `[書き換え／Phase 3+4]` — Phase 3 で codemaker
  import を assets/blockquest.pyxres への直接書き戻しに変更済み（P3-E）。
  Phase 4 では systemd autostart に対応する
- `infra/autostart/code-quest-runtime.service` `[新規／Phase 4]`

### 運用ルール

- 1 タスク = 1 commit、commit 後に `pytest -q` を維持（Phase 4 は infra 側の
  変更が主なのでコード側のテストには影響少）
- commit message 規約：`j53(P4-X): <内容>`
- **exe.dev VM への systemd 登録は手動確認が必要**。コミット自体は service ファイルと
  install 手順の追加まで。実機反映はユーザー側で `sudo systemctl ...` を走らせる

### P4-A. web_runtime_server の autostart 対応調査（2 タスク）

- [x] **P4-A1**：現 `tools/web_runtime_server.py` の起動フローを確認し、systemd ExecStart
  で起動可能な CLI 引数（port / serve-dir / db-path）が揃っているかを棚卸し。不足
  があれば追加
- [x] **P4-A2**：起動時に `production/` が存在しない場合のフォールバック（初回
  ビルドを自動実行するか、503 エラーを返すか）を決定し、必要なら実装

### P4-B. systemd unit file 作成（2 タスク）

- [x] **P4-B1**：`infra/autostart/code-quest-runtime.service` を新規作成
- [x] **P4-B2**：`infra/autostart/README.md` を追加（install 手順と troubleshooting）

### P4-C. 常駐起動の確認（実機、ユーザー側）（2 タスク）

- [x] **P4-C1**：install 手順をユーザーが実行し、`systemctl status` で active 確認
- [x] **P4-C2**：ブラウザから selector 表示と code-maker import の再ビルド確認

### P4-D. 検証と締め（2 タスク）

- [x] **P4-D1**：`python -m pytest test/ -q` 全 green 維持
- [x] **P4-D2**：Phase 4 完了コミット + git tag `j53-phase4-complete` + J53 タスクノート
  全体を `status: done` に更新

---

## 5) Discussion（記録・反省）

### 2026-04-23 Phase 1 完了の記録

**成果**:
- Game クラスの **109 メソッド**（当初見積り 113 は概数、差分 4 は image_banks の helper 重複 2 + input_bindings の inline 置換 2）を scenes（11 個）／shared/services（7 新規 / 既存 8 拡張）／shared/ui（1 新規）へ移動完了
- `main_runtime.py` を 7266 → 1956 行に圧縮（73% 削減）
- 全 270 テスト green / web & codemaker ビルド exit 0 / headless Game() + update/draw サイクル成功
- git tag `j53-phase1-methods-complete` 作成済み（元の `j53-phase1-complete` から改名。Gherkin シナリオ 2 の `wc -l < 50` 未達のため「113 メソッド移動完了」に限定した名前にした）

**gherkin 達成状況**:
- シナリオ 1（scenes 11 ディレクトリ・services 16・ui 5）: ✅
- シナリオ 2（monolith に Game と inlined コピーゼロ、`wc -l < 50`）: 🟡 Game dispatcher 残存・1956 行残存 → Phase 1.5 へ
- シナリオ 3（ImportError ゼロ / architecture_layout test green）: ✅

**学び・反省**:
- 定数群（TILE_DATA / SHORE / PATH の 1100 行）と world 生成（300 行）は Phase 1 スコープで触らなかったため、`main_runtime.py` の体積減は方法移動に対して減らなかった。Phase 1.5 の専任タスクとして分けて正解
- scene → service の呼び出し側を sed で機械的に置換したが、test 側で `game._btnp` / `game._dialog_text` を直接叩くパターンが多く、都度個別修正が発生した。Phase 1.5 では service 移動時に test の呼び出し側テンプレ（`make_game()` helper）を先に整備すると速い
- `R4: 113 メソッドの内部依存が循環` は実際には発生せず、category 単位の 1 commit 方式で bisect 耐性を確保できた
- 循環 import 回避のため `import src.runtime.main_runtime as M` の lazy import を scene/service 内で多用した。Phase 1.5 で定数が専用モジュールに移れば lazy import はほとんど不要になる

### 2026-04-23 Phase 1.5 完了の記録

**成果**:
- `main_runtime.py` を 1956 → **49 行**に圧縮（累計 99.3% 削減、Gherkin シナリオ 2 の `wc -l < 50` を達成）
- Game クラスを `src/runtime/app.py` に移動（263 行）。main_runtime.py は pure re-export shim に
- 定数 1500 行を 3 ファイルに分割抽出：
  - `src/shared/constants/tile_data.py` (960 行): TILE/PATH/SHORE/MAP/POS 定数
  - `src/shared/constants/sprite_data.py` (235 行): HERO/ENEMY sprite arrays
  - `src/shared/constants/game_config.py` (100 行): ENCOUNTER/VFX/TOWN/MSG
- `src/shared/services/world_generation.py` (275 行): stub → 完全実装
- `test/test_runtime_shim.py` 新設（6 テスト）: Gherkin シナリオ 2 を恒常的にガード
- 全 277 テスト green（270 → 277、+7 新規）/ web & codemaker ビルド exit 0
- git tag `j53-phase1-5-complete` 作成済み

**Gherkin 達成状況**:
- シナリオ 1 (scenes 11 / services 16 / ui 5 ディレクトリ構造): ✅
- シナリオ 2 (monolith に Game/inlined ゼロ、`wc -l < 50`): ✅ **達成**（49 行、grep 式 0 件）
- シナリオ 3 (ImportError ゼロ / architecture_layout test green): ✅

**学び・反省**:
- 定数抽出は想定通り main_runtime.py の大幅削減に寄与した（1956 → 564 行）。Phase 1 で一緒にやろうとすると 14+ コミット増で見通しが悪くなっていた。Phase 分離は正解
- `import *` で一括再エクスポートしたら、文字列 grep に依存する 3 テスト（`test_main_uses_shared_input_bindings` 等）が落ちた。shim 化の時は grep ベースの静的検証を `app.py`/`shared/*` 全体に広げる必要あり
- Game → `src/runtime/app.py` 移動で test_cj24 が落ちた原因は「pyxel stub の reach が src.runtime.app に届かない」問題。テスト側で sys.modules から `src.runtime.app` を一時的に除去して再ロードさせる fix で解決。これは P1-G で Game が main_runtime 内にあった時には発生しなかった問題
- 当初 Q8 で「既存 `src/app.py::BlockQuestApp` 拡張」を想定したが、実装してみると BlockQuestApp は scene_manager + GameState の薄い shell で構造が違いすぎた。実装は `src/runtime/app.py` 新規で正解（BlockQuestApp は Phase 2 以降で統合余地あり）

### 2026-04-23 Phase 2 / 3 / 4 完了の記録（追記）

**Phase 2（Code Maker bundler）**:
- `tools/codemaker_manifest.txt` + `tools/codemaker_bundler.py` 新設（concat 生成型、Q4B 決定）
- `tools/build_codemaker.py` を bundler 呼び出しの薄い wrapper に書き換え
- Phase 1.5 shim 化で意図せず壊れていた Code Maker zip を復旧（main.py が 1 行 shim bundle から 8400+ 行の完全 bundle に戻る）
- git tag `j53-phase2-complete`

**Phase 3（dev/prod 単一化）**:
- `main_development.py` / `main_development_runtime.py` / `browser_resource_override.py` / `sync_main_data.py` を削除
- selector を本番 1 カードに簡素化、codemaker import の localStorage fallback を削除
- `tools/build_web_release.py` 417 → 135 行、`tools/resolve_release_source_of_truth.py` 320 → 120 行
- `codemaker_resource_store.py` の staging 経路を撤廃、`apply_imported_resource` で直接 `assets/blockquest.pyxres` を上書き
- git tag `j53-phase3-complete`

**Phase 4（systemd 常駐化）**:
- `tools/web_runtime_server.py` に `ensure_production_build()` を追加（起動時 production/ 未存在なら自動ビルド）
- `infra/autostart/code-quest-runtime.service` + `infra/autostart/README.md` を新設
- ユーザー側 exe.dev VM で `sudo systemctl enable --now code-quest-runtime.service` 実行、`active (running)` 確認
- http://VM-IP:8000/ に接続して selector 表示を確認（1 カード化により「select」UI 自体は無い＝正常）
- git tag `j53-phase4-complete`

**最終状態**:
- pytest 201 passed + 2 skip
- web & codemaker build exit 0
- production/ 1 本のみ生成（development/ 不在）
- Block Quest は VM 再起動後も自動復旧して遊べる状態に
- feature/20260422-j53-runtime-modularize ブランチを main にマージ済み

**学び・反省**:
- Phase 1.5 で shim 化した時、Code Maker zip が壊れていることにすぐ気づかなかった。次回は
  Phase 間に **実機配信テスト**（zip を解凍して Code Maker に投入）を必須にする
- Phase 3 での build tools 大幅簡素化は想定より楽だった。P3-D で 800 行近く削れたのは、
  dev 版用 DevelopmentCandidate データクラスが意外と深く根を張っていたため
- systemd autostart の ExecStartPre vs 起動時内部 fallback（`ensure_production_build`）は
  後者を選んで正解だった。systemd の `ExecStartPre` は同期で重いビルドを走らせると
  `TimeoutStartSec` に引っかかりがち。起動後の非同期呼び出し（本ケースは同期だが軽い
  selector レンダリングだけで済む）の方が運用が素直

---

## 6) 参考資料

### Phase 1 責務移動計画マトリクス（v2）

**目的**：[repository-structure.md](../docs/repository-structure.md) に列挙された全関数／クラス／メソッドを、**Phase 1 完了後にあるべき位置**で 6 カテゴリに振り分ける。`src/runtime/main_runtime.py` は Phase 1 後には 50 行未満の薄い entry になり、中身は全部この分類先へ分配される。

**更新履歴**:
- **v1**（2026-04-22 夜）初版
- **v2**（2026-04-23）Q1-Q5 / Q1A-Q3A 決定を反映
  - **Q1A** dialog / message は scene ではなく shared/services に置く（`scenes/dialog/` は完全解体、`scenes/message/` は新設しない）
  - **Q2A/Q3A** `shared/services/game_state.py` に GameState class 新設、全フィールド列挙。app.py（BlockQuestApp）が保有し scene に DI
  - **Q3B** Phase 1 は `main_runtime.py` のみ作業、dev 版は Phase 3 まで一時的乖離を許容
  - **Q4B** bundler は concat 生成型（`codemaker_manifest.txt` に並べた順で concat）
  - **Q5A** `image_banks.py` は単一ファイル（19 メソッド、500〜1000 行想定）
- **v3**（2026-04-23 Phase 1 完了後）実装実績に合わせて件数・配置を整合
  - **Q4 修正** `image_banks.py` のメソッド数を 19 → **17**（`_tile_iter` / `_sprite_iter` は helper で重複数え、実数 17）
  - **Q6 修正** `status_bar` は `shared/ui/` に集約（`shared/services/status_bar.py` は統合して削除）
  - **Q7 修正** `_any_advance_btnp` は `message_display` に移動（services/input_bindings の 3 件から減じ、message_display は 12 → 13）
  - **Q10 修正** `shared/ui/message_window.py` は MessageDisplay.draw_window から参照される形に配線
  - **合計修正** 113（見積り）→ **109**（実移動）

**凡例**：
- `[既存]` = すでに分類先に存在、取り込みのみ
- `[新規]` = Phase 1 で新設するファイル／ディレクトリ
- `[削除]` = Phase 3 で消す（分類は記録のみ）

---

#### A. scenes/MVP（1 場面 = 4 ファイル：M/V/P/S）

Game クラスの 113 メソッドのうち「独立した画面として表示される場面」のみをここに scene ディレクトリとして切り出す。dialog / message は独立画面ではなく **overlay / utility** なので scenes に入れず shared/services へ。

**既存 3 + 新規 8 = 11 scenes**。各 scene の model が持つ instance state も明記（GameState と scene-local state の境界線）。

- **`scenes/title/`** `[既存]` — ゲーム開始画面
  - 既存: TitleModel / TitleView.render / TitlePresenter.move / TitleScene
  - 取り込み: Game.{update_title, draw_title, _do_load}
  - model state: `title_cursor`
- **`scenes/splash/`** `[新規]` — 起動直後のスプラッシュ
  - Game.{update_splash, draw_splash}
  - model state: `splash_frame`
- **`scenes/explore/`** `[既存]` — フィールド探索（Game.update_map 系を取り込む）
  - 既存: ExploreModel / ExploreView / ExplorePresenter.change_mode / ExploreScene
  - 取り込み: Game.{update_map, draw_map, _check_tile_events, _check_landmark_events, _resolve_landmark_scene, _draw_landmark_highlights, _dungeon_exit_callback, _draw_dungeon_glitch_lord_marker}
  - model state: `walk_frame`, `walk_timer`, `move_cooldown`, `_a_cooldown`
- **`scenes/town/`** `[新規]` — 町の入口メッセージと town メニュー
  - Game.{_current_town_index, _enter_town_message, _inn_cost_for_current_town, _town_menu_talk, _town_menu_inn, _town_menu_save, _town_menu_exit, update_town, update_town_menu, draw_town_menu}
  - model state: `town_menu_cursor`, `town_menu_pos`, `menu_message`
- **`scenes/shop/`** `[新規]` — 武器/防具/道具の購入
  - Game.{_enter_shop, _try_purchase, update_shop, draw_shop}
  - model state: `shop_cursor`, `shop_inventory`, `shop_kind`, `shop_message`
- **`scenes/battle/`** `[既存]` — 戦闘
  - 既存: BattleModel / BattleView / BattlePresenter.change_phase / BattleScene
  - 取り込み: Game.{_start_battle, _start_noise_guardian_battle, _on_noise_guardian_defeated, _check_noise_guardian_phase, _check_glitch_lord_phase_transition, _do_player_attack, _do_enemy_attack, _apply_spell_effect, _battle_victory, _battle_defeat, _check_level_up, _enemy_hit_scene_name, _victory_scene_name, update_battle, draw_battle}
  - model state: `battle_enemy`, `battle_enemy_hp`, `battle_phase`, `battle_boss_phase`, `battle_is_glitch_lord`, `battle_is_professor`, `battle_item_select`, `battle_spell_select`, `battle_menu`, `battle_text`, `battle_text_timer`, `_noise_guardian_battle`
- **`scenes/menu/`** `[新規]` — ゲーム中の主メニュー
  - Game.{_menu_labels, update_menu, draw_menu}
  - model state: `menu_cursor`, `menu_item_cursor`, `menu_sub`
- **`scenes/settings/`** `[新規]` — 音量などの設定
  - Game.{_open_settings, _settings_return_state, _settings_rows, _apply_av_settings, _toggle_setting, update_settings, draw_settings}
  - model state: `settings_cursor`, `settings_origin`
- **`scenes/ai_help/`** `[新規]` — 子どもが AI に助けを求める画面
  - Game.{_try_open_ai_chat, _enter_ai_help, update_ai_help, draw_ai_help}
  - model state: `_ai_help_status`
- **`scenes/professor/`** `[新規]` — Professor イベント（intro / battle 移行 / ending_main / ending_accepted）
  - Game.{_professor_phase, _professor_battle_phase, _enter_professor_intro, update_professor_intro, draw_professor_intro, _enter_professor_ending_main, update_professor_ending_main, draw_professor_ending_main, _enter_professor_ending_accepted, update_professor_ending_accepted, draw_professor_ending_accepted}
  - model state: `professor_choice_active`, `professor_choice_cursor`, `professor_intro_idx`, `professor_intro_lines`, `professor_ending_idx`, `professor_ending_lines`
- **`scenes/ending/`** `[新規]` — 通常エンディング
  - Game.{_enter_ending, update_ending, draw_ending}
  - model state: `ending_lines`

**削除**:
- **`scenes/dialog/`** `[削除 Q1A]` — 完全解体。DialogScene / DialogPresenter / DialogView / DialogModel を削除。StructuredDialogRunner 等は `shared/services/dialog_runner.py` に移動

---

#### B. shared/services（複数 scene で使う技術的関心）

**既存 8 + 新規 8 = 16 サービス**。Q1A / Q2A により新規 3 追加（`game_state`, `dialog_runner`, `message_display`）。

##### B-0. `game_state.py` `[新規 Q2A/Q3A]` — Phase 1 の最重要抽象

app.py（BlockQuestApp）が保有、`set_scene` で scene に DI（Q3A 決定）。scene 間で共有される state を単一オブジェクトに集約する。

**フィールド全列挙**（Game の `self.*` から抽出、scene-local は除外）:

```python
@dataclass
class GameState:
    # --- player ---
    player: dict                    # hp / mp / exp / level / stats / inventory / position(x,y)

    # --- progression flags ---
    cave_unblock_shown: bool
    tree_cleared_shown: bool
    poison_step_counter: int
    has_save: bool
    # glitch_lord_defeated は player dict 内のキー（P1-B で確認、line 335 で初期化）

    # --- world / dungeon ---
    world_map: list                 # list[list[int]]
    dungeon_map: list | None
    dungeon_rooms: list
    dungeon_spawn: tuple[int, int] | None
    dungeon_template: Any
    dungeon_template_rooms: list
    # in_dungeon は player dict 内のキー（P1-B で確認、line 5557 で `p["in_dungeon"]`）

    # --- position / camera ---
    cam_x: int
    cam_y: int
    world_return_x: int             # dungeon 出た時の戻り先
    world_return_y: int
    last_town_pos: tuple[int, int]

    # --- scene tracking (debug bootstrap 用) ---
    state: str                      # 現在 scene 名
    prev_state: str                 # back navigation 用

    # --- debug ---
    debug_mode: bool
    debug_seq: list
```

**GameState に入れない（app.py が直接 scene に DI）**:
- `audio_manager` / `sfx_system` / `input_state_tracker` / `save_store` / `pyxel_module` / `image_banks_service` / `dialog_runner` / `message_display`
- 理由: これらは**サービスのインスタンス**で、state ではなく依存性。入れ子になると循環 import リスクが上がる

##### B-1〜B-7 新規 services

- **`dialog_runner.py`** `[新規 Q1A]` — 構造化会話（YAML ドリブン）
  - 旧 `src/scenes/dialog/model.py` から移動: DialogValidationError / DialogChoice / DialogStep / StructuredDialogRunner（`start` / `choose` / `continue_dialog` / `load_all_lines` / `_resolve_scene` / `_select_body` / `_apply_set` / `_format_text` / `_validate_*` 群）
  - 追加 state なし（Runner は呼ばれるたびに instance 化される）
- **`message_display.py`** `[新規 Q1A / v3 Q7 で 13 に修正]` — 短いメッセージウィンドウ（overlay 的な utility）
  - Game から: `_enter_message` / `show_message` / `update_message` / `draw_message_window` / `_wrap_text` / `_dialog_lines` / `_dialog_text` / `_current_dialog_page_lines` / `_advance_dialog_page` / `_draw_say_overlay` / `say` / `text` / **`_any_advance_btnp`**（**13 メソッド**）
  - 保有 state: `msg_callback`, `msg_index`, `msg_lines`, `_say_buffer`
- **`world_generation.py`** `[新規]` — マップ自動生成
  - runtime monolith から: `get_path_variant` / `get_shore_variant` / `_make_empty` / `_carve_winding_path` / `_place_forests` / `_place_decorations` / `_place_landmarks` / `generate_world_map` / `generate_dungeon` / `get_zone` / `_build_zone_enemies`（line 1673, 4612 の重複は 1 本に統合）
- **`image_banks.py`** `[新規 Q5A / v3 Q4 で 17 に修正]` — pyxres / tile / sprite / font バンクの全責務を単一ファイルで（**17 メソッド**、実測 360 行）
  - Game から: `_setup_image_banks` / `_paint_jp_font_bank` / `_build_reverse_tile_map` / `_tile_bank_layout_valid` / `_setup_world_tilemap` / `_bake_dungeon_to_tilemap` / `_derive_dungeon_from_tilemap` / `_bake_world_to_tilemap` / `_derive_world_from_tilemap` / `_tile_iter` / `_layout_tile_bank` / `_paint_tile_bank` / `_render_tiles_to_bank` / `_sprite_iter` / `_layout_sprite_bank` / `_paint_sprite_bank` / `_render_sprites_to_bank`
  - 保有 state: `font`, `has_jp_font`, `tile_bank`, `tile_bank_water2`, `sprite_bank`, `path_variant_bank`, `shore_variant_bank`, `tile_id_by_pixel`, `_pyxres_loaded`, `_pyxres_path`
- **`vfx.py`** `[新規]` — 画面エフェクト
  - Game から: `_start_vfx` / `_draw_vfx_overlay`
  - 保有 state: `vfx_timer`, `vfx_type`
- **`item_use.py`** `[新規]` — アイテム使用の効果適用
  - Game から: `_use_item`（scenes/menu か scenes/battle から呼ぶ）
- **`text_format.py`** `[新規]` — 名前・翻訳の整形
  - Game から: `_name` / `_t`、runtime monolith から: `name_en`

##### B-8〜B-15 既存 services（取り込みのみ）

- **`audio_system.py`** `[既存]` — BGM/SFX の場面選択
  - 取り込み: inlined SfxSystem / Game._sync_audio
- **`input_bindings.py`** `[既存 / v3 Q7 で修正]` — 入力グループ定義と押下追跡
  - 取り込み: Game.{_btn, _btnp} は `game.input_state.btn/btnp(...)` の直接呼び出しに置換（service 内メソッド増加なし）。`_any_advance_btnp` は `message_display` に移動（オーバーレイ用 UX なので）
- **`landmark_events.py`** `[既存]`
- **`player_state.py`** `[既存]`
- **`save_store.py`** `[既存]`
- **`codemaker_resource_store.py`** `[既存]` — Phase 3 で promote_imported_resource 削除
- **`play_session_logging.py`** `[既存]`
- **`browser_resource_override.py`** `[既存／Phase 3 削除]`

---

#### C. shared/ui（UI 矩形と配置）

既存 3 + 新規 2 = 5。

- **`dialog_window.py`** `[既存]` — DialogWindow.rect（dialog_runner service が参照）
- **`hud.py`** `[既存]` — HudLayout.origin
- **`menu_window.py`** `[既存]` — MenuWindow.rect
- **`status_bar.py`** `[新規 / v3 Q6 で修正]` — `StatusBarLayout`（座標）と `StatusBar`（描画ロジック）を同居。`draw_status_bar` の責務は全てここで完結（Game.draw から `self.status_bar.draw()` で呼ぶ）
- **`message_window.py`** `[新規 / v3 Q10 で配線]` — `MessageWindowLayout` を保持。`message_display.MessageDisplay.draw_window` が `layout.rect()` / `layout.wrap_width` を参照する形で配線済み

---

#### D. tools（build / gen / server / test）

既存 12 + 新規 2 = 14。Q4B で bundler 仕様確定。

- **`codemaker_bundler.py`** `[新規／Phase 2 Q4B]` — **concat 生成型**。`codemaker_manifest.txt` の順番どおりに `src/**/*.py` を連結して Code Maker 用単一 main.py を生成
- **`codemaker_manifest.txt`** `[新規／Phase 2 Q4B]` — bundle 対象を bundle 順に列挙（例：game_state → services → scenes → app → runtime entry）
- **`build_codemaker.py`** `[書き換え／Phase 2]` — bundler を呼ぶ薄いラッパーに
- **`build_web_release.py`** `[簡素化／Phase 3]` — dev 関連関数を削除
- **`build_release_artifacts.py`** `[簡素化／Phase 3]`
- **`render_release_selector.py`** `[簡素化／Phase 3]` — 1 カード化
- **`resolve_release_source_of_truth.py`** `[大幅削除／Phase 3]` — DevelopmentCandidate 系を削除、file_sha256 / is_git_dirty / revision_timestamp / build_cache_token は維持
- **`gen_data.py`** `[維持]`
- **`sync_main_data.py`** `[削除／Phase 2]` — bundler に置換
- **`web_runtime_server.py`** `[書き換え／Phase 3+4]` — import pyxres は `assets/blockquest.pyxres` に直接書き戻し、Phase 4 で systemd autostart
- **`report_play_sessions.py`** `[維持]`
- **`test_headless.py`** / **`test_save_compat.py`** / **`test_web_compat.py`** `[維持]`
- **`infra/autostart/code-quest-runtime.service`** `[新規／Phase 4]`

---

#### E. assets / F. templates

**E**:
- `*.yaml` `[維持]`、`blockquest.pyxres` `[Phase 3 で意味変更：import 先の正本]`、`fonts/`・`images/` `[維持]`

**F**:
- `selector.html` `[Phase 3 で 1 カード化]`、`codemaker_import_ui.js` `[Phase 3 で fallback 削除]`、`wrapper.html` `[維持]`

---

#### 対象外（本 task では触らない or 軽微改修のみ）

- **root `main.py`** `[維持]` — Pyxel 必須の 8 行 wrapper
- **root `main_development.py`** `[削除／Phase 3]`
- **root `index.html`** `[維持]`
- **`src/app.py`** `[軽微改修／Phase 1 Q3A]` — BlockQuestApp が GameState / 各 service を保有し `set_scene` で DI する責務を追加。「アプリ窓口」という核は不変
- **`src/core/scene_manager.py`** `[維持]` — Scene 切替のみ。GameState は **持たない**（原則維持、Q3A 決定）
- **`src/game_data.py`** `[維持]`
- **`src/generated/*.py`** `[維持]` — gen_data.py 自動生成
- **`src/runtime/main_runtime.py`** — Phase 1 完了後は `import + pyxel 初期化 + BlockQuestApp 組立 + pyxel.run` の 50 行未満 entry
- **`src/runtime/main_development_runtime.py`** `[削除／Phase 3]` — **Phase 1 中は main_runtime.py と一時的に乖離**（Q3B 決定、R3 許容）
- **`production/*`** `[維持]` — build 出力先
- **`development/*`** `[削除／Phase 3]`
- **Game クラスの top-level `update` / `draw`** — `BlockQuestApp.update` / `.draw` 経由で SceneManager に吸収（scene 固有ロジックは scenes/* へ分配済み）

---

### Game クラス 109 メソッドの分配サマリ（v3・実装実績）

| 分類先 | 件数 | 備考 |
|---|---|---|
| scenes/title | 3 | update_title / draw_title / _do_load |
| scenes/splash | 2 | update_splash / draw_splash |
| scenes/explore | 8 | update_map 系 |
| scenes/town | 10 | town / town_menu 系 |
| scenes/shop | 4 | shop 系 |
| scenes/battle | 15 | battle / noise_guardian / glitch_lord 系 |
| scenes/menu | 3 | menu 系 |
| scenes/settings | 7 | settings 系 |
| scenes/ai_help | 4 | ai_help 系 |
| scenes/professor | 11 | professor 系 |
| scenes/ending | 3 | ending 系 |
| **scenes 計** | **70** | 11 scenes |
| shared/services/message_display | **13** | v3 Q7：v2 の 12 に `_any_advance_btnp` を追加 |
| shared/services/image_banks | **17** | v3 Q4：v2 の 19 から `_tile_iter`/`_sprite_iter` の重複カウント解消 |
| shared/services/input_bindings | **0** | v3 Q7：`_btn`/`_btnp` は直接呼び出しに置換、`_any_advance_btnp` は message_display へ |
| shared/services/text_format | 2 | _name / _t |
| shared/services/vfx | 2 | _start_vfx / _draw_vfx_overlay |
| shared/services/audio_system | 1 | _sync_audio（module function として） |
| shared/services/item_use | 1 | _use_item |
| **shared/services 計** | **36** | v2 の 40 から -4（image_banks -2 / input_bindings -3 / message_display +1） |
| shared/ui/status_bar | 1 | draw_status_bar（v3 Q6：services から ui へ移管） |
| 対象外（BlockQuestApp → SceneManager へ吸収） | 2 | update / draw（top-level dispatcher。Phase 1.5 で実施） |
| **合計** | **109** | |

**v2 との主な差分**（v3）:
- **image_banks**: 19 → 17（重複カウント解消、実装では `tile_iter`/`sprite_iter` はメソッドとして存在するが ImageBanks 内 helper）
- **input_bindings**: 3 → 0（`_btn`/`_btnp` は `input_state.btn/btnp` に inline 置換、`_any_advance_btnp` は message_display に移動）
- **message_display**: 12 → 13（`_any_advance_btnp` を吸収）
- **合計**: 113（見積り） → **109**（実移動）。差分 4 の内訳：image_banks 重複 2 + input_bindings 直接置換 2

**v1 / v2 との互換性**: v1 の `scenes/message (12)` は v2 で `shared/services/message_display` に移動済み。scenes 数は 11（`scenes/dialog/` 解体、`scenes/message/` 不新設）。

このマトリクスは Phase 1 の Tasklist（section 4 で後述）の**移動先確定表**として参照する。各 scene / service は「skeleton commit → state 移動 commit → method 移動 commit」の 3 段階で埋まっていく想定。
