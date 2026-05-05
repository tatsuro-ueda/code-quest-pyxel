---
status: open
priority: normal
scheduled: 2026-05-06T00:00:00.000+09:00
dateCreated: 2026-05-05T23:30:00.000+09:00
dateModified: 2026-05-05T23:30:00.000+09:00
tags:
  - task
---

# 2026年5月5日 TILE_WATER2 / tile_bank_water2 削除と view_model docstring の stale 記述更新

> 状態：① Journey 起票完了、ユーザー承認待ち
> 次のゲート：（ユーザー）Journey/Gherkin/Design/Tasklist の妥当性を確認 →「実装」or「修正」と指示

---

## 1) Journey（どこへ行くか）

- **深層的目的**：「動いていない描画コード」を 0 に近づける
- **やらないこと**：runtime の描画方式変更／pyxres の中身編集／path_variant・shore_variant の整理（別タスク）

### Before（現状）

- 😕 `TILE_WATER2`（`src/shared/constants/tile_data.py:60`、16×16 の波模様タイル）と `tile_bank_water2`（`src/shared/services/image_banks.py:58,123,124,282,307`）が **runtime ホットパスで一切使われない**。
- 😕 過去には水アニメ（frame_count で 2 フレーム交互描画）として動いていたと推測されるが、**A 案（2026-05-05、`pyxel.bltm` 1 回呼び）で動的タイル合成が消えた時点で死コード化**。`grep -rn "frame_count.*water\|water.*frame_count"` は 0 件。
- 😕 `image_banks.tile_iter()` は今も `("water2", "water2", M.TILE_WATER2)` を yield し、`paint_tile_bank` がこの 16×16 を image bank 0 の特定スロットに焼いている。pyxres 不在時 fallback でしか走らないが、コード上は「使う前提」に見えてしまう。
- 😕 `src/scenes/explore/view_model.py:7` の docstring に「タイル境界判定や地形 variant の解決はランタイム計算量が大きいので **view 内のループに残す**」と書かれているが、**A 案で view 内ループは撤去済**。stale 記述。
- 😕 test 2 ファイルで `tile_bank_water2 = None` を防御的に書いているが、削除すれば不要になる。
- ⚠ **リスク**：`tile_iter` から water2 を抜くと、image bank 0 のレイアウトが path_variant 以降 1 マス左にシフトする。`pyxel.tilemaps[0]` に保存されている pixel 座標は古いレイアウト基準なので、レイアウトが変わると tilemap の絵が崩れる（ユーザーが Code Maker で配置したパスの絵が水になる等）。**コード削除と pyxres 再 bake はセット**で行う必要がある。

### After（達成状態）

- 🙂 `TILE_WATER2` 定数 / `tile_bank_water2` フィールド / `tile_iter` の water2 yield / `layout_tile_bank` の water2 分岐 / `build_reverse_tile_map` の water2 登録、すべて削除。
- 🙂 test 2 ファイルから `tile_bank_water2 = None` 行を削除。
- 🙂 `view_model.py` の docstring を A 案後の現状に書き換え（「bltm 1 回呼びで一気に貼る」「variant 解決は撤去済」）。
- 🙂 `assets/blockquest.pyxres` を新レイアウトで再 bake（既存 path_variant の絵が 1 マス左にシフトするので、pyxres image bank 0 を作り直す）。`tools/probe_codemaker_layout.py` 等で再 bake が必要。
- 🙂 `make build` 後の `production/code-maker.zip` 内の `my_resource.pyxres` も新レイアウトで一致。
- 🙂 `pytest test/ -q` 全緑（718 passed 維持）。

---

## 2) Gherkin（完了条件）

### シナリオ 1：dead code が消える

- 🧱 Given：実装後の repo
- 🎬 When：`grep -rnE "TILE_WATER2|tile_bank_water2|water2" src/ test/ tools/ --include='*.py'` を実行
- ✅ Then：マッチ 0 件。

### シナリオ 2：view_model docstring が現状と一致する

- 🧱 Given：実装後の `src/scenes/explore/view_model.py`
- 🎬 When：先頭 docstring を読む
- ✅ Then：「view 内のループ」記述がなく、「`pyxel.bltm` 1 回呼び」「variant 解決は撤去済」が明記されている。

### シナリオ 3：runtime の見た目が変わらない（リスク確認の本丸）

- 🧱 Given：作業前の `assets/blockquest.pyxres` と作業後の再 bake 版
- 🎬 When：`python tools/probe_tilemap_ssot.py`（または等価の検証スクリプト）で `pyxel.tilemaps[0]` を読み出して比較
- ✅ Then：world マップ（道・水・木・装飾）の **見た目が一致**。path / shore variant が「1 マスズレて water になっている」ような崩れがゼロ。

