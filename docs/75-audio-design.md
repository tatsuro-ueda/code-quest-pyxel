# オーディオ機能設計

本ドキュメントは `audio-concepts.md` の8手法をブロッククエストの実装に落とし込む設計書である。
現行コードのオーディオ層（`audioCtx`, `playTone`, `sfx*` 関数群）に対して
**何を・どう変えるか**を定義する。

> 更新注記: この文書には旧HTML版前提の記述が残っている。現行のPyxel実装では `assets/audio/` に配置した `WAV/OGG` を `pyxel.sounds[n].pcm(...)` で再生する。

---

## 設計方針

| レイヤー | 対応するコンセプト手法 | 本ゲームでの実装方針 |
|----------|-----------------------|---------------------|
| 感情を作る | ②テンポ ③緊張音 ⑤楽器選び | シーン別BPM + 音色切替 + ダンジョン不協和音 |
| 行動を誘導する | ②テンポ ⑥レイヤー変化 ⑧SE分担 | バトルは高速、マップは中速、SE周波数帯を分離 |
| 記憶を作る | ①エリアテーマ ④ループ ⑦無音 | ゾーン別BGM + 自然なループ + ボス前の無音演出 |

---

## 技術基盤: TinyMusic ライブラリ

### 概要

TinyMusic は Web Audio API 上に構築された軽量音楽シーケンサーライブラリ。
`Sequence` クラスで音符列を定義し、`play()` / `stop()` で制御する。

- GitHub: https://github.com/kevincennis/TinyMusic
- サイズ: 約2KB（minified）
- ライセンス: MIT

### 採用理由

| 要件 | TinyMusic の対応 |
|------|-----------------|
| 単一ファイル制約 | ソースが小さく `index.html` にインライン埋め込み可能 |
| 既存 audioCtx との統合 | コンストラクタに既存の `AudioContext` を渡せる |
| チップチューン音色 | Web Audio の `oscillator.type`（square/sawtooth/triangle/sine）を直接指定 |
| ループ再生 | `sequence.loop = true` で自動ループ |
| テンポ制御 | `sequence.tempo` で BPM を動的変更可能 |
| 音量制御 | `sequence.gain.gain.value` で制御 |

### 組み込み方式

TinyMusic のソースコード（MIT ライセンス）を `index.html` の `// ===== AUDIO =====` セクション内に
インライン展開する。外部CDN参照はしない（オフライン動作保証のため）。

```js
// ===== TINYMUSIC (MIT License) =====
// https://github.com/kevincennis/TinyMusic
// [TinyMusic ソースコードをここにインライン]

// ===== BGM SYSTEM =====
// [本設計のBGMシステムをここに配置]
```

---

## 1. BGMシーン定義

### 1.1 シーン一覧

ゲーム内の `gameState` + コンテキストに応じて、以下のBGMシーンを定義する。

| BGMシーン ID | トリガー条件 | 手法 | 感情目標 |
|-------------|-------------|------|----------|
| `title` | `gameState === 'title'` | ①⑤ | ワクワク・冒険の予感 |
| `map_zone0` | `gameState === 'map'` かつ `getEnemyZone() === 0` | ①②④ | 安心・平和・探索 |
| `map_zone1` | `gameState === 'map'` かつ `getEnemyZone() === 1` | ①②④ | やや緊張・深い森 |
| `map_zone2` | `gameState === 'map'` かつ `getEnemyZone() === 2` | ①②③ | 不穏・警戒 |
| `map_zone3` | `gameState === 'map'` かつ `getEnemyZone() === 3` | ①②③ | 荒廃・決意 |
| `dungeon` | `gameState === 'map'` かつ `player.inDungeon` | ①③⑤ | 緊張・不気味 |
| `battle` | `gameState === 'battle'` かつ `!enemy.isBoss` | ②⑤⑥ | 緊張・興奮 |
| `boss` | `gameState === 'battle'` かつ `enemy.isBoss` | ②③⑤⑥ | 最高緊張・決戦 |
| `town` | `gameState === 'npc'` | ①④ | 安心・休息 |
| `victory` | バトル勝利時（`battleState.phase === 'victory'`） | ⑥ | 達成感 |
| `ending` | `gameState === 'ending'` | ①⑤⑦ | 感動・余韻 |
| `(無音)` | ボス部屋突入直前（BOSS_POS 隣接時） | ⑦ | 緊張の極み |

