---
status: done
priority: normal
scheduled: 2026-05-09T00:00:00.000+09:00
dateCreated: 2026-05-09T00:00:00.000+09:00
dateModified: 2026-05-09T00:00:00.000+09:00
tags:
  - task
  - docs
  - architecture
  - framework-rule
  - archived
---

# 2026年5月9日 docs/architecture.md 廃止と人用詳細の置き換え

> 状態：⑥ Discussion（実装完了 / 検証済み）
> 親ノート：`steering/done/20260505-architecture-md-decision.md`
> 完了条件：`docs/architecture.md` を消しても repo の案内・責務表・static guard が壊れず、人用詳細の正本が別名で成立していること

---

## 1) Journey

- **深層的目的**：文書名の役割を混同しない
- **やらないこと**：人用詳細そのものを捨てない

**Before（現状）**：
- 💦 `docs/architecture.md` が人用詳細の役割を持っているが、`architecture_rules.yml` と名前が衝突していて何が正本候補か迷いやすい
- 💦 AGENTS / README / static guard が `docs/architecture.md` 前提なので、単純削除すると壊れる

**After（達成状態）**：
- ❤️ 人用詳細は `docs/repository-structure.md` として残り、`docs/architecture.md` は live repo から消えている
- ❤️ AGENTS / README / framework-rule / architecture_rules / test が新しい人用詳細を参照し、full test で維持できる

---

## 2) Gherkin

### シナリオ1：人用詳細の置き場が残る

🧱 Given：AI や開発者が repo の責務表と build runbook を読みたい  
🎬 When：`AGENTS.md` や `README.md` から詳細文書を辿る  
✅ Then：`docs/repository-structure.md` に到達し、`docs/architecture.md` がなくても迷わない

### シナリオ2：単純削除で test が壊れない

🧱 Given：`test/test_cjg_framework_rule_guards.py` が人用詳細文書の存在を guard している  
🎬 When：`python -m pytest test/ -q` を回す  
✅ Then：guard は `docs/repository-structure.md` を正として通り、`docs/architecture.md` 不在で落ちない

### シナリオ3：live 文書に古い導線が残らない

🧱 Given：AI と人は live な docs / tests / AGENTS / README を起点に読む  
🎬 When：repo 内の live 文書を確認する  
✅ Then：`docs/architecture.md` 参照は historical な `steering/done/` 以外に残らない

---

## 3) Design

- 人用詳細の役割自体は維持し、ファイル名だけ `docs/repository-structure.md` へ戻す
- TDD として、まず static guard を「新しい正が必要 / 古い正は消える」形へ更新して失敗を確認する
- その後に文書 rename と live 参照の置換を行い、`docs/architecture_rules.yml` の replacement target も合わせる
- historical な `steering/done/` は当時の判断記録として残し、live repo だけを新状態へ揃える

---

## 4) Tasklist

- [x] （CC）`/superpowers:writing-plans` 相当で実装順を固める
- [x] （CC）guard を先に更新し、red を確認する
- [x] （CC）文書 rename と live 参照置換を行う
- [x] （CC）full test と検索で `docs/architecture.md` の live 参照が消えたことを確認する

### 作業記録

#### 2026年5月9日

**Observe**：`docs/architecture.md` は AGENTS / README / framework-rule / tests / architecture_rules から live 参照されていた  
**Think**：単純削除は unsafe で、最小変更は人用詳細を `docs/repository-structure.md` へ戻し、導線と guard を張り替えること  
**Act**：削除条件と移設方針を本 note に固定した

#### 2026年5月9日（guard を red にした）

**Observe**：`docs/repository-structure.md` の存在と live 導線の張り替えを test で定義すると、期待どおり 2 件 fail した  
**Think**：rename 前に red を見たので、今回の変更が本当に新しい guard を通すためのものだと確認できた  
**Act**：`test/test_cjg_framework_rule_guards.py` に `repository-structure.md` 存在 check と live navigation check を追加した

#### 2026年5月9日（rename / 参照置換 / 検証）

**Observe**：live 参照は AGENTS / README / framework-rule / architecture_rules / PRD / test に集中していた  
**Think**：historical な `steering/done/` まで書き換えると当時の判断記録が壊れるため、live repo のみ揃えるのが妥当  
**Act**：`docs/architecture.md` を `docs/repository-structure.md` へ戻し、関連参照を更新。`python3 -m pytest test/ -q`、`python3 tools/check_architecture_rules.py`、`python3 tools/architecture_guardian.py` を通した

---

## 5) Result

### 実施内容

- 人用詳細の正を `docs/architecture.md` から `docs/repository-structure.md` へ戻した
- `AGENTS.md` / `README.md` / `docs/framework-rule.md` の導線を新しい人用詳細へ更新した
- `docs/architecture_rules.yml` の replacement target と scope path を新しい文書名へ更新した
- `docs/product-requirements-guardrails.md` と `test/test_cjg_scene_directory_structure.py` の live 参照を更新した
- `test/test_cjg_framework_rule_guards.py` を更新し、`repository-structure.md` の存在と live 文書の導線を guard するようにした

### 検証結果

```text
$ python3 -m pytest test/test_cjg_framework_rule_guards.py -q
23 passed, 20 subtests passed

$ python3 -m pytest test/test_architecture_guardian.py test/test_architecture_rules_checker.py test/test_cjg_scene_directory_structure.py -q
19 passed, 108 subtests passed

$ python3 tools/check_architecture_rules.py
run_ok: true, has_warnings: false

$ python3 tools/architecture_guardian.py
status: OK, cycles: 1

$ python3 -m pytest test/ -q
691 passed, 2 skipped, 14233 subtests passed
```

### 変更ファイル

- `AGENTS.md`
- `README.md`
- `docs/repository-structure.md`
- `docs/framework-rule.md`
- `docs/architecture_rules.yml`
- `docs/product-requirements-guardrails.md`
- `test/test_cjg_framework_rule_guards.py`
- `test/test_cjg_scene_directory_structure.py`


---

## 6) Discussion

- historical な `steering/done/` は当時 `docs/architecture.md` を正としていた記録なので、そのまま残す
- live repo で `docs/architecture.md` が残ると `architecture_rules.yml` と名前が競合しやすいため、役割どおり `repository-structure.md` に戻したのは妥当
- 今後この人用詳細をさらに分割したくなったら、「build runbook」と「責務表」を別文書へ切り出す余地はあるが、今回は削除安全性を優先して split はしなかった

---

### 反省とルール化

- 次にやること：guard を red にしてから rename を進める
