# アーキテクチャ

## 1. 目的

この文書は「どの file / 関数が何を担当するか」を固定する責務分担表です。`docs` と `code` がずれたら **未実装 / バグ / 仕様ずれ** として扱い、コードではなくこの文書を正本とみなします（AI が読める分担表の維持は [CJ37](customer-journeys.md#cj37-責務が曖昧で直すほど別の所が壊れる) そのもの）。

## 2. 設計原則

- `src/` と `assets/` を source of truth にする
- `production/` と `development/` は source ではなく **配布物の置き場**
- root `main.py` / `main_development.py` は薄い wrapper（runtime 本体は `src/` 側）
- `Pyxel Code Maker` は子どもの正式な編集面
- image bank は `.pyxres` 往復、`Sound / Music` は Code Maker → code 側 audio asset に取り込んでから runtime
- runtime は Pyxel の「単一 main.py」制約を受けるので bundler で concat する（手で inlined コピーは維持しない）

## 3. ディレクトリと関数責務

```text
/
├─ index.html（親子の入口：production / development 比較 selector）
├─ main.py（8 行 wrapper、src/runtime/main_runtime.py を exec）
├─ main_development.py（9 行 wrapper、src/runtime/main_development_runtime.py を exec）
├─ src/
│  ├─ app.py
│  │   class BlockQuestApp（アプリ全体の窓口）
│  │     ├ set_scene（Scene を差し替える）
│  │     ├ update（現在 Scene に update を委譲）
│  │     └ draw（現在 Scene に draw を委譲）
│  ├─ game_data.py（YAML と生成済みデータの読み出し口）
│  │   ├ load_yaml（YAML ファイルを dict で返す）
│  │   ├ _build_zone_enemies（enemies list をゾーン別 dict に索引化）
│  │   ├ glitch_lord_phase（HP 比から Glitch Lord の phase 名を返す）
│  │   ├ load_enemies / load_items / load_weapons / load_armors（各カテゴリを generated module 経由で読む）
│  │   ├ load_spells / load_shops（同上）
│  │   └ load_dialogue（言語指定で dialogue を読む）
│  ├─ core/
│  │  └─ scene_manager.py
│  │      ├ class Scene(Protocol)（update / draw を持つ最小 IF）
│  │      └ class SceneManager（現在 Scene を保持：set_scene / update / draw）
│  ├─ scenes/（共通 MVP: model=状態 / view.render=見た目整形 / presenter=入力進行 / scene=束ね）
│  │  ├─ title/
│  │  │   ├ TitleModel（カーソル位置と設定開閉）
│  │  │   ├ TitleView.render（cursor / settings_open を描画 dict に整形）
│  │  │   ├ TitlePresenter.move（item 数内で cursor を回す）
│  │  │   └ TitleScene.{__post_init__, update, draw}（束ね）
│  │  ├─ explore/
│  │  │   ├ ExploreModel（現在 mode）
│  │  │   ├ ExploreView.render（mode を描画 dict へ）
│  │  │   ├ ExplorePresenter.change_mode（mode 切替）
│  │  │   └ ExploreScene.{__post_init__, update, draw}
│  │  ├─ battle/
│  │  │   ├ BattleModel（phase）
│  │  │   ├ BattleView.render（phase を描画 dict へ）
│  │  │   ├ BattlePresenter.change_phase（phase 遷移）
│  │  │   └ BattleScene.{__post_init__, update, draw}
│  │  └─ dialog/
│  │      ├ model.py
│  │      │   ├ class DialogValidationError（YAML 不正時の例外）
│  │      │   ├ class DialogChoice（選択肢：label / goto / set）
│  │      │   ├ class DialogStep（1 表示単位：speaker / text / choices / meta）
│  │      │   └ class StructuredDialogRunner（YAML ドリブン会話エンジン）
│  │      │       ├ start（scene 名から会話開始）
│  │      │       ├ choose（選択肢 index で分岐）
│  │      │       ├ continue_dialog（次 step へ）
│  │      │       ├ load_all_lines（全 step を平坦化、テスト用）
│  │      │       ├ _resolve_scene / _select_body（when 条件で variant を選ぶ）
│  │      │       ├ _apply_set（set 指令で変数更新）
│  │      │       ├ _format_text（{var} 展開）
│  │      │       └ _validate_*（variables / scenes / scene / variant / entry / choice の型検証）
│  │      ├ view.py: DialogView.render（DialogStep を描画 dict へ）
│  │      ├ presenter.py: DialogPresenter.{start, choose, continue_dialog}（scene 操作へ変換）
│  │      └ scene.py: DialogScene.{__post_init__, start, choose, continue_dialog, update, draw}（束ね）
│  ├─ shared/services/
│  │  ├─ audio_system.py（BGM/SFX の場面選択。track literal は持たず import 済み audio を適用）
│  │  │   ├ melody_slot / bass_slot / drum_slot（scene → 各パート sound slot 解決）
│  │  │   ├ music_index / track_slot（scene → music slot 解決）
│  │  │   ├ choose_bgm_scene（戦闘 / エリア / イベント文脈から BGM scene 決定）
│  │  │   └ class AudioManager
│  │  │       ├ _load_tracks（Pyxel sound / music バンクに流し込み）
│  │  │       ├ play_scene（scene 名で BGM を切替）
│  │  │       └ set_enabled（音の ON/OFF）
│  │  ├─ browser_resource_override.py（localStorage の Code Maker zip を runtime staging に戻す）
│  │  │   ├ _load_browser_import_payload（JS bridge で base64 zip と meta を読む）
│  │  │   └ stage_browser_imported_resource（pyxres を抽出して staging path に書く、J53 Phase 3 で削除）
│  │  ├─ codemaker_resource_store.py（Code Maker zip の採否と保管）
│  │  │   ├ _sha256_bytes（ハッシュ）
│  │  │   ├ _manifest_path / _imported_resource_path / _canonical_resource_path（各種 path 解決）
│  │  │   ├ _load_zip_entries（zip を開いてエントリ名を返す）
│  │  │   ├ _resolve_resource_entry（zip 内 pyxres を特定）
│  │  │   ├ extract_codemaker_resource_archive（zip から pyxres バイト列を抽出）
│  │  │   ├ import_codemaker_resource_zip（staging に保管 + manifest 更新）
│  │  │   ├ load_imported_resource_manifest（staging の状態を返す）
│  │  │   ├ get_imported_resource_path（staging された pyxres path を返す）
│  │  │   ├ clear_imported_resource（staging を破棄）
│  │  │   └ promote_imported_resource（staging → 本番昇格、J53 Phase 3 で削除）
│  │  ├─ input_bindings.py
│  │  │   ├ any_btn / any_btnp（ボタン群の OR 判定）
│  │  │   └ class InputStateTracker（update / btn / btnp でフレーム差分を管理）
│  │  ├─ landmark_events.py
│  │  │   ├ class LandmarkEvent（座標 / scene 名 / 条件 flag を持つ接触イベント）
│  │  │   ├ find_landmark_event / find_landmark_at（座標検索）
│  │  │   └ resolve_scene（flags から遷移先 scene を決定）
│  │  ├─ play_session_logging.py（Web プレイ記録を sqlite に保存）
│  │  │   ├ _normalize_timestamp / _serialize_timestamp / _active_seconds / _connect（内部）
│  │  │   ├ start_session（セッション開始を insert）
│  │  │   ├ heartbeat_session（生存 ping を update）
│  │  │   ├ end_session（終了時刻と active 秒を固定）
│  │  │   └ summarize_sessions / summarize_sessions_by_browser（集計 view）
│  │  ├─ player_state.py
│  │  │   ├ exp_for_level（level → 必要 EXP）
│  │  │   ├ stats_for_level（level → HP/MP/ATK/DEF）
│  │  │   ├ create_initial_player（初期値で player dict を作る）
│  │  │   ├ dump_snapshot（save 用に整形）
│  │  │   └ restore_snapshot（save から復元）
│  │  └─ save_store.py（保存先差分の吸収層）
│  │      ├ class SaveStoreError / SaveStore(Protocol)
│  │      ├ _validate_loaded（読み出し結果の型検証）
│  │      ├ class InMemorySaveStore（テスト用、{exists, load, save}）
│  │      ├ class FileSaveStore（desktop JSON、{exists, load, save}）
│  │      ├ class LocalStorageSaveStore（Web / Pyodide、{exists, load, save}）
│  │      └ make_save_store（環境判定で実装を返す factory）
│  ├─ shared/ui/
│  │  ├─ dialog_window.py: DialogWindow.rect（会話ウィンドウ矩形）
│  │  ├─ hud.py: HudLayout.origin（HUD 基準座標）
│  │  └─ menu_window.py: MenuWindow.rect（メニュー矩形）
│  ├─ generated/（YAML から `tools/gen_data.py` が生成。手で触らない）
│  │   dialogue.py / enemies.py / items.py / weapons.py / armors.py / spells.py / shops.py
│  └─ runtime/（Pyxel の単一ファイル制約の受け皿。J53 で分解対象）
│     ├─ main_runtime.py（本番、7266 行のモノリス。inlined で shared/services のコピーを抱える）
│     │   【inlined コピー層 — J53 Phase 1 で import 化して削除】
│     │   ├ input 群：any_btn / any_btnp / InputStateTracker
│     │   ├ landmark 群：LandmarkEvent / find_landmark_event / find_landmark_at / resolve_scene
│     │   ├ player 群：exp_for_level / stats_for_level / create_initial_player / dump_snapshot / restore_snapshot
│     │   ├ save 群：SaveStoreError / SaveStore / _validate_loaded / InMemory/File/LocalStorageSaveStore / make_save_store
│     │   ├ browser 群：_load_browser_import_payload / _extract_browser_import_resource / stage_browser_imported_resource
│     │   ├ SFX 群：class SfxSystem（sound slot 監視と play_scene の受け口）
│     │   ├ dialog 群：DialogValidationError / DialogChoice / DialogStep / StructuredDialogRunner
│     │   ├ audio 群：melody_slot / bass_slot / drum_slot / music_index / track_slot / choose_bgm_scene / AudioManager
│     │   └ data 群：_build_zone_enemies（※line 1673 / 4612 に重複）/ glitch_lord_phase
│     │                load_enemies / load_items / load_weapons / load_armors / load_spells / load_shops / load_dialogue
│     │   【world 生成層 — 未抽出、J53 Phase 1.5 で src/shared/services/world_generation.py へ移動想定】
│     │   ├ get_path_variant / get_shore_variant（タイル隣接から variant index を算出）
│     │   ├ _make_empty（W×H グリッドを fill で初期化）
│     │   ├ _carve_winding_path（2 点間をうねり道で接続）
│     │   ├ _place_forests / _place_decorations / _place_landmarks（密度や structure を見て配置）
│     │   ├ generate_world_map（seed でワールドを生成）
│     │   ├ generate_dungeon（seed でダンジョンを生成）
│     │   └ get_zone（tile_y と in_dungeon から zone 名を返す）
│     │   【misc トップレベル】
│     │   ├ name_en（英字名変換）
│     │   ├ say / say_clear（デバッグ overlay 用）
│     │   └ run（Pyxel 起動 entry）
│     │   【class Game — 約 2500 行、113 メソッド。Phase 1.6 で src/runtime/game.py に抽出し更に分割】
│     │   ├ 初期化：__init__ / start / _setup_image_banks / _paint_jp_font_bank / _build_reverse_tile_map
│     │   │        / _tile_bank_layout_valid / _setup_world_tilemap / _bake_dungeon_to_tilemap
│     │   │        / _derive_dungeon_from_tilemap / _bake_world_to_tilemap / _derive_world_from_tilemap
│     │   │        / _tile_iter / _layout_tile_bank / _paint_tile_bank / _render_tiles_to_bank
│     │   │        / _sprite_iter / _layout_sprite_bank / _paint_sprite_bank / _render_sprites_to_bank
│     │   ├ 入力：_btn / _btnp / _any_advance_btnp
│     │   ├ splash / title / load：update_splash / update_title / _do_load / draw_splash / draw_title
│     │   ├ map / explore：update_map / _check_tile_events / _check_landmark_events / _resolve_landmark_scene
│     │   │                / draw_map / _draw_landmark_highlights / _dungeon_exit_callback
│     │   ├ town：_current_town_index / _enter_town_message / _inn_cost_for_current_town
│     │   │       / _town_menu_talk / _town_menu_inn / _town_menu_save / _town_menu_exit
│     │   │       / update_town / update_town_menu / draw_town_menu
│     │   ├ shop：_enter_shop / _try_purchase / update_shop / draw_shop
│     │   ├ battle：_start_battle / _start_noise_guardian_battle / _on_noise_guardian_defeated
│     │   │        / _check_noise_guardian_phase / _check_glitch_lord_phase_transition
│     │   │        / _do_player_attack / _do_enemy_attack / _apply_spell_effect
│     │   │        / _battle_victory / _battle_defeat / _check_level_up
│     │   │        / _enemy_hit_scene_name / _victory_scene_name / update_battle / draw_battle
│     │   ├ dialog / message：_enter_message / _dialog_lines / _dialog_text / _current_dialog_page_lines
│     │   │                   / _advance_dialog_page / show_message / update_message / _wrap_text
│     │   │                   / say / text / _draw_say_overlay / draw_message_window
│     │   ├ menu / settings：_menu_labels / _open_settings / _settings_return_state / _settings_rows
│     │   │                  / _apply_av_settings / _toggle_setting / update_menu / draw_menu
│     │   │                  / update_settings / draw_settings
│     │   ├ item：_use_item
│     │   ├ AI help：_try_open_ai_chat / _enter_ai_help / update_ai_help / draw_ai_help
│     │   ├ professor / ending：_professor_phase / _professor_battle_phase
│     │   │                    / _enter_professor_intro / update_professor_intro / draw_professor_intro
│     │   │                    / _enter_professor_ending_main / update_professor_ending_main / draw_professor_ending_main
│     │   │                    / _enter_professor_ending_accepted / update_professor_ending_accepted
│     │   │                    / draw_professor_ending_accepted
│     │   │                    / _enter_ending / update_ending / draw_ending
│     │   ├ vfx：_start_vfx / _draw_vfx_overlay
│     │   ├ audio：_sync_audio（現在 scene に合う BGM を流す）
│     │   ├ トップ：update（全体 dispatcher）/ draw（全体 dispatcher）
│     │   └ その他：_name（表示名整形）/ _t（翻訳）/ _draw_dungeon_glitch_lord_marker / draw_status_bar / show_message
│     └─ main_development_runtime.py（開発版、7328 行。main_runtime.py と **完全二重管理**。J53 Phase 3 で削除）
├─ assets/（人が直す正本：*.yaml / blockquest.pyxres / フォント / 画像）
├─ tools/
│  ├─ build_web_release.py（production / development の Web 配布物生成）
│  │   ├ resolve_pyxel_command（pyxel 実行コマンド解決）
│  │   ├ development_outputs_are_available / development_codemaker_zip_is_available（dev 成果物の有無）
│  │   ├ validate_development_files（必須 file 検証）
│  │   ├ promote（staging → 昇格）
│  │   ├ approve_development / reject_development（承認ゲート、J53 Phase 3 で削除）
│  │   ├ build_web_release（production build 本体）
│  │   ├ build_development_release（dev build、J53 Phase 3 で削除）
│  │   └ main（CLI entry）
│  ├─ build_codemaker.py（Code Maker 用 zip 生成）
│  │   ├ _sha256_text（ハッシュ）
│  │   ├ _split_core_and_entrypoint / _normalize_entrypoint_source（core と entry を分離）
│  │   ├ build_codemaker_main_text（CORE + STUDENT の単一 main.py を組み立て）
│  │   ├ build_codemaker_zip（block-quest/ を zip 梱包）
│  │   └ main（CLI entry、J53 Phase 2 で bundler 呼び出しに書き換え）
│  ├─ build_release_artifacts.py（配布成果物の staging と prune）
│  │   ├ collect_release_paths / stage_release（staging に集約）
│  │   ├ production_output_dir / development_output_dir（出力先 path 解決）
│  │   ├ write_wrapper_outputs（play.html / pyxel.html を出力）
│  │   ├ prune_legacy_root_outputs / prune_development_outputs（古い配布物を削除）
│  │   ├ apply_stage_overrides（staging 上書き）
│  │   └ build_codemaker_release（code-maker.zip を production/ と development/ に配置）
│  ├─ render_release_selector.py（selector / wrapper の HTML テンプレート展開）
│  │   ├ versioned_asset_url（?v=TOKEN 付与）
│  │   ├ generate_wrapper（play.html 本体を出力）
│  │   ├ generate_selector（play ページ内 selector）
│  │   ├ load_top_page_changes（top_changes.json を読む）
│  │   └ generate_top_selector（変更説明付き root selector を出力）
│  ├─ resolve_release_source_of_truth.py（dev / prod 判定、J53 Phase 3 で DevelopmentCandidate 系を削除）
│  │   ├ class DevelopmentCandidate（候補の形：preview code 有無 / imported resource 有無）
│  │   ├ file_sha256 / is_git_dirty / revision_timestamp（状態収集）
│  │   ├ validate_change_list_freshness（change list の鮮度判定）
│  │   ├ build_cache_token（?v= 用トークン）
│  │   ├ _resource_override_differs_from_base（imported resource が base と異なるか）
│  │   ├ build_development_change_list（人への説明文を組み立て）
│  │   ├ resolve_development_candidate（dev 候補を確定、条件不成立なら ValueError）
│  │   ├ build_development_dependency_paths / build_development_codemaker_dependency_paths（build 依存 path 集め）
│  │   └ load_development_meta_payload / load_development_meta / write_development_meta（メタ永続化）
│  ├─ gen_data.py（assets/*.yaml → src/generated/*.py、一方向生成）
│  │   ├ _repr_value（値を Python リテラルに整形）
│  │   ├ _write_generated_module（module ファイルを書き出し）
│  │   ├ _dialogue_module_lines（dialogue 専用整形：dict of dict）
│  │   ├ generate_one（カテゴリ単位生成）
│  │   └ main（全カテゴリを生成、CI で使用）
│  ├─ sync_main_data.py（monolith に inlined を貼り戻す、J53 Phase 2 で bundler に置換）
│  │   ├ build_inlined_section（generated module → inlined section テキスト）
│  │   ├ _read_generated_definition_lines（生成済み定義を読み込む）
│  │   ├ build_inlined_dialogue_section（dialogue 専用整形）
│  │   ├ _replace_inlined_section（`# === inlined: NAME ===` ブロックを置換）
│  │   ├ sync_file（対象 file 1 本を処理）
│  │   ├ sync（全対象を処理）
│  │   └ main（CLI entry）
│  ├─ web_runtime_server.py（配布 + session API + resource import API の同居サーバー、J53 Phase 4 で autostart）
│  │   ├ _parse_timestamp / _client_ip（リクエスト解析）
│  │   ├ rebuild_after_codemaker_resource_import（import 受信後に build 再実行）
│  │   ├ _make_handler（HTTP handler クラスを動的生成）
│  │   ├ make_server（http.server を組み立て）
│  │   └ main（CLI entry）
│  ├─ report_play_sessions.py（sqlite のプレイ記録を人間可読に）
│  │   ├ render_summary / render_browser_summary（テキスト整形）
│  │   └ main（CLI entry）
│  ├─ test_headless.py: main（起動のみを確認）
│  ├─ test_save_compat.py（save 互換検証）
│  │   ├ restore_snapshot（簡易版）
│  │   └ main
│  └─ test_web_compat.py（Playwright で配布 HTML 確認）
│      ├ start_server（一時 HTTP サーバー起動）
│      └ main
├─ templates/（build 前テンプレート、完成 HTML は置かない）
│   ├ selector.html（root selector 本体）
│   ├ codemaker_import_ui.js（selector 内の upload UI 振る舞い）
│   └ wrapper.html（play ラッパー）
├─ production/（承認済み本番配布物、source は置かない）
│   index.html / play.html / pyxel.html / pyxel.pyxapp / code-maker.zip
└─ development/（比較用開発版配布物、J53 Phase 3 で削除）
    index.html / play.html / pyxel.html / pyxel.pyxapp / code-maker.zip
```

## 4. 責務の線引き（書かないべきこと）

- `app.py` に戦闘ロジックを書く／`scene_manager.py` にプレイヤー状態を持たせる
- `model.py` に `pyxel.blt()` を書く／`view.py` に save / logging / build を書く
- `presenter.py` に scene 外の永続化を書く
- `shared/services` は複数 Scene で共有される技術的関心のみ（単一 scene の状態は持たない）
- `audio_system.py` にメロディ / SE の定義そのものを正本として置かない（YAML または Code Maker に任せる）
- `codemaker_resource_store.py` は zip 採否までで、どの場面でどの音を鳴らすかは決めない
- `assets/` に build 済みファイルを置く／`templates/` に完成 HTML を置く
- `production/` と `development/` に別々の source tree を置く
- `.pyxres` を AI が直接編集する前提にする
- runtime monolith の inlined コピーを手で維持する（J53 後は bundler の自動生成のみ）

## 5. 使用ライブラリ

| ライブラリ | 主な場所 | 責務 |
|---|---|---|
| Pyxel | `src/runtime/*.py`, root `main*.py`, build 系 | 実行 / 描画 / 音、`package` / `app2html` |
| pytest | `test/` | 自動検証 |
| sqlite3 | `src/shared/services/play_session_logging.py` | Web プレイ記録の保存 |
| Playwright | `tools/test_web_compat.py` | 配布 HTML の互換確認 |
| Pyodide JS bridge | `src/shared/services/save_store.py`, `browser_resource_override.py` | browser 側 save / import 橋渡し |
| 標準ライブラリ | `tools/`, `src/shared/services/` | build / packaging / メタ処理 |

## 6. 現在地（J53 を進める理由）

- `src/runtime/main_runtime.py`（7266 行）と `main_development_runtime.py`（7328 行）はほぼ同一の inlined 二重管理。これが CJ37（責務が曖昧で直すほど別の所が壊れる）の発生源
- inlined 側は `shared/services` と同名・同責務の写しで、片側だけ直すと必ず別箇所に漏れる
- Game クラスは 113 メソッドを持つ単一責務過多（title / map / battle / dialog / shop / menu / ending / AI help 全部入り）。上の分類群がそのまま Phase 1.6 の分割指針になる
- J53 の方針：
  - **Phase 1** inlined を `from src.shared.services.* import ...` に置換、Game クラスを `src/runtime/game.py` に抽出
  - **Phase 2** Code Maker 用 bundler を作り、`main_runtime.py` は import 参照ベース、zip 生成時だけ concat
  - **Phase 3** `main_development*.py` / `DevelopmentCandidate` / `development/` 配布 / 承認ゲートを廃止、`assets/blockquest.pyxres` を唯一の正本に
  - **Phase 4** `tools/web_runtime_server.py` を systemd user unit で常時起動
  - **Phase 5** CJ26 note を再開、artifact 一致 regression を追加
