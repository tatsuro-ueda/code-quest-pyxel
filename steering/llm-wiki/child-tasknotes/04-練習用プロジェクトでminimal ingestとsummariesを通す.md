# 04 練習用プロジェクトで minimal ingest と summaries を通す

- 推奨タイトル:
  - `YYYY年M月D日 練習用プロジェクトで minimal ingest と summaries を通す`
- 目的:
  - raw source から summary 生成を通す
- 入力:
  - `raw/knowledge`
  - `raw/tasknotes`
- 完了条件:
  - latest docs と最初の tasknotes から summaries が生成される
  - summary が raw 名を mirror している
- 最初の一手:
  - latest docs 1件、tasknote 1件で ingest の形を確認する
- メモ:
  - TL;DR が崩れる docs はここで早めに見つける
- 委任メモ:
  - 🟡 ingest 主体と summary 粒度が決まれば任せやすい
- 先に決めること:
  - 手動 / スクリプト / CLI 一括のどれで回すか

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 判断ゲート 1: ingest 主体

親note には `raw → summaries` の工程図だけがあり、**実行主体が書かれていない**：

| 選択肢 | 説明 | 利点 | 欠点 |
|---|---|---|---|
| A: Claude Code 手動 | 毎回インタラクティブに生成 | 柔軟、品質高 | 再現性低、コスト高 |
| B: Python スクリプト | `gen_wiki.py` でバッチ生成 | 再現性高、SSoT 整合 | 初期工数大、品質は LLM 任せ |
| C: Codex CLI 一括 | `codex` で一気に処理 | 速い | 出力ばらつき |

→ SSoT ポリシーと整合させるなら **B 寄り**。03 の判断ゲート 2（raw 二重化方針）で C を選んだ場合は B 一択になる。

### 判断ゲート 2: 粒度

大型 docs の summary 粒度：

| ファイル | サイズ | 推奨粒度（暫定） |
|---|---|---|
| `stakeholder_voices.yml` | 107KB | YAML key 単位（stakeholder ごと）|
| `customer-journeys.md` | 95KB | journey 単位（章分割）|
| `architecture_rules.yml` | 63KB | principles 配列の各要素単位 |
| `product-requirements-guardrails.md` | 56KB | g1〜g15 工程単位（章分割） |
| `product-requirements-platform.md` | 39KB | 章単位 |
| `framework-rule.md` | 35KB | 章単位 |
| 他（< 20KB） | - | 1ファイル = 1summary |

**粒度判断は委任しにくい**（書いてみないと評価できない）。
spot check: latest docs 1件で粒度を試し、**ユーザーと擦り合わせてから**全件適用。

### 判断ゲート 3: YAML / Markdown 混在

03 で決めた命名規約に従う。summary 形式：

- **YAML raw → summary**: YAML key リスト + 各 key の TL;DR + 重要 field 抜粋
- **Markdown raw → summary**: TL;DR + 章節 outline + 重要キーワード

summary はすべて Markdown で統一する。

### summary テンプレート（暫定）

```markdown
---
source: <raw からの相対パス>
source_type: knowledge | tasknote
last_ingested: 2026-MM-DD
size_class: small | medium | large
---

# {{ source title }}

## TL;DR

（1段落、3〜5文）

## 主要トピック

- ...

## キーワード

- ...

## 注意点

- （含意される暗黙ルール、関連 docs への言及、矛盾点など）
```

### 委任時の暴走パターン

- 全 docs を一気に summary 化 → 粒度がバラバラで使えない
  - 防止策: **1件 → 2件 → 全件** の段階適用
- summary に raw の生引用を大量に貼る → summary の目的を失う
  - 防止策: TL;DR と outline 重視のテンプレを先に与える
- 大型 YAML を 1summary にまとめる → 内容が消える
  - 防止策: 粒度表をテンプレと一緒に渡す

### 完了条件（拡張）

- ingest 主体が確定している
- 1件 spot check の結果がユーザーに承認されている
- summary テンプレが確定している
- 全件適用後、`summaries/knowledge/` と `summaries/tasknotes/` が raw 名と mirror している
