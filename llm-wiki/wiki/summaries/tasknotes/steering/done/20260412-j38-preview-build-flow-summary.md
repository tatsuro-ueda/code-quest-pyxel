---
source: raw/tasknotes/steering/done/20260412-j38-preview-build-flow.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月12日 J38 preview build を current に混ぜない Summary Draft

## summary

この tasknote は、未承認の変更が `pyxel.html` 側へ混ざって子どもの比較導線を壊さないように、preview build と current build の責務を分離した記録です。実装上は `tools/build_web_release.py` の `--preview` / `--promote` と preview 専用 artifact で解決済みで、tasknote はその運用事実を仕様として整理し直しました。

## key_points

- 問題の芯は、通常 build が current 側の `pyxel.html` を更新してしまい、承認前の変更が混ざることだった。
- 方針は「通常 build は current 用に残し、preview build は `--preview` の別入口にする」だった。
- preview build は `main_preview.py` と `preview_meta.json` を専用入力にし、preview 側だけへ成果物を出す。
- `--promote preview|current` で承認・却下後の昇格と掃除を 1 か所へまとめた。
- selector から `play.html` / `play-preview.html` を経由して `pyxel.html` / `pyxel-preview.html` を辿る導線をテストで固定した。
- 最終的には、保留だった設計判断より先に実装が成立しており、done だったのは tasknote の整理だった。

## important_quotes

- "preview build と current build の役割をコード上ではっきり分ける"
- "承認後にだけ current 側へ昇格する流れ"
- "通常 build は current のまま、preview は `--preview` の別入口"

## open_questions

- `--preview` / `--promote` の親向け運用手順を README や runbook に書くか。
- `index.html` の preview 説明面を、approval flow と一緒にどこまで整備するか。
- preview/current の責務分離を今後の build 変更でも崩さない検査を追加するか。
