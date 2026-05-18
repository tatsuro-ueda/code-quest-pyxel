"""複数シーンから共通利用するモジュール群の入口。

Problems:
    - シーン横断のサービス / 状態 / UI / 定数を 1 箇所にまとめないと、
      シーン間で似た実装が再発明される。

Solutions:
    - shared パッケージに services / state / ui / constants / assets を
      置き、scenes 側からの import 経路を統一する。
"""
