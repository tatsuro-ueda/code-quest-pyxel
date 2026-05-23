---
status: active
origin:
  - docs/framework-rule.md
last_synced: 2026-05-23
---

# Framework Checklist

`docs/framework-rule.md` の運用ルールを、開発前後に確認しやすい形へ圧縮した checklist。

## 正本と生成物

- [ ] YAML / docs / Code Maker / `.pyxres` のどれが正本かを最初に固定している
- [ ] generated や `dist` を手修正の正本にしていない

## M1 View 境界

- [ ] Pyxel 描画 API は View か最外殻だけで使っている
- [ ] 入力 API を Model / Service / Presenter に漏らしていない

## M2 ViewModel 境界

- [ ] View は ViewModel だけを見ている
- [ ] 表示用の解釈を Presenter 側で済ませている

## M3 Presenter 責務

- [ ] Presenter は入力解釈、scene 遷移、副作用指揮に留めている
- [ ] Presenter が直接描画していない

## M4 Model / State

- [ ] 新しい状態は `dataclass` で表している
- [ ] Scene local / shared / service state の置き場を明示している
- [ ] dict の残骸や dynamic 属性で状態を増やしていない

## M5 検証

- [ ] 変更に対応するテストかガードレールを追加している
- [ ] 命名や layer ルールを AI が自力で再検証できる形にしている

## done の扱い

- [ ] pytest 等の検証コマンドを実行した
- [ ] 実物確認が必要な変更では、画面や配布物まで確認した
