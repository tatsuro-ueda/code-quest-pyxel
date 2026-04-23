# リポジトリ構造定義書

## 1. 目的

この文書は「どの file / 関数が何を担当するか」を固定する責務分担表である。`docs` と `code` がずれたら **未実装 / バグ / 仕様ずれ** として扱い、コードではなくこの文書を正本とする（AI が読める分担表の維持は [CJ37](customer-journeys.md) 「責務が曖昧で直すほど別の所が壊れる」のガードレール）。

## 2. 設計原則

- `src/` と `assets/` を source of truth にする
- `production/` は source ではなく **配布物の置き場**
- root `main.py` / `main_development.py` は 8 行の wrapper（runtime 本体は `src/` 側）
- `Pyxel Code Maker` は子どもの正式な編集面
- image bank は `.pyxres` 往復、`Sound / Music` は Code Maker → code 側 audio asset に取り込んでから runtime
- runtime は Pyxel の「単一 main.py」制約を受けるので bundler で concat する（手で inlined コピーは維持しない）
- Scene は MVP パターン（model / view / presenter / scene）。scene 横断 state は `GameState` に集約して DI

## 3. 全体構造

```text
/
├─ index.html                 親子の入口（selector）
├─ main.py                    8 行 wrapper、src/runtime/main_runtime.py を exec
├─ main_development.py        8 行 wrapper（J53 Phase 3 で削除予定）
├─ src/                       ソース正本
│  ├─ app.py                  BlockQuestApp（scene_manager + GameState 保持の薄い shell）
│  ├─ game_data.py            YAML 生成物の読み出し口
│  ├─ core/                   Scene プロトコル・SceneManager
│  ├─ scenes/                 11 scene の MVP 実装
│  ├─ shared/
│  │  ├─ services/            16 サービス（scene 横断のロジック／state）
│  │  ├─ ui/                  描画レイアウト helper
│  │  ├─ constants/           タイル・スプライト・ゲーム設定の定数
│  │  └─ assets/              埋め込み asset データ（jp_font_data 等）
│  ├─ generated/              YAML → Python の自動生成物（手で触らない）
│  └─ runtime/                Pyxel 単一ファイル制約の受け皿
│     ├─ main_runtime.py              49 行の re-export shim
│     ├─ app.py                       Game クラス本体（263 行）と entry point
│     └─ main_development_runtime.py  旧 monolith、Phase 3 で削除
├─ assets/                    人が直す正本（YAML / .pyxres / フォント）
├─ tools/                     build / 配布 / データ生成 / 検証
├─ test/                      pytest（36 ファイル）
├─ templates/                 build 前 HTML テンプレート
├─ production/                承認済み配布物
└─ docs/                      本文書を含むドキュメント群
```

## 4. ディレクトリ詳細

### 4.1 `src/app.py`

- **class BlockQuestApp**：アプリ全体の窓口。`GameState` と scene_manager を保持
  - `set_scene(name)`：Scene を差し替え、`GameState.state / prev_state` を更新
  - `update() / draw()`：現在 Scene に委譲

### 4.2 `src/game_data.py`

YAML 生成物を runtime に供給する読み出し口。
- `load_enemies / load_items / load_weapons / load_armors / load_spells / load_shops / load_dialogue`
- `glitch_lord_phase(hp_ratio)`：HP 比から Glitch Lord の phase 名を返す
- `_build_zone_enemies`：enemies list をゾーン別 dict に索引化

### 4.3 `src/core/scene_manager.py`

- **class Scene(Protocol)**：`update / draw` を持つ最小 IF
- **class SceneManager**：現在 Scene のみを保持。GameState は持たない（app.py が保有）

### 4.4 `src/scenes/`（11 scene、MVP パターン）

各 scene ディレクトリは `model.py / view.py / presenter.py / scene.py / __init__.py` で構成する。

