import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import moops
    from pathlib import Path
    from animation_timeline import load_timeline, state_at
    from export_video import encode_video
    from phone_scene import render_phone
    from phone_inputs import PhonePresets

    return (
        Path,
        PhonePresets,
        encode_video,
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
        defaults=timeline["labels"] | {"notification_scale": timeline.get("notification_scale", 1)},
    )
    return (presets,)


@app.cell
def _(moops, presets):
    args = moops.Group(presets=presets)
    return (args,)


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
    ### Phone notification overlay\nEdit the text below, check the preview, then export.
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
    # The banner keeps the screen's width; past 1.8 a typical title no longer fits on its line.
    notification_scale = args.slider(
        start=1,
        stop=1.8,
        step=0.05,
        value=timeline.get("notification_scale", 1),
        option="--notification-size",
        label="Notification size",
        help_text="Notification height and text size, 1 = phone-accurate",
        show_value=True,
    )
    output = args.text(
        value="output/phone-overlay.mov",
        option="--output",
        label="Output MOV",
        help_text="Transparent ProRes MOV to export",
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
        output,
    )


@app.cell
def _(
    account,
    args,
    caption,
    mo,
    notification_app,
    notification_body,
    notification_scale,
    notification_title,
    output,
):
    interface = args.interface(
        account,
        caption,
        notification_app,
        notification_title,
        notification_body,
        notification_scale,
        output,
    )
    mo.vstack(
        [
            mo.md(
                "Save a named **preset** to reuse these text fields and the notification size. Selecting one updates the preview. Export uses the values shown here."
            ),
            interface,
        ]
    )
    return (interface,)


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
            mo.md("""**Export for Final Cut:** click **Export MOV** below, or run the
    command under **Notebook CLI info** above, which carries the current values.

    10 seconds: arrival at 2s, readable hold, upward dismissal at 6.3s.
    Place your video underneath the MOV and crop it to the screen opening.
    See `phone_overlay.md` for exact geometry and a masking option.
    """),
        ]
    )
    return


@app.cell
def _(interface):
    export_button = interface.run_button(label="Export MOV")
    export_button
    return (export_button,)


@app.cell
def _(
    Path,
    encode_video,
    export_button,
    live_labels,
    mo,
    notification_scale,
    output,
    render_phone,
    state_at,
    timeline,
):
    mo.stop(not export_button.value)
    with mo.status.spinner("Exporting MOV..."):
        overlay = {"labels": live_labels, "notification_scale": notification_scale.value}
        exported = Path(output.value)
        frames = encode_video(
            lambda time: render_phone(
                state_at(timeline, time) | overlay,
                width=timeline["width"],
                height=timeline["height"],
                transparent=True,
            ),
            output=exported,
            fps=timeline["fps"],
            start=0,
            end=timeline["duration"],
            transparent=True,
            overwrite=True,
        )
        print(f"Saved {exported.resolve()} ({frames} frames)")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