### シナリオ 4：テストが緑のまま

- 🧱 Given：作業前 `pytest test/ -q` = 718 passed
- 🎬 When：削除 + 再 bake 後
- ✅ Then：718 passed 維持（test 内の `tile_bank_water2 = None` 削除分は test 数に影響しない）。

### シナリオ 5：本番配布が壊れない

- 🧱 Given：実装後
- 🎬 When：`make build`
- ✅ Then：`production/pyxel.html / pyxel.pyxapp / code-maker.zip` が再生成され、`code-maker.zip` 内の `my_resource.pyxres` が新レイアウトで矛盾なし（zip を解凍して Pyxel Code Maker で開いて崩れない、目視確認）。

### シナリオ 6：再侵入を防ぐ（リスク確認）

- 🧱 Given：将来「水アニメを復活したい」と思った開発者
- 🎬 When：`tile_iter` に新しい water 系 yield を追加する
- ✅ Then：`tile_id_by_pixel` の構築規約と `regenerate_world_tilemap_fallback` の variant 焼き戻し規約に従って **正規ルートで足す**ことが可能。本タスクで削除するのは「未使用の残骸」だけで、新規追加経路を塞がない。

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：Read / Edit / Bash / pytest。Pyxel Code Maker での目視確認は人作業（CC では再現性のない部分）。

### 構成図

```text
インプット                                処理                              アウトプット
─────────                                ─────                             ─────────
src/shared/constants/tile_data.py    ┐                                  ┌→ TILE_WATER2 削除
src/shared/services/image_banks.py   ├→ 死コード削除 → pyxres 再bake → ├→ tile_bank_water2 等削除
src/scenes/explore/view_model.py     │   pytest 緑 → make build → 目視  ├→ docstring 更新
test/test_world_map_ssot.py          │                                   ├→ tile_bank_water2=None 削除
test/test_tilemap_editor_truth.py    ┘                                   ├→ assets/blockquest.pyxres 再生成
                                                                          └→ production/code-maker.zip 再生成
```

### 削除対象詳細

| 削除対象 | 場所 | 影響 |
|---|---|---|
| `TILE_WATER2 = [...]` 17 行 | `src/shared/constants/tile_data.py:60-78` | 定数定義消失 |
| `tile_bank_water2: object \| None = None` フィールド | `src/shared/services/image_banks.py:58` | dataclass field 1 つ減 |
| `if self.tile_bank_water2: ... self.tile_id_by_pixel[...] = M.T_WATER` | 同上 L123-124 | reverse-lookup 1 entry 減 |
| `yield ("water2", "water2", M.TILE_WATER2)` | 同上 L282 | image bank layout から 1 slot 減 |
| `elif kind == "water2": self.tile_bank_water2 = (bx, by)` | 同上 L306-307 | 同上の処理分岐削除 |
| `ib.tile_bank_water2 = None` | `test/test_world_map_ssot.py:111` | 防御的初期化を削除 |
| `game.image_banks.tile_bank_water2 = None` | `test/test_tilemap_editor_truth.py:109` | 同上 |
| view_model docstring stale 記述 | `src/scenes/explore/view_model.py:6-7` | 記述置換 |

### 再 bake 戦略（リスク対応）

`tile_iter` から water2 を抜くと、**`paint_tile_bank` で焼かれる image bank 0 のスロット位置が water2 以降の path/shore variant について 1 マス左にシフト**する。pyxres tilemap[0] に保存されている `(tu, tv)` は古いレイアウト基準なので、絵がズレる。

対処：

1. **コード削除を先に commit**（pyxres は触らず）。
2. **`assets/blockquest.pyxres` を一旦削除**して `python main.py` を起動（または等価の bake 専用スクリプト）。`ImageBanks.setup_world_tilemap` の `pyxres_loaded == False` 経路で `paint_tile_bank` が新レイアウトで image bank を焼き、`regenerate_world_tilemap_fallback` が tilemap も新レイアウト基準で焼き直し、`pyxel.save` で **新生 pyxres を作成**する。
3. **目視確認**：Pyxel Code Maker で新 pyxres を開き、image bank 0 / tilemap 0 が崩れていないかを確認。
4. **`make build` で `production/code-maker.zip` を再生成** → zip 内の `my_resource.pyxres` も新レイアウトに更新。
5. **`assets/blockquest.pyxres` の再 bake コミット**を別 commit に分離（コードレビューしやすさのため）。

