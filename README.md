# Political spectrum animation

The notebook has one preview with **Scene**, **Manual / Timeline**, and **Video format** controls. It opens on the blocked-partnership timeline. Both modes use the same scene renderer as export. In a live notebook, SVG frames refer to images served by marimo rather than embedding their bytes. An independent asset-loading cell keeps the URLs alive across scrubbing; rerun that cell after replacing portraits. Script/static exports retain marimo’s portable data-URL fallback.

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

Choose **Manual** to experiment with individual sliders, or **Timeline** to scrub the complete animation. Switching modes preserves manual edits and timeline position; manual edits do not write keyframes. The Israeli Y slider now uses the same direct 0–300 offset as the timeline. Color pickers apply in both modes; the displayed export command includes the selected colors.

The format dropdown defaults to **Instagram portrait, 9:16 (1080×1920)**. **Landscape, 16:9 (1920×1080)** is also available. Changing format keeps the animation timing unchanged. The notebook shows the matching export command; choosing a preview format does not rewrite `timeline.json`.

For playback, speed controls, scrubbing, and chapter jumps:

```sh
uv run python animation_preview.py
```

Open http://127.0.0.1:8765. This server listens only on localhost. The playback server reads timeline files on each request; reload its page after changing durations or chapter markers. It requires permission to bind a local port. Browser preview and native export share SVG artwork; very small differences in font/filter rendering are possible.

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

A left wedge brightens when its needle enters. When both visible meters enter, both brighten further and a soft green connection appears between them. Amber shading increases as each needle advances into its right zone. The corresponding icon smoothly grows up to 125% and gains a matching glow as the needle moves deeper into either zone. Both left icons receive an extra shared glow during reconciliation. The effect reverses on exit and remains deterministic when scrubbing.

Manual mode exposes boundary sliders; their settings also apply when you switch to Timeline. The displayed export command includes them. CLI equivalents: `--reconciliation-end 0.25 --right-zone-start 0.8`. These are illustrative thresholds, not measured political probabilities.

## Scenes and the full sequence

Choose **Blocked partnership** (12 seconds), **Escalation** (the existing 25-second animation), or **Full sequence** (38.5 seconds including a 1.5-second transition). The scene dropdown is available in both the notebook and the playback preview. Each selection remembers its scrub position. Chapter navigation jumps to a beat; switching scenes does not reset manual sliders. Full sequence always uses timeline controls.

The blocked-partnership scene introduces Netanyahu and Mansur Abbas, draws a possible partnership, and moves a dashed green *potential* needle left. Smotrich enters, the partnership is crossed out, and the possibility fades. The actual needle stays at its original position throughout. The Palestinian meter is absent in this introduction. Manual controls let you adjust the actors, partnership, blocking mark, potential needle, and final caption independently.

The notebook watches all three JSON files with `mo.watch.file`: saving edits automatically reloads the animation data (with automatic cell execution enabled), without restarting.

- `timeline_blocked.json`: introduction timing and motion, including the seven additional actor/possibility tracks.
- `timeline.json`: existing escalation scene, kept independently editable.
- `sequence.json`: scene order and the transition title/duration. Fade timing at joins is 0.4 seconds; standalone timelines have no join fades.

The introduction uses the portraits `netanyahu.png`, `mansur_abbas.png`, and `smotrich.png` beside `animation_scene.py`, with transparent outer backgrounds and their cream circular backdrops preserved. Each is optional: missing portraits keep their silhouette. Artwork fits inside a 110×110 box with the name beneath it; use consistently cropped busts with a little transparent padding. Newly added or replaced images appear on the next render. The existing combined portrait remains in the escalation scene.

Export either scene or the complete sequence:

```sh
uv run python export_video.py --scene blocked --output output/blocked.mp4
uv run python export_video.py --scene escalation --output output/escalation.mp4
uv run python export_video.py --scene full --format portrait --output output/full.mp4
```

`--scene` and `--timeline` are alternatives; `--timeline path.json` loads a custom standalone scene. For compatibility, export without either option still selects escalation. The browser preview starts with the introduction; use `--scene full` to start on the full sequence. Export sidecars include all resolved timelines and transition settings. Manual sliders are for visual experiments and do not write timeline keyframes; export renders the selected timeline.

Colors can also be set with `--israeli-color '#0056d6' --palestinian-color '#149149' --needle-color '#7a7a7a'`.

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
