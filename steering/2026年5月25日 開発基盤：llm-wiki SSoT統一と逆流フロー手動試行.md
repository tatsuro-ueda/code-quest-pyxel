---
status: in-progress
priority: normal
scheduled: 2026-05-25T09:00:00.000+09:00
dateCreated: 2026-05-25T22:00:00.000+09:00
dateModified: 2026-05-25T22:00:00.000+09:00
tags:
  - task
  - llm-wiki
  - infra
---

# 2026年5月25日 開発基盤：llm-wiki SSoT統一と逆流フロー手動試行

> 状態：⑨ Closing の手前。実作業ほぼ完了、`docs/repository-structure.md` コミット残り
> 次のゲート：（ユーザー）`docs/repository-structure.md` の差分をどの単位でコミットするか

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 wiki で育てた知見を docs/X.md に戻すフローをまず手動で成立させる
> 補足：やらないこと スキル化や新 route の実装、まずは手動で 1〜2 周回す
> 補足：責務分担厳格度 none

1. 前提条件
   1. 💦 `raw/knowledge/docs/` が `docs/` の実体コピーで SSoT が二重管理
   2. 💦 wiki/areas は育っているが docs/ への逆流フローはまだ無い

2. Before
   1. 💦 wiki の知見が docs/ に戻る経路が無く wiki が孤立しがち
   2. 💦 更新候補の宛先が docs/ か raw/ か曖昧
   3. ❌ 不安

3. After
   1. 💦 raw 6 本撤去で SSoT を docs/ に一本化
   2. 💦 逆流フロー（target → area → 候補 → 採用 → Edit）を 2 周回した
   3. ✅ ux-policy.md と repository-structure.md に wiki 由来改善が入った
   4. ✅ 副産物で wiki 側 stale (preview→current) を発見
   5. ❤️ 安心

4. 例外
   1. 候補 4 (Code Maker import 2 lane) は説明不足で却下
   2. 候補 5 (preview/current 昇格) は wiki 側 stale で不採用

5. 境界条件
   1. raw 撤去は指定 6 本のみ、`product-requirements-*` 等は scope 外
   2. ingest-log は append-only、過去 entry は書き換えず追記
   3. archive/ と docs/superpowers/plans/ の履歴参照は据え置く

6. 委任度
   1. 🟡 target docs 選定と候補採否はユーザー判断、抽出と Edit は CC
   2. 🟢 raw 撤去のような機械的書換えは CC 単独で進めてよい

---

## 2) ユーザーストーリーマップ

> 委任度：🟡 各 target docs の選定と候補採否はユーザー判断
> 残る曖昧さ：wiki side stale をどう直すか (candidate に切るか直接書換えか) は未確定

### 話題一覧

#### 話題1：raw/knowledge/docs/ の SSoT 統一

##### ユーザー：tatsuro（SSoT 統一）

1. 当初計画
    1. ❓ docs/ と raw/ の二重管理を解消
    2. 👀 6 本を raw から削除し wiki 参照を docs/ に repoint
    3. 📝 tasknote確認済み：0件（さかのぼり起票のため参照 tasknote なし）
    4. 📝 skill・tool・MCP確認済み：使う skill・tool・MCP は Bash の grep / sed、Edit、git、TaskCreate（MCP は 0件）
    5. 📝 永続的ドキュメント確認済み：見る永続的ドキュメントは 0件 ではなく `docs/llm-wiki-ops-schema.md` / `llm-wiki/wiki/indexes/master-index.md`

2. 追加分
    1. 👀 ingest-log を append-only として尊重 → 撤去 entry を追記
    2. ✂️ source-inbox は受付履歴として据え置く
    3. 📝 撤去対象外 8 本は別タスクへ送る

#### 話題2：wiki → docs/ への逆流フロー手動実行

##### ユーザー：tatsuro（逆流フロー）

1. 当初計画
    1. ❓ target docs を 1 つ選び wiki ドリフト候補を提示する
    2. 👀 `ux-policy.md` で 1 周、続けて `repository-structure.md` で 2 周
    3. 📝 tasknote確認済み：0件
    4. 📝 skill・tool・MCP確認済み：使う skill・tool・MCP は Read、Edit、AskUserQuestion、git（MCP は 0件）
    5. 📝 永続的ドキュメント確認済み：見る永続的ドキュメントは 0件 ではなく `docs/ux-policy.md` / `docs/repository-structure.md` / `llm-wiki/wiki/areas/*` の関連 4〜5 枚

