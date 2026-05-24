---
source: raw/tasknotes/steering/done/20260505-rename-production-to-dist.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 production/ → dist/ にリネーム（dev/prod 一本化の名残整理） Summary Draft

## summary

この note は、`production/` を `dist/` へ改名して build/server/artifact の呼び名を一本化した記録です。同時に、直前 task の staged 漏れが rename commit に混入した事実も明示し、rename 作業そのものの事故教訓まで残しています。

## key_points

- `git mv production dist` を軸に、build script、runtime server、infra、test、README まで参照を揃えた。
- `page_kind="production"` のような内部識別子は互換性のため温存し、folder rename と分離した。
- 前 detach task で 7 ファイルが commit から漏れていたことを記録し、`git status --short` 確認ルールを残した。

## important_quotes

- "`production/` → `dist/`"
- "`7 ファイル変更が commit から漏れた`"

## open_questions

- historical PRD に残る `development/` / `production/` 言及を、どの順で live 文書から掃除するべきか。
- multi-line `git add` 事故を今後どう防ぎ、どこまで自動化すべきか。
