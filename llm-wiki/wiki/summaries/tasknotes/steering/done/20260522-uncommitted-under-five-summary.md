---
source: raw/tasknotes/steering/done/20260522-uncommitted-under-five.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月22日 未コミットを5個以下に保って安心して進める Summary Draft

## summary

この note は、Git Graph の `Uncommitted Changes (89)` 表示に振り回されず、terminal の `git status` を正とする運用判断を記録した小さな安全ノートです。UI の stale 数字より shell の fresh state を優先する読み方を明文化しました。

## key_points

- Git Graph は 89 件表示のまま更新中だったが、`git status --short -uall | wc -l` は 5 行だった。
- 5 行のうち 2 行は同一 tasknote の move 由来で、目標「5個以下」は達成していた。
- built-in Git エラーの拡張ログを確認し、GUI ではなく terminal を正本とする結論を残した。

## important_quotes

- "`GUI 表示ではなく terminal を正本`"
- "`git status --short -uall`"

## open_questions

- UI stale と terminal truth のズレを、どこまで team rule として明文化するべきか。
- 同種の Git UI 不調時に、最初に見る診断コマンドをどこへまとめるべきか。
