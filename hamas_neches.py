import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full")


@app.cell
def _(
    abbas_entry,
    arc_reveal,
    args,
    block_visibility,
    blocked_chapters,
    blocked_outcome,
    blocked_time,
    control_mode,
    endpoint_text_size,
    escalation_chapters,
    escalation_time,
    far_right_peek_progress,
    full_chapters,
    full_time,
    intro_chapters,
    intro_time,
    isr_meter_color_picker,
    isr_meter_y_offset,
    left_reveal,
    logos_reveal,
    meter_spacing,
    needle_color_picker,
    needle_reveal,
    netanyahu_entry,
    pal_meter_color_picker,
    pal_meter_y_offset,
    pal_political_position,
    pal_translation_progress,
    partnership_visibility,
    political_position,
    potential_opacity,
    potential_position,
    reconciliation_boundary,
    right_reveal,
    right_zone_boundary,
    scene_choice,
    smotrich_entry,
    video_format,
    zone_text_size,
    zones_reveal,
):
    interface = args.interface(
        scene_choice,
        control_mode,
        video_format,
        political_position,
        pal_political_position,
        isr_meter_y_offset,
        pal_meter_y_offset,
        pal_translation_progress,
        far_right_peek_progress,
        intro_chapters,
        intro_time,
        blocked_chapters,
        blocked_time,
        escalation_chapters,
        escalation_time,
        full_chapters,
        full_time,
        left_reveal,
        right_reveal,
        arc_reveal,
        needle_reveal,
        logos_reveal,
        zones_reveal,
        potential_position,
        potential_opacity,
        netanyahu_entry,
        abbas_entry,
        smotrich_entry,
        partnership_visibility,
        blocked_outcome,
        block_visibility,
        endpoint_text_size,
        zone_text_size,
        meter_spacing,
        reconciliation_boundary,
        right_zone_boundary,
        isr_meter_color_picker,
        pal_meter_color_picker,
        needle_color_picker,
    )
    interface
    return


@app.cell
def _():
    import marimo as mo
    import moops
    from animation_inputs import (
        build_export_command,
        layout_controls,
        boundary_controls,
        color_controls,
        scene_control,
        format_control,
    )
    from animation_scene import notebook_asset_urls, render_scene
    from animation_timeline import (
        DEFAULT_TIMELINE,
        SCENE_FILES,
        SCENE_LABELS,
        ease,
        load_scene,
        state_at,
    )
    from video_formats import FORMATS

    return (
        DEFAULT_TIMELINE,
        FORMATS,
        SCENE_FILES,
        SCENE_LABELS,
        boundary_controls,
        build_export_command,
        color_controls,
        ease,
        format_control,
        layout_controls,
        load_scene,
        mo,
        moops,
        notebook_asset_urls,
        render_scene,
        scene_control,
        state_at,
    )


@app.cell
def _(moops):
    args = moops.Group()
    return (args,)


@app.cell
def _(notebook_asset_urls):
    # Keep virtual files alive independently of timeline scrubbing and controls.
    preview_assets = notebook_asset_urls()
    return (preview_assets,)


@app.cell
def _(DEFAULT_TIMELINE, SCENE_FILES, mo):
    intro_timeline_file = mo.watch.file(
        DEFAULT_TIMELINE.with_name(SCENE_FILES["intro"])
    )
    # Watchers must be named globals: marimo does not track state inside lists.
    blocked_timeline_file = mo.watch.file(
        DEFAULT_TIMELINE.with_name(SCENE_FILES["blocked"])
    )
    escalation_timeline_file = mo.watch.file(
        DEFAULT_TIMELINE.with_name(SCENE_FILES["escalation"])
    )
    sequence_file = mo.watch.file(DEFAULT_TIMELINE.with_name("sequence.json"))
    return (
        blocked_timeline_file,
        escalation_timeline_file,
        intro_timeline_file,
        sequence_file,
    )


