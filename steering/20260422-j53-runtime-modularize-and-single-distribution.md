---
status: in-progress
priority: high
scheduled: 2026-04-22T23:54:40+00:00
dateCreated: 2026-04-22T23:54:40+00:00
dateModified: 2026-04-22T23:54:40+00:00
tags:
  - task
  - j53
  - architecture
  - runtime
  - refactor
  - single-distribution
---

# 2026年4月22日 J53 runtime monolith 分解と dev/prod 単一化

> 状態：`in-progress`
> 次のゲート：（ユーザー）各フェーズ完了ごとに PR / コミットを確認する

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

### 今回の方針

- 「参考資料」セクションにある通りのディレクトリ構造にする

---

## 2) 改善対象gherkin（完了条件）

> スコープ：ディレクトリ構造のみ。挙動（ゲームが正しく動くか）や配信（build 出力）の完了条件は別 gherkin で扱う。本 gherkin はすべて `find` / `grep` / `ls` / AST parse で機械的に検証できる形に書く。

### シナリオ1：正常系（マトリクスどおりに新規ディレクトリとファイルが生えている）

> 🧱 Given: Phase 1 の作業が完了し、参考資料の分配マトリクスに従って monolith が分解されている。
> 🎬 When: `find src/scenes src/shared -type f -name '*.py'` でファイル一覧を取得する。
> ✅ Then: 以下がすべて存在する：
> - `src/scenes/{title, splash, explore, town, shop, battle, dialog, message, menu, settings, ai_help, professor, ending}/` の 13 ディレクトリ
> - 各 scene ディレクトリに `model.py / view.py / presenter.py / scene.py / __init__.py` の 5 ファイル
> - `src/shared/services/` に既存 8（`audio_system / input_bindings / landmark_events / player_state / save_store / codemaker_resource_store / play_session_logging / browser_resource_override`）+ 新規 5（`world_generation / image_banks / vfx / item_use / text_format`）の 13 `.py`
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

1. **inlined → import 置換**（monolith → shared/services、14 ブロック）
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
- 合計 **51 タスク**。見積もり：category あたり数十分〜2 時間、Phase 1 全体で 2〜3 日（集中作業時）

---

### P1-A. 準備（2 タスク）

- [ ] **P1-A1**：`grep -nE '^# === inlined' src/runtime/main_runtime.py` で inlined block の正確な行範囲と名前をメモ（14 blocks 想定）。結果を `tmp/inlined_blocks.txt` に保存
- [ ] **P1-A2**：`test/test_architecture_layout.py` の存在確認。あれば内容を読む、なければ P1-H5 で新設する方針を確定

### P1-B. Game instance state 棚卸し（3 タスク）

- [ ] **P1-B1**：`sed -n '4771,7234p' src/runtime/main_runtime.py | grep -oE 'self\.[a-zA-Z_][a-zA-Z_0-9]*' | sort -u` で Game 内の全 self フィールドを列挙（約 80 件）
- [ ] **P1-B2**：各 field を `{GameState / scene-local model / service 保有}` に分類。マトリクス v2 との diff があれば note を更新
- [ ] **P1-B3**：棚卸し結果を `tmp/state_inventory.md` に保存（P1-G 段階で参照）

### P1-C. inlined → import 置換（13 タスク）

各 task は「inlined block を削除 + `from src.shared... import ...` に置換」。commit 後 `pytest` green 確認。

- [ ] **P1-C1**：`input_bindings` block（line ~130）を削除 → `from src.shared.services.input_bindings import any_btn, any_btnp, InputStateTracker`
- [ ] **P1-C2**：`landmark_events` block → `from src.shared.services.landmark_events import ...`
- [ ] **P1-C3**：`player_factory` + `player_snapshot` 2 block → `from src.shared.services.player_state import ...`
- [ ] **P1-C4**：`save_store` block → `from src.shared.services.save_store import ...`
- [ ] **P1-C5**：`browser_resource_override` block → `from src.shared.services.browser_resource_override import ...`
- [ ] **P1-C6**：`sfx_system` block を `shared/services/audio_system.py` に吸収（`SfxSystem` class を追加）、inlined を import に置換
- [ ] **P1-C7**：`chiptune_tracks` block を `audio_system.py::_load_tracks` で使う形に統合、inlined を import に置換
- [ ] **P1-C8**：`scenes/dialog/model.py` block を **`shared/services/dialog_runner.py`** に移動（Q1A）。既存 `src/scenes/dialog/model.py` もここに統合して重複を解消
- [ ] **P1-C9**：`audio_system` block → `from src.shared.services.audio_system import ...`
- [ ] **P1-C10**：`game_data` block → `from src.game_data import ...`
- [ ] **P1-C11**：`generated/dialogue` block → `from src.generated.dialogue import ...`
- [ ] **P1-C12**：`jp_font_data` block を `image_banks.py` 内の class 定数として吸収（または `src/shared/assets/jp_font_data.py` に抽出）
- [ ] **P1-C13**：`grep '# === inlined' src/runtime/main_runtime.py` がゼロを確認。`wc -l src/runtime/main_runtime.py` で約 2500 行減っていることを確認

