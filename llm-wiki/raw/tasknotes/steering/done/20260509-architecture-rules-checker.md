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

# 2026年5月9日 architecture_rules.yml checker 初版

> 状態：⑥ Discussion（実装完了 / 検証済み）
> 親タスクノート：`steering/done/20260508-architecture-rules-yaml.md`
> 対応シナリオ：CJ37（責務が曖昧で直すほど別の所が壊れる）/ CJ44（シンプルさは変更速度の前提条件）
> 完了条件：`docs/architecture_rules.yml` の `validation_rules` を読んで、repo 実体に照らして deterministic rule を warning として報告できる Python CLI が動作し、AI 向け Gherkin を満たす

---

## 1) Journey

- **上流ジョブ**：AI / 大人が「この repo は architecture_rules.yml に従っているか」をすばやく確認できる状態をつくる
- **深層的目的**：YAML を読んで人が手で照合する運用から、warning ベースの checker でズレを早く見つける運用へ移す

1. 💦 `docs/architecture_rules.yml` はあるが、実コードや実ファイルと合っているか毎回手で見比べる必要がある
2. Before：規約違反の見落としや、見ている人ごとの差が出やすい
3. After：1 コマンドで deterministic rule の warning 一覧が出て、`llm_assisted` / `manual` は未実行として区別して読める

### やらないこと

- 初版から hard fail checker にはしない
- 初版から LLM 呼び出し本体までは入れない
- `.pyxres` の意味判断や実物確認を Python だけで自動化しない
- `facts` 全体を網羅検査するのではなく、まずは `validation_rules` を主語にする

---

## 2) Gherkin

### USM

- As a AI / 大人
- I want to `docs/architecture_rules.yml` の rule を repo 実体に照らして自動で見たい
- So that architecture のズレを人手レビュー前に warning として早く拾える

### 人間レベル Gherkin

```gherkin
Feature: architecture_rules checker の初版
  Scenario: deterministic rule をまとめて確認できる
    Given docs/architecture_rules.yml と repo 実体がある
    When  checker CLI を実行する
    Then  deterministic rule ごとに OK / warning が JSON で出力される
    And   llm_assisted / manual rule は未実行として JSON 上で区別される

  Scenario: warning を読めばどこが怪しいかわかる
    Given rule 違反または YAML と実体のズレがある
    When  checker の結果を見る
    Then  rule id と rule message が JSON に含まれる
    And   どの path / check を見たのか追いやすい構造になっている
    And   直すために何をすべきかが JSON から分かる
    And   warning だけなら exit code は 0 のままである
```

### AI 検収レベル Gherkin

```gherkin
Feature: validation_rules を主語にした warning checker
  Scenario: rule 定義を読んで deterministic だけ実行する
    Given docs/architecture_rules.yml の validation_rules
    When  checker が rule を走査する
    Then  enforcement.mode == deterministic の rule だけ実行対象になる
    And   enforcement.mode == llm_assisted または manual の rule は skip 扱いになる

  Scenario: deterministic check が repo 実体と照合される
    Given runtime_entry_chain, dist_not_source, generated_files_edit_policy, build_runbook_paths の rule がある
    When  checker が repo の file / path / script を読む
    Then  YAML の scope / evidence に対応する check 関数で warning 判定できる
```

---

## 3) Design

### 大まかな責務分担

- **`docs/architecture_rules.yml`** — ルールブック本体。`validation_rules` が「何をチェックするか」を定義する。
- **`tools/check_architecture_rules.py`** — checker の本体 CLI。YAML を読み、実行可能な rule を順番に走らせ、warning / skip を表示する。
- **check 関数群** — `evidence.checks` に書かれた名前ごとに対応する Python 関数。repo 実体を読んで OK / warning を判定する。

### 採用方針

- checker は `docs/architecture_rules.yml` を主入力にする
- 初版は `facts` 全体ではなく `validation_rules` を主語にする
- 初版は repo 実体との照合まで行う
- 実行対象は `deterministic` rule のみ
- `llm_assisted` / `manual` は定義を読んだ上で skip 表示する
- warning only で始める
- warning が出ても exit code は 0 のままにする
  - 非 0 は YAML 読み込み失敗や CLI 実行失敗のような実行エラーに限る
- CLI 名は `tools/check_architecture_rules.py` に固定する
- 出力形式は JSON にする
- `evidence.checks` の各名前は Python の check 関数と 1:1 で対応させる
- warning の JSON に「次に何をすべきか」を入れる
- 修正ガイドの正本は `docs/architecture_rules.yml` 側に置く
  - Python は YAML に書かれた修正ガイドを結果 JSON に載せるだけにする
- 方式は `rule-runner 型`
  - YAML がルールブック
  - Python がそのルールを順番に読む見回り係

