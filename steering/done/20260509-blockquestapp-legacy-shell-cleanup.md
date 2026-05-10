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
  - runtime
  - archived
---

# 2026年5月9日 BlockQuestApp legacy shell 整理

> 状態：⑥ Discussion（実装完了 / 検証済み）

---

## 1) Journey（どこへ行くか）

- **深層的目的**：実行入口を一つにする
- **やらないこと**：Code Maker bundler 互換を無視して壊すこと

**Before（現状）**：
- 💦 `src/runtime/app.py::Game` が本体なのに `src/app.py::BlockQuestApp` が残っていた
- 💦 `BlockQuestApp` が bundle に本当に必要か未確定だった

**After（達成状態）**：
- ❤️ runtime root は `src/runtime/app.py::Game` のみと言える
- ❤️ `src/app.py` は削除され、manifest / docs / guard が新状態を維持する

---

## 2) Gherkin（完了条件）

### シナリオ1：実行入口の正が一つに揃う

🧱 Given：開発者や AI が runtime の入口を探す  
🎬 When：`src/app.py` の legacy shell を整理する  
✅ Then：本体は `src/runtime/app.py::Game` だと迷わず追える

### シナリオ2：互換経路を壊さずに整理できる

🧱 Given：Code Maker bundler 互換を守る必要がある  
🎬 When：`BlockQuestApp` を消して bundle を再確認する  
✅ Then：bundle 起動は維持され、不要な実体二重化だけが消える

### シナリオ3：再侵入を機械で止める

🧱 Given：将来また第二の app root が生えうる  
🎬 When：static guard や checker を追加する  
✅ Then：`src/app.py` の復活を pytest で止められる

---

## 3) Design（どうやるか）

- 先に test を「`src/app.py` が無い」前提へ倒して red を取る
- Code Maker bundle を模擬実行し、`src/app.py` なしでも `Game()` が起動することを確認する
- manifest / docs / architecture rules / guard をまとめて更新する

### 1-2-3 の組み込み方

1. **rule 先行**  
   runtime root は `Game` のみ、`src/app.py` は removed と docs に先に書く
2. **deterministic check へ昇格**  
   `src/app.py` の存在そのものを static guard で止める
3. **guardian は安全な正規化だけ**  
   manifest section 整形だけ guardian に任せ、削除判断は人が行う

---

## 4) Tasklist

- [x] rule 先行：`BlockQuestApp` の target state を docs / rules に書いた
- [x] red：`src/app.py` 不在を要求する test に倒した
- [x] green：`src/app.py` を削除し、manifest / docs / bundle を整理した
- [x] deterministic 昇格：`src/app.py` 復活 guard を追加した
- [x] guardian 境界確認：manifest section 整形以外は autofix させないと維持した

### 作業記録

#### 2026年5月9日

**Observe**：`src/app.py` の live 参照は test / docs / manifest に限られていた  
**Think**：bundle 実行まで試して不要だと確認できれば、互換層ではなく削除が最短  
**Act**：manifest から外した仮 bundle で `Game()` 起動を確認した上で、`src/app.py` を削除した

---

## 5) Result（成果物）

### 実施内容

- `src/app.py` を削除した
- `tools/codemaker_manifest.txt` と `docs/architecture_rules.yml` から `src/app.py` を外した
- `docs/repository-structure.md` / `docs/framework-rule.md` / `AGENTS.md` の runtime 説明を更新した
- `test/test_architecture_layout.py` と `test/test_cjg_framework_rule_guards.py` を `src/app.py` 不在 guard へ更新した

### 検証結果

```text
$ python3 tools/build_codemaker.py
OK: dist/code-maker.zip を生成

$ python3 -m pytest test/test_architecture_layout.py test/test_codemaker_bundle_smoke.py -q
18 passed

$ python3 -m pytest test/ -q
695 passed, 2 skipped, 14233 subtests passed
```

---

## 6) Discussion（反省）

- `BlockQuestApp` は「互換で残す」より「不要を実 bundle で確認して消す」方が整理が早かった
- この task は `src/core/scene_manager.py` 整理と同時実行にした方が安全だった

---

### 反省とルール化

- 次にやること：legacy shell を残す理由は bundle 実行で先に検証する
