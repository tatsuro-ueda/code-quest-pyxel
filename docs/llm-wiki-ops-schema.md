# LLM Wiki Ops Schema

## Purpose

この schema は、この repo の `llm-wiki/` を generic chatbot ではなく disciplined wiki maintainer として保守するための既定動作をまとめる。対象は `llm-wiki/raw/` の immutable source、`llm-wiki/wiki/` の generated markdown、そしてそれらをつなぐ ingest / query / health-check の運用である。

## Shared Skill Routes

- `llm-wiki`: generic 入口。目的から child route を選ぶ
- `llm-wiki-query`: current wiki へ質問し、必要なら query page や candidate を残す
- `llm-wiki-health-check`: compiled wiki を read-only で点検し、`health-check-log` を残す
- `llm-wiki-update-schema`: `health-check-log` を踏まえ、安定した rule だけを schema に昇格する
- `llm-wiki-capture-and-ingest-source`: source を raw / summary draft / related page 更新へつなぐ

## Default Flow

1. 新しい source を `llm-wiki/raw/` 配下の適切な subtree に追加する。
2. source を読み、対応する `llm-wiki/wiki/summaries/` 配下に summary を作る。
3. `llm-wiki/wiki/indexes/master-index.md`、`llm-wiki/wiki/areas/`、`llm-wiki/wiki/logs/ingest-log.md` を更新する。
4. representative query を 1 本作り、再利用価値があれば `llm-wiki/wiki/query/` に保存する。
5. core 6 + `data_gaps` の health-check を行い、`llm-wiki/wiki/logs/health-check-log.md` に分類付きで残す。

## File Layout

- `llm-wiki/raw/`: immutable source documents
- `llm-wiki/wiki/summaries/`: source summaries
- `llm-wiki/raw/knowledge/`: knowledge sources
- `llm-wiki/raw/tasknotes/`: tasknote sources
- `llm-wiki/wiki/summaries/knowledge/`: knowledge summaries
- `llm-wiki/wiki/summaries/tasknotes/`: tasknote summaries
- `llm-wiki/wiki/indexes/master-index.md`: content-oriented index
- `llm-wiki/wiki/areas/`: related concept/topic pages
- `llm-wiki/wiki/query/`: saved answers
- `llm-wiki/wiki/candidates/`: external gap から切り出した next source candidates
- `llm-wiki/wiki/logs/source-inbox.md`: source 受付 log
- `llm-wiki/wiki/logs/ingest-log.md`: ingest chronology
- `llm-wiki/wiki/logs/health-check-log.md`: lint chronology

## Adapter Contract

- machine-readable path と tasknote section 名は `llm-wiki/adapter.yml` に置く
- human-readable な運用 rule は `docs/llm-wiki-ops-schema.md` に置く
- skill / helper は adapter を path 解決の SSoT とし、route の意味判断は schema に残す
- adapter に repo 名条件分岐や workflow policy を入れない

## Ingest Defaults

- one-by-one が既定である
- 初回 ingest の done 条件は `raw / summary / master index / related pages / ingest log`
- related page は最低 2 件更新する。届かないときは保留理由を log に残す
- 早すぎる entity / concept 分離は行わず、まず `areas` を使う
- 新規 area page は日本語の論点名ベースの file 名を既定にする
- `/` `\\` `:` `*` `?` `\"` `<` `>` `|` と改行は `・` に置き換える
- 既存の英語 slug area page は legacy 例として残し、今回の rule 更新では自動 rename しない

## Query Defaults

- representative question を 1 本選ぶ
- `master-index` を入口に related page を読む
- 迷ったら markdown で answer を作る
- evidence を answer に残す
- 再利用価値がある答えだけ `llm-wiki/wiki/query/` に保存する
- wiki 外の事実が必要なら answer に直混ぜせず、`llm-wiki/wiki/candidates/` に切り出す

### Query Read Order

- 質問文と質問者名を受け取り、`question_type` を先に決める
- current repo の query では `master-index` -> `summaries/knowledge` -> `areas` の順を既定にする
- 既存 query page は、同じ比較軸や synthesis が既にあるときだけ補助的に読む
- raw source や web 検索は query の既定入口にしない

### Answer Shape

- answer object は `question` `answer` `evidence` `compared_pages` `confidence` を必須とする
- `evidence` は page ごとの claim を 2〜5 bullet で残す
- `compared_pages` は実際に読んだ page の相対 path を列挙する
- `confidence` は `High` `Medium` `Low` と理由 1 文を持つ

### Format Rule

- markdown が既定である
- 比較中心の問いだけ table に切り替える
- table では `観点 | A | B | implication` の比較軸を優先する

### Save Gate

- official save の前に answer preview を見せ、`残すか` を user に確認する
- user が最初から `保存して` `wiki/query/ に残して` と明示しているときは `yes` 扱いでよい
- `no` のときは chat reply だけで止め、official page は作らない

