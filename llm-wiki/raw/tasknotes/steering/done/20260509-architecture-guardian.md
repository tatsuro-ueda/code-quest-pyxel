---
status: done
priority: high
scheduled: 2026-05-09T00:00:00.000+09:00
dateCreated: 2026-05-09T00:00:00.000+09:00
dateModified: 2026-05-09T23:59:00.000+09:00
tags:
  - task
  - architecture
  - guardian
  - checker
  - autofix
---

# 2026年5月9日 architecture guardian 自動修復ループ

> 状態：⑥ Discussion（実装完了 / 検証済み）
> 親タスクノート：`steering/done/20260509-architecture-rules-checker.md`
> 対応シナリオ：CJ37（責務が曖昧で直すほど別の所が壊れる）/ CJ44（シンプルさは変更速度の前提条件）
> 完了条件：guardian が `checker -> fixer -> recheck` を最大 5 周回し、直せる違反を working tree 上で自動修復し、残った問題だけを `NEEDS_HUMAN` / `ERROR` として返す

---

## 1) Journey

- **上流ジョブ**：AI / 大人が repo の architecture drift を見つけた瞬間に止まらず、直せるものは自動で戻せる状態をつくる
- **深層的目的**：warning を読む道具から、修復まで引き受ける守護者へ上げる

1. 💦 checker は warning を返せるが、直せる問題でも人がコマンドや patch を考える必要がある
2. Before：generated / dist / runbook / entry chain のような機械的 drift でも、毎回人が復旧オペを回す
3. After：guardian が `scan -> repair -> reverify` を自動で回し、直せるものは working tree に反映したうえで再検査する

### やらないこと

- `.pyxres` の意味変更は自動修復しない
- scene 責務再設計のような曖昧修正はやらない
- commit / push / PR は guardian の責務にしない

---

## 2) Gherkin

### USM

- As a AI / 大人
- I want to architecture guardian が直せる違反を自動で直してから結果を返してほしい
- So that 人がやるのは本当に判断が必要な修正だけになる

### 人間レベル Gherkin

```gherkin
Feature: architecture guardian の自動修復
  Scenario: generated rule の drift を自動修復する
    Given generated_files_edit_policy に反する状態がある
    When  guardian を通常実行する
    Then  guardian は generated 側の drift を直す
    And   同じ rule を再検査して clean なら AUTOFIXED として返す

  Scenario: dist / artifact drift を自動修復する
    Given dist artifact が不足しているか古い
    When  guardian を通常実行する
    Then  guardian は build を回して artifact を再生成する
    And   再検査で clean なら AUTOFIXED として返す

  Scenario: 直せない問題だけ人へ返す
    Given 自動修復の境界を超える問題がある
    When  guardian を通常実行する
    Then  guardian は最大 5 周まで試す
    And   残った問題だけを NEEDS_HUMAN または ERROR として返す
```

### AI 検収レベル Gherkin

```gherkin
Feature: guardian loop（AI 検収）
  Scenario: checker / fixer / recheck の 3 段が分離されている
    Given guardian module
    When  実装を読む
    Then  checker, fixer, guardian loop の役割が関数または型で分かれている

  Scenario: 最大 5 周の自動修復ループ
    Given 自動修復で収束する fixture
    When  guardian を実行する
    Then  cycle 数は 5 以下である
    And   final result は remaining warning を持たない

  Scenario: rule filtering と warning fail mode
    Given 特定 rule だけ再確認したい
    When  checker を --rule-id つきで実行する
    Then  指定 rule だけが走る
    And   --fail-on-warning では warning 件数 > 0 で exit 1 になる
```

---

## 3) Design

### 構成

- **`tools/check_architecture_rules.py`**
  - schema / registry validation
  - rule filtering
  - fail-on-warning
  - `expected / observed / rule_source` を含む診断 JSON
- **`tools/architecture_guardian.py`**
  - checker 結果を読む
  - autofixable rule を fixer に渡す
  - 最大 5 周の loop を回す
- **fixer 関数群**
  - `generated_files_edit_policy`
  - `dist_not_source`
  - `build_runbook_paths`
  - `runtime_entry_chain`

### 状態

- `OK`
- `AUTOFIXED`
- `NEEDS_HUMAN`
- `ERROR`

### autofix の初期対象

