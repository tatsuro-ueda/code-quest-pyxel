---
source: raw/tasknotes/steering/done/20260414-j43-public-access-log-runtime.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月14日 J43 実公開URLで遊んでもアクセスログが残らない Summary Draft

## summary

この tasknote は、実公開 URL で遊ばれても play session が残らなかった問題を、機能未実装ではなく「公開導線がログ受付サーバにつながっていない」問題として直した記録です。修正の芯は、`python -m http.server` で配っていた 8888 番ポートを、`POST /internal/play-sessions/*` を受けられる `tools/web_runtime_server.py` ベースへ差し替え、実運用の起動方式まで固めたことでした。

## key_points

- `CJ21` が done でも、実公開導線では `.runtime/play_sessions.sqlite3` が空のままだった。
- 8888 の公開プロセスが `python -m http.server` で、`POST /internal/play-sessions/start` に `501` を返していた。
- コード側のログ基盤は正常で、壊れていたのは実公開プロセスだけだった。
- `CJ43` を新設して、「実公開で遊ばれた記録が見える」責務を切り出した。
- 8888 を `tools/web_runtime_server.py --host 0.0.0.0 --port 8888` へ差し替える方針にした。
- user systemd service で永続化し、実公開 URL から SQLite へ記録が残ることを確認した。

## important_quotes

- "壊れていたのは 8888 の実公開プロセスだけだった。"
- "公開プロセスの差し替え"
- "実公開で遊ばれた記録が見える"

## open_questions

- 実公開ログの問題は、コードの仕事と運用の仕事をどう分けるのがよいか。
- この公開サーバの起動ルールを、どこまで repo の標準手順として固定するべきか。
