"""Render exact SVG frames with resvg and encode an MP4 or transparent ProRes MOV."""
import argparse
import json
import math
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import resvg_py
from animation_scene import render_scene
from animation_timeline import DEFAULT_TIMELINE, load_timeline, state_at


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeline", type=Path, default=DEFAULT_TIMELINE)
    parser.add_argument("--output", type=Path, default=Path("output/political-spectrum.mp4"))
    parser.add_argument("--transparent", action="store_true", help="ProRes 4444 with alpha; requires .mov output")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--fps", type=float)
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--end", type=float)
    parser.add_argument("--stills", type=Path, help="Also save chapter frames for visual review")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    config = load_timeline(args.timeline)
    width = args.width if args.width is not None else config["width"]
    height = args.height if args.height is not None else config["height"]
    fps = args.fps if args.fps is not None else config["fps"]
    end = args.end if args.end is not None else config["duration"]
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        parser.error("Width and height must be positive even integers")
    if not math.isfinite(fps) or fps <= 0 or not 0 <= args.start < end <= config["duration"]:
        parser.error("Use a positive fps and 0 <= start < end <= timeline duration")
    suffix = ".mov" if args.transparent else ".mp4"
    if args.output.suffix.lower() != suffix:
        parser.error(f"This export mode requires a {suffix} output")
    if args.output.exists() and not args.overwrite:
        parser.error("Output already exists; use --overwrite to replace it")
    if not shutil.which("ffmpeg"):
        parser.error("FFmpeg is required (on macOS: brew install ffmpeg)")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frames = math.ceil((end-args.start)*fps)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as tmp:
        @lru_cache(maxsize=2)
        def rasterize(svg):
            return resvg_py.svg_to_bytes(svg_string=svg, font_family="Arial")

        def draw(time):
            svg = render_scene(state_at(config, time), width=width,
                               height=height, transparent=args.transparent)
            return rasterize(svg)

        if args.stills:
            args.stills.mkdir(parents=True, exist_ok=True)
            for i, chapter in enumerate(config["chapters"]):
                (args.stills/f"{i:02d}-{chapter['time']:05.2f}.png").write_bytes(draw(chapter["time"] + .5))
        temp_output = Path(tmp)/("render"+suffix)
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "image2pipe", "-vcodec", "png",
                   "-framerate", str(fps), "-i", "pipe:0", "-an"]
        if args.transparent:
            command += ["-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le"]
        else:
            command += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
        command += [str(temp_output)]
        # Stream frames instead of leaving thousands of intermediate PNGs on disk.
        with tempfile.TemporaryFile() as errors:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=errors)
            try:
                for index in range(frames):
                    process.stdin.write(draw(args.start + index/fps))
                    if index % max(1, round(fps)) == 0:
                        print(f"Rendering {index+1}/{frames} frames", flush=True)
                process.stdin.close()
                if process.wait() != 0:
                    errors.seek(0)
                    raise RuntimeError(errors.read().decode())
            except BrokenPipeError as error:
                process.wait()
                errors.seek(0)
                raise RuntimeError("FFmpeg stopped encoding: " + errors.read().decode()) from error
            finally:
                if not process.stdin.closed:
                    process.stdin.close()
                if process.poll() is None:
                    process.kill()
                    process.wait()
        temp_output.replace(args.output)
        (args.output.with_suffix(args.output.suffix + ".json")).write_text(json.dumps({
            "timeline": config, "width": width, "height": height, "fps": fps,
            "start": args.start, "end": end, "frames": frames, "transparent": args.transparent,
        }, indent=2))
        print(f"Saved {args.output.resolve()} ({frames} frames)")



if __name__ == "__main__":
    main()
