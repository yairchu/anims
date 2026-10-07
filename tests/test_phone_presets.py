"""Presets round-trip all text without changing the timeline file."""

import json
import shlex
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

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
            defaults = timeline["labels"] | {"notification_scale": timeline["notification_scale"]}
            presets = PhonePresets(lambda: selected[0], store, filename=preset_path, defaults=defaults)
            # Running the notebook as a script exports; keep these runs to the preview.
            no_export = SimpleNamespace(value=False)
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
                "export_button": no_export,
            })
            self.assertEqual(edited["live_labels"], labels)
            serialized = edited["interface"].preset_args()
            self.assertNotIn("--time", shlex.split(serialized))
            presets.save("Dog reel", serialized)
            reloaded = PhonePresets(lambda: selected[0], store, filename=preset_path, defaults=defaults)
            reloaded.rename("Dog reel", "Hebrew reel")
            self.assertEqual(list(reloaded.list()), ["Hebrew reel"])
            # Change defaults to ensure even empty / formerly default values restore.
            other_defaults = timeline | {"labels": {key: "different" for key in labels}}
            _, restored = app.run(defs={
                "args": moops.Group(["phone_notification.py"], presets=reloaded),
                "timeline_path": timeline_path, "timeline": other_defaults,
                "export_button": no_export,
            })
            self.assertEqual(restored["live_labels"], labels)
            self.assertEqual(timeline_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
