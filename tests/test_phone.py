"""Check the overlay's compositing contract and shared export path."""

import subprocess
import unittest
import xml.etree.ElementTree as ET

import numpy as np
import resvg_py

from animation_scene import render_scene
from animation_timeline import load_scene, state_at
from export_video import parse_options


class PhoneTests(unittest.TestCase):
    def test_notification_can_be_scrubbed_and_returns_to_original_interface(self):
        timeline = load_scene("phone")
        render = lambda t: render_scene(state_at(timeline, t), transparent=True)
        held = render(3)
        self.assertIsNotNone(ET.fromstring(held).find(".//*[@id='notification']"))
        self.assertIsNotNone(ET.fromstring(render(6.35)).find(".//*[@id='touch']"))
        # The banner leaves no trace; only the later like changes the reel.
        unliked = lambda t: render_scene(state_at(timeline, t) | {"like": 0, "like_touch": 0}, transparent=True)
        self.assertEqual(render(0), unliked(9))
        self.assertNotEqual(render(0), render(9))
        self.assertEqual(held, render(3))
        args = parse_options(["export_video.py", "--scene", "phone", "--transparent", "--output", "output/phone.mov"])
        self.assertEqual(args.scene, "phone")
        self.assertTrue(args.transparent)

    def test_actual_raster_has_clear_video_and_caption_areas(self):
        timeline = load_scene("phone")
        for time in (0, 3, 6.4, 9):
            svg = render_scene(state_at(timeline, time), width=720, height=1280, transparent=True)
            png = resvg_py.svg_to_bytes(svg_string=svg, font_family="Arial")
            rgba = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "rawvideo", "-pix_fmt", "rgba", "pipe:1"],
                input=png, capture_output=True, check=True,
            ).stdout
            alpha = np.frombuffer(rgba, dtype=np.uint8).reshape(1280, 720, 4)[:, :, 3]
            self.assertEqual(int(alpha[350:500, 250:450].max()), 0, "Video window must stay transparent")
            self.assertEqual(int(alpha[960:, 440:].max()), 0, "Caption area beside the hand must stay transparent")
            self.assertEqual(int(alpha[1200, 40]), 255, "The hand holds the phone from the bottom left")
            self.assertEqual(int(alpha[0:30, :].max()), 0, "Outside phone must stay transparent")
            self.assertEqual(int(alpha[880, 360]), 255, "Navigation bar must remain opaque")
            if time == 3:
                self.assertGreater(int(alpha[180, 360]), 230, "Notification must cover underlying footage")


if __name__ == "__main__":
    unittest.main()
