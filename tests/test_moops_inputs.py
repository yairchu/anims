"""Exercise shared defaults, CLI overrides, and notebook/renderer agreement."""

import contextlib
import io
import unittest
from unittest.mock import patch

import marimo as mo
import moops

from animation_inputs import color_controls, scene_control
from animation_scene import render_scene
from animation_timeline import load_scene, state_at
from export_video import parse_options
from hamas_neches import app


class MoopsInputTests(unittest.TestCase):
    def test_default_preview_export_and_renderer_agree(self):
        options = parse_options(["export_video.py"])
        _, values = app.run(defs={"args": moops.Group(["hamas_neches.py"])})
        self.assertEqual(options.reconciliation_end, 0.2)
        for option, control in (
            ("reconciliation_end", "reconciliation_boundary"),
            ("right_zone_start", "right_zone_boundary"),
            ("israeli_color", "isr_meter_color_picker"),
            ("palestinian_color", "pal_meter_color_picker"),
            ("needle_color", "needle_color_picker"),
        ):
            self.assertEqual(getattr(options, option), values[control].value)
        state = state_at(load_scene("blocked"), 4)
        shared = {
            key: getattr(options, key)
            for key in (
                "reconciliation_end",
                "right_zone_start",
                "israeli_color",
                "palestinian_color",
                "needle_color",
            )
        }
        self.assertEqual(
            render_scene(state, assets=values["preview_assets"]),
            render_scene(state, assets=values["preview_assets"], **shared),
        )
        self.assertEqual(options.scene, "escalation")
        self.assertIsNone(options.format)
        self.assertEqual(values["scene_choice"].value, "intro")

    def test_overrides_reach_notebook_render_and_export(self):
        flags = [
            "--scene",
            "blocked",
            "--format",
            "landscape",
            "--reconciliation-end",
            "0.3",
            "--right-zone-start",
            "0.7",
            "--israeli-color",
            "#123456",
            "--needle-color",
            "#654321",
        ]
        options = parse_options(["export_video.py", *flags])
        _, values = app.run(
            defs={
                "args": moops.Group(
                    [
                        "hamas_neches.py",
                        *flags,
                        "--blocked-time",
                        "4",
                    ]
                )
            }
        )
        self.assertEqual(
            values["reconciliation_boundary"].value, options.reconciliation_end
        )
        self.assertEqual(values["right_zone_boundary"].value, options.right_zone_start)
        expected = render_scene(
            state_at(load_scene("blocked"), 4),
            assets=values["preview_assets"],
            width=1920,
            height=1080,
            reconciliation_end=options.reconciliation_end,
            right_zone_start=options.right_zone_start,
            israeli_color=options.israeli_color,
            palestinian_color=options.palestinian_color,
            needle_color=options.needle_color,
        )
        self.assertEqual(values["scene_svg"], expected)

    def test_custom_widgets_keep_live_values_and_cli_defaults(self):
        group = moops.Group(["test", "--israeli-color", "#123456"])
        with patch.object(mo, "running_in_notebook", return_value=True):
            israeli, _, _ = color_controls(group)
            scene = scene_control(group, default="intro")
        self.assertEqual(israeli.value, "#123456")
        israeli.widget.color = "#abcdef"
        self.assertEqual(israeli.value, "#abcdef")
        self.assertEqual(scene.value, "intro")
        scene._update(["Blocked partnership"])
        self.assertEqual(scene.value, "blocked")

    def test_reject_invalid_cli_before_export(self):
        for flags in (
            ["--unknown"],
            ["--reconciliation-end", "nan"],
            ["--reconciliation-end", "0.9"],
            ["--scene", "missing"],
            ["--start", "none"],
        ):
            with self.subTest(flags=flags), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises((SystemExit, ValueError)):
                    parse_options(["export_video.py", *flags])
        with self.assertRaisesRegex(ValueError, "either --scene or --timeline"):
            parse_options(
                ["export_video.py", "--scene", "intro", "--timeline", "custom.json"]
            )
        with self.assertRaisesRegex(ValueError, "integer"):
            parse_options(["export_video.py", "--width", "100.5"])

    def test_export_options_preserve_types(self):
        options = parse_options(
            [
                "export_video.py",
                "--timeline",
                "custom.json",
                "--width",
                "320",
                "--height",
                "180",
                "--fps",
                "29.97",
                "--start",
                "1.5",
                "--end",
                "2",
                "--transparent",
                "--output",
                "test.mov",
                "--stills",
                "stills",
                "--overwrite",
            ]
        )
        self.assertEqual(str(options.timeline), "custom.json")
        self.assertIsInstance(options.width, int)
        self.assertEqual(options.fps, 29.97)
        self.assertEqual(options.start, 1.5)
        self.assertTrue(options.transparent)
        self.assertTrue(options.overwrite)


if __name__ == "__main__":
    unittest.main()
