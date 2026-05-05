---
status: open
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:45:00+09:00
dateModified: 2026-05-05T17:45:00+09:00
tags:
  - task
  - framework-rule
  - m1-1
  - services
  - ui
  - cleanup
---

# 2026年5月5日 services/ui レイヤーの Pyxel 描画ポリシー確定（M1-1 判断待ち統合）

> 状態：① Journey 略式（`steering/20260425-autonomous-rule-compliance-loop.md` 判断待ちリスト 4 件を統合起票）
> 分離元：autonomous-rule-compliance-loop.md の以下 4 エントリ
> - 2026-04-25 15:15 `image_banks.py` 全体（13 pyxel 違反）
> - 2026-04-25 15:20 `message_display.py` 全体（7 pyxel 違反）
> - 2026-04-25 15:25 `vfx.py` 全体（1 pyxel 違反）
> - 2026-04-25 16:05 `status_bar.py` 全体（5 pyxel 違反）

---

## 1) Journey

- **深層的目的**：`services/` と `shared/ui/` で残る pyxel 直呼び 26 件を「規約改訂」「物理移動」「DI 化」のいずれかで解消し、framework-rule.md M1-1 が「実装に追いついている」状態にする
- **やらないこと**：
  - audio_system.py の 24 件（既に Audio ラッパで M1-1 例外規定に該当、別途確認のみで触らない）
  - scenes/ の M1-1 違反（既に compliance 完了 0 件）
  - 本日 (2026-05-05) の `framework-rule.md` M1 改訂は「Model からの読み取り系」に閉じている。本タスクは「Service / shared/ui の描画」を扱う

## 2) Gherkin

### シナリオ1：image_banks.py の 13 件
> 🧱 Given: `image_banks.py` に `pyxel.load / save / images / tilemaps` の参照 13 件。🎬 When: M4-2 改訂版（本日 2026-05-05：ImageBanks は **書き込み・初期化のみ**）に照らす。✅ Then: 全件 M4-2 例外規定の範囲内（pyxres 永続化と image bank 初期化の責務）に収まる。M1-1 例外規定に「Resource ラッパ」を追記すれば violation 解消。

### シナリオ2：message_display.py の 7 件 / vfx.py の 1 件 / status_bar.py の 5 件
> 🧱 Given: 描画機能を持つ services / shared/ui ファイル 3 本、合計 13 違反。🎬 When: 「(C) shared/ui への物理移動」もしくは「(B) M1-1 例外に Text-rendering / VFX / UI-bar ラッパを追記」のどちらを採るかを決める。✅ Then: 全件 M1-1 違反 0 件、`grep -nE 'pyxel\.(blt|bltm|text|line|rect|...)' src/shared/services/*.py` の出力が「Audio ラッパのみ」になる。

### シナリオ3：framework-rule.md M1-1 検証 grep の整合
> 🧱 Given: 改訂後の framework-rule.md と test_cjg_framework_rule_guards.py。🎬 When: 検証 grep を実行。✅ Then: `services/` と `shared/ui/` のうち例外に該当する範囲だけが grep から除外され、新規違反は 0 件。

## 3) Design

### 個別方針候補
- **image_banks.py**：M4-2 改訂で「書き込み・初期化のみ」と既に明文化済。M1-1 にも「Resource ラッパ（`pyxel.load / save`、image bank 初期化）」を追記して許容
- **message_display.py**：61 箇所からの `game.messages.text(...)` 呼び出しを壊さない案として、(C) `shared/ui/text_renderer.py` に `text()` だけ抽出するのが筋。state 管理は services に残す
- **vfx.py**：1 件だけなので、(C) `shared/ui/vfx_overlay.py` に物理移動が安価
- **status_bar.py**：既に `shared/ui/` にあるので、framework-rule M1-1 に「ui/ ディレクトリは views と同等」を明記すれば違反でなくなる

### 関連スキル
- 標準ツール：Bash / Edit / Grep / pytest

### 委任度
🟡 中：物理移動が複数ファイルに波及する。docs 改訂の文言はユーザー確認が望ましい

## 4) Tasklist

（着手時に詳細化）

- [ ] image_banks.py：M1-1 例外規定追記（docs/framework-rule.md）
- [ ] message_display.py：text() を shared/ui/text_renderer.py へ抽出
- [ ] vfx.py：shared/ui/vfx_overlay.py へ物理移動
- [ ] status_bar.py：framework-rule.md M1-1 に「ui/ は views と同等」を明記
- [ ] test_cjg_framework_rule_guards.py：services / ui の例外を grep から正しく除外
- [ ] pytest 全 green
- [ ] autonomous-rule-compliance-loop.md の該当 4 エントリを「→ 本ノートに分離」更新

## 5) Result / 6) Discussion

（着手時に追記）
