import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from animation_scene import render_scene, zone_emphasis, ASSET_FILES
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

    def test_format_canvas_and_hidden_entrances(self):
        from video_formats import FORMATS
        assets = {name: filename for name, filename in ASSET_FILES.items()}
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for width, height in FORMATS.values():
            root = ET.fromstring(render_scene(state_at(self.timeline, 0), assets=assets, width=width, height=height))
            x, y, w, h = map(float, root.attrib["viewBox"].split())
            self.assertAlmostEqual(w / h, width / height)
            image = root.find("svg:g/svg:image", ns)
            self.assertGreater(float(image.attrib["x"]), x+w)
            pal = root.find("svg:g[@id='palestinian']", ns)
            pal_y = float(pal.attrib["transform"].split()[1].rstrip(')'))
            self.assertLess(pal_y+305, y)

    def test_reconciliation_requires_both_visible_meters(self):
        assets = {name: filename for name, filename in ASSET_FILES.items()}
        state = state_at(self.timeline, 23)
        state.update(israeli_position=.1, palestinian_position=.1)
        self.assertIn('id="reconciliation-connection"', render_scene(state, assets=assets))
        state['palestinian_position'] = .5
        self.assertNotIn('id="reconciliation-connection"', render_scene(state, assets=assets))
        state.update(palestinian_position=.1, palestinian_y=-400)
        self.assertNotIn('id="reconciliation-connection"', render_scene(state, assets=assets))

    def test_zone_boundaries_and_right_intensity(self):
        assets = {name: filename for name, filename in ASSET_FILES.items()}
        state = state_at(self.timeline, 23)
        with self.assertRaises(ValueError):
            render_scene(state, assets=assets, reconciliation_end=.9, right_zone_start=.8)
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        def right_opacity(position):
            state['israeli_position'] = position
            root = ET.fromstring(render_scene(state, assets=assets))
            return float(root.find("svg:g[@id='israeli']/svg:g/svg:path[@data-zone='right']", ns).attrib['fill-opacity'])
        self.assertLess(right_opacity(.8), right_opacity(1))

    def test_icon_emphasis_is_smooth_at_zone_boundaries(self):
        self.assertEqual(zone_emphasis(.5), (0, 0))
        self.assertEqual(zone_emphasis(.25), (0, 0))
        self.assertEqual(zone_emphasis(.8), (0, 0))
        self.assertEqual(zone_emphasis(0), (1, 0))
        self.assertEqual(zone_emphasis(1), (0, 1))
        self.assertLess(zone_emphasis(.25-1e-6)[0], 1e-8)
        self.assertLess(zone_emphasis(.8+1e-6)[1], 1e-8)

    def test_icon_scale_and_shared_glow(self):
        assets = {name: filename for name, filename in ASSET_FILES.items()}
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        state = state_at(self.timeline, 23)
        state.update(israeli_position=0, palestinian_position=.5)
        def render():
            return ET.fromstring(render_scene(state, assets=assets))
        def glow(root):
            return float(root.find(".//svg:filter[@id='israeli-logo-0-zone-glow']/svg:feDropShadow", ns).attrib['flood-opacity'])
        solo = render()
        icon = solo.find("svg:g[@id='israeli']/svg:g[@data-icon-zone='reconciliation']", ns)
        self.assertAlmostEqual(float(icon.attrib['data-scale']), 1.25)
        state['palestinian_position'] = 0
        both = render()
        self.assertGreater(glow(both), glow(solo))
        state['palestinian_y'] = -400
        self.assertEqual(glow(render()), glow(solo))

    def test_alpha_export_omits_only_background(self):
        assets = {name: filename for name, filename in ASSET_FILES.items()}
        state = state_at(self.timeline, 14)
        opaque = render_scene(state, assets=assets)
        alpha = render_scene(state, assets=assets, transparent=True)
        ns = {"svg": "http://www.w3.org/2000/svg"}
        self.assertIsNotNone(ET.fromstring(opaque).find("svg:rect", ns))
        self.assertIsNone(ET.fromstring(alpha).find("svg:rect", ns))
        self.assertIn('smotrich_and_bibi.png', alpha)


if __name__ == '__main__':
    unittest.main()
