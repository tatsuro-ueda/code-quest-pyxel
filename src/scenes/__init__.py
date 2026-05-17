"""scenes パッケージの入口。

Problems:
    - 各シーンの位置を 1 箇所で見渡せないと、機能追加で似た構造を
      再発明しやすい。

Solutions:
    - src.scenes 配下に 1 シーン 1 ディレクトリで MVP
      （model/view/view_model/presenter/scene）を並べる。
"""
