# リポジトリ構造定義書

> **この文書の役割**：人用の詳細リファレンス（リポジトリ構造 + ディレクトリ規約 + 責務分担表）。AI も必要時にここを参照する。
>
> **上位文書（最優先・自動 load）**：[../AGENTS.md](../AGENTS.md)（≤100 行、AI 用エントリポイント）
>
> **規約本体（M1〜M5 詳細）**：[framework-rule.md](framework-rule.md)

## 1. 目的

この文書は「どの file / 関数が何を担当するか」を固定する責務分担表である。`docs` と `code` がずれたら **未実装 / バグ / 仕様ずれ** として扱い、コードではなくこの文書を正本とする（AI が読める分担表の維持は [CJ37](customer-journeys.md) 「責務が曖昧で直すほど別の所が壊れる」のガードレール）。

## 2. 設計原則

- `src/` と `assets/` を source of truth にする
- `dist/` は source ではなく **配布物の置き場**
- root `main.py` は 8 行の wrapper（runtime 本体は `src/runtime/app.py` 側。`main_development.py` は Phase 3 で廃止済）
- `Pyxel Code Maker` は子どもの正式な編集面
- image bank は `.pyxres` 往復、`Sound / Music` は Code Maker → code 側 audio asset に取り込んでから runtime
- runtime は Pyxel の「単一 main.py」制約を受けるので bundler で concat する（手で inlined コピーは維持しない）
- Scene は MVP パターン（model / view / presenter / scene）。scene 横断 state は `GameState` に集約して DI

## 3. 全体構造

```text
/
├─ index.html                 子ども向けピクセルアート系トップページ（プレイ導線）
├─ main.py                    8 行 wrapper、src/runtime/main_runtime.py を exec
├─ src/                       ソース正本
│  ├─ game_data.py            YAML 生成物の読み出し口
│  ├─ scenes/                 11 scene の MVP 実装
│  ├─ shared/
│  │  ├─ services/            18 サービス（scene 横断のロジック／state）
│  │  ├─ state/               PlayerModel など scene 横断 Model（M4-4）
│  │  ├─ ui/                  描画レイアウト helper
│  │  ├─ constants/           タイル・スプライト・ゲーム設定の定数
│  │  └─ assets/              埋め込み asset データ（jp_font_data 等）
│  ├─ generated/              YAML → Python の自動生成物（手で触らない）
│  └─ runtime/                Pyxel 単一ファイル制約の受け皿（**実行入口**）
│     ├─ main_runtime.py              47 行の re-export shim（test / Code Maker bundler 互換用）
│     └─ app.py                       Game クラス本体（326 行）と entry point（**実装の窓口**）
├─ assets/                    人が直す正本（YAML / .pyxres / フォント / screenshots / essay-manga.jpg）
├─ tools/                     build / 配布 / データ生成 / 検証 / architecture rules CLI
├─ test/                      pytest（102 ファイル / 717 tests）
├─ templates/                 build 前 HTML テンプレート
├─ dist/                承認済み配布物
├─ steering/                  task note（done/ にアーカイブ済み）
└─ docs/                      本文書を含むドキュメント群
```

## 3.5 build の起動方法（runbook）

> AI（Claude）と人間の両方が「毎回迷わずに」 build を再生できるための定型手順。
> BGM / pyxres / view / scene を変更した後は **必ず両方** を順番に実行する。
> （2026-05-07 追加：CJ44 確定版の運用安定化を目的に、build runbook を docs に明文化した）

### 3.5.1 dist/code-maker.zip だけを再生成する

```bash
python tools/build_codemaker.py
```

- 出力：`dist/code-maker.zip`（block-quest/main.py + my_resource.pyxres を梱包した教材版 zip）
- `tools/codemaker_manifest.txt` の順番で全 .py を 1 ファイルに inline する
- **PYTHONPATH 不要**（スクリプト先頭で `sys.path.insert(0, _HERE)` 済み）

### 3.5.2 dist/ 配下の全 release artifacts を再生成する

```bash
PYTHONPATH=. python tools/build_web_release.py
```

