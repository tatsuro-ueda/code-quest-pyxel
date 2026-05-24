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
  - checker
  - guardian
---

# 2026年5月9日 architecture_rules tree-first 後の rule coverage 拡張

> 状態：⑥ Discussion（実装完了 / 検証済み）
> 親タスクノート：`steering/done/20260509-architecture-rules-tree-facts.md`
> 完了条件：tree-first 化した `facts` を前提に、`validation_rules` の coverage を deterministic / llm_assisted / manual の各観点で拡張する方針が固まり、次の checker / guardian 拡張単位が切り出されていること

---

## 1) Journey

- **上流ジョブ**：tree-first に整理した architecture rules を、より多くの rule で実際の guardrail に変える
- **深層的目的**：読みやすい YAML を守りの強さにもつなげる

1. 🙂 `facts.tree` は読みやすくなったが、guardian が自動で見ている deterministic rule はまだ 4 件に限られていた
2. Before：`scene_mvp_boundary` や `shared_service_vs_state_boundary` は tree があっても `skipped` のままで、次に何を deterministic 化するかが YAML 上で読めなかった
3. After：各 `validation_rules` に `coverage` を持たせ、`deterministic_review` / `next_checker_unit` / `guardian_autofix` / `rationale` を明示したことで、次の checker 拡張単位と guardian の見送り理由が repo 内に残った

### やらないこと

- いきなり全 rule を hard fail にしない
- `.pyxres` の意味判断を Python だけに押し込まない

---

## 2) Gherkin

```gherkin
Feature: tree-first 後の rule coverage 拡張
  Scenario: deterministic 化できる rule を切り分ける
    Given tree-first facts がある
    When  validation_rules を棚卸しする
    Then  Python だけで判定できる rule を切り出せる

  Scenario: llm_assisted の入力根拠を tree から拾える
    Given scene / shared の path が tree node で明示されている
    When  LLM 補助 rule の入力を設計する
    Then  対象 path と責務説明を一貫した形で渡せる
```

---

## 3) Design

- `validation_rules[*].coverage` を追加し、各 rule の現在地と次の拡張単位を YAML に持たせる
- checker は `coverage_review` を返し、mode ごとの件数、deterministic 候補 2 件、guardian の既存 / 見送り判定を JSON から読めるようにする
- `scene_mvp_boundary` は既存の static guard を昇格させる前提で `scene_static_boundary_checks` を次単位にする
- `shared_service_vs_state_boundary` は shared 配下の配置・命名・禁止 API 利用を昇格させる前提で `shared_directory_role_checks` を次単位にする
- guardian は既存 deterministic 4 rule の autofix を維持し、新規の code 移動 / 責務再配置系 autofix は安全でないため見送る

---

## 4) Tasklist

- [x] tree-first 化後の `validation_rules` を mode ごとに棚卸しする
- [x] deterministic 化候補を 1〜2 件に絞る
- [x] guardian の autofix 対象を増やせるか判定する

### 作業記録

#### 2026年5月9日

**Observe**：`validation_rules` には mode はあるが、「どこまで自動化済みで次に何を切り出すか」は YAML から読めなかった  
**Think**：task note だけに判断を書くと checker / guardian から再利用できない。rule ごとに coverage metadata を持たせる方が次の実装単位を固定しやすい  
**Act**：`coverage` を各 rule に追加し、checker に `coverage_review` 集計を実装。`scene_mvp_boundary` と `shared_service_vs_state_boundary` を deterministic 候補 2 件として固定し、guardian の新規 autofix は今回は見送ると判断した

---

## 5) Result

### 棚卸し結果

- `deterministic` 4 件：`runtime_entry_chain`, `dist_not_source`, `generated_files_edit_policy`, `build_runbook_paths`
- `llm_assisted` 3 件：`code_maker_primary_editor`, `scene_mvp_boundary`, `shared_service_vs_state_boundary`
- `manual` 1 件：`pyxres_source_of_truth`

### deterministic 候補として残した 2 件

- `scene_mvp_boundary`
  - 次単位：`scene_static_boundary_checks`
  - 根拠：既存の `test_cjg_framework_rule_guards.py` と scene ディレクトリ構造 test を使えば、Pyxel 呼び出し境界・入力取得禁止・scene package 形状までは static に昇格できる
- `shared_service_vs_state_boundary`
  - 次単位：`shared_directory_role_checks`
  - 根拠：`shared/services` と `shared/state` の配置、命名、Pyxel 利用禁止、state holder / cross-scene model の切り分けは static guard 化できる

### guardian 判定

- 既存 autofix 維持：`runtime_entry_chain`, `dist_not_source`, `generated_files_edit_policy`, `build_runbook_paths`
- 新規 autofix 候補：なし
- 見送り理由：`scene_mvp_boundary` と `shared_service_vs_state_boundary` は code の責務再配置やファイル移動を伴うため、自動修復より warning + 人判断の方が安全

### 作成・更新ファイル

| パス | 種類 | 役割 |
| --- | --- | --- |
| `docs/architecture_rules.yml` | 更新 | `validation_rules[*].coverage` を追加し、原則文を「〜しなければならない / 〜してはならない」へ寄せた |
| `tools/check_architecture_rules.py` | 更新 | `coverage` schema を検証し、`coverage_review` を JSON 出力する |
| `tools/architecture_guardian.py` | 更新 | YAML 書き戻し時の可読整形を統一し、後続の autofix でも file ごとの切れ目を維持する |
| `test/test_architecture_rules_checker.py` | 更新 | coverage metadata と `coverage_review` の regression test を追加 |
| `test/test_architecture_guardian.py` | 更新 | guardian の YAML 整形と新 schema fixture を検証する |

### 動作確認

```text
$ python3 -m pytest test/test_architecture_rules_checker.py -q
10 passed in 1.45s

$ python3 -m pytest test/test_architecture_guardian.py -q
3 passed in 0.13s

$ python3 tools/check_architecture_rules.py
run_ok: true, executed_rules: 4, warning_rules: 0

$ python3 tools/architecture_guardian.py
status: OK, cycles: 1

$ python3 -m pytest test/ -q
688 passed, 2 skipped, 14233 subtests passed in 7.01s
```

---

## 6) Discussion

- 派生元：`steering/done/20260509-architecture-rules-tree-facts.md`
- `scene_mvp_boundary` と `shared_service_vs_state_boundary` は、既存 test の static guard を checker registry に昇格させる次タスクへそのまま接続できる
- `code_maker_primary_editor` と `pyxres_source_of_truth` は、子どもが見ている実物や変更意図の読解が不可欠なので、当面は `llm_assisted` / `manual` を維持する
