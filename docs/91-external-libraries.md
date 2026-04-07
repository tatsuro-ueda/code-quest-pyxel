# 外部ライブラリ・素材

> Status: 積極的に使うこと。Pyxel本体の薄い API を補う既成資産は限られているため、
> ここに挙げたものは「自前実装に走る前にまず使えないか検討する」対象とする。

## 採用方針

- Pyxel エコシステムには rexUI / pygame_gui のような統合 UI ライブラリは存在しない（2026-04 時点で調査済み）。
- そのため、UI 部品はほぼ自前実装になるが、**周辺の補助ライブラリ・素材は積極的に取り込む**。
- 下記のリポジトリは「使えるところは必ず使う」方針とする。

## 使用対象ライブラリ・素材

### 1. pyxel-extensions（gediminasz/pyxel-extensions）
- URL: https://github.com/gediminasz/pyxel-extensions
- 内容: Pyxel ゲーム開発のヘルパー集。Redux 風のゲーム状態ストア、Scene クラス（画面遷移）、ホットモジュールリロードを提供。
- 使いどころ:
  - `state` 文字列で巨大な if 分岐になっている `update()` / `draw()` を Scene クラスに分割する候補。
  - `self.player`, `self.battle_*`, `self.msg_*` などの状態を Redux 風ストアに集約する候補。
  - 開発時のホットリロードで、`main.py` の編集→即反映を可能にする。
- 優先度: 高（状態分割は将来的に必須になる）。

### 2. PyxelUnicode（AceBee007/PyxelUnicode）
- URL: https://github.com/AceBee007/PyxelUnicode
- 内容: Unicode に対応したピクセルフォントビルダー。任意の Unicode 文字を Pyxel で扱えるフォントイメージに変換する。
- 使いどころ:
  - 現在の `assets/umplus_j10r.bdf` + `pyxel.Font` でカバーできない記号・特殊文字（♥ ★ ☆ など）の追加。
  - 多言語化を想定する場合の予備手段。
- 優先度: 中（必要が生じた時点で導入）。

### 3. Pyxel-Button-Example（Andressance/Pyxel-Button-Example）
- URL: https://github.com/Andressance/Pyxel-Button-Example
- 内容: Pyxel 用のクリック可能なボタンクラス（矩形・楕円、ホバー効果付き）のサンプル実装。pip パッケージではなく参照用コード。
- 使いどころ:
  - メニュー画面・装備画面・ショップ画面などにマウス対応を入れる場合のリファレンス。
  - 「自前で `pyxel.btnp` を散らかす」前にこのクラスを移植して使う。
- 優先度: 中（マウス UI を導入するときに参照）。

### 4. pyxel-rpg-sepack（shiromofufactory/pyxel-rpg-sepack）
- URL: https://github.com/shiromofufactory/pyxel-rpg-sepack
- 内容: Pyxel でレトロ RPG を作る際の効果音（SE）素材集。Pyxel ネイティブな形式で配布されている。
- 使いどころ:
  - メッセージ送り音、決定音、キャンセル音、ダメージ音、回復音、レベルアップ音などの差し替え。
  - 現在 BGM 中心で SE が薄い領域を補う。
- 優先度: 高（メッセージパネル改修と相性が良い：メッセージ送り音の追加）。

---

# Pyxel 以外も含む RPG 向けライブラリ調査結果

Pyxel エコシステム外も探索した結果。Pyxel に直接組み込めるかどうかを軸に整理する。

## B. タイルマップ・スクロール（Pyxel 不可・参考）

pygame Surface 前提のため Pyxel に直接持ち込めない。ただし「Tiled Map Editor で編集 → TMX を読む」という**設計思想**は採用可能。

| 名前 | URL | 内容 |
|---|---|---|
| pytmx | https://github.com/bitcraft/pytmx | Tiled の TMX を読む業界標準ローダー |
| pyscroll | https://github.com/bitcraft/pyscroll | pytmx と組むレイヤー対応スクロール描画 |

→ **優先度: 中**。Pyxel 用に自前 TMX ローダーを書く価値あり。Tiled 自体は無料の優良エディタ。

### pedre の JSON 構造のどこが参考になるか

#### 5. 起動時バリデーション
- `npcs.json` に存在しない NPC を `dialogs/*.json` から参照していたら、**起動時にエラー**になる。
- **学べる点**: 自前で JSON ローダーを書くなら「読み込み直後に整合性チェック」を入れることで、ゲーム実行中に「KeyError でクラッシュ」を防げる。これは安全装置として真似する価値が高い。

## おすすめ導入順（参考）

3. **Tiled + 自前 TMX ローダー** — マップ編集体験の改善（コストはやや高い）
