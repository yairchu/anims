"""Each quote reveals over its audio duration; the next speaker then appears above, over their target."""

import re
import unittest
import xml.etree.ElementTree as ET

from animation_scene import render_scene
from animation_timeline import load_scene, state_at
from export_video import parse_options

SVG = "{http://www.w3.org/2000/svg}"


class QuoteChainTests(unittest.TestCase):
    def setUp(self):
        self.timeline = load_scene("quote_chain")
        self.schedule = self.timeline["schedule"]

    def render(self, time):
        return ET.fromstring(render_scene(state_at(self.timeline, time), assets={}))

    def ids(self, time):
        return [element.get("id") for element in self.render(time).iter() if element.get("id")]

    def camera(self, time):
        transform = next(g for g in self.render(time).iter(SVG + "g") if g.get("font-family")).get("transform")
        return float(re.search(r"translate\(0 (\S+)\)", transform).group(1))

    def test_quotes_follow_their_audio_durations(self):
        for quote, s in zip(self.timeline["quotes"], self.schedule):
            self.assertAlmostEqual(s["end"] - s["start"], quote["duration"])
        # An opening chapter, one per quote, and the closing.
        self.assertEqual(len(self.timeline["chapters"]), len(self.schedule) + 2)

    def test_next_speaker_appears_above_after_the_quote(self):
        first = self.schedule[0]
        self.assertNotIn("face-smotrich", self.ids(first["end"]))
        self.assertIn("quote-0", self.ids(first["start"]))
        self.assertIn("face-smotrich", self.ids(first["scroll_end"]))
        self.assertNotIn("quote-0", self.ids(first["scroll_end"]), "The spoken quote fades as it scrolls away")
        speaker, target = (float(re.search(r"translate\(360 (\S+)\)", self.render(first["scroll_end"])
                                           .find(f".//*[@id='face-{name}']").get("transform")).group(1))
                           for name in ("smotrich", "netanyahu"))
        self.assertLess(speaker, target, "Smotrich appears above Netanyahu")

    def test_camera_scrolls_one_speaker_per_quote(self):
        first, second = self.schedule[:2]
        self.assertEqual(self.camera(first["end"]), 0)
        step = self.camera(second["start"])
        self.assertGreater(step, 0)
        self.assertAlmostEqual(self.camera(self.timeline["duration"]), step * len(self.schedule))

    def test_chain_closes_on_the_first_speaker_and_quote(self):
        ids = self.ids(self.timeline["duration"])
        self.assertEqual(ids.count("face-netanyahu"), 2)
        self.assertIn("quote-reprise", ids)

    def test_long_quotes_fit_three_lines(self):
        long_quote = ("מילא להחרים אירועים בהשתתפותי ולהתבייש להצטלם איתי, "
                      "אבל גם הקריאה הנרגשת לאחדות היא בכלל משחק ציני?!")
        timeline = dict(self.timeline, quotes=[dict(q, text=long_quote) for q in self.timeline["quotes"]])
        quote = ET.fromstring(render_scene(state_at(timeline, self.schedule[0]["end"]), assets={})
                              ).find(".//*[@id='quote-0']")
        quote_lines = [t for t in quote.iter(SVG + "text") if t.get("font-weight") == "700"][1:]
        self.assertLessEqual(len(quote_lines), 3)

    def test_unknown_speaker_is_rejected(self):
        from quote_chain_scene import build_timeline
        data = dict(self.timeline, quotes=[dict(self.timeline["quotes"][0], speaker="nobody")])
        with self.assertRaises(ValueError):
            build_timeline(data)

    def test_exporter_accepts_the_scene(self):
        args = parse_options(["export_video.py", "--scene", "quote_chain", "--output", "output/q.mp4"])
        self.assertEqual(args.scene, "quote_chain")


if __name__ == "__main__":
    unittest.main()
