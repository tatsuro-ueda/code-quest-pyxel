from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class _FakeSound:
    def __init__(self):
        self.notes: list[object] = []
        self.tones: list[object] = []
        self.volumes: list[object] = []
        self.effects: list[object] = []
        self.speed = 30
        self.set_calls: list[tuple[str, str, str, str, int]] = []

    def set(self, notes: str, tones: str, volumes: str, effects: str, speed: int) -> None:
        self.set_calls.append((notes, tones, volumes, effects, speed))
        self.notes = [notes] if notes else []
        self.tones = [tones] if tones else []
        self.volumes = [volumes] if volumes else []
        self.effects = [effects] if effects else []
        self.speed = speed


class _FakeMusic:
    def __init__(self):
        self.set_calls: list[tuple[list[int], list[int], list[int], list[int]]] = []

    def set(self, seqs0, seqs1, seqs2, seqs3) -> None:
        self.set_calls.append((seqs0, seqs1, seqs2, seqs3))


class _FakePyxel(types.ModuleType):
    def __init__(self, name: str):
        super().__init__(name)
        self.sounds = [_FakeSound() for _ in range(64)]
        self.musics = [_FakeMusic() for _ in range(8)]
        self.channels = [types.SimpleNamespace(gain=0.125) for _ in range(8)]
        self.init = lambda *args, **kwargs: None
        self.load = lambda *args, **kwargs: None
        self.save = lambda *args, **kwargs: None
        self.Font = lambda *args, **kwargs: None
        self.play = lambda *args, **kwargs: None
        self.playm = lambda *args, **kwargs: None
        self.stop = lambda *args, **kwargs: None


def _load_main_module(script_name: str, pyxel_stub: _FakePyxel) -> types.ModuleType:
    script_path = ROOT / script_name
    source = script_path.read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType(f"{script_name.replace('.', '_')}_cj24_test")
    module.__file__ = str(script_path.resolve())
    original_pyxel = sys.modules.get("pyxel")
    sys.modules[module.__name__] = module
    sys.modules["pyxel"] = pyxel_stub
    try:
        exec(compile(source, module.__file__, "exec"), module.__dict__)
    finally:
        if original_pyxel is None:
            del sys.modules["pyxel"]
        else:
            sys.modules["pyxel"] = original_pyxel
    return module


class CJ24SoundEditorTruthTest(unittest.TestCase):
    def test_docs_keep_cj24_and_cjg24_roundtrip_contract_visible(self):
        journeys = (ROOT / "docs" / "customer-journeys.md").read_text(encoding="utf-8")
        av = (ROOT / "docs" / "cj-gherkin-av.md").read_text(encoding="utf-8")
        guardrails = (ROOT / "docs" / "cj-gherkin-guardrails.md").read_text(encoding="utf-8")

        self.assertIn("### CJ24: 効果音を自分で作る", journeys)
        self.assertIn("Scenario: Soundエディタで編集したSFXがゲーム内で使われる", av)
        self.assertIn("And 固定のコード定義で別音へ戻らない", av)
        self.assertIn("Scenario: imported Sound / Music が runtime audio の正本になる", guardrails)

    def test_main_runtime_keeps_imported_attack_sfx_after_pyxres_load(self):
        self._assert_runtime_keeps_imported_attack_sfx("main.py")

    def test_main_development_runtime_keeps_imported_attack_sfx_after_pyxres_load(self):
        self._assert_runtime_keeps_imported_attack_sfx("main_development.py")

    def _assert_runtime_keeps_imported_attack_sfx(self, script_name: str) -> None:
        pyxel_stub = _FakePyxel(f"pyxel_for_{script_name}")
        module = _load_main_module(script_name, pyxel_stub)

        imported_attack = ("c4", "p", "7", "n", 8)
        attack_slot = module.SFX_BASE_SLOT + list(module.SFX_DEFINITIONS).index("attack")

        module.AudioManager = lambda pyxel_module: types.SimpleNamespace(pyxel=pyxel_module)
        module.StructuredDialogRunner = lambda data: types.SimpleNamespace(source=data)
        module.generate_world_map = lambda: [[0]]
        module.create_initial_player = lambda: types.SimpleNamespace()
        module.make_save_store = lambda path: types.SimpleNamespace(exists=lambda: False)
        module.InputStateTracker = lambda: types.SimpleNamespace()
        module.Game._setup_world_tilemap = lambda self: None
        module.Game._apply_av_settings = lambda self: None
        module.Game._sync_audio = lambda self: None

        def fake_setup_image_banks(game_self) -> None:
            game_self._pyxres_loaded = True
            game_self._pyxres_path = Path("my_resource.pyxres")
            pyxel_stub.sounds[attack_slot].set(*imported_attack)

        module.Game._setup_image_banks = fake_setup_image_banks

        game = module.Game()

        self.assertEqual(game.sfx._slots["attack"], attack_slot)
        self.assertEqual(pyxel_stub.sounds[attack_slot].set_calls[-1], imported_attack)
        self.assertEqual(len(pyxel_stub.sounds[attack_slot].set_calls), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