2. 追加分
    1. 👀 候補が 10 個出たので上位 5 + 補足 3 に絞った
    2. ✂️ ユーザーが「分かりやすく 15 行で」と要求 → やさしい言葉で再提示
    3. 📝 2 周目で候補 4 説明不足 / 候補 5 wiki side stale を学んだ

---

## 3) Gherkin（完了条件）

> 委任度：🟢 backfill なのでシナリオはすべて実行済み事実として書ける
> 残る曖昧さ：なし

### シナリオ一覧

- [x] シナリオ1-1：raw/knowledge/docs/ の 6 本が削除される

1. 🧱 SSoT が docs/ にあるのに raw/ にも実体コピーが存在する（リポジトリ）
2. 🎬 git rm で 6 本削除し wiki 参照を docs/ に repoint し ingest-log に撤去 entry 追記（リポジトリ）
3. ✅ wiki/ live 参照に raw への参照が残らず `llm-wiki/raw/knowledge/docs/` には scope 外 8 本だけが残る（リポジトリ）

```gherkin
Given docs/ と llm-wiki/raw/knowledge/docs/ に同名 .md が 6 ペア存在し内容が完全一致している
When CC が git rm で raw 側 6 本を削除し wiki/summaries (6) / master-index (6 行) / areas (16 ファイル) のパスを docs/ に書き換える
Then llm-wiki/raw/knowledge/docs/ の残りは product-requirements-* 等の 8 ファイルだけになる
And wiki/ 配下の live 参照に raw/knowledge/docs/{6 本} は残らない
And ingest-log には append-only で [2026-05-25] retire entry が追記されている
```

- [x] シナリオ2-1：ux-policy.md に wiki ドリフトが反映される

1. 🧱 docs/ux-policy.md が古く wiki/areas/ に最近のタスクノート由来知見が蓄積されている（リポジトリ）
2. 🎬 候補リストを提示しユーザーが採用する候補を選ぶ（対話）
3. ✅ docs/ux-policy.md の該当項目が wiki の主張を反映する形に更新される（リポジトリ）

```gherkin
Given docs/ux-policy.md と llm-wiki/wiki/areas/child-readable-ux-and-parent-assist.md がある
When CC が候補リストを 5 個 + 補足 3 個で提示しユーザーが 1 と 2 を採用する
Then 第 2 項に「会話 UI では現在ページだけを表示し前ページが残らないようにする」が追加される
And 第 4 項が「.pyxres や Code Maker で作った効果音・音楽・画像など子どもの編集内容」に拡張される
And 差分は 2 行 (1 追加 + 1 置換) になる
```

- [x] シナリオ2-2：repository-structure.md に wiki ドリフトが反映される

1. 🧱 docs/repository-structure.md は詳細だが最近の運用方針が薄い（リポジトリ）
2. 🎬 候補リストを提示しユーザーが採用する候補を選ぶ（対話）
3. ✅ 5.2 表の役割明示 + 5.2 下の補足段落 + 3 章ツリー + 5.7 新節が追加される（リポジトリ）

```gherkin
Given docs/repository-structure.md と関連 wiki area がある
When CC が候補 5 個を提示しユーザーが 1,2,3 を採用し 4 と 5 を不採用にする
Then 5.2 表の test_*/hooks 行が役割明示形に書き換わる
And 5.2 表下に「guardrail entrypoint の 2 系統」補足段落が追加される
And 3 章の全体構造ツリーに llm-wiki/ 行が追加される
And 5.7 「llm-wiki/」節 (パス表 + 1 行説明) が追加される
```

- [x] シナリオ3-1：wiki 側 stale が副産物として検出される

1. 🧱 候補 5 で preview/current 昇格モデルを提示する（対話）
2. 🎬 ユーザーが「やめた (バグが多い)」と返す（対話）
3. ✅ wiki/areas/ に stale な記述が残っていることが判明し health-check 案件として記録される（tasknote）

```gherkin
Given wiki/areas/ に preview→current 昇格モデルが現行運用として書かれている
When ユーザーがその仕様は廃止済みと回答する
Then 候補 5 は不採用となる
And tasknote の Discussion に「wiki → 現実の逆方向ドリフト = health-check 案件」として記録される
```

---

## 4) Design（どうやるか）

- **関連スキル・MCP**：WebFetch / WebSearch (Karpathy 予習)、TaskCreate / TaskUpdate (進行管理)、Edit / Read / Bash (実作業)、Skill (`manage-tasknotes` 系)

### 【参照】

- Steering: なし (これ自体が steering tasknote)
- Architecture: `docs/repository-structure.md`
- UXPolicy: `docs/ux-policy.md`
- Ops schema: `docs/llm-wiki-ops-schema.md`

