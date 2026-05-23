# llm-wiki-how-to

別PJで LLM Wiki 構築を始めるときの shared starter kit。
「dotfiles を更新して tasknote を import したあと、数回の意思決定が必要でも最後の試運転までたどり着ける」ことを目標にしている。

## 3分サマリー

- 誰向け:
  - 別PJで Karpathy 寄りの小さな LLM Wiki を始めたい人
- 何がつらいか:
  - `latest docs` と `Git snapshot` と `closed tasknotes` の入れ方と判断順が毎回重い
- 何が得られるか:
  - 親note 1本と child tasknote 12本で、最小 wiki と checklist と dry-run までの道筋が見える
- どこで止まりやすいか:
  - 途中で数回の意思決定はあるが、その位置と理由を先に読める

## このパッケージで最後まで行く流れ

1. dotfiles を更新して、この package を受け取る
2. 対象PJへ shared note を持ち込み、現在日付の tasknote として切り直す
3. `01` で `latest docs` と `history snapshots` を棚卸しする
4. `03` と `04` で raw / wiki / summaries の最小骨格を通す
5. `09` `10` `11` で checklist を query から辿れるようにする
6. `12` で小さな開発 task 1本を試運転し、足りない導線を別 note に残す

## まず始める1本

- デフォルトは `child-tasknotes/01-練習用プロジェクトの正本docsとGit snapshot候補を棚卸しする.md`
- ただし repo に強い SSoT / codegen 方針があるなら、`01` を始める前に `03` の「置き場所」と「raw の作り方」だけ先に読む
- 迷ったら、次の順で考える
  1. 今の正本 docs は何か
  2. wiki をどこへ置くか
  3. `raw` を `docs/` からどう作るか

## 今決めること

- `latest docs` を何と見なすか
- `wiki/` をどこへ置くか
- `raw` を `docs/` からどう作るか（コピー / 参照 / 生成）

## 後で決めること

- `query` の運用をどこまで記録に残すか
- checklist 入力が欠けたときに何を代替正本にするか
- 試運転に使う小さな開発 task を何にするか

## child-tasknotes 早見表

| 領域 | 該当 note | 委任しやすさ | 先に止まりやすい判断 |
| --- | --- | --- | --- |
| 棚卸し | `01` | 🟢 | 正本 docs の最終採否 |
| 選別 | `02` | 🟡 | 件数上限と選別基準 |
| skeleton | `03` | 🟢 | wiki の置き場所と raw 方針 |
| ingest / rebuild | `04` `05` `07` | 🟡 | 実行主体と summary 粒度 |
| query | `06` | 🟡 | QA を残すか、直問中心にするか |
| candidates | `08` | 🟢 | final 昇格をこの段で扱うか |
| architecture checklist | `09` | 🟡 | 代替正本を 1系統か 2系統か |
| ux checklist | `10` | 🔴 | `ux-policy.md` を新規作成するか |
| checklist 反映 | `11` | 🟢 | raw にコピーするか参照にするか |
| dry-run | `12` | 🟡 | 既存 open task を使うか新規小 task にするか |

## よく詰まる3論点

### 1. `raw` と既存 SSoT をどう両立させるか

| 方式 | 何をするか | 向いている状況 | 弱み |
| --- | --- | --- | --- |
| A: コピー | `docs/` を `wiki/raw/knowledge/` にコピーする | docs-first の小さな pilot | 正本が二重化する |
| B: 参照 | raw 側には参照リストだけ置く | 最速で試したい pilot | discipline が弱いと境界が崩れる |
| C: 生成 | `docs/` から `wiki/raw/` を生成する | 既に codegen / SSoT が強い repo | 初期工数が増える |

- おすすめ:
  - repo に既存の generator や SSoT があるなら **C**
  - docs-first でまず小さく試すなら **A**
  - まず理解優先で最速 pilot を回すなら **B**

### 2. `query は read-only` の意味

- `query` は「答えを断定する装置」ではなく、「根拠へ行く入口」
- tasknote 実行中に `raw` や `summaries` を勝手に更新しない
- 何度も使う質問だけ `wiki/query/*.md` に残し、一回限りの質問は agent へ直問してよい

### 3. `architecture.md` や `ux-policy.md` が無いとき

- 無理に「変換」を始めず、先に代替正本を決める
- UX 側に正本が無ければ、`ux-policy.md` 自体を新規作成してから checklist 化するほうが筋がよい
- child `09` `10` は「翻訳 task」ではなく「入力を整える task」になることがある

## 入っているもの

- `フィール流LLM Wikiの作り方（途中まで）.md`
  - 親noteの共有版
- `child-tasknotes/`
  - 次に切る tasknote の下書き 12 本

## code-quest-pyxel を使うときだけ読む

ここから先は `code-quest-pyxel` 固有の事情。
共通手順が分かったあとに読む。

### 最初に止まりやすい点

- `docs/architecture.md` `docs/ux-policy.md` が無い
  - `09` `10` は代替入力か新規正本作成が要る
- 大型 docs が多い
  - `04` で 1ファイル1summary にするか章分割するかを決める
- 既存 SSoT が強い
  - `03` で `raw` と codegen 方針の整合を決める

### 暫定おすすめ

- `01` を始める前に `03` の判断ゲートだけ読む
- architecture checklist の入力は `docs/architecture_rules.yml` を第一候補にする
- UX 側は「変換」ではなく `ux-policy.md` の新規作成を前提に考える
- `12` の試運転は、既存 open task の派生小 task を切るのが中間解

### 詳細を読む場所

- 正本 docs と snapshot 候補: `child-tasknotes/01-...`
- raw / SSoT / 置き場所: `child-tasknotes/03-...`
- ingest 主体と粒度: `child-tasknotes/04-...`
- query 方式: `child-tasknotes/06-...`
- checklist 入力代替: `child-tasknotes/09-...` `child-tasknotes/10-...`

## Source

- business-docs 親note:
  - `todos/8-社内管理/2026年5月22日 フィール流LLM Wikiの作り方（途中まで）.md`
- business-docs commit:
  - `3634946b tasknote: add llm wiki how-to parent note`
