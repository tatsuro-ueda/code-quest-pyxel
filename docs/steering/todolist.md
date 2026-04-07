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
- ❌ 未着手

---

## 1. 入力系

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| キーボード入力 | `pressKey/releaseKey/getKey` | `src/input_bindings.py` | ✅ | |
| ゲームパッド | `initGamepad` | `src/input_bindings.py` | ✅ | Pyxel側で抽象化 |
| タッチ仮想パッド | `setupTouch` | — | ❌ | 設計方針で「仮想パッドなし、モバイルはゲームパッドのみ」と決定済み（除外） |
| 振動 | `haptic` | — | ❌ | デスクトップ/ゲームパッド前提のため不要 |

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

JS版には28個の `sfx*` 関数があり、Pyxel版では未実装。`docs/85-sfx-design.md` の21SE設計に従って移植する。

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

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| ダメージポップアップ | `addPopup` / `gfx.popups` | — | ❌ | |
| パーティクルバースト | `addParticleBurst` / `gfx.particles` | — | ❌ | |
| GFX更新 | `updateGfx` | — | ❌ | |
| GFX描画 | `drawGfx` | — | ❌ | |

---

## 4. マップ生成

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| ワールドマップ生成 | （複数関数: `forest/lake/sand/mtn/clearAround/carveWindingPath/generateDecorations`） | `generate_world_map` (`main.py:877`) | ✅ |
| ダンジョン生成 | `carveDungeon` | `generate_dungeon` (`main.py:924`) | ✅ |
| パスバリアント | — | `get_path_variant` (`main.py:570`) | ✅ |
| 海岸バリアント | — | `get_shore_variant` (`main.py:586`) | ✅ |
| ゾーン判定 | — | `get_zone` (`main.py:960`) | ✅ |

---

## 5. 描画

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| マップ描画 | `drawMap` | `Game.draw_map` | ✅ | |
| タイル描画 | `drawTile` | `_render_tiles_to_bank` | ✅ | バンク描画 |
| 主人公描画 | `drawHero` | `_render_sprites_to_bank` | ✅ | |
| 装飾描画 | `drawDeco` | （バンクに含む） | ✅ | |
| ランドマーク描画 | `drawLandmarks` | — | ⚠️ | 検出はあるが「世界樹/塔」のランドマーク強調描画は未確認 |
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

| 機能 | JS版 | Pyxel版 | 状態 | メモ |
|---|---|---|---|---|
| 初期プレイヤー生成 | `createInitialPlayer` | `Game.__init__` 内のリテラル | ⚠️ | ファクトリ関数化されていない |
| EXPテーブル | `expForLevel` | — | ❌ | レベルアップ条件が未確認 |
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
| プロフェッサー戦予約 | `queueProfessorEncounter` | — | ❌ |
| プロフェッサー後日談 | `queueProfessorEpilogue` | — | ❌ |

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
| ボスフェーズ | `getBossPhases` | — | ❌ | 多段階ボス未実装 |
| メッセージ自動進行タイマー | `updateBattleMessageTimer` | — | ❌ | |
| 「攻撃ホールド」検出 | `isBattleAdvanceHeld/clearBattleAdvanceHold` | — | ❌ | |

---

## 10. アイテム / 魔法 / 装備

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
| 世界樹インタラクション | `interactWorldTree` | — | ❌ | `landmarkTreeSeen` フィールドはあるが処理なし |
| 塔インタラクション | `interactTower` | — | ❌ | `landmarkTowerSeen` 同上 |
| 塔エピローグ | `queueTowerEpilogue` | — | ❌ |
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
| プロフェッサーエンディング進入 | `enterProfessorEnding` | — | ❌ |
| プロフェッサーエンディング描画 | `drawProfessorEnding` | — | ❌ |
| プロフェッサーエンディング完了 | `completeProfessorEnding` | — | ❌ |

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

JS版には開発者報告用URL生成機能があります。Pyxel版はネイティブアプリのため URL を開く部分は別実装が必要。

| 機能 | JS関数 | 状態 | メモ |
|---|---|---|---|
| 報告コンテキスト構築 | `buildReportContext` | ❌ | |
| Issue URL生成 | `buildIssueUrl` | ❌ | |
| Shelley URL生成 | `buildShelleyUrl` | ❌ | |
| Terminal URL生成 | `buildTerminalUrl` | ❌ | |
| 外部リンクオープン | `openExternal` | ❌ | webブラウザ起動 or 表示のみ |

---

## 17. ゲームループ／フレーム制御

| 機能 | JS版 | Pyxel版 | 状態 |
|---|---|---|---|
| update | `update(dt)` | `Game.update` | ✅ |
| render | `render` | `Game.draw` | ✅ |
| メインループ | `gameLoop(time)` | `pyxel.run` | ✅ |
| 例外セーフな描画 | `_safeDraw` | — | ❌ |
| シーンキー（リセット用） | `_sceneKey` | — | ❌ |
| 入力フラッシュ | `_flushInput` | — | ❌ |

---

## 18. 敵データ充足度

JS版 12種類の敵 vs Pyxel版 9種類 + ボス1種。

| 敵 | JS版 | Pyxel版 |
|---|---|---|
| 10ほスライム | ✅ | ✅ |
| かいてんゴブリン | ✅ | ✅ |
| ループゴースト | ✅ | ✅ |
| 10かいナイト | ✅ | ✅ |
| もしガード | ✅ | ✅ |
| でなければスライム | ✅ | ✅ |
| HPカウンター | ✅ | ✅ |
| クローン忍者 | ✅ | ✅ |
| 無限バグ | ✅ | ✅ |
| 魔王グリッチのクローン (postClearOnly) | ✅ | ❌ |
| 魔王グリッチ (ラスボス) | ✅ | ✅ (`BOSS_DATA`) |
| プロフェッサー (真ボス) | ✅ | ❌ |

> Pyxel版の敵パラメータはリバランス済み（HPと攻撃力が大幅に増加）。要バランス検証。

---

## 優先順位の提案

このチェックリストは「全部やる」リストではなく「意思決定の素材」です。
推奨する着手順:

### 第1優先（プレイ可能性）
1. **ショップ実装**（武器・防具・道具屋） — `SHOP_WIP_MSG` を本実装に置換。`getItemPrice/tryPurchase/drawShop/processTownInput` 相当
2. **武器・防具データの拡充** — 価格・購入メッセージを JS から移植
3. **アイテムの追加**（アンチウイルス・セーブポイント・毒システム）

### 第2優先（演出と気持ちよさ）
4. **SFX 21音の実装** — `docs/85-sfx-design.md` に従う
5. **ダメージポップアップ／パーティクル**
6. **スプラッシュ画面**
7. **フィールドの足音（タイル別）**

### 第3優先（深さ）
8. **魔法システム**（5呪文 + レベル習得 + MP消費）
9. **多段階ボス**（`getBossPhases` 相当）
10. **ランドマーク個別イベント**（世界樹・塔）
11. **プロフェッサー戦＋真エンディング**

### 第4優先（リファクタ・任意）
12. `createInitialPlayer/resetGameState/_safeDraw` の整理
13. 報告URL（バグレポート連携）— Pyxel/ネイティブ向け代替設計が必要

---

## 進め方のアドバイス

- **1機能 = 1コミット = 1テスト追加** を徹底する
- 各機能の完了基準を「JS版で動いていた挙動が Pyxel版でも再現できる」に置く
- ✅/⚠️/❌ をこのファイルで更新しながら進める（PRごとに差分が出る）
- 第1優先の3項目だけでも完了すれば「ひととおり遊べるRPG」になる
