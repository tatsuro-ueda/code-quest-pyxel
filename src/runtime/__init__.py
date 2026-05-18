"""Pyxel エントリポイント周りのランタイムをまとめるパッケージの入口。

Problems:
    - pyxel.run の呼び出し点や Game クラスの定義場所が散ると、
      初期化順序の追跡が難しくなる。

Solutions:
    - runtime パッケージにエントリポイント (app / main_runtime) を集め、
      ゲーム全体の初期化と main loop を一本化する。
"""