### 1.2 シーン遷移ルール

```
title ──[ぼうけんをはじめる/つづきから]-→ map_zone0〜3 / dungeon
map_* ──[エンカウント]──────────────→ battle / boss
map_* ──[町に入る]────────────────→ town
map_* ──[洞窟に入る]──────────────→ dungeon
map_* ──[ゾーン移動]──────────────→ map_zone(別)
battle ─[勝利]─────────────────→ victory ─[数秒後]─→ map_*
battle ─[敗北]─────────────────→ (無音) ─→ map_zone0
boss ──[勝利]─────────────────→ victory ─→ ending
town ──[退出]─────────────────→ map_*
dungeon ─[BOSS_POS隣接]───────────→ (無音) ─[ボス戦突入]─→ boss
```

---

## 2. BGM楽曲設計

### 2.1 音色パレット

TinyMusic は Web Audio の OscillatorType を使用する。
本ゲームでは以下の音色パレットを統一的に使う。

| 用途 | OscillatorType | 音域 | 理由 |
|------|---------------|------|------|
| メロディ | `square` | C4〜C6 | ファミコン風の主旋律。チップチューンRPGの王道 |
| ベースライン | `triangle` | C2〜C4 | 柔らかい低音。FC三角波チャンネル相当 |
| ハーモニー/対旋律 | `sawtooth` | C3〜C5 | やや荒い音色。緊張感や厚みを追加 |
| パッド/効果 | `sine` | C3〜C5 | 純音。穏やかなシーンや不気味な持続音 |

### 2.2 各BGMの設計仕様

#### title — タイトル画面

| 項目 | 値 |
|------|------|
| BPM | 120 |
| 拍子 | 4/4 |
| キー | C major |
| 小節数 | 8小節ループ |
| 音色 | メロディ: square / ベース: triangle |
| 雰囲気 | ドラクエ風ファンファーレ的な明るさ。冒険の始まりを予感させる |
| コンセプト手法 | ①記憶（タイトル＝この曲）⑤楽器（チップチューン＝レトロゲーム） |

音楽的特徴:
- 上行形のメロディ（希望・出発）
- 4小節目にサブドミナント（F）で広がり
- 8小節で自然にループする構造

#### map_zone0 — 城〜はじめの村周辺

| 項目 | 値 |
|------|------|
| BPM | 100 |
| 拍子 | 4/4 |
| キー | C major |
| 小節数 | 8小節ループ |
| 音色 | メロディ: square / ベース: triangle |
| 雰囲気 | 穏やか・安心・広い草原を歩く |
| コンセプト手法 | ①場所記憶 ②ゆっくり→探索 ④自然ループ |

音楽的特徴:
- シンプルな順次進行（C→G→Am→F）
- メロディは狭い音域（C4〜G4中心）で親しみやすく
- 8分音符主体のゆったりした動き

#### map_zone1 — ループ地帯

| 項目 | 値 |
|------|------|
| BPM | 108 |
| 拍子 | 4/4 |
| キー | A minor |
| 小節数 | 8小節ループ |
| 音色 | メロディ: square / ベース: triangle / 対旋律: sine（控えめ） |
| 雰囲気 | やや暗い・深い森・前に進む緊張感 |
| コンセプト手法 | ①場所記憶 ②やや速い→警戒 ④自然ループ |

音楽的特徴:
- Am→Dm→G→C の進行（マイナー感）
- zone0 より BPM を上げて少し焦る印象
- 低音にオクターブのパルス（ループ＝繰り返しの暗示）

#### map_zone2 — 条件分岐エリア

| 項目 | 値 |
|------|------|
| BPM | 112 |
| 拍子 | 4/4 |
| キー | D minor |
| 小節数 | 8小節ループ |
| 音色 | メロディ: square / ベース: triangle / ハーモニー: sawtooth（控えめ） |
| 雰囲気 | 不穏・判断を迫られる・曇り空 |
| コンセプト手法 | ①場所記憶 ②速め→緊張 ③不協和音を部分的に使用 |