- 出力：`dist/code-maker.zip` / `dist/pyxel.html` / `dist/pyxel.pyxapp` / `dist/play.html` / `dist/index.html`
- 内部で `tools/build_codemaker.py` も呼ぶので、上の 3.5.1 を別途実行する必要はない
- **PYTHONPATH=. が必要な理由**：`tools/build_release_artifacts.py` が
  `from tools.build_codemaker import build_codemaker_zip` という形でパッケージ相対 import を行っているため、
  CWD（リポジトリ root）を `PYTHONPATH` に乗せる必要がある。
  `build_web_release.py` 自体は `sys.path.insert` で済ませているが、その先で読まれる
  `build_release_artifacts.py` が `tools.*` 名前空間で読まれるため

### 3.5.3 BGM / pyxres / view / scene を変更したときの順序

1. 変更を `src/` または `assets/` に commit する前にローカル検証：
   ```bash
   PYTHONPATH=. python -m pytest -x
   ```
2. release artifacts を再生成：
   ```bash
   PYTHONPATH=. python tools/build_web_release.py
   ```
3. bundle 内の `block-quest/main.py` に旧シンボル（例: `class AudioManager` / `class SettingsScene`）が
   残っていないかを Python で確認：
   ```bash
   python -c "import zipfile,re; z=zipfile.ZipFile('dist/code-maker.zip'); \
     t=z.read('block-quest/main.py').decode('utf-8'); \
     print('AudioManager:',len(re.findall(r'class AudioManager',t))); \
     print('SettingsScene:',len(re.findall(r'class SettingsScene',t))); \
     print('play_bgm_track:',len(re.findall(r'play_bgm_track\(',t)))"
   ```
4. `git status` で `dist/` 配下の差分のみが出ていることを確認（src 側は既に commit 済みのはず）

### 3.5.4 よくある落とし穴

- `python tools/build_release_artifacts.py` を直接叩くと `ModuleNotFoundError: No module named 'tools'` になる。
  必ず `PYTHONPATH=. python tools/build_web_release.py` の方を使うこと
- `dist/code-maker.zip` を Code Maker にロードして子どもが編集した結果を本編に戻したい場合は、
  `dist/code-maker.zip` ではなく `assets/blockquest.pyxres` を **直接 SSoT として更新** する
  （CJ44 確定版・BGM SSoT タスクで確定した方針）
- bundle に古い AudioManager / SettingsScene が残ったまま release した経歴があるので、毎回 3.5.3 の
  自己検査を回すこと

## 4. ディレクトリ詳細

### 4.1 `src/runtime/app.py`（**実装の窓口**）

- **class Game**：本プロジェクトのアプリ本体（pyxel 初期化＋全 Scene/Service の組み立て＋update/draw dispatcher）。
  - `__init__`：pyxel.init / フォント / SfxSystem / ImageBanks / GameState / PlayerModel / SceneManager（state holder）/ DebugService / 10 Scene を組み立てる（CJ44 確定版で `settings_scene` は撤去済、AudioManager も撤去済、`current_bgm` のような BGM 状態も Game には持たない）
  - **BGM の現在値**：`Game` クラスは BGM 状態を保持しない。冪等な BGM 再生は `src/shared/services/audio_system.py::play_bgm_track` 関数（モジュールスコープのプライベート変数 `_current_bgm_track` を使用）に集約されている。各 scene の `view.py::play_bgm` はこの関数を 1 行で呼ぶだけ
  - `start()`：`pyxel.run(self.update, self.draw)`
  - `update() / draw()`：現在 scene の update/draw を呼ぶ dispatcher
  - **property forward（M4-3 段階移行）**：`current_town` は `GameState.current_town` へ、`debug_mode / debug_seq` は `DebugService` へ、`state / prev_state` は `SceneManager` へ自動委譲する @property を持つ。`Game.__init__` が直接これらを `self.X = ...` で書くと static guard で fail する。

### 4.2 `src/game_data.py`

YAML 生成物を runtime に供給する読み出し口。
- `load_enemies / load_items / load_weapons / load_armors / load_spells / load_shops / load_dialogue`
- `glitch_lord_phase(hp_ratio)`：HP 比から Glitch Lord の phase 名を返す
- `_build_zone_enemies`：enemies list をゾーン別 dict に索引化

### 4.3 削除済み legacy runtime helper

