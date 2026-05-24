---
source: raw/tasknotes/steering/done/20260505-services-ui-pyxel-policy.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 services/ui レイヤーの Pyxel 描画ポリシー確定（M1-1 判断待ち統合） Summary Draft

## summary

この note は、services/ui レイヤーの Pyxel 描画境界を hybrid 方針で確定した実装記録です。`message_display` と `vfx` の描画ロジックを `shared/ui` へ移しつつ、resource/audio ラッパーだけを例外として残し、M1-1 を docs と guard の両方で揃えました。

## key_points

- services 内の pyxel 直呼び件数を先に数え、`shared/ui` を正規の描画許可ゾーンとして明文化した。
- `message_display.py` / `vfx.py` から `import pyxel` を外し、新しい ui helper への薄い委譲に置換した。
- `test_cjg_framework_rule_guards.py` に service draw 禁止の static guard を追加し、例外は `audio_system.py` と `image_banks.py` のみとした。

## important_quotes

- "`ハイブリッドが最小差分`"
- "`shared/ui`"

## open_questions

- `MessageDisplay.text()` の互換 API を、どのタイミングで deprecated 扱いにするべきか。
- 他の render helper も `shared/ui` 側へどこまで寄せるべきか。
