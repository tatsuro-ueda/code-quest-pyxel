---
source: raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月12日 G12 code-maker.zip 再ビルド Summary Draft

## summary

この tasknote は、Code Maker 用 `code-maker.zip` が古い snapshot で止まっていた問題を、Web 版と同じ `main.py` と `blockquest.pyxres` をそのまま packaging し直すことで解消した記録です。修正の芯は runtime の作り替えではなく、zip 内 `main.py` と `my_resource.pyxres` の一致を artifact 単位で確かめ、さらに headless 起動で配布物として通ることまで確認した点にあります。

## key_points

- `code-maker.zip` は古い snapshot で止まっており、当時の `main.py` は現行の Web 版より古かった。
- 対応は `tools/build_codemaker.py` を作り、既にインライン済みの `main.py` と `blockquest.pyxres` を Code Maker 互換の zip へ詰め直す narrow fix に留めた。
- zip 内 `main.py` がプロジェクトの `main.py` と同一であることを確認した。
- zip 内 `my_resource.pyxres` が `blockquest.pyxres` と同一であることを確認した。
- zip 展開物を使った headless 起動が通り、Code Maker 向け artifact としての最低動作を検証した。
- Code Maker 向け配布物では、source を直すだけでなく、実際に持ち出す zip が現行正本と一致していることを done 条件に含める必要がある。

## important_quotes

- "Code Makerで遊ぶゲームをWeb版と同じ最新版にする"
- "main.pyは既にインライン済みなので、zipに詰めるだけのシンプルなスクリプトで十分。"
- "code-maker.zip内のmain.py(6,343行)と現在のmain.py(6,823行)が別バージョン。"

## open_questions

- この packaging 確認を定期 build や checklist に入れて、zip freshness を継続監視するか。
- Code Maker 持ち出し導線の検証を、headless 起動以外の user-facing artifact check まで広げるか。
- この学びを他の guardrail tasknote と横断テーマ化するか。
