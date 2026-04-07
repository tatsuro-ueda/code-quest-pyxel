# 移植チェックリスト（JS版 → Pyxel版）

> **更新日**: 2026-04-07
> **元コード**: `/home/exedev/game/index.html` (3370行・148関数)
> **現コード**: `code-quest-pyxel/main.py` (2153行) + `src/` (12モジュール)
>
> JS版の機能を機能カテゴリ別にリストし、Pyxel版での実装状況を ✅/⚠️/❌ で示す。
> ⚠️ は「部分実装」「簡易版」「TODO/WIP扱い」。

---

## 凡例

- ✅ 実装済み（JS版相当の挙動が動く）
- ⚠️ 部分実装（仕様の一部のみ・簡易版・WIP）
- ❌ 未着手（やる予定）
- ❓ 保留（やる/やらないを後日決める）
- ➖ 対象外（移植しない／環境制約で実現不可）

委任しやすさの記号:

- 🤖 **AI完全委任OK** — JS版に明確な参照実装があり、機械的に再現できる。テストで自動検証可能
- 🤖🧑 **AI下書き → 人で仕上げ** — AIで一次実装は可能だが、視覚・聴覚の判断や最終確認が必要
- 🧑 **人手必須** — GUIツール操作や手作業の編集が前提

---

## 優先順位（委任しやすい順）

> **AIに連続委任する範囲**: **#1 〜 #11**（🤖印）
> 上から順に処理すれば、データ移植 → 既存ハードコードのYAML置換 → リファクタ → データ駆動の機能拡張、という依存順にも沿う。
> #12 以降は人の判断・操作を伴うため、AIスイープからは切り離す。

### 🤖 完全委任ゾーン（一気にやってOK）

| # | 項目 | 元番号 | なぜ委任しやすいか |
|---|---|---|---|
| 1 | **YAMLローダ＋データスキーマ実装** | 0 | 既存 `src/simple_yaml.py` を流用。スキーマ定義と汎用ローダだけなので機械的 |
| 2 | **敵データを `assets/enemies.yaml` に全12種移植** | 4 | JS `ENEMIES` を YAML に書き起こすだけ。検証は件数とキー一致でOK |
| 3 | **武器・防具を `weapons.yaml` / `armors.yaml` に7種ずつ移植** | 2 | 同上。`buyMsg` テキストもJSからそのまま転記 |
| 4 | **アイテムを `items.yaml` に移植 + 効果ロジック追加** | 3 | アンチウイルス・セーブポイント・毒システムをJS参照で追加 |
| 5 | **EXPテーブル/`statsForLevel` を `exp_table.yaml` 化** | （0の一部） | JSの `expForLevel/statsForLevel` をそのまま転記 |
| 6 | **`createInitialPlayer/resetGameState` のリファクタ** | 14 | リテラル散在をファクトリ関数に集約。純粋リファクタ |
| 7 | **ショップ実装**（武器屋・防具屋・道具屋） | 1 | `SHOP_WIP_MSG` を本実装に置換。JS `drawShop/tryPurchase/getItemPrice` が参照可能 |
| 8 | **魔法システム**（5呪文 + レベル習得 + MP消費） | 8 | `spells.yaml` を読んで戦闘・メニューに統合。JS `applySpellEffect/useSelectedMenuSpell` 参照 |
| 9 | **多段階ボス**（`getBossPhases` 相当） | 9 | JS にロジックあり。HP 閾値で切替える定型実装 |
| 10 | **世界樹インタラクション** | 10 | JS `interactWorldTree` + `landmarkTreeSeen` 連動をそのまま移植 |
| 11 | **通信塔インタラクション + 塔エピローグ** | 11 | JS `interactTower/queueTowerEpilogue` + `landmarkTowerSeen` を移植 |

> このあとに **プロフェッサー戦＋真エンディング**（旧#12）も続けて委任可能だが、テキスト量が多くストーリー判断が混じるため、いったん #1〜#11 が終わってから別スイープにする方が安全。

### 🤖🧑 半委任ゾーン（AI下書き → 人が確認）

| # | 項目 | 元番号 | なぜ単純委任しづらいか |
|---|---|---|---|
| 12 | **プロフェッサー戦＋真エンディング** | 12 | 量が多くストーリーテキスト判断が伴う。1スイープから分離 |
| 13 | **ランドマーク強調描画** | 7 | 「目印として目立たせる」の判断は視覚レビュー必須 |
| 14 | **SFX 21音**（`pyxel-rpg-sepack` 導入＋マッピング） | 5 | ライブラリ導入後、どの音をどの場面に当てるかは耳で確認 |
| 15 | **スプラッシュ画面** | 6 | 構図・配色の最終判断が必要 |

