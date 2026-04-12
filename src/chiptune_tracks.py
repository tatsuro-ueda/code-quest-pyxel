from __future__ import annotations

"""Chiptune BGM definitions for ブロッククエスト.

各シーン1曲につき、メロディ・ベース・ドラムの3チャンネル分を定義する。
ノート文字列は Pyxel のサウンド記法（letter + octave、`r` はレスト、空白無視）。

Pyxel music API 経由で再生する設計：
    pyxel.musics[scene_index].set([melody_slot], [bass_slot], [drum_slot], [])
    pyxel.playm(scene_index, loop=True)

これにより Pyxel Code Maker / `pyxel edit` の Music タブで編集可能になる。
Pyxel の music スロットは8個までなので、本作も **8トラックに収まるよう取捨選択** している：

    title / town / overworld / dungeon / battle / boss / victory / ending

旧 zone1/zone2/zone3 は `overworld` に統合（ゾーンが進んでも曲は変わらない）。
旧 boss1/boss2 は `boss` に統合（HP低下による曲切替えなし）。

シーン → サウンドスロット割当:
    melody_slot = scene_index * 3
    bass_slot   = scene_index * 3 + 1
    drum_slot   = scene_index * 3 + 2
シーン数8 × 3スロット = 24スロット使用 (sound 0-23)

トーン:
    p = pulse (メロディに使用)
    t = triangle (ベースに使用)
    n = noise (ドラムに使用)
"""



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
    # overworld — 旅のテーマ (G major)。旧 zone1/zone2/zone3 を統合
    # ──────────────────────────────────────────────────────────
    "overworld": {
        "melody": "g2b2d3g3 d3b2g2d2 e2g2b2d3 b2g2d2g2",
        "bass":   "g1g1g1g1 d1d1d1d1 c1c1c1c1 g1g1g1g1",
        "drums":  "f0rrr a4rrr f0rrr a4rrr",
        "speed":  23,
        "gain":   0.30,
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
    # boss — 重厚なボス戦 (F#m)。旧 boss1/boss2 を統合
    # ──────────────────────────────────────────────────────────
    "boss": {
        "melody": "f#2a2c#3f#3 c#3a2f#2c#2 e2g2b2e3 b2g2e2b1",
        "bass":   "f#1f#1c#1c#1 f#1f#1c#1c#1 e1e1b0b0 e1e1b0b0",
        "drums":  "f0f0a4r f0f0a4r f0f0a4r f0a4a4r",
        "speed":  17,
        "gain":   0.36,
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