音楽的特徴:
- Dm→Bb→Gm→A7 の進行
- メロディに時々短2度（半音）のぶつかりを入れて不穏さを演出
- 4小節目と8小節目で小さなブレイク（手法⑦の微小な無音）

#### map_zone3 — 変数/クローンエリア

| 項目 | 値 |
|------|------|
| BPM | 116 |
| 拍子 | 4/4 |
| キー | E minor |
| 小節数 | 8小節ループ |
| 音色 | メロディ: sawtooth / ベース: triangle / パッド: sine（不穏な持続音） |
| 雰囲気 | 荒廃・最終エリア前の決意 |
| コンセプト手法 | ①場所記憶 ②速め→緊張 ③不協和音 |

音楽的特徴:
- Em→C→D→B7 の進行
- メロディ音色を sawtooth に切り替え（zone0〜2 との差別化）
- 持続する sine 低音が不穏な雰囲気を作る

#### dungeon — グリッチのサーバー

| 項目 | 値 |
|------|------|
| BPM | 88 |
| 拍子 | 4/4 |
| キー | B minor |
| 小節数 | 8小節ループ |
| 音色 | メロディ: square（低め） / ベース: triangle / 効果: sine（不気味な装飾音） |
| 雰囲気 | 暗い・不気味・地下深く |
| コンセプト手法 | ①場所記憶 ②遅い→慎重に ③緊張音 ⑤暗い音色 |

音楽的特徴:
- Bm→F#→G→Em の進行
- BPM を下げて慎重さを演出
- 装飾の sine 音が半音階で上下してグリッチ感（バグっぽさ）を表現
- エコー感を gainNode のリリースを長めにして表現

#### battle — 通常バトル

| 項目 | 値 |
|------|------|
| BPM | 160 |
| 拍子 | 4/4 |
| キー | A minor |
| 小節数 | 4小節ループ（短くテンション維持） |
| 音色 | メロディ: square / ベース: sawtooth / リズム: square（低音パルス） |
| 雰囲気 | 緊張・興奮・戦闘 |
| コンセプト手法 | ②速い→戦う ⑤攻撃的音色 ⑥楽器が増える |

音楽的特徴:
- Am→F→G→E の進行
- 16分音符主体の速いメロディ
- ベースに sawtooth でドライブ感
- 低音 square のパルスがリズムを刻む（ドラム代替）

#### boss — ボス戦（魔王グリッチ）

| 項目 | 値 |
|------|------|
| BPM | 172 |
| 拍子 | 4/4 |
| キー | D minor |
| 小節数 | 8小節ループ |
| 音色 | メロディ: sawtooth / ベース: triangle / ハーモニー: square / 効果: sine |
| 雰囲気 | 最高緊張・絶望と決意・最終決戦 |
| コンセプト手法 | ②最速→全力 ③不協和音で絶望感 ⑤全音色投入 ⑥4声フル稼働 |

音楽的特徴:
- Dm→Bb→C→A7 → Dm→F→Gm→A7 の8小節
- 全4声を使った最も厚いアレンジ
- メロディに装飾音（前打音的な短い音）を入れて焦燥感
- 途中で半拍の無音（⑦）を挟んで緊張のピーク

#### town — 町

| 項目 | 値 |
|------|------|
| BPM | 92 |
| 拍子 | 3/4（ワルツ） |
| キー | F major |
| 小節数 | 8小節ループ |
| 音色 | メロディ: sine / ベース: triangle |
| 雰囲気 | 安心・休息・あたたかさ |
| コンセプト手法 | ①場所記憶 ④ループ（長時間滞在対応） |

音楽的特徴:
- F→C→Dm→Bb の進行
- 3拍子で穏やかな揺れ（マップBGMとの明確な差別化）
- メロディに sine を使い柔らかさを強調
- 町の中でショップや宿屋を行き来しても違和感がない万能曲

#### victory — 勝利ファンファーレ

| 項目 | 値 |
|------|------|
| BPM | 140 |
| 拍子 | 4/4 |
| キー | C major |
| 小節数 | 2小節（ループしない） |
| 音色 | メロディ: square / ハーモニー: square（3度上） |
| 雰囲気 | 達成感・爽快 |
| コンセプト手法 | ⑥急に明るくなる（対比） |

