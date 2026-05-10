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
  - player-model
  - archived
---

# 2026年5月9日 PlayerModel 最終吸収（item_use / player_state）

> 状態：⑥ Discussion（実装完了 / 検証済み）

---

## 1) Journey（どこへ行くか）

- **深層的目的**：player の正本を一つにする
- **やらないこと**：save 互換を壊したまま進めること

**Before（現状）**：
- 💦 `PlayerModel` が正本になりつつも、`item_use.py` と `player_state.py` が production 側にも影を残していた
- 💦 legacy helper 再侵入を止める deterministic guard が不足していた

**After（達成状態）**：
- ❤️ runtime / scenes は `PlayerModel` 経由で player を扱う
- ❤️ `item_use.py` / `player_state.py` は test / bundle 互換 shim に縮退し、再侵入 guard が入った

---

## 2) Gherkin（完了条件）

### シナリオ1：player の正本が `PlayerModel` に一本化される

🧱 Given：戦闘・回復・save/load が player 情報を使っている  
🎬 When：`item_use.py` と `player_state.py` の責務を `PlayerModel` へ寄せる  
✅ Then：runtime / scene は legacy helper ではなく `PlayerModel` 経由で player を扱う

### シナリオ2：既存の save 互換が落ちない

🧱 Given：旧 save key や snapshot 互換を守る必要がある  
🎬 When：吸収後に save/load 系 test を回す  
✅ Then：既存 save 形式を読めるまま進められる

### シナリオ3：移行後の再侵入を自動で止める

🧱 Given：一度 legacy helper を縮退させても将来また戻る危険がある  
🎬 When：pytest / checker に再侵入防止を追加する  
✅ Then：`item_use.py` や `player_state.py` 前提の新規 code が入った時点で fail する

---

## 3) Design（どうやるか）

- `PlayerModel.use_item()` に warp を含む item 使用ルールを集約する
- `src/scenes/menu/presenter.py` と `src/scenes/battle/presenter.py` は `PlayerModel` を直接呼ぶ
- `item_use.py` / `player_state.py` は互換 shim としてのみ残す
- `docs/architecture_rules.yml` / `docs/repository-structure.md` / static guard を新しい正へ更新する

### 1-2-3 の組み込み方

1. **rule 先行**  
   player の正本は `PlayerModel`、legacy helper は互換 shim という target state を docs に先に書く
2. **deterministic check へ昇格**  
   runtime / scenes が `player_state.py` / `item_use.py` を import したら fail する guard を足す
3. **guardian は安全な正規化だけ**  
   guardian には YAML 整形だけを任せ、コード移動は人手で行う

---

## 4) Tasklist

- [x] rule 先行：`docs/architecture_rules.yml` と `docs/repository-structure.md` に target state を書いた
- [x] red：helper 依存を残すと落ちる guard test を追加した
- [x] green：`item_use.py` と `player_state.py` の責務を `PlayerModel` 基準へ寄せた
- [x] deterministic 昇格：再侵入防止の pytest を追加した
- [x] guardian 境界確認：autofix は YAML 正規化のみと確認した

### 作業記録

#### 2026年5月9日

**Observe**：`PlayerModel` はあるが、runtime / scene に legacy helper 依存が残っていた  
**Think**：helper を即削除するより、production 依存を剥がして互換 shim に縮退させる方が安全  
**Act**：`PlayerModel.use_item()` を拡張し、menu / battle presenter と runtime shim の import を切り替えた

---

## 5) Result（成果物）

### 実施内容

- `src/shared/state/player_model.py` に item 使用ルールを寄せた
- `src/scenes/menu/presenter.py` と `src/scenes/battle/presenter.py` の `item_use.py` 直 import を削除した
- `src/runtime/main_runtime.py` の `player_state.py` / `item_use.py` 依存を削除した
- `src/shared/services/item_use.py` と `src/shared/services/player_state.py` を互換 shim として位置づけ直した
- `test/test_cjg_framework_rule_guards.py` に再侵入防止 guard を追加した

### 検証結果

```text
$ python3 -m pytest test/test_player_model.py test/test_cjg_player_model_use_item.py test/test_cjg_menu_item_use_service.py test/test_runtime_shim.py -q
48 passed

$ python3 tools/check_architecture_rules.py
run_ok: true, executed_rules: 7, warning_rules: 0

$ python3 tools/architecture_guardian.py
status: OK

$ python3 -m pytest test/ -q
695 passed, 2 skipped, 14233 subtests passed
```

---

## 6) Discussion（反省）

- `item_use.py` / `player_state.py` はまだ bundle / test 互換のため残しているが、production の正本ではなくなった
- 次に本当に削るべき残件は `player_state.py` の bundle 互換をどこまで減らせるか

---

### 反省とルール化

- 次にやること：legacy helper を残す場合でも production import は先に切る
