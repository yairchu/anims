import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import marimo as mo
    from pathlib import Path
    from animation_timeline import load_timeline, state_at
    from phone_scene import render_phone

    timeline_path = Path(__file__).with_name("timeline_phone.json")
    return json, load_timeline, mo, render_phone, state_at, timeline_path


@app.cell
def _(json, load_timeline):
    def save_labels(path, labels):
        current = load_timeline(path)
        current["labels"] = current.get("labels", {}) | labels
        path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n")
        return "Saved. Rerun the export command to update your video."

    return (save_labels,)


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
    mo.vstack([mo.md("### Phone notification overlay\nEdit the text below, check the preview, then save it for export."), time])
    return (time,)


@app.cell
def _(mo, timeline):
    account = mo.ui.text(value=timeline["labels"]["account"], label="Account name", full_width=True)
    caption = mo.ui.text(value=timeline["labels"]["caption"], label="Post text", full_width=True)
    notification_app = mo.ui.text(value=timeline["labels"]["app"], label="Notification app name", full_width=True)
    notification_title = mo.ui.text(value=timeline["labels"]["title"], label="Notification title", full_width=True)
    notification_body = mo.ui.text(value=timeline["labels"]["body"], label="Notification message", full_width=True)
    mo.vstack([account, caption, notification_app, notification_title, notification_body])
    return (
        account,
        caption,
        notification_app,
        notification_body,
        notification_title,
    )


@app.cell
def _(
    account,
    caption,
    notification_app,
    notification_body,
    notification_title,
):
    live_labels = {
        "account": account.value,
        "caption": caption.value,
        "app": notification_app.value,
        "title": notification_title.value,
        "body": notification_body.value,
    }
    return (live_labels,)


@app.cell
def _(live_labels, mo, save_labels, timeline_path):
    save_button = mo.ui.button(
        label="Save text for export",
        on_click=lambda _: save_labels(timeline_path, live_labels),
    )
    save_button
    return


@app.cell
def _(live_labels, mo, timeline):
    save_status = "Saved text matches the preview." if live_labels == timeline["labels"] else "Unsaved text — click Save text for export before rendering a video."
    mo.md(save_status)
    return


@app.cell
def _(live_labels, mo, render_phone, state_at, time, timeline):
    preview_state = state_at(timeline, time.value) | {"labels": live_labels}
    scene_svg = render_phone(preview_state, width=1080, height=1920, transparent=True)
    preview_svg = scene_svg.replace('width="1080" height="1920"', 'width="432" height="768"', 1)
    mo.Html('<div style="width:432px;max-width:100%;background:repeating-conic-gradient(#d9dce0 0% 25%,#f4f5f7 0% 50%) 0 0/24px 24px">' + preview_svg + '</div>')
    return (scene_svg,)


@app.cell
def _(mo, scene_svg):
    mo.vstack([
        mo.download(scene_svg, filename="phone-overlay.svg", mimetype="image/svg+xml", label="Download transparent frame"),
        mo.md("""**Export for Final Cut:**
    ```sh
    uv run python export_video.py --scene phone --transparent --output output/phone-overlay.mov --overwrite
    ```
    **Playback:** `uv run python animation_preview.py --scene phone`

    Save your text above before exporting. This command replaces the previous MOV.
    10 seconds: arrival at 2s, readable hold, upward dismissal at 6.3s.
    Place your video underneath the MOV and crop it to the screen opening.
    See `phone_overlay.md` for exact geometry and a masking option.
    """),
    ])
    return


if __name__ == "__main__":
    app.run()
