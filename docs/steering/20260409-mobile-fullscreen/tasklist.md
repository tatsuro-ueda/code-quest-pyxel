# タスクリスト: スマホ全画面対応

## git ルール（本タスク共通）

1. branch 作成時は `git checkout -b feature/xxx main`（ローカルのmainから切る）
2. merge 前に `git log origin/main..HEAD --oneline` で余計なコミットが混ざっていないか確認

---

## タスク

- [ ] 1. ブランチ作成: `git checkout -b feature/mobile-fullscreen main`
- [ ] 2. `templates/wrapper.html` を新規作成（HTMLラッパーテンプレート）
  - viewport meta タグ（D2相当: mobile最適化）
  - iframe#game-frame src={{PYXEL_HTML_SRC}} allowfullscreen（D1, D12）
  - button#fullscreen-btn「ぜんがめんであそぶ」（P8, D9）
  - p#fallback-msg ひらがな案内テキスト（P4, D5）
  - CSS: body黒背景、iframe全画面、ボタン下部中央半透明、フェードアウトtransition（D6, D8, D9）
  - JS: タッチ判定→API判定→ボタン/案内表示、フェードアウト5秒、余白タップ再表示、fullscreen切り替え（D3, D4, D8, D13）
- [ ] 3. `tools/build_web_release.py` を拡張
  - generate_wrapper() 関数追加（D7, D11）
  - build_web_release() の戻り値に index.html を追加
  - index.html をプロジェクトルートにコピー（D10）
- [ ] 4. ビルド実行して動作確認
  - `python tools/build_web_release.py` 実行
  - index.html が生成されること
  - index.html 内に iframe src=pyxel.html があること
  - allowfullscreen 属性があること
- [ ] 5. コミット
- [ ] 6. `git log origin/main..HEAD --oneline` で確認
