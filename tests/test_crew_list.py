"""The crew list travels airline → authority → bin, leaving the caption area clear."""

import math
import subprocess
import unittest
import xml.etree.ElementTree as ET

import numpy as np
import resvg_py

import crew_list_scene as scene
from animation_scene import render_scene
from tunnels_scene import cubic
from animation_timeline import load_scene, state_at
from export_video import parse_options

SVG = "{http://www.w3.org/2000/svg}"


def alpha_at(timeline, time, **overrides):
    svg = render_scene(state_at(timeline, time) | overrides, width=720, height=1280, transparent=True)
    png = resvg_py.svg_to_bytes(svg_string=svg, font_family="Arial")
    rgba = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "rawvideo", "-pix_fmt", "rgba", "pipe:1"],
        input=png, capture_output=True, check=True,
    ).stdout
    return np.frombuffer(rgba, dtype=np.uint8).reshape(1280, 720, 4)[:, :, 3]


class CrewListTests(unittest.TestCase):
    def setUp(self):
        self.timeline = load_scene("crew_list")

    def render(self, time, **overrides):
        return ET.fromstring(render_scene(state_at(self.timeline, time) | overrides, transparent=True))

    def test_flagged_crew_member_is_on_the_list(self):
        crew_list = self.render(5).find(".//*[@id='crew-list']")
        self.assertIsNotNone(crew_list)
        dark_heads = [e for e in crew_list.iter(SVG + "ellipse") if e.get("fill") == "#1d1f24"]
        self.assertEqual(len(dark_heads), 1, "Exactly one masked crew member")

    def test_list_is_filed_behind_the_authority_then_binned(self):
        def ids(time):
            return [element.get("id") for element in self.render(time).iter() if element.get("id")]
        filed = ids(9.5)
        self.assertLess(filed.index("crew-list"), filed.index("agency"), "Filed behind the authority's card")
        self.assertNotIn("bin", filed)
        falling = ids(11.5)
        self.assertGreater(falling.index("crew-list"), falling.index("agency"), "In front once it clears the card")
        binned = ids(13)
        self.assertLess(binned.index("bin-back"), binned.index("crew-list"))
        self.assertEqual(binned[-1], "bin", "The bin's front covers the binned list")

    def test_list_clears_the_largest_cards_on_its_way_to_the_bin(self):
        ids = [element.get("id") for element in self.render(11.5, card_text_scale=1.5).iter()
               if element.get("id")]
        self.assertGreater(ids.index("crew-list"), ids.index("agency"))

    def test_list_enters_the_bin_through_its_opening(self):
        rim = scene.BIN[1] - 58 * scene.BIN_SCALE
        opening = 50 * scene.BIN_SCALE - 4
        for card_scale in (1, 1.5):
            route = scene.discard_route(card_scale)
            for step in range(1001):
                discard = step / 1000
                x, y = cubic(route, discard)
                size = scene.discard_scale(discard)
                angle = math.radians(scene.discard_spin(discard))
                for cx, cy in ((-70, -90), (70, -90), (70, 90), (-70, 90)):
                    px = x + size * (cx * math.cos(angle) - cy * math.sin(angle))
                    py = y + size * (cx * math.sin(angle) + cy * math.cos(angle))
                    if py > rim:
                        self.assertLess(abs(px - scene.BIN[0]), opening,
                                        f"Crosses the bin's wall at discard={discard}, card scale {card_scale}")

    def test_caption_area_stays_clear(self):
        for scale in (1, 1.5):
            for time in (0, 5, 11.4, 14):
                alpha = alpha_at(self.timeline, time, card_text_scale=scale)
                self.assertEqual(int(alpha[950:].max()), 0,
                                 f"Caption area must stay transparent at {time}s, card scale {scale}")

    def test_exporter_accepts_the_scene(self):
        args = parse_options(["export_video.py", "--scene", "crew_list", "--output", "output/crew.mp4"])
        self.assertEqual(args.scene, "crew_list")


if __name__ == "__main__":
    unittest.main()
