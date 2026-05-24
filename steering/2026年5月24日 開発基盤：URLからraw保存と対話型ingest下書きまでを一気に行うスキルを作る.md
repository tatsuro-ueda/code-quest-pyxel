---
status: open
priority: high
scheduled: 2026-05-24T05:50:18+00:00
dateCreated: 2026-05-24T05:50:18+00:00
dateModified: 2026-05-24T05:50:18+00:00
tags:
  - task
  - llm-wiki
  - ingest
  - skill
  - karpathy
---

# 2026年5月24日 開発基盤：URLからraw保存と対話型ingest下書きまでを一気に行うスキルを作る

> 状態：① Journey
> 次のゲート：（ユーザー）このスキルを project 固有か共通 skill か決める

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 source を見つけた直後の熱量を落とさず、Karpathy 流の対話型 ingest を 1 回で始められるようにする
> 補足：やらないこと related page 更新や query 保存や health-check まで 1 本の skill に詰め込まない
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 入力は URL、動画リンク、短いメモ付き URL のいずれかを想定する
   2. 💦 raw source は `llm-wiki/raw/knowledge/` に保存する
   3. 💦 Karpathy の原文どおり ingest は対話を挟む
   4. 💦 今回の scope は parent note の [5]-[21] に相当する

2. Before
   1. 💦 source 保存と ingest 下書きが別々の依頼になりやすい
   2. 💦 `source_id` や frontmatter を毎回手で組み立て直している
   3. 💦 summary draft に行く前の対話導線が skill 化されていない
   4. ❌ だるい

3. After
   1. 💦 1 本の skill で source 種別判定から raw file 作成まで進められる
   2. ✅ `source-inbox` 記録と summary draft 作成まで一気に通せる
   3. ✅ AI が先に要点案と引用候補を返し、人が強調点を返す流れを固定できる
   4. ❤️ ラクチン

4. 例外
   1. source 本文が取れないときは `raw_notes` 中心で raw file を作ってよい
   2. transcript 不足の動画は metadata と first impression だけ先に保存してよい

5. 境界条件
   1. related pages、index、ingest log 更新は今回の skill に含めない
   2. batch ingest や自動巡回は扱わない
   3. 人の review 前に summary draft を確定版として広げない

6. 委任度
   1. 🟢 source capture から summary draft までの大枠は固まっている
   2. 🟢 CCのみで可：tasknote draft と skill workflow の初稿作成
   3. 🟡 人の判断: skill の設置場所を project 固有か共通かで決める

---

## 2) ユーザーストーリーマップ

> source を見つけてから summary draft を返すまでの 1 回分を、capture と対話 ingest に分けてそろえる。
> 委任度：🟢 draft workflow の整理までは CC が進められる
> 残る曖昧さ：skill の保存先は未確定

### 事前確認

- [x] tasknote確認済み
- [x] skill・tool・MCP確認済み
  - [x] `manage-tasknotes`
  - [x] `brainstorming`
  - [x] `create-skill`
  - [x] shared `tasknote-lint`
- [x] 永続的ドキュメント確認済み
  - [x] `AGENTS.md`
  - [x] `manage-tasknotes/TEMPLATE.md`
  - [x] `manage-tasknotes/RULES.md`
  - [x] `steering/done/2026年5月23日 開発基盤：Karpathy型LLM Wiki運用の親ノート.md`

### 本体

#### 話題1：URL やメモから raw source を作る

##### ユーザー：Karpathy 型の知識キュレーター（capture）

1. 当初計画
    1. 👀 source が記事か動画か投稿かを見分ける
    2. 🏷️ `source_id` と file path を決める
    3. 📝 raw file に metadata と `why_saved` を書く
    4. 📥 `raw_text` または `raw_notes` を入れる
    5. 🕒 `source-inbox` に `status=inbox` で記録する

#### 話題2：raw source から対話型 ingest 下書きを返す

##### ユーザー：Karpathy 型の知識キュレーター（interactive ingest）