### 変更範囲

- やること:
  - `llm-wiki/raw/knowledge/docs/` から 6 本撤去
  - `wiki/summaries` (6) / `master-index` (6 行) / `areas` (16 ファイル) のパスを docs/ に repoint
  - `wiki/logs/ingest-log.md` に append-only で retire entry 追記
  - `docs/ux-policy.md` に第 2 項追加 + 第 4 項拡張
  - `docs/repository-structure.md` に 4 箇所追加 (3 章ツリー / 5.2 表書き換え + 補足段落 / 5.7 新節)
- やらないこと:
  - raw 撤去の対象拡大 (`product-requirements-*` 等は別タスク)
  - wiki side stale (preview→current) の修正 (health-check 案件として残置)
  - 逆流フローの skill 化 (まずは手動で機能確認まで)

### 検証

- 検証コマンド:
  - `grep -rn "raw/knowledge/docs/\(6本\)\.md" llm-wiki/wiki/` で残存参照確認
  - `git diff docs/ux-policy.md` `git diff docs/repository-structure.md` で diff 確認
  - pre-commit hook (`make verify`) で 3 系統 verifier 通過 (`verify_module_docstrings.py` / `verify_cj_cjob.py` / `scene_to_cj.py --verify-only`)
- 成功条件:
  - wiki/ live 参照に raw への参照ゼロ (ingest-log の append-only entry を除く)
  - docs/ 編集が pre-commit hook を通って commit できる
- 未実施時の扱い:
  - 残った参照はその都度 grep で発見し追加対応

---

## 5) Tasklist

- [x] (CC) Karpathy LLM Wiki gist + 解説記事を WebFetch で予習し現プロジェクトの ops-schema と対比
- [x] (CC) docs/ と raw/knowledge/docs/ の同一性を diff で確認 → 6 本完全一致
- [x] (User) 撤去方針を AskUserQuestion で確認 → 「raw から外し docs/ を SSoT として育てる」「6 本だけ試して様子見」を選択
- [x] (CC) 影響範囲を grep (47 箇所)、TaskCreate で 6 タスクに分解
- [x] (CC) summaries frontmatter 6 本書き換え (`source` を `../docs/foo.md` に、冗長な `origin:` 削除)
- [x] (CC) master-index の Raw 行 6 件を SSoT 行に書き換え
- [x] (CC) areas 配下 16 ファイルの参照を sed で一括書き換え (機械的書換のため Bash sed を採用)
- [x] (CC) ingest-log に `[2026-05-25] retire` エントリ追記
- [x] (CC) git rm で raw/ 6 本削除し git commit (`a988d1e`)
- [x] (User) 「タイムラインを先に考えたい」と方向再確認 → 「llm-wiki-query で docs/X.md 更新候補が出て採用で更新」フロー成立がゴール
- [x] (CC) `ux-policy.md` で 1 周目: target + 関連 wiki 4 枚を Read、候補 10 個抽出 → 上位 5 に絞って提示
- [x] (User) 「分かりやすく 15 行で」要求 → やさしい言葉で再提示
- [x] (User) 候補 1,2 を採用
- [x] (CC) `ux-policy.md` を Edit (第 2 項追加、第 4 項拡張)、git commit (`62cbeba`)
- [x] (User) 次の target docs を AskUserQuestion で確認 → `repository-structure.md` を選択
- [x] (CC) `repository-structure.md` で 2 周目: target + 関連 wiki 4 枚を Read、候補 5 個抽出
- [x] (User) 候補 1,2,3 採用、4 不採用 (説明不足)、5 不採用 (wiki 側 stale)
- [x] (CC) `repository-structure.md` を Edit (4 箇所: ツリー / 5.2 表書換 + 補足 / 5.7 新節)
- [ ] (User) `repository-structure.md` の差分をどの単位でコミットするか判断
- [ ] (Later) `wiki/areas/` の preview→current 昇格 stale 記述を `llm-wiki-health-check` で記録

### 記録の分け方

#### 作業ログ に書く

- 変更したファイルや差分
- 実行した確認コマンドと結果
- 未解決なら起きた事実と影響

#### Discussion に書く

- なぜ「raw 撤去 → 逆流フロー」の順だったか
- 候補抽出が wiki/areas + tasknote summaries で機能した理由
- 候補 4 説明不足の反省、候補 5 stale 発見の意義

---

## 6) 作業ログ

