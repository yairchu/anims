"""Integration checks for the independent notebook and shared rendering path."""

import io
import json
import shlex
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from unittest.mock import patch

import moops
from marimo._runtime.virtual_file import VirtualFileLifecycleItem

from animation_preview import make_handler
from animation_scene import available_asset_files, render_scene
from animation_timeline import load_scene, state_at
from export_video import parse_options
from tunnels_2014 import app


NS = {"s": "http://www.w3.org/2000/svg"}


class TunnelsTests(unittest.TestCase):
    def test_bennett_stays_right_through_every_frame_and_seeking_is_repeatable(self):
        timeline = load_scene("tunnels")
        assets = available_asset_files()
        for frame in range(34 * 30 + 1):
            root = ET.fromstring(render_scene(state_at(timeline, frame/30), assets=assets))
            actors = {
                node.get("id"): tuple(map(float, node.get("transform")[10:-1].split()))
                for node in root.iter()
                if node.get("id", "").startswith("actor-")
            }
            bx = actors["actor-bennett"][0]
            self.assertGreater(bx, 500)
            self.assertTrue(all(bx > xy[0] for name, xy in actors.items() if name != "actor-bennett"))
        forward = render_scene(state_at(timeline, 15.5), assets=assets)
        state_at(timeline, 30)
        self.assertEqual(forward, render_scene(state_at(timeline, 15.5), assets=assets))

    def test_clip_export_matches_notebook_frame_and_uses_stable_asset_urls(self):
        files = {}
        registry = SimpleNamespace(
            has=lambda name: name in files,
            add=lambda file, ctx: files.update({file.filename: file}),
        )
        context = SimpleNamespace(virtual_files_supported=True, virtual_file_registry=registry)
        with patch.object(VirtualFileLifecycleItem, "add_to_cell_lifecycle_registry", lambda item: item.create(context)):
            _, values = app.run(defs={"args": moops.Group.with_overrides({
                "clip": "2026", "time": 5, "format": "panel", "transparent": True,
            })})
        self.assertEqual(values["absolute_time"], 29)
        self.assertEqual(set(values["preview_assets"]), {"netanyahu", "gantz", "winter", "bennett"})
        self.assertTrue(all(url.startswith("./@file/") for url in values["preview_assets"].values()))
        self.assertNotIn("data:image", values["scene_svg"])
        self.assertLess(len(values["scene_svg"]), 20_000)
        asset_cell = next(cell for cell in app._graph.cells.values() if "preview_assets" in cell.defs)
        self.assertEqual(asset_cell.refs, {"notebook_asset_urls"})
        args = parse_options(shlex.split(values["export_command"])[3:])
        self.assertEqual((args.start, args.end, args.width, args.height), (24, 34, 960, 1080))
        self.assertTrue(args.transparent)
        expected = render_scene(
            state_at(load_scene(args.scene), args.start + 5), assets=values["preview_assets"],
            width=args.width, height=args.height, transparent=args.transparent,
        )
        self.assertEqual(values["scene_svg"], expected)
        root = ET.fromstring(expected)
        self.assertIsNone(root.find("s:rect", NS))

    def test_browser_preview_uses_same_scene_and_new_portraits(self):
        handler = object.__new__(make_handler(scene="tunnels"))
        handler.path = "/frame?scene=tunnels&t=17.5&format=landscape"
        handler.wfile = io.BytesIO()
        handler.send_response = lambda status: self.assertEqual(status, 200)
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.send_error = lambda *args: self.fail(str(args))
        handler.do_GET()
        svg = handler.wfile.getvalue().decode()
        root = ET.fromstring(svg)
        self.assertEqual((root.get("width"), root.get("height")), ("1920", "1080"))
        for name in ("netanyahu", "gantz", "winter", "bennett"):
            self.assertIn(f'/assets/{name}.png', svg)

    def test_halfway_information_line_ends_at_the_document(self):
        root = ET.fromstring(render_scene(state_at(load_scene("tunnels"), 15.5), assets={}))
        contact = root.find(".//s:g[@id='direct-contact']", NS)
        reply = [node for node in contact.findall("s:path", NS) if node.get("stroke") == "#b77924"][0]
        endpoint = tuple(map(float, reply.get("d").split()[-2:]))
        doc = contact.find("s:g", NS)
        position = tuple(map(float, doc.get("transform").split(")")[0][10:].split()))
        self.assertEqual(endpoint, position)
        self.assertLess(endpoint[0], 699)  # It must not already reach Bennett.


if __name__ == "__main__":
    unittest.main()
