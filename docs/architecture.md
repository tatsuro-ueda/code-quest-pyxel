# アーキテクチャ

## 1. 目的

この文書の目的は、`きれいな設計名` を並べることではなく、**この repo で各ファイルが何を担当するか** を固定することです。
`docs` と `code` がずれたら、`code が正しい` のではなく **未実装 / バグ / 仕様ずれ** として扱います。

## 2. 設計原則

- `src/` と `assets/` を source of truth にする
- `production/` と `development/` は source ではなく **配布物の置き場** にする
- root `index.html` は親子が本番と開発版を比べる入口として残す
- `main.py` / `main_development.py` の monolith は当面残すが、新構成へ責務を逃がしていく
- `Pyxel Code Maker` は子どもの正式な編集面として守る
- image bank 系は `.pyxres` の往復を保ち、`Sound / Music` は Code Maker から戻した内容を code 側 audio asset として取り込んでから runtime で使う

## 3. ディレクトリ構成

```text
/
├─ index.html（本番と開発版を比べる root selector）
├─ main.py（本番 runtime entrypoint）
├─ main_development.py（開発版 runtime entrypoint）
├─ src/（ゲーム本体の source of truth）
│  ├─ app.py（アプリ全体の窓口）
│  ├─ game_data.py（生成済みデータと派生データの読み出し口）
│  ├─ core/
│  │  └─ scene_manager.py（現在 Scene の切り替え管理）
│  ├─ scenes/
│  │  ├─ title/
│  │  │  ├─ model.py（タイトル画面の状態）
│  │  │  ├─ view.py（タイトル画面の見た目情報）
│  │  │  ├─ presenter.py（タイトル入力と進行）
│  │  │  └─ scene.py（title 一式の束ね役）
│  │  ├─ explore/
│  │  │  ├─ model.py（探索 Scene の現在モード）
│  │  │  ├─ view.py（探索 Scene の見た目状態）
│  │  │  ├─ presenter.py（探索モード切り替え）
│  │  │  └─ scene.py（explore 一式の束ね役）
│  │  ├─ battle/
│  │  │  ├─ model.py（戦闘 Scene の phase）
│  │  │  ├─ view.py（戦闘 Scene の見た目 phase）
│  │  │  ├─ presenter.py（戦闘 phase の進行）
│  │  │  └─ scene.py（battle 一式の束ね役）
│  │  └─ dialog/
│  │     ├─ model.py（構造化会話の検証と進行）
│  │     ├─ view.py（会話 1 step の見える形）
│  │     ├─ presenter.py（会話 runner を scene 操作へ変換）
│  │     └─ scene.py（dialog 一式の束ね役）
│  ├─ shared/
│  │  ├─ services/
│  │  │  ├─ audio_system.py（BGM/SFX の場面選択と imported audio asset の適用。track literal の正本を持たない）
│  │  │  ├─ browser_resource_override.py（browser localStorage の Code Maker zip を runtime staging に戻す）
│  │  │  ├─ codemaker_resource_store.py（Code Maker zip から import 対象 asset を抽出・保管し、audio import へ渡す）
│  │  │  ├─ input_bindings.py（入力グループ定義と押下追跡）
│  │  │  ├─ landmark_events.py（ランドマーク接触イベント定義）
│  │  │  ├─ play_session_logging.py（Web プレイ記録の保存と集計）
│  │  │  ├─ player_state.py（プレイヤー生成と save snapshot 整形）
│  │  │  └─ save_store.py（保存先差分を吸収する save backend）
│  │  └─ ui/
│  │     ├─ dialog_window.py（会話ウィンドウ矩形）
│  │     ├─ hud.py（HUD 基準位置）
│  │     └─ menu_window.py（メニューウィンドウ矩形）
│  └─ generated/（YAML から生成されるデータ）
├─ assets/（人が直す素材と YAML の正本）
├─ tools/
│  ├─ build_web_release.py（root selector / production / development の配布物生成）
│  ├─ build_codemaker.py（Code Maker 用 zip 生成）
│  ├─ sync_main_data.py（main.py 系の inlined data 同期）
│  ├─ test_web_compat.py（配布 HTML の互換確認）
│  ├─ report_play_sessions.py（プレイ記録レポート出力）
│  └─ web_runtime_server.py（配布物、session API、resource import API の同居サーバー）
├─ templates/
│  ├─ selector.html（root selector の HTML ひな型）
│  ├─ codemaker_import_ui.js（selector の Code Maker upload UI 振る舞い）
│  └─ wrapper.html（play wrapper の HTML ひな型）
├─ production/
│  ├─ index.html（本番入口ページ）
│  ├─ play.html（本番 runtime wrapper）
│  ├─ pyxel.html（本番 Web runtime 本体）
│  ├─ pyxel.pyxapp（本番 desktop 配布物）
│  └─ code-maker.zip（本番 Code Maker bundle）
└─ development/
   ├─ index.html（開発版入口ページ）
   ├─ play.html（開発版 runtime wrapper）
   ├─ pyxel.html（開発版 Web runtime 本体）
   ├─ pyxel.pyxapp（開発版 desktop 配布物）
   └─ code-maker.zip（開発版 Code Maker bundle）
```

