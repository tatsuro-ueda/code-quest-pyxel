---
status: done
priority: normal
scheduled: 2026-05-09T00:00:00.000+09:00
dateCreated: 2026-05-09T00:00:00.000+09:00
dateModified: 2026-05-09T08:35:00.000+09:00
tags:
  - task
  - architecture
  - yaml
  - readability
  - checker
---

# 2026年5月9日 architecture_rules facts を木構造へ再編

> 状態：⑥ Discussion（実装完了 / 検証済み）
> 親タスクノート：`steering/done/20260508-architecture-rules-yaml.md`
> 対応シナリオ：CJ37（責務が曖昧で直すほど別の所が壊れる）/ CJ44（シンプルさは変更速度の前提条件）
> 完了条件：`docs/architecture_rules.yml` の `facts` が「実在するディレクトリとファイルの木」を主役にした構造へ再編され、人間が repo の地図として上から読めること。あわせて `flows / entry_points / validation_rules` のような横断情報を分離し、checker / guardian が新構造を解釈できる移行方針まで定義されていること

---

## 1) Journey

- **上流ジョブ**：AI / 大人が `docs/architecture_rules.yml` を repo の地図として自然に読める状態をつくる
- **深層的目的**：checker 都合のフラット定義から、人間が迷わず辿れる tree-first な architecture 定義へ上げる

1. 💦 今の `facts` は `repository.roots` / `scenes` / `shared` の列挙が中心で、repo を開いたときのフォルダ構造と頭の中で対応づける必要がある
2. Before：`runtime` や `generated` の意味は分かるが、`src/scenes/battle/view.py` のような実在 path へ降りていく読み方がしづらい
3. After：`src -> scenes -> battle -> view.py` のように実在する木をそのまま読めて、横断的な情報は別セクションにまとまっている

### やらないこと

- `facts` の見た目だけを入れ子にして、中身の責務が曖昧なまま残る変更はしない
- `validation_rules` を一気に全部作り直さない
- guardian / checker を壊したまま schema だけ先に変えない

### 委任度

- 🟡 YAML 再設計と checker 追従がセットなので、方針は CC が固められるが移行順序の設計が必要

---

## 2) Gherkin

### USM

- As a AI / 大人
- I want to `docs/architecture_rules.yml` をディレクトリ木の地図として読めて、必要なときだけ横断ルールを別に追いたい
- So that architecture の把握とレビューが checker 実装より先に自然にできる

### 人間レベル Gherkin

```gherkin
Feature: architecture_rules.yml の tree-first 化
  Scenario: 人が repo の地図として上から読める
    Given architecture_rules.yml を開いた
    When  facts を上から読む
    Then  実在する directory / file の入れ子として構造を辿れる
    And   path 一覧を頭の中で組み立て直さなくてよい

  Scenario: 横断情報を別に読める
    Given runtime entry chain や generated flow のような横断情報が必要
    When  tree 本体とは別のセクションを見る
    Then  実在 path の木と混ざらずに意図を読める
    And   tree node が概念 node で汚れない

  Scenario: checker / guardian が追従できる
    Given tree-first な facts 構造へ移行した
    When  checker と guardian を実行する
    Then  新構造から必要な path / role / artifact 情報を読み取れる
    And   少なくとも既存 deterministic rule は回帰しない
```

### AI 検収レベル Gherkin

```gherkin
Feature: tree-first facts schema の移行設計
  Scenario: facts の主役が実在する木になる
    Given 新しい architecture_rules schema
    When  facts を確認する
    Then  主体は directory / file の tree である
    And   runtime や generated のような横断概念は tree node として混在しない

  Scenario: 横断情報は明示的に分離される
    Given flow / entry point / generated source / validation rule
    When  schema を確認する
    Then  tree 本体とは別セクションで参照される
    And   必要なら tree node の path を key として参照できる

  Scenario: 移行は段階的である
    Given 既存 checker / guardian 実装
    When  schema 変更を適用する
    Then  loader / lookup は新旧差分を吸収する計画を持つ
    And   verify と test で回帰確認できる
```