- `src/app.py`：2026-05-09 に削除。Phase 1 由来の `BlockQuestApp` shell は不要になり、runtime root を `src/runtime/app.py::Game` に一本化した。
- `src/core/scene_manager.py`：2026-05-09 に削除。旧 Scene object manager は不要になり、scene 切替メタは `shared/services/scene_manager.py::SceneManager`（current / previous の 2 値 state holder）へ一本化した。

### 4.4 `src/scenes/`（11 scene、MVP パターン）

各 scene ディレクトリは `model.py / view.py / presenter.py / scene.py / __init__.py` で構成する。

| Scene | 責務 | scene-local state（model 保有） |
|---|---|---|
| `splash/` | 起動スプラッシュ | `splash_frame` |
| `title/` | タイトル画面 | `title_cursor` |
| `explore/` | フィールド / ダンジョン歩行 | `walk_frame, walk_timer, move_cooldown, _a_cooldown` |
| `town/` | 町メニュー（宿・店・会話・セーブ） | `town_menu_cursor, town_menu_pos, menu_message` |
| `shop/` | 武器・防具・道具の売買 | `shop_cursor, shop_inventory, shop_kind, shop_message` |
| `battle/` | 戦闘全体（通常・ボス・Noise Guardian） | `battle_enemy, battle_phase, battle_text, battle_item_select` ほか 12 フィールド |
| `menu/` | メニュー画面 | `menu_cursor, menu_item_cursor, menu_sub` |
| `ai_help/` | Glitch Lord 戦の AI ヘルプ | - |
| `professor/` | Professor 戦 intro / ending | `professor 系 6 state` |
| `ending/` | エンディング | - |

> 2026-05-07 改訂（CJ44 確定版）：`settings/` は撤去（演出 ON/OFF UI 廃止）。Scene は 10 個。

**共通原則**：
- `model.py` は state の保持だけ。pyxel 呼び出しは禁止
- `view.py::render` は model を描画用 dict に整形するだけ。save / logging / build は禁止
- `presenter.py` は入力を model 操作に変換するだけ。scene 外の永続化は禁止
- `scene.py` は MVP を束ねる薄い層

### 4.5 `src/shared/services/`（18 サービス）

**scene 横断の state／ロジック**。単一 scene の状態は持たない。

| ファイル | 責務 | 主要 class / 関数 |
|---|---|---|
| `game_state.py` | scene 間共有 state を集約（M4-3 圧縮済） | `@dataclass GameState`（13 フィールド：player_model / 進行 4 flag / world_return / cam / dungeon_template / current_town 等。`world_map / dungeon_map / dungeon_rooms` は撤去、pyxres = SSoT、Model 直読に移行） + `TownContext` |
| `scene_manager.py` | scene 切替メタを集約（M4-3） | `SceneManager`（current / previous の 2 値 state holder。Scene オブジェクト自体は持たない） |
| `debug_service.py` | デバッグ state を集約（M4-3） | `DebugService`（mode / seq / record_up / record_down / UUDD トグル） |
| `audio_system.py` | SFX 再生（pyxres SSoT、空 slot のみ fallback 書き込み）。BGM は各 scene の view.py が直接 `pyxel.playm` を呼ぶ（CJ44 確定版で `AudioManager` / `CHIPTUNE_TRACKS` / `choose_bgm_scene` / `sync_audio` は撤去済） | `SfxSystem`, `SFX_DEFINITIONS`, `SFX_CHANNEL`, `_slot_has_sound` ガード |
| `dialog_runner.py` | YAML ドリブン構造化会話 | `StructuredDialogRunner`, `DialogStep`, `DialogChoice`, `DialogValidationError` |
| `message_display.py` | 短メッセージ overlay | `MessageDisplay`（say / show_message / wrap_text 等） |
| `image_banks.py` | pyxres ロード / 初期化 / **fallback 焼き戻し**（pyxres 不在時のみ）/ pyxres 保存 | `ImageBanks`（`setup_image_banks` / `setup_world_tilemap` / `regenerate_world_tilemap_fallback` / `regenerate_dungeon_tilemap_fallback` / `paint_*` / `derive_dungeon_from_tilemap`）。**読み取りは Model 直読**（pyxel.tilemaps[0] / pyxel.images[n]）に移管済（2026-05-05 改訂） |
| `input_bindings.py` | 入力判定・フレーム差分 | `InputStateTracker`, `any_btn`, `any_btnp` |
| `landmark_events.py` | 座標接触イベント | `LandmarkEvent`, `find_landmark_*`, `resolve_scene` |
| `player_state.py` | legacy 互換 shim（M4-4 後半で縮退済） | test / bundle 互換のための `dump_snapshot`, `restore_snapshot`, `exp_for_level`, `stats_for_level`。**production の正本は `src/shared/state/player_model.py::PlayerModel`** |
| `save_store.py` | セーブ先差分の吸収 | `SaveStore(Protocol)`, `InMemory/File/LocalStorageSaveStore`, `make_save_store` |
| `world_generation.py` | 初回起動時のワールド／ダンジョン生成（pyxres 不在時の fallback でのみ呼ばれる。pyxres 在ればその tilemap を読む） | `generate_world_map`, `generate_dungeon`, `get_zone`, `get_path_variant`, `_place_*` |
| `vfx.py` | ダメージ等の視覚エフェクト | `VfxSystem`（保有 state: `vfx_timer, vfx_type`） |
| `item_use.py` | legacy item-use bridge | `PlayerModel.use_item()` の結果をメッセージ / SFX に変換する互換ブリッジ。production の item ルール本体ではない |
| `text_format.py` | 表示名整形・翻訳 | `TextFormat`, `name_en`, `NAME_EN_MAP` |
| `play_session_logging.py` | Web プレイ記録の sqlite 永続化 | `start_session`, `heartbeat_session`, `end_session`, `summarize_sessions` |
| `codemaker_resource_store.py` | Code Maker zip の採否・保管 | `import_codemaker_resource_zip`, `promote_imported_resource`, manifest 管理 |