| Scene | 責務 | scene-local state（model 保有） |
|---|---|---|
| `splash/` | 起動スプラッシュ | `splash_frame` |
| `title/` | タイトル画面・設定開閉 | `title_cursor` |
| `explore/` | フィールド / ダンジョン歩行 | `walk_frame, walk_timer, move_cooldown, _a_cooldown` |
| `town/` | 町メニュー（宿・店・会話・セーブ） | `town_menu_cursor, town_menu_pos, menu_message` |
| `shop/` | 武器・防具・道具の売買 | `shop_cursor, shop_inventory, shop_kind, shop_message` |
| `battle/` | 戦闘全体（通常・ボス・Noise Guardian） | `battle_enemy, battle_phase, battle_text, battle_item_select` ほか 12 フィールド |
| `menu/` | メニュー画面 | `menu_cursor, menu_item_cursor, menu_sub` |
| `settings/` | AV・操作設定 | `settings_cursor, settings_return_state` |
| `ai_help/` | Glitch Lord 戦の AI ヘルプ | - |
| `professor/` | Professor 戦 intro / ending | `professor 系 6 state` |
| `ending/` | エンディング | - |

**共通原則**：
- `model.py` は state の保持だけ。pyxel 呼び出しは禁止
- `view.py::render` は model を描画用 dict に整形するだけ。save / logging / build は禁止
- `presenter.py` は入力を model 操作に変換するだけ。scene 外の永続化は禁止
- `scene.py` は MVP を束ねる薄い層

### 4.5 `src/shared/services/`（16 サービス）

**scene 横断の state／ロジック**。単一 scene の状態は持たない。

| ファイル | 責務 | 主要 class / 関数 |
|---|---|---|
| `game_state.py` | scene 間共有 state を集約 | `@dataclass GameState`（19 フィールド） |
| `audio_system.py` | BGM / SFX の scene 選択・再生 | `AudioManager`, `SfxSystem`, `choose_bgm_scene`, `sync_audio`, melody/bass/drum slot |
| `dialog_runner.py` | YAML ドリブン構造化会話 | `StructuredDialogRunner`, `DialogStep`, `DialogChoice`, `DialogValidationError` |
| `message_display.py` | 短メッセージ overlay | `MessageDisplay`（say / show_message / wrap_text 等） |
| `image_banks.py` | Pyxel image bank レイアウト | `ImageBanks`（tile_bank / sprite_bank / jp_font bank） |
| `input_bindings.py` | 入力判定・フレーム差分 | `InputStateTracker`, `any_btn`, `any_btnp` |
| `landmark_events.py` | 座標接触イベント | `LandmarkEvent`, `find_landmark_*`, `resolve_scene` |
| `player_state.py` | player dict の生成・復元 | `create_initial_player`, `dump_snapshot`, `restore_snapshot`, `exp_for_level`, `stats_for_level` |
| `save_store.py` | セーブ先差分の吸収 | `SaveStore(Protocol)`, `InMemory/File/LocalStorageSaveStore`, `make_save_store` |
| `world_generation.py` | ワールド／ダンジョン生成 | `generate_world_map`, `generate_dungeon`, `get_zone`, `get_path_variant`, `_place_*` |
| `vfx.py` | ダメージ等の視覚エフェクト | `VfxSystem`（保有 state: `vfx_timer, vfx_type`） |
| `item_use.py` | アイテム使用ロジック | `use_item` |
| `text_format.py` | 表示名整形・翻訳 | `TextFormat`, `name_en`, `NAME_EN_MAP` |
| `play_session_logging.py` | Web プレイ記録の sqlite 永続化 | `start_session`, `heartbeat_session`, `end_session`, `summarize_sessions` |
| `codemaker_resource_store.py` | Code Maker zip の採否・保管 | `import_codemaker_resource_zip`, `promote_imported_resource`, manifest 管理 |
| `browser_resource_override.py` | localStorage 経由の pyxres 復元 | `stage_browser_imported_resource`（Phase 3 で削除） |

**GameState に入れないもの（app.py が直接 scene に DI）**：
`AudioManager / SfxSystem / InputStateTracker / SaveStore / ImageBanks / DialogRunner / MessageDisplay / VfxSystem / TextFormat / StatusBar` — これらは **サービスインスタンス**（依存性）であり state ではない。入れ子にすると循環 import リスクが上がる。

### 4.6 `src/shared/ui/`

描画レイアウト helper（座標計算のみ。pyxel 描画は scene / service 側）。

