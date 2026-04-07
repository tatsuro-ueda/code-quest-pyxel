"""Chiptune BGM definitions for ブロッククエスト.

各シーン1曲につき、メロディ・ベース・ドラムの3チャンネル分を定義する。
ノート文字列は Pyxel のサウンド記法（letter + octave、`r` はレスト、空白無視）。
これらは AudioManager._load_tracks() で `pyxel.sounds[N].set()` に渡される。

シーン → サウンドスロット割当:
    melody_slot = scene_index * 3
    bass_slot   = scene_index * 3 + 1
    drum_slot   = scene_index * 3 + 2
シーン数11 × 3スロット = 33スロット使用 (最大64枠の半分)

トーン:
    p = pulse (メロディに使用)
    t = triangle (ベースに使用)
    n = noise (ドラムに使用)
"""

from __future__ import annotations


CHIPTUNE_TRACKS: dict[str, dict] = {
    # ──────────────────────────────────────────────────────────
    # title — 英雄的なオープニング (Em)
    # ──────────────────────────────────────────────────────────
    "title": {
        "melody": "e2g2a2b2 e3d3b2a2 g2a2b2c3 d3e3rr",
        "bass":   "e1e1e1e1 c1c1c1c1 d1d1d1d1 e1e1e1e1",
        "drums":  "f0ra4r f0ra4r f0ra4r f0f0a4r",
        "speed":  22,
        "gain":   0.30,
    },
    # ──────────────────────────────────────────────────────────
    # town — のどかな町 (C major)
    # ──────────────────────────────────────────────────────────
    "town": {
        "melody": "c2e2g2c3 a2g2e2g2 f2a2c3a2 g2e2c2r",
        "bass":   "c1c1c1c1 f1f1f1f1 g1g1g1g1 c1c1c1c1",
        "drums":  "f0rrr a4rrr f0rrr a4rrr",
        "speed":  25,
        "gain":   0.28,
    },
    # ──────────────────────────────────────────────────────────
    # zone1 — 開けた草原 (G major)
    # ──────────────────────────────────────────────────────────
    "zone1": {
        "melody": "g2b2d3g3 d3b2g2d2 e2g2b2d3 b2g2d2g2",
        "bass":   "g1g1g1g1 d1d1d1d1 c1c1c1c1 g1g1g1g1",
        "drums":  "f0rrr a4rrr f0rrr a4rrr",
        "speed":  23,
        "gain":   0.30,
    },
    # ──────────────────────────────────────────────────────────
    # zone2 — やや緊張感 (D minor)
    # ──────────────────────────────────────────────────────────
    "zone2": {
        "melody": "d2f2a2d3 f2d2a1d2 g2a2g2f2 e2d2a1d2",
        "bass":   "d1d1d1d1 g1g1g1g1 a1a1a1a1 d1d1d1d1",
        "drums":  "f0rf0r a4rf0r f0rf0r a4rf0r",
        "speed":  22,
        "gain":   0.30,
    },
    # ──────────────────────────────────────────────────────────
    # zone3 — 不穏 (A minor)
    # ──────────────────────────────────────────────────────────
    "zone3": {
        "melody": "a2c3e3a3 g3e3c3a2 f2g2a2c3 e3c3a2e2",
        "bass":   "a1a1a1a1 f1f1f1f1 g1g1g1g1 a1a1a1a1",
        "drums":  "f0rf0r a4rf0r f0rf0r a4rf0r",
        "speed":  20,
        "gain":   0.32,
    },
    # ──────────────────────────────────────────────────────────
    # dungeon — 暗く重い (Em, slow)
    # ──────────────────────────────────────────────────────────
    "dungeon": {
        "melody": "e2rg2r b2re3r d3rb2r g2re2r",
        "bass":   "e1e1e1e1 e1e1e1e1 c1c1c1c1 d1d1d1d1",
        "drums":  "f0rrr rrrr f0rrr rrrr",
        "speed":  30,
        "gain":   0.32,
    },
    # ──────────────────────────────────────────────────────────
    # battle — エネルギッシュ (Am)
    # ──────────────────────────────────────────────────────────
    "battle": {
        "melody": "a2c3a2e2 c3e3c3a2 g2b2g2d2 b2d3b2g2",
        "bass":   "a1a1e1e1 a1a1e1e1 g1g1d1d1 g1g1d1d1",
        "drums":  "f0ra4r f0f0a4r f0ra4r f0f0a4r",
        "speed":  16,
        "gain":   0.34,
    },
    # ──────────────────────────────────────────────────────────
    # boss1 — 重厚なボス戦 (F#m)
    # ──────────────────────────────────────────────────────────
    "boss1": {
        "melody": "f#2a2c#3f#3 c#3a2f#2c#2 e2g2b2e3 b2g2e2b1",
        "bass":   "f#1f#1c#1c#1 f#1f#1c#1c#1 e1e1b0b0 e1e1b0b0",
        "drums":  "f0f0a4r f0f0a4r f0f0a4r f0a4a4r",
        "speed":  17,
        "gain":   0.36,
    },
    # ──────────────────────────────────────────────────────────
    # boss2 — 終盤の追い込み (F#m, faster)
    # ──────────────────────────────────────────────────────────
    "boss2": {
        "melody": "f#3a3c#4f#4 c#4a3f#3a3 e3g3b3e4 b3g3e3g3",
        "bass":   "f#1c#2f#1c#2 f#1c#2f#1c#2 e1b1e1b1 e1b1e1b1",
        "drums":  "f0a4f0a4 f0a4f0a4 f0a4f0a4 f0f0a4a4",
        "speed":  13,
        "gain":   0.38,
    },
    # ──────────────────────────────────────────────────────────
    # victory — 短い勝利ファンファーレ (C major)
    # ──────────────────────────────────────────────────────────
    "victory": {
        "melody": "c3e3g3c4 g3c4rr e3g3c4e4 c4rrr",
        "bass":   "c2c2c2c2 c2c2rr f1g1c2c2 c2rrr",
        "drums":  "f0f0a4r f0f0a4r f0f0a4a4 f0rrr",
        "speed":  18,
        "gain":   0.34,
    },
    # ──────────────────────────────────────────────────────────
    # ending — 感動的なエンディング (D major, slow)
    # ──────────────────────────────────────────────────────────
    "ending": {
        "melody": "d3f#3a3d4 a3f#3d3a2 g2b2d3g3 f#3d3a2d2",
        "bass":   "d1d1d1d1 g1g1g1g1 a1a1a1a1 d1d1d1d1",
        "drums":  "f0rrr rrrr f0rrr rrrr",
        "speed":  32,
        "gain":   0.30,
    },
}