@app.cell
def _(
    SCENE_LABELS,
    blocked_timeline_file,
    escalation_timeline_file,
    intro_timeline_file,
    load_scene,
    sequence_file,
):
    intro_timeline_file.read_text()
    blocked_timeline_file.read_text()
    escalation_timeline_file.read_text()
    sequence_file.read_text()
    scene_timelines = {
        name: load_scene(name) for name in SCENE_LABELS.values()
    }
    return (scene_timelines,)


@app.cell
def _(args, format_control, mo, scene_control):
    scene_choice = scene_control(args, default="intro")
    control_mode = args.custom(
        args.dropdown(
            ["Manual", "Timeline"],
            value="Timeline",
            allow_select_none=False,
            option="--control-mode",
            help_text="Controls",
        ),
        lambda value: mo.ui.radio(
            ["Manual", "Timeline"], value=value, inline=True, label="Controls"
        ),
    )
    video_format = format_control(args, default="portrait")
    mo.hstack(
        [scene_choice, control_mode, video_format], justify="start", gap=2
    )
    return control_mode, scene_choice, video_format


@app.cell
def _(args):
    # Construct controls independently of the mode so switching preserves edits.
    political_position = args.slider(
        0,
        1,
        0.001,
        0.5,
        label="Israeli political position (left → right)",
        full_width=True,
        option="--political-position",
        help_text="Israeli political position (left → right)",
    )
    pal_political_position = args.slider(
        0,
        1,
        0.001,
        0.5,
        label="Palestinian political position (left → right)",
        full_width=True,
        option="--pal-political-position",
        help_text="Palestinian political position (left → right)",
    )
    isr_meter_y_offset = args.slider(
        0,
        300,
        1,
        140,
        label="Israeli meter Y position (positive → down)",
        show_value=True,
        full_width=True,
        option="--isr-meter-y-offset",
        help_text="Israeli meter Y position (positive → down)",
    )
    pal_meter_y_offset = args.slider(
        -400,
        300,
        1,
        -400,
        label="Palestinian meter Y position (positive → down)",
        show_value=True,
        full_width=True,
        option="--pal-meter-y-offset",
        help_text="Palestinian meter Y position (positive → down)",
    )
    pal_translation_progress = args.slider(
        0,
        1,
        0.01,
        0,
        label="Palestinian labels: Arabic → Hebrew (blur)",
        full_width=True,
        option="--pal-translation-progress",
        help_text="Palestinian labels: Arabic → Hebrew (blur)",
    )
    far_right_peek_progress = args.slider(
        0,
        1,
        0.01,
        1,
        label="Smotrich and Bibi: in frame ← → offscreen",
        full_width=True,
        option="--far-right-peek-progress",
        help_text="Smotrich and Bibi: in frame ← → offscreen",
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
def _(args, scene_timelines):
    intro_chapters = args.dropdown(
        {
            f"{chapter['time']:g}s · {chapter['label']}": chapter["time"]
            for chapter in scene_timelines["intro"]["chapters"]
        },
        value=next(
            iter(
                {
                    f"{chapter['time']:g}s · {chapter['label']}": chapter[
                        "time"
                    ]
                    for chapter in scene_timelines["intro"]["chapters"]
                }
            )
        ),
        label="Jump to chapter",
        allow_select_none=False,
        option="--intro-chapters",
        help_text="Jump to chapter",
    )
    return (intro_chapters,)


@app.cell
def _(args, intro_chapters, scene_timelines):
    intro_time = args.slider(
        0,
        scene_timelines["intro"]["duration"],
        0.01,
        intro_chapters.value,
        label="Animation time (seconds)",
        show_value=True,
        full_width=True,
        option="--intro-time",
        help_text="Animation time (seconds)",
    )
    return (intro_time,)


@app.cell
def _(args, scene_timelines):
    blocked_chapters = args.dropdown(
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
        option="--blocked-chapters",
        help_text="Jump to chapter",
    )
    return (blocked_chapters,)


@app.cell
def _(args, blocked_chapters, scene_timelines):
    blocked_time = args.slider(
        0,
        scene_timelines["blocked"]["duration"],
        0.01,
        blocked_chapters.value,
        label="Animation time (seconds)",
        show_value=True,
        full_width=True,
        option="--blocked-time",
        help_text="Animation time (seconds)",
    )
    return (blocked_time,)


@app.cell
def _(args, scene_timelines):
    escalation_chapters = args.dropdown(
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
        option="--escalation-chapters",
        help_text="Jump to chapter",
    )
    return (escalation_chapters,)


@app.cell
def _(args, escalation_chapters, scene_timelines):
    escalation_time = args.slider(
        0,
        scene_timelines["escalation"]["duration"],
        0.01,
        escalation_chapters.value,
        label="Animation time (seconds)",
        show_value=True,
        full_width=True,
        option="--escalation-time",
        help_text="Animation time (seconds)",
    )
    return (escalation_time,)


@app.cell
def _(args, scene_timelines):
    full_chapters = args.dropdown(
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
        option="--full-chapters",
        help_text="Jump to chapter",
    )
    return (full_chapters,)


@app.cell
def _(args, full_chapters, scene_timelines):
    full_time = args.slider(
        0,
        scene_timelines["full"]["duration"],
        0.01,
        full_chapters.value,
        label="Animation time (seconds)",
        show_value=True,
        full_width=True,
        option="--full-time",
        help_text="Animation time (seconds)",
    )
    return (full_time,)


@app.cell
def _(args):
    left_reveal = args.slider(
        0,
        1,
        0.01,
        1,
        label="Left label reveal",
        full_width=True,
        option="--left-reveal",
        help_text="Left label reveal",
    )
    right_reveal = args.slider(
        0,
        1,
        0.01,
        1,
        label="Right label reveal",
        full_width=True,
        option="--right-reveal",
        help_text="Right label reveal",
    )
    arc_reveal = args.slider(
        0,
        1,
        0.01,
        1,
        label="Arc drawing reveal",
        full_width=True,
        option="--arc-reveal",
        help_text="Arc drawing reveal",
    )
    needle_reveal = args.slider(
        0,
        1,
        0.01,
        1,
        label="Needle reveal",
        full_width=True,
        option="--needle-reveal",
        help_text="Needle reveal",
    )
    logos_reveal = args.slider(
        0,
        1,
        0.01,
        1,
        label="Logos reveal",
        full_width=True,
        option="--logos-reveal",
        help_text="Logos reveal",
    )
    zones_reveal = args.slider(
        0,
        1,
        0.01,
        0,
        label="Opportunity zones reveal",
        full_width=True,
        option="--zones-reveal",
        help_text="Opportunity zones reveal",
    )
    return (
        arc_reveal,
        left_reveal,
        logos_reveal,
        needle_reveal,
        right_reveal,
        zones_reveal,
    )


@app.cell
def _(args):
    potential_position = args.slider(
        0,
        1,
        0.01,
        0.3,
        label="Potential needle position",
        full_width=True,
        option="--potential-position",
        help_text="Potential needle position",
    )
    potential_opacity = args.slider(
        0,
        1,
        0.01,
        0.65,
        label="Potential needle visibility",
        full_width=True,
        option="--potential-opacity",
        help_text="Potential needle visibility",
    )
    netanyahu_entry = args.slider(
        0,
        1,
        0.01,
        1,
        label="Netanyahu entrance",
        full_width=True,
        option="--netanyahu-entry",
        help_text="Netanyahu entrance",
    )
    abbas_entry = args.slider(
        0,
        1,
        0.01,
        1,
        label="Abbas entrance",
        full_width=True,
        option="--abbas-entry",
        help_text="Abbas entrance",
    )
    smotrich_entry = args.slider(
        0,
        1,
        0.01,
        0,
        label="Smotrich entrance",
        full_width=True,
        option="--smotrich-entry",
        help_text="Smotrich entrance",
    )
    partnership_visibility = args.slider(
        0,
        1,
        0.01,
        1,
        label="Possible partnership visibility",
        full_width=True,
        option="--partnership-visibility",
        help_text="Possible partnership visibility",
    )
    blocked_outcome = args.slider(
        0,
        1,
        0.01,
        0,
        label="Final caption visibility",
        full_width=True,
        option="--blocked-outcome",
        help_text="Final caption visibility",
    )
    block_visibility = args.slider(
        0,
        1,
        0.01,
        0,
        label="Partnership block visibility",
        full_width=True,
        option="--block-visibility",
        help_text="Partnership block visibility",
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
def _(args, layout_controls):
    endpoint_text_size, zone_text_size, meter_spacing = layout_controls(args)
    return endpoint_text_size, meter_spacing, zone_text_size


@app.cell
def _(
    args,
    boundary_controls,
    endpoint_text_size,
    meter_spacing,
    zone_text_size,
):
    (endpoint_text_size,)
    (zone_text_size,)
    (meter_spacing,)
    reconciliation_boundary, right_zone_boundary = boundary_controls(args)
    return reconciliation_boundary, right_zone_boundary


@app.cell
def _(args, color_controls):
    isr_meter_color_picker, pal_meter_color_picker, needle_color_picker = (
        color_controls(args)
    )
    return isr_meter_color_picker, needle_color_picker, pal_meter_color_picker


@app.cell
def _(
    FORMATS,
    abbas_entry,
    arc_reveal,
    block_visibility,
    blocked_chapters,
    blocked_outcome,
    blocked_time,
    build_export_command,
    control_mode,
    ease,
    endpoint_text_size,
    escalation_chapters,
    escalation_time,
    far_right_peek_progress,
    full_chapters,
    full_time,
    intro_chapters,
    intro_time,
    isr_meter_color_picker,
    isr_meter_y_offset,
    left_reveal,
    logos_reveal,
    meter_spacing,
    mo,
    needle_color_picker,
    needle_reveal,
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
    right_reveal,
    right_zone_boundary,
    scene_choice,
    scene_timelines,
    smotrich_entry,
    state_at,
    video_format,
    zone_text_size,
    zones_reveal,
):
    intro_controls = [
        political_position,
        isr_meter_y_offset,
        left_reveal,
        right_reveal,
        arc_reveal,
        needle_reveal,
        logos_reveal,
        zones_reveal,
    ]
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
        "intro": (intro_time, intro_chapters),
        "blocked": (blocked_time, blocked_chapters),
        "escalation": (escalation_time, escalation_chapters),
        "full": (full_time, full_chapters),
    }[selected_scene]
    use_timeline = control_mode.value == "Timeline" or selected_scene == "full"
    active_controls = (
        mo.vstack([selected_chapters, selected_time])
        if use_timeline
        else mo.vstack(
            intro_controls
            if selected_scene == "intro"
            else blocked_controls
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
    if not use_timeline and selected_scene == "intro":
        scene_state = dict(
            scene_state,
            scene="intro",
            left_reveal=left_reveal.value,
            right_reveal=right_reveal.value,
            arc_reveal=arc_reveal.value,
            needle_reveal=needle_reveal.value,
            logos_reveal=logos_reveal.value,
            zones_reveal=zones_reveal.value,
        )
    preview_width, preview_height = FORMATS[video_format.value]
    render_settings = dict(
        israeli_color=isr_meter_color_picker.value,
        palestinian_color=pal_meter_color_picker.value,
        needle_color=needle_color_picker.value,
        reconciliation_end=reconciliation_boundary.value,
        right_zone_start=right_zone_boundary.value,
        endpoint_text_size=endpoint_text_size.value,
        zone_text_size=zone_text_size.value,
        meter_spacing=meter_spacing.value,
    )
    scene_svg = render_scene(
        scene_state,
        assets=preview_assets,
        width=preview_width,
        height=preview_height,
        **render_settings,
    )
    export_command = build_export_command(
        selected_scene,
        video_format.value,
        scene_timelines[selected_scene],
        **render_settings,
    )
    # Fit either format on screen while retaining the exact export aspect ratio.
    preview = mo.Html(
        f'<div style="width:min(100%, {720 * preview_width / preview_height}px);'
        f'margin:auto;line-height:0;outline:1px solid #808080">{scene_svg}</div>'
    )
    color_layout = mo.hstack(
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
                    endpoint_text_size,
                    zone_text_size,
                    meter_spacing,
                    reconciliation_boundary,
                    right_zone_boundary,
                    color_layout,
                    mo.md(f"Export this format: `{export_command}`"),
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