| ファイル | 提供 |
|---|---|
| `dialog_window.py` | `DialogWindow.rect`（会話ウィンドウ矩形） |
| `menu_window.py` | `MenuWindow.rect`（メニュー矩形） |
| `message_window.py` | 短メッセージウィンドウの矩形 |
| `hud.py` | `HudLayout.origin`（HUD 基準座標） |
| `status_bar.py` | `StatusBar`（HP/MP/lvl 表示、service 的役割） |

### 4.7 `src/shared/constants/`

コード側の正本として固定する定数（YAML 化の対象ではない）。

| ファイル | 内容 |
|---|---|
| `tile_data.py` | タイル定義・`_PATH_VARIANTS`・`_SHORE_VARIANTS`・`_ZONE_DECORATIONS` |
| `sprite_data.py` | HERO / ENEMY スプライトのピクセル配列 |
| `game_config.py` | 画面サイズ等のゲーム設定 |

### 4.8 `src/shared/assets/`

Python コードに埋め込む asset データ。

| ファイル | 内容 |
|---|---|
| `jp_font_data.py` | `JP_FONT_LAYOUT`（日本語ビットマップフォント） |

### 4.9 `src/generated/`（自動生成、手で触らない）

`tools/gen_data.py` が `assets/*.yaml` から一方向生成する。
`dialogue.py / enemies.py / items.py / weapons.py / armors.py / spells.py / shops.py`

### 4.10 `src/runtime/`

Pyxel の「単一 main.py」制約の受け皿。

| ファイル | 行数 | 責務 |
|---|---|---|
| `main_runtime.py` | 49 | **re-export shim**。test / Code Maker bundler / 旧 import の互換用。module-level 名前を `src.shared.services.*` / `src.scenes.*` / `src.runtime.app` から再エクスポート |
| `app.py` | 263 | **Game クラス本体**（`__init__ / start / update / draw` の 4 メソッド）、say / say_clear module helper、`run()` entry |
| `main_development_runtime.py` | 7328 | 旧 monolith（Phase 3 で削除） |

**原則**：runtime 側には業務ロジックを書かない。ロジックはすべて scenes / shared/services に配置し、runtime は組み立てと dispatcher だけに徹する。

## 5. その他のトップレベル

### 5.1 `assets/`（人が直す正本）

`*.yaml`（敵・アイテム・呪文・店・武具・会話）、`blockquest.pyxres`、`umplus_j10r.bdf`、`screenshots/`

### 5.2 `tools/`

| ファイル | 責務 |
|---|---|
| `build_web_release.py` | production / development の Web 配布物生成。`build_web_release`, `build_development_release`（Phase 3 削除）, `approve_development`（同）, `promote` |
| `build_codemaker.py` | Code Maker 用 zip 生成。`build_codemaker_main_text`, `build_codemaker_zip`（Phase 2 で bundler 呼び出しに書き換え） |
| `build_release_artifacts.py` | 配布成果物の staging と prune。`stage_release`, `write_wrapper_outputs`, `prune_*`, `build_codemaker_release` |
| `render_release_selector.py` | selector / wrapper の HTML 展開。`generate_wrapper`, `generate_selector`, `generate_top_selector`, `load_top_page_changes`, `versioned_asset_url` |
| `resolve_release_source_of_truth.py` | dev / prod 判定。`DevelopmentCandidate`, `resolve_development_candidate`, `build_cache_token`, `build_development_change_list`（DevelopmentCandidate 系は Phase 3 で削除） |
| `gen_data.py` | `assets/*.yaml` → `src/generated/*.py` の一方向生成。`generate_one`, `_write_generated_module` |
| `sync_main_data.py` | monolith に inlined を貼り戻す（Phase 2 で bundler に置換） |
| `web_runtime_server.py` | 配布 + session API + resource import API の同居サーバー（Phase 4 で systemd 常時起動） |
| `report_play_sessions.py` | sqlite のプレイ記録を人間可読に |
| `test_headless.py` | 起動のみ確認 |
| `test_save_compat.py` | save 互換検証 |
| `test_web_compat.py` | Playwright で配布 HTML 互換確認 |
| `hooks/` | pre/post commit hook |

### 5.3 `test/`