### 手順フロー

1. **影響範囲の最終 grep**（`TILE_WATER2 / tile_bank_water2 / water2`）→ 想定 5 ファイル。
2. **コード削除 commit**：tile_data.py / image_banks.py / view_model.py / 2 test ファイルから一括削除、`pytest test/ -q` 緑確認、commit。
3. **pyxres 再 bake commit**：`assets/blockquest.pyxres` を削除して `python main.py` を一度起動 → 新 pyxres 生成 → 起動・終了 → 目視確認（Pyxel Code Maker で開く）→ 新 pyxres を commit。
4. **build 再生成 commit**：`make build` → `production/code-maker.zip` / `pyxel.pyxapp` / `pyxel.html` 再生成 → commit。
5. **Result / Discussion 記入** → steering/done/ へ移動。

### リスクと対処

| リスク | 対処 |
|---|---|
| 再 bake で path/shore variant の絵が崩れる | `python main.py` 起動 → Pyxel Code Maker で image bank 目視確認 |
| 既存ユーザー（pyxres を Code Maker で編集中の人）の編集が崩れる | この pyxres は repo 同梱版で「初期状態」。本タスクで再 bake する → 配布物が更新される。ユーザーローカルの編集物は再ダウンロードが必要（README に追記するか別タスク） |
| pyxres を消した状態で起動が壊れる | `regenerate_world_tilemap_fallback` が動くはず（`world_map_ssot` 関連 test で fallback 経路は緑） |
| tile_id_by_pixel から water2 を抜いた結果、Code Maker で water2 を「使ってしまった」既存マップが grass 扱いになる | 該当する pyxres エントリは現 repo の pyxres には無いはず（grep 確認）。配布後にユーザーが water2 を Code Maker で置く可能性は新レイアウトでは無くなる（image bank に水のグラフィックが 1 種だけになるため） |

### ゲート

- ユーザー承認待ち。承認後は途中で止めずに完走可。

---

## 4) Tasklist

> 上から順に実施。CC が CoVe で自力検証しながら進める。

- [ ] （CC）影響範囲の最終 grep（`TILE_WATER2 / tile_bank_water2 / water2`）
- [ ] （CC）`src/shared/constants/tile_data.py` から `TILE_WATER2` 定義削除
- [ ] （CC）`src/shared/services/image_banks.py` から water2 関連 5 箇所（field / build_reverse_tile_map / tile_iter / layout_tile_bank の各分岐）削除
- [ ] （CC）`src/scenes/explore/view_model.py` の docstring を A 案後の状態に更新
- [ ] （CC）`test/test_world_map_ssot.py` / `test/test_tilemap_editor_truth.py` から `tile_bank_water2 = None` 行削除
- [ ] （CC）`pytest test/ -q` 全緑確認（718 passed 維持）
- [ ] （CC）コード削除を commit（pyxres は触らない）
- [ ] （CC）`assets/blockquest.pyxres` を削除し `python main.py` を一度起動 → 新 pyxres を生成（fallback 経路を意図的に踏む）
- [ ] （ユーザー）Pyxel Code Maker で新 pyxres を開き、image bank 0 / tilemap 0 の見た目を目視確認
- [ ] （CC）目視 OK 後、新 pyxres を commit
- [ ] （CC）`make build` で `production/` 配布物を再生成 → commit
- [ ] （CC）`git push origin main`
- [ ] （CC）Result セクションに作業ログ、Discussion に保留点・要約を記入
- [ ] （CC）steering/done/ へ移動

### 作業記録

> Observe → Think → Act を刻む。

#### 2026-05-05 23:30（起票）

**Observe**：先の調査で「`pyxel.bltm` は 1 か所のみ」と「shared/services にマップ系コードが大量に残る」のギャップを整理した結果、`TILE_WATER2 / tile_bank_water2` を真の dead code 候補として特定した。view_model docstring も A 案後 stale。
**Think**：単純削除に見えて、`tile_iter` からの除去で image bank 0 のレイアウトが path/shore variant 1 マス左にシフトするため、pyxres の再 bake が必要。「即やれる」と紹介したが、実際は 3 commit（コード削除 / pyxres 再生成 / build 再生成）で進める。コード自体の削除行数は 25 行程度。
**Act**：本タスクノートを起票し Journey/Gherkin/Design/Tasklist を書いた。リスク（レイアウトシフト）は Design セクションで明示。ユーザー承認後に実装へ進む。

---

## 5) Result（成果物）

実装後に作業ログを書く。

---

## 6) Discussion（反省）

実装後に保留点・指針・要約を書く。

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：
