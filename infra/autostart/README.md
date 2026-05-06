# code-quest-runtime systemd autostart (J53 Phase 4)

Block Quest の `tools/web_runtime_server.py` を exe.dev VM 上で常駐起動する
ための systemd service 設定。

## 役割

- 子どもがいつブラウザを開いても http://VM-IP:8000/ で Block Quest が遊べる
- VM 再起動後も自動復旧（`Restart=on-failure` + `WantedBy=multi-user.target`）
- `dist/` artifacts が未生成なら起動時に自動ビルド（`ensure_dist_build`）

## Install 手順

```bash
# 1. service file を systemd にコピー
sudo cp /home/exedev/code-quest-pyxel/infra/autostart/code-quest-runtime.service \
    /etc/systemd/system/code-quest-runtime.service

# 2. systemd に再読み込みさせる
sudo systemctl daemon-reload

# 3. enable して即時起動
sudo systemctl enable --now code-quest-runtime.service

# 4. 状態確認
sudo systemctl status code-quest-runtime.service

# 5. ログ確認（起動時の ensure_dist_build 結果など）
journalctl -u code-quest-runtime.service -f
```

## Troubleshooting

### `systemctl status` で `failed` になる

ログを確認する：

```bash
journalctl -u code-quest-runtime.service -n 50 --no-pager
```

よくある原因:

| 症状 | 対処 |
|---|---|
| `ModuleNotFoundError: No module named 'pyxel'` | `/usr/bin/python3` から pyxel が見えない。system-wide install が必要、または `ExecStart` を `.venv/bin/python3` に差し替える |
| `Address already in use` | 8000 番を既に他で使っている。`sudo ss -ltnp \| grep :8000` で特定して停止。あるいは unit file の `--port` を変更 |
| `Permission denied` on db path | `.runtime/play_sessions.sqlite3` の親ディレクトリ権限。`chown -R exedev:exedev /home/exedev/code-quest-pyxel/.runtime` |

### Code Maker import 後に本番が更新されない

`_handle_codemaker_resource_import` → `rebuild_after_codemaker_resource_import` →
`build_web_release` のチェーンに失敗している可能性。同期的に走るので
journalctl にエラーが出ているはず。

```bash
journalctl -u code-quest-runtime.service --since "10 min ago"
```

### service を一時停止したい

```bash
sudo systemctl stop code-quest-runtime.service       # 今だけ止める
sudo systemctl disable code-quest-runtime.service    # 次回起動時も止める
```

再開:

```bash
sudo systemctl enable --now code-quest-runtime.service
```

## 関連ドキュメント

- 本 task: `steering/20260422-j53-runtime-modularize-and-single-distribution.md` の
  section 4.8 (Phase 4 Tasklist)
- `tools/web_runtime_server.py` line 155-175: `ensure_dist_build()` の詳細
