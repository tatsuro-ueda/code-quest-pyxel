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
  - scene-manager
---

# 2026年5月9日 core scene_manager legacy 整理

> 状態：③ Design（起票済み / 未着手）
> 次のゲート：（ユーザー）この note を着手対象にしてよいか

---

## 1) Journey（どこへ行くか）

- **深層的目的**：scene 管理の考え方を一つにする
- **やらないこと**：test を無理やり壊して進めること

**Before（現状）**：
- 💦 `src/core/scene_manager.py` は test 互換のためだけに残っていて、実運用の `shared/services/scene_manager.py` と二重に見える
- 💦 どこまで置き換えたら削除できるかが note と guard に固定されていない

**After（達成状態）**：
- ❤️ live code と tests が同じ `SceneManager` の考え方を前提にできる
- ❤️ `src/core/scene_manager.py` を消したあとも再侵入を deterministic check で止められる

---

## 2) Gherkin（完了条件）

### シナリオ1：scene 管理の正が一つに揃う

🧱 Given：scene 切替の正は `shared/services/scene_manager.py` にある  
🎬 When：`src/core/scene_manager.py` 依存を整理する  
✅ Then：test も live code も同じ方針で scene 切替を扱う

### シナリオ2：test 互換の置き換えが完了する

🧱 Given：旧 `Scene` protocol / manager を使う test が残っている  
🎬 When：新しい state holder 前提へ test を直す  
✅ Then：`src/core/scene_manager.py` を削除しても test が通る

### シナリオ3：旧 manager の再侵入を止める

🧱 Given：一度削除しても将来また import される危険がある  
🎬 When：pytest / checker の guard を追加する  
✅ Then：`src.core.scene_manager` 参照が再び入ったら fail する

---

## 3) Design（どうやるか）

- 対象ファイルは `docs/architecture_rules.yml`, `docs/repository-structure.md`, `src/core/scene_manager.py`, `src/shared/services/scene_manager.py`, 関連 test 群
- 旧 manager を使う test を先に列挙し、新 state holder へ移せるものから順に直す
- protocol が本当に必要なら test helper へ局所化し、production code からは消す

### 1-2-3 の組み込み方

1. **rule 先行**  
   `architecture_rules.yml` と `repository-structure.md` に「旧 core scene_manager は撤去対象」と先に書く
2. **deterministic check へ昇格**  
   移行後は `src.core.scene_manager` import を grep / pytest / checker で止める
3. **guardian は安全な正規化だけ**  
   guardian には YAML 上の legacy status 整理だけを任せ、test の置換や code 削除は人がやる

---

## 4) Tasklist

- [ ] rule 先行：旧 `core scene_manager` の target state を docs / rules に書く
- [ ] red：旧 manager を使っている test / import を固定する
- [ ] green：test を新 `SceneManager` 前提へ移し、旧 file を削除または空化する
- [ ] deterministic 昇格：`src.core.scene_manager` 再侵入 guard を追加する
- [ ] guardian 境界確認：YAML 正規化以外は autofix させない

### 作業記録

#### 2026年5月9日（起票）

**Observe**：旧 `core scene_manager` は test 互換用としてだけ残っている  
**Think**：この task は test 置換が主で、guardian が自動で code move する種類ではない  
**Act**：`1-2-3` flow を note に組み込み、分解した

#### 2026年5月9日（close-session 中断メモ）

**Observe**：この note は Design までで止まっており、旧 manager の import 残数をまだ取っていない。  
**Think**：最初に import 棚卸しをしないと、削除 task と test helper 抽出 task が混ざる。  
**Act**：再開時の最初の 1 手を `rg -n "src\\.core\\.scene_manager|from src\\.core\\.scene_manager import|import src\\.core\\.scene_manager" src test tools docs -S` に固定した。

---

## 5) Result（成果物）


---

## 6) Discussion（反省）



---

### 反省とルール化

- 次にやること：`src.core.scene_manager` import の現残数を先に棚卸しする
