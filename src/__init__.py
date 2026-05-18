"""Code Quest Pyxel パッケージのトップ。

Problems:
    - パッケージ階層の入口がないと、import path が
      ばらつき、scenes / shared / runtime の依存関係が読み取れない。

Solutions:
    - src パッケージとして空の __init__.py を置き、サブパッケージ
      (scenes / shared / runtime / core / generated) の親を明示する。
"""
