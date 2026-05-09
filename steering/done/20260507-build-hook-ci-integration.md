---
status: done
priority: normal
scheduled: 2026-05-07T00:00:00.000+09:00
dateCreated: 2026-05-07T00:00:00.000+09:00
dateModified: 2026-05-07T00:00:00.000+09:00
tags:
  - task
  - tools
  - ci
  - hook
  - archived
---

# 2026年5月7日 検証スクリプトを pre-commit / CI に統合（B2 + C4 の補足）

> 状態：⑥ Discussion（実施可能 / 完了。CI 実起動はプッシュ後にしか確認できない＝環境依存）
> 親タスクノート：`steering/20260507-src-header-functions-for-all-files.md`
> 対応シナリオ：B2（pre-commit / CI に組み込み）/ C4（CJ/CJob 整合の定期実行）

---

## 1) Journey

- **上流ジョブ**：JIS 親（主体性支援）を支える
- **上流CJ**：CJ37（修正しやすい状態を維持する）
- **深層的目的**：`make verify` を「思い出したらやる」ではなく、コミット前 / push 前に「自動で起こる」状態にする

1. 💦 （AI / 大人）コードを変えてコミットする
2. Before：`make verify` を叩き忘れて drift / リンク切れがコミットされる → 後続作業が壊れる
3. After：コミット時に pre-commit hook が `make verify` を自動起動。失敗すればコミットを止める

---

## 2) Gherkin

### USM

- As a 大人 / AI
- I want to コミット前 / push 前 / CI で `make verify` が自動起動してほしい
- So that 検証を忘れる選択肢自体を仕組みで消せる

### 人間レベル Gherkin

```gherkin
Feature: 検証の定期実行
  Scenario: コミット時に pre-commit hook が verify を起動
    Given .git/hooks/pre-commit が用意されている
    When  git commit を試みる
    Then  事前に make verify が走る
    And   失敗したらコミットは中止される

  Scenario: GitHub Actions で push 時に CI が verify を実行
    Given .github/workflows/verify.yml がある
    When  push が起きる
    Then  CI が make verify を走らせる
    And   失敗したらワークフローが赤くなる
```

### AI 検収レベル Gherkin

```gherkin
Feature: pre-commit / CI 統合（AI 検収）

  Scenario: pre-commit-config.yaml が用意されている
    Given .pre-commit-config.yaml がある
    When  cat .pre-commit-config.yaml
    Then  少なくとも 1 つの hook entry に "make verify" または verify_module_docstrings / verify_cj_cjob が含まれる

  Scenario: pre-commit インストールスクリプトの提供
    Given tools/install_hooks.sh または同等のスクリプト
    When  bash tools/install_hooks.sh を実行する
    Then  .git/hooks/pre-commit に make verify を呼ぶフックが入る（既存 post-commit と並存）

  Scenario: GitHub Actions ワークフロー
    Given .github/workflows/verify.yml がある
    When  yaml をパースする
    Then  jobs.verify.steps の中に "make verify" を呼ぶステップがある
    And   on: [push, pull_request] が指定されている
```

---

## 3) Design

### 大まかな責務分担

- **`.pre-commit-config.yaml`**（新規）: 公式 pre-commit フレームワーク用の設定。`make verify` を呼ぶ local hook を 1 つ定義。
- **`tools/install_hooks.sh`**（更新）: 既存の post-commit インストールに加えて pre-commit hook も冪等にインストールする。
- **`.github/workflows/verify.yml`**（新規）: GitHub Actions で push / PR 時に `make verify` を走らせる。
- **`docs/`**（更新）: `AGENTS.md` または README に `bash tools/install_hooks.sh` で hook を有効にする手順を追記。

### 親ディレクトリで責務がわかるファイル一覧

| パス | 責務 |
| ----- | ----- |
| `.pre-commit-config.yaml` | pre-commit フレームワーク用の hook 定義（local hook で `make verify`） |
| `tools/install_hooks.sh` | pre-commit と post-commit の両方を `.git/hooks/` に冪等インストール |
| `.github/workflows/verify.yml` | GitHub Actions で `make verify` を実行する CI ジョブ |
| `AGENTS.md` | hook 有効化手順の追記 |

### 実施不能の可能性

- **pre-commit フレームワーク本体は VM に未インストールの可能性あり**：その場合は `.pre-commit-config.yaml` だけ用意し、生 git hook（`tools/install_hooks.sh` で `.git/hooks/pre-commit` に直書き）の方を主軸にする
- **GitHub Actions は実行環境がリポジトリの remote 側**：ローカルでは「ファイルが正しく書けたか」までが検証範囲。実起動は GitHub にプッシュしたあと

---

## 4) Tasklist