1. 当初計画
    1. 👀 AI が raw file を読む
    2. 💬 AI が `key_takeaways` と引用候補を先に返す
    3. 👆 人が強調点、違和感、保留点を返す
    4. ✂️ AI が `key_points` `important_quotes` `open_questions` を絞る
    5. 📝 summary draft file を作る

#### 話題3：skill の責務を summary draft で止める

##### ユーザー：Karpathy 型の知識キュレーター（boundary）

1. 当初計画
    1. ✂️ related page 更新より前で 1 回止まる
    2. 👀 人が summary draft を読んでから次へ進む
    3. 🔗 後続の `update-related-pages` は別 route に分ける

#### 話題4：skill と tasknote を後続実装へつなぐ

##### ユーザー：この repo の運用者（implementation）

1. 当初計画
    1. ❓ skill の保存先を 1 つ決める
    2. 🛠️ trigger phrase と入力形式を定める
    3. 🧪 1 本の source で dry-run する
    4. 📝 運用で使えるなら parent note へ戻す

---

## 3) Gherkin（完了条件）

> 委任度：🟢 skill draft の設計と起票までは CC が進められる
> 残る曖昧さ：skill の保存先は未確定

### シナリオ一覧

- [ ] シナリオ1：URL から raw source と inbox entry を一度に作れる

1. 🧱 運用者が URL か動画リンクを 1 本持っている
2. 🎬 skill に source と短い保存理由を渡す
3. ✅ raw file と `source-inbox` entry がそろって作られる

```gherkin
Given 運用者が ingest したい source URL を 1 本持っている
When capture 付き ingest skill に URL と保存理由を渡す
Then source 種別と `source_id` が決まる
And `llm-wiki/raw/knowledge/` に raw file が作られる
And `llm-wiki/wiki/logs/source-inbox.md` に inbox entry が追加される
```

- [ ] シナリオ2：AI が先に要点案を返し、人が強調点を返せる

1. 🧱 raw file が作られている
2. 🎬 AI が要点候補と引用候補を返す
3. ✅ 人が強調点と保留点を返せる

```gherkin
Given raw source file が作られている
When AI が source を読んで仮の `key_takeaways` と引用候補を返す
Then 人は強調点と違和感と保留点を返せる
And ingest は summary 確定前に 1 回対話を挟む
```

- [ ] シナリオ3：対話を反映した summary draft が作られる

1. 🧱 人の返答で強調点が見えている
2. 🎬 AI が `key_points` と `important_quotes` を絞る
3. ✅ summary draft file が作られる

```gherkin
Given 人が強調点と保留点を AI に返している
When AI がその返答を反映して `key_points` `important_quotes` `open_questions` を整理する
Then `llm-wiki/wiki/summaries/knowledge/` に summary draft file が作られる
And draft は human review 前の状態として扱われる
```

- [ ] シナリオ4：skill は related page 更新の前で止まる

1. 🧱 summary draft まで作成できている
2. 🎬 skill の責務範囲を確認する
3. ✅ related page 更新は別 route に残る

```gherkin
Given raw file と summary draft file が作成できている
When skill の責務範囲を確認する
Then related page 更新と index 更新はこの skill に含まれない
And 後続の別 route に分けて扱う
```

---

## 4) Design（どうやるか）

### 責務分担概要

- 1 本目の責務は `capture-source` と `interactive-ingest-draft` をまとめる
- 保存先は `llm-wiki/raw/knowledge/` と `llm-wiki/wiki/summaries/knowledge/` に限定する
- 対話は `key_takeaways` 提示と human feedback 反映の 1 往復を最小単位にする
- related page 更新や query 保存は別 skill または別 route に分ける

### 責務分担概要図

```mermaid
flowchart LR
    A[URL or note] --> B[source type 判定]
    B --> C[raw file 作成]
    C --> D[source-inbox 追記]
    D --> E[key takeaways 提示]
    E --> F[human feedback]
    F --> G[summary draft 作成]
```

