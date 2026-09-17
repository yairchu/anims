import unittest
import xml.etree.ElementTree as ET

from animation_scene import ASSET_FILES, render_scene
from animation_timeline import load_scene, state_at
from video_formats import FORMATS


class IntroductionTests(unittest.TestCase):
    def setUp(self):
        self.intro = load_scene('intro')
        self.full = load_scene('full')

    def test_reveals_follow_narration(self):
        stages = [(0, (0, 0, 0, 0)), (4, (1, 0, 0, 0)),
                  (7, (1, 1, 0, 0)), (10, (1, 1, 1, 0)), (13, (1, 1, 1, 1))]
        for time, expected in stages:
            state = state_at(self.intro, time)
            self.assertEqual(tuple(state[key] for key in
                                   ('right_reveal', 'left_reveal', 'arc_reveal', 'needle_reveal')), expected)
            self.assertEqual(state['logos_reveal'], 0)
            self.assertEqual(state['zones_reveal'], 0)
        self.assertAlmostEqual(state_at(self.intro, 9)['arc_reveal'], .5)

    def test_continuous_handoff_preserves_meter_exactly(self):
        before = state_at(self.full, self.intro['duration'] - 1e-6)
        after = state_at(self.full, self.intro['duration'])
        self.assertEqual(before['scene'], 'intro')
        self.assertEqual(after['scene'], 'blocked')
        self.assertEqual(before['scene_opacity'], 1)
        self.assertEqual(after['scene_opacity'], 1)
        for width, height in FORMATS.values():
            meters = []
            for state in (before, after):
                root = ET.fromstring(render_scene(state, assets=ASSET_FILES, width=width, height=height))
                meter = root.find("{http://www.w3.org/2000/svg}g/{http://www.w3.org/2000/svg}g[@id='israeli']")
                self.assertIsNotNone(meter)
                meters.append(ET.tostring(meter))
            self.assertEqual(*meters)
        self.assertEqual(after['logos_reveal'], 0)
        self.assertEqual(state_at(self.full, 15)['logos_reveal'], 1)

    def test_intro_artwork_has_no_actors_or_second_meter(self):
        svg = render_scene(state_at(self.intro, 7), assets=ASSET_FILES)
        self.assertNotIn('actor-', svg)
        self.assertNotIn('id="palestinian"', svg)
        self.assertNotIn('smotrich_and_bibi.png', svg)
        root = ET.fromstring(svg)
        ns = {'s': 'http://www.w3.org/2000/svg'}
        self.assertEqual(root.find(".//s:path[@id='israeli-arc']", ns).attrib['opacity'], '0')
        self.assertEqual(float(root.find(".//s:g[@id='israeli-needle']", ns).attrib['opacity']), 0)


if __name__ == '__main__':
    unittest.main()