### P1-D. Game 外残存関数を services へ（2 タスク）

- [ ] **P1-D1**：新規 `src/shared/services/world_generation.py` を作成、Game 外の 11 関数（`get_path_variant` / `get_shore_variant` / `_make_empty` / `_carve_winding_path` / `_place_forests` / `_place_decorations` / `_place_landmarks` / `generate_world_map` / `generate_dungeon` / `get_zone` / `_build_zone_enemies`）を移動。**line 1673 / 4612 の `_build_zone_enemies` 重複を 1 本に統合**
- [ ] **P1-D2**：新規 `src/shared/services/text_format.py` を作成、runtime monolith の `name_en` を移動（Game 内の `_name` / `_t` は P1-G14 で移動）

### P1-E. skeleton 作成（4 タスク）

- [ ] **P1-E1**：新規 8 scenes（`splash` / `town` / `shop` / `menu` / `settings` / `ai_help` / `professor` / `ending`）の `model.py` / `view.py` / `presenter.py` / `scene.py` / `__init__.py` を空で作成（40 ファイル）。既存 `title` / `explore` / `battle` の skeleton は変更なし
- [ ] **P1-E2**：新規 6 services を空で作成：`game_state.py` / `dialog_runner.py`（P1-C8 でも触れる）/ `message_display.py` / `image_banks.py` / `vfx.py` / `item_use.py`
- [ ] **P1-E3**：新規 2 shared/ui を空で作成：`status_bar.py` / `message_window.py`
- [ ] **P1-E4**：`src/scenes/dialog/` を削除（Q1A 完全解体）。`dialog_runner` 実装は P1-C8 で `shared/services/` に移動済み

### P1-F. GameState 実装（2 タスク）

- [ ] **P1-F1**：`shared/services/game_state.py` に `@dataclass GameState` を定義（マトリクス v2 の 19 フィールド、`default_factory` 付き）
- [ ] **P1-F2**：`src/app.py::BlockQuestApp` が GameState を保有、`set_scene` で DI する形に改修。scene constructor に GameState 引数を追加（既存 scenes も含む）

### P1-G. Game メソッドを category 単位で移動（15 タスク）

各 task は「Game から該当メソッドを切り出し、target file に移動」。Q3A に従い **名前はそのまま**。scene に移す場合は `_update_map` 等 `_` 付きのままで OK。

