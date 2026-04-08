# Block Quest — コードのぼうけん

子どもが「コードを書き換えてゲームを育てる」ことを核に置いた、Pyxel製のRPG。

![Block Quest タイトル画面](assets/screenshots/title.png)

## ブラウザで遊ぶ

**▶ [いますぐ遊ぶ（GitHub Pages）](https://tatsuro-ueda.github.io/code-quest-pyxel/pyxel.html)**

ブラウザだけで動きます。インストール不要。スマホでも遊べます。

## 操作方法

| 操作 | キーボード | ゲームパッド |
|---|---|---|
| 移動 | 矢印キー | 十字キー |
| 決定 | Z / Space / Enter | B ボタン |
| キャンセル / メニュー | X / Escape | A ボタン |

戦闘・町メニュー・個人メニュー（B/X）・セーブ・ショップ など、ふつうのRPGの操作感です。

## ゲームの特徴

- **コードのぼうけん** — 主人公は「プログラマー」。敵を倒すことを「りかいする」と呼ぶ
- **5つの魔法システム** — レベルに応じて新しい呪文を覚える
- **武器・防具・道具のショップ** — 町でお金を使って装備を整える
- **やどや & セーブ** — 町に戻って休む／記録を書き留める
- **マルチフェーズのボス戦** — 複数段階の戦いに挑む
- **すべて仮名・カタカナのUI** — 漢字が読めない子どもでも一人で遊べる

## ローカルで遊ぶ

```bash
# 1. 仮想環境を用意
python -m venv .venv
source .venv/bin/activate
pip install pyxel

# 2. ゲームを起動
python main.py
```

## Pyxel Code Maker で遊ぶ・改造する

[Pyxel Code Maker](https://kitao.github.io/pyxel/wasm/code-maker.html) にアップロードする場合は、[`code-maker.zip`](code-maker.zip) を使ってください。コード全体が1つの `main.py` にインライン化されています。

```
code-maker.zip
└── block-quest/
    ├── main.py            (5,902 行・全モジュールをインライン化)
    └── my_resource.pyxres
```

## 配布物

- [`pyxel.html`](pyxel.html) — ブラウザ版（GitHub Pages で自動配信）
- [`pyxel.pyxapp`](pyxel.pyxapp) — Pyxel デスクトップ版（`pyxel run pyxel.pyxapp` で起動）
- [`code-maker.zip`](code-maker.zip) — Pyxel Code Maker アップロード用

## ドキュメント

設計と開発の経緯は `docs/` 配下にまとめています：

- [`docs/05-pyxel-code-maker-jouney.md`](docs/05-pyxel-code-maker-jouney.md) — Pyxel Code Maker と Anthropic Claude を組み合わせて子どもと作るゲームの設計原則
- [`docs/steering/`](docs/steering/) — 機能ごとのジャーニー・受け入れ条件・設計書

## ライセンス

未定（個人プロジェクト）。
