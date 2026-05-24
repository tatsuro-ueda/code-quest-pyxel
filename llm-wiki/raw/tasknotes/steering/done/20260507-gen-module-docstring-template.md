---
status: done
priority: normal
scheduled: 2026-05-07T00:00:00.000+09:00
dateCreated: 2026-05-07T00:00:00.000+09:00
dateModified: 2026-05-07T00:00:00.000+09:00
tags:
  - task
  - tools
  - codegen
  - archived
---

# 2026年5月7日 docstring 雛形生成スクリプト（B3）

> 状態：⑥ Discussion（実施可能 / 完了）
> 親タスクノート：`steering/20260507-src-header-functions-for-all-files.md`
> 対応シナリオ：B3（drift 修正の雛形を生成できる）

---

## 1) Journey

- **上流ジョブ**：JIS 親（主体性支援）を支える
- **上流CJ**：CJ37（修正しやすい状態を維持する）
- **深層的目的**：drift を修正するコストを下げて、コメント整備を継続できるようにする

1. 💦 （AI / 大人）`make verify` で drift 検出 → docstring を直さないといけない
2. Before：1 ファイルずつ手で関数・クラスを目視し、箇条書きを書き直す → 数十ファイル横展開で疲弊
3. After：`python tools/gen_module_docstring_template.py <path>` でファイルの AST から箇条書き雛形が標準出力 → コピペして役割文を書き込むだけ

---

## 2) Gherkin

### USM

- As a 大人 / AI（drift を直したい側）
- I want to 対象ファイルの AST を解析して、箇条書きの「形」だけ自動生成してほしい
- So that 手で関数・クラス・メソッドを列挙する作業がなくなり、役割文の執筆だけに集中できる

### 人間レベル Gherkin

```gherkin
Feature: docstring 雛形生成
  Scenario: AST から箇条書き雛形を出力する
    Given 対象ファイル <path>
    When  雛形生成スクリプトを実行する
    Then  そのファイルのトップレベル def / class の数だけ "- <役割を1行で>" が並ぶ
    And   各 ClassDef のメソッド数だけ "  - <役割を1行で>" がネストで並ぶ
    And   コピペすればモジュール docstring の形式 A1〜A5 を満たす
```

### AI 検収レベル Gherkin

```gherkin
Feature: gen_module_docstring_template.py（AI 検収）
  Scenario: 出力フォーマット
    Given 対象ファイル <path>
    When  python tools/gen_module_docstring_template.py <path> を実行する
    Then  終了コードは 0
    And   stdout はトリプルクォート """ で始まり、トリプルクォートで終わる
    And   stdout の1行目は "<モジュール概要を1行で>。" のようなプレースホルダ
    And   stdout には AST の (FunctionDef + ClassDef) の数だけ ^- <.+> が並ぶ
    And   各 ClassDef のメソッド数だけ ^  - <.+> がネストで並ぶ

  Scenario: 既存 docstring がある場合は対象外
    Given 既に箇条書き docstring を持つファイル
    When  スクリプトを実行する
    Then  stdout に「既に整備済」のメッセージを出して exit 0
    And   または、上書き用の雛形を新たに生成する（--force オプション）
```

---

## 3) Design

### 大まかな責務分担

- **`tools/gen_module_docstring_template.py`** — AST を読んで docstring の形だけを出力する純粋な CLI。役割文（`<...>`）は書かない、それは人 / AI が後で埋める。

### 親ディレクトリで責務がわかるファイル一覧

| パス | 責務 |
| ----- | ----- |
| `tools/gen_module_docstring_template.py` | AST → 箇条書き雛形（プレースホルダのみ）を stdout 出力 |

---

## 4) Tasklist

- [x] T1: `tools/gen_module_docstring_template.py` 実装
- [x] T2: 整備済ファイル `src/scenes/battle/view.py` で雛形を生成し、形式 A1〜A5 の構造を満たすことを確認
- [x] T3: 整備未完ファイル（`src/runtime/app.py`）でも雛形が正しく生成されることを確認

---

## 5) Result

### 作成ファイル

| パス | 種類 | 役割 |
| ----- | ----- | ----- |
| `tools/gen_module_docstring_template.py` | 新規 | AST → docstring 雛形（プレースホルダ + 元識別子コメント）を stdout 出力 |

### 動作確認

整備済ファイル（既存箇条書きを尊重）:
```
$ python3 tools/gen_module_docstring_template.py src/scenes/battle/view.py
already has bullet docstring: src/scenes/battle/view.py (use --force to regenerate)
→ exit 0
```

`--force` で再生成（識別子を `# <name>` で残して役割文の手がかりにする）:
```
$ python3 tools/gen_module_docstring_template.py src/scenes/battle/view.py --force
"""<モジュール概要を1行で>。

このファイルに含まれる関数・クラス：

- <役割を1行で>  # _select_battle_bgm
- <役割を1行で>  # play_bgm
- <役割を1行で>  # BattleView
  - <役割を1行で>  # render
  - <役割を1行で>  # draw
"""
```

整備未完ファイル（例: src/runtime/app.py）:
```
- <役割を1行で>  # Game
  - <役割を1行で>  # __init__
  - <役割を1行で>  # current_town
  ... 計 14 メソッド
- <役割を1行で>  # say
- <役割を1行で>  # say_clear
- <役割を1行で>  # run
```

---

## 6) Discussion

### まとめ

「実施可能」状態で完了。drift を直すコストが「関数を目視で列挙する」ステップ分だけ削減され、横展開時の負担が大幅に軽くなる。

### Gherkin CoVe 検証

| シナリオ | 結果 |
| ----- | --- |
| USM 人間 Scenario (AST から雛形) | ✅ トップレベル数だけ `^- `、メソッド数だけ `^  - ` |
| AI 検収 Scenario 1 (出力フォーマット) | ✅ `"""` 開始/終了、1 行目句点プレースホルダ、件数一致 |
| AI 検収 Scenario 2 (既存 docstring) | ✅ `--force` 無しで「既に整備済」、`--force` で再生成 |

### 懸念点

1. **`@property` のセッター/ゲッターが個別メソッドとして数えられる**
   - `runtime/app.py` の出力で `current_town / current_town / debug_mode / debug_mode ...` のように同名メソッドが 2 度ずつ現れる
   - これは `@property` と `@*.setter` の両方が AST 上で別 FunctionDef として現れるため
   - **対処は別タスクで判断**：A2「実態整合」も同じ件数で数えているため、雛形側だけ間引くと逆に drift の原因になる。両方を統一して間引くか、両方とも残すかは横展開時に決める

2. **`__init__` も箇条書きに含まれる**
   - 役割が自明なメソッドまで列挙する必要があるか、人 / AI が編集時に判断する余地を残す
   - `--no-names` を付ければ識別子コメントは消える

### 残課題

- なし（このタスク単体で完結）
- 横展開時に上記 1（@property の重複扱い）の方針を決める必要

### 判定：**実施可能（完了）**
