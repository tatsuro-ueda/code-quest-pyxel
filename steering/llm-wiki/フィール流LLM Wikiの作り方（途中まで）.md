# フィール流LLM Wikiの作り方（途中まで）

> 状態：未完了
> 次のゲート：練習用プロジェクトの正本 docs と Git snapshot 候補を棚卸しする

## 何を作るか

別マシンの小さな開発プロジェクトで、Karpathy寄りの最小 LLM Wiki を再現する。  
ただし今回は「知識基盤を全部作る」ことではなく、開発支援に必要な所までを短時間で通す。

## このパッケージのユーザーストーリー

- ユーザー:
  - Feel
- 課題:
  - 別PJで LLM Wiki 構築を始めるたびに、入口と意思決定の順番が重い
- ソリューション:
  - dotfiles 経由で配る親note + child tasknotes の共有パッケージ
- ストーリー:
  - dotfiles を更新し、tasknote を import して開始する
  - 途中で数回の意思決定があっても、最後の試運転までたどり着ける

## 今回のゴール

- `raw -> summaries -> indexes -> areas -> query -> candidates` を通す
- `architecture checklist` と `ux checklist` を wiki から辿れるようにする
- 小さな開発 task 1 本で、wiki と checklist を実際に使ってみる

## 最初に決めること

### 1. latest docs

まず今の正本 docs を決める。候補は project ごとに違ってよい。

- `architecture.md`
- `ux-policy.md`
- `customer-journey.md`
- `customer-jobs.md`
- `glossary.md`

### 2. raw の置き場所と SSoT との関係

`wiki/` をどこに置き、`raw` を `docs/` からどう作るかを決める。

- コピーして置く
- 参照だけを持つ
- generator で作る

repo に既存の codegen / SSoT が強いなら、この判断を `history snapshots` より先に読むほうが安全。

### 3. history snapshots

Git 履歴から、方針が変わった節目だけを拾う。  
全部の commit を raw に入れるのではなく、2〜3個の転換点に絞る。

### 4. closed tasknotes

docs がなぜ変わったかを補うために、closed tasknotes を古い順に追加する。

### 5. query / ingest の実行主体

工程図だけでなく、「誰がどう回すか」も決める。

- ingest: 手動 / スクリプト / CLI 一括
- query: QA 蓄積 / 直問 / 併用

## 推奨順序

1. latest docs を `raw/knowledge` に入れる
2. Git 履歴から転換点 snapshot を `raw/knowledge` に足す
3. closed tasknotes を `raw/tasknotes` に入れる
4. `summaries` を生成する
5. `indexes` と `areas/current-state` を生成する
6. `query` を read-only で通す
7. `candidates` を出す
8. `architecture checklist` を作る
9. `ux checklist` を作る
10. checklist docs を `raw/knowledge` と `summaries/knowledge` に合流させる
11. 小さな開発 task 1 本で試運転する

## 重要な考え方

### latest docs を先に入れる

古い tasknote を先に大量投入すると、今の正本がぼけやすい。  
先に latest docs を固定し、そのあとで経緯を足す方が安全。

### Git 履歴を tasknote の代わりに使ってよい

練習用プロジェクトでは、tasknote が薄くても Git 履歴つき docs が強い。  
`今の正本` と `昔の方針転換点` を分けて raw に入れれば、AI が追いやすい。

### query は read-only

`query` は「答えを断定する装置」ではなく、「根拠へ行く入口」。  
tasknote 処理中に `raw` や `summaries` を勝手に更新しない。

### raw と SSoT は project ごとに決める

`raw を正本にする` という言い方は、その project に既存の正本が無い場合は素直に効く。
一方、すでに `docs/` や generator が正本なら、wiki 側は「pilot 用の snapshot 層」と割り切るほうが安全なことがある。

- docs-first の小さい repo:
  - `raw` へコピーする方が分かりやすい
- codegen / SSoT が強い repo:
  - `raw` を generator で作る方が一貫しやすい
- 最速 pilot:
  - 参照方式でもよいが、境界ルールを README に明文化する

### concept/entity は保留でよい

最初は `candidates` を出すだけでよい。  
final の `concepts/` や `entities/` は、人と LLM が相談してからでよい。

## この段階でまだやらないこと

- 本格 `lint:wiki`
- stale claims 監査
- contradiction 検出
- concept/entity の自動昇格
- 常駐 ingest

