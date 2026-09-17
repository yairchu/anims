import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full")


@app.cell
def _():
    import shlex
    import marimo as mo
    import wigglystuff
    from animation_scene import notebook_asset_urls, render_scene
    from animation_timeline import (
        DEFAULT_TIMELINE,
        SCENE_FILES,
        SCENE_LABELS,
        ease,
        load_scene,
        state_at,
    )
    from video_formats import FORMATS, FORMAT_LABELS

    return (
        DEFAULT_TIMELINE,
        FORMATS,
        FORMAT_LABELS,
        SCENE_FILES,
        SCENE_LABELS,
        ease,
        load_scene,
        mo,
        notebook_asset_urls,
        render_scene,
        shlex,
        state_at,
        wigglystuff,
    )


@app.cell
def _(notebook_asset_urls):
    # Keep virtual files alive independently of timeline scrubbing and controls.
    preview_assets = notebook_asset_urls()
    return (preview_assets,)


@app.cell
def _(DEFAULT_TIMELINE, SCENE_FILES, mo):
    # Watchers must be named globals: marimo does not track state inside lists.
    blocked_timeline_file = mo.watch.file(
        DEFAULT_TIMELINE.with_name(SCENE_FILES["blocked"])
    )
    escalation_timeline_file = mo.watch.file(
        DEFAULT_TIMELINE.with_name(SCENE_FILES["escalation"])
    )
    sequence_file = mo.watch.file(DEFAULT_TIMELINE.with_name("sequence.json"))
    return blocked_timeline_file, escalation_timeline_file, sequence_file


@app.cell
def _(
    SCENE_LABELS,
    blocked_timeline_file,
    escalation_timeline_file,
    load_scene,
    sequence_file,
):
    blocked_timeline_file.read_text()
    escalation_timeline_file.read_text()
    sequence_file.read_text()
    scene_timelines = {
        name: load_scene(name) for name in SCENE_LABELS.values()
    }
    return (scene_timelines,)


@app.cell
def _(FORMAT_LABELS, SCENE_LABELS, mo):
    scene_choice = mo.ui.dropdown(
        SCENE_LABELS,
        value="Blocked partnership",
        label="Scene",
        allow_select_none=False,
    )
    control_mode = mo.ui.radio(
        ["Manual", "Timeline"], value="Timeline", inline=True, label="Controls"
    )
    video_format = mo.ui.dropdown(
        FORMAT_LABELS,
        value="Instagram portrait · 9:16 (1080×1920)",
        label="Video format",
        allow_select_none=False,
    )
    mo.hstack(
        [scene_choice, control_mode, video_format], justify="start", gap=2
    )
    return control_mode, scene_choice, video_format


@app.cell
def _(mo):
    # Construct controls independently of the mode so switching preserves edits.
    political_position = mo.ui.slider(
        0,
        1,
        0.001,
        0.5,
        label="Israeli political position (left → right)",
        full_width=True,
    )
    pal_political_position = mo.ui.slider(
        0,
        1,
        0.001,
        0.5,
        label="Palestinian political position (left → right)",
        full_width=True,
    )
    isr_meter_y_offset = mo.ui.slider(
        0,
        300,
        1,
        140,
        label="Israeli meter Y position (positive → down)",
        show_value=True,
        full_width=True,
    )
    pal_meter_y_offset = mo.ui.slider(
        -400,
        300,
        1,
        -400,
        label="Palestinian meter Y position (positive → down)",
        show_value=True,
        full_width=True,
    )
    pal_translation_progress = mo.ui.slider(
        0,
        1,
        0.01,
        0,
        label="Palestinian labels: Arabic → Hebrew (blur)",
        full_width=True,
    )
    far_right_peek_progress = mo.ui.slider(
        0,
        1,
        0.01,
        1,
        label="Smotrich and Bibi: in frame ← → offscreen",
        full_width=True,
    )
    return (
        far_right_peek_progress,
        isr_meter_y_offset,
        pal_meter_y_offset,
        pal_political_position,
        pal_translation_progress,
        political_position,
    )


@app.cell
def _(mo, scene_timelines):
    blocked_chapters = mo.ui.dropdown(
        {
            f"{chapter['time']:g}s · {chapter['label']}": chapter["time"]
            for chapter in scene_timelines["blocked"]["chapters"]
        },
        value=next(
            iter(
                {
                    f"{chapter['time']:g}s · {chapter['label']}": chapter[
                        "time"
                    ]
                    for chapter in scene_timelines["blocked"]["chapters"]
                }
            )
        ),
        label="Jump to chapter",
        allow_select_none=False,
    )
    return (blocked_chapters,)


