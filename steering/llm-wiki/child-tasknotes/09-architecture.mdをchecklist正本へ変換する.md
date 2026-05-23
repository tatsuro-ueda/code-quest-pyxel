# 09 architecture.md を checklist 正本へ変換する

- 推奨タイトル:
  - `YYYY年M月D日 architecture.md を checklist 正本へ変換する`
- 目的:
  - architecture の方針を開発前に使える checklist に落とす
- 入力:
  - `architecture.md`
  - 関連する tasknotes
- 完了条件:
  - `architecture-checklist.md` 相当ができている
  - 項目ごとに確認できる形になっている
- 最初の一手:
  - architecture の章立てを見て、確認項目に分解する
- メモ:
  - 「正本に照らして fail/pass を判定できる形」を優先する
- 委任メモ:
  - 🟡 代替正本を決めれば任せやすい
- 先に決めること:
  - architecture source を 1系統か 2系統か

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 入力欠落

下書きの入力 `architecture.md` は **存在しない**。代替候補：

| 候補 | サイズ / 状態 | 適性 |
|---|---|---|
| `docs/architecture_rules.yml` | 63KB / `status: draft` 正本候補 | ◎ principles + must / must_not 構造で checklist に直翻訳できる |
| `docs/framework-rule.md` | 35KB / 命名・運用ルール | ○ 補完情報、特に運用面 |
| `docs/repository-structure.md` | 26KB / リプレース予定 | △ 古い、参照のみ |

### 統合判断（ユーザーゲート）

3 つの選択肢：

- **A) 単独**: `architecture_rules.yml` から直翻訳のみ
  - 利点: 最短、構造化済みで翻訳が機械的
  - 欠点: `framework-rule.md` の運用ルールが落ちる
- **B) 2系統**: `architecture-checklist.md` と `framework-checklist.md` に分離
  - 利点: 責務がクリア
  - 欠点: 2ファイルを使い分ける運用が増える
- **C) 統合**: 1ファイルに統合
  - 利点: 1箇所で済む
  - 欠点: ファイルが大きくなる、改訂が大変

→ 着手前にユーザー判断。**B 推奨**（responsibility が分かれている方が運用しやすい）。

### 翻訳方針（architecture_rules.yml → checklist）

YAML 構造の翻訳ルール：

```yaml
facts:
  principles:
    - label_ja: Code Maker を子どもの正式編集面として守る
      id: code_maker_primary_editor
      summary: Pyxel Code Maker は子どもの正式な編集面である。
      must:
        - tilemap / sprite / sound / .pyxres の編集面では Code Maker を最初の正として扱わなければならない
      must_not:
        - 内部都合で Code Maker を不要化したり脇役化したりしてはならない
```

→ checklist の項目：

```markdown
### Code Maker を子どもの正式編集面として守る（id: code_maker_primary_editor）

**前提**: Pyxel Code Maker は子どもの正式な編集面である。

**必須項目**（must）:
- [ ] tilemap / sprite / sound / .pyxres の編集面では Code Maker を最初の正として扱っている

**禁止項目**（must_not）:
- [ ] 内部都合で Code Maker を不要化していない
- [ ] 内部都合で Code Maker を脇役化していない
```

### `framework-rule.md` の扱い（B を採る場合）

- 章立てから checklist 項目を抽出
- 命名規約・運用ルールが中心
- 「正本に照らして fail/pass を判定できる形」を維持

### 委任時の暴走パターン

- `architecture_rules.yml` の `meta.status: draft` を無視して fully active 扱い
  - 防止策: status を checklist 冒頭に明記
- `must_not` を `must` と同じ章に混ぜる → fail 判定が曖昧化
  - 防止策: 必須 / 禁止 を分離してテンプレ化
- 自分で項目を**追加**してしまう（YAML に無いものを足す）
  - 防止策: 「YAML の facts 配列の要素を漏れなく訳す、追加しない」を tasknote 冒頭に明記

### 完了条件（拡張）

- どの代替入力を使うか確定している
- A / B / C のどれを取るか確定している
- `architecture_rules.yml` の全 principles が checklist 項目に対応している
- `meta.status: draft` を checklist 冒頭で告知している
- fail/pass を判定できる形になっている
