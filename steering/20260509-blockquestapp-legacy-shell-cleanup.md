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
  - runtime
---

# 2026年5月9日 BlockQuestApp legacy shell 整理

> 状態：③ Design（起票済み / 未着手）
> 次のゲート：（ユーザー）この note を着手対象にしてよいか

---

## 1) Journey（どこへ行くか）

- **深層的目的**：実行入口を一つにする
- **やらないこと**：Code Maker bundler 互換を無視して壊すこと

**Before（現状）**：
- 💦 実際の本体は `src/runtime/app.py::Game` なのに、`src/app.py::BlockQuestApp` が legacy shell として残っていて迷いやすい
- 💦 「完全削除できるのか、薄い互換層として残すのか」が rule と test で固定されていない

**After（達成状態）**：
- ❤️ runtime の本体は `Game` だと code / docs / tests がそろって言える
- ❤️ `BlockQuestApp` を残すなら役割が極小化され、消すなら再侵入を deterministic check で止められる

---

## 2) Gherkin（完了条件）

### シナリオ1：実行入口の正が一つに揃う

🧱 Given：開発者や AI が runtime の入口を探す  
🎬 When：`src/app.py` の legacy shell を整理する  
✅ Then：本体は `src/runtime/app.py::Game` だと迷わず追える

### シナリオ2：互換経路を壊さずに整理できる

🧱 Given：test / Code Maker bundler 互換のために残っている経路がある  
🎬 When：`BlockQuestApp` の削除または縮退を行う  
✅ Then：必要な互換だけ残し、不要な実体二重化はなくなる

### シナリオ3：再侵入を機械で止める

🧱 Given：将来また第二の app root が生えうる  
🎬 When：static guard や checker を追加する  
✅ Then：`BlockQuestApp` 前提の新規 import や runtime 二重化が pytest で止まる

---

## 3) Design（どうやるか）

- 対象ファイルは `docs/architecture_rules.yml`, `docs/repository-structure.md`, `src/app.py`, `src/runtime/main_runtime.py`, `src/runtime/app.py`, bundler / test 関連
- 先に `BlockQuestApp` の現使用箇所を洗い、完全削除か「0 ロジック互換層」かを test 基準で決める
- runtime entry chain rule と矛盾しない形で整理する。`main.py -> main_runtime.py -> Game` は崩さない

### 1-2-3 の組み込み方

1. **rule 先行**  
   `architecture_rules.yml` と `repository-structure.md` に `BlockQuestApp` の target state を先に書く
2. **deterministic check へ昇格**  
   移行後は `BlockQuestApp` 依存や第二入口の再侵入を pytest / checker で止める
3. **guardian は安全な正規化だけ**  
   guardian には entry chain facts や YAML の整形だけを任せ、`src/app.py` の整理そのものは人がやる

---

## 4) Tasklist

- [ ] rule 先行：`BlockQuestApp` の target state を docs / rules に書く
- [ ] red：現使用箇所と必要互換を failing test または import 検索で固定する
- [ ] green：`src/app.py` を削除または 0 ロジック互換層へ縮退させる
- [ ] deterministic 昇格：`Game` 以外を実体 app root に戻せない guard を追加する
- [ ] guardian 境界確認：entry chain 正規化以外は autofix させない

### 作業記録

#### 2026年5月9日（起票）

**Observe**：`BlockQuestApp` は legacy shell として残っているが、実体 root ではない  
**Think**：これは単なる整形ではなく互換判断が必要なので、guardian 先行ではなく note 先行にするべき  
**Act**：`1-2-3` flow を Design と Tasklist に埋め込んだ

#### 2026年5月9日（close-session 中断メモ）

**Observe**：この note 自体は未着手で、checker/guardian 周辺の別タスクを先に完了した。  
**Think**：次は `src/app.py` の実参照を棚卸しし、削除ではなく「0 ロジック互換層」で足りるかを先に決めるべき。  
**Act**：再開時の最初の 1 手を `rg -n "BlockQuestApp|from src\\.app import|import src\\.app" src test tools docs -S` で現参照を固定することにした。

---

## 5) Result（成果物）


---

## 6) Discussion（反省）



---

### 反省とルール化

- 次にやること：`src/app.py` の参照元一覧を取って削除可否を先に確定する
