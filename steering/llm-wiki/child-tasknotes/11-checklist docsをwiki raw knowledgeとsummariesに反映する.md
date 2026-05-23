# 11 checklist docs を wiki raw knowledge と summaries に反映する

- 推奨タイトル:
  - `YYYY年M月D日 checklist docs を wiki raw knowledge と summaries に反映する`
- 目的:
  - checklist を query から辿れる状態にする
- 入力:
  - `architecture-checklist.md`
  - `ux checklist`
  - raw knowledge / summaries
- 完了条件:
  - checklist docs が raw knowledge に入っている
  - summaries と query から辿れる
- 最初の一手:
  - checklist docs を snapshot source として raw knowledge に置く
- メモ:
  - 開発支援で使うには「作る」だけでなく「辿れる」が必要
- 委任メモ:
  - 🟢 09 と 10 の成果があれば反映作業は任せやすい
- 先に決めること:
  - raw へコピーするか参照リストにするか

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 依存

- **09**（architecture-checklist の生成）が完了している
- **10**（ux-checklist + 新規 ux-policy.md）が完了している
- **03** の raw 二重化方針に従う

### 反映先の整理

09 で B を選んだ場合（2系統）、checklist は 2 つある：

- `checklists/architecture-checklist.md`
- `checklists/framework-checklist.md`
- `checklists/ux-checklist.md`

raw 二重化方針別の手順：

- **方針 A（コピー）**: checklist を `wiki/raw/knowledge/checklists/` にコピー
- **方針 B（参照）**: `wiki/raw/knowledge/checklists.md` に参照リストを置く
- **方針 C（gen_wiki.py）**: スクリプトに checklist を含める

### summary 生成

04 の summary テンプレを再利用。checklist の場合の追加メタ：

```yaml
---
source: checklists/architecture-checklist.md
source_type: checklist
status: active
origin: architecture_rules.yml   # ← 元の正本
last_synced: 2026-MM-DD
---
```

### query からの辿り方

06 の spot check 質問のうち、checklist を必要とするものを足す：

- `architecture の checklist は何か` → `summaries/checklists/architecture-checklist-summary.md`
- `UX 方針の checklist は何か` → `summaries/checklists/ux-checklist-summary.md`
- `ガードレール開発時に確認すべき項目は` → 上記 + framework

### 委任時の暴走パターン

- 09 / 10 を待たずに着手 → 空 checklist の summary を作ってしまう
- checklist と原典（architecture_rules.yml 等）が**乖離**したまま summary 化
  - 防止策: summary の `origin` フィールドと `last_synced` で乖離検出

### 完了条件（拡張）

- 全 checklist が raw に入っている（方針 A/B/C のいずれか）
- 各 checklist に対応する summary が出ている
- summary の `origin` フィールドが原典を指している
- 06 の query から checklist を辿って引用できる