## 4. 責務の線引き

- `app.py` は起動と委譲だけを持ち、戦闘や保存の中身を書かない
- `scene_manager.py` は Scene 切り替えだけを持ち、プレイヤー HP や会話本文を持たない
- `model.py` は状態とルールを持ち、`pyxel.blt()` のような描画を持たない
- `view.py` は見た目に必要な情報整理を持ち、save 書き込みや I/O を持たない
- `presenter.py` は入力と進行を持ち、scene 外の永続化責務を持たない
- `shared/services` は複数 Scene で共有される技術的関心を持つ
- `shared/ui` は共通 UI 部品の位置や矩形を持つ
- `main.py` / `main_development.py` には Code Maker 単一ファイル制約のため一部 service が inline で残る
- `assets/` は人が直す正本であり、build 出力先ではない
- `audio_system.py` は scene / event と音の対応づけを持つが、メロディや SE 定義そのものを正本として抱えない
- `codemaker_resource_store.py` は zip の採否と import 対象の抽出を持つが、どの場面でどの音を鳴らすかは決めない
- `templates/` はひな型だけを持ち、完成した配布物を置かない
- `production/` / `development/` は source tree を持たず、build 結果だけを置く

## 5. `assets` / `templates` / 配布物の意味

- `assets/*.yaml` はゲームデータの正本
- `assets/blockquest.pyxres` は Code Maker へ持ち出す baseline resource であり、image bank 系の往復を支える
- `Sound / Music` は Code Maker で authoring したあと、runtime 直前には code 側 audio asset へ同期される
- `.runtime/codemaker_resource_imports/*` は取り込み後、承認前の resource staging
- `templates/selector.html` と `templates/wrapper.html` は build 前のテンプレート
- root `index.html` は親子が最初に触る比較ページ
- `production/*` は承認済みの本番配布物
- `development/*` は比較用の開発版配布物

## 6. 使用ライブラリと責務

| ライブラリ / API | 主な場所 | 責務 |
|---|---|---|
| `Pyxel` | `main.py`, `main_development.py`, build 系 | ゲーム実行、描画、音、`package` / `app2html` |
| `pytest` | `test/` | 自動検証 |
| `sqlite3` | `src/shared/services/play_session_logging.py` | プレイ記録の保存と集計 |
| `Playwright` | `tools/test_web_compat.py` | browser 上の配布確認 |
| `Pyodide js bridge` | `src/shared/services/save_store.py` | browser localStorage save |
| Python 標準ライブラリ | `tools/`, `src/shared/services/` | build、packaging、保存、メタデータ処理 |

## 7. 現在地

- 実際の runtime entrypoint はまだ `main.py` / `main_development.py`
- ここには大きい `Game` クラスが残っている
- つまり **repo 構成は新設計へ寄っているが、runtime 本体はまだ monolith**
- image bank / tilemap 側は `.pyxres` の往復で前進している一方、`Sound / Music` はまだ `AudioManager` / `SfxSystem` の固定データが強く、architecture と code がずれている
- 今回の構造は、`shared/services`、`scenes/dialog`、`app/core`、`production/` / `development/` を先に整え、完全分割へ進むための土台

## 8. 書いてはいけないこと

- `app.py` に戦闘ロジックを書く
- `scene_manager.py` にプレイヤー状態を持たせる
- `model.py` に描画 API を直接書く
- `view.py` に save / logging / build を書く
- `assets/` に build 済みファイルを置く
- `templates/` に本番完成 HTML を置く
- `production/` と `development/` に別々の source tree を置く
- `.pyxres` を Codex が直接編集する前提にする

## 9. この文書の要点

- `src/` と `assets/` が正本
- `production/` と `development/` は配布結果
- root `index.html` は親子の入口
- `Pyxel Code Maker` は子どもの正式な編集面であり、`Sound / Music` はそこから code 側へ取り込んで本編で使う
- 責務を越えて書かないことが、この構造の価値
