---
status: done
priority: normal
scheduled: 2026-05-08T00:00:00.000+09:00
dateCreated: 2026-05-08T00:00:00.000+09:00
dateModified: 2026-05-08T23:59:00.000+09:00
tags:
  - task
  - docs
  - architecture
  - yaml
  - ai-review
---

# 2026年5月8日 architecture.md を architecture_rules.yml に段階移行

> 状態：⑥ Discussion（初版 YAML 実装完了 / follow-up あり）
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
    Then  intended_replacement_for に docs/architecture.md が含まれる
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
- `intended_replacement_for`
- `audiences`
- `intent`

例：

```yaml
meta:
  document_id: architecture_rules
  version: 1
  status: draft
  intended_replacement_for:
    - docs/architecture.md
  replacement_status: staged_migration
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
- `generated_files_edit_policy`
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

## 4) Implementation Plan

> 実行方式：Subagent-Driven。task ごとに implementer → spec review → code quality review の順で回す。

### 4-1. 対象ファイル

- `docs/architecture_rules.yml`
  - sample の `layers` / `rules` を廃止し、`meta` / `facts` / `validation_rules` を持つ初版 schema に置き換える
- `steering/20260508-architecture-rules-yaml.md`
  - 実装結果に合わせて tasklist / result / discussion を更新する
- 参照：
  - `AGENTS.md`
  - `docs/architecture.md`

### 4-2. 実行タスク

#### Task A: sample YAML を schema scaffold に置き換える

1. 先に shape check を失敗させる
   - `python3 -c "from pathlib import Path; import yaml; data = yaml.safe_load(Path('docs/architecture_rules.yml').read_text()); assert set(data) == {'meta', 'facts', 'validation_rules'}"`
2. `docs/architecture_rules.yml` を次の scaffold に全置換する

```yaml
meta:
  document_id: architecture_rules
  version: 1
  status: draft
  intended_replacement_for:
    - docs/architecture.md
  replacement_status: staged_migration
  audiences:
    - ai
    - human
  intent:
    - architecture_source_of_truth
    - human_reviewable
    - checker_readable

facts:
  principles: []
  repository:
    roots: []
  data_flows: []
  runtime: {}
  scenes: []
  shared:
    services: []
    state: []
    ui: []
    constants: []
    assets: []
  generated:
    entries: []
  distribution:
    artifacts: []
  runbooks: []
  migration_notes: []

