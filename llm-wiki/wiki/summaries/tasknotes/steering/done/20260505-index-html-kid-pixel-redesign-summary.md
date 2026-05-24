---
source: raw/tasknotes/steering/done/20260505-index-html-kid-pixel-redesign.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 index.html を子ども向けピクセルアート系に再デザイン Summary Draft

## summary

この note は、`index.html` を子ども向けピクセルアート導線へ全面再デザインした実装記録です。`title.png` を主役にしたビジュアル刷新を 1 ファイル内で完結させつつ、既存の Code Maker / 外部リンク導線は壊さずに残しています。

## key_points

- `index.html` を 111 行から 649 行へ書き直し、ピクセルフォント、グラデ背景、ドットパターン、lightbox を追加した。
- 実画像追加が難しい制約を受け、SVG ピクセル装飾と `title.png` の見せ方で子ども向けの空気を作った。
- Code Maker 連携や外部リンク処理には手を入れず、見た目変更に機能リスクを持ち込まない方針を守った。

## important_quotes

- "`子ども本人 × ピクセルアート系`"
- "`機能リスクゼロ`"

## open_questions

- 実機スクリーンショットをどのタイミングで assets 化し、トップページへ差し込むべきか。
- Google Fonts 依存を、オフライン配信前にローカル同梱へ切り替えるべきか。
