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

# 2026年5月9日 shared boundary の deterministic 昇格

> 状態：③ Design（起票済み / 未着手）
> 次のゲート：（ユーザー）この note を着手対象にしてよいか

---

## 1) Journey（どこへ行くか）

- **深層的目的**：shared 配置のルールを機械で守る
- **やらないこと**：file move を guardian にやらせること

**Before（現状）**：
- 💦 `shared_service_vs_state_boundary` は candidate で、`shared/services` と `shared/state` の境界を checker が完全自動では見られない
- 💦 `PlayerModel` / state holder / service の置き場を将来また混ぜる危険がある

**After（達成状態）**：
- ❤️ `shared/services` と `shared/state` の配置違反を checker が deterministic に warning できる
- ❤️ guardian は YAML 整形だけを行い、責務の物理移動は人判断のままにする

---

## 2) Gherkin（完了条件）

### シナリオ1：shared 配置違反を checker が機械で検出できる

🧱 Given：`shared/services` と `shared/state` の責務分担ルールがある  
🎬 When：checker を実行する  
✅ Then：misplace された state holder / cross-scene model を deterministic に warning できる

### シナリオ2：M4-4 の移行と衝突しない

🧱 Given：`PlayerModel` 吸収や legacy helper 撤去が並行する  
🎬 When：shared boundary rule を実装する  
✅ Then：移行途中でも target state が docs と checker で一致する

### シナリオ3：guardian が危険な移動をしない

🧱 Given：shared 配置違反の修正は file rename / import 更新を伴う  
🎬 When：guardian を実行する  
✅ Then：自動修復はせず、人の判断が必要な warning として止まる

---

## 3) Design（どうやるか）

- 対象ファイルは `docs/architecture_rules.yml`, `tools/check_architecture_rules.py`, `test/test_architecture_rules_checker.py`, `test/test_cjg_framework_rule_guards.py`, `docs/repository-structure.md`
- `shared/services` と `shared/state` の命名・配置・pyxel 利用禁止を checker rule としてまとめる
- `PlayerModel` 吸収 task と矛盾しないよう、移行中の例外は明示しながら最終形を固定する

### 1-2-3 の組み込み方

1. **rule 先行**  
   `architecture_rules.yml` と `repository-structure.md` に shared の target state を先に固定する
2. **deterministic check へ昇格**  
   static guard / grep 相当を checker registry に寄せ、coverage を `implemented` に上げる
3. **guardian は安全な正規化だけ**  
   guardian は coverage / YAML の整形だけを担当し、shared 配置の code 修正は人手に残す

---

## 4) Tasklist

- [ ] rule 先行：shared 境界の target state と例外を YAML / docs に書く
- [ ] red：checker 側で未実装を示す failing test を追加する
- [ ] green：shared directory role checks を checker registry に実装する
- [ ] deterministic 昇格：coverage を `implemented` に更新し JSON 出力を固定する
- [ ] guardian 境界確認：autofix は増やさず `not_recommended` を維持する

### 作業記録

#### 2026年5月9日（起票）

**Observe**：shared boundary はまだ candidate で、人手判断が前提になっている  
**Think**：ここは docs と checker の結線 task として独立させると進めやすい  
**Act**：`1-2-3` flow を shared boundary task に落とし込んだ

#### 2026年5月9日（close-session 中断メモ）

**Observe**：shared boundary 昇格は未着手で、`shared/services` と `shared/state` の違反パターン一覧もまだ作っていない。  
**Think**：次は配置違反の taxonomy を作り、checker が静的に止められるものだけを切り出すべき。  
**Act**：再開時の最初の 1 手を `rg -n "shared/services|shared/state|PlayerModel|GameState|SceneManager|DebugService" docs/repository-structure.md docs/architecture_rules.yml test/test_cjg_framework_rule_guards.py src/shared -S` に固定した。

---

## 5) Result（成果物）


---

## 6) Discussion（反省）



---

### 反省とルール化

- 次にやること：`shared/services` と `shared/state` の境界違反パターン一覧を先に作る