**GameState に入れないもの（Game クラスが直接 scene に DI）**：
`SfxSystem / InputStateTracker / SaveStore / ImageBanks / DialogRunner / MessageDisplay / VfxSystem / TextFormat / StatusBar / DebugService / SceneManager` — これらは **サービスインスタンス**（依存性）であり state ではない。入れ子にすると循環 import リスクが上がる。

> 2026-05-07 改訂（CJ44 確定版・追加整理）：`AudioManager` は撤去。BGM は各 scene の view.py が `audio_system.play_bgm_track(target)` を呼ぶ（内部で `pyxel.playm` を冪等に発火）。BGM の現在値は `audio_system._current_bgm_track`（モジュールスコープ変数）に集約され、`Game.current_bgm` は持たない。

### 4.5.1 `src/shared/state/`（M4-4 で新設）

scene 横断の **Model**（service ではなく rule を持つ dataclass）。

| ファイル | 責務 |
|---|---|
| `player_model.py` | `PlayerModel`：HP/MP/EXP/装備/所持品/位置などプレイヤー state の正本。`apply_damage / heal / gain_exp / can_use_spell` などのルールを保持。GameState から `player_model` で参照される |

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

### 4.10 `src/runtime/`（**実行入口**）

Pyxel の「単一 main.py」制約の受け皿。runtime 側には業務ロジックを書かない（組み立てと dispatcher のみ）。

| ファイル | 行数 | 責務 |
|---|---|---|
| `main_runtime.py` | 47 | **re-export shim**。test / Code Maker bundler / 旧 import の互換用。module-level 名前を `src.shared.services.*` / `src.scenes.*` / `src.runtime.app` から再エクスポート |
| `app.py` | 326 | **Game クラス本体**（`__init__ / start / update / draw` ＋ M4-3 段階移行用 @property forward 4 種）、say / say_clear module helper、`run()` entry |

`main_development_runtime.py` は Phase 3 で削除済（2026-05-04）。`main_development.py` wrapper も同時に廃止し、配布物は `dist/` 一本化済（→ memory `single_distribution_policy`）。

## 5. その他のトップレベル

### 5.1 `assets/`（人が直す正本）

`*.yaml`（敵・アイテム・呪文・店・武具・会話）、`blockquest.pyxres`、`umplus_j10r.bdf`、`screenshots/`

### 5.2 `tools/`

