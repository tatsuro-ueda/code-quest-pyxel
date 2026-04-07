# テスト設計

Pyxel版ブロッククエストのテスト方針と現状の構成。

> **元ドキュメントは旧JS版（`game/index.html` + vitest）の設計だった。** 本ドキュメントはPyxel版（Python + 標準 `unittest`）に書き換えたもの。

---

## 1. 基本方針

- **標準ライブラリの `unittest` のみ**を使う。pytest や外部テストランナーは導入しない（依存を増やさない）。
- **`src/` 配下の純粋ロジックを優先的にユニットテストする**。`pyxel` モジュールに直接依存する処理は薄い層に閉じ込め、テスト側は `_FakePyxel` で差し替える。
- **描画・サウンド・入力の最終出力は単体テストの対象外**。これらは `pyxel-mcp` の `run_and_capture` / `render_audio` / `play_and_capture` など視覚・音声ツールで検証する（後述）。
- **統合チェックはスクリプトとアセットの整合を監視するだけに留める**。例：`main.py` が期待するシーン名をdialogue.yamlが供給しているか、`my_resource.pyxres` が壊れていないか。

## 2. 実行方法

プロジェクトルートから：

```bash
cd code-quest-pyxel
python -m unittest discover -s test -p "test_*.py"
```

個別実行：

```bash
python -m unittest test.test_save_store
python test/test_save_store.py        # 各ファイル末尾の unittest.main() で単独実行も可
```

> 現時点で **59 テスト / 0 失敗**（`Ran 59 tests in 0.094s`）。

## 3. ディレクトリ構成

```
code-quest-pyxel/
├── main.py                      # ゲーム本体（pyxel.run まで）
├── src/                         # 純粋ロジック層（テスト対象の中心）
│   ├── audio_system.py
│   ├── input_bindings.py
│   ├── landmark_events.py
│   ├── map_registry.py
│   ├── player_snapshot.py
│   ├── save_store.py
│   ├── simple_yaml.py
│   ├── structured_dialog.py
│   ├── tiled_loader.py
│   └── tmx_validator.py
├── tools/                       # ビルド/プレビュー補助スクリプト
│   ├── build_web_release.py
│   └── serve_pyxel_preview.py
└── test/
    ├── test_audio_system.py         # FakePyxel で channel/sound を差し替え
    ├── test_dialogue_integration.py # main.py が参照するシーン名の存在確認
    ├── test_input_bindings.py       # FakePyxel で btn/btnp を差し替え
    ├── test_landmark_events.py      # 純粋ロジック
    ├── test_player_snapshot.py      # dump/restore のラウンドトリップ
    ├── test_preview_server.py       # tools/serve_pyxel_preview.py
    ├── test_release_build.py        # tools/build_web_release.py の収集ロジック
    ├── test_resource_compat.py      # my_resource.pyxres が valid zip か
    ├── test_save_store.py           # InMemory / FileSaveStore
    ├── test_structured_dialog.py    # YAML駆動ダイアログランナー
    └── test_tmx_foundation.py       # tmx_validator + tiled_loader + map_registry
```

## 4. import の作法

`src/` を絶対 import するため、各テストファイル冒頭で `sys.path` にプロジェクトルートを差し込む：

```python
from __future__ import annotations
import sys, unittest
from pathlib import Path

PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))

from src.save_store import InMemorySaveStore  # noqa: E402
```

このパターンを全テストで統一する。`pyproject.toml` でのパッケージ化はしない（Pyxel本体が単一スクリプト構成のため）。

## 5. テストパターン

### A. 純粋ロジック（pyxel非依存）

`src/` の純粋関数・データクラスは直接 import してテストする。

| テスト | 対象 | 確認内容 |
|---|---|---|
| `test_save_store` | `InMemorySaveStore` / `FileSaveStore` | save→load ラウンドトリップ、`exists()`、上書き、エラー時挙動 |
| `test_player_snapshot` | `dump_snapshot` / `restore_snapshot` | `SAVE_VERSION` 整合、`SAVED_PLAYER_KEYS` の網羅 |
| `test_landmark_events` | `find_landmark_event` | プレイヤー座標とフラグから期待イベントが返る |
| `test_structured_dialog` | `StructuredDialogRunner` | YAMLパース、バリデーションエラー、シーン遷移 |

