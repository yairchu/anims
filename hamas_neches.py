import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import wigglystuff
    from animation_scene import render_scene
    from animation_timeline import ease, load_timeline, state_at
    from video_formats import FORMATS, FORMAT_LABELS

    animation_timeline = load_timeline()
    return (
        FORMATS,
        FORMAT_LABELS,
        animation_timeline,
        ease,
        mo,
        render_scene,
        state_at,
        wigglystuff,
    )


@app.cell
def _(FORMAT_LABELS, mo):
    control_mode = mo.ui.radio(["Manual", "Timeline"], value="Manual", inline=True, label="Controls")
    video_format = mo.ui.dropdown(
        FORMAT_LABELS, value="Instagram portrait · 9:16 (1080×1920)",
        label="Video format", allow_select_none=False,
    )
    mo.hstack([control_mode, video_format], justify="start", gap=2)
    return control_mode, video_format


@app.cell
def _(animation_timeline, mo):
    # Construct controls independently of the mode so switching preserves edits.
    political_position = mo.ui.slider(0, 1, .001, .5, label="Israeli political position (left → right)", full_width=True)
    pal_political_position = mo.ui.slider(0, 1, .001, .5, label="Palestinian political position (left → right)", full_width=True)
    isr_meter_y_offset = mo.ui.slider(0, 300, 1, 140, label="Israeli meter Y position (positive → down)", show_value=True, full_width=True)
    pal_meter_y_offset = mo.ui.slider(-400, 300, 1, -400, label="Palestinian meter Y position (positive → down)", show_value=True, full_width=True)
    pal_translation_progress = mo.ui.slider(0, 1, .01, 0, label="Palestinian labels: Arabic → Hebrew (blur)", full_width=True)
    far_right_peek_progress = mo.ui.slider(0, 1, .01, 1, label="Smotrich and Bibi: in frame ← → offscreen", full_width=True)
    animation_time = mo.ui.slider(0, animation_timeline["duration"], .01, 0, label="Animation time (seconds)", show_value=True, full_width=True)
    return (
        animation_time,
        far_right_peek_progress,
        isr_meter_y_offset,
        pal_meter_y_offset,
        pal_political_position,
        pal_translation_progress,
        political_position,
    )


@app.cell
def _(mo):
    reconciliation_boundary = mo.ui.slider(.1, .45, .01, .25, label="Reconciliation zone ends at", show_value=True, full_width=True)
    right_zone_boundary = mo.ui.slider(.55, .95, .01, .8, label="Right-hand zones start at", show_value=True, full_width=True)
    return reconciliation_boundary, right_zone_boundary


@app.cell
def _(mo, wigglystuff):
    isr_meter_color_picker = mo.ui.anywidget(wigglystuff.ColorPicker(color="#0056d6"))
    pal_meter_color_picker = mo.ui.anywidget(wigglystuff.ColorPicker(color="#149149"))
    needle_color_picker = mo.ui.anywidget(wigglystuff.ColorPicker(color="#7a7a7a"))
    return isr_meter_color_picker, needle_color_picker, pal_meter_color_picker


@app.cell
def _(
    FORMATS,
    animation_time,
    animation_timeline,
    control_mode,
    ease,
    far_right_peek_progress,
    isr_meter_color_picker,
    isr_meter_y_offset,
    mo,
    needle_color_picker,
    pal_meter_color_picker,
    pal_meter_y_offset,
    pal_political_position,
    pal_translation_progress,
    political_position,
    reconciliation_boundary,
    render_scene,
    right_zone_boundary,
    state_at,
    video_format,
):
    manual_controls = mo.vstack([
        political_position, pal_political_position, isr_meter_y_offset,
        pal_meter_y_offset, pal_translation_progress, far_right_peek_progress,
        reconciliation_boundary, right_zone_boundary,
    ])
    active_controls = manual_controls if control_mode.value == "Manual" else animation_time
    scene_state = (
        dict(
            israeli_position=political_position.value,
            palestinian_position=pal_political_position.value,
            israeli_y=isr_meter_y_offset.value,
            palestinian_y=pal_meter_y_offset.value,
            portrait=ease(1 - far_right_peek_progress.value),
            translation=pal_translation_progress.value, outcome=0, events=[],
        )
        if control_mode.value == "Manual"
        else state_at(animation_timeline, animation_time.value)
    )
    preview_width, preview_height = FORMATS[video_format.value]
    scene_svg = render_scene(
        scene_state, width=preview_width, height=preview_height,
        israeli_color=isr_meter_color_picker.value["color"],
        palestinian_color=pal_meter_color_picker.value["color"],
        needle_color=needle_color_picker.value["color"],
        reconciliation_end=reconciliation_boundary.value,
        right_zone_start=right_zone_boundary.value,
    )
    # Fit either format on screen while retaining the exact export aspect ratio.
    preview = mo.Html(f'<div style="width:min(100%, {720 * preview_width / preview_height}px);margin:auto">{scene_svg}</div>')
    color_controls = mo.hstack([
        mo.vstack([mo.md("Israel"), isr_meter_color_picker]),
        mo.vstack([mo.md("Palestinians"), pal_meter_color_picker]),
        mo.vstack([mo.md("Needle"), needle_color_picker]),
    ], justify="start")
    mo.hstack([
        mo.vstack([active_controls, color_controls, mo.md(
            f"Export this format: `uv run python export_video.py --format {video_format.value} "
            f"--reconciliation-end {reconciliation_boundary.value:.2f} --right-zone-start {right_zone_boundary.value:.2f}`"
        )]),
        preview,
    ], widths=[1, 2], align="start", gap=2)
    return


if __name__ == "__main__":
    app.run()
