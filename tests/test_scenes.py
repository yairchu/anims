import io
import json
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from animation_preview import make_handler
from animation_scene import ASSET_FILES, render_scene
from animation_timeline import load_scene, state_at
from video_formats import FORMATS


class SceneTests(unittest.TestCase):
    def setUp(self):
        self.assets = dict(ASSET_FILES)
        self.blocked = load_scene('blocked')
        self.full = load_scene('full')

    def test_blocked_possibility_never_moves_actual_needle(self):
        for frame in range(361):
            state = state_at(self.blocked, frame / 30)
            self.assertEqual(state['israeli_position'], .5)
        before = state_at(self.blocked, 5)
        after = state_at(self.blocked, 10)
        self.assertLess(before['potential_position'], before['israeli_position'])
        self.assertGreater(before['potential_opacity'], 0)
        self.assertEqual(after['potential_opacity'], 0)
        self.assertEqual(after['partnership'], 0)
        self.assertEqual(after['outcome'], 1)

    def test_sequence_boundaries_and_clamping(self):
        self.assertEqual(self.full['duration'], 38.5)
        self.assertEqual(state_at(self.full, 11.99)['scene'], 'blocked')
        self.assertEqual(state_at(self.full, 12)['scene'], 'transition')
        self.assertEqual(state_at(self.full, 13.49)['scene'], 'transition')
        self.assertEqual(state_at(self.full, 13.5)['scene'], 'escalation')
        self.assertEqual(state_at(self.full, -10), state_at(self.full, 0))
        self.assertEqual(state_at(self.full, 100), state_at(self.full, 38.5))
        expected = state_at(self.full, 18.5)
        state_at(self.full, 1)
        self.assertEqual(expected, state_at(self.full, 18.5))
        self.assertEqual(expected['israeli_position'], state_at(load_scene('escalation'), 5)['israeli_position'])
        self.assertEqual(self.full['chapters'][5]['time'], 13.5)

    def test_embedded_sequence_can_be_serialized_for_export(self):
        snapshot = json.loads(json.dumps(self.full))
        for time in (0, 5, 12.7, 13.5, 30, 38.5):
            self.assertEqual(state_at(snapshot, time), state_at(self.full, time))

    def test_scene_artwork_and_optional_portraits(self):
        state = state_at(self.blocked, 7.2)
        svg = render_scene(state, assets=self.assets)
        self.assertNotIn('id="palestinian"', svg)
        self.assertNotIn('smotrich_and_bibi.png', svg)
        self.assertIn('id="potential-needle"', svg)
        for actor in ('netanyahu', 'abbas', 'smotrich'):
            self.assertIn(f'id="actor-{actor}"', svg)
        portraits = self.assets | {'abbas': 'custom-abbas.png'}
        self.assertIn('custom-abbas.png', render_scene(state, assets=portraits))
        ns = {'s': 'http://www.w3.org/2000/svg'}
        for width, height in FORMATS.values():
            for scene, times in ((self.blocked, (0, 3, 7.2, 12)), (self.full, (12, 12.7, 13.5, 38.5))):
                for time in times:
                    root = ET.fromstring(render_scene(state_at(scene, time), assets=self.assets,
                                                     width=width, height=height, transparent=True))
                    self.assertIsNone(root.find('s:rect', ns))
                    _, _, w, h = map(float, root.attrib['viewBox'].split())
                    self.assertAlmostEqual(w / h, width / height)

    def request(self, path, **kwargs):
        # Exercise the real HTTP handler without opening a listening socket.
        handler = object.__new__(make_handler(**kwargs))
        handler.path = path
        handler.wfile = io.BytesIO()
        handler.send_response = lambda status: None
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        errors = []
        handler.send_error = lambda code, *args: errors.append(code)
        handler.do_GET()
        return handler.wfile.getvalue(), errors

    def test_preview_routes_select_scene_and_reject_unknown_scene(self):
        body, errors = self.request('/scenes')
        self.assertFalse(errors)
        self.assertEqual(json.loads(body)['selected'], 'blocked')
        for scene, duration in (('blocked', 12), ('escalation', 25), ('full', 38.5)):
            body, errors = self.request('/config?scene=' + scene)
            self.assertFalse(errors)
            self.assertEqual(json.loads(body)['duration'], duration)
            body, errors = self.request('/frame?scene=' + scene + '&t=5&format=landscape')
            self.assertFalse(errors)
            ET.fromstring(body)
        self.assertEqual(self.request('/frame?scene=missing')[1], [400])
        self.assertEqual(self.request('/frame?scene=blocked&t=nan')[1], [400])

    def test_new_portrait_is_available_to_preview_and_embedding(self):
        from animation_scene import available_asset_files
        with patch('animation_scene.Path.is_file', return_value=True):
            self.assertEqual(available_asset_files()['abbas'], 'abbas.png')
        with patch('animation_scene.Path.is_file', return_value=False):
            self.assertNotIn('abbas', available_asset_files())


if __name__ == '__main__':
    unittest.main()