音楽的特徴:
- C→G→C の単純な進行
- 上行音型で駆け上がる
- 既存の `sfxVictory()` を置き換える

#### ending — エンディング

| 項目 | 値 |
|------|------|
| BPM | 80 |
| 拍子 | 4/4 |
| キー | C major |
| 小節数 | 16小節（ループ） |
| 音色 | メロディ: sine / ベース: triangle / ハーモニー: square（控えめ） |
| 雰囲気 | 感動・余韻・達成 |
| コンセプト手法 | ①記憶（title曲のモチーフを再利用）⑤柔らかい音色 ⑦無音からのフェードイン |

音楽的特徴:
- タイトル曲のメロディをスローアレンジ（記憶の回帰）
- 16小節と長めでゆったりと余韻に浸れる
- 冒頭2小節はベースのみ → メロディがフェードイン（⑥レイヤー変化）

---

## 3. BGMマネージャー設計

### 3.1 データ構造

```js
const BGM_TRACKS = {
  title:     { sequences: [...], tempo: 120, loop: true },
  map_zone0: { sequences: [...], tempo: 100, loop: true },
  map_zone1: { sequences: [...], tempo: 108, loop: true },
  map_zone2: { sequences: [...], tempo: 112, loop: true },
  map_zone3: { sequences: [...], tempo: 116, loop: true },
  dungeon:   { sequences: [...], tempo: 88,  loop: true },
  battle:    { sequences: [...], tempo: 160, loop: true },
  boss:      { sequences: [...], tempo: 172, loop: true },
  town:      { sequences: [...], tempo: 92,  loop: true },
  victory:   { sequences: [...], tempo: 140, loop: false },
  ending:    { sequences: [...], tempo: 80,  loop: true },
};
```

各 `sequences` は TinyMusic の `Sequence` オブジェクト配列（メロディ/ベース等の複数声部）。

### 3.2 BGMマネージャー関数

```js
let currentBGM = null;       // 現在再生中のBGMシーンID
let bgmSequences = [];       // 現在再生中の Sequence オブジェクト配列
let bgmVolume = 0.08;        // マスター音量（SE との競合を避ける控えめな値）

function playBGM(sceneId) {
  if (currentBGM === sceneId) return;  // 同じ曲なら何もしない
  stopBGM();
  const track = BGM_TRACKS[sceneId];
  if (!track) return;
  bgmSequences = track.sequences.map(seq => {
    // TinyMusic Sequence を生成 & 設定
    const s = new TinyMusic.Sequence(audioCtx, seq.tempo, seq.notes);
    s.loop = track.loop;
    s.gain.gain.value = bgmVolume * (seq.volumeScale || 1.0);
    s.staccato = seq.staccato || 0.2;
    s.waveType = seq.waveType || 'square';
    return s;
  });
  bgmSequences.forEach(s => s.play());
  currentBGM = sceneId;
}

function stopBGM() {
  bgmSequences.forEach(s => s.stop());
  bgmSequences = [];
  currentBGM = null;
}

function setBGMVolume(vol) {
  bgmVolume = vol;
  bgmSequences.forEach(s => {
    s.gain.gain.value = bgmVolume;
  });
}
```

### 3.3 BGMシーン判定関数

ゲームループの `update()` 内で毎フレーム呼び出す。

```js
function updateBGM() {
  let targetScene = null;

  switch (gameState) {
    case 'title':
      targetScene = 'title';
      break;
    case 'map':
      if (player.inDungeon) {
        // ボス部屋隣接判定（手法⑦ 無音）
        const distToBoss = Math.abs(player.x - BOSS_POS.x) + Math.abs(player.y - BOSS_POS.y);
        targetScene = (distToBoss <= 2 && !player.bossDefeated) ? null : 'dungeon';
      } else {
        const zone = getEnemyZone();
        targetScene = 'map_zone' + Math.min(zone, 3);
      }
      break;
    case 'battle':
      if (battleState) {
        if (battleState.phase === 'victory') {
          targetScene = 'victory';
        } else if (battleState.phase === 'defeat') {
          targetScene = null; // 敗北時は無音
        } else {
          targetScene = battleState.enemy.isBoss ? 'boss' : 'battle';
        }
      }
      break;
    case 'npc':
      targetScene = 'town';
      break;
    case 'menu':
      // メニュー中はマップBGMを継続（変更しない）
      return;
    case 'ending':
      targetScene = 'ending';
      break;
  }

  if (targetScene === null) {
    stopBGM();
  } else {
    playBGM(targetScene);
  }
}
```

