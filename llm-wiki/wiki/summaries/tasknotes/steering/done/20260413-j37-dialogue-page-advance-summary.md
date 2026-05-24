---
source: raw/tasknotes/steering/done/20260413-j37-dialogue-page-advance.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月13日 J37 セリフ送りで前のフレーズが消えない Summary Draft

## summary

この tasknote は、複数フレーズ会話で前ページが残ってしまう不具合を、`今の 1 ページだけを表示する` 責務へ揃えて直した記録です。中心は `draw_message_window()` が current page 以外まで描いていた問題を再現テストで固定し、ページ送り helper を `message` / `town` / `professor` 系へ通したことでした。

## key_points

- 不具合は、世界樹や通信塔などの複数フレーズ会話で、決定ボタン後も前のフレーズが消えないことだった。
- 失敗テストで、`draw_message_window()` が現在ページに加えて次の 2 ページまで同時に描いていることを確認した。
- 根本原因は「現在ページの切り出し責務が分散していたこと」だった。
- `main.py` に `_advance_dialog_page()` と `_current_dialog_page_lines()` を追加し、`message` / `town` / `professor` 系へ適用した。
- `battle_text` は別経路なので今回の不具合と同根ではないことを確認した。
- `test/test_dialogue_paging.py` の追加・拡張と既存 dialogue 系テストの回帰確認で、複数フレーズ進行を Green に戻した。

## important_quotes

- "現在ページの切り出し責務が分散していたこと"
- "今の1ページだけを表示する"
- "ページ単位と行単位が混ざっていた"

## open_questions

- 世界樹、通信塔、プロフェッサーの見た目確認を実画面でも別途行うか。
- `battle_text` 側に似たページ送り問題があるなら別 task として切り出すか。
- 今回の helper へ、ほかの会話経路もどこまで寄せるか。