### Query Filename Rule

- 新規 query page は日本語質問文ベースの file 名を既定にする
- 既定形は `YYYY年M月D日（質問者）質問内容.md`
- 質問者名が無いときは `YYYY年M月D日 質問内容.md`
- `/` `\\` `:` `*` `?` `\"` `<` `>` `|` と改行は `・` に置き換える
- 長すぎるときは主題を残して 40〜60 文字程度へ丸める
- 既存の英語 slug query page は legacy 例として残し、今回の rule 更新では自動 rename しない

### Candidate Defaults

- current wiki に無い外部事実が answer の核になるときだけ candidate page を作る
- candidate page には `missing_fact` `why_needed` `search_hint` `priority` を残す
- candidate file 名は `YYYY年M月D日 候補source：不足論点.md` を既定にする
- official answer に wiki 外の事実を直混ぜしない

## Health-Check Defaults

- `llm-wiki-health-check` は compiled wiki を主に読む read-only route である
- 既定の scope は `master-index` `areas` `query` `summaries/knowledge` `logs`
- core 6 を見る: contradictions / stale claims / orphan pages / missing concepts / missing crossrefs / data gaps
- raw source や tasknote 原文は主入力にしない
- 成功条件は「問題ゼロ」ではなく、「分類付き log が残ること」
- issue が無い項目は `none` と明記する
- `no issue` の回でも health-check log を残す
- 結果は `fix now / next ingest / candidate source / notes` に分ける
- `fix now` が見えても、この route 自体では page 修正を行わない
- schema 更新は `llm-wiki-update-schema` route に渡す
- small wiki でも source summary、related page、saved answer があれば 1 回回してよい

## Batch Policy

- batch ingest は initial health-check のあとでのみ検討する
- 開始条件は `health-check log あり / inbox 3 本以上 / 同テーマで低リスク`
- 既定は 3 本。2 回連続で安定したら 5 本まで広げてよい
- 各 source で `title / metadata / summary 冒頭` を見る
- batch 全体で `created pages / updated pages / index diff` を見る
- source ごとに 1 箇所だけ spot-check する
- `summary の質低下 / related page 理由不足 / index のつながり不自然` のどれか 1 つで止め、remaining source を inbox へ戻し、次は single-source に戻る

## Tasknote Ship Flow

close 済み tasknote の知見は business-docs の llm-wiki に一本化する（SSoT）。この repo の
`steering/done/` に置いたままにしない。close の直後に2手とも実行する。

```bash
cd ~/code-quest-pyxel

# 1手目: 送信箱（todos/files-to-fetch/5-製品開発/code-quest/）へ出す
uv run --no-project --with pyyaml python3 \
  ~/.local/share/chezmoi/shared/llm-wiki-core/python/llm_wiki_tasknote_ship_helper.py \
  "steering/done/<閉じたノート>.md"

# 2手目: business-docs へ push する
llm-wiki-push push --dry-run   # 送る対象を確認
llm-wiki-push push             # ACK を受けたファイルだけ送信箱から消える
```

- `status: done` → 送信箱へ移動し、元ファイルは残さない。`status: wont` は送らず `todos/wont/` へ退避する。
- **2手目を省かない。** 送信箱に置いただけでは bd に届かない。bd 側からの fetch 回収は 2026-07-26 に廃止済みで、ディレクトリ名 `files-to-fetch` は当時の名残。
- 結果 JSON の `conflict` / `failed` は自動復旧しない。送信箱に残るので中身を見て人が判断する。
- 送信箱は `.gitignore` 済み。中身を手で消さない。
- 送れるのは `.md` だけ。スクショ `.png` は `steering/done/` に残るので、参照している tasknote 本文に要点を書き写しておく。
- 送信設定の正本は `llm-wiki/adapter.yml` の `tasknote_ship`（category は `5-製品開発/code-quest`）。
- 理由: bd の llm-wiki を全マシンの頭脳として鍛えるため。2026-08-14 に、この導線が無く3か月ぶん26本が滞留していた取りこぼしを解消した。

## Exceptions

- high-risk source、重要判断を変える source、special output format は人判断を優先する
- 実験メモや一時的な迷いは tasknote に残し、schema には入れない
- optional tooling は source が増えてから検討する

## Update Rule

- `llm-wiki-update-schema` は `health-check-log` を主入力にする
- recurring pattern だけを schema 更新候補にする
- tasknote 原文や局所 incident は schema に直入れしない
- current schema の見出しは維持し、内部対応で 5 バケットを扱う
- 同じルールが 2 回連続で通ったときだけ schema を更新する
- evidence が弱い回は `no schema change` で止める
- 2 セッション連続で崩れなければ AGENTS から参照してよい
- それまでは tasknote を正本とし、schema は draft として扱う