- `generated_files_edit_policy`
  - `tools/gen_data.py` 実行
  - `facts.generated.entries` の `hand_editable` / `generated_from` の補正
- `dist_not_source`
  - `dist/` 不在や不足時の release rebuild
  - `facts.repository.roots.dist_root` の正規化
- `build_runbook_paths`
  - artifact 不足時の rebuild
  - `facts.runbooks` / `facts.distribution.artifacts` の path 補正
- `runtime_entry_chain`
  - `main.py` wrapper 正規化
  - `facts.runtime.entry_chain` の正規化
  - 必要なら `src/runtime/main_runtime.py` の entry point tail 補正

### ループ停止条件

- 全 warning が消えた
- autofixable rule が残っていない
- 5 周に達した
- guardian 自身が schema error / internal error を出した

### Tasklist

- [x] T1: guardian task note と plan を起票する
- [x] T2: checker を強化する（schema validation, rule filtering, fail-on-warning, expected/observed）
- [x] T3: guardian loop と fixer registry を実装する
- [x] T4: generated / dist / runbook / runtime の autofix を実装する
- [x] T5: guardian 専用 test を追加し、loop 収束と停止条件を検証する
- [x] T6: 実 CLI と full pytest で AI Gherkin を照合する

---

## 4) Result

### 作成・更新ファイル

| パス | 種類 | 役割 |
| ----- | ----- | ----- |
| `docs/superpowers/plans/2026-05-09-architecture-guardian.md` | 新規 | guardian 実装計画 |
| `steering/done/20260509-architecture-guardian.md` | 更新 | guardian task note と実施結果 |
| `tools/check_architecture_rules.py` | 更新 | schema validation, `--rule-id`, `--fail-on-warning`, `expected/observed`, `rule_source` を追加 |
| `tools/architecture_guardian.py` | 新規 | checker -> fixer -> recheck を最大 5 周回す guardian CLI |
| `test/test_architecture_rules_checker.py` | 更新 | checker hardening の回帰 test を追加 |
| `test/test_architecture_guardian.py` | 新規 | guardian の autofix loop / stop 条件 test |

### 動作確認

```text
$ python3 -m pytest test/test_architecture_rules_checker.py test/test_architecture_guardian.py -q
9 passed in 0.71s

$ python3 tools/check_architecture_rules.py --rule-id runtime_entry_chain
{
  "run_ok": true,
  "summary": {
    "total_rules": 1,
    "executed_rules": 1,
    "warning_rules": 0,
    "skipped_rules": 0,
    "error_rules": 0
  },
  ...
}

$ python3 tools/architecture_guardian.py
{
  "status": "OK",
  "cycles": 1,
  "history": [...],
  "applied_fixes": [],
  "final_check": {...}
}

$ python3 -m pytest test/ -q
684 passed, 2 skipped, 14233 subtests passed in 6.27s
```

---

## 5) Discussion

### 方針

guardian は `見るだけの checker` ではなく、`診断 + 自動修復 + 再検査` を一体で回す守護者として実装する。  
ただし commit はしない。working tree に直した内容を残し、人が最後に差分確認できる形に止める。

### AI 向け Gherkin 照合

| シナリオ | 結果 |
| ----- | ----- |
| checker / fixer / guardian loop の役割分離 | ✅ `tools/check_architecture_rules.py` と `tools/architecture_guardian.py` を分離し、fixer registry を独立実装 |
| 最大 5 周の自動修復ループ | ✅ guardian test で `cycles <= 5` を確認 |
| generated drift を自動修復して clean に戻す | ✅ temp repo fixture で `AUTOFIXED` を確認 |
| 直せない問題は `NEEDS_HUMAN` で止める | ✅ `src/runtime/app.py` 欠損 fixture で確認 |
| checker の `--rule-id` | ✅ 実 CLI で `runtime_entry_chain` 単独実行を確認 |
| checker の `--fail-on-warning` | ✅ checker test で exit 1 を確認 |
| warning payload の `expected / observed` | ✅ generated warning fixture test で確認 |

### 実装メモ

- guardian の autofix 対象は初期版として `generated_files_edit_policy`, `dist_not_source`, `build_runbook_paths`, `runtime_entry_chain`
- 自動修復は working tree まで。commit/push は行わない
- current repo は clean 判定のため guardian 実 CLI では `status: OK`, `cycles: 1`
