# Political spectrum animation

The notebook keeps its original manual controls and adds a **Full animation timeline** scrubber. Both use the same meter renderer in `animation_scene.py`.

## Setup

```sh
uv sync
brew install ffmpeg  # if FFmpeg is not installed
```

Video rendering uses resvg (installed by `uv sync`) and FFmpeg. It does not need a browser, API key, or network access after setup. System fonts must include Hebrew and Arabic; Arial is used on macOS. Different system fonts can change text metrics.

## Preview

```sh
uv run marimo edit hamas_neches.py
```

Use the timeline slider at the bottom of the notebook. The original sliders remain a separate manual design preview. Color pickers apply to both notebook views; exported colors currently use the defaults in `render_scene`.

For playback, speed controls, scrubbing, and chapter jumps:

```sh
uv run python animation_preview.py
```

Open http://127.0.0.1:8765. This server listens only on localhost. Reload after changing `timeline.json`. It requires permission to bind a local port. Browser preview and native export share SVG artwork; very small differences in font/filter rendering are possible.

## Export

Silent 25-second, 1920×1080, 30 fps MP4 (white background):

```sh
uv run python export_video.py
```

Transparent ProRes 4444 for compositing in a video editor:

```sh
uv run python export_video.py --transparent --output output/political-spectrum-alpha.mov
```

A short, lower-resolution render for checking changes:

```sh
uv run python export_video.py --start 13 --end 18 --width 960 --height 540 --fps 15 --output output/preview.mp4
```

Add `--stills output/stills` for chapter screenshots, or `--overwrite` to replace a previous export. MP4 cannot carry alpha; transparent exports require `.mov`. Generated videos are ignored by Git. A `.json` sidecar records the exact timeline and export settings used for each video. Completed videos replace the destination only after encoding succeeds.

The alpha export removes the scene background, but deliberately preserves backgrounds inside the individual image assets (such as the portrait's cream circle). No narration, soundtrack, or captions are baked in.

## Edit timing and motion

`timeline.json` contains:

- `duration`, `fps`, `width`, `height`: export defaults.
- `tracks`: lists of `[time_in_seconds, value]` keyframes. Values ease smoothly between keys and hold before/after the key range. Repeat a value at a later time to make a hold.
- `events`: discrete `push`, `cash`, or `knife` animations with a `start` and `duration` in seconds.
- `chapters`: preview navigation markers.

All frames depend only on their timestamp. Seeking backward produces the same result as forward playback, and changing FPS does not change motion timing. The full sequence is currently an editable first cut:

| Seconds | Beat |
| --- | --- |
| 0–3 | Israeli spectrum |
| 3–5 | Portrait enters |
| 5–8 | Two direct nudges; needle returns |
| 8–11 | Israeli meter moves down, Palestinian meter enters |
| 11–13 | Arabic labels blur into Hebrew |
| 13–17 | Cash moves toward the Hamas emblem; Palestinian needle shifts |
| 17–22 | Knives originate at the Hamas emblem; Israeli needle reacts |
| 22–25 | Hold on the political outcome |

The initial needle positions are illustrative and equal. These are editorial animation values, not polling estimates. The sequence does not add a “mission accomplished” quote or claim a documented intention to provoke attacks.

Artwork and paths live in `animation_scene.py`. Timing is independent of artwork. The 600-unit meter design sits within a 720-unit-high scene; landscape output adds side space. Narrow formats fit the whole scene rather than cropping its labels.

## Checks

```sh
uv run python -m unittest discover -s tests -v
uv run marimo check hamas_neches.py
uv run python hamas_neches.py
```
