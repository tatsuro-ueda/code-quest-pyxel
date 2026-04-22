from __future__ import annotations

import importlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEPRECATED_WRAPPERS = [
    ROOT / 'src' / 'dialogue_data.py',
    ROOT / 'src' / 'audio_system.py',
    ROOT / 'src' / 'input_bindings.py',
    ROOT / 'src' / 'play_session_logging.py',
    ROOT / 'src' / 'save_store.py',
    ROOT / 'src' / 'structured_dialog.py',
    ROOT / 'src' / 'chiptune_tracks.py',
    ROOT / 'src' / 'landmark_events.py',
    ROOT / 'src' / 'player_factory.py',
    ROOT / 'src' / 'player_snapshot.py',
]
ALLOWED_ROOT_FILES = {
    ROOT / 'src' / '__init__.py',
    ROOT / 'src' / 'app.py',
    ROOT / 'src' / 'game_data.py',
}
TARGETS = [
    ROOT / 'main.py',
    ROOT / 'main_development.py',
    ROOT / 'tools' / 'report_play_sessions.py',
    ROOT / 'tools' / 'web_runtime_server.py',
    ROOT / 'tools' / 'test_web_compat.py',
    ROOT / 'test' / 'test_audio_system.py',
    ROOT / 'test' / 'test_input_bindings.py',
    ROOT / 'test' / 'test_landmark_events.py',
    ROOT / 'test' / 'test_landmark_resolve.py',
    ROOT / 'test' / 'test_play_session_logging.py',
    ROOT / 'test' / 'test_player_factory.py',
    ROOT / 'test' / 'test_player_snapshot.py',
    ROOT / 'test' / 'test_report_play_sessions.py',
    ROOT / 'test' / 'test_save_store.py',
    ROOT / 'test' / 'test_spell_logic.py',
    ROOT / 'test' / 'test_structured_dialog.py',
    ROOT / 'test' / 'test_dialogue_integration.py',
    ROOT / 'test' / 'test_web_runtime_server.py',
]
FORBIDDEN_IMPORTS = [
    'src.dialogue_data',
    'src.audio_system',
    'src.input_bindings',
    'src.landmark_events',
    'src.play_session_logging',
    'src.player_factory',
    'src.player_snapshot',
    'src.save_store',
    'src.structured_dialog',
    'src.chiptune_tracks',
]


class TestArchitectureLayout(unittest.TestCase):
    def test_shared_service_modules_exist(self):
        audio = importlib.import_module('src.shared.services.audio_system')
        landmark_events = importlib.import_module('src.shared.services.landmark_events')
        player_state = importlib.import_module('src.shared.services.player_state')
        save_store = importlib.import_module('src.shared.services.save_store')
        input_bindings = importlib.import_module('src.shared.services.input_bindings')
        play_session_logging = importlib.import_module('src.shared.services.play_session_logging')

        self.assertTrue(hasattr(audio, 'AudioManager'))
        self.assertTrue(hasattr(audio, 'CHIPTUNE_TRACKS'))
        self.assertTrue(hasattr(landmark_events, 'find_landmark_event'))
        self.assertTrue(hasattr(player_state, 'create_initial_player'))
        self.assertTrue(hasattr(player_state, 'restore_snapshot'))
        self.assertTrue(hasattr(save_store, 'make_save_store'))
        self.assertTrue(hasattr(input_bindings, 'InputStateTracker'))
        self.assertTrue(hasattr(play_session_logging, 'summarize_sessions'))

    def test_dialog_scene_modules_exist(self):
        dialog_model = importlib.import_module('src.scenes.dialog.model')
        dialog_scene = importlib.import_module('src.scenes.dialog.scene')

        self.assertTrue(hasattr(dialog_model, 'StructuredDialogRunner'))
        self.assertTrue(hasattr(dialog_scene, 'DialogScene'))

    def test_app_and_scene_manager_exist(self):
        app = importlib.import_module('src.app')
        scene_manager = importlib.import_module('src.core.scene_manager')

        self.assertTrue(hasattr(app, 'BlockQuestApp'))
        self.assertTrue(hasattr(scene_manager, 'SceneManager'))

    def test_legacy_wrapper_modules_are_gone(self):
        missing = [path for path in DEPRECATED_WRAPPERS if path.exists()]
        self.assertEqual(missing, [], f'legacy wrappers still present: {missing}')

    def test_src_root_contains_only_app_and_game_data_modules(self):
        root_files = {path for path in (ROOT / 'src').glob('*.py')}
        self.assertEqual(root_files, ALLOWED_ROOT_FILES)

    def test_repo_imports_only_new_module_paths(self):
        offenders: list[str] = []
        for path in TARGETS:
            text = path.read_text(encoding='utf-8')
            for forbidden in FORBIDDEN_IMPORTS:
                if forbidden in text:
                    offenders.append(f'{path}: {forbidden}')
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()