### 親ディレクトリで責務がわかるファイル一覧

| パス | 責務 |
| ----- | ----- |
| `docs/architecture_rules.yml` | architecture rule の正本。checker が読む入力 |
| `tools/check_architecture_rules.py` | rule-runner 型の warning checker CLI |
| `test/` | checker の unit test / fixture の置き場 |

### 初版で実行対象にする deterministic rule

- `runtime_entry_chain`
- `dist_not_source`
- `generated_files_edit_policy`
- `build_runbook_paths`

### JSON 出力の最小 schema

初版の CLI は stdout に JSON だけを出す。人間向け整形表示は後回しにし、まずは他ツールから読める形を優先する。

```json
{
  "run_ok": true,
  "has_warnings": true,
  "summary": {
    "total_rules": 8,
    "executed_rules": 4,
    "warning_rules": 1,
    "skipped_rules": 4,
    "error_rules": 0
  },
  "results": [
    {
      "rule_id": "runtime_entry_chain",
      "status": "ok",
      "severity": "warning",
      "mode": "deterministic",
      "checked_paths": [
        "main.py",
        "src/runtime/main_runtime.py",
        "src/runtime/app.py"
      ],
      "failed_checks": [],
      "message": null,
      "suggested_actions": []
    }
  ]
}
```

`status` は次の 4 種に固定する。

- `ok`
- `warning`
- `skipped`
- `error`

### YAML に持たせる追加情報

`docs/architecture_rules.yml` の各 `validation_rules` に、初版 checker 用として次の key を追加する。

- `suggested_actions`
  - warning が出たときに、次に何をすべきかを短い文で並べる

配置は rule のトップレベルに置く。  
つまり、`message` が「何がまずいか」、`suggested_actions` が「次に何をするか」を担当する。

例:

```yaml
  - id: generated_files_edit_policy
    summary: generated module は手編集禁止で、編集元が assets/*.yaml に固定されている
    severity: warning
    enforcement:
      mode: deterministic
    scope:
      paths:
        - src/generated
        - assets
        - tools/gen_data.py
    evidence:
      checks:
        - generated_entries_mark_non_hand_editable_and_sources
    message: generated module の手編集禁止ポリシーまたは入力元定義が欠けている可能性があります
    suggested_actions:
      - src/generated 配下を手編集せず、assets/*.yaml を修正して tools/gen_data.py を実行する
      - docs/architecture_rules.yml の generated.entries に hand_editable: false と source_paths をそろえる
```

### check 関数の呼び出しモデル

`evidence.checks` に書かれた名前を、そのまま Python 関数名として引く。

- YAML: `wrapper_chain_present`
- Python: `def wrapper_chain_present(context, rule) -> CheckOutcome`

ここで `context` は repo root, parsed YAML, facts, path helper をまとめた読み取り専用の入れ物、  
`rule` は現在実行中の validation rule 本体とする。

### deterministic rule 4 件の判定方針

| rule_id | 何を見るか | warning になる条件 |
| ----- | ----- | ----- |
| `runtime_entry_chain` | `main.py`, `src/runtime/main_runtime.py`, `src/runtime/app.py`, `facts.runtime.entry_chain` | path 不在 / `Game` 不在 / wrapper → shim → Game の流れをコードと facts が満たさない |
| `dist_not_source` | `facts.repository.roots`, `dist/` | `dist` が root facts に無い / `source_of_truth: false` でない / `status: distribution` でない |
| `generated_files_edit_policy` | `facts.generated.entries`, `src/generated/`, `assets/`, `tools/gen_data.py` | generated entry に `hand_editable: false` が無い / source path が assets を指さない / target path が存在しない |
| `build_runbook_paths` | `facts.runbooks`, `facts.distribution.artifacts`, `tools/build_*.py`, `Makefile` | runbook command に出る script path が存在しない / 出力 artifact path が artifact facts と対応しない |

### 終了コード

- `0`
  - 実行成功
  - warning が 0 件でも 1 件以上でも同じ
- `1`
  - YAML parse 失敗
  - 必須 key 欠落
  - check 実行中の内部例外
  - CLI 引数不正

### test 方針

- `unit`
  - YAML loader
  - rule filtering
  - check registry
  - 各 deterministic check の pure function 部分
- `integration`
  - repo の実ファイルを読む CLI 実行
  - stdout JSON が parse できること
  - warning があっても exit 0 のままなこと
  - broken fixture では warning result と `suggested_actions` が返ること

### 初版のイメージ

