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

# 2026年5月9日 shared boundary の deterministic 昇格

> 状態：⑥ Discussion（実装完了 / 検証済み）

---

## 1) Journey（どこへ行くか）

- **深層的目的**：shared 配置のルールを機械で守る
- **やらないこと**：file move を guardian にやらせること

**Before（現状）**：
- 💦 `shared_service_vs_state_boundary` は candidate のままで、checker が自動実行していなかった
- 💦 `PlayerModel` / legacy shim / service/state holder の境界が checker coverage に出てこなかった

**After（達成状態）**：
- ❤️ `shared_service_vs_state_boundary` は deterministic rule として checker で実行される
- ❤️ shared/state の pyxel 汚染、legacy shim import、role/status drift を自動で warning にできる

---

## 2) Gherkin（完了条件）

### シナリオ1：shared 配置違反を checker が機械で検出できる

🧱 Given：`shared/services` と `shared/state` の責務分担ルールがある  
🎬 When：checker を実行する  
✅ Then：misplace された state / legacy shim 依存を deterministic に warning できる

### シナリオ2：M4-4 の移行と衝突しない

🧱 Given：`PlayerModel` 吸収や legacy helper 縮退が並行する  
🎬 When：shared boundary rule を実装する  
✅ Then：移行後の target state と checker が一致する

### シナリオ3：guardian が危険な移動をしない

🧱 Given：shared 配置違反の修正は file rename / import 更新を伴う  
🎬 When：guardian を実行する  
✅ Then：自動修復はせず、人判断の warning として止まる

---

## 3) Design（どうやるか）

- `shared_directory_role_checks` で 3 種類を見る
- `shared/state` での `pyxel` 利用禁止
- runtime / scenes からの `player_state.py` / `item_use.py` 直 import 禁止
- facts.tree 上の `player_model.py` / legacy shim の role/status 整合

### 1-2-3 の組み込み方

1. **rule 先行**  
   shared の target state と legacy shim の位置づけを YAML に先に固定する
2. **deterministic check へ昇格**  
   `shared_directory_role_checks` を checker registry に追加する
3. **guardian は安全な正規化だけ**  
   autofix は増やさず `not_recommended` を維持する

---

## 4) Tasklist

- [x] rule 先行：shared 境界の target state を YAML / docs に書いた
- [x] red：coverage review と fixture warning test を追加した
- [x] green：`shared_directory_role_checks` を checker に実装した
- [x] deterministic 昇格：coverage を `implemented` に更新した
- [x] guardian 境界確認：autofix を増やさず `not_recommended` を維持した

### 作業記録

#### 2026年5月9日

**Observe**：shared boundary は pytest 側に guard があっても checker coverage では candidate のままだった  
**Think**：`PlayerModel` の source-of-truth role、legacy shim import、shared/state の `pyxel` 汚染をまとめて checker 化すれば十分強い  
**Act**：`tools/check_architecture_rules.py` に `shared_directory_role_checks` を追加し、YAML rule を deterministic 化した

---

## 5) Result（成果物）

### 実施内容

- `docs/architecture_rules.yml` の `shared_service_vs_state_boundary` を deterministic 化した
- `tools/check_architecture_rules.py` に `shared_directory_role_checks` を追加した
- `test/test_architecture_rules_checker.py` に fixture warning test を追加した
- task 1 で入れた legacy shim 再侵入 guard を checker 側にも昇格した

### 検証結果

```text
$ python3 tools/check_architecture_rules.py
run_ok: true, executed_rules: 7, warning_rules: 0

$ python3 tools/architecture_guardian.py
status: OK

$ python3 -m pytest test/test_architecture_rules_checker.py test/test_cjg_framework_rule_guards.py test/test_player_model.py test/test_runtime_shim.py -q
64 passed, 20 subtests passed
```

---

## 6) Discussion（反省）

- shared boundary は「配置」と「依存」を静的に見れば十分役立つ
- file move の autofix は誤爆コストが高いので、今回は warning で止める方が正しい

---

### 反省とルール化

- 次にやること：state/service の legacy 例外を作ったら facts.tree の role/status も同時に更新する
