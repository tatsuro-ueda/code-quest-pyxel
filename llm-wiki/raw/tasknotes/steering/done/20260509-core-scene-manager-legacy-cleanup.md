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
  - scene-manager
  - archived
---

# 2026年5月9日 core scene_manager legacy 整理

> 状態：⑥ Discussion（実装完了 / 検証済み）

---

## 1) Journey（どこへ行くか）

- **深層的目的**：scene 管理の考え方を一つにする
- **やらないこと**：test を無理やり壊して進めること

**Before（現状）**：
- 💦 `src/core/scene_manager.py` が test 互換用に残り、`shared/services/scene_manager.py` と二重に見えていた
- 💦 bundle でも旧 manager が混ざっていた

**After（達成状態）**：
- ❤️ scene 切替メタは `shared/services/scene_manager.py` に一本化された
- ❤️ `src/core/scene_manager.py` は削除され、再侵入 guard が入った

---

## 2) Gherkin（完了条件）

### シナリオ1：scene 管理の正が一つに揃う

🧱 Given：scene 切替の正は `shared/services/scene_manager.py` にある  
🎬 When：`src/core/scene_manager.py` 依存を整理する  
✅ Then：test も live code も同じ state holder を前提にする

### シナリオ2：test 互換の置き換えが完了する

🧱 Given：旧 `Scene` protocol / manager を使う test が残っている  
🎬 When：新しい state holder 前提へ test を直す  
✅ Then：`src/core/scene_manager.py` を削除しても test が通る

### シナリオ3：旧 manager の再侵入を止める

🧱 Given：一度削除しても将来また import される危険がある  
🎬 When：pytest / checker の guard を追加する  
✅ Then：`src/core/scene_manager.py` 復活を fail できる

---

## 3) Design（どうやるか）

- `test/test_scene_responsibilities.py` を shared `SceneManager.set()` 前提へ置き換える
- bundle が旧 manager なしでも動くことを確認してから file を削除する
- docs / manifest / guardian section ルールを合わせて掃除する

### 1-2-3 の組み込み方

1. **rule 先行**  
   旧 `core scene_manager` は removed と docs / rules に先に書く
2. **deterministic check へ昇格**  
   `src/core/scene_manager.py` の復活を file existence guard で止める
3. **guardian は安全な正規化だけ**  
   manifest の section 整形だけを guardian に任せる

---

## 4) Tasklist

- [x] rule 先行：旧 `core scene_manager` の target state を docs / rules に書いた
- [x] red：旧 manager を前提にしていた test を新しい正へ倒した
- [x] green：test を shared `SceneManager` 前提へ移し、旧 file を削除した
- [x] deterministic 昇格：`src/core/scene_manager.py` 再侵入 guard を追加した
- [x] guardian 境界確認：YAML / manifest 正規化以外は autofix させないと維持した

### 作業記録

#### 2026年5月9日

**Observe**：旧 manager は production から外れており、test と manifest にだけ残っていた  
**Think**：`src/app.py` と同時に bundle から外せるなら、別名互換より削除の方が明確  
**Act**：scene responsibility test を shared state holder 前提へ更新し、旧 manager を削除した

---

## 5) Result（成果物）

### 実施内容

- `src/core/scene_manager.py` を削除した
- `test/test_scene_responsibilities.py` を shared `SceneManager` 前提へ更新した
- manifest / architecture rules / docs から旧 manager 参照を外した
- `test/test_cjg_framework_rule_guards.py` に旧 manager 復活 guard を追加した

### 検証結果

```text
$ python3 -m pytest test/test_scene_responsibilities.py test/test_architecture_layout.py -q
15 passed

$ python3 tools/build_codemaker.py
OK: dist/code-maker.zip を生成

$ python3 -m pytest test/ -q
695 passed, 2 skipped, 14233 subtests passed
```

---

## 6) Discussion（反省）

- 旧 manager を残すより、test を先に shared state holder へ寄せた方が整理しやすかった
- `src/app.py` 削除と同時にやったことで、manifest / bundle の shadow 問題も一緒に解消できた

---

### 反省とルール化

- 次にやること：旧 protocol 型 helper は live import 数を先に棚卸しする
