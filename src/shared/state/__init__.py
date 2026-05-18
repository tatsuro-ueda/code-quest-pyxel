"""Scene 横断で共有される state モデルをまとめるパッケージの入口。

Problems:
    - 主人公や所持品など、scenes をまたいで参照する状態を分散させると、
      framework-rule M4 (state は 1 箇所) に反する。

Solutions:
    - state パッケージで Player / 進行フラグなどの永続状態を 1 箇所に集約し、
      services から間接的に読み書きする。
"""
