# Political spectrum animation

The notebook has one preview with a **Manual / Timeline** switch and a **Video format** dropdown. Both modes use the same scene renderer as export.

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

Choose **Manual** to experiment with individual sliders, or **Timeline** to scrub the complete animation. Switching modes preserves manual edits and timeline position; manual edits do not write keyframes. The Israeli Y slider now uses the same direct 0–300 offset as the timeline. Color pickers apply in both modes; exported colors currently use the defaults in `render_scene`.

The format dropdown defaults to **Instagram portrait, 9:16 (1080×1920)**. **Landscape, 16:9 (1920×1080)** is also available. Changing format keeps the animation timing unchanged. The notebook shows the matching export command; choosing a preview format does not rewrite `timeline.json`.

For playback, speed controls, scrubbing, and chapter jumps:

```sh
uv run python animation_preview.py
```

Open http://127.0.0.1:8765. This server listens only on localhost. Reload after changing `timeline.json`. It requires permission to bind a local port. Browser preview and native export share SVG artwork; very small differences in font/filter rendering are possible.

## Export

Silent 25-second, 1080×1920, 30 fps portrait MP4 (white background):

```sh
uv run python export_video.py --format portrait --output output/political-spectrum-portrait.mp4
```

Landscape uses the same timeline:

```sh
uv run python export_video.py --format landscape --output output/political-spectrum-landscape.mp4
```

Transparent ProRes 4444 for compositing in a video editor:

```sh
uv run python export_video.py --format portrait --transparent --output output/political-spectrum-portrait-alpha.mov
```

A short, lower-resolution render for checking changes:

```sh
uv run python export_video.py --start 13 --end 18 --width 960 --height 540 --fps 15 --output output/preview.mp4
```

Add `--stills output/stills` for chapter screenshots, or `--overwrite` to replace a previous export. MP4 cannot carry alpha; transparent exports require `.mov`. Generated videos are ignored by Git. A `.json` sidecar records the exact timeline and export settings used for each video. Completed videos replace the destination only after encoding succeeds.

The alpha export removes the scene background, but deliberately preserves backgrounds inside the individual image assets (such as the portrait's cream circle). No narration, soundtrack, or captions are baked in.

## Shaded zones

Both meters have a green reconciliation zone (leftmost 25%) and an amber right-hand zone (rightmost 20%). Labels are **פתח לפיוס** on both left ends, **חלון לסיפוח** on the Israeli right, and **סכנת הסלמה** on the Palestinian right. Palestinian zone labels translate from Arabic along with the main labels.

A left wedge brightens when its needle enters. When both visible meters enter, both brighten further and a soft green connection appears between them. Amber shading increases as each needle advances into its right zone.

Manual mode exposes boundary sliders; their settings also apply when you switch to Timeline. The displayed export command includes them. CLI equivalents: `--reconciliation-end 0.25 --right-zone-start 0.8`. These are illustrative thresholds, not measured political probabilities.

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

Artwork and paths live in `animation_scene.py`. Timing is independent of artwork. The 600-unit meter design sits in a centered composition. Portrait uses a 720-unit-wide canvas with extra vertical room; landscape adds side space. Both formats have an exact matching viewBox, a full-frame background, and offscreen entrances adjusted to the frame. Explicit `--width` and `--height` override preset dimensions.

## Checks

```sh
uv run python -m unittest discover -s tests -v
uv run marimo check hamas_neches.py
uv run python hamas_neches.py
```
