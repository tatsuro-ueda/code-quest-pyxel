# 03 練習用プロジェクト向け LLM Wiki skeleton と命名ルールを置く

- 推奨タイトル:
  - `YYYY年M月D日 練習用プロジェクト向け LLM Wiki skeleton と命名ルールを置く`
- 目的:
  - `raw` と `wiki` の境界、命名ルール、最小構造を置く
- 入力:
  - 親note
  - Karpathy gist の原則
- 完了条件:
  - `wiki/raw` と `wiki/wiki` ができている
  - `*-summary.md` と `current-state.md` を優先する命名方針が書かれている
- 最初の一手:
  - `wiki/README.md` を作り、source と generated の境界を書く
- メモ:
  - `architecture.md` のような generated 側の誤解名は避ける
- 委任メモ:
  - 🟢 置き場所と raw 方針が決まれば任せやすい
- 先に決めること:
  - `wiki/` の場所と `raw` の作り方

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 判断ゲート 1: 置き場所

| 候補 | 利点 | 欠点 |
|---|---|---|
| `wiki/`（リポジトリトップ） | 親note 想定に近い、Karpathy 流命名 | トップが膨らむ |
| `steering/llm-wiki/wiki/` | 既存の下書き場所と地続き | steering と wiki の責務が混ざる |
| `docs/wiki/` | docs 系と並列 | docs（正本）と wiki（generated）が意味衝突 |
| `generated/wiki/` | SSoT ポリシーと整合 | Karpathy 流命名とズレる、generated/ 自体まだ無い場合あり |

→ **着手前にユーザー判断**。SSoT ポリシー（`YAML → gen_data.py → generated 一方通行`）との整合を取るなら `generated/wiki/` が最も筋が通る。

### 判断ゲート 2: raw の正本二重化

親note は「raw を正本にする」と言うが、本プロジェクトは `docs/` が既に正本。
選択肢：

- **A) コピー**: `docs/` を `wiki/raw/knowledge/` にコピー
  - 利点: 親note 原則そのまま、独立に管理できる
  - 欠点: 正本が二重化、SSoT 違反、`docs/` 更新時に同期漏れ
- **B) 参照**: `wiki/raw/knowledge/` は `docs/` への参照リストだけ持つ
  - 利点: 二重化なし
  - 欠点: 親note の「raw を正本」原則と齟齬
- **C) gen_wiki.py**: `docs/` から `wiki/raw/` を生成スクリプトで作る
  - 利点: SSoT 流儀と整合、再現性あり
  - 欠点: スクリプト書く工数

### 判断ゲート 3: YAML 素材の扱い

`architecture_rules.yml` `stakeholder_voices.yml` のような構造化 YAML は raw に入れたあと、

- そのまま `.yml` で保存（summary 化で構造が崩れやすい）
- Markdown に変換（意味が落ちる）

の選択がある。**命名規約に「YAML raw は `.yml`、summary は同名の `*-summary.md`」と明文化**。

### 判断ゲート 4: query 規約の明文化

親note の「query は read-only」を**運用ルールとして明文化**する。これが無いと AI が自然に raw を書き換える。

`wiki/README.md` に書くべき条項（例）：

- `wiki/wiki/query/` 配下の作業中、`Edit` / `Write` で `wiki/raw/` を更新しない
- query が「raw が古い」と判断した場合は `wiki/wiki/maintenance.md` に追記して人が後で対応
- `concept` / `entity` の昇格は人と LLM が相談してから

### スケルトン雛形（決定後）

```
{wiki_root}/
├── README.md             # ← 境界・命名・read-only 規約
├── raw/
│   ├── knowledge/        # 正本 docs の snapshot
│   └── tasknotes/        # closed tasknotes の snapshot
├── wiki/
│   ├── summaries/
│   │   ├── knowledge/
│   │   └── tasknotes/
│   ├── indexes/
│   ├── areas/
│   │   └── <area>/current-state.md
│   ├── query/
│   ├── candidates/
│   │   ├── concepts.md
│   │   └── entities.md
│   └── maintenance.md
└── checklists/
    ├── architecture-checklist.md
    └── ux-checklist.md
```

### 完了条件（拡張）

- 置き場所が確定している
- raw の二重化方針が確定している（A / B / C のどれか）
- YAML 素材の命名規約が書かれている
- query の read-only 運用ルールが README に書かれている
- スケルトンディレクトリが置かれている

### 委任時の暴走パターン

- 置き場所を勝手に決める（特に `docs/wiki/` を選びがち）
- query 規約を「原則だけ」書いて運用ルールに落とさない
- 既存の `docs/` を勝手に `wiki/raw/` にコピーしてしまう