36 ファイルの pytest。`test_architecture_layout.py` が shared/services の配置・inline コピーの不在を検証する。

### 5.4 `templates/`

build 前テンプレート（完成 HTML は置かない）。
`selector.html` / `codemaker_import_ui.js` / `wrapper.html`

### 5.5 `production/`

承認済み本番配布物（source は置かない）。
`index.html / play.html / pyxel.html / pyxel.pyxapp / code-maker.zip`

### 5.6 `docs/`

| ファイル | 役割 |
|---|---|
| `customer-jobs.md` | 顧客のジョブと好循環の定義 |
| `customer-journeys.md` | 43 カスタマージャーニーとソリューション構成 |
| `product-requirements-*.md` | 6 分野の gherkin（av / battle / guardrails / map / narrative / platform） |
| `repository-structure.md` | 本文書 |
| `framework-rule.md` | 設計ルール |

## 6. 依存関係のルール

### 6.1 レイヤー依存

```
runtime/ (app.py)
   ↓ DI
scenes/ ──┐
          ├→ shared/services/
shared/ui ┘    ↓
         shared/constants/, shared/assets/, generated/
```

**禁止**：
- `shared/services/` → `scenes/` / `runtime/`
- `shared/ui/` → `shared/services/`（ui は座標計算のみ）
- `core/scene_manager.py` が GameState を持つ
- scene 同士が直接 import する（共有は GameState / services 経由）

### 6.2 循環依存の禁止

GameState は **dataclass の values のみ** を持ち、サービスインスタンスは入れない。サービスは app.py から DI で渡す。

## 7. 責務の線引き（書かないべきこと）

- `app.py` に戦闘ロジックを書く
- `scene_manager.py` にプレイヤー状態を持たせる
- `model.py` に `pyxel.blt()` を書く
- `view.py` に save / logging / build を書く
- `presenter.py` に scene 外の永続化を書く
- `shared/services` が単一 scene の scene-local state を持つ
- `audio_system.py` にメロディ / SE の定義そのものを正本として置く（YAML or Code Maker の正本に任せる）
- `codemaker_resource_store.py` が「どの場面でどの音を鳴らすか」を決める
- `assets/` に build 済みファイルを置く
- `templates/` に完成 HTML を置く
- `production/` に source を置く
- `.pyxres` を AI が直接編集する前提にする
- runtime monolith の inlined コピーを **手で維持する**（Phase 2 以降は bundler の自動生成のみ）

## 8. 使用ライブラリ

| ライブラリ | 主な場所 | 責務 |
|---|---|---|
| Pyxel | `src/runtime/*.py`, root `main*.py`, build 系 | 実行 / 描画 / 音、`package` / `app2html` |
| pytest | `test/` | 自動検証 |
| sqlite3 | `src/shared/services/play_session_logging.py` | Web プレイ記録 |
| Playwright | `tools/test_web_compat.py` | 配布 HTML 互換確認 |
| Pyodide JS bridge | `src/shared/services/save_store.py`, `browser_resource_override.py` | browser 側 save / import 橋渡し |
| 標準ライブラリ | `tools/`, `src/shared/services/` | build / packaging / メタ処理 |

## 9. 現状と残タスク（J53）

**Phase 1 完了**：runtime monolith を scenes（11）／shared/services（16）／shared/ui（5）／shared/constants（3）／shared/assets（1）へ分解。`main_runtime.py` は 7266 → **49 行**（99.3% 削減）。

**Phase 1.5 完了**：Game クラスを `src/runtime/app.py` に抽出（263 行、4 メソッド）。`main_runtime.py` は re-export shim に圧縮。

**残タスク**：

| Phase | 内容 |
|---|---|
| **Phase 2** | Code Maker 用 bundler を導入し、zip 生成時だけ concat する形へ（`sync_main_data.py` を置換） |
| **Phase 3** | `main_development*.py` / `DevelopmentCandidate` / `development/` 配布 / 承認ゲートを廃止、`assets/blockquest.pyxres` を唯一の正本に |
| **Phase 4** | `tools/web_runtime_server.py` を systemd user unit で常時起動 |
| **Phase 5** | CJ26 note を再開、artifact 一致 regression テストを追加 |