### 3.4 特殊演出

#### ボス前の無音（手法⑦）

ダンジョン内で BOSS_POS の距離2マス以内に入ると BGM を停止する。
`updateBGM()` 内で `distToBoss <= 2` の条件で `targetScene = null` にするだけで実現。

#### 勝利ファンファーレ → マップ復帰

`victory` BGM は `loop: false` で再生し、再生終了後に自動的に `gameState` が `'map'` に
戻った時点で `updateBGM()` がマップBGMを再開する。

#### 敗北時

`processDefeat()` で城に戻された後、`gameState === 'map'` で `updateBGM()` が
`map_zone0`（城周辺）を再生開始する。死亡〜復活の間は無音。

---

## 4. 効果音との役割分担（手法⑧）

### 4.1 周波数帯の分離

| 音の種類 | 周波数帯 | 音量 |
|----------|---------|------|
| BGM メロディ | C4〜C6 (262〜1047Hz) | 0.08 |
| BGM ベース | C2〜C4 (65〜262Hz) | 0.06 |
| SE（攻撃/被ダメ） | 100〜300Hz | 0.10 |
| SE（魔法/回復） | 400〜900Hz | 0.08 |
| SE（カーソル/決定） | 600〜900Hz | 0.05 |
| SE（レベルアップ） | 300〜700Hz | 0.06 |

BGM は SE より音量を低く設定し、SE が鳴った時に自然に聴こえるようにする。

### 4.2 SE発生時のBGM処理

SE はバースト的（0.05〜0.3秒）なので、BGM を特別に制御する必要はない。
音量バランスだけで共存させる（ダッキングはしない — 実装コスト対効果が低い）。

### 4.3 既存SE関数の変更

既存の `sfx*` 関数群はそのまま維持する。変更不要。
`sfxVictory()` は BGM の `victory` トラックに機能的に置き換わるが、
BGM 未対応のフォールバックとして関数自体は残す。

---

## 5. 音源の調達方針

### 5.1 ネット素材の活用

TinyMusic の音符データ（ノート文字列）は自前で記述する必要があるが、
メロディや和声進行の参考としてフリー素材・パブリックドメインの楽譜を活用する。

