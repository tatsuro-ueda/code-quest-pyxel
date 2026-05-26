# Fixed-Width Message Wrap Design

## Goal

battle と shop の固定幅 message 枠で長文が右にはみ出す不具合を、View 層の責務を崩さずに横断修正する。

## Context

- battle では [src/scenes/battle/view.py](/home/exedev/code-quest-pyxel/.worktrees/20260526-message-wrap-sweep/src/scenes/battle/view.py:215) の main message が既に個別修正されている。
- shop では [src/scenes/shop/view.py](/home/exedev/code-quest-pyxel/.worktrees/20260526-message-wrap-sweep/src/scenes/shop/view.py:49) の下部 message が 1 行描画のまま残っている。
- 既存の折返し規約は [src/shared/services/message_display.py](/home/exedev/code-quest-pyxel/.worktrees/20260526-message-wrap-sweep/src/shared/services/message_display.py:199) の `wrap_text()` にある。

## Chosen Approach

1. View 専用の小 helper を `src/shared/ui/` に追加する。
2. helper は `text_writer.wrap_text()` を呼び、最大行数を適用するだけに留める。
3. battle と shop のように長文化しうる固定幅枠だけが opt-in で helper を使う。

## Why This Approach

- battle / shop の root cause は同じだが、すべての scene を共通 message window に寄せるのは過剰。
- helper を View 層に閉じることで、M1/M2/M3 の責務境界を崩さない。
- `text_writer.wrap_text()` を持たない test double が残っていても fallback を維持できる。

## Scope

### In

- `src/shared/ui/wrapped_text.py` の追加
- `src/scenes/battle/view.py` の main message 行解決の共通化
- `src/scenes/shop/view.py` の下部 message 複数行描画
- `test/test_cjg_battle_message_wrap.py`
- `test/test_cjg_shop_message_wrap.py`

### Out

- title / splash / menu のレイアウト変更
- `MessageDisplay.wrap_text()` のロジック変更
- message 文言の変更
- scene 遷移や state 更新の変更

## Testing Strategy

- battle: 長文は複数行、短文は従来位置のまま
- shop: 長い `buy_msg` は複数行、短文は従来位置のまま
- full regression: `python -m pytest test/ -q`
- artifact regression: `PYTHONPATH=. python tools/build_web_release.py`

## Risks and Mitigations

- `wrap_text()` を持たない test double で壊れる
  - helper で 1 行 fallback を返す
- shop の message 枠が 2 行化で既存座標と干渉する
  - 先に描画ベースの failing test を追加する
- 他 scene を過剰修正する
  - inventory の事実確認に留め、note に未適用理由を残す

## Verification Targets

- battle と shop で overflow が再現しない
- short message の表示位置が回帰しない
- build artifact 再生成が通る
