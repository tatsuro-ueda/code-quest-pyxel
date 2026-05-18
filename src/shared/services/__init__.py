"""シーン横断で使い回す副作用付きサービスの入口。

Problems:
    - 各シーンから直接 pyxel API を叩くと、入力 / 描画 / 音 / 保存などの
      副作用が散らばって差し替えにくくなる。

Solutions:
    - services パッケージで「副作用を一元化する責務」を集約し、
      scenes は services 経由でのみ pyxel を扱う。
"""
