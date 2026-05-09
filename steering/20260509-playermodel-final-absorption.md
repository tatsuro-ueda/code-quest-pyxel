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
  - player-model
---

# 2026年5月9日 PlayerModel 最終吸収（item_use / player_state）

> 状態：③ Design（起票済み / 未着手）
> 次のゲート：（ユーザー）この note を着手対象にしてよいか

---

## 1) Journey（どこへ行くか）

- **深層的目的**：player の正本を一つにする
- **やらないこと**：save 互換を壊したまま進めること

**Before（現状）**：
- 💦 `PlayerModel` が正本になりつつも、`item_use.py` と `player_state.py` が legacy helper として残っている
- 💦 どこまで自動で見張れるかが作業前に固定されていない

**After（達成状態）**：
- ❤️ player のルールと変換が `PlayerModel` に集まり、legacy helper 依存が消える
- ❤️ 移行完了後は再侵入を deterministic check で止められる

---

## 2) Gherkin（完了条件）

### シナリオ1：player の正本が `PlayerModel` に一本化される

🧱 Given：戦闘・回復・save/load が player 情報を使っている  
🎬 When：`item_use.py` と `player_state.py` の責務を `PlayerModel` へ寄せる  
✅ Then：scene / service は free function や legacy helper ではなく `PlayerModel` 経由で player を扱う

### シナリオ2：既存の save 互換が落ちない

🧱 Given：旧 save key や snapshot 互換を守る必要がある  
🎬 When：吸収後に save/load 系 test を回す  
✅ Then：既存 save 形式を読めるまま進められる

### シナリオ3：移行後の再侵入を自動で止める

🧱 Given：一度 legacy helper を消しても将来また戻る危険がある  
🎬 When：pytest / checker に再侵入防止を追加する  
✅ Then：`item_use.py` や `player_state.py` 前提の新規 code が入った時点で fail する

---

## 3) Design（どうやるか）

- 対象ファイルは `docs/architecture_rules.yml`, `docs/repository-structure.md`, `src/shared/state/player_model.py`, `src/shared/services/item_use.py`, `src/shared/services/player_state.py`, 関連 test 群
- save 互換を保つため、先に振る舞い test を固定してから helper を `PlayerModel` へ寄せる
- `item_use.py` / `player_state.py` は一気に削除前提ではなく、最終的に「薄い互換層」か「削除」のどちらに倒すかを test で決める

### 1-2-3 の組み込み方

1. **rule 先行**  
   `architecture_rules.yml` と `repository-structure.md` に「player の正本は `PlayerModel`」「legacy helper は撤去対象」「どこまで自動化するか」を先に書く
2. **deterministic check へ昇格**  
   移行後は `player_state.py` / `item_use.py` 依存の再侵入を pytest / checker で機械的に止める
3. **guardian は安全な正規化だけ**  
   guardian には YAML 上の status / scope / summary 整形だけを任せ、`PlayerModel` へのコード移動は人がやる

---

## 4) Tasklist

- [ ] rule 先行：`docs/architecture_rules.yml` と `docs/repository-structure.md` に target state と自動化範囲を書く
- [ ] red：`PlayerModel` 経由に寄せたい振る舞いを failing test で固定する
- [ ] green：`item_use.py` と `player_state.py` の責務を `PlayerModel` へ吸収する
- [ ] deterministic 昇格：再侵入防止の pytest / checker を追加する
- [ ] guardian 境界確認：autofix は YAML 正規化のみと明記する

### 作業記録

#### 2026年5月9日（起票）

**Observe**：`PlayerModel` は正本だが、legacy helper がまだ残っている  
**Think**：この作業は code 移動と save 互換が絡むので、guardian 先行より task note 先行が安全  
**Act**：`1-2-3` の flow を Design に組み込み、実行手順を Tasklist に落とした

#### 2026年5月9日（close-session 中断メモ）

**Observe**：`item_use.py` / `player_state.py` の吸収は未着手で、save 互換を守る failing test もまだ増やしていない。  
**Think**：次は実装より先に `PlayerModel` に寄せる振る舞い test を列挙して、互換の境界を固定する必要がある。  
**Act**：再開時の最初の 1 手を `rg -n "item_use|player_state|PlayerModel" test src/shared -S` で既存 test と呼び出し点を集めることにした。

---

## 5) Result（成果物）


---

## 6) Discussion（反省）



---

### 反省とルール化

- 次にやること：player 振る舞いの failing test を先に列挙する