### B. Pyxel依存ロジック（FakePyxelで隔離）

`pyxel` モジュールに依存するロジックは、テスト内で `_FakePyxel` を組み立てて差し替える。代表例（`test_audio_system.py`）：

```python
class _FakeSound:
    def __init__(self):
        self.loaded = []
    def pcm(self, filename):
        self.loaded.append(filename)

class _FakeChannel:
    def __init__(self):
        self.gain = 0.125

class _FakePyxel:
    def __init__(self):
        self.sounds = [_FakeSound() for _ in range(64)]
        self.channels = [_FakeChannel() for _ in range(4)]
        self.play_calls = []
    def play(self, ch, snd, loop=False):
        self.play_calls.append((ch, snd, loop))
    def stop(self, ch=None): ...
```

`test_input_bindings.py` も同様に `btn` / `btnp` を返すだけの `FakePyxel` を渡す。**実 `pyxel` を import しない**ことで CI でもヘッドレスに動く。

### C. 統合・整合チェック

| テスト | 役割 |
|---|---|
| `test_dialogue_integration` | `main.py` と `src/landmark_events.py` を **テキストとして読み**、`town.start.entry` 等のシーン名キーが文字列リテラルとして含まれているかを確認。シーン名のtypo検知が目的 |
| `test_resource_compat` | `my_resource.pyxres` が存在し、ZIP として開けて `pyxel_resource.toml` を含むことを確認 |
| `test_tmx_foundation` | `tmx_validator` / `tiled_loader` / `map_registry` のスモーク。サンプル TMX を読んで期待 MapData が組み立つこと |
| `test_release_build` | `tools/build_web_release.collect_release_paths` が「ランタイム必須ファイルだけ」を返すこと |
| `test_preview_server` | `tools/serve_pyxel_preview.build_preview_urls` がプレビューURLを正しく生成すること |

## 6. テスト対象外（pyxel-mcpに委ねる）

以下は単体テストを書かない。代わりに **`pyxel-mcp` の検証ツール** をワークフローに組み込む。

| 領域 | 検証手段 |
|---|---|
| 描画結果 | `run_and_capture` でフレームをキャプチャ、`compare_frames` で差分比較 |
| アニメーション・遷移 | `capture_frames`（複数フレーム）、`inspect_animation` |
| 画面レイアウト | `inspect_screen`（カラーグリッド）、`inspect_layout`（マージン警告） |
| パレット使用 | `inspect_palette` |
| タイルマップ | `inspect_tilemap`、`inspect_bank` |
| サウンド | `render_audio`（チャンネル毎にWAV化して試聴） |
| 入力依存ロジック（メニュー操作・移動） | `play_and_capture`（仮想入力シーケンスを与えてキャプチャ） |
| スクリプトの構文・アンチパターン | `validate_script`（ASTチェック、`run_and_capture` より高速） |
| ランタイム変数の値 | `inspect_state` |

これらは「機械的に判定できないが、人間（または LLM）が見れば判別できる」種類の検証であり、ユニットテストの代替ではなく**補完**として扱う。

## 7. 乱数を含むロジックのテスト戦略

- **シード固定** — `random.seed(42)` を `setUp` で呼ぶ。
- **境界値の直接アサート** — ダメージ計算等は `Math.max(1, ...)` のような最低保証を必ずアサートする。
- **モンキーパッチ** — どうしても乱数源を制御したいときは `unittest.mock.patch("random.random", return_value=0.5)`。
- **統計テストは原則書かない** — `N=1000` で平均を見るような統計テストは fragile になりがちなので避け、代わりに境界値を直接突く。

## 8. CI

現状 CI 設定なし。ローカルで `python -m unittest discover -s test -p "test_*.py"` をコミット前に走らせる運用。将来 CI を入れる際は同じコマンドをそのまま流せばよい（依存パッケージは `pyxel` 本体のみ）。
