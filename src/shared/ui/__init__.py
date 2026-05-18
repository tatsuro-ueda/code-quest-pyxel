"""シーン横断で使い回す描画用 UI 部品の入口。

Problems:
    - メッセージ枠 / メニュー枠などを scenes ごとに再実装すると、
      見た目と挙動の細部が揃わなくなる。

Solutions:
    - ui パッケージで MessageWindow / MenuWindow / HUD / StatusBar 等の
      汎用描画部品をまとめ、scenes からは「使う」だけにする。
"""
