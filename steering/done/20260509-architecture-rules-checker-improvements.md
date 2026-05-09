---
status: done
priority: normal
scheduled: 2026-05-09T00:00:00.000+09:00
dateCreated: 2026-05-09T00:00:00.000+09:00
dateModified: 2026-05-09T23:59:00.000+09:00
tags:
  - task
  - architecture
  - yaml
  - checker
  - verification
---

# 2026年5月9日 architecture_rules checker 改良

> 状態：⑥ Discussion（guardian 実装に吸収済み）
> 親タスクノート：`steering/done/20260509-architecture-rules-checker.md`
> 対応シナリオ：CJ37（責務が曖昧で直すほど別の所が壊れる）/ CJ44（シンプルさは変更速度の前提条件）
> 完了条件：checker が「何が壊れているか」だけでなく「どこをどう見直せばよいか」をより具体的に返し、CLI と自己検証も運用向きになる

---

## 1) Journey

- **上流ジョブ**：AI / 大人が architecture rule のズレを早く見つけて、迷わず直せる状態をつくる
- **深層的目的**：初版 checker の「warning を出せる」段階から、「warning を使って修正作業を前に進められる」段階へ上げる

1. 💦 checker は動くが、warning が出たときに「何が実際に見つかったか」「どの rule だけ見たいか」「CI で fail させたいか」を細かく扱えない
2. Before：JSON は返るが、修正者が自分で追加調査する量がまだ多い。loader も top-level key しか見ておらず、rule 定義ミスを早期発見しづらい
3. After：checker が rule 単位で実行でき、warning には expected / observed のような具体情報が入り、YAML 定義ミスも checker 自身が検知できる

### やらないこと

- 今回も `llm_assisted` / `manual` の本実行までは入れない
- checker を最初から巨大なフレームワークにしない
- `architecture_rules.yml` の全設計を作り直さない

---

## 2) Gherkin

### USM

- As a AI / 大人
- I want to checker の warning からそのまま修正作業に入れて、必要なら特定 rule だけを再実行したい
- So that architecture のズレ修正を小さく、速く、繰り返せる

### 人間レベル Gherkin

```gherkin
Feature: architecture_rules checker の改良
  Scenario: warning の中身だけで直し始められる
    Given checker が warning を返した
    When  JSON を読む
    Then  期待していた値と実際に見つかった値の差が分かる
    And   修正者が追加調査なしで次の修正候補を決めやすい

  Scenario: 特定 rule だけを再実行できる
    Given 1 つの rule だけ直して確認したい
    When  checker を rule 指定つきで実行する
    Then  指定した rule だけが実行される
    And   他 rule の結果に埋もれず再確認できる

  Scenario: warning を CI では fail 扱いに切り替えられる
    Given ローカルでは warning-only の運用を続けたい
    And   CI では warning を失敗として扱いたい
    When  fail-on-warning オプション付きで checker を実行する
    Then  warning が 1 件以上あると非 0 で終了する
```

### AI 検収レベル Gherkin

```gherkin
Feature: checker 自己検証と実行モード拡張
  Scenario: validation_rules 定義ミスを checker 自身が検知する
    Given docs/architecture_rules.yml の validation_rules に必須 key 欠落や未知の check 名がある
    When  checker を実行する
    Then  実行前の schema / registry 検証で error が返る

  Scenario: rule 指定実行
    Given runtime_entry_chain だけ見たい
    When  checker を --rule-id runtime_entry_chain で実行する
    Then  summary.executed_rules は 1 になる
    And   results はその rule だけを含む

  Scenario: warning payload が比較情報を持つ
    Given deterministic rule が失敗する fixture
    When  checker が warning を返す
    Then  result に expected / observed / checked_paths が含まれる
    And   failed_checks と suggested_actions も維持される
```

---

## 3) Design

### 改良対象

- **`tools/check_architecture_rules.py`**
  - loader の schema 検証を強化する
  - CLI filtering / fail mode を追加する
  - warning payload に比較情報を追加する
- **`docs/architecture_rules.yml`**
  - 必要なら rule ごとの期待値を補助する field を足す
  - 少なくとも checker が要求する key の正本として振る舞う
- **`test/test_architecture_rules_checker.py`**
  - 各 deterministic rule の warning 系テストを増やす
  - schema error / rule filter / fail-on-warning をカバーする

### 改良の柱

#### 1. loader / registry の自己検証

今は top-level key しか見ていない。次は少なくとも次を検証する。

- 各 `validation_rules` に `id`, `severity`, `enforcement.mode`, `scope.paths`, `evidence.checks`, `message`, `suggested_actions` がある
- `deterministic` rule の `evidence.checks` は全て registry に存在する
- `suggested_actions` は list[str] である

これで rule 定義ミスを「warning 判定の途中」ではなく「起動直後の error」として返せる。

#### 2. CLI 実行モード拡張

少なくとも次を追加候補にする。

- `--rule-id <id>`
  - 1 rule だけ実行
- `--fail-on-warning`
  - warning 件数 > 0 なら exit 1
- `--pretty`
  - JSON 自体は維持しつつ、人が読む indent / sort の指定を安定化

`--mode` のような大きい抽象化は急がず、まずは実運用で効く option から入れる。

#### 3. warning payload の具体化

今の JSON は `message` と `suggested_actions` はあるが、「何を期待して何が見つかったか」が薄い。

次は warning result に次の追加を検討する。

- `expected`
- `observed`
- `rule_source`
  - どの YAML rule を根拠にしたか

例:

```json
{
  "rule_id": "dist_not_source",
  "status": "warning",
  "expected": {
    "status": "distribution",
    "source_of_truth": false
  },
  "observed": {
    "status": "active",
    "source_of_truth": true
  }
}
```

#### 4. test coverage の拡張

初版は `generated_files_edit_policy` の warning path が中心だった。改良では少なくとも次を増やす。

- `runtime_entry_chain` warning fixture
- `dist_not_source` warning fixture
- `build_runbook_paths` warning fixture
- schema error fixture
- `--rule-id` 実行の integration test
- `--fail-on-warning` の exit code test

### Tasklist

- [ ] T1: checker 改良 scope を `loader/registry`, `CLI mode`, `warning payload`, `test coverage` の 4 本に固定する
- [ ] T2: `tools/check_architecture_rules.py` の schema/registry validation を強化する
- [ ] T3: `--rule-id` と `--fail-on-warning` を追加する
- [ ] T4: warning payload に `expected` / `observed` / `rule_source` を追加する
- [ ] T5: deterministic 4 rule の warning fixture test をそろえる
- [ ] T6: AI 向け Gherkin を checker test と実 CLI で照合する

---

## 4) Result

### まだ結果はない

起票のみ。未実装。

---

## 5) Discussion

### なぜこの改良順か

次に大事なのは rule 数を増やすことより、checker の「信用できる壊れ方」と「再実行しやすさ」を先に固めること。  
そのため、`llm_assisted` に進む前に、

- rule 定義ミスを自己検知できる
- 1 rule だけを素早く再実行できる
- warning が expected / observed を持つ

の 3 点を先に上げる方が、運用の密度が上がる。
