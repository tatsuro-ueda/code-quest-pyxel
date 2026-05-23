# LLM Wiki Ops Schema

## Purpose

この schema は、この repo の `llm-wiki/` を generic chatbot ではなく disciplined wiki maintainer として保守するための既定動作をまとめる。対象は `llm-wiki/raw/` の immutable source、`llm-wiki/wiki/` の generated markdown、そしてそれらをつなぐ ingest / query / health-check の運用である。

## Default Flow

1. 新しい source を `llm-wiki/raw/knowledge/` に追加する。
2. source を読み、`llm-wiki/wiki/summaries/knowledge/` に summary を作る。
3. `llm-wiki/wiki/indexes/master-index.md`、`llm-wiki/wiki/areas/`、`llm-wiki/wiki/logs/ingest-log.md` を更新する。
4. representative query を 1 本作り、再利用価値があれば `llm-wiki/wiki/query/` に保存する。
5. core 5 の health-check を行い、`llm-wiki/wiki/logs/health-check-log.md` に分類付きで残す。

## File Layout

- `llm-wiki/raw/knowledge/`: immutable source documents
- `llm-wiki/wiki/summaries/knowledge/`: source summaries
- `llm-wiki/wiki/indexes/master-index.md`: content-oriented index
- `llm-wiki/wiki/areas/`: related concept/topic pages
- `llm-wiki/wiki/query/`: saved answers
- `llm-wiki/wiki/candidates/`: external gap から切り出した next source candidates
- `llm-wiki/wiki/logs/source-inbox.md`: source 受付 log
- `llm-wiki/wiki/logs/ingest-log.md`: ingest chronology
- `llm-wiki/wiki/logs/health-check-log.md`: lint chronology

## Ingest Defaults

- one-by-one が既定である
- 初回 ingest の done 条件は `raw / summary / master index / related pages / ingest log`
- related page は最低 2 件更新する。届かないときは保留理由を log に残す
- 早すぎる entity / concept 分離は行わず、まず `areas` を使う

## Query Defaults

- representative question を 1 本選ぶ
- `master-index` を入口に related page を読む
- 迷ったら markdown で answer を作る
- evidence を answer に残す
- 再利用価値がある答えだけ `llm-wiki/wiki/query/` に保存する
- wiki 外の事実が必要なら answer に直混ぜせず、`llm-wiki/wiki/candidates/` に切り出す

## Health-Check Defaults

- core 5 を見る: contradictions / stale claims / orphan pages / missing concepts / missing crossrefs
- 成功条件は「問題ゼロ」ではなく、「分類付き log が残ること」
- 結果は `fix now / next ingest / candidate source` に分ける
- small wiki でも source summary、related page、saved answer があれば 1 回回してよい

## Batch Policy

- batch ingest は initial health-check のあとでのみ検討する
- 開始条件は `health-check log あり / inbox 3 本以上 / 同テーマで低リスク`
- 既定は 3 本。2 回連続で安定したら 5 本まで広げてよい
- 各 source で `title / metadata / summary 冒頭` を見る
- batch 全体で `created pages / updated pages / index diff` を見る
- source ごとに 1 箇所だけ spot-check する
- `summary の質低下 / related page 理由不足 / index のつながり不自然` のどれか 1 つで止め、remaining source を inbox へ戻し、次は single-source に戻る

## Exceptions

- high-risk source、重要判断を変える source、special output format は人判断を優先する
- 実験メモや一時的な迷いは tasknote に残し、schema には入れない
- optional tooling は source が増えてから検討する

## Update Rule

- 同じルールが 2 回連続で通ったときだけ schema を更新する
- 2 セッション連続で崩れなければ AGENTS から参照してよい
- それまでは tasknote を正本とし、schema は draft として扱う
