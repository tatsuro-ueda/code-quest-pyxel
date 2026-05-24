---
status: done
priority: normal
scheduled: 2026-05-07T00:00:00.000+09:00
dateCreated: 2026-05-07T00:00:00.000+09:00
dateModified: 2026-05-07T00:00:00.000+09:00
tags:
  - task
  - tools
  - traceability
  - archived
---

# 2026年5月7日 scene ↔ CJ 対応表と影響範囲提示 CLI（C3）

> 状態：⑥ Discussion（実施可能 / 完了）
> 親タスクノート：`steering/20260507-src-header-functions-for-all-files.md`
> 対応シナリオ：C3（コード変更 → 上流 docs 影響範囲の提示）

---

## 1) Journey

- **上流ジョブ**：JIS 親（主体性支援）を支える
- **上流CJ**：CJ37（修正しやすい状態を維持する）
- **深層的目的**：コード変更が上流 CJ / CJob にどう響くかを「変えた瞬間に」可視化する

1. 💦 （AI / 大人）コードを変えた → 上流 docs を更新する必要があるか不明
2. Before：scene を変えても CJ への影響が分からず、上流 docs の更新を忘れる
3. After：`python tools/scene_to_cj.py --since HEAD~1` で「変更した scene → 関連 CJ → 該当カテゴリ」が即表示される

---

## 2) Gherkin

### USM

- As a 大人 / AI（コード変更後に上流 docs を更新するか判断したい側）
- I want to 変更ファイルから関連 CJ を引いて、上流の影響範囲を即座に列挙してほしい
- So that コードと上流 docs の同期更新を「忘れない仕組み」として持てる

### 人間レベル Gherkin

```gherkin
Feature: scene ↔ CJ 影響範囲提示
  Scenario: 触れた scene から関連 CJ/CJob 候補が出せる
    Given 直近のコミットで src/scenes/<scene>/ 配下のファイルが変更された
    When  影響範囲提示コマンドを走らせる
    Then  その scene に紐づく CJ ID 候補が列挙される
    And   各 CJ の該当カテゴリも合わせて表示される
```

### AI 検収レベル Gherkin

```gherkin
Feature: scene_to_cj.py（AI 検収）
  Scenario: 対応表 YAML が読める
    Given tools/scene_to_cj.yml が存在する
    When  python tools/scene_to_cj.py --list を実行する
    Then  exit code は 0
    And   stdout に各 scene と対応 CJ ID が表示される

  Scenario: git diff からの影響範囲提示
    Given リポジトリルートで `git diff --name-only HEAD~1 HEAD` の結果に `src/scenes/battle/` 配下が含まれる
    When  python tools/scene_to_cj.py --since HEAD~1 を実行する
    Then  exit code は 0
    And   stdout に "battle" scene の関連 CJ が列挙される
    And   各 CJ ID は customer-journeys.md に実在する

  Scenario: scene 配下が変わっていなければ何も提示しない
    Given 直近の差分が src/scenes/ 配下を含まない
    When  上記コマンドを実行する
    Then  exit code は 0
    And   stdout に "no relevant scene changes" のような行が出る
```

---

## 3) Design

### 大まかな責務分担

- **`tools/scene_to_cj.yml`** — scene 名 ↔ CJ ID の対応表（手書きの SSoT）。最初は粗くてよい。
- **`tools/scene_to_cj.py`** — git diff を取り、scene 名を抽出し、対応表を引いて CJ + カテゴリを stdout に出す CLI。
  - `verify_cj_cjob.py` が持つ「customer-journeys.md から CJ → カテゴリを抽出する関数」を再利用する（DRY）。

### 親ディレクトリで責務がわかるファイル一覧

| パス | 責務 |
| ----- | ----- |
| `tools/scene_to_cj.yml` | scene 名 → CJ ID リストの対応表（手書き SSoT） |
| `tools/scene_to_cj.py` | `git diff --name-only` → scene 名 → 対応表参照 → CJ + カテゴリ列挙 |

### 対応表の初期内容

