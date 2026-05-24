---
status: done
priority: normal
scheduled: 2026-05-07T00:00:00.000+09:00
dateCreated: 2026-05-07T00:00:00.000+09:00
dateModified: 2026-05-07T00:00:00.000+09:00
tags:
  - task
  - bundle
  - infra
---

# 2026年5月7日 bundle 再ビルド（BGM pyxres SSoT 反映）

> 状態：④ Tasklist
> 次のゲート：完了確認（このタスクは自動委任で完遂）

---

## 1) Journey（どこへ行くか）

- **深層的目的**：BGM SSoT 化の変更が dist/code-maker.zip に反映され、Code Maker と本編で同じ音が鳴る
- **やらないこと**：bundle 仕様自体の変更（CJ44 確定版の方針はそのまま）

### 背景

`steering/20260506-bgm-pyxres-ssot.md` で AudioManager 撤去・View 直書き・設定画面撤去を完了した。
src/scenes/settings/ 削除と src/runtime/main_runtime.py shim の変更により、Code Maker bundler
（`tools/build_codemaker.py`）が生成する `code-maker.zip` と inline 化される `main_runtime.py`
の中身が古いままになっている可能性がある。

### 完了条件（CoVe 検証項目）

1. `tools/build_codemaker.py` がエラーなく完走する
2. `dist/code-maker.zip` の中の `main.py` が SettingsScene を含まない
3. `dist/code-maker.zip` の中の `main.py` が AudioManager を含まない
4. `production/code-maker.zip` も同様（同じビルド成果物が両方に置かれる場合）
5. 既存テスト（`test_main_inlined_dialogue_covers_runtime_scene_ids` 等）が引き続き green

---

## 2) Gherkin（完了条件）

```gherkin
Feature: bundle が CJ44 確定版の構造を反映している
  Code Maker と本編で同じ音が鳴り、子どもが pyxres を編集すれば即時反映されるには
  bundle 内の inlined main.py が新しい view 直書き方式に揃っていなければならない

  Scenario: bundle に古い AudioManager / SettingsScene が残らない
    Given src/scenes/settings/ は削除済み
    And src/shared/services/audio_system.py から AudioManager は撤去済み
    When tools/build_codemaker.py を実行する
    Then dist/code-maker.zip の main.py に "class AudioManager" が含まれない
    And dist/code-maker.zip の main.py に "class SettingsScene" が含まれない

  Scenario: bundle で BGM が pyxel.playm 直呼びで発火する
    Given 各 scene の view.py に play_bgm() が定義されている
    When bundle を build する
    Then dist/code-maker.zip の main.py に "pyxel.playm(" が含まれる
    And manifest 漏れによる NameError が起きない
```

---

## 3) Design

- 実行コマンド: `python tools/build_codemaker.py`
- 影響範囲: dist/code-maker.zip / production/code-maker.zip / production/pyxel.html /
  production/pyxel.pyxapp（既存ビルド成果物）
- 検証: 上記 Gherkin の Scenario を bash で確認

---

## 4) Tasklist

- [x] bundle 再ビルド実行（`python tools/build_codemaker.py`）
- [x] release artifacts 再生成（`PYTHONPATH=. python tools/build_web_release.py`）
- [x] 結果検証（Scenario 2 件 CoVe）
- [x] git status 確認（dist/ の差分のみ。想定どおり）

---

## 5) Result

- `dist/code-maker.zip` (370648 bytes) 再生成
- `dist/pyxel.html` (382726 bytes) 再生成
- `dist/pyxel.pyxapp` (286890 bytes) 再生成
- `dist/play.html` / `dist/index.html` 更新
- bundle 内 `block-quest/main.py` 検証結果:
  - `class AudioManager`: 0 件（撤去成功）
  - `class SettingsScene`: 0 件（撤去成功）
  - `pyxel.playm(`: 5 件（title/explore/battle/ending の play_bgm + ExploreView 内の 1 件）
  - `def play_bgm`: 4 件（title/explore/battle/ending）
  - `audio.play_scene`: 0 件（旧 API 撤去成功）
  - 残存する `CHIPTUNE_TRACKS` / `choose_bgm_scene` / `sync_audio` / `bgm_enabled` /
    `vfx_enabled` の文字列はすべて **改訂コメント / docstring / legacy AV キー pop 処理**
    のみ。実コードへの参照はゼロ。

最終 pytest: **674 passed, 2 skipped** （6.44s）

---

## 6) Discussion

### 結果

CJ44 確定版の bundle 反映は完了。Code Maker 側の挙動も view.py の `pyxel.playm` 直呼び方式
で統一されたことを確認した。

### 気づき

`build_release_artifacts.py` は `from tools.build_codemaker import ...` をしているため、
コマンドラインから直接実行するには `PYTHONPATH=.` 指定が必要。`build_web_release.py` 側は
`sys.path.insert` で済ませている。両者の起動方法を docs/architecture.md に書いておくと
次の人が悩まないかもしれない（次タスクで観察する）。
