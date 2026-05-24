---
source: raw/tasknotes/steering/done/20260413-j21-access-log-visibility.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月13日 J21 共有後のプレイ時間がわかるようにする Summary Draft

## summary

この tasknote は、共有 URL を送ったあとに「少しだけ触られたのか、しばらく遊ばれたのか」を親が後から把握できるように、same-origin の play session logging を最小構成で追加した記録です。中心は `play.html` ラッパーでの `start / heartbeat / end` 送信、SQLite 保存、集計 CLI、そして Web 互換を壊さないことでした。

## key_points

- 深層的目的は、共有後の反応を `件数` ではなく `遊ばれ方の長短` で判断できるようにすることだった。
- 保存層として `src/play_session_logging.py` と `.runtime/play_sessions.sqlite3` を追加し、`active_seconds` を元データとして残す方針を採った。
- `tools/web_runtime_server.py` で静的配信と `POST /internal/play-sessions/start|heartbeat|end` を同じ Python プロセスにまとめた。
- `templates/wrapper.html` と `tools/build_web_release.py` を拡張し、`play.html` / `play-preview.html` に `page_kind` と内部ログ API を埋め込めるようにした。
- `tools/report_play_sessions.py` で、日別・ページ別の session 数、平均 `active_seconds`、`short / middle / long` を端末から見られるようにした。
- `59 / 60 / 299 / 300` 秒境界や終了通知なしのケースをテストで固定し、`tools/test_web_compat.py` でも共有導線が壊れていないことを確認した。

## important_quotes

- "少しだけ触ったのか、長く遊んだのか"
- "可視化UIや親向けダッシュボードは今回のスコープに入れず"
- "start / heartbeat / end"

## open_questions

- same-origin の Python ログ API を実際の配信運用でどう常駐させるか。
- `tools/report_play_sessions.py` の見方や運用ルールを別ノートへ切り出すか。
- play log を `理解` の材料に留め、`監視` へ寄せない表示面をどこで設計するか。