`docs/customer-journeys.md` の本文を読みながら大まかに紐付ける（厳密性は後で調整）：
- `battle` → CJ08 / CJ10 / CJ13 / CJ16 / CJ29 / CJ44（戦闘・敵・呪文・BGM）
- `explore` → CJ12 / CJ14 / CJ15 / CJ20 / CJ44（マップ・歩く・フィールド演出）
- `town` → CJ09 / CJ15 / CJ20 / CJ44（NPC・町・町 BGM）
- `professor` → CJ09 / CJ27 / CJ30（セリフ・分岐）
- `ai_help` → CJ22 / CJ31 / CJ32 / CJ33 / CJ34（AI 改造・承認）
- `menu` → CJ01〜CJ07（タイル系メニュー操作）
- `shop` → CJ29（バランス・売買）
- `splash` / `title` / `ending` → CJ42（やり切れる体験）
- 共通 / 全体: `runtime` → CJ37（責務）/ CJ41（技術基盤）

> 注: この紐付けは初期粗版。実運用で精度を上げる。検証スクリプトは「対応表の CJ ID が実在するか」だけ厳密にチェックする。

---

## 4) Tasklist

- [x] T1: `tools/scene_to_cj.json` を初期内容で作成（YAML 依存を避けて JSON）
- [x] T2: `tools/scene_to_cj.py` 実装（--list / --since / --verify-only 3 モード対応）
- [x] T3: `--verify-only` で対応表の CJ ID がすべて customer-journeys.md に実在することを確認 → "scene_to_cj map OK"
- [x] T4: `--since HEAD~3` で battle / ending / explore / menu / title / runtime / shared が拾える、`--since HEAD~1` では変更なしを認識

---

## 5) Result

### 作成ファイル

| パス | 種類 | 役割 |
| ----- | ----- | ----- |
| `tools/scene_to_cj.json` | 新規 | scene 名 / area 名 → CJ ID リスト の対応表（JSON、PyYAML 不要） |
| `tools/scene_to_cj.py` | 新規 | git diff から scene/area を抽出 → 対応表参照 → CJ + カテゴリ表示。`--list` / `--since` / `--verify-only` の 3 モード |

### 動作確認

```
$ python3 tools/scene_to_cj.py --verify-only
scene_to_cj map OK
→ exit 0

$ python3 tools/scene_to_cj.py --since HEAD~3
## changed scenes
- battle → CJ08, CJ10, CJ13, CJ16, CJ29, CJ44
    CJ08: ①子（プレイヤー・没入）, ⑤親（関係・コミュニケーション）
    ...
- ending → CJ30, CJ42
- explore → CJ12, CJ14, CJ15, CJ20, CJ44
- menu → CJ01〜CJ07
- title → CJ42
## changed areas
- runtime → CJ37, CJ41
- shared → CJ37
→ exit 0

$ python3 tools/scene_to_cj.py --since HEAD~1
no relevant scene / area changes since HEAD~1
→ exit 0
```

---

## 6) Discussion

### まとめ

「実施可能」状態で完了。コード変更後に `--since` を叩けば、即座に関連 CJ + カテゴリが視覚的に列挙される。Makefile 統合は今回見送り（影響範囲提示は失敗扱いではなく情報提供なので、`make verify` の失敗条件には入れない判断）。`--verify-only` は CI で対応表自体の健全性を担保する用途で使う。

### Gherkin CoVe 検証

| シナリオ | 結果 |
| ----- | --- |
| AI 検収 Scenario 1 (--list) | ✅ 各 scene と対応 CJ + カテゴリを正しく表示 |
| AI 検収 Scenario 2 (--since 影響範囲) | ✅ HEAD~3 で 5 scene + 2 area を抽出、各 CJ ID は実在 |
| AI 検収 Scenario 3 (差分なし) | ✅ HEAD~1 で "no relevant scene / area changes" |

### 懸念点

1. **対応表は粗版（手書き）**
   - 例えば `battle` には CJ08 / CJ10 / CJ13 / CJ16 / CJ29 / CJ44 を紐付けたが、運用しながら精度を上げる必要
   - 紐付けが薄すぎる scene（`splash` → CJ42 だけなど）も再検討余地

2. **YAML ではなく JSON にした**
   - PyYAML は標準ライブラリではないため依存追加を避けた
   - コメントが書きづらい（`_comment` キーで擬似コメント）。可読性で困るなら後で TOML / pyproject 風 に移す余地

3. **`--since` は git の commit-ish に依存**
   - 浅い clone 環境では HEAD~3 が引けない可能性あり。CI で使う場合は `fetch-depth` の調整が必要

### 残課題

- 対応表の精度向上：横展開（src/ docstring 整備）と並行して紐付けを見直す
- `make verify` から `--verify-only` を呼んで対応表の健全性も build 時に保証する選択肢（現時点は別タスクで判断）

### 判定：**実施可能（完了）**
