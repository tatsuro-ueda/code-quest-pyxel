---
status: in_progress
priority: normal
scheduled: 2026-05-08T00:00:00.000+09:00
dateCreated: 2026-05-08T00:00:00.000+09:00
dateModified: 2026-05-08T00:00:00.000+09:00
tags:
  - task
  - docs
  - architecture
  - yaml
  - ai-review
---

# 2026年5月8日 architecture.md を architecture_rules.yml に段階移行

> 状態：③ Design（task note 起票 / 設計確定、実装前）
> 対応シナリオ：CJ37（責務が曖昧で直すほど別の所が壊れる）/ CJ44（シンプルさは変更速度の前提条件）
> 完了条件：`docs/architecture_rules.yml` 初版が AI 検収と人間レビューの両方に使える

---

## 1) Journey

- **上流ジョブ**：AI / 大人が repo の責務を毎回迷わず確認できる状態をつくる
- **上流CJ**：CJ37 を主対象。必要に応じて CJ44 の build / SSoT ルールも受ける
- **深層的目的**：`architecture.md` の説明文を「AI が検収に使える定義」に変えつつ、人間が YAML 単体で妥当性を確認できるようにする

1. 💦 AI が repo を読んでも、どれが規約でどれが説明か混ざっていて検収しづらい
2. Before：Markdown の長文を都度解釈するため、責務・SSoT・runbook の抜け漏れが起きる
3. After：`docs/architecture_rules.yml` を読めば、AI は warning ベースで検収でき、人間は YAML 単体で正しさをレビューできる

### やらないこと

- 初版から完全自動の hard fail checker まではやらない
- `.pyxres` 実体の中身を YAML に置き換えない
- `architecture.md` を 1 回で完全削除しない

---

## 2) Gherkin

### USM

- As a AI / 大人
- I want to `docs/architecture_rules.yml` だけで repo の責務・規約・運用手順を把握したい
- So that 実装修正や検収時に `architecture.md` の長文を毎回読み直さなくて済む

### 人間レベル Gherkin

```gherkin
Feature: architecture_rules.yml を人間と AI の共通正本にする
  Scenario: 人間が YAML 単体で妥当性をレビューできる
    Given docs/architecture_rules.yml を開く
    When  repository / runtime / scenes / shared / runbooks を読む
    Then  各項目に責務と正本性が日本語で書かれている
    And   architecture.md を開かなくても大意が追える

  Scenario: AI が YAML 単体で warning ベースの検収観点を得られる
    Given docs/architecture_rules.yml を AI が読む
    When  validation_rules を参照する
    Then  どの rule が deterministic か llm_assisted か manual か区別できる
    And   初版ではすべて severity=warning で扱える
```

### AI 検収レベル Gherkin

```gherkin
Feature: architecture_rules.yml 初版（AI 検収）
  Scenario: 文書の身分が明記されている
    Given docs/architecture_rules.yml
    When  meta を読む
    Then  replaces に docs/architecture.md が含まれる
    And   audiences に ai と human が含まれる

  Scenario: facts と validation_rules が分離されている
    Given docs/architecture_rules.yml
    When  top-level keys を確認する
    Then  facts が存在する
    And   validation_rules が存在する

  Scenario: checker 前提の rule 情報がある
    Given validation_rules の各要素
    When  任意の rule を見る
    Then  severity が warning である
    And   enforcement.mode が deterministic / llm_assisted / manual のいずれかである
    And   scope / evidence / message を持つ
```

---

## 3) Design

### 3-1. 採用方針

採用するのは **「規約 + 実体 + 運用」の 3 層スキーマ**。
`architecture.md` の prose をそのまま YAML に移すのではなく、次の 2 つに分ける。

- **`facts`**：repo の実体定義。何が正本で、どこが何を担当するか
- **`validation_rules`**：AI / 将来の Python checker が何をどう warning 判定するか

これにより、

- 人間は `summary` / `notes` を日本語で読める
- AI は `must` / `must_not` / `source_of_truth` / `enforcement` を読んで検収できる
- 将来の checker は deterministic なものだけ先に自動化できる

### 3-2. 表記ルール

- **キー名**：英語 `snake_case`
- **説明文**：日本語
- **各要素**：可能なら `id` を持つ
- **repo 参照**：`path` と必要に応じて `symbol`
- **state / status**：`active`, `legacy`, `generated`, `distribution`, `removed`
- **rule severity**：初版はすべて `warning`

### 3-3. YAML のトップレベル

```yaml
meta:
facts:
validation_rules:
```

### 3-4. `meta`

文書の身分を定義する。

- `document_id`
- `version`
- `status`
- `replaces`
- `audiences`
- `intent`

例：

```yaml
meta:
  document_id: architecture_rules
  version: 1
  status: draft
  replaces:
    - docs/architecture.md
  audiences:
    - ai
    - human
  intent:
    - architecture_source_of_truth
    - human_reviewable
    - checker_readable
```

### 3-5. `facts`

`facts` は次の単位に分ける。

- `principles`
- `repository`
- `data_flows`
- `runtime`
- `scenes`
- `shared`
- `generated`
- `distribution`
- `runbooks`
- `migration_notes`