### 🧑 人手必須ゾーン

| # | 項目 | 元番号 | 理由 |
|---|---|---|---|
| 16 | **Tiled で全マップを編集可能化** | 13 | Tiled (GUIツール) 上での編集が前提。AIはローダ側の整備までしかできない |

### 対象外（やらない）

- 振動API
- メッセージ自動進行タイマー
- 攻撃ホールド検出
- 報告系URL（Issue/Shelley/Terminal）
- ループ・フレーム制御の細部（`_safeDraw/_sceneKey/_flushInput`）

### 保留（後日決定）

- VFX（ダメージポップアップ・パーティクル）

---

## 進め方のアドバイス

- **1機能 = 1コミット = 1テスト追加** を徹底する
- 各機能の完了基準を「JS版で動いていた挙動が Pyxel版でも再現できる」に置く
- ✅/⚠️/❌/❓/➖ をこのファイル内のカテゴリ別表で更新しながら進める
- AIスイープ時は #1 → #11 を順に実行し、各 # の完了時に必ず `pytest test/` をパスさせる
- #1〜#5（データ系）が終わると、#7〜#11 はほぼデータ参照＋ロジック追加になり、進捗が加速する

---

## 1. 入力系

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| キーボード入力 | `pressKey/releaseKey/getKey` | `src/input_bindings.py` | ✅ | |
| ゲームパッド | `initGamepad` | `src/input_bindings.py` | ✅ | Pyxel側で抽象化 |
| タッチ仮想パッド | `setupTouch` | （対応済み） | ✅ | |
| 振動 | `haptic` | — | ➖ | スマホでの振動APIアクセスは現状不可のため対象外 |

---

## 2. オーディオ系

### 2.1 BGM

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| BGMシーン選択 | `updateBGM` | `src/audio_system.py:choose_bgm_scene` | ✅ | |
| BGM再生切替 | `playBGM/stopBGM` | `AudioManager.play_scene` | ✅ | |
| 楽曲データ | `BGM_WAV` (登録式) | `src/chiptune_tracks.py` | ✅ | チップチューン版は4ch直書き |
| ボス戦・エンディング等のシーン | 11シーン (zone1-3, dungeon, battle, boss1-2, city, victory, endroll, top) | 同等のキー | ✅ | |

### 2.2 SFX（効果音）

JS版には28個の `sfx*` 関数があり、Pyxel版では未実装。

> **方針**: `pyxel-rpg-sepack` (`shiromofufactory/pyxel-rpg-sepack`) を採用する予定。
> 自前で `sfx*` 関数を再実装するのではなく、ライブラリの音色セットから適切なSEを割り当てる方向で進める。
> `docs/91-external-libraries.md` および `docs/85-sfx-design.md` 参照。

| 機能 | JS関数 | Pyxel版 | 状態 |
|---|---|---|---|
| 攻撃 | `sfxAttack` | — | ❌ |
| 被弾 | `sfxHit` | — | ❌ |
| 魔法 | `sfxMagic` | — | ❌ |
| 回復 | `sfxHeal` | — | ❌ |
| レベルアップ | `sfxLevelUp` | — | ❌ |
| 勝利 | `sfxVictory` | — | ❌ |
| 死亡 | `sfxDead` | — | ❌ |
| カーソル | `sfxCursor` | — | ❌ |
| 決定 | `sfxSelect` | — | ❌ |
| 戦闘開始 | `sfxBattle` | — | ❌ |
| ミス | `sfxMiss` | — | ❌ |
| 足音（タイル別） | `sfxStep` | — | ❌ |
| 毒/治毒 | `sfxPoison/sfxCure/sfxPoisonTick` | — | ❌ |
| セーブ | `sfxSave` | — | ❌ |
| ダンジョン入場 | `sfxDungeonIn` | — | ❌ |
| ボス遭遇/撃破 | `sfxBossApproach/sfxBossDefeat` | — | ❌ |
| クリティカル | `sfxCritical` | — | ❌ |
| ゾーン変化 | `sfxZoneChange` | — | ❌ |
| 購入/失敗 | `sfxPurchase/sfxPurchaseFail` | — | ❌ |
| 宿屋 | `sfxInn` | — | ❌ |
| 町入場 | `sfxEnterTown` | — | ❌ |

**全体**: ❌ 21SE 全て未実装

---

## 3. ビジュアルエフェクト

