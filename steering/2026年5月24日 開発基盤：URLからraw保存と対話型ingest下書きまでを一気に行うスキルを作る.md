---
status: done
priority: high
scheduled: 2026-05-24T05:50:18+00:00
dateCreated: 2026-05-24T05:50:18+00:00
dateModified: 2026-05-24T06:08:41+00:00
tags:
  - task
  - llm-wiki
  - ingest
  - skill
  - karpathy
---

# 2026年5月24日 開発基盤：URLからraw保存と対話型ingest下書きまでを一気に行うスキルを作る

> 状態：⑧ Closing
> 次のゲート：なし

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
   2. 🟢 CCのみで可：共通 skill の追加、同期、検証まで進められる
   3. 🟢 共通 skill 配置後は残りの実装判断も tasknote と skill に閉じる

---

## 2) ユーザーストーリーマップ

> source を見つけてから summary draft を返すまでの 1 回分を、capture と対話 ingest に分けてそろえる。
> 委任度：🟢 共通 skill の実装と登録反映まで CC が進められた
> 残る曖昧さ：なし

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

> 委任度：🟢 共通 skill の作成と検証まで CC が完了した
> 残る曖昧さ：なし

### シナリオ一覧

- [x] シナリオ1：URL から raw source と inbox entry を一度に作れる

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

- [x] シナリオ2：AI が先に要点案を返し、人が強調点を返せる

1. 🧱 raw file が作られている
2. 🎬 AI が要点候補と引用候補を返す
3. ✅ 人が強調点と保留点を返せる

```gherkin
Given raw source file が作られている
When AI が source を読んで仮の `key_takeaways` と引用候補を返す
Then 人は強調点と違和感と保留点を返せる
And ingest は summary 確定前に 1 回対話を挟む
```

- [x] シナリオ3：対話を反映した summary draft が作られる

1. 🧱 人の返答で強調点が見えている
2. 🎬 AI が `key_points` と `important_quotes` を絞る
3. ✅ summary draft file が作られる

```gherkin
Given 人が強調点と保留点を AI に返している
When AI がその返答を反映して `key_points` `important_quotes` `open_questions` を整理する
Then `llm-wiki/wiki/summaries/knowledge/` に summary draft file が作られる
And draft は human review 前の状態として扱われる
```

- [x] シナリオ4：skill は related page 更新の前で止まる

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
- `~/.claude/skills/capture-and-ingest-source/SKILL.md` （➕：共通 skill 本体として追加した）
- `~/.codex/AGENTS.md` （✏️：新しい skill 登録が同期された）

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
  - `npx -y markdownlint-cli2 '/home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md'`
  - `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py --check`
  - `git -C /home/exedev/dotfiles diff --check`
- 成功条件:
  - tasknote が lint を通る
  - skill が `raw -> inbox -> takeaways -> summary draft` の flow を持つ
  - AGENTS から `capture-and-ingest-source` を発見できる
  - dotfiles diff に整形エラーがない
- 未実施時の扱い:
  - いずれか未実施なら common skill 完了扱いにしない

---

## 5) Tasklist

- [x] skill の保存先を共通 skill に決める
- [x] trigger phrase と入力形式を固める
- [x] skill の workflow を `capture + interactive ingest draft` で書く
- [x] 1 本の source を想定した example flow を skill に入れる
- [x] 必要な戻し先と境界を tasknote に残す

---

## 6) 作業ログ

- 仮 tasknote を起票した
- scope を `[5]-[21]` 相当のうち summary draft までに絞った
- 共通 skill の保存先を `~/.claude/skills/capture-and-ingest-source/` に確定した
- `~/.codex/AGENTS.md` と dotfiles 側 AGENTS に新しい skill 登録を同期した
- skill 本体の markdownlint と dotfiles diff check を通した

---

## 7) 評価と成果物

> 評価：🟢 共通 skill の追加、登録同期、検証まで一連で完了した

### 成果物

- `steering/2026年5月24日 開発基盤：URLからraw保存と対話型ingest下書きまでを一気に行うスキルを作る.md`
- `docs/superpowers/plans/2026-05-24-source-to-summary-draft-skill.md`
- `/home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`
- `/home/exedev/.codex/AGENTS.md`

---

## 8) Discussion

- `capture-source` と `interactive-ingest-draft` を 1 本化すると、source 発見直後の摩擦が減る
- ただし related page 更新まで入れると責務が広がるので、summary draft で止める方が Karpathy の対話 ingest に合う
- 共通 skill にしたことで、repo ごとの local schema を読む入口と既定 path の fallback を両立できた
- live invocation はこの session 中に再読み込みできないため、例示フローと AGENTS 登録確認で運用入口を固めた

---

## 9) Closing

- 状態: done
- 次のゲート: なし
- close 条件:
  - [x] skill の保存先が決まっている
  - [x] skill の workflow が tasknote から読める
  - [x] dry-run の入口が決まっている

---

## 10) 参考資料

- `steering/done/2026年5月23日 開発基盤：Karpathy型LLM Wiki運用の親ノート.md`
- `llm-wiki/raw/knowledge/2026-04-04-karpathy-llm-wiki.md`
- `docs/superpowers/plans/2026-05-24-source-to-summary-draft-skill.md`
- `/home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`
- Karpathy, `LLM Wiki`: `https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`
