"""Render exact SVG frames with resvg and encode an MP4 or transparent ProRes MOV."""

import json
import math
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

import moops
import resvg_py

from animation_inputs import (
    layout_controls,
    boundary_controls,
    color_controls,
    format_control,
    scene_control,
)
from animation_scene import render_scene
from animation_timeline import load_scene, state_at
from video_formats import FORMATS
from scene_defaults import DEFAULT_EXPORT_SCENE


def parse_options(argv=None):
    """Resolve the same moops controls used by the notebook, plus export inputs."""
    group = moops.Group(argv)
    reconciliation_end, right_zone_start = boundary_controls(group)
    israeli_color, palestinian_color, needle_color = color_controls(group)
    endpoint_text_size, zone_text_size, meter_spacing = layout_controls(group)
    controls = dict(
        endpoint_text_size=endpoint_text_size,
        zone_text_size=zone_text_size,
        meter_spacing=meter_spacing,
        reconciliation_end=reconciliation_end,
        right_zone_start=right_zone_start,
        israeli_color=israeli_color,
        palestinian_color=palestinian_color,
        needle_color=needle_color,
        scene=scene_control(group),
        timeline=group.text(
            option="--timeline", help_text="Custom standalone timeline JSON"
        ),
        output=group.text(
            value="output/political-spectrum.mp4",
            option="--output",
            help_text="Output video path",
        ),
        transparent=group.checkbox(
            flag="--transparent",
            help_text="ProRes 4444 with alpha; requires .mov output",
        ),
        format=format_control(group),
        width=group.number(
            option="--width",
            help_text="Output width (otherwise use preset or timeline)",
        ),
        height=group.number(
            option="--height",
            help_text="Output height (otherwise use preset or timeline)",
        ),
        fps=group.number(
            option="--fps", help_text="Frames per second (otherwise use timeline)"
        ),
        start=group.number(
            value=0,
            allow_none=False,
            option="--start",
            help_text="First time to render, in seconds",
        ),
        end=group.number(
            option="--end",
            help_text="Last time to render (otherwise use timeline duration)",
        ),
        stills=group.text(
            option="--stills", help_text="Also save chapter frames in this directory"
        ),
        overwrite=group.checkbox(
            flag="--overwrite", help_text="Replace an existing output"
        ),
    )
    group.interface(*controls.values())
    args = SimpleNamespace(
        **{name: control.value for name, control in controls.items()}
    )
    for name in ("endpoint_text_size", "zone_text_size", "meter_spacing"):
        if not math.isfinite(getattr(args, name)):
            option = name.replace("_", "-")
            raise ValueError(f"--{option} must be finite")
    if args.timeline and args.scene is not None:
        raise ValueError("Use either --scene or --timeline, not both")
    if not args.output:
        raise ValueError("--output must be a nonempty path")
    args.scene = args.scene or DEFAULT_EXPORT_SCENE
    for name in ("timeline", "output", "stills"):
        value = getattr(args, name)
        setattr(args, name, Path(value) if value else None)
    for name in ("width", "height"):
        value = getattr(args, name)
        if value is not None:
            if not math.isfinite(value) or value != int(value):
                raise ValueError(f"--{name} must be an integer")
            setattr(args, name, int(value))
    if not 0 < args.reconciliation_end < args.right_zone_start < 1:
        raise ValueError(
            "Zone boundaries must satisfy 0 < reconciliation-end < right-zone-start < 1"
        )
    return args


