---
source: raw/tasknotes/steering/done/20260422-j52-main-runtime-full-extraction.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月22日 J52 main.py / main_development.py を thin wrapper にし runtime 本体を src/runtime へ移した Summary Draft

## summary

この tasknote は、root `main.py` / `main_development.py` を thin wrapper にし、runtime 本体の正本を `src/runtime/` へ移した記録です。ここで大事だったのは、見た目だけ main を薄くするのではなく、build、Code Maker、preview metadata、promote の前提も runtime file 基準へそろえ、`root main が薄いだけで build は旧 monolith 依存` という偽ゴールを避けたことでした。

## key_points

- J51 後も、runtime monolith の本体と build の正本は root `main.py` 側に残っていた。
- 単なる import wrapper 化では不十分で、Code Maker zip と preview/promote も runtime file 基準へ切り替える必要があった。
- `src/runtime/main_runtime.py` と `src/runtime/main_development_runtime.py` を新設し、root runtime 本体を移した。
- root `main.py` / `main_development.py` は 20 行以内の thin wrapper へ置き換えた。
- 272 tests、headless/save/web compat、web/dev/codemaker build を通し、正本反転後も配布導線が壊れていないことを確認した。

## important_quotes

- "`main.py` が薄いだけで build は旧 monolith 依存"
- "root main がスッカラカンで、build / Code Maker / preview flow が壊れないこと"
- "`python -m pytest test/ -q` で `272 passed`"

## open_questions

- thin wrapper 化したあとの runtime monolith を、どの粒度でさらに分解するべきか。
- root entrypoint の薄さを、どの guardrail で継続的に検査するべきか。