- raw 撤去前 grep: wiki/, docs/ 配下に 47 箇所の `raw/knowledge/docs/{6 本}` 参照
- raw 撤去後 grep: wiki/ live 参照 (summaries / areas / master-index) はゼロ、append-only な ingest-log と受付履歴な source-inbox にのみ残存（意図通り）
- raw 撤去コミット `a988d1e`: 30 files changed, +72 / -3163 lines, pre-commit OK
- `ux-policy.md` diff: `+1` 行 (会話 UI ルール) と `±1` 行 (第 4 項拡張) = 2 行差分
- `ux-policy.md` コミット `62cbeba`: 1 file changed, +2 / -1 lines, pre-commit OK
- `repository-structure.md` diff: +24 / -3 行、4 箇所追加、未コミット

---

## 7) 評価と成果物

> 評価：🟢 期待通り完了した (`repository-structure.md` コミットだけ残り)

### 成果物

- コミット `a988d1e`: `docs: retire 6 raw doc copies and unify SSoT to docs/`
- コミット `62cbeba`: `docs: extend ux-policy with dialog page rule and Code Maker asset guard`
- 未コミット差分: `docs/repository-structure.md` (4 箇所追加)
- 副産物: wiki side stale 発見 (preview→current 昇格廃止が wiki に未反映) → 次の health-check 課題
- フロー実証: 「target docs → 関連 area 読み → ドリフト候補抽出 → ユーザー選択 → docs/ Edit」が 2 周回って機能することを確認

---

## 8) Discussion

- **raw 撤去を先にやった理由**: 残ったままだと「query が docs/ を更新するのか raw/ を更新するのか」分岐が生まれる。撤去でフロー設計がシンプルになる
- **area page が育っている前提が効いた**: 既に area が「最近の決定を SSoT の語彙にまとめ直す層」として機能していたため、ドリフト検出はかなりやりやすかった。area が薄い場合は候補抽出が貧弱になる可能性
- **候補 4「2 lane」が伝わらなかった**: 技術用語 (static host / shared server / browser fallback) を並べてしまい、ユーザーが「意味がわからない」と返した。`AskUserQuestion` の preview を使うか、具体例 (「friend に URL 送るときの挙動」など) で書き直すべきだった
- **候補 5「preview→current」**: wiki に「現行運用」として書かれていたが実は廃止済み (バグ多い)。これは逆方向のドリフト = health-check 案件であり、「wiki → docs」だけでなく「現実 → wiki」も periodic に必要
- **手動実行で見えた skill 化要件**:
  - target docs ファイル名から関連 area を引く仕組み (今回は master-index と勘で決定)
  - 候補の優先度づけを機械化 (複数 area で言及 / 最近の tasknote / 既存項との関連度 など)
  - 候補提示は技術用語禁止、やさしい言葉と具体例
- **target docs 優先リスト（ユーザー指定 2026-05-25）**: 次回以降の逆流フローは、別途指定がなければ次の 3 つを優先 target にする
  - `docs/framework-rule.md`（コーディング原則 / MVP 規約本体）
  - `docs/repository-structure.md`（リポジトリ構造 + 責務分担）
  - `docs/ux-policy.md`（子ども向け UI / 親補助境界）

### 反省とルール化

- 記入先：feedback memory / 将来の `llm-wiki-query` skill 拡張
- 次にやること：
  - `repository-structure.md` の差分コミット
  - `wiki/areas/platform-sharing-and-approval-ops.md` と `repository-operating-structure.md` の preview→current stale 記述を `llm-wiki-health-check` で記録 → candidate にするか直接書換えか判断
  - memory に「候補提示は技術用語を避け、具体例 + やさしい言葉で」を feedback として残す検討
  - 逆流フローを 3 周目で別 docs (`customer-jobs` か `framework-rule`) で安定確認 → skill 化の機運

---

## 9) Closing

- 状態: in-progress (実作業はほぼ完了、`repository-structure.md` コミットだけ残る)
- 次のゲート: ユーザー判断: `repository-structure.md` の差分をどの単位でコミットするか (この tasknote と一緒 / 別 / 後回し)
- close 条件:
  - [ ] `docs/repository-structure.md` がコミットされる
  - [ ] wiki side stale (preview→current) を次の health-check 案件として記録する
  - [ ] このセッションの reflection を memory に save するか判断する

---

## 10) 参考資料

- Karpathy gist: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
- 関連 docs: `docs/llm-wiki-ops-schema.md` / `docs/ux-policy.md` / `docs/repository-structure.md`
- 関連 wiki page: `llm-wiki/wiki/indexes/master-index.md` / `wiki/areas/child-readable-ux-and-parent-assist.md` / `wiki/areas/repository-operating-structure.md`
- 関連 commit: `a988d1e` (raw 撤去), `62cbeba` (ux-policy 反映)
