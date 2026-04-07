# 実機テスト手順

## 目的

同じ Wi-Fi にいるスマホから `pyxel.html` を開き、配布物に近い状態で操作確認を行う。

## 起動コマンド

```bash
cd /home/exedev/code-quest-pyxel
python tools/serve_pyxel_preview.py --host 0.0.0.0 --port 8000
```

起動後はターミナルに `LAN preview` の URL が表示される。スマホでは `index.html` ではなく `pyxel.html` を優先して開く。

## 前提

- PC とスマホが同じ Wi-Fi に接続されている
- PC 側のファイアウォールで指定ポートが遮断されていない
- 配布確認は `pyxel.html` を基準に行う

## 最小チェックリスト

1. タイトル画面で A を押してゲーム開始できる
2. ワールドマップで十字キーで連続移動できる
3. B でメニューを開ける
4. メッセージウィンドウで A による送りができる
5. メニューや戦闘で B によるキャンセルができる

## 入力方針

- `pyxel.html` 側の `gamepad: "enabled"` を使う
- ゲーム本体は `GAMEPAD1_BUTTON_*` とキーボード入力を同じ判定にまとめて扱う
- カスタムのブラウザ用パッドは現時点では追加しない
