# 05 練習用プロジェクトで raw tasknotes index と area current-state を通す

- 推奨タイトル:
  - `YYYY年M月D日 練習用プロジェクトで raw tasknotes index と area current-state を通す`
- 目的:
  - `indexes` と `areas/current-state` を作る
- 入力:
  - generated summaries
  - manifests
- 完了条件:
  - `raw tasknotes index` ができている
  - area ごとの `current-state.md` ができている
- 最初の一手:
  - manifest の `moved_from` から area を推定できるか確認する
- メモ:
  - 練習用プロジェクトでは area 分けを粗くしてよい
- 委任メモ:
  - 🟢 area 粒度が粗くてよければ任せやすい
- 先に決めること:
  - manifest 代替に何を使うか

---

## code-quest-pyxel 固有メモ（2026-05-22）

### area 候補（既存の docs / tags に整合）

`product-requirements-*.md` の分け方と `closed tasknote` の prefix から自然に出る area：

| area | 関連 docs | 関連 tasknote prefix |
|---|---|---|
| `battle` | `product-requirements-battle.md` | j21, j36, j38（戦闘系） |
| `narrative` | `product-requirements-narrative.md` | j37, j42 など対話系 |
| `map` | `product-requirements-map.md` | journey 移動系 |
| `av` | `product-requirements-av.md` | sound / image 系 |
| `platform` | `product-requirements-platform.md` | g11, g12（配信系） |
| `guardrails` | `product-requirements-guardrails.md` | guardrails-1〜6, g1〜g15 |
| `code-maker` | （docs 横断） | g12, j33 など |
| `customer-journey` | `customer-journeys.md` | cj09, cj44 |

### manifest の有無

このプロジェクトには `closed tasknote` 用の manifest（`moved_from` を含むもの）は無い。
代わりに：

- `closed tasknote` の frontmatter `tags`
- 命名 prefix（`j`, `g`, `cj`, `guardrails-`）

から area を推定する。

### area 推定ロジック（暫定）

1. `tags` に上の area 名が含まれていれば、その area
2. 含まれていなければ命名 prefix で:
   - `guardrails-*` → `guardrails`
   - `g[0-9]+` → tags 補強で判定（platform / guardrails / code-maker）
   - `j[0-9]+` → tags 補強で判定（battle / narrative / map）
   - `cj[0-9]+` → `customer-journey`
3. それでも決まらないものは `unknown` に分類

### current-state.md テンプレ

```markdown
---
area: battle
last_updated: 2026-MM-DD
sources:
  - product-requirements-battle.md
  - <closed tasknotes...>
---

# {{ area }} の現状

## いまの正本

- 該当 docs と要点

## 最近の方針転換点

- closed tasknote ベース

## 未解決の open 項目

- open tasknote ベース（任意）

## 関連 area

- ...
```

### 委任時の暴走パターン

- area を細かく切りすぎる（10個以上）→ 練習段階では粗くてよい
- `current-state.md` に raw を貼り付ける → summary とリンクで足りる
