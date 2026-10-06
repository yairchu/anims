"""Presets round-trip all text without implicitly changing the export timeline."""

import json
import shlex
import tempfile
import unittest
from pathlib import Path

import moops

from animation_timeline import load_scene
from phone_notification import app
from phone_inputs import PhonePresets


class PhonePresetTests(unittest.TestCase):
    def test_save_reload_select_and_apply(self):
        with tempfile.TemporaryDirectory() as folder:
            preset_path = Path(folder) / "presets.json"
            timeline_path = Path(folder) / "timeline.json"
            timeline = load_scene("phone")
            timeline_path.write_text(json.dumps(timeline))
            before = timeline_path.read_bytes()
            selected = [None]
            def store(value):
                selected[0] = value
            presets = PhonePresets(lambda: selected[0], store, filename=preset_path, defaults=timeline["labels"])
            labels = {
                "account": "dog's.club", "caption": 'שלום & "hello" <3',
                "app": "בדיקת צוותים", "title": "רשימה חדשה", "body": "",
            }
            options = dict(zip(
                ("--account", "--caption", "--notification-app", "--notification-title", "--notification-body"),
                labels.values(),
            ))
            argv = ["phone_notification.py"] + [token for pair in options.items() for token in pair]
            _, edited = app.run(defs={
                "args": moops.Group(argv, presets=presets), "timeline_path": timeline_path,
            })
            self.assertEqual(edited["live_labels"], labels)
            serialized = edited["text_interface"].preset_args()
            self.assertNotIn("--time", shlex.split(serialized))
            presets.save("Dog reel", serialized)
            reloaded = PhonePresets(lambda: selected[0], store, filename=preset_path, defaults=timeline["labels"])
            reloaded.rename("Dog reel", "Hebrew reel")
            self.assertEqual(list(reloaded.list()), ["Hebrew reel"])
            # Change defaults to ensure even empty / formerly default values restore.
            other_defaults = timeline | {"labels": {key: "different" for key in labels}}
            _, restored = app.run(defs={
                "args": moops.Group(["phone_notification.py"], presets=reloaded),
                "timeline_path": timeline_path, "timeline": other_defaults,
            })
            self.assertEqual(restored["live_labels"], labels)
            self.assertEqual(timeline_path.read_bytes(), before)
            restored["save_labels"](timeline_path, restored["live_labels"])
            applied = json.loads(timeline_path.read_text())
            self.assertEqual(applied["labels"], labels)
            self.assertEqual(applied["tracks"], timeline["tracks"])
            self.assertEqual(applied["duration"], timeline["duration"])


if __name__ == "__main__":
    unittest.main()