- [x] T1: `.pre-commit-config.yaml` を作成（local hook で 3 検証）
- [x] T2: `tools/install_hooks.sh` を更新して pre-commit / post-commit 両方を冪等インストール
- [x] T3: `bash tools/install_hooks.sh` を実行して `.git/hooks/pre-commit` が生成されることを確認
- [x] T4: hook を直接呼んで動作確認 → make verify + pytest 675 passed で exit 0
- [x] T5: `.github/workflows/verify.yml` を作成
- [x] T6: yaml をパースして構造妥当性を確認（jobs.verify.steps = [Checkout, Set up Python, Run make verify, Run pytest]）
- [x] T7: `README.md` に hook 有効化手順と CI 統合を追記（AGENTS.md ではなく既存の README に既存セクションを拡張）

---

## 5) Result

### 作成・更新ファイル

| パス | 種類 | 役割 |
| ----- | ----- | ----- |
| `.pre-commit-config.yaml` | 新規 | pre-commit フレームワーク用の local hook 定義（将来用） |
| `tools/install_hooks.sh` | 更新 | pre-commit + post-commit を冪等インストール |
| `.github/workflows/verify.yml` | 新規 | push / PR 時に make verify + make test を走らせる |
| `README.md` | 更新 | hook 有効化手順と CI 統合の説明 |

### 動作確認

```
$ bash tools/install_hooks.sh
[install-hooks] installed: /home/exedev/code-quest-pyxel/.git/hooks/pre-commit
[install-hooks] installed: /home/exedev/code-quest-pyxel/.git/hooks/post-commit

$ .git/hooks/pre-commit
pre-commit: make verify ...
83 files OK
CJ link OK: 36 unique CJ IDs in steering/, all resolved
CJob category OK: 73 category tokens checked
scene_to_cj map OK
pre-commit: pytest ...
675 passed, 2 skipped, 14233 subtests passed in 6.58s
pre-commit: All tests passed.
→ exit 0
```

GitHub Actions ワークフローの YAML パース確認:
```
YAML keys: ['name', True, 'jobs']  ← "on:" は YAML で True に解釈されるが GitHub Actions は文字列キーで動く
jobs.verify.steps: ['Checkout', 'Set up Python', 'Run make verify', 'Run pytest']
```

検収 grep:
```
$ grep -rEln "verify-module-docstring|verify-cj-cjob|verify_module_docstrings|verify_cj_cjob" Makefile .pre-commit-config.yaml .github
Makefile
.github/workflows/verify.yml
.pre-commit-config.yaml
```

3 箇所すべてに検証エントリあり。

---

## 6) Discussion

### まとめ

「実施可能」状態で完了。pre-commit hook はローカルで実起動を確認済（make verify + pytest が exit 0）。GitHub Actions は YAML 構造とエントリの存在まで確認したが、実起動は GitHub にプッシュした後しか確認できないため「環境依存」。

### Gherkin CoVe 検証

| シナリオ | 結果 |
| ----- | --- |
| 人間 Scenario 1（pre-commit が verify を起動） | ✅ hook 直接呼び出しで確認 |
| 人間 Scenario 2（CI が verify を実行） | ⚠️ ファイルは存在するが実起動はリモート確認が必要 |
| AI 検収 Scenario 1（.pre-commit-config.yaml に hook entry） | ✅ 3 つの local hook 定義 |
| AI 検収 Scenario 2（install_hooks.sh で .git/hooks/pre-commit が入る） | ✅ 冪等インストール確認 |
| AI 検収 Scenario 3（GitHub Actions yaml に make verify ステップ） | ✅ jobs.verify.steps に "Run make verify" |

### 懸念点

1. **GitHub Actions 実起動はリモート依存**
   - ローカル VM では「ファイルが正しく書けたか」までしか確認できない
   - 初回 push 時にワークフロー実起動 → 失敗があれば修正、というイテレーションが必要

2. **既存の手書き pre-commit を上書きした**
   - 元の hook も pytest を呼んでいたので機能後退はないが、SKIP_TESTS=1 は引き続き有効に保った
   - 既存の運用と互換

3. **`pre-commit` フレームワーク本体は未インストール**
   - `.pre-commit-config.yaml` は将来 `pip install pre-commit && pre-commit install` した時のための保険
   - 現時点の主軸は `tools/install_hooks.sh` で .git/hooks/ に直書きする方式

4. **`make verify` + pytest で pre-commit が ~7 秒程度かかる**
   - 受容範囲だが、横展開で対象ファイルが増えると伸びる可能性
   - 必要なら `--skip-missing-docstring` を外すタイミングで再評価

### 残課題

- **CI 初回起動の確認**：GitHub に push したあと、ワークフローが実際に走り、両ジョブが green になることを目視確認する。失敗時はログを見て調整。
- 横展開（src/ docstring 整備）後に Makefile の `--skip-missing-docstring` を外す

### 判定：**実施可能（ローカル完了 / CI はリモート確認待ち）**