> **方針**: 現時点でノープラン。やる/やらないを後日決める保留枠。

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| ダメージポップアップ | `addPopup` / `gfx.popups` | — | ❓ | 保留 |
| パーティクルバースト | `addParticleBurst` / `gfx.particles` | — | ❓ | 保留 |
| GFX更新 | `updateGfx` | — | ❓ | 保留 |
| GFX描画 | `drawGfx` | — | ❓ | 保留 |

---

## 4. マップ生成

> **方針**: 最終的には Tiled (TMX) でマップを編集できる状態にする（微修正のため）。
> 現在は手続き生成 (`generate_world_map/generate_dungeon`) と TMX読込 (`src/tiled_loader.py`) が併存。
> 既存ステアリング: `docs/steering/20260406-TiledMapEditor/`

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| ワールドマップ生成 | （複数関数: `forest/lake/sand/mtn/clearAround/carveWindingPath/generateDecorations`） | `generate_world_map` (`main.py:877`) | ✅ |
| ダンジョン生成 | `carveDungeon` | `generate_dungeon` (`main.py:924`) | ✅ |
| パスバリアント | — | `get_path_variant` (`main.py:570`) | ✅ |
| 海岸バリアント | — | `get_shore_variant` (`main.py:586`) | ✅ |
| ゾーン判定 | — | `get_zone` (`main.py:960`) | ✅ |
| Tiled (TMX) 読込 | — | `src/tiled_loader.py` + `src/map_registry.py` | ⚠️ |
| Tiled で全マップを編集可能にする | — | — | ❌ |

---

## 5. 描画

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| マップ描画 | `drawMap` | `Game.draw_map` | ✅ | |
| タイル描画 | `drawTile` | `_render_tiles_to_bank` | ✅ | バンク描画 |
| 主人公描画 | `drawHero` | `_render_sprites_to_bank` | ✅ | |
| 装飾描画 | `drawDeco` | （バンクに含む） | ✅ | |
| ランドマーク強調描画 | `drawLandmarks` | — | ❌ | 強調描画は未実装。世界樹・通信塔などを目印として描き分ける必要あり |
| ステータスバー | （drawMap内） | `draw_status_bar` | ✅ | |
| DQ風ウィンドウ | `drawDQWindow` | `draw_message_window` | ✅ | |
| テキスト描画 | `drawText` | `pyxel.Font` (`umplus_j10r.bdf`) | ✅ | |
| スプラッシュ | `drawSplash` | — | ❌ | |
| タイトル | `drawTitle` | `Game.draw_title` | ✅ | |

---

## 6. メッセージ／ダイアログ

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| 単発メッセージ | `showMsg` | `Game.show_message` | ✅ |
| 連続メッセージキュー | `queueMessages/nextMsg` | `Game._enter_message` | ✅ |
| メッセージ描画 | `drawMsg` | `draw_message_window` | ✅ |
| 構造化ダイアログ | （main.pyに直書き） | `src/structured_dialog.py` + `assets/dialogue.yaml` | ✅ |

---

## 7. プレイヤー／ステータス

> **方針**: EXPテーブル・敵・アイテム・スキルなどのゲームデータは
> `assets/` 配下の YAML ファイルとして外部化する。コードはローダーとロジックだけを持つ。

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| 初期プレイヤー生成 | `createInitialPlayer` | `Game.__init__` 内のリテラル | ⚠️ | ファクトリ関数化＋YAML化したい |
| EXPテーブル (YAML) | `expForLevel` | — | ❌ | `assets/exp_table.yaml` 等 |
| ステータス計算 | `statsForLevel` | — | ❌ | |
| ゲーム状態リセット | `resetGameState` | — | ⚠️ | 個別に再初期化 |
| レベルアップ処理 | `processLevelUp` | `Game._check_level_up` | ✅ | |
| 装備合計ATK/DEF | `playerTotalAtk/Def` | `_do_player_attack/_do_enemy_attack` 内 | ✅ | |

---

## 8. エンカウント

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| ゾーン判定 | `getEnemyZone` | `get_zone` | ✅ |
| 敵プール取得 | `getEncounterPool` | `ZONE_ENEMIES` (`main.py:970`) | ✅ |
| エンカウント発生 | `checkEncounter` | `Game.update_map` 内 | ✅ |
| ボス判定 | `isBossLike` | `is_boss` フラグで対応 | ✅ |
| プロフェッサー戦予約 | `queueProfessorEncounter` | — | ❌ | やる |
| プロフェッサー後日談 | `queueProfessorEpilogue` | — | ❌ | やる |