@app.cell
def _(blocked_chapters, mo, scene_timelines):
    blocked_time = mo.ui.slider(
        0,
        scene_timelines["blocked"]["duration"],
        0.01,
        blocked_chapters.value,
        label="Animation time (seconds)",
        show_value=True,
        full_width=True,
    )
    return (blocked_time,)


@app.cell
def _(mo, scene_timelines):
    escalation_chapters = mo.ui.dropdown(
        {
            f"{chapter['time']:g}s · {chapter['label']}": chapter["time"]
            for chapter in scene_timelines["escalation"]["chapters"]
        },
        value=next(
            iter(
                {
                    f"{chapter['time']:g}s · {chapter['label']}": chapter[
                        "time"
                    ]
                    for chapter in scene_timelines["escalation"]["chapters"]
                }
            )
        ),
        label="Jump to chapter",
        allow_select_none=False,
    )
    return (escalation_chapters,)


@app.cell
def _(escalation_chapters, mo, scene_timelines):
    escalation_time = mo.ui.slider(
        0,
        scene_timelines["escalation"]["duration"],
        0.01,
        escalation_chapters.value,
        label="Animation time (seconds)",
        show_value=True,
        full_width=True,
    )
    return (escalation_time,)


@app.cell
def _(mo, scene_timelines):
    full_chapters = mo.ui.dropdown(
        {
            f"{chapter['time']:g}s · {chapter['label']}": chapter["time"]
            for chapter in scene_timelines["full"]["chapters"]
        },
        value=next(
            iter(
                {
                    f"{chapter['time']:g}s · {chapter['label']}": chapter[
                        "time"
                    ]
                    for chapter in scene_timelines["full"]["chapters"]
                }
            )
        ),
        label="Jump to chapter",
        allow_select_none=False,
    )
    return (full_chapters,)


@app.cell
def _(full_chapters, mo, scene_timelines):
    full_time = mo.ui.slider(
        0,
        scene_timelines["full"]["duration"],
        0.01,
        full_chapters.value,
        label="Animation time (seconds)",
        show_value=True,
        full_width=True,
    )
    return (full_time,)


@app.cell
def _(mo):
    potential_position = mo.ui.slider(
        0, 1, 0.01, 0.3, label="Potential needle position", full_width=True
    )
    potential_opacity = mo.ui.slider(
        0, 1, 0.01, 0.65, label="Potential needle visibility", full_width=True
    )
    netanyahu_entry = mo.ui.slider(
        0, 1, 0.01, 1, label="Netanyahu entrance", full_width=True
    )
    abbas_entry = mo.ui.slider(
        0, 1, 0.01, 1, label="Abbas entrance", full_width=True
    )
    smotrich_entry = mo.ui.slider(
        0, 1, 0.01, 0, label="Smotrich entrance", full_width=True
    )
    partnership_visibility = mo.ui.slider(
        0, 1, 0.01, 1, label="Possible partnership visibility", full_width=True
    )
    blocked_outcome = mo.ui.slider(
        0, 1, 0.01, 0, label="Final caption visibility", full_width=True
    )
    block_visibility = mo.ui.slider(
        0, 1, 0.01, 0, label="Partnership block visibility", full_width=True
    )
    return (
        abbas_entry,
        block_visibility,
        blocked_outcome,
        netanyahu_entry,
        partnership_visibility,
        potential_opacity,
        potential_position,
        smotrich_entry,
    )


@app.cell
def _(mo):
    reconciliation_boundary = mo.ui.slider(
        0.1,
        0.45,
        0.01,
        0.2,
        label="Reconciliation zone ends at",
        show_value=True,
        full_width=True,
    )
    right_zone_boundary = mo.ui.slider(
        0.55,
        0.95,
        0.01,
        0.8,
        label="Right-hand zones start at",
        show_value=True,
        full_width=True,
    )
    return reconciliation_boundary, right_zone_boundary


@app.cell
def _(mo, wigglystuff):
    isr_meter_color_picker = mo.ui.anywidget(
        wigglystuff.ColorPicker(color="#0056d6")
    )
    pal_meter_color_picker = mo.ui.anywidget(
        wigglystuff.ColorPicker(color="#149149")
    )
    needle_color_picker = mo.ui.anywidget(
        wigglystuff.ColorPicker(color="#7a7a7a")
    )
    return isr_meter_color_picker, needle_color_picker, pal_meter_color_picker