### 責務分担詳細

- `steering/2026年5月24日 開発基盤：URLからraw保存と対話型ingest下書きまでを一気に行うスキルを作る.md` （➕：skill 化の判断と手順の draft を持つ）
- `steering/done/2026年5月23日 開発基盤：Karpathy型LLM Wiki運用の親ノート.md` （➕：[5]-[21] の元になる運用タイムラインを持つ）
- `llm-wiki/raw/knowledge/` （✏️：source 実体の保存先として扱う）
- `llm-wiki/wiki/logs/source-inbox.md` （✏️：capture 後の inbox 記録先として扱う）
- `llm-wiki/wiki/summaries/knowledge/` （✏️：summary draft の保存先として扱う）
- `~/.claude/skills/<skill-name>/SKILL.md` （➕：共通 skill にする場合の候補）
- `.claude/skills/<skill-name>/SKILL.md` （➕：project 固有 skill にする場合の候補）

### 【参照】

- Steering: `steering/done/2026年5月23日 開発基盤：Karpathy型LLM Wiki運用の親ノート.md`
- Architecture: `AGENTS.md`
- Source: `llm-wiki/raw/knowledge/2026-04-04-karpathy-llm-wiki.md`

### 変更範囲

- やること:
  - scope を URL 受け取りから summary draft 作成までで固定する
  - skill 化に必要な入力、出力、対話 1 往復を定義する
  - 保存先の候補と dry-run の観点を tasknote に残す
- やらないこと:
  - 今この場で skill 実装まで確定すること
  - related page 更新や index 更新を同じ skill に入れること
  - batch ingest や watcher を追加すること

### 検証

- 検証コマンド:
  - `node /home/exedev/dotfiles/shared/linter/coding-rules/tasknote/run_tasknote_lint.mjs --config ./tasknote-lint.config.json 'steering/2026年5月24日 開発基盤：URLからraw保存と対話型ingest下書きまでを一気に行うスキルを作る.md'`
- 成功条件:
  - tasknote が lint を通る
  - scope が `raw -> inbox -> takeaways -> summary draft` で読める
  - 未確定点が skill の保存先だけに絞られている
- 未実施時の扱い:
  - lint 未実施なら仮起票止まりとする

---

## 5) Tasklist

- [ ] skill の保存先を決める
- [ ] trigger phrase と入力形式を固める
- [ ] skill の workflow を `capture + interactive ingest draft` で書く
- [ ] 1 本の source で dry-run する
- [ ] 必要なら parent note へ戻し先を追記する

---

## 6) 作業ログ

- 仮 tasknote を起票した
- scope を `[5]-[21]` 相当のうち summary draft までに絞った
- 未確定点を skill の保存先 1 点に圧縮した

---

## 7) 評価と成果物

> 評価：🟢 scope と未確定点を provisional note として切り出せた

### 成果物

- `steering/2026年5月24日 開発基盤：URLからraw保存と対話型ingest下書きまでを一気に行うスキルを作る.md`

---

## 8) Discussion

- `capture-source` と `interactive-ingest-draft` を 1 本化すると、source 発見直後の摩擦が減る
- ただし related page 更新まで入れると責務が広がるので、summary draft で止める方が Karpathy の対話 ingest に合う
- skill 作成前に、共通 skill か project 固有 skill かだけを決める必要がある

---

## 9) Closing

- 状態: open
- 次のゲート: （ユーザー）このスキルを project 固有か共通 skill か決める
- close 条件:
  - [ ] skill の保存先が決まっている
  - [ ] skill の workflow が tasknote から読める
  - [ ] dry-run の入口が決まっている

---

## 10) 参考資料

- `steering/done/2026年5月23日 開発基盤：Karpathy型LLM Wiki運用の親ノート.md`
- `llm-wiki/raw/knowledge/2026-04-04-karpathy-llm-wiki.md`
- Karpathy, `LLM Wiki`: `https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`