#### principles

Code Maker 優先、`pyxres = SSoT`、`dist` は source ではない、done は実物確認まで含む、などの最上位原則。

#### repository

`src`, `assets`, `tools`, `dist`, `docs` などの責務。
単なるツリーではなく `role` と `source_of_truth` を持たせる。

#### data_flows

`assets/*.yaml -> tools/gen_data.py -> src/generated/*.py -> src/game_data.py -> runtime`
のような一方向の流れと、`.pyxres` / Code Maker の流れを表す。

#### runtime

`main.py -> src/runtime/main_runtime.py -> src/runtime/app.py::Game`
の入口チェーン、`Game` の責務、property forward、`Game` が持ってはいけない state を置く。

#### scenes

各 scene の責務、scene-local state、MVP 境界、やってはいけないことを置く。

#### shared

`services`, `state`, `ui`, `constants`, `assets` をまとめる。
特に `services` は scene 横断ロジック、`state` は dataclass 中心の正本 model、`ui` は描画 helper であることを明示する。

#### generated

自動生成物と入力元を明記する。
`src/generated/*.py` を手で触らないこと、入力元は `assets/*.yaml` であることを固定する。

#### distribution

`dist/code-maker.zip`, `dist/pyxel.html`, `dist/pyxel.pyxapp`, `dist/play.html`, `dist/index.html`
など artifact の意味を置く。

#### runbooks

`build_codemaker.py`, `build_web_release.py`, bundle 自己検査などの順序付き手順を置く。
各 step は `command`, `outputs`, `checks`, `common_failures` を持てる形にする。

#### migration_notes

`src/app.py::BlockQuestApp` のような legacy shell や、段階移行中だけ残る注意点を隔離する。

### 3-6. `validation_rules`

各 rule は次の形に揃える。

```yaml
validation_rules:
  - id: runtime_entry_chain
    summary: runtime の入口は wrapper -> shim -> Game の流れを保つ
    severity: warning
    enforcement:
      mode: deterministic
    scope:
      paths:
        - main.py
        - src/runtime/main_runtime.py
        - src/runtime/app.py
    evidence:
      checks:
        - wrapper_chain_present
    message: runtime の入口構成が architecture 定義から外れている可能性があります
```

`enforcement.mode` は初版で次の 3 種を想定する。

- `deterministic`
- `llm_assisted`
- `manual`

### 3-7. 初版で必ず入れる validation rule 群

- `runtime_entry_chain`
- `code_maker_primary_editor`
- `pyxres_source_of_truth`
- `dist_not_source`
- `generated_files_not_hand_edited`
- `scene_mvp_boundary`
- `shared_service_vs_state_boundary`
- `build_runbook_paths`

このうち、

- path / file / symbol / top-level key の確認は `deterministic`
- 責務のにじみや View/Presenter の境界は `llm_assisted`
- build 生成物の実物確認は `manual`

とする。

### 3-8. `architecture.md` からの移行方針

段階移行は 3 ステップで進める。

1. `docs/architecture_rules.yml` に stable な内容をほぼ全部寄せる
2. `docs/architecture.md` を「導入 + YAML の読み方 + 補足説明」に縮小する
3. YAML が安定したら `architecture.md` は短い入口文書へ役割変更する

初版では `architecture.md` を消さないが、検収に必要な事実は YAML 側を優先して追加していく。

---

## 4) Tasklist

- [x] T1: task note を起票し、Journey / Gherkin / Design を整理する
- [ ] T2: `docs/architecture_rules.yml` の初版 schema を実ファイルとして作成する
- [ ] T3: `architecture.md` の stable な内容を `facts` に移し始める
- [ ] T4: 初版 `validation_rules` を warning only で定義する
- [ ] T5: `architecture.md` を補助説明へ縮小する範囲を別 commit で判断する
- [ ] T6: 将来の Python checker 向けに deterministic / llm_assisted / manual の使い分けを README 化する

---

## 5) Discussion

### 採用判断

- **採用**：キーは英語、説明は日本語
- **採用**：`facts` と `validation_rules` を分離
- **採用**：初版は warning only
- **不採用**：Markdown の節構造をそのままフラット YAML に写す方式
- **不採用**：完全日本語キー

### 理由

完全日本語キーは人間には読みやすいが、将来の Python checker と LLM プロンプトの両方で扱いが重くなる。
逆に説明文まで英語にすると、repo の運用者が YAML 単体で妥当性を判断しづらい。
そのため **「構造は英語、意味は日本語」** に固定する。

また、この repo の `architecture.md` は単なるディレクトリ説明ではなく、SSoT / runtime / build / migration note まで含む。
したがって「依存ルールだけの小さな YAML」では足りず、**規約 + 実体 + 運用** を同じ文書に持つ必要がある。

### 次の実装単位

実装の最初の 1 歩は `docs/architecture_rules.yml` の schema 雛形をつくること。
その後に `meta`, `facts.principles`, `facts.runtime`, `facts.runbooks` の順で埋めると、AI 検収への効き目が早い。