@app.cell
def _(
    FORMATS,
    abbas_entry,
    block_visibility,
    blocked_chapters,
    blocked_outcome,
    blocked_time,
    control_mode,
    ease,
    escalation_chapters,
    escalation_time,
    far_right_peek_progress,
    full_chapters,
    full_time,
    isr_meter_color_picker,
    isr_meter_y_offset,
    mo,
    needle_color_picker,
    netanyahu_entry,
    pal_meter_color_picker,
    pal_meter_y_offset,
    pal_political_position,
    pal_translation_progress,
    partnership_visibility,
    political_position,
    potential_opacity,
    potential_position,
    preview_assets,
    reconciliation_boundary,
    render_scene,
    right_zone_boundary,
    scene_choice,
    scene_timelines,
    shlex,
    smotrich_entry,
    state_at,
    video_format,
):
    escalation_controls = [
        political_position,
        pal_political_position,
        isr_meter_y_offset,
        pal_meter_y_offset,
        pal_translation_progress,
        far_right_peek_progress,
    ]
    blocked_controls = [
        political_position,
        isr_meter_y_offset,
        potential_position,
        potential_opacity,
        netanyahu_entry,
        abbas_entry,
        smotrich_entry,
        partnership_visibility,
        block_visibility,
        blocked_outcome,
    ]
    selected_scene = scene_choice.value
    selected_time, selected_chapters = {
        "blocked": (blocked_time, blocked_chapters),
        "escalation": (escalation_time, escalation_chapters),
        "full": (full_time, full_chapters),
    }[selected_scene]
    use_timeline = control_mode.value == "Timeline" or selected_scene == "full"
    active_controls = (
        mo.vstack([selected_chapters, selected_time])
        if use_timeline
        else mo.vstack(
            blocked_controls
            if selected_scene == "blocked"
            else escalation_controls
        )
    )
    scene_state = (
        dict(
            israeli_position=political_position.value,
            palestinian_position=pal_political_position.value,
            israeli_y=isr_meter_y_offset.value,
            palestinian_y=pal_meter_y_offset.value,
            portrait=ease(1 - far_right_peek_progress.value),
            translation=pal_translation_progress.value,
            outcome=0,
            events=[],
        )
        if not use_timeline
        else state_at(scene_timelines[selected_scene], selected_time.value)
    )
    if not use_timeline and selected_scene == "blocked":
        scene_state = dict(
            scene_state,
            scene="blocked",
            potential_position=potential_position.value,
            potential_opacity=potential_opacity.value,
            netanyahu=netanyahu_entry.value,
            abbas=abbas_entry.value,
            smotrich=smotrich_entry.value,
            partnership=partnership_visibility.value,
            block=block_visibility.value,
            outcome=blocked_outcome.value,
        )
    preview_width, preview_height = FORMATS[video_format.value]
    scene_svg = render_scene(
        scene_state,
        assets=preview_assets,
        width=preview_width,
        height=preview_height,
        israeli_color=isr_meter_color_picker.value["color"],
        palestinian_color=pal_meter_color_picker.value["color"],
        needle_color=needle_color_picker.value["color"],
        reconciliation_end=reconciliation_boundary.value,
        right_zone_start=right_zone_boundary.value,
    )
    # Fit either format on screen while retaining the exact export aspect ratio.
    preview = mo.Html(
        f'<div style="width:min(100%, {720 * preview_width / preview_height}px);margin:auto">{scene_svg}</div>'
    )
    color_controls = mo.hstack(
        [
            mo.vstack([mo.md("Israel"), isr_meter_color_picker]),
            mo.vstack([mo.md("Palestinians"), pal_meter_color_picker]),
            mo.vstack([mo.md("Needle"), needle_color_picker]),
        ],
        justify="start",
    )
    mo.hstack(
        [
            mo.vstack(
                [
                    mo.md(
                        "Full sequence uses timeline controls."
                        if selected_scene == "full"
                        else ""
                    ),
                    active_controls,
                    reconciliation_boundary,
                    right_zone_boundary,
                    color_controls,
                    mo.md(
                        f"Export this format: `uv run python export_video.py --scene {selected_scene} --format {video_format.value} "
                        f"--reconciliation-end {reconciliation_boundary.value:.2f} --right-zone-start {right_zone_boundary.value:.2f} "
                        f"--israeli-color {shlex.quote(isr_meter_color_picker.value['color'])} "
                        f"--palestinian-color {shlex.quote(pal_meter_color_picker.value['color'])} "
                        f"--needle-color {shlex.quote(needle_color_picker.value['color'])}`"
                    ),
                ]
            ),
            preview,
        ],
        widths=[1, 2],
        align="start",
        gap=2,
    )
    return


if __name__ == "__main__":
    app.run()