| 素材源 | 用途 | ライセンス |
|--------|------|-----------|
| [OpenGameArt.org](https://opengameart.org/) Audio カテゴリ | メロディ構造の参考（そのまま使用はしない） | 各素材による (CC0/CC-BY 多数) |
| [FreeMidi.org](https://freemidi.org/) | コード進行・メロディ構造の分析参考 | 個人利用 |
| [MusicTheory.net](https://www.musictheory.net/) | コード進行パターンの理論的参考 | 教育用途 |
| [chiptune コミュニティ作品](https://modarchive.org/) | 音色・アレンジ技法の参考 | 各素材による |

### 5.2 メロディ創作の方針

- RPGの定番コード進行（I-V-vi-IV 等）をベースに独自のメロディを乗せる
- 既存楽曲のコピーはしない（著作権回避）
- 各シーンのメロディは4〜8音のモチーフを基本単位とし、変奏で展開する
- タイトル曲のモチーフをエンディングで再利用（手法①の記憶効果）

---

## 6. 実装計画

### 6.1 新規追加するコード領域

`index.html` 内の配置:

```
// ===== AUDIO =====
const audioCtx = ...;            // ← 既存
function playTone(...) { ... }    // ← 既存（SE用、変更なし）
function sfxAttack() { ... }      // ← 既存（変更なし）
...

// ===== TINYMUSIC (MIT License) =====
// [TinyMusic ライブラリソース ≈ 80行]

// ===== BGM SYSTEM =====
const BGM_TRACKS = { ... };       // ← 新規：全BGMデータ定義
let currentBGM = null;            // ← 新規
let bgmSequences = [];            // ← 新規
let bgmVolume = 0.08;             // ← 新規
function playBGM(sceneId) { ... } // ← 新規
function stopBGM() { ... }        // ← 新規
function updateBGM() { ... }      // ← 新規
```

### 6.2 既存コードの変更箇所

| 変更箇所 | 変更内容 |
|----------|---------|
| `update()` 関数 | 末尾に `updateBGM()` 呼び出しを追加 |
| `resetGameState()` | `stopBGM(); currentBGM = null;` を追加 |
| `module.exports` | `playBGM`, `stopBGM`, `updateBGM`, `currentBGM`(getter) を追加 |

### 6.3 追加しないもの

| 機能 | 理由 |
|------|------|
| BGM音量設定UI | 初期バージョンでは不要。将来メニューに追加可能 |
| フェードイン/フェードアウト | TinyMusic 標準では非対応。必要なら gainNode を手動で制御するが優先度低 |
| ダッキング（SE時にBGM音量下げ） | 音量バランスで十分。実装コスト対効果が低い |

---

## 7. 実装優先度

| 優先度 | 項目 | 効果 | 工数 |
|:---:|------|------|:---:|
| S | TinyMusic 埋め込み + BGMマネージャー基盤 (§3) | 全BGMの前提 | 中 |
| S | バトルBGM (§2 battle) | 最も体験が変わる | 中 |
| S | マップBGM zone0 (§2 map_zone0) | 最初に聞く曲 | 中 |
| A | タイトルBGM (§2 title) | 第一印象 | 小 |
| A | 町BGM (§2 town) | 安心感の演出 | 小 |
| A | ダンジョンBGM (§2 dungeon) | 緊張感の演出 | 中 |
| B | マップBGM zone1〜3 (§2 map_zone1〜3) | ゾーン差別化 | 中 |
| B | ボスBGM (§2 boss) | 最終決戦感 | 中 |
| B | 勝利ファンファーレ (§2 victory) | 達成感 | 小 |
| C | エンディングBGM (§2 ending) | 感動 | 中 |
| C | ボス前無音演出 (§3.4) | 緊張の極み | 小 |
| D | フェードイン/アウト | 滑らかな遷移 | 中 |
| D | BGM音量設定UI | ユーザー制御 | 中 |

工数: 小 = ~20行, 中 = ~50行

---

## 8. 変更影響範囲

| 変更 | 影響する関数/変数 | テスト影響 |
|------|-------------------|------------|
| TinyMusic 追加 | 新規コード（Audio依存） | テスト対象外 |
| BGM_TRACKS 追加 | 新規定数 | データ構造テスト追加可能 |
| playBGM / stopBGM 追加 | 新規関数（Audio依存） | テスト対象外（モック経由なら可） |
| updateBGM 追加 | 新規関数（gameState/player 参照） | ロジックテスト対象 |
| update() 変更 | `updateBGM()` 呼び出し追加 | 既存テストへの影響なし |
| resetGameState() 変更 | `stopBGM()` 追加 | 既存テストへの影響なし（Audio モック済み） |

`module.exports` に `updateBGM`, `playBGM`, `stopBGM`, `BGM_TRACKS` を追加すること。
`updateBGM` はロジック部分（シーン判定）がテスト可能。Audio 呼び出し部分はモックで吸収。

---

## 設計原則（audio-concepts.md との対応）

| コンセプト手法 | 本設計での実現 |
|---------------|---------------|
| ①エリアテーマ | ゾーン別4曲 + ダンジョン + 町 + タイトル + エンディング（8テーマ） |
| ②テンポ調整 | BPM 80(ending)〜172(boss) のレンジで行動速度を誘導 |
| ③不協和音 | zone2〜3 の半音ぶつかり、ダンジョンのグリッチ装飾音 |
| ④ループ構造 | 全曲 4〜16小節の自然なループ設計 |
| ⑤楽器選び | チップチューン4音色でレトロRPG感を統一 |
| ⑥レイヤー変化 | ボス戦で4声フル稼働、町は2声のみ |
| ⑦無音 | ボス前2マス、敗北時、エンディング冒頭 |
| ⑧SE分担 | 周波数帯分離 + 音量バランスで共存 |
