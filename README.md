# Political spectrum animation

The notebook has one preview with **Scene**, **Manual / Timeline**, and **Video format** controls. It opens on the meter-introduction timeline. Both modes use the same scene renderer as export. In a live notebook, SVG frames refer to images served by marimo rather than embedding their bytes. An independent asset-loading cell keeps the URLs alive across scrubbing; rerun that cell after replacing portraits. Script/static exports retain marimo’s portable data-URL fallback.

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

## Shared notebook and CLI inputs

The notebook controls and exporter use **moops**. Boundary, color, scene, and format
controls are declared once in `animation_inputs.py`; rendering and those controls
share visual defaults from `scene_defaults.py`. Change `RECONCILIATION_END` there
to update both preview and export (currently `0.2`, symmetric with `0.8`). The CLI
uses the same boundary ranges as the sliders: `0.1–0.45` and `0.55–0.95`.

All notebook inputs are also available as CLI options. For example:

```sh
uv run python hamas_neches.py --help
uv run python hamas_neches.py --scene blocked --blocked-time 4 --reconciliation-end 0.3
uv run python export_video.py --help
```

Running the notebook as a script computes its preview; use `export_video.py` to
write video files. The notebook's **Notebook CLI info** panel reproduces its
current controls. The separate export command renders the selected timeline.
Color pickers and the Manual/Timeline radio retain their notebook UI through
moops custom controls, with equivalent CLI inputs.

## Text size and meter spacing

The notebook exposes **Endpoint font size**, **Zone font size**, and **Meter gap**
in both Manual and Timeline modes. All three use absolute scene units, which
scale with the artwork: one unit is 1.5 pixels in a 1080×1920 export.
Defaults are 33.8, 22.4, and 150 units, respectively.

The gap is measured vertically between the centers of the two facing arcs when
the Palestinian meter's entrance offset is zero. Changing it moves the
Palestinian meter and its attached effects; its timeline/manual Y offset still
controls entrance motion. Text line spacing scales with the font size.

```sh
uv run python export_video.py --scene escalation --endpoint-text-size 33.8 --zone-text-size 22.4 --meter-spacing 150
```

Endpoint size accepts 20–42 units, zone size 12–29, and meter gap 0–240.
The displayed export command and exported JSON include these settings.

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

Both meters have a green reconciliation zone (leftmost 20%) and an amber right-hand zone (rightmost 20%). Labels are **פתח לפיוס** on both left ends, **חלון לסיפוח** on the Israeli right, and **סכנת הסלמה** on the Palestinian right. Palestinian zone labels translate from Arabic along with the main labels.

A left wedge brightens when its needle enters. When both visible meters enter, both brighten further and a soft green connection appears between them. Amber shading increases as each needle advances into its right zone. The corresponding icon smoothly grows up to 125% and gains a matching glow as the needle moves deeper into either zone. Both left icons receive an extra shared glow during reconciliation. The effect reverses on exit and remains deterministic when scrubbing.

Manual mode exposes boundary sliders; their settings also apply when you switch to Timeline. The displayed export command includes them. CLI equivalents: `--reconciliation-end 0.2 --right-zone-start 0.8`. These are illustrative thresholds, not measured political probabilities.

## Scenes and the full sequence

Choose **Meter introduction** (14 seconds), **Blocked partnership** (12 seconds), **Escalation** (25 seconds), or **Full sequence** (52.5 seconds including the later 1.5-second transition). The scene dropdown is available in both the notebook and the playback preview. Each selection remembers its scrub position. Chapter navigation jumps to a beat; switching scenes does not reset manual sliders. Full sequence always uses timeline controls.

The blocked-partnership scene introduces Netanyahu and Mansur Abbas, draws a possible partnership, and moves a dashed green *potential* needle left. Smotrich enters, the partnership is crossed out, and the possibility fades. The actual needle stays at its original position throughout. The Palestinian meter is absent in this introduction. Manual controls let you adjust the actors, partnership, blocking mark, potential needle, and final caption independently.

The notebook watches all four JSON files with `mo.watch.file`: saving edits automatically reloads the animation data (with automatic cell execution enabled), without restarting.

- `timeline_intro.json`: piece-by-piece meter reveal timing.
- `timeline_blocked.json`: partnership timing and motion, including the seven additional actor/possibility tracks.
- `timeline.json`: existing escalation scene, kept independently editable.
- `sequence.json`: scene order and the transition title/duration. `continuous_joins` keeps the introduction → partnership handoff uninterrupted. Other joins use a transition card with 0.4-second fades.

The introduction uses the portraits `netanyahu.png`, `mansur_abbas.png`, and `smotrich.png` beside `animation_scene.py`, with transparent outer backgrounds and their cream circular backdrops preserved. Each is optional: missing portraits keep their silhouette. Artwork fits inside a 110×110 box with the name beneath it; use consistently cropped busts with a little transparent padding. Newly added or replaced images appear on the next render. The existing combined portrait remains in the escalation scene.

Export either scene or the complete sequence:

```sh
uv run python export_video.py --scene blocked --output output/blocked.mp4
uv run python export_video.py --scene escalation --output output/escalation.mp4
uv run python export_video.py --scene full --format portrait --output output/full.mp4
```

`--scene` and `--timeline` are alternatives; `--timeline path.json` loads a custom standalone scene. For compatibility, export without either option still selects escalation. The browser preview starts with the meter introduction; use `--scene full` to start on the full sequence. Export sidecars include all resolved timelines and transition settings. Manual sliders are for visual experiments and do not write timeline keyframes; export renders the selected timeline.

Colors can also be set with `--israeli-color '#0056d6' --palestinian-color '#149149' --needle-color '#7a7a7a'`.

### Meter introduction

The opening contains no actors or Palestinian meter. Its first cut leaves space for narration:

| Seconds | Reveal |
| --- | --- |
| 0–2 | Empty frame for the opening question |
| 2–3 | Left endpoint label and Vegan Friendly logo fade in |
| 5–6 | Right endpoint label and Kach logo fade in |
| 8–10 | Arc draws from right to left, joining the positions |
| 11–12 | Needle fades in |
| 12–14 | Hold on the completed meter |

Edit `right_reveal`, `left_reveal`, `arc_reveal`, and `needle_reveal` in `timeline_intro.json`. Values run from 0 (hidden) to 1 (complete). Each logo follows its endpoint’s reveal, multiplied by `logos_reveal` (default 1). Both remain visible through the handoff. `zones_reveal` stays at 0 in this scene and fades in during the first second of `timeline_blocked.json`. These tracks are optional in other standalone timelines and default to fully visible. Manual introduction controls expose the same reveals and reuse the existing needle-position and meter-Y sliders.

The endpoint text stays consistent with the following scenes: the left label says “everyone deserves rights.” No narration is baked in. At the continuous join, keep the introduction’s final meter position/Y aligned with the partnership’s initial values if you edit them.

```sh
uv run python export_video.py --scene intro --output output/meter-introduction.mp4
```

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
