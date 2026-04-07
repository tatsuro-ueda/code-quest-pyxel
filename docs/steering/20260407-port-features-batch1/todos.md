# バッチ1: AI完全委任ゾーン #1〜#11

> **出典**: `docs/steering/todolist.md` の「優先順位（委任しやすい順）」セクションから #1〜#11 を抽出。
> **方針**: JS版 (`/home/exedev/game/index.html`) を正解として、機械的に Pyxel版へ移植する。

## 委任範囲

このバッチに含めるのは、JS版に明確な参照実装があり、AI が単独で完了させられる項目のみ。
プロフェッサー戦＋真エンディング（旧#12）以降は別バッチに切り出す。

## #1 YAMLローダ＋データスキーマ実装

- 既存の `src/simple_yaml.py` を流用
- `src/game_data.py`（新規）に `load_enemies / load_items / load_weapons / load_armors / load_spells / load_exp_table` を実装
- スキーマ検証は最低限（必須キーの存在チェック）
- `assets/` 配下の YAML ファイルへのパス解決

## #2 敵データを `assets/enemies.yaml` に全12種移植

- JS `ENEMIES` 配列をそのまま転記
  - 10ほスライム、かいてんゴブリン、ループゴースト、10かいナイト、もしガード、でなければスライム、HPカウンター、クローン忍者、無限バグ、魔王グリッチのクローン、魔王グリッチ、プロフェッサー
- 各エントリのキー: `name, sprite, hp, atk, def, agi, exp, gold, zone, category, desc`
- ボス系フラグ: `is_boss, is_professor, post_clear_only`
- spells（魔法を使う敵）も含める
- 既存 `ZONE_ENEMIES` ハードコードを `enemies.yaml` 由来に置換

## #3 武器・防具を YAML 化

- `assets/weapons.yaml` に7種（マウス〜アーキテクト）
- `assets/armors.yaml` に7種（きほんのちしき〜さいてきかのしこう）
- 各エントリ: `name, atk/def, price, buy_msg`
- 既存 `WEAPONS / ARMORS` ハードコードを置換

## #4 アイテムを YAML 化＋効果ロジック追加

- `assets/items.yaml` にJS版 4種（バグレポート、エナジードリンク、アンチウイルス、セーブポイント）
- 各エントリ: `name, type, value, price, desc`
  - type: `heal`, `mp_heal`, `cure_poison`, `warp`
- 戦闘とメニューで `cure_poison` `warp` の効果を実装
- 毒状態 (`poisoned`) の継続ダメージ処理を追加

## #5 EXPテーブル / `statsForLevel` を YAML 化

- `assets/exp_table.yaml` に MAX_LEVEL とフォーミュラパラメータ
- もしくは `src/game_data.py` 内の純粋関数として実装（YAMLは係数のみ保持）
- JS式: `expForLevel(lv) = lv===2?26: floor(10*lv^2 + 6*lv)`、`statsForLevel(lv) = {max_hp:30+lv*15, max_mp:10+lv*6, atk:5+lv*2, def:3+lv*3, agi:5+lv*2}`
- レベルアップ判定 (`_check_level_up`) で使う

## #6 `createInitialPlayer / resetGameState` のリファクタ

- `Game.__init__` 内のプレイヤーリテラルを `src/player_factory.py:create_initial_player()` に切り出す
- ゲームリセット時の状態初期化も同モジュールの `reset_game_state()` に集約
- `statsForLevel(1)` の結果を初期 HP/MP/ATK/DEF/AGI に流用

## #7 ショップ実装（武器屋・防具屋・道具屋）

- 既存の `SHOP_WIP_MSG` プレースホルダを置換
- 町ごとの在庫: `assets/shops.yaml`（JS の `SHOPS` 相当）
- `update_shop()` `draw_shop()` を新規実装
- 購入処理: gold を消費して player の inventory に追加・武器/防具を更新
- 失敗ケース（gold 不足）のメッセージ
- `INN_PRICES` 町別宿代もこの YAML に統合（JS の `INN_PRICES`）

## #8 魔法システム（5呪文）

- `assets/spells.yaml` にJS `SPELLS` を移植
  - デバッグ/プリント/ループブレイク/リファクタリング/コンパイル
- 各エントリ: `name, mp, type (heal/attack), power, desc, learn_lv`
- レベルアップ時に `learn_lv` を満たした呪文を `player["spells"]` に追加
- 戦闘メニューに「じゅもん」項目を追加 → 呪文選択 → 効果適用
- フィールドメニューにも「じゅもん」タブを追加（heal系のみ使用可）

## #9 多段階ボス（`getBossPhases` 相当）

- HP 残量に応じてボスの行動パターン/メッセージを変える
- JS `getBossPhases(enemy)` を参照
- 適用対象: 魔王グリッチ、魔王グリッチのクローン、プロフェッサー
- バトルメッセージにフェーズ移行演出

## #10 世界樹インタラクション

- JS `interactWorldTree` の挙動を移植
- ワールドマップ上の世界樹タイル（座標は JS から）に到達したら専用ダイアログ
- `player["landmarkTreeSeen"]` を立てる
- すでに見ていれば短縮メッセージ

## #11 通信塔インタラクション + 塔エピローグ

- JS `interactTower / queueTowerEpilogue` の挙動を移植
- 通信塔タイルでのダイアログ起動
- `player["landmarkTowerSeen"]` を立てる
- 塔クリア後のエピローグメッセージキュー