validation_rules: []
```

3. parse check
   - `python3 -c "from pathlib import Path; import yaml; data = yaml.safe_load(Path('docs/architecture_rules.yml').read_text()); assert set(data) == {'meta', 'facts', 'validation_rules'}; assert data['meta']['intended_replacement_for'] == ['docs/architecture.md']; assert data['meta']['replacement_status'] == 'staged_migration'; print('schema scaffold ok')"`

#### Task B: `facts.principles` / `repository` / `data_flows` を追加する

1. `principles`, `repository.roots`, `data_flows` が空であることを確認
2. `facts.principles` に次を追加
   - `code_maker_primary_editor`
   - `docs_are_requirements`
   - `pyxres_source_of_truth`
   - `dist_is_distribution`
   - `done_requires_real_artifacts`
3. `facts.repository.roots` に次を追加
   - `index.html`, `main.py`, `src`, `assets`, `tools`, `test`, `templates`, `dist`, `steering`, `docs`
4. `facts.data_flows` に次を追加
   - `generated_game_data`
   - `pyxres_roundtrip`
5. verify
   - `python3 -c "from pathlib import Path; import yaml; data = yaml.safe_load(Path('docs/architecture_rules.yml').read_text()); principle_ids = {item['id'] for item in data['facts']['principles']}; root_ids = {item['id'] for item in data['facts']['repository']['roots']}; flow_ids = {item['id'] for item in data['facts']['data_flows']}; assert {'code_maker_primary_editor', 'pyxres_source_of_truth', 'dist_is_distribution'} <= principle_ids; assert {'src_root', 'assets_root', 'dist_root'} <= root_ids; assert {'generated_game_data', 'pyxres_roundtrip'} <= flow_ids; print('principles/repository/data_flows ok')"`

#### Task C: `facts.runtime` / `scenes` / `shared` を追加する

1. `runtime`, `scenes`, `shared.services` の空 shape を確認
2. `facts.runtime` に次を追加
   - entry chain: `main.py -> src/runtime/main_runtime.py -> src/runtime/app.py::Game`
   - `game_responsibilities`
   - `property_forwards`
   - `must_not_store`
3. `facts.scenes` に次を追加
   - `splash_scene`, `title_scene`, `explore_scene`, `town_scene`, `shop_scene`, `battle_scene`, `menu_scene`, `ai_help_scene`, `professor_scene`, `ending_scene`
   - `settings_scene` は `status: removed` として明記
4. `facts.shared` に次を追加
   - `services`
   - `state`
   - `ui`
   - `constants`
   - `assets`
5. verify
   - `python3 -c "from pathlib import Path; import yaml; data = yaml.safe_load(Path('docs/architecture_rules.yml').read_text()); runtime_ids = {item['id'] for item in data['facts']['runtime']['entry_chain']}; scene_ids = {item['id'] for item in data['facts']['scenes']}; service_ids = {item['id'] for item in data['facts']['shared']['services']}; assert {'runtime_main_wrapper', 'runtime_shim', 'runtime_game'} <= runtime_ids; assert {'battle_scene', 'explore_scene', 'settings_scene'} <= scene_ids; assert {'game_state_service', 'audio_system_service', 'image_banks_service'} <= service_ids; print('runtime/scenes/shared ok')"`

#### Task D: `generated` / `distribution` / `runbooks` / `migration_notes` を追加する

1. `generated.entries`, `distribution.artifacts`, `runbooks`, `migration_notes` が空であることを確認
2. `generated.entries` に `dialogue / enemies / items / weapons / armors / spells / shops` を追加
3. `distribution.artifacts` に `dist/code-maker.zip`, `dist/pyxel.html`, `dist/pyxel.pyxapp`, `dist/play.html`, `dist/index.html` を追加
4. `runbooks` に次を追加
   - `build_codemaker_zip`
   - `build_all_release_artifacts`
   - `post_change_release_sequence`
5. `migration_notes` に次を追加
   - `blockquestapp_legacy_shell`
   - `core_scene_manager_legacy`
   - `development_runtime_removed`
6. verify
   - `python3 -c "from pathlib import Path; import yaml; data = yaml.safe_load(Path('docs/architecture_rules.yml').read_text()); gen_ids = {item['id'] for item in data['facts']['generated']['entries']}; artifact_ids = {item['id'] for item in data['facts']['distribution']['artifacts']}; runbook_ids = {item['id'] for item in data['facts']['runbooks']}; note_ids = {item['id'] for item in data['facts']['migration_notes']}; assert {'generated_dialogue', 'generated_enemies', 'generated_shops'} <= gen_ids; assert {'codemaker_zip', 'pyxel_html', 'top_index_html'} <= artifact_ids; assert {'build_codemaker_zip', 'build_all_release_artifacts', 'post_change_release_sequence'} <= runbook_ids; assert {'blockquestapp_legacy_shell', 'core_scene_manager_legacy'} <= note_ids; print('generated/distribution/runbooks/migration ok')"`

#### Task E: `validation_rules` を warning only で定義する

1. `validation_rules` が空であることを確認
2. 次の 8 rule を追加
   - `runtime_entry_chain`
   - `code_maker_primary_editor`
   - `pyxres_source_of_truth`
   - `dist_not_source`
   - `generated_files_edit_policy`
   - `scene_mvp_boundary`
   - `shared_service_vs_state_boundary`
   - `build_runbook_paths`
3. rule schema 条件
   - 全件 `severity: warning`
   - `enforcement.mode` は `deterministic`, `llm_assisted`, `manual` のいずれか
   - 各 rule は `id`, `summary`, `severity`, `enforcement`, `scope`, `evidence`, `message` を持つ
4. verify
   - `python3 -c "from pathlib import Path; import yaml; data = yaml.safe_load(Path('docs/architecture_rules.yml').read_text()); rules = data['validation_rules']; assert len(rules) == 8; assert {rule['severity'] for rule in rules} == {'warning'}; assert {'deterministic', 'llm_assisted', 'manual'} <= {rule['enforcement']['mode'] for rule in rules}; assert all({'id', 'summary', 'severity', 'enforcement', 'scope', 'evidence', 'message'} <= set(rule) for rule in rules); print('validation_rules ok')"`

#### Task F: 最終確認と task note 更新

1. full parse
   - `python3 -c "from pathlib import Path; import yaml; data = yaml.safe_load(Path('docs/architecture_rules.yml').read_text()); assert data['meta']['document_id'] == 'architecture_rules'; assert any(item['id'] == 'runtime_game' for item in data['facts']['runtime']['entry_chain']); assert any(item['id'] == 'battle_scene' for item in data['facts']['scenes']); assert any(item['id'] == 'build_all_release_artifacts' for item in data['facts']['runbooks']); print('full yaml ok')"`
2. coverage spot check
   - `python3 -c "from pathlib import Path; text = Path('docs/architecture_rules.yml').read_text(); required = ['code_maker_primary_editor', 'pyxres_source_of_truth', 'runtime_game', 'post_change_release_sequence', 'blockquestapp_legacy_shell']; missing = [item for item in required if item not in text]; assert not missing, missing; print('architecture coverage spot check ok')"`
3. task note の `Tasklist` / `Result` / `Discussion` を更新
4. repo verification
   - `python3 tools/verify_cj_cjob.py`
   - `python3 tools/scene_to_cj.py --verify-only`
   - `python3 -m pytest test/ -q`

---

## 5) Tasklist

- [x] T1: task note を起票し、Journey / Gherkin / Design を整理する
- [x] T2: `docs/architecture_rules.yml` の初版 schema を実ファイルとして作成する
- [x] T3: `architecture.md` の stable な内容を `facts` に移し始める
- [x] T4: 初版 `validation_rules` を warning only で定義する
- [ ] T5: `architecture.md` を補助説明へ縮小する範囲を別 commit で判断する
- [ ] T6: 将来の Python checker 向けに deterministic / llm_assisted / manual の使い分けを README 化する

---

## 6) Discussion

### Result

- `docs/architecture_rules.yml` は sample から初版の実 schema へ置き換えられた
- top-level は `meta` / `facts` / `validation_rules` を持つ構成になった
- `facts` と `validation_rules` は review loop を通して、実コードの配置と現行 build 挙動に揃うよう精査された
- rule set は warning only のままで、`deterministic` / `llm_assisted` / `manual` をカバーしている
- verification: `full yaml ok`
- verification: `architecture coverage spot check ok`
- verification: `CJ link OK` / `scene_to_cj map OK`
- verification: `python3 -m pytest test/ -q` passed (`669 passed, 8 skipped`)

`architecture.md` の縮小と README / checker usage の文書化は、この task とは分けた follow-up work として残す。

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
