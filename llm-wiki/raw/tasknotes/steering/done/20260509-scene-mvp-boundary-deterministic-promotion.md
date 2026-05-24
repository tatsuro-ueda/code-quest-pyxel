---
status: done
priority: normal
scheduled: 2026-05-09T00:00:00.000+09:00
dateCreated: 2026-05-09T00:00:00.000+09:00
dateModified: 2026-05-09T00:00:00.000+09:00
tags:
  - task
  - architecture
  - framework-rule
  - checker
  - archived
---

# 2026年5月9日 scene MVP boundary の deterministic 昇格

> 状態：⑥ Discussion（実装完了 / 検証済み）

---

## 1) Journey（どこへ行くか）

- **深層的目的**：scene 境界を機械で見張る
- **やらないこと**：責務移動を guardian に自動でやらせること

**Before（現状）**：
- 💦 `scene_mvp_boundary` は `llm_assisted` / `candidate` で、checker が自動実行していなかった
- 💦 pytest 側の static guard と architecture checker が分断されていた

**After（達成状態）**：
- ❤️ `scene_mvp_boundary` は deterministic rule として checker で実行される
- ❤️ guardian は warning を出すだけで、autofix は増やしていない

---

## 2) Gherkin（完了条件）

### シナリオ1：scene 境界違反を checker が機械で検出できる

🧱 Given：scene 配下の pyxel 呼び出し境界や package 形状に規約がある  
🎬 When：checker を実行する  
✅ Then：違反があれば deterministic rule として warning を返せる

### シナリオ2：既存 test と二重管理にならない

🧱 Given：同種の static guard がすでに pytest にある  
🎬 When：checker 側へ昇格する  
✅ Then：同じ規約を checker 出力でも読める

### シナリオ3：guardian が危険な自動修復をしない

🧱 Given：責務違反の修正は file move や code rewrite を伴う  
🎬 When：guardian を実行する  
✅ Then：autofix はせず `not_recommended` を維持する

---

## 3) Design（どうやるか）

- 既存の scene structure / pyxel draw / input read guard を checker 側へ写す
- `docs/architecture_rules.yml` の `scene_mvp_boundary` を deterministic / implemented へ更新する
- guardian の autofix は増やさない

### 1-2-3 の組み込み方

1. **rule 先行**  
   `scene_mvp_boundary` が何を deterministic に見るかを YAML に先に固定する
2. **deterministic check へ昇格**  
   `scene_static_boundary_checks` を checker registry に実装する
3. **guardian は安全な正規化だけ**  
   coverage metadata 以外の自動修復は増やさない

---

## 4) Tasklist

- [x] rule 先行：deterministic scope を YAML に固定した
- [x] red：7 deterministic / 2 skipped を期待する checker test に倒した
- [x] green：`scene_static_boundary_checks` を checker に実装した
- [x] deterministic 昇格：coverage を `implemented` に更新した
- [x] guardian 境界確認：`not_recommended` を維持した

### 作業記録

#### 2026年5月9日

**Observe**：scene 境界は pytest では守れていたが、checker coverage review では candidate のままだった  
**Think**：まずは file 構造、model/presenter の pyxel draw 禁止、view 系の input 読み禁止までを deterministic 化するのが妥当  
**Act**：`tools/check_architecture_rules.py` に `scene_static_boundary_checks` を追加し、YAML rule を昇格させた

---

## 5) Result（成果物）

### 実施内容

- `docs/architecture_rules.yml` の `scene_mvp_boundary` を deterministic 化した
- `tools/check_architecture_rules.py` に `scene_static_boundary_checks` を追加した
- `test/test_architecture_rules_checker.py` に real repo expectation と fixture warning test を追加した

### 検証結果

```text
$ python3 tools/check_architecture_rules.py
run_ok: true, executed_rules: 7, warning_rules: 0

$ python3 tools/architecture_guardian.py
status: OK

$ python3 -m pytest test/test_architecture_rules_checker.py test/test_cjg_scene_directory_structure.py test/test_cjg_framework_rule_guards.py -q
47 passed, 20 subtests passed
```

---

## 6) Discussion（反省）

- checker に上げたのは static に判定できる範囲だけで十分だった
- `scene` の責務修正そのものは依然として人手判断が必要なので、autofix を増やさなかったのは妥当

---

### 反省とルール化

- 次にやること：pytest に新しい static guard を足したら checker 昇格余地も同時に見る