---

## 3) Design

### 方針

- `facts` の主役は `実在する directory / file の tree`
- 各 node は `path`, `kind`, `status`, `role`, `source_of_truth`, `summary` を持つ
- 子要素は `children` に入れる
- `runtime`, `generated`, `distribution` のような横断概念は tree node ではなく別セクションで持つ
- `validation_rules` は当面維持し、`scope.paths` や参照 lookup を tree に追従させる

### 想定スキーマ

- `facts.tree`
  - root 直下に `index.html`, `main.py`, `src`, `assets`, `tools`, `test`, `templates`, `dist`, `docs`, `steering`
  - `src` の下に `runtime`, `scenes`, `shared`, `generated`, `app.py`, `game_data.py`
  - `src/scenes/battle` のような node をそのまま入れ子にする
- `facts.flows`
  - `generated_game_data`
  - `pyxres_roundtrip`
  - `pyxres_runtime_loading`
- `facts.entry_points`
  - `runtime_entry_chain`
- `facts.runbooks`
  - build / release / post-change sequence
- `validation_rules`
  - 既存 rule を維持しつつ、内部 lookup を tree-aware に変更

### 移行の考え方

1. 先に tree schema を task note で固定する
2. `docs/architecture_rules.yml` を tree-first 化する
3. checker loader に tree lookup helper を追加する
4. guardian fixer が触る `runtime / generated / distribution / runbooks` の参照先を新構造へ移す
5. verify / pytest / guardian 実行で回帰確認する

### リスク

- tree を深くしすぎると YAML が長くなる
- checker が flat 前提で参照している箇所を見落とすと guardian が誤修復する
- `shared` や `scenes` の node 粒度を細かくしすぎると保守コストが上がる

### 委任度

- 🟢 難しい判断は tree の主役化と横断情報分離までで、ここからの実装は CC が順に進められる

---

## 4) Tasklist

> `writing-plans` の方針で、この note の中に実装計画を記録する。TDD・verify・小刻みな回帰確認を前提に進める。

- [x] **Task 1: tree-first facts 向けの失敗テストを追加する**
  - Files:
    - Modify: `test/test_architecture_rules_checker.py`
    - Modify: `test/test_architecture_guardian.py`
  - Steps:
    - [x] tree schema から deterministic rule が読めることを期待する checker test を追加する
    - [x] tree schema から guardian autofix が動くことを期待する fixture test を追加する
    - [x] 対象テストだけ実行して失敗を確認する

- [x] **Task 2: architecture_rules.yml を tree-first facts へ再編する**
  - Files:
    - Modify: `docs/architecture_rules.yml`
  - Steps:
    - [x] `facts.tree` を追加し、root / src / assets / tools / test / templates / dist / docs / steering を実在 path の木として定義する
    - [x] `scenes`, `shared`, `generated`, `distribution` の情報を tree node に寄せる
    - [x] 横断情報を `facts.flows`, `facts.entry_points`, `facts.runbooks`, `facts.migration_notes` に整理する

- [x] **Task 3: checker を tree-aware にする**
  - Files:
    - Modify: `tools/check_architecture_rules.py`
    - Test: `test/test_architecture_rules_checker.py`
  - Steps:
    - [x] tree node lookup helper を追加する
    - [x] `runtime_entry_chain`, `dist_not_source`, `generated_files_edit_policy`, `build_runbook_paths` が tree-first facts を読むよう更新する
    - [x] checker test を実行して green に戻す

- [x] **Task 4: guardian fixer を tree-first facts に追従させる**
  - Files:
    - Modify: `tools/architecture_guardian.py`
    - Test: `test/test_architecture_guardian.py`
  - Steps:
    - [x] generated / dist / runtime / runbook の fixers が tree node を更新するよう変更する
    - [x] guardian fixture test を実行して green に戻す

