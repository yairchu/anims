import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    from animation_timeline import load_timeline, state_at
    from phone_scene import render_phone

    timeline_path = Path(__file__).with_name("timeline_phone.json")
    return load_timeline, mo, render_phone, state_at, timeline_path


@app.cell
def _(mo, timeline_path):
    timeline_file = mo.watch.file(timeline_path)
    return (timeline_file,)


@app.cell
def _(load_timeline, timeline_file, timeline_path):
    timeline_file.read_text()
    timeline = load_timeline(timeline_path)
    return (timeline,)


@app.cell
def _(mo, timeline):
    time = mo.ui.slider(start=0, stop=timeline["duration"], step=1/30, value=3, label="Time (seconds)", show_value=True)
    mo.vstack([mo.md("### Phone notification overlay\nTransparent screen for your own reel. Edit labels and timing in `timeline_phone.json`."), time])
    return (time,)


@app.cell
def _(mo, render_phone, state_at, time, timeline):
    scene_svg = render_phone(state_at(timeline, time.value), width=1080, height=1920, transparent=True)
    preview_svg = scene_svg.replace('width="1080" height="1920"', 'width="432" height="768"', 1)
    mo.Html('<div style="width:432px;max-width:100%;background:repeating-conic-gradient(#d9dce0 0% 25%,#f4f5f7 0% 50%) 0 0/24px 24px">' + preview_svg + '</div>')
    return (scene_svg,)


@app.cell
def _(mo, scene_svg):
    mo.vstack([
        mo.download(scene_svg, filename="phone-overlay.svg", mimetype="image/svg+xml", label="Download transparent frame"),
        mo.md("""**Export for Final Cut:**
```sh
uv run python export_video.py --scene phone --transparent --output output/phone-overlay.mov
```
**Playback:** `uv run python animation_preview.py --scene phone`

10 seconds: arrival at 2s, readable hold, upward dismissal at 6.3s.
Place your video underneath the MOV and crop it to the screen opening.
See `phone_overlay.md` for exact geometry and a masking option.
"""),
    ])
    return


if __name__ == "__main__":
    app.run()
