"""Netanyahu vouches for his partners, who call him a liar; then the two ways out of the loop."""

import unittest
import xml.etree.ElementTree as ET

from animation_scene import render_scene
from animation_timeline import load_scene, state_at


class TrustLoopTests(unittest.TestCase):
    def setUp(self):
        self.timeline = load_scene("trust_loop")
        self.starts = self.timeline["starts"]

    def ids(self, time):
        svg = ET.fromstring(render_scene(state_at(self.timeline, time), assets={}))
        return [element.get("id") for element in svg.iter() if element.get("id")]

    def test_beats_follow_each_other(self):
        times = list(self.starts.values())
        self.assertEqual(times, sorted(times))
        self.assertAlmostEqual(self.timeline["duration"], self.starts["outro"] + self.timeline["timing"]["outro"])

    def test_trust_goes_down_before_the_answer_comes_back(self):
        ids = self.ids(self.starts["trust_hold"])
        self.assertIn("trust-arrow", ids)
        self.assertNotIn("liar-arrow", ids)
        for name in [self.timeline["leader"], *self.timeline["partners"]]:
            self.assertIn(f"face-{name}", ids)
        self.assertIn("liar-arrow", self.ids(self.starts["liar_hold"]))

    def test_pulse_runs_only_during_the_loop(self):
        self.assertNotIn("pulse", self.ids(self.starts["liar_hold"]))
        self.assertIn("pulse", self.ids(self.starts["loop"] + 1))
        self.assertNotIn("pulse", self.ids(self.starts["settle"] + .05))

    def test_both_ways_out_end_at_the_verdict(self):
        self.assertNotIn("if_him", self.ids(self.starts["settle"] + .05))
        ids = self.ids(self.timeline["duration"])
        for beat in ("if_him", "if_them", "verdict", "diagram"):
            self.assertIn(beat, ids)


if __name__ == "__main__":
    unittest.main()
