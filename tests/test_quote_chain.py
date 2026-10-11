"""Each quote reveals over its audio duration; the next speaker then appears above, over their target.

When the next quote's target isn't the previous speaker, the camera pans left to a new strip instead."""

import re
import unittest
import xml.etree.ElementTree as ET

from animation_scene import render_scene
from animation_timeline import load_scene, state_at
from export_video import parse_options
from quote_chain_scene import PAN

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
        return tuple(map(float, re.search(r"translate\((\S+) (\S+)\)", transform).groups()))

    def breaks(self):
        """Indices of quotes whose target isn't the previous quote's speaker.

        The closing speaker counts as one more, reprising the first quote."""
        quotes = self.timeline["quotes"]
        closing = self.timeline.get("closing_speaker")
        if closing == quotes[0]["speaker"]:
            quotes = quotes + [dict(quotes[0])]
        return [i for i in range(1, len(quotes)) if quotes[i]["about"] != quotes[i - 1]["speaker"]]

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

    def test_camera_scrolls_up_or_pans_left_once_per_quote(self):
        first, second = self.schedule[:2]
        self.assertEqual(self.camera(first["end"]), (0, 0))
        _, step = self.camera(second["start"])
        self.assertGreater(step, 0)
        breaks = len(self.breaks())
        self.assertGreater(breaks, 0, "The sample chain has breaks to test")
        pan, rise = self.camera(self.timeline["duration"])
        self.assertAlmostEqual(rise, step * (len(self.schedule) - breaks))
        self.assertAlmostEqual(pan, PAN * breaks)

    def face_x(self, time, name):
        return [float(re.search(r"translate\((\S+) ", g.get("transform")).group(1))
                for g in self.render(time).iter(SVG + "g") if g.get("id") == f"face-{name}"]

    def test_chain_opens_with_the_first_target_below(self):
        ids = self.ids(self.timeline["timing"]["intro"])
        self.assertIn("face-ben_gvir", ids)
        self.assertIn("face-netanyahu", ids)

    def test_a_chain_break_pans_left_to_a_new_strip(self):
        index = [i for i in self.breaks() if i < len(self.schedule)][-1]
        before, during = self.schedule[index - 1], self.schedule[index]
        quote = self.timeline["quotes"][index]
        pan_before, rise_before = self.camera(before["end"])
        pan_after, rise_after = self.camera(during["start"])
        self.assertGreater(pan_after, pan_before, "The camera pans left")
        self.assertEqual(rise_after, rise_before, "and doesn't scroll up")
        # On screen, the new speaker and target sit where the previous ones were.
        target_x = [x + pan_after for x in self.face_x(during["start"], quote["about"])]
        speaker_x = [x + pan_after for x in self.face_x(during["start"], quote["speaker"])]
        self.assertIn(360, target_x)
        self.assertIn(360, speaker_x)

    def test_a_person_shared_across_a_break_holds_still(self):
        from quote_chain_scene import build_timeline
        keys = ("scene", "fps", "width", "height", "speakers", "parties")
        quote = dict(text="ציטוט", source="test", duration=2)
        timeline = build_timeline({key: self.timeline[key] for key in keys} | {"quotes": [
            dict(quote, speaker="netanyahu", about="ben_gvir"),
            dict(quote, speaker="netanyahu", about="saar"),  # Same speaker
            dict(quote, speaker="smotrich", about="saar"),  # Same target
        ]})

        def on_screen(time, name):
            svg = ET.fromstring(render_scene(state_at(timeline, time), assets={}))
            pan = float(re.search(r"translate\((\S+) ", next(
                g for g in svg.iter(SVG + "g") if g.get("font-family")).get("transform")).group(1))
            return [round(float(re.search(r"translate\((\S+) ", g.get("transform")).group(1)) + pan, 6)
                    for g in svg.iter(SVG + "g") if g.get("id") == f"face-{name}"]

        for index, (shared, panned) in enumerate((("netanyahu", "ben_gvir"), ("saar", "netanyahu"))):
            s = timeline["schedule"][index]
            for time in (s["scroll"], (s["scroll"] + s["scroll_end"]) / 2, s["scroll_end"]):
                with self.subTest(shared=shared, time=time):
                    self.assertEqual(on_screen(time, shared), [360])
            self.assertNotIn(360, on_screen((s["scroll"] + s["scroll_end"]) / 2, panned))

    def test_chain_closes_on_the_first_speaker_and_quote(self):
        ids = self.ids(self.timeline["duration"])
        self.assertEqual(ids.count("face-netanyahu"), 3)
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