- [ ] **P1-G1**：title 3 メソッド → `scenes/title/scene.py::TitleScene`、`title_cursor` state → `TitleModel`
- [ ] **P1-G2**：splash 2 メソッド → `scenes/splash/scene.py::SplashScene`、`splash_frame` state → `SplashModel`
- [ ] **P1-G3**：explore 8 メソッド → `scenes/explore/scene.py::ExploreScene`、`walk_frame` / `walk_timer` / `move_cooldown` / `_a_cooldown` → `ExploreModel`
- [ ] **P1-G4**：town 10 メソッド → `scenes/town/scene.py::TownScene`、`town_menu_cursor` / `town_menu_pos` / `menu_message` → `TownModel`
- [ ] **P1-G5**：shop 4 メソッド → `scenes/shop/scene.py::ShopScene`、shop 系 4 state → `ShopModel`
- [ ] **P1-G6**：battle 15 メソッド → `scenes/battle/scene.py::BattleScene`、battle 系 12 state → `BattleModel`
- [ ] **P1-G7**：menu 3 メソッド → `scenes/menu/scene.py::MenuScene`、menu 系 3 state → `MenuModel`
- [ ] **P1-G8**：settings 7 メソッド → `scenes/settings/scene.py::SettingsScene`、settings 系 2 state → `SettingsModel`
- [ ] **P1-G9**：ai_help 4 メソッド → `scenes/ai_help/scene.py::AiHelpScene`、`_ai_help_status` → `AiHelpModel`
- [ ] **P1-G10**：professor 11 メソッド → `scenes/professor/scene.py::ProfessorScene`、professor 系 6 state → `ProfessorModel`
- [ ] **P1-G11**：ending 3 メソッド → `scenes/ending/scene.py::EndingScene`、`ending_lines` → `EndingModel`
- [ ] **P1-G12**：message_display 12 メソッド → `shared/services/message_display.py::MessageDisplay`、`msg_callback` / `msg_index` / `msg_lines` / `_say_buffer` を service が保有
- [ ] **P1-G13**：image_banks 19 メソッド → `shared/services/image_banks.py::ImageBanks`、`font` / `tile_bank` / `sprite_bank` / `path_variant_bank` / `shore_variant_bank` / `tile_id_by_pixel` / `has_jp_font` / `_pyxres_loaded` / `_pyxres_path` / `tile_bank_water2` を service が保有
- [ ] **P1-G14**：vfx 2 + item_use 1 + text_format 2 を各 service に移動。vfx の `vfx_timer` / `vfx_type` state は vfx service が保有
- [ ] **P1-G15**：input 3（`_btn` / `_btnp` / `_any_advance_btnp`）を直接 `InputStateTracker` 呼び出しに置換。`_sync_audio` を `AudioManager` メソッドに移動。`draw_status_bar` は該当 scene 側に残す（座標は `shared/ui/status_bar.py` 参照）

### P1-H. Game class 削除 & entry 薄化（5 タスク）

- [ ] **P1-H1**：Game class に残存メソッドがゼロ（or top-level `update` / `draw` のみ）を `grep -c '^    def ' src/runtime/main_runtime.py` で確認
- [ ] **P1-H2**：Game class に残存 state がゼロを確認。漏れがあれば P1-G に戻って対応
- [ ] **P1-H3**：Game class 定義を削除。`update` / `draw` dispatcher は `BlockQuestApp.update` / `.draw` に統合済みとする
- [ ] **P1-H4**：`main_runtime.py` を書き換え：`import` + `run()` のみ、**50 行未満**
- [ ] **P1-H5**：`test/test_runtime_shim.py` を新規作成（gherkin シナリオ 2 の grep 式と `wc -l < 50` を固定）。`test/test_architecture_layout.py` を新 layout で書き換えまたは新規作成

### P1-I. 検証と締め（5 タスク）

- [ ] **P1-I1**：`python -m pytest test/ -q` 全 green
- [ ] **P1-I2**：`python -c 'import src.runtime.main_runtime'` 成功
- [ ] **P1-I3**：`python main.py` で実機 splash → title → ゲーム本編の **1 分動作確認**
- [ ] **P1-I4**：gherkin 3 シナリオを手動実行（`find` / `grep` / `wc` による機械検証）
- [ ] **P1-I5**：Phase 1 完了コミット + git tag `j53-phase1-complete`

---

## 5) Discussion（記録・反省）

（Phase 1 着手後、各 category 完了時に追記予定）

---

## 6) 参考資料

### Phase 1 責務移動計画マトリクス（v2）

**目的**：[architecture.md](../docs/architecture.md) に列挙された全関数／クラス／メソッドを、**Phase 1 完了後にあるべき位置**で 6 カテゴリに振り分ける。`src/runtime/main_runtime.py` は Phase 1 後には 50 行未満の薄い entry になり、中身は全部この分類先へ分配される。

