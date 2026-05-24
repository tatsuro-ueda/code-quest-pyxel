---
source: raw/tasknotes/steering/2026年5月24日 開発基盤：raw tasknote ingestの単純作業をPythonに寄せる.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：raw tasknote ingestの単純作業をPythonに寄せる Summary Draft

## summary

この note は、raw tasknote ingest のうち `決まった形に並べる仕事` を Python helper に寄せ、要約の意味づけは AI に残す方針を固めた記録です。`Result` を事実 section として拾う JSON contract を置き、raw tasknote 限定の scope を切り出しました。

## key_points

- 今回は speed のために Python 化するが、要約の言い過ぎを防ぐため文章生成はまだ AI に残す
- `Result` は事実の section とみなし、根拠候補に含める
- helper の返り値は JSON に固定し、以後の細かい形式判断は CC が引き取る

## important_quotes

- "`Result` は事実の section とみなし、根拠候補に含める"
- "helper の返り値は JSON に固定し、以後の細かい形式判断は CC が引き取る"

## open_questions

- なし。
