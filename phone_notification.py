import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import marimo as mo
    import moops
    from pathlib import Path
    from animation_timeline import load_timeline, state_at
    from phone_scene import render_phone
    from phone_inputs import PhonePresets

    return (
        Path,
        PhonePresets,
        json,
        load_timeline,
        mo,
        moops,
        render_phone,
        state_at,
    )


@app.cell
def _(Path):
    timeline_path = Path(__file__).with_name("timeline_phone.json")
    return (timeline_path,)


@app.cell
def _(mo):
    get_preset, set_preset = mo.state(None)
    return get_preset, set_preset


@app.cell
def _(PhonePresets, get_preset, set_preset, timeline, timeline_path):
    presets = PhonePresets(
        get_preset,
        set_preset,
        filename=timeline_path.with_name("phone_notification_presets.json"),
        defaults=timeline["labels"],
    )
    return (presets,)


@app.cell
def _(moops, presets):
    args = moops.Group(presets=presets)
    return (args,)


@app.cell
def _(json, load_timeline):
    def save_overlay(path, labels, notification_scale):
        current = load_timeline(path)
        current["labels"] = current.get("labels", {}) | labels
        current["notification_scale"] = notification_scale
        path.write_text(
            json.dumps(current, ensure_ascii=False, indent=2) + "\n"
        )
        return "Saved. Rerun the export command to update your video."

    return (save_overlay,)


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
def _(mo):
    mo.md(r"""
    ### Phone notification overlay\nEdit the text below, check the preview, then save it for export.
    """)
    return


@app.cell
def _(args, mo, timeline):
    account = args.text(
        value=timeline["labels"]["account"],
        option="--account",
        label="Account name",
        help_text="Account name",
    )
    caption = args.text(
        value=timeline["labels"]["caption"],
        option="--caption",
        label="Post text",
        help_text="Post text",
    )
    notification_app = args.text(
        value=timeline["labels"]["app"],
        option="--notification-app",
        label="Notification app name",
        help_text="Notification app name",
    )
    notification_title = args.text(
        value=timeline["labels"]["title"],
        option="--notification-title",
        label="Notification title",
        help_text="Notification title",
    )
    notification_body = args.text(
        value=timeline["labels"]["body"],
        option="--notification-body",
        label="Notification message",
        help_text="Notification message",
    )
    # 1.8 is about the widest banner that fits the 720-unit canvas.
    notification_scale = mo.ui.slider(
        start=1,
        stop=1.8,
        step=0.05,
        value=timeline.get("notification_scale", 1),
        label="Notification size",
        show_value=True,
    )
    mo.hstack(
        [
            account,
            caption,
            notification_app,
            notification_title,
            notification_body,
            notification_scale,
        ],
        wrap=True,
    )
    return (
        account,
        caption,
        notification_app,
        notification_body,
        notification_scale,
        notification_title,
    )


@app.cell
def _(
    account,
    args,
    caption,
    mo,
    notification_app,
    notification_body,
    notification_title,
):
    text_interface = args.interface(
        account,
        caption,
        notification_app,
        notification_title,
        notification_body,
    )
    mo.vstack(
        [
            mo.md(
                "Save a named **preset** to reuse these five text fields. Selecting one updates the preview. Use **Save text and size for export** below to apply it to the video."
            ),
            text_interface,
        ]
    )
    return


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
def _(live_labels, mo, notification_scale, save_overlay, timeline_path):
    save_button = mo.ui.button(
        label="Save text and size for export",
        on_click=lambda _: save_overlay(
            timeline_path, live_labels, notification_scale.value
        ),
    )
    save_button
    return


@app.cell
def _(live_labels, mo, notification_scale, timeline):
    saved = live_labels == timeline[
        "labels"
    ] and notification_scale.value == timeline.get("notification_scale", 1)
    save_status = (
        "Saved text and size match the preview."
        if saved
        else "Unsaved changes — click Save text and size for export before rendering a video."
    )
    mo.md(save_status)
    return


@app.cell
def _(mo, timeline):
    time = mo.ui.slider(
        start=0,
        stop=timeline["duration"],
        step=1 / 30,
        value=3,
        label="Time (seconds)",
        show_value=True,
    )
    time
    return (time,)


@app.cell
def _(
    live_labels,
    mo,
    notification_scale,
    render_phone,
    state_at,
    time,
    timeline,
):
    preview_state = state_at(timeline, time.value) | {
        "labels": live_labels,
        "notification_scale": notification_scale.value,
    }
    scene_svg = render_phone(
        preview_state, width=1080, height=1920, transparent=True
    )
    preview_svg = scene_svg.replace(
        'width="1080" height="1920"', 'width="432" height="768"', 1
    )
    mo.Html(
        '<div style="width:432px;max-width:100%;background:repeating-conic-gradient(#d9dce0 0% 25%,#f4f5f7 0% 50%) 0 0/24px 24px">'
        + preview_svg
        + "</div>"
    )
    return (scene_svg,)


@app.cell
def _(mo, scene_svg):
    mo.vstack(
        [
            mo.download(
                scene_svg,
                filename="phone-overlay.svg",
                mimetype="image/svg+xml",
                label="Download transparent frame",
            ),
            mo.md("""**Export for Final Cut:**
    ```sh
    uv run python export_video.py --scene phone --transparent --output output/phone-overlay.mov --overwrite
    ```
    **Playback:** `uv run python animation_preview.py --scene phone`

    Save your text and size above before exporting. This command replaces the previous MOV.
    10 seconds: arrival at 2s, readable hold, upward dismissal at 6.3s.
    Place your video underneath the MOV and crop it to the screen opening.
    See `phone_overlay.md` for exact geometry and a masking option.
    """),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
