---
status: done
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:45:00+09:00
dateModified: 2026-05-06T00:00:00+09:00
tags:
  - task
  - framework-rule
  - m1-1
  - services
  - ui
  - cleanup
  - archived
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

- **概要**：`services/` と `shared/ui/` で残る pyxel 直呼び 26 件を「規約改訂」「物理移動」「DI 化」のいずれかで解消し、framework-rule.md M1-1 が「実装に追いついている」状態にする
- **やらないこと**：
  - audio_system.py の 24 件（既に Audio ラッパで M1-1 例外規定に該当、別途確認のみで触らない）
  - scenes/ の M1-1 違反（既に compliance 完了 0 件）
  - 本日 (2026-05-05) の `framework-rule.md` M1 改訂は「Model からの読み取り系」に閉じている。本タスクは「Service / shared/ui の描画」を扱う

1. 💦 （開発者）機能を追加したりバグ修正したい（コードエディタ）
2. 💦 （開発者）リポジトリを眺める（コードエディタ、あなめる）
3. Before
  1. ❌ もう使っていないファイルや関数が残っている（コードエディタ）
  2. ❌ （開発者）わかりにくい
4. After
  1. ✅ もう使っていないファイルや関数が残っていない（コードエディタ）
  2. ♥️ （開発者）嬉しい

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
- 標準ツール：Bash / Edit / Grep / pytest, manage-pyxel skill, pyxel mcp

## 4) Tasklist

> 上から順に実施。CC が CoVe で自力検証しながら進める。Tasklist は `superpowers:writing-plans`
> の TDD 流（red → green → refactor）の精神で「先に検証手段を確定し、最小差分で潰す」順に並ぶ。

### Phase A：M1-1 例外規定の明文化（docs 側を実装に追いつける）

- [ ] A1. `docs/framework-rule.md` の M1-1「許可」セクションに以下を追記
  - `src/shared/services/audio_system.py`（**Audio ラッパ**：BGM/SE 再生制御。既に M4-2 で別途明記済の追認）
  - `src/shared/services/image_banks.py`（**Resource ラッパ**：pyxres ロード/保存、image bank 初期化、`pyxel.tilemaps[0]` への書き込み）
  - `src/shared/ui/`（**View と同等**：UI 描画は views の延長として `shared/ui/` 配下に置いてよい）
- [ ] A2. M1-1「禁止」セクションは現状（services の通常ファイルでは描画系禁止）を維持。
- [ ] A3. 検証 grep の例（コメント）を `services/audio_system.py` `services/image_banks.py` `shared/ui/` を除外する形に書き換え。

### Phase B：物理移動（services 側 pyxel 直呼びを 0 件にする）

- [ ] B1. `src/shared/ui/text_renderer.py` を新設し `draw_text(x, y, s, col)` を実装（`pyxel.pal + pyxel.blt + JP_FONT_LAYOUT` の glyph 描画）
- [ ] B2. `src/shared/ui/message_window.py` に `draw_message_window(x, y, w, h, lines)` と blink カーソル描画関数を追加（`pyxel.rect / rectb / frame_count`）
- [ ] B3. `src/shared/ui/message_window.py` に `draw_say_overlay(say_buffer)` を追加（`pyxel.rect` + `draw_text` の呼び出し）
- [ ] B4. `src/shared/ui/vfx_overlay.py` を新設し `draw_vfx_overlay(color)` を実装（`pyxel.rect`）
- [ ] B5. `src/shared/services/message_display.py::text / draw_window / draw_say_overlay` を新 ui 関数の薄い委譲に書き換え（state 管理は service に残す）
- [ ] B6. `src/shared/services/vfx.py::draw_overlay` を新 ui 関数の薄い委譲に書き換え（判定ロジックは service に残す）
- [ ] B7. `import pyxel` を `services/message_display.py` `services/vfx.py` から削除

### Phase C：静的 guard 追加（再侵入防止）

