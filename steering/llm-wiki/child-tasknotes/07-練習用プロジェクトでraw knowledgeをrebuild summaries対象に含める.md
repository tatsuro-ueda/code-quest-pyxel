# 07 練習用プロジェクトで raw knowledge を rebuild summaries 対象に含める

- 推奨タイトル:
  - `YYYY年M月D日 練習用プロジェクトで raw knowledge を rebuild summaries 対象に含める`
- 目的:
  - docs 系 source も tasknotes と同じ rebuild に乗せる
- 入力:
  - `raw/knowledge`
  - current rebuild 実装
- 完了条件:
  - knowledge docs の summary が `summaries/knowledge` に出る
  - query と current-state から辿れる
- 最初の一手:
  - latest docs 1件を summary 対象にして path mirror を確認する
- メモ:
  - 練習段階でも `正本 + 最近の動き` を一緒に見られる形を目指す
- 委任メモ:
  - 🟢 04 のテンプレが決まれば任せやすい
- 先に決めること:
  - knowledge summary に追加 field を持たせるか

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 依存

- **04** で決まる方式（ingest 主体 + summary テンプレ）に依存
- **03** で決まる raw 二重化方針に依存
  - 二重化方針 C（`gen_wiki.py`）を選んだ場合、knowledge も同スクリプトに乗せる

### 着手前の確認

- 04 の spot check（docs 1件 + tasknote 1件）が**両方とも**通っていること
- 04 で knowledge と tasknote のテンプレが分離されているか、共通か確認
  - knowledge 用テンプレに「正本かどうか」「リプレース予定の有無」フィールドを追加するか検討

### knowledge summary の追加フィールド

```yaml
---
source: docs/architecture_rules.yml
source_type: knowledge
status: draft | active | deprecated   # ← 重要
replacement_of:                        # ← architecture_rules.yml の場合
  - docs/repository-structure.md
last_ingested: 2026-MM-DD
size_class: large
---
```

→ `status: deprecated` の summary は query から低優先で扱う、などのルールを 06 と整合させる。

### 委任時の暴走パターン

- 04 を待たずに先行着手 → テンプレが分裂する
- knowledge の summary に「正本性」のメタデータを入れない → 06 の query が deprecated docs を引用してしまう

### 完了条件（拡張）

- knowledge summary に正本性メタが入っている
- `summaries/knowledge/<path>-summary.md` が `raw/knowledge/<path>` と mirror している
- 06 の spot check 質問が knowledge summary を引用して答えられる