**更新履歴**:
- **v1**（2026-04-22 夜）初版
- **v2**（2026-04-23）Q1-Q5 / Q1A-Q3A 決定を反映
  - **Q1A** dialog / message は scene ではなく shared/services に置く（`scenes/dialog/` は完全解体、`scenes/message/` は新設しない）
  - **Q2A/Q3A** `shared/services/game_state.py` に GameState class 新設、全フィールド列挙。app.py（BlockQuestApp）が保有し scene に DI
  - **Q3B** Phase 1 は `main_runtime.py` のみ作業、dev 版は Phase 3 まで一時的乖離を許容
  - **Q4B** bundler は concat 生成型（`codemaker_manifest.txt` に並べた順で concat）
  - **Q5A** `image_banks.py` は単一ファイル（19 メソッド、500〜1000 行想定）

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
    glitch_lord_defeated: bool
    has_save: bool

    # --- world / dungeon ---
    world_map: list                 # list[list[int]]
    dungeon_map: list | None
    dungeon_rooms: list
    dungeon_spawn: tuple[int, int] | None
    dungeon_template: Any
    dungeon_template_rooms: list
    # in_dungeon は dungeon_map is not None で派生

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
- **`message_display.py`** `[新規 Q1A]` — 短いメッセージウィンドウ（overlay 的な utility）
  - Game から: `_enter_message` / `show_message` / `update_message` / `draw_message_window` / `_wrap_text` / `_dialog_lines` / `_dialog_text` / `_current_dialog_page_lines` / `_advance_dialog_page` / `_draw_say_overlay` / `say` / `text`（12 メソッド）
  - 保有 state: `msg_callback`, `msg_index`, `msg_lines`, `_say_buffer`
- **`world_generation.py`** `[新規]` — マップ自動生成
  - runtime monolith から: `get_path_variant` / `get_shore_variant` / `_make_empty` / `_carve_winding_path` / `_place_forests` / `_place_decorations` / `_place_landmarks` / `generate_world_map` / `generate_dungeon` / `get_zone` / `_build_zone_enemies`（line 1673, 4612 の重複は 1 本に統合）
- **`image_banks.py`** `[新規 Q5A]` — pyxres / tile / sprite / font バンクの全責務を単一ファイルで（19 メソッド、500〜1000 行想定）
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
- **`input_bindings.py`** `[既存]` — 入力グループ定義と押下追跡
  - 取り込み: Game.{_btn, _btnp, _any_advance_btnp} は直接 InputStateTracker 呼び出しに置換
- **`landmark_events.py`** `[既存]`
- **`player_state.py`** `[既存]`
- **`save_store.py`** `[既存]`
- **`codemaker_resource_store.py`** `[既存]` — Phase 3 で promote_imported_resource 削除
- **`play_session_logging.py`** `[既存]`
- **`browser_resource_override.py`** `[既存／Phase 3 削除]`

---

#### C. shared/ui（UI 矩形と配置）

既存 3 + 新規 2 = 5（変更なし）。

- **`dialog_window.py`** `[既存]` — DialogWindow.rect（dialog_runner service が参照）
- **`hud.py`** `[既存]` — HudLayout.origin
- **`menu_window.py`** `[既存]` — MenuWindow.rect
- **`status_bar.py`** `[新規]` — Game.draw_status_bar の座標
- **`message_window.py`** `[新規]` — message_display の行幅・改行位置（_wrap_text が参照）

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

### Game クラス 113 メソッドの分配サマリ（v2）

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
| **scenes 計** | **70** | 11 scenes（v1 の 82 から -12） |
| shared/services/message_display | **12** | **v2 追加**：v1 の scenes/message 12 件をここへ移動 |
| shared/services/image_banks | 19 | pyxres / tile / sprite / font バンク系 |
| shared/services/input_bindings | 3 | _btn / _btnp / _any_advance_btnp |
| shared/services/text_format | 2 | _name / _t |
| shared/services/vfx | 2 | _start_vfx / _draw_vfx_overlay |
| shared/services/audio_system | 1 | _sync_audio |
| shared/services/item_use | 1 | _use_item |
| **shared/services 計** | **40** | v1 の 28 から +12 |
| shared/ui/status_bar（描画は scene 側） | 1 | draw_status_bar |
| 対象外（BlockQuestApp → SceneManager へ吸収） | 2 | update / draw（top-level dispatcher） |
| **合計** | **113** | |

**v1 との主な差分**: v1 の `scenes/message (12)` を v2 で `shared/services/message_display (12)` に移動。scenes 数は 12 → 11（`scenes/dialog/` 解体、`scenes/message/` 不新設）。

このマトリクスは Phase 1 の Tasklist（section 4 で後述）の**移動先確定表**として参照する。各 scene / service は「skeleton commit → state 移動 commit → method 移動 commit」の 3 段階で埋まっていく想定。
