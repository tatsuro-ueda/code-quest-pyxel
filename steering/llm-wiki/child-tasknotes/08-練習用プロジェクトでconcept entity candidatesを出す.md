# 08 練習用プロジェクトで concept entity candidates を出す

- 推奨タイトル:
  - `YYYY年M月D日 練習用プロジェクトで concept entity candidates を出す`
- 目的:
  - final note ではなく候補一覧まで作る
- 入力:
  - summaries
- 完了条件:
  - `candidates/concepts.md` と `candidates/entities.md` がある
  - 何を昇格候補にするか相談できる状態になっている
- 最初の一手:
  - docs 名や tasknote 題名から繰り返し現れる語を確認する
- メモ:
  - ここでは final の concept/entity をまだ作らない
- 委任メモ:
  - 🟢 候補一覧の生成までは委任しやすい
- 先に決めること:
  - final 昇格はこの task で扱わない

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 抽出ヒント

このプロジェクトに頻出する語の暫定リスト：

**concept 候補**（抽象概念・方針）:
- `SSoT`（Single Source of Truth）
- `Codegen`
- `Guardrail`
- `Customer Job`
- `Customer Journey`
- `Journey Redesign`
- `好循環`（メモリ: `project_core_premise`）
- `AIコーディング前提`
- `子ども向けひらがな表記`（メモリ: `project_ui_policy`）
- `単一配信方針`（メモリ: `project_single_distribution_policy`）
- `生成物 vs 正本`（SSoT 一方通行）

**entity 候補**（具体・固有）:
- `Pyxel`, `Pyxres`, `Code Maker`
- `Battle`, `Map`, `Narrative`
- `Block Quest`, `Code Quest`
- product-requirements-* 群（av / battle / guardrails / map / narrative / platform）
- closed tasknote の prefix 群（g, guardrails, j, cj）

### 機械的抽出ルール（委任可）

1. `wiki/summaries/` 配下の Markdown を全件 grep
2. 大文字始まり連語 + カタカナ語 + `*.yml` / `*.md` ファイル名で頻度集計
3. 頻度 >= 5 のものを candidates に
4. ストップワード除外: `Code`（一般語） / `Tasknote` など

### 出力テンプレ

```markdown
# concepts candidates

| 用語 | 頻度 | 出現 summary | 関連 area | 昇格優先度 |
|---|---|---|---|---|
| SSoT | 42 | guardrails-1, ssot-codegen, ... | guardrails | 高 |
| ... |
```

### 委任時の暴走パターン

- final な `concepts/<term>.md` を勝手に作る → 親note 原則違反
  - 防止策: 「candidates まで、final は作らない」を tasknote 冒頭に明記
- 一般語まで拾う（`code`, `file`, `change` 等）
  - 防止策: ストップワードを先に渡す

### 完了条件（拡張）

- `candidates/concepts.md` `candidates/entities.md` が出ている
- 各候補に**頻度** + **出現 summary** + **関連 area** が紐付いている
- final 昇格判断のための材料が揃っている（昇格自体はやらない）
