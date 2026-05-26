"""CJG/audio: pyxres の Sound / Music truth を runtime が壊さない。"""

from __future__ import annotations

import ast
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ALLOWED_SOUND_SET_FILES = {
    ROOT / "src" / "shared" / "services" / "audio_system.py",
}


class _FakeSound:
    def __init__(self):
        self.notes: list[object] = []
        self.tones: list[object] = []
        self.volumes: list[object] = []
        self.effects: list[object] = []
        self.speed = 30
        self.set_calls: list[tuple[str, str, str, str, int]] = []

    def set(
        self,
        notes: str,
        tones: str,
        volumes: str,
        effects: str,
        speed: int,
    ) -> None:
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
        self.play_calls: list[tuple[int, int, bool]] = []
        self.playm_calls: list[tuple[int, bool]] = []
        self.stop_calls: list[object] = []
        self.init = lambda *args, **kwargs: None
        self.load = lambda *args, **kwargs: None
        self.save = lambda *args, **kwargs: None
        self.Font = lambda *args, **kwargs: None
        self.play = self._record_play
        self.playm = self._record_playm
        self.stop = self._record_stop

    def _record_play(self, ch: int, slot: int, loop: bool = False) -> None:
        self.play_calls.append((ch, slot, loop))

    def _record_playm(self, slot: int, loop: bool = True) -> None:
        self.playm_calls.append((slot, loop))

    def _record_stop(self, ch=None) -> None:
        self.stop_calls.append(ch)


def _load_main_module(script_name: str, pyxel_stub: _FakePyxel) -> types.ModuleType:
    script_path = ROOT / script_name
    source = script_path.read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType(f"{script_name.replace('.', '_')}_audio_truth_test")
    module.__file__ = str(script_path.resolve())
    original_pyxel = sys.modules.get("pyxel")
    removed_modules: dict[str, object] = {}
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith("src.runtime.app") or mod_name == script_path.stem:
            removed_modules[mod_name] = sys.modules.pop(mod_name)
    sys.modules[module.__name__] = module
    sys.modules["pyxel"] = pyxel_stub
    try:
        exec(compile(source, module.__file__, "exec"), module.__dict__)
    finally:
        if original_pyxel is None:
            del sys.modules["pyxel"]
        else:
            sys.modules["pyxel"] = original_pyxel
        for mod_name, mod_obj in removed_modules.items():
            sys.modules.setdefault(mod_name, mod_obj)
    return module


def _iter_pyxel_content_calls(path: Path) -> list[tuple[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    calls: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        if func.attr == "mml":
            calls.append(("mml", node.lineno))
            continue
        if func.attr != "set":
            continue
        owner = func.value
        if not isinstance(owner, ast.Subscript):
            continue
        collection = owner.value
        if not isinstance(collection, ast.Attribute):
            continue
        if collection.attr in {"sounds", "musics"}:
            calls.append((collection.attr, node.lineno))
    return calls


class AudioRuntimeTruthTest(unittest.TestCase):
    def test_runtime_does_not_overwrite_imported_title_music(self) -> None:
        pyxel_stub = _FakePyxel("pyxel_for_audio_music_truth")
        module = _load_main_module("main.py", pyxel_stub)
        audio_module = sys.modules["src.shared.services.audio_system"]
        imported_title = ([60], [61], [62], [])
        title_slot = 0

        module.StructuredDialogRunner = lambda data: types.SimpleNamespace(source=data)
        module.make_save_store = lambda path: types.SimpleNamespace(exists=lambda: False)
        module.InputStateTracker = lambda: types.SimpleNamespace()

        def fake_setup_image_banks(banks_self) -> None:
            banks_self.pyxres_loaded = True
            banks_self.pyxres_path = Path("my_resource.pyxres")
            pyxel_stub.musics[title_slot].set(*imported_title)

        module.ImageBanks.setup_image_banks = fake_setup_image_banks
        module.ImageBanks.setup_world_tilemap = lambda self: None

        audio_module._pyxel = pyxel_stub
        module.reset_bgm_state_for_tests()
        module.Game()
        module.play_bgm_track(title_slot)
        module.play_bgm_track(title_slot)

        self.assertEqual(pyxel_stub.musics[title_slot].set_calls, [imported_title])
        self.assertEqual(pyxel_stub.playm_calls, [(title_slot, True)])

    def test_src_has_no_python_defined_music_contents(self) -> None:
        music_writers: list[str] = []
        sound_writers: list[str] = []

        for path in (ROOT / "src").rglob("*.py"):
            for kind, lineno in _iter_pyxel_content_calls(path):
                rel = path.relative_to(ROOT)
                item = f"{rel}:{lineno}"
                if kind in {"musics", "mml"}:
                    music_writers.append(item)
                    continue
                if path not in ALLOWED_SOUND_SET_FILES:
                    sound_writers.append(item)

        self.assertEqual(
            music_writers,
            [],
            f"music content must stay in pyxres, not Python: {music_writers}",
        )
        self.assertEqual(
            sound_writers,
            [],
            f"sound set() writers outside audio_system.py are forbidden: {sound_writers}",
        )


if __name__ == "__main__":
    unittest.main()