---

## 9. バトル

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| 戦闘開始 | `startBattle` | `Game._start_battle` | ✅ | |
| 戦闘UI | `drawBattle` | `Game.draw_battle` | ✅ | |
| 敵スプライト | `drawEnemySprite` | スプライトバンク経由 | ✅ | |
| 戦闘背景 | `drawBattleBg` | `draw_battle` 内 | ✅ | |
| ダメージ計算 | `calcDamage` | `_do_player_attack/_do_enemy_attack` 内 | ✅ | |
| プレイヤーターン入力 | `processBattleInput` | `update_battle` | ✅ | |
| 敵ターン | `enemyTurn` | `_do_enemy_attack` | ✅ | |
| 勝利処理 | `processVictory` | `_battle_victory` | ✅ | |
| 敗北処理 | `processDefeat` | `_battle_defeat` | ✅ | |
| ボスフェーズ | `getBossPhases` | — | ❌ | 多段階ボス（やる） |
| メッセージ自動進行タイマー | `updateBattleMessageTimer` | — | ➖ | 不要（手動進行のみ） |
| 「攻撃ホールド」検出 | `isBattleAdvanceHeld/clearBattleAdvanceHold` | — | ➖ | 不要 |

---

## 10. アイテム / 魔法 / 装備

> **方針**: アイテム・スキル（魔法）・武器・防具のデータは `assets/` 配下の YAML に外部化する。
> 例: `assets/items.yaml` `assets/spells.yaml` `assets/weapons.yaml` `assets/armors.yaml`。
> コード側は構造化ローダ（`src/structured_dialog.py` のような）を1つ用意してそれぞれを読む。

### 10.1 アイテム

| 種類 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| バグレポート (HP30回復) | ✅ | ✅ (`ITEMS[0]`) | ✅ |
| エナジードリンク (MP20回復) | ✅ | ✅ | ✅ |
| アンチウイルス (毒治癒) | ✅ | — | ❌ |
| セーブポイント (ワープ) | ✅ | — | ❌ |
| 毒状態のシステム自体 | ✅ (`canPoison`, poison tick) | — | ❌ |

### 10.2 魔法（SPELLS）

JS版には5つの呪文（デバッグ/プリント/ループブレイク/リファクタリング/コンパイル）があり、レベル習得制。**Pyxel版は `spells: []` で完全未実装**。

| 機能 | 状態 |
|---|---|
| 魔法定義 (SPELLS配列) | ❌ |
| 戦闘で魔法を使う | ❌ |
| メニューから魔法を使う | ❌ |
| レベルアップで習得 | ❌ |
| MP消費 | ❌ |

**全体**: ❌

### 10.3 装備（武器・防具）

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| 武器/防具データ | 7種類ずつ・価格・購入メッセージ | 数種・価格なし | ⚠️ |
| 装備変更 | ショップで購入→装備 | メニューでサイクル切替（デバッグ風） | ⚠️ |
| 装備購入メッセージ | `buyMsg` 文学テキスト | — | ❌ |

---

## 11. 町 / ショップ / 宿屋

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| 町進入 | `enterTown` | `update_town/update_town_menu` | ✅ | |
| 町メニュー描画 | `drawTownMenu` | `draw_town_menu` | ✅ | |
| 町メニューUI | はなす/武器屋/防具屋/道具屋/宿屋/セーブ/出る | はなす/宿屋/セーブ/出る + ショップ系は `SHOP_WIP_MSG` | ⚠️ | **武器屋・防具屋・道具屋が「工事中」プレースホルダ** |
| ショップ描画 | `drawShop` | — | ❌ |
| ショップ購入 | `tryPurchase` | — | ❌ |
| アイテム価格取得 | `getItemPrice` | — | ❌ |
| 宿屋 | `tryInn` | `_town_menu_inn` | ✅ |
| NPC会話 | `NPCS[townIdx][i]` | dialogue.yaml + `_town_menu_talk` | ✅ |
| 町ごとの在庫 (`SHOPS`) | ✅ | — | ❌ |
| 宿代テーブル (`INN_PRICES`) | 5/15/40 (町ごと) | `INN_COST=10` 固定 | ⚠️ |

---