def encode_video(draw_svg, *, output, fps, start, end, transparent=False,
                 overwrite=False, stills=None, chapters=()):
    """Rasterize draw_svg(time) for each frame and encode an MP4 or alpha MOV."""
    suffix = ".mov" if transparent else ".mp4"
    if output.suffix.lower() != suffix:
        raise ValueError(f"This export mode requires a {suffix} output")
    if output.exists() and not overwrite:
        raise ValueError("Output already exists; use --overwrite to replace it")
    if not shutil.which("ffmpeg"):
        raise ValueError("FFmpeg is required (on macOS: brew install ffmpeg)")
    output.parent.mkdir(parents=True, exist_ok=True)
    frames = math.ceil((end - start) * fps)
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:

        @lru_cache(maxsize=2)
        def rasterize(svg):
            return resvg_py.svg_to_bytes(svg_string=svg, font_family="Arial")

        def draw(time):
            return rasterize(draw_svg(time))

        if stills:
            stills.mkdir(parents=True, exist_ok=True)
            for i, chapter in enumerate(chapters):
                (stills / f"{i:02d}-{chapter['time']:05.2f}.png").write_bytes(
                    draw(chapter["time"] + 0.5)
                )
        temp_output = Path(tmp) / ("render" + suffix)
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "image2pipe",
            "-vcodec",
            "png",
            "-framerate",
            str(fps),
            "-i",
            "pipe:0",
            "-an",
        ]
        if transparent:
            command += [
                "-c:v",
                "prores_ks",
                "-profile:v",
                "4",
                "-pix_fmt",
                "yuva444p10le",
            ]
        else:
            command += [
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
            ]
        command += [str(temp_output)]
        # Stream frames instead of leaving thousands of intermediate PNGs on disk.
        with tempfile.TemporaryFile() as errors:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=errors)
            try:
                for index in range(frames):
                    process.stdin.write(draw(start + index / fps))
                    if index % max(1, round(fps)) == 0:
                        print(f"Rendering {index + 1}/{frames} frames", flush=True)
                process.stdin.close()
                if process.wait() != 0:
                    errors.seek(0)
                    raise RuntimeError(errors.read().decode())
            except BrokenPipeError as error:
                process.wait()
                errors.seek(0)
                raise RuntimeError(
                    "FFmpeg stopped encoding: " + errors.read().decode()
                ) from error
            finally:
                if not process.stdin.closed:
                    process.stdin.close()
                if process.poll() is None:
                    process.kill()
                    process.wait()
        temp_output.replace(output)
    return frames


def main():
    args = parse_options()
    config = load_scene(args.scene, args.timeline)
    preset_width, preset_height = (
        FORMATS[args.format] if args.format else (config["width"], config["height"])
    )
    width = args.width if args.width is not None else preset_width
    height = args.height if args.height is not None else preset_height
    fps = args.fps if args.fps is not None else config["fps"]
    end = args.end if args.end is not None else config["duration"]
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise ValueError("Width and height must be positive even integers")
    if (
        not math.isfinite(fps)
        or fps <= 0
        or not 0 <= args.start < end <= config["duration"]
    ):
        raise ValueError("Use a positive fps and 0 <= start < end <= timeline duration")

    def draw_svg(time):
        return render_scene(
            state_at(config, time),
            width=width,
            height=height,
            transparent=args.transparent,
            israeli_color=args.israeli_color,
            palestinian_color=args.palestinian_color,
            needle_color=args.needle_color,
            reconciliation_end=args.reconciliation_end,
            right_zone_start=args.right_zone_start,
            endpoint_text_size=args.endpoint_text_size,
            zone_text_size=args.zone_text_size,
            meter_spacing=args.meter_spacing,
        )

    frames = encode_video(
        draw_svg,
        output=args.output,
        fps=fps,
        start=args.start,
        end=end,
        transparent=args.transparent,
        overwrite=args.overwrite,
        stills=args.stills,
        chapters=config["chapters"],
    )
    (args.output.with_suffix(args.output.suffix + ".json")).write_text(
        json.dumps(
            {
                "timeline": config,
                "israeli_color": args.israeli_color,
                "palestinian_color": args.palestinian_color,
                "needle_color": args.needle_color,
                "width": width,
                "height": height,
                "fps": fps,
                "start": args.start,
                "end": end,
                "frames": frames,
                "transparent": args.transparent,
                "reconciliation_end": args.reconciliation_end,
                "right_zone_start": args.right_zone_start,
                "endpoint_text_size": args.endpoint_text_size,
                "zone_text_size": args.zone_text_size,
                "meter_spacing": args.meter_spacing,
            },
            indent=2,
        )
    )
    print(f"Saved {args.output.resolve()} ({frames} frames)")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error)) from error
