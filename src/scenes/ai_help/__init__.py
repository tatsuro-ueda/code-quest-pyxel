"""ai_help scene modules.

Problems:
    - シーン関連モジュールが起動時に都度パッケージ化されないと、
      import パスが揺れて呼び出し側が壊れる。

Solutions:
    - ai_help/ をパッケージ化し、model / presenter / view / view_model
      の責務分割を維持する。
"""