| ファイル | 責務 |
|---|---|
| `build_web_release.py` | production / development の Web 配布物生成。`build_web_release`, `build_development_release`（Phase 3 削除）, `approve_development`（同）, `promote` |
| `build_codemaker.py` | Code Maker 用 zip 生成。`build_codemaker_main_text`, `build_codemaker_zip`（Phase 2 で bundler 呼び出しに書き換え） |
| `build_release_artifacts.py` | 配布成果物の staging と prune。`stage_release`, `write_wrapper_outputs`, `prune_*`, `build_codemaker_release` |
| `check_architecture_rules.py` | architecture rules checker の薄い CLI 入口 |
| `fix_architecture_rules.py` | architecture rules fixer の薄い CLI 入口 |
| `repair_architecture_rules.py` | architecture rules repair の薄い CLI 入口 |
| `architecture_rules/` | checker / fixer / repair の実装パッケージ |
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

102 ファイルの pytest（717 tests）。`test_architecture_layout.py` が shared/services の配置・inline コピーの不在を検証し、`test_cjg_framework_rule_guards.py` が M1〜M5 規約の static guard（AGENTS≤100 行、repository-structure.md 存在、Game クラスの deprecated field 復活防止、SSoT 違反検出など）をまとめて持つ。

### 5.4 `templates/`

build 前テンプレート（完成 HTML は置かない）。
`selector.html` / `codemaker_import_ui.js` / `wrapper.html`

### 5.5 `dist/`

承認済み本番配布物（source は置かない）。
`index.html / play.html / pyxel.html / pyxel.pyxapp / code-maker.zip`

### 5.6 `docs/` と上位文書

| ファイル | 役割 |
|---|---|
| `../AGENTS.md` | **AI 用最優先・自動 load・エントリポイント（≤100 行）**。`test_cjg_framework_rule_guards.py::test_agents_md_under_100_lines` で行数を保証 |
| `repository-structure.md`（本文書） | 人用詳細リファレンス（リポジトリ構造 + ディレクトリ規約 + 責務分担表） |
| `framework-rule.md` | 規約本体（M1〜M5 詳細根拠） |
| `customer-jobs.md` | 顧客のジョブと好循環の定義 |
| `customer-journeys.md` | カスタマージャーニーとソリューション構成 |
| `product-requirements-*.md` | 6 分野の gherkin（av / battle / guardrails / map / narrative / platform） |

AI / 人ともに `AGENTS.md` → 必要なら `repository-structure.md`（本文書）→ 必要なら `framework-rule.md` の順に降りる 2 層構造。詳細は `framework-rule.md::M5-3` を参照。

## 6. 依存関係のルール

### 6.1 レイヤー依存

```
runtime/app.py (Game)
   ↓ DI
scenes/ ──┐
          ├→ shared/services/
shared/state/   shared/ui/   shared/constants/   shared/assets/   generated/
   ↑                ↑
   └─ scenes / services はここを利用（state は Model、ui は座標計算）
```

**禁止**：
- `shared/services/` → `scenes/` / `runtime/`
- `shared/ui/` → `shared/services/`（ui は座標計算のみ）
- `shared/services/scene_manager.py` が Scene オブジェクトを保持する（state holder のみ）
- scene 同士が直接 import する（共有は GameState / services 経由）

### 6.2 循環依存の禁止

GameState は **dataclass の values のみ**（PlayerModel・進行 flag・座標等）を持ち、サービスインスタンスは入れない。サービスは `runtime/app.py::Game` から DI で渡す。

## 7. 責務の線引き（書かないべきこと）

