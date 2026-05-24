---
source: raw/tasknotes/steering/done/20260505-docs-sync-with-recent-steering.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 AGENTS.md / docs/ を最近の steering 改訂に追従させる Summary Draft

## summary

この note は、5月前半の steering refactor 群に AGENTS と docs を追従させた同期記録です。runtime root、shared services、SSoT rename、dev/prod 一本化などの実態を 3 文書へ反映し、repo map の stale entrypoint を減らしました。

## key_points

- `AGENTS.md`、`docs/architecture.md`、`docs/framework-rule.md` の 3 ファイルを recent steering に合わせて更新した。
- `main_development` 廃止、`src/runtime/app.py::Game` 昇格、`shared/services/scene_manager.py` / `debug_service.py` 追加などを docs へ追記した。
- コード rename と docs sync を同 commit に寄せる運用へ切り替えるべきだと Discussion に残した。

## important_quotes

- "`docs と code の同時改修ペア化`"
- "`AGENTS.md がちょうど 100 行`"

## open_questions

- `BlockQuestApp` や旧 `SceneManager` の live 記述を、どのタイミングで完全削除に寄せるべきか。
- 今後の rename/refactor で docs sync を同 commit に強制するには、どの guard が適切か。