```json
{
  "ok": true,
  "warnings": 1,
  "results": [
    {
      "rule_id": "runtime_entry_chain",
      "status": "ok",
      "mode": "deterministic",
      "checked_paths": [
        "main.py",
        "src/runtime/main_runtime.py",
        "src/runtime/app.py"
      ]
    },
    {
      "rule_id": "generated_files_edit_policy",
      "status": "warning",
      "mode": "deterministic",
      "message": "generated module の手編集禁止ポリシーまたは入力元定義が欠けている可能性があります",
      "checked_paths": [
        "src/generated",
        "assets",
        "tools/gen_data.py"
      ],
      "failed_checks": [
        "generated_entries_mark_non_hand_editable_and_sources"
      ],
      "suggested_actions": [
        "src/generated 配下を手編集せず、assets/*.yaml を修正して tools/gen_data.py を実行する",
        "docs/architecture_rules.yml の generated.entries に hand_editable: false と source_paths をそろえる"
      ]
    },
    {
      "rule_id": "code_maker_primary_editor",
      "status": "skipped",
      "mode": "llm_assisted",
      "reason": "初版では deterministic rule のみ実行する"
    }
  ]
}
```

---

## 4) Tasklist

- [x] T1: `docs/architecture_rules.yml` の `validation_rules` に `suggested_actions` を追加する
- [x] T2: `test/test_architecture_rules_checker.py` を作成し、YAML 契約・deterministic 実行・JSON/exit code の failing test を先に書く
- [x] T3: `tools/check_architecture_rules.py` を作成し、YAML loader / rule-runner / skipped JSON / CLI 骨格を実装する
- [x] T4: deterministic rule 4 件の check 関数を実装し、repo 実体との照合で OK / warning を返せるようにする
- [x] T5: warning JSON に `checked_paths` / `failed_checks` / `message` / `suggested_actions` を載せる
- [x] T6: checker 専用 test と `python3 tools/check_architecture_rules.py` を実行して AI 向け Gherkin を照合する
- [x] T7: 追加で不足が見つかったら Tasklist に追記して埋める


## 5) Result

### 作成・更新ファイル

| パス | 種類 | 役割 |
| ----- | ----- | ----- |
| `docs/superpowers/plans/2026-05-09-architecture-rules-checker.md` | 新規 | checker 実装計画 |
| `docs/architecture_rules.yml` | 更新 | 各 `validation_rules` に `suggested_actions` を追加 |
| `tools/check_architecture_rules.py` | 新規 | deterministic rule を JSON warning として返す CLI |
| `test/test_architecture_rules_checker.py` | 新規 | checker の unit / integration test |
| `steering/done/20260509-architecture-rules-checker.md` | 更新 | 実装計画と結果記録 |

### 動作確認

```text
$ python3 -m pytest test/test_architecture_rules_checker.py -q
4 passed in 0.42s

$ python3 tools/check_architecture_rules.py
{
  "run_ok": true,
  "has_warnings": false,
  "summary": {
    "total_rules": 8,
    "executed_rules": 4,
    "warning_rules": 0,
    "skipped_rules": 4,
    "error_rules": 0
  },
  ...
}

$ python3 -m pytest test/ -q
673 passed, 8 skipped, 14233 subtests passed in 2.83s
```

### Open Questions
 
- なし

---

## 6) Discussion

### いま決まっていること

- `validation_rules` を主語にする
- repo 実体との照合まで入れる
- `deterministic` だけ実行する
- `llm_assisted` / `manual` は skip 表示にする
- CLI は warning checker として始める
- warning-only のため、warning 件数では fail させない
- CLI 名は `tools/check_architecture_rules.py` とする
- 出力は機械可読な JSON とする
- `evidence.checks` と Python 関数は 1:1 対応にする
- warning JSON には `checked_paths` / `failed_checks` / `suggested_actions` を含める
- 修正ガイドの正本は YAML 側に持たせる
- YAML の修正ガイド key 名は `suggested_actions` にする
- 初版の終了コードは `warning では 0 / 実行失敗だけ 1` にする

### AI 向け Gherkin 照合

| シナリオ | 結果 |
| ----- | ----- |
| deterministic だけ実行し、llm/manual は skip 扱い | ✅ `executed_rules = 4`, `skipped_rules = 4` を CLI JSON で確認 |
| deterministic check が repo 実体と照合される | ✅ `runtime_entry_chain`, `dist_not_source`, `generated_files_edit_policy`, `build_runbook_paths` を実コード・実ファイルに照合 |
| warning が出ても exit code は 0 | ✅ broken YAML fixture を使う test で確認 |
| warning JSON から直し方が分かる | ✅ `suggested_actions` を YAML 正本から返す test で確認 |

### まとめ

初版の architecture rule checker は実装完了。`validation_rules` を主語にし、deterministic rule のみを実行して JSON を返す。`llm_assisted` / `manual` は skipped として区別され、warning 時は `checked_paths` / `failed_checks` / `message` / `suggested_actions` で修正の起点が分かる。