- [ ] C1. `test/test_cjg_framework_rule_guards.py` の `M1PyxelBoundaryTest` に
  `test_no_pyxel_draw_calls_in_shared_services_except_resource_audio` を追加
  - 対象：`src/shared/services/*.py`
  - 例外：`audio_system.py`, `image_banks.py`
- [ ] C2. shared/ui/ は **許可ディレクトリ**として guard を入れない（誤検出防止）。

### Phase D：検証 + commit

- [ ] D1. `pytest test/ -q` 緑（718 → 719 passed: C1 追加で +1 期待）
- [ ] D2. `grep -nE 'pyxel\.(blt|bltm|text|line|rect|rectb|circ|circb|cls|pset)' src/shared/services/*.py` の出力が **`audio_system.py` と `image_banks.py` のみ**
- [ ] D3. commit：`refactor(services): pyxel 描画系を shared/ui/ に物理移動し M1-1 ガード追加`
- [ ] D4. Result セクションに作業ログ、Discussion に保留点・要約を記入
- [ ] D5. ノート移動：`steering/done/` へ

## 5) Result（成果物）

### 作業記録

#### 2026-05-06 自走実装（CC）

**Observe**：4 ファイルの pyxel 直呼び実数を grep — image_banks.py 13、message_display.py 7、vfx.py 1、status_bar.py 5。`game.messages.text()` は 61+ 箇所から呼ばれているため API 互換が必須。test_cjg_framework_rule_guards.py の M1-1 guard は scenes/ のみ対象で services は未ガードだった。

**Think**：(B) M1-1 例外規定追加（image_banks / audio_system / shared/ui） + (C) message_display / vfx は描画ロジックのみ shared/ui へ物理移動して service は薄い委譲化、のハイブリッドが最小差分。services 側 API は不変なので呼び出し元 61 箇所は無修正。

**Act**：
1. `docs/framework-rule.md` M1-1 「許可」に Audio/Resource ラッパと shared/ui を追記、検証 grep 例も併記。
2. `src/shared/ui/text_renderer.py` 新設、`message_window.py` に `draw_message_window` / `draw_say_overlay` 追加、`vfx_overlay.py` 新設。`draw_text_fn` injection を入れて test での差し替えを維持。
3. `services/message_display.py` / `services/vfx.py` から `import pyxel` を削除し、内部実装を新 ui 関数の薄い委譲に置換。
4. `test_cjg_framework_rule_guards.py::M1PyxelBoundaryTest` に `test_no_pyxel_draw_calls_in_shared_services_except_resource_audio` を追加。例外は `audio_system.py` / `image_banks.py` のみ。
5. `pytest test/ -q` = **719 passed**（+1 guard）。`grep -nE 'pyxel\.(blt|...)' src/shared/services/*.py` の出力 = audio_system / image_banks のみ → Gherkin 全シナリオ達成。

---

## 6) Discussion（反省）

### 達成

- M1-1 例外規定が docs（framework-rule.md）と実装（コードと guard）で一致。次に新しい service が pyxel 描画系を呼んだら guard が即 fail する。
- `game.messages.text()` の API 互換を保ちつつ pyxel 直呼びを 0 件に圧縮。呼び出し元 61 箇所は touch 不要。
- shared/ui/ を「views と同等の描画許可ゾーン」として明文化したため、今後の HUD / overlay 追加は迷わず shared/ui/ に置ける。

### 保留点

- 当初は status_bar.py も検討対象だったが既に shared/ui/ にあるので touch 不要だった。ノートで列挙していた 26 件のうち 13 件 (status_bar 5 + image_banks 13 のうち status_bar 5 と vfx 1) は規定追加で「合法」になり、実コードを動かしたのは message_display / vfx のみ。
- `draw_text_fn` injection は test 容易性のための小さな smell。長期的には `MessageDisplay.text()` を deprecation して直接 `draw_text` を呼ぶ方が清潔だが、61 箇所の呼び出し元 migration は別タスク。

### ルール化候補

- 「pyxel 描画 API を services に書く前に framework-rule.md M1-1 の例外規定を確認する」を CLAUDE.md に追加 → 既に framework-rule.md M1-1 が SoT なので、改めての追記不要。