## 12. 城 / ダンジョン / ランドマーク

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| 城進入 | `enterCastle` | `_check_tile_events` で `castle.professor.entry` トリガ | ⚠️ | 城内のフロー未実装 |
| ダンジョン進入 | `enterDungeon` | `_check_tile_events` 内 | ✅ | |
| ダンジョン退出 | `handleDungeonExit` | `update_map` 内 | ✅ | |
| 世界樹インタラクション | `interactWorldTree` | — | ❌ | やる。`landmarkTreeSeen` 連動 |
| 通信塔インタラクション | `interactTower` | — | ❌ | やる。`landmarkTowerSeen` 連動 |
| 塔エピローグ | `queueTowerEpilogue` | — | ❌ | やる |
| ランドマーク汎用イベント | — | `src/landmark_events.py` + `find_landmark_event` | ✅ | 汎用機構はあるが個別イベント未登録 |

---

## 13. セーブ / ロード

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| セーブ | `saveGame` | `src/save_store.py` (Local/File/Memory) | ✅ |
| ロード | `loadGame` | 同上 | ✅ |
| プレイヤー状態のシリアライズ | （直接JSON化） | `src/player_snapshot.py:dump_snapshot/restore_snapshot` | ✅ |

---

## 14. タイトル / エンディング

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| スプラッシュ画面 | `drawSplash` | — | ❌ |
| タイトル描画 | `drawTitle` | `draw_title` | ✅ |
| タイトル入力 | `processTitleInput` | `update_title` | ✅ |
| 通常エンディング進入 | `enterEnding` | `_enter_ending` | ✅ |
| 通常エンディング描画 | `drawEnding` | `draw_ending` | ✅ |
| 通常エンディング完了 | `completeEnding` | `update_ending` | ✅ |
| プロフェッサーエンディング進入 | `enterProfessorEnding` | — | ❌ | やる |
| プロフェッサーエンディング描画 | `drawProfessorEnding` | — | ❌ | やる |
| プロフェッサーエンディング完了 | `completeProfessorEnding` | — | ❌ | やる |

---

## 15. メニュー（フィールド）

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| メニュー状態生成 | `createMenuState` | `Game.__init__` 内 | ⚠️ |
| タブ取得/移動 | `getMenuTab/moveMenuTab` | `update_menu` 内 | ✅ |
| カーソル移動 | `moveMenuCursor` | 同 | ✅ |
| アイテム使用 | `useSelectedMenuItem` | 同 | ✅ |
| 魔法使用 | `useSelectedMenuSpell` | — | ❌ |
| メニュー描画 | `drawMenu` | `draw_menu` | ✅ |
| 入力処理 | `processMenuInput` | `update_menu` | ✅ |

---

## 16. 報告 / 外部リンク（バグレポート連携）

> **方針**: 移植しない（対象外）。

| 機能 | JS関数 | 状態 |
|---|---|---|
| 報告コンテキスト構築 | `buildReportContext` | ➖ |
| Issue URL生成 | `buildIssueUrl` | ➖ |
| Shelley URL生成 | `buildShelleyUrl` | ➖ |
| Terminal URL生成 | `buildTerminalUrl` | ➖ |
| 外部リンクオープン | `openExternal` | ➖ |

---

## 17. ゲームループ／フレーム制御

> **方針**: 移植しない（対象外）。Pyxel側の `pyxel.run` で十分。

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| update | `update(dt)` | `Game.update` | ✅ |
| render | `render` | `Game.draw` | ✅ |
| メインループ | `gameLoop(time)` | `pyxel.run` | ✅ |
| 例外セーフな描画 | `_safeDraw` | — | ➖ |
| シーンキー（リセット用） | `_sceneKey` | — | ➖ |
| 入力フラッシュ | `_flushInput` | — | ➖ |

---

## 18. 敵データ充足度

> **方針**: JS版 12種類の敵を**全部移し切る**。データは `assets/enemies.yaml` に外部化する。

| 敵 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| 10ほスライム | ✅ | ✅ | ✅ |
| かいてんゴブリン | ✅ | ✅ | ✅ |
| ループゴースト | ✅ | ✅ | ✅ |
| 10かいナイト | ✅ | ✅ | ✅ |
| もしガード | ✅ | ✅ | ✅ |
| でなければスライム | ✅ | ✅ | ✅ |
| HPカウンター | ✅ | ✅ | ✅ |
| クローン忍者 | ✅ | ✅ | ✅ |
| 無限バグ | ✅ | ✅ | ✅ |
| 魔王グリッチのクローン (postClearOnly) | ✅ | — | ❌ |
| 魔王グリッチ (ラスボス) | ✅ | ✅ (`BOSS_DATA`) | ✅ |
| プロフェッサー (真ボス) | ✅ | — | ❌ |

> Pyxel版の敵パラメータはリバランス済み（HPと攻撃力が大幅に増加）。要バランス検証。

---