- `runtime/app.py::Game` に戦闘ロジックを書く（scene の Model に置く）
- `shared/services/scene_manager.py::SceneManager` にプレイヤー状態を持たせる（state holder の current/previous 2 値だけ）
- `Game` クラス本体に M4-3 で移送済の deprecated field（`current_town / debug_mode / debug_seq / state / prev_state / world_map / dungeon_map / dungeon_rooms / cam_x / cam_y`）を `self.X = ...` で直接初期化する（@property フォワードのみ許可、static guard あり）
- `model.py` に `pyxel.blt()` を書く
- `view.py` に save / logging / build を書く
- `presenter.py` に scene 外の永続化を書く
- `shared/services` が単一 scene の scene-local state を持つ
- `image_banks.py` が pyxres / pyxel.tilemaps の **読み取り**を担う（読み取りは Model 直読、ImageBanks は書き込み・初期化・fallback のみ）
- `world_generation.py::generate_world_map` の戻り値を runtime / scene が手元に snapshot する（pyxres = SSoT）
- `audio_system.py` にメロディ / SE の定義そのものを正本として置く（YAML or Code Maker の正本に任せる）
- `codemaker_resource_store.py` が「どの場面でどの音を鳴らすか」を決める
- `assets/` に build 済みファイルを置く
- `templates/` に完成 HTML を置く
- `dist/` に source を置く
- `.pyxres` を AI が直接編集する前提にする
- runtime monolith の inlined コピーを **手で維持する**（bundler が自動生成）

## 8. 使用ライブラリ

| ライブラリ | 主な場所 | 責務 |
|---|---|---|
| Pyxel | `src/runtime/*.py`, root `main*.py`, build 系 | 実行 / 描画 / 音、`package` / `app2html` |
| pytest | `test/` | 自動検証 |
| sqlite3 | `src/shared/services/play_session_logging.py` | Web プレイ記録 |
| Playwright | `tools/test_web_compat.py` | 配布 HTML 互換確認 |
| Pyodide JS bridge | `src/shared/services/save_store.py`, `browser_resource_override.py` | browser 側 save / import 橋渡し |
| 標準ライブラリ | `tools/`, `src/shared/services/` | build / packaging / メタ処理 |

## 9. 現状と残タスク（J53 / M4 / M5）

**Phase 1 完了**：runtime monolith を scenes（11）／shared/services（18）／shared/state（1）／shared/ui（5）／shared/constants（3）／shared/assets（1）へ分解。`main_runtime.py` は 7266 → **47 行**（99.4% 削減）。

**Phase 1.5 完了**：Game クラスを `src/runtime/app.py` に抽出（326 行、`__init__` + `start/update/draw` + M4-3 段階移行用 @property forward 4 種）。`main_runtime.py` は re-export shim に圧縮。

**Phase 2 完了**：Code Maker 用 bundler を導入し、zip 生成時に concat する形へ移行（`sync_main_data.py` 置換）。

**Phase 3 完了**：`main_development_runtime.py` / `main_development.py` wrapper / DevelopmentCandidate / `development/` 配布 / 承認ゲートを廃止、`dist/` 一本化。`assets/blockquest.pyxres` が唯一の正本（→ memory `single_distribution_policy`）。

**M4-3 完了**（2026-05-05）：`current_town / cam_x / cam_y / dungeon_rooms / world_map / dungeon_map / debug_mode / debug_seq / state / prev_state` を Game クラスから移送。pyxres = SSoT を確立し、`bake_world_to_tilemap` を `regenerate_world_tilemap_fallback` にリネーム（pyxres 不在時 fallback 専用）。新 `DebugService` / `shared/services/scene_manager.py` を追加。`test_cjg_framework_rule_guards.py` で deprecated field 復活防止 static guard を整備。

**M4-4 継続移行**：`PlayerModel` 新設、scenes 側の `player_state` shim 利用は PlayerModel 直呼びに統合済。`item_use.py` は互換ブリッジへ縮退、`player_state.py` は test / bundle 互換 shim として残置。production の player ルール本体は `PlayerModel` に寄せた。

**2026-05-09 完了**：`src/app.py` と `src/core/scene_manager.py` を削除。Code Maker bundle もこの 2 file に依存しない形へ整理し、runtime root を `src/runtime/app.py::Game` に一本化した。

**M5-3 完了**：AGENTS.md ≤100 行制約・docs/repository-structure.md / docs/framework-rule.md の 2 層文書ナビを維持。人用詳細は役割どおり `repository-structure.md` 名に戻した。

**残タスク**：

| 項目 | 内容 |
|---|---|
| **M4-4 後半** | `player_state.py` の test / bundle 互換 shim をどこまで削れるか整理 |
| **systemd 常時起動** | `tools/web_runtime_server.py` の systemd user unit 化（→ memory `single_distribution_policy`） |
| **CJ26 / artifact 一致 regression** | Code Maker zip と本番 main.py の一致確認 |