- [x] **Task 5: 実 repo で回帰確認する**
  - Files:
    - Verify only
  - Steps:
    - [x] `python3 -m pytest test/test_architecture_rules_checker.py test/test_architecture_guardian.py -q`
    - [x] `python3 tools/check_architecture_rules.py`
    - [x] `python3 tools/architecture_guardian.py`
    - [x] `make verify`
    - [x] `python3 -m pytest test/ -q`

### 作業記録

#### 2026年5月9日 00:00（起票）

**Observe**：`architecture_rules.yml` は checker 向けの flat 列挙が多く、人が repo の木として読むには一段変換が必要  
**Think**：主役を tree にし、横断情報を別に分けると読みやすさは上がる。一方で checker / guardian は参照方法の移行が必要  
**Act**：tree-first 化の follow-up task note を起票した

#### 2026年5月9日 08:10（Tasklist 開始）

**Observe**：user は「tasklistへ進み、完走してほしい」と明示している。checker と guardian は現状 flat facts 前提で動いている  
**Think**：schema 変更だけ先に入れると guardian が壊れるので、テスト → YAML 再編 → checker → guardian の順で進める  
**Act**：branch `feature/tree-facts-architecture-rules` を作成し、Tasklist を具体化した

#### 2026年5月9日 08:35（実装完了）

**Observe**：tree-first YAML, checker, guardian, tests, verify を一通り更新しないと Gherkin を閉じられない  
**Think**：`facts.tree` を主役にしつつ `flows / entry_points / runbooks` を横断情報として分ければ、人の読みやすさと機械検査の両方を維持できる  
**Act**：`docs/architecture_rules.yml` を tree-first 化し、checker / guardian の tree lookup と fixer を更新、verify と full pytest まで通した

---

## 5) Result

### 作成・更新ファイル

| パス | 種類 | 役割 |
| ----- | ----- | ----- |
| `docs/architecture_rules.yml` | 更新 | `facts` を tree-first へ再編し、`flows / entry_points / runbooks` を横断情報として分離 |
| `tools/check_architecture_rules.py` | 更新 | tree node lookup を追加し、deterministic rule を新 schema に追従 |
| `tools/architecture_guardian.py` | 更新 | fixers が tree node / entry_points を更新するよう変更 |
| `test/test_architecture_rules_checker.py` | 更新 | real YAML と warning fixture を tree-first 前提へ変更 |
| `test/test_architecture_guardian.py` | 更新 | guardian fixture を tree-first facts 前提へ変更 |
| `steering/20260509-architecture-rules-tree-facts.md` | 更新 | task note の Tasklist / Result / Discussion を記録 |

### 動作確認

```text
$ python3 -m pytest test/test_architecture_rules_checker.py -q
8 passed in 1.14s

$ python3 -m pytest test/test_architecture_guardian.py -q
2 passed in 0.12s

$ python3 tools/check_architecture_rules.py
run_ok: true, executed_rules: 4, warning_rules: 0

$ python3 tools/architecture_guardian.py
status: OK, cycles: 1

$ make verify
verify_module_docstrings OK
CJ link OK
scene_to_cj map OK

$ python3 -m pytest test/ -q
685 passed, 2 skipped, 14233 subtests passed
```

---

## 6) Discussion

### 反省とルール化

- `architecture_rules.yml` は AI 向けの機械可読性だけでなく、人が repo の地図として読めることも正本要件に含める
- tree と横断情報を分けることで、説明責務と検査責務を混ぜない
- 実装順は `赤テスト -> YAML 再編 -> checker -> guardian -> full verify` が安全だった
- 次タスクとして `tree-first facts を前提に llm_assisted / manual rule の coverage をどう広げるか` を切り出した
- 次にやること：
  - tree-first facts を前提に rule coverage 拡張の task note を進める
