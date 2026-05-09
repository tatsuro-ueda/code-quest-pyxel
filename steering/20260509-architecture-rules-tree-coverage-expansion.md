---
status: open
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

> 状態：① Journey / ② Gherkin / ③ Design 素案
> 親タスクノート：`steering/done/20260509-architecture-rules-tree-facts.md`
> 完了条件：tree-first 化した `facts` を前提に、`validation_rules` の coverage を deterministic / llm_assisted / manual の各観点で拡張する方針が固まり、次の checker / guardian 拡張単位が切り出されていること

---

## 1) Journey

- **上流ジョブ**：tree-first に整理した architecture rules を、より多くの rule で実際の guardrail に変える
- **深層的目的**：読みやすい YAML を守りの強さにもつなげる

1. 🙂 `facts.tree` は読みやすくなったが、guardian が自動で見ている deterministic rule はまだ 4 件に限られる
2. Before：`scene_mvp_boundary` や `shared_service_vs_state_boundary` は tree があっても `skipped` のまま
3. After：tree-first facts を足場に、次に deterministic 化できる rule と LLM 補助が必要な rule の境界が明確になる

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

- `scene_mvp_boundary` の deterministic 化余地を調査する
- `shared_service_vs_state_boundary` の入力を tree node ベースに整理する
- `manual` rule のまま残すべき境界を明記する

---

## 4) Tasklist

- [ ] tree-first 化後の `validation_rules` を mode ごとに棚卸しする
- [ ] deterministic 化候補を 1〜2 件に絞る
- [ ] guardian の autofix 対象を増やせるか判定する

---

## 5) Result

未着手

---

## 6) Discussion

- 派生元：`steering/done/20260509-architecture-rules-tree-facts.md`
