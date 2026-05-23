# query

generated wiki を読むときの read-only 入口。

## read-only rules

- query 中に `llm-wiki/raw/` を更新しない
- 根拠は summary / checklist / index に限定して返す
- 情報不足なら不足と書く
- raw が古そうでも maintenance note 以外は更新しない

## available sources

- knowledge summaries: 10
- checklist summaries: 3
- tasknote summaries: 5

## answer template

```markdown
## Q: <質問>

### A

<2〜5文の答え>

### 根拠

- `summaries/...`
- `checklists/...`

### 情報不足（あれば）

- ...
```
