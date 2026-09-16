import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from animation_scene import render_scene, ASSET_FILES
from animation_timeline import load_timeline, sample, state_at


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.timeline = load_timeline()

    def test_interpolation_and_holds(self):
        keys = [[0, 0], [2, 1], [4, 1]]
        self.assertEqual(sample(keys, -1), 0)
        self.assertEqual(sample(keys, 1), .5)
        self.assertEqual(sample(keys, 3), 1)
        self.assertEqual(sample(keys, 99), 1)

    def test_nonfinite_time_is_rejected(self):
        with self.assertRaises(ValueError):
            state_at(self.timeline, float('nan'))

    def test_random_seeking_is_repeatable(self):
        expected = state_at(self.timeline, 17.5)
        state_at(self.timeline, 24)
        state_at(self.timeline, 0)
        self.assertEqual(state_at(self.timeline, 17.5), expected)

    def test_direct_nudge_returns_before_attacks(self):
        self.assertGreater(state_at(self.timeline, 5.5)['israeli_position'], .5)
        self.assertEqual(state_at(self.timeline, 8)['israeli_position'], .5)
        self.assertGreater(state_at(self.timeline, 23)['israeli_position'], .8)

    def test_events_end_without_lingering_projectiles(self):
        self.assertEqual(state_at(self.timeline, 25)['events'], [])
        cash = self.timeline['events'][2]
        active = state_at(self.timeline, cash['start'])['events']
        self.assertTrue(any(e['kind'] == 'cash' and e['progress'] == 0 for e in active))
        self.assertFalse(any(e['start'] == cash['start'] for e in state_at(self.timeline, cash['start']+cash['duration'])['events']))

    def test_reject_duplicate_keyframe_times(self):
        broken = copy.deepcopy(self.timeline)
        broken['tracks']['portrait'] = [[0, 0], [0, 1]]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'bad.json'
            path.write_text(json.dumps(broken))
            with self.assertRaises(ValueError):
                load_timeline(path)

    def test_scene_at_every_frame_has_valid_xml(self):
        assets = {name: filename for name, filename in ASSET_FILES.items()}
        for frame in range(751):
            ET.fromstring(render_scene(state_at(self.timeline, frame/30), assets=assets))

    def test_alpha_export_omits_only_background(self):
        assets = {name: filename for name, filename in ASSET_FILES.items()}
        state = state_at(self.timeline, 14)
        opaque = render_scene(state, assets=assets)
        alpha = render_scene(state, assets=assets, transparent=True)
        self.assertIn('height="720" fill="white"', opaque)
        self.assertNotIn('height="720" fill="white"', alpha)
        self.assertIn('smotrich_and_bibi.png', alpha)


if __name__ == '__main__':
    unittest.main()