## 完了条件

- `query` が根拠リンク付きで答える
- `architecture checklist` を wiki から辿れる
- `ux checklist` を wiki から辿れる
- 小さな開発 task 1 本で `current-state + checklist` を使ってみた結果が残る

## まだ終わっていないこと

- 練習用プロジェクトの `latest docs` をまだ確定していない
- Git 履歴の転換点 snapshot をまだ拾っていない
- closed tasknotes の投入順もまだ未確定
- raw / summaries / indexes / areas / query / candidates は、対象プロジェクト側でまだ未実行
- checklist docs の生成と試運転もまだ未実行

## 次に使うファイル

- `child-tasknotes/01-練習用プロジェクトの正本docsとGit snapshot候補を棚卸しする.md`
- `child-tasknotes/02-練習用プロジェクトのclosed tasknotes投入候補と順番を固定する.md`
- `child-tasknotes/03-練習用プロジェクト向けLLM Wiki skeletonと命名ルールを置く.md`

---

## code-quest-pyxel への適用上の懸念（2026-05-22 追記）

### 1. 正本 docs が揺れている

- `docs/architecture.md` `docs/ux-policy.md` は存在しない（09 / 10 の入力欠落）
- `docs/architecture_rules.yml` が `status: draft` の正本候補（`repository-structure.md` をリプレース予定で並存）
- `customer-jobs.md` と `old-customer-jobs.md` の並存
- → 01 で「どちらを正本にするか」ユーザー判断が必要

### 2. docs サイズの問題

- 大型ファイルが複数（最大 107KB の YAML、95KB の Markdown）
- `minimal ingest` を素直にやるとサマリーが粗くなる
- 1ファイル1サマリーか章分割かの**粒度判断**は委任しにくい
- 04 着手時、まず 1件 で形を試してから全件適用する

### 3. YAML / Markdown 混在

- 正本候補のうち、構造化 YAML が複数（`architecture_rules.yml`, `stakeholder_voices.yml`）
- 親note は md 前提なので、YAML の summary 化規約を 03 で追加で決める必要がある

### 4. ingest pipeline と query の実装方式が抽象用語のまま

- 親note は工程図だけ示し、**実行主体（手動 / スクリプト / Codex 一括）**が未定義
- query も実装方式（手動 QA 蓄積 / Claude 直問 / SQLite）が未定義
- これらは 04 / 06 着手前に決める

### 5. SSoT ポリシーとの整合

- プロジェクトには `YAML → gen_data.py → generated 一方通行` の既存ポリシーあり
- `raw を正本にする`（親note 原則）とぶつかる可能性
- 03 で置き場所と二重化方針を確定する

### 6. closed tasknote 選別のヒドゥンコスト

- `steering/done/` に 115件
- 「docs変更理由が強い」の判定は本文を読まないとできない
- AI 丸投げは過剰選択しやすい
- 02 では**件数上限**と**タグフィルタ**を先に与える

### 7. 09 / 10 の入力代替

- architecture-checklist の元: `architecture_rules.yml`（最有力）/ `framework-rule.md` / `repository-structure.md`
- ux-checklist の元: 単独で ux-policy として成立する docs が無い
  - → **ux-policy.md 自体を新規作成**する選択肢を検討する

### 8. 試運転 task の難度設定

- 簡単すぎる → checklist の価値が見えない
- 複雑すぎる → checklist で防げる範囲を超える
- 既存 open task（例: `steering/20260517-battle-stale-spell-message.md`）を兼ねるか、捨て試運転にするかの判断が要る

### 9. 親note が「途中まで」である事の波及

- 「query は read-only」「concept は自動昇格しない」は原則のみで運用ルールが欠落
- Claude Code は自然に書き換えに行く性質があるので、03 で **wiki/README に運用ルールを明文化**する

### 10. 委任で詰まる順序

```
01 棚卸し（軽い判断ゲート 1, 7）
└─ 03 skeleton（判断ゲート 5, 9）★ここを通すと一気に走れる
   └─ 02 選別（判断ゲート 6）
      └─ 04 ingest（判断ゲート 2, 3, 4）★ここで再度詰まる
         └─ 05, 06, 07, 08
            └─ 09, 10（判断ゲート 7）★ここで再度詰まる
               └─ 11, 12（判断ゲート 8）
```
