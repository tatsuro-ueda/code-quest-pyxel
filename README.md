# Block Quest — コードのぼうけん

子どもが「コードを書き換えてゲームを育てる」ことを核に置いた、Pyxel製のRPG。

> **規約に従って実装するには？**
> [AGENTS.md](AGENTS.md) (≤100 行・最優先) → [docs/architecture.md](docs/architecture.md) (人用詳細) → [docs/framework-rule.md](docs/framework-rule.md) (規約本体 M1〜M5) の順に辿ってください。


![Block Quest タイトル画面](assets/screenshots/title.png)

## ブラウザで遊ぶ

**▶ [いますぐ遊ぶ（GitHub Pages）](https://tatsuro-ueda.github.io/code-quest-pyxel/)**

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
pip install pyxel anthropic

# 2. pre-commit / post-commit hook を install（drift 検出 + top_changes.json 自動更新）
bash tools/install_hooks.sh

# 3. ゲームを起動
python main.py
```

`tools/install_hooks.sh` は 2 つの hook を `.git/hooks/` に冪等インストールします：

- **pre-commit**: `make verify`（モジュール docstring drift / CJ ↔ カスタマージャーニー / カスタマージョブ整合 / scene_to_cj 対応表）と `pytest` を走らせる。失敗すればコミットがブロックされる。緊急時は `SKIP_TESTS=1 git commit` でバイパス可能。
- **post-commit**: `tools/update_top_changes.py` が走り、Claude Haiku が「子どもに関係ある変更」を判定して `top_changes.json` の先頭に追記する。`ANTHROPIC_API_KEY` を環境変数に設定すると AI 判定が有効化される（未設定でも silent skip）。手動で `top_changes.json` を編集 → `python tools/render_top_changes.py` で kid-pixel `index.html` のマーカー間に反映できる。

CI でも同等の検証が `.github/workflows/verify.yml` で push / PR 時に走ります。

## Pyxel Code Maker で遊ぶ・改造する

[Pyxel Code Maker](https://kitao.github.io/pyxel/wasm/code-maker.html) にアップロードする場合は、[`dist/code-maker.zip`](dist/code-maker.zip) を使ってください。コード全体が1つの `main.py` にインライン化されています。

```
dist/code-maker.zip
└── block-quest/
    ├── main.py            (5,902 行・全モジュールをインライン化)
    └── my_resource.pyxres
```

## 配布物

- [`index.html`](index.html) — kid-pixel デザインのトップページ（プレイ導線 + 「あたらしくなったこと」）
- [`dist/pyxel.html`](dist/pyxel.html) — 本番ブラウザ版
- [`dist/pyxel.pyxapp`](dist/pyxel.pyxapp) — 本番デスクトップ版
- [`dist/code-maker.zip`](dist/code-maker.zip) — 本番 Code Maker アップロード用

## ドキュメント

設計と開発の経緯は次にまとめています：

- [`docs/customer-jobs.md`](docs/customer-jobs.md) — この製品で何を解決したいか
- [`docs/customer-journeys.md`](docs/customer-journeys.md) — 子どもと親にどんな体験を作るか
- [`docs/product-requirements-platform.md`](docs/product-requirements-platform.md) — 体験をどう約束し、どう確かめるか
- [`steering/`](steering/) — 機能ごとの task note と完了記録

## ライセンス

未定（個人プロジェクト）。
