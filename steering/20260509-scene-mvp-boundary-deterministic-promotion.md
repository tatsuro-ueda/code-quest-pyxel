---
status: open
priority: normal
scheduled: 2026-05-09T00:00:00.000+09:00
dateCreated: 2026-05-09T00:00:00.000+09:00
dateModified: 2026-05-09T00:00:00.000+09:00
tags:
  - task
  - architecture
  - framework-rule
  - checker
---

# 2026年5月9日 scene MVP boundary の deterministic 昇格

> 状態：③ Design（起票済み / 未着手）
> 次のゲート：（ユーザー）この note を着手対象にしてよいか

---

## 1) Journey（どこへ行くか）

- **深層的目的**：scene 境界を機械で見張る
- **やらないこと**：責務移動を guardian に自動でやらせること

**Before（現状）**：
- 💦 `scene_mvp_boundary` は candidate で、checker から完全自動では見張れていない
- 💦 既存の framework guard test はあるが、architecture checker の deterministic rule へまだ昇格していない

**After（達成状態）**：
- ❤️ scene の model / presenter / view / scene 境界違反を checker が deterministic に warning できる
- ❤️ guardian は warning を出すだけで、危険な code move は自動でやらない

---

## 2) Gherkin（完了条件）

### シナリオ1：scene 境界違反を checker が機械で検出できる

🧱 Given：scene 配下の pyxel 呼び出し境界や package 形状に規約がある  
🎬 When：checker を実行する  
✅ Then：違反があれば deterministic rule として warning を返せる

### シナリオ2：既存 test と二重管理にならない

🧱 Given：同種の static guard がすでに pytest にある  
🎬 When：checker 側へ昇格する  
✅ Then：根拠 test を再利用しつつ、architecture rule 出力でも読める

### シナリオ3：guardian が危険な自動修復をしない

🧱 Given：責務違反の修正は file move や code rewrite を伴う  
🎬 When：guardian を実行する  
✅ Then：NEEDS_HUMAN または warning で止まり、勝手に責務を動かさない

---

## 3) Design（どうやるか）

- 対象ファイルは `docs/architecture_rules.yml`, `tools/check_architecture_rules.py`, `test/test_architecture_rules_checker.py`, `test/test_cjg_framework_rule_guards.py`, `test/test_cjg_scene_directory_structure.py`
- 既存の scene static guard を checker registry へ昇格し、`scene_mvp_boundary` の coverage を `candidate` から `implemented` に寄せる
- guardian は `not_recommended` のまま維持し、autofix は増やさない

### 1-2-3 の組み込み方

1. **rule 先行**  
   `architecture_rules.yml` に「何を deterministic に見るか」を先に固定する
2. **deterministic check へ昇格**  
   既存 pytest guard を checker registry に接続して rule 実行へ昇格する
3. **guardian は安全な正規化だけ**  
   coverage metadata や YAML 整形だけを guardian 対象にし、scene 責務修正は人手のままにする

---

## 4) Tasklist

- [ ] rule 先行：`scene_mvp_boundary` の deterministic scope を YAML に固定する
- [ ] red：checker 側の未実装を示す test を追加する
- [ ] green：scene static boundary checks を checker registry に実装する
- [ ] deterministic 昇格：coverage を `implemented` に更新し、JSON 出力を固定する
- [ ] guardian 境界確認：autofix を増やさず `not_recommended` を維持する

### 作業記録

#### 2026年5月9日（起票）

**Observe**：`scene_mvp_boundary` は candidate のまま残っている  
**Think**：ここは code migration ではなく checker 昇格 task として切る方がよい  
**Act**：`1-2-3` flow を checker task 用に落とし込んだ

#### 2026年5月9日（close-session 中断メモ）

**Observe**：今回 checker/guardian の bundle rule は完了したが、scene boundary の deterministic 昇格は未着手のまま残っている。  
**Think**：次は `test/test_cjg_framework_rule_guards.py` と `test/test_cjg_scene_directory_structure.py` のどの assertion を checker registry へ移せるか対応表を作るのが先。  
**Act**：再開時の最初の 1 手を `rg -n "scene|pyxel|presenter|view_model|model" test/test_cjg_framework_rule_guards.py test/test_cjg_scene_directory_structure.py tools/check_architecture_rules.py -S` に固定した。

---

## 5) Result（成果物）


---

## 6) Discussion（反省）



---

### 反省とルール化

- 次にやること：既存 scene guard のどれを checker registry に寄せるか対応表を作る
