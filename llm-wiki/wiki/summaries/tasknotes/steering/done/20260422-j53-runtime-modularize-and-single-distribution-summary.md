---
source: raw/tasknotes/steering/done/20260422-j53-runtime-modularize-and-single-distribution.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月22日 J53 runtime monolith 分解と dev/prod 単一化 Summary Draft

## summary

この tasknote は、runtime monolith の分解から Code Maker bundler、development/production の単一化、systemd 常駐化までを段階的に完了した大きな移行記録です。Phase 1 で 109 メソッドを scenes / services / UI へ移し、Phase 1.5 で `main_runtime.py` を 49 行まで圧縮し、Phase 2 で Code Maker bundler を入れ、Phase 3 と 4 で production 1 本化と自動復旧まで閉じたことで、repo 構造と配布構造を同じ方向へそろえました。

## key_points

- Phase 1 で Game クラスの 109 メソッドを scenes（11 個）と shared/services・UI へ移し、`main_runtime.py` を 7266 → 1956 行に圧縮した。
- Phase 1.5 で定数群と world generation を専用 module へ抽出し、`main_runtime.py` を 49 行の pure re-export shim にした。
- Phase 2 で `codemaker_manifest.txt` と `codemaker_bundler.py` を導入し、shim 化で壊れた Code Maker zip を完全 bundle として復旧した。
- Phase 3 で development 系の split や browser fallback を削除し、production 1 本の配布へ寄せた。
- Phase 4 で `web_runtime_server.py` の自動 build と systemd 常駐化を入れ、VM 再起動後も遊べる状態にした。

## important_quotes

- "Game クラスの **109 メソッド**"
- "`main_runtime.py` を 1956 → **49 行**に圧縮"
- "production/ 1 本のみ生成（development/ 不在）"

## open_questions

- phase をまたぐ bundler / build 変更の学びを、どの guardrail に昇格するべきか。
- runtime modularization の次に、どの scene から framework-rule 適合を進めるべきか。
