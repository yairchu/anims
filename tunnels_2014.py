import marimo

__generated_with = "0.25.0"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    import shlex

    import marimo as mo
    import moops

    from animation_inputs import labeled_choice
    from animation_scene import notebook_asset_urls, render_scene
    from animation_timeline import DEFAULT_TIMELINE, load_timeline, state_at
    from video_formats import FORMATS

    tunnel_path = DEFAULT_TIMELINE.with_name("timeline_tunnels.json")
    output_formats = FORMATS | {"panel": (960, 1080)}
    return (
        json,
        labeled_choice,
        load_timeline,
        mo,
        moops,
        notebook_asset_urls,
        output_formats,
        render_scene,
        shlex,
        state_at,
        tunnel_path,
    )


@app.cell
def _(moops):
    args = moops.Group()
    return (args,)


@app.cell
def _(mo, tunnel_path):
    timeline_file = mo.watch.file(tunnel_path)
    return (timeline_file,)


@app.cell
def _(load_timeline, timeline_file, tunnel_path):
    timeline_file.read_text()
    timeline = load_timeline(tunnel_path)
    return (timeline,)


@app.cell
def _(notebook_asset_urls):
    # This cell stays alive while scrubbing; no embedded image bytes per frame.
    preview_assets = notebook_asset_urls({"netanyahu", "bennett", "gantz", "winter"})
    return (preview_assets,)


@app.cell
def _(args, labeled_choice):
    clip_choice = labeled_choice(
        args,
        {"Full animation": "full", "2014 · information bypass": "2014", "Transition + 2026": "2026"},
        "--clip", "Clip", "full",
    )
    control_mode = labeled_choice(
        args, {"Timeline": "timeline", "Manual": "manual"},
        "--control-mode", "Controls", "timeline",
    )
    video_format = labeled_choice(
        args,
        {"Instagram / Shorts · 9:16": "portrait", "Landscape · 16:9": "landscape", "Half-screen panel · 8:9": "panel"},
        "--format", "Video format", "portrait",
    )
    transparent = args.checkbox(
        value=False, flag="--transparent", label="Transparent background",
        help_text="Preview and export with alpha (ProRes MOV)",
    )
    return clip_choice, control_mode, transparent, video_format


@app.cell
def _(clip_choice, timeline):
    clip = timeline["clips"][clip_choice.value]
    chapter_options = {
        f"{chapter['time'] - clip['start']:g}s · {chapter['label']}": chapter["time"] - clip["start"]
        for chapter in timeline["chapters"]
        if clip["start"] <= chapter["time"] < clip["end"]
    }
    if not chapter_options:
        chapter_options = {"0s · Clip start": 0}
    return chapter_options, clip


@app.cell
def _(args, chapter_options):
    chapter = args.dropdown(
        chapter_options,
        value=next((label for label, time in chapter_options.items() if time == 3), next(iter(chapter_options))),
        label="Jump to chapter", allow_select_none=False,
        option="--chapter", help_text="Jump to a chapter in the selected clip",
    )
    return (chapter,)


@app.cell
def _(args, chapter, clip):
    animation_time = args.slider(
        0, clip["end"] - clip["start"], 0.01, chapter.value,
        label="Clip time (seconds)", show_value=True, full_width=True,
        option="--time", help_text="Seconds from the start of the selected clip",
    )
    return (animation_time,)


@app.cell
def _(args):
    hierarchy = args.slider(0, 1, .01, 1, label="Hierarchy reveal", help_text="Hierarchy reveal", option="--hierarchy", full_width=True)
    knowledge = args.slider(0, 1, .01, 1, label="Tunnel information", help_text="Tunnel information", option="--knowledge", full_width=True)
    withheld = args.slider(0, 1, .01, 1, label="Missing cabinet briefing", help_text="Missing cabinet briefing", option="--withheld", full_width=True)
    question = args.slider(0, 1, .01, 0, label="Bennett's question", help_text="Bennett's question", option="--question", full_width=True)
    request = args.slider(0, 1, .01, 1, label="Bennett → Winter contact", help_text="Bennett → Winter contact", option="--request", full_width=True)
    disclosure = args.slider(0, 1, .01, 1, label="Winter → Bennett information", help_text="Winter → Bennett information", option="--disclosure", full_width=True)
    surprise = args.slider(0, 1, .01, 1, label="Bennett's surprise", help_text="Bennett's surprise", option="--surprise", full_width=True)
    cabinet_update = args.slider(0, 1, .01, 0, label="Bennett briefs the cabinet", help_text="Bennett briefs the cabinet", option="--cabinet-update", full_width=True)
    modern = args.slider(0, 1, .01, 0, label="2014 → 2026 rearrangement", help_text="2014 → 2026 rearrangement", option="--modern", full_width=True)
    alignment = args.slider(0, 1, .01, 1, label="2026 political grouping", help_text="2026 political grouping", option="--alignment", full_width=True)
    return (
        alignment,
        cabinet_update,
        disclosure,
        hierarchy,
        knowledge,
        modern,
        question,
        request,
        surprise,
        withheld,
    )


@app.cell
def _(
    alignment,
    animation_time,
    cabinet_update,
    clip,
    control_mode,
    disclosure,
    hierarchy,
    knowledge,
    modern,
    output_formats,
    preview_assets,
    question,
    render_scene,
    request,
    state_at,
    surprise,
    timeline,
    transparent,
    video_format,
    withheld,
):
    manual_state = dict(
        scene="tunnels", labels=timeline.get("labels", {}), events=[],
        hierarchy=hierarchy.value, knowledge=knowledge.value, withheld=withheld.value,
        question=question.value, request=request.value, disclosure=disclosure.value,
        surprise=surprise.value, cabinet_update=cabinet_update.value,
        modern=modern.value, alignment=alignment.value,
    )
    absolute_time = clip["start"] + animation_time.value
    scene_state = state_at(timeline, absolute_time) if control_mode.value == "timeline" else manual_state
    preview_width, preview_height = output_formats[video_format.value]
    scene_svg = render_scene(
        scene_state, assets=preview_assets,
        width=preview_width, height=preview_height, transparent=transparent.value,
    )
    return absolute_time, preview_height, preview_width, scene_state, scene_svg


@app.cell
def _(
    clip,
    clip_choice,
    preview_height,
    preview_width,
    shlex,
    transparent,
    video_format,
):
    export_parts = ["uv", "run", "python", "export_video.py", "--scene", "tunnels"]
    if video_format.value == "panel":
        export_parts += ["--width", str(preview_width), "--height", str(preview_height)]
    else:
        export_parts += ["--format", video_format.value]
    export_parts += ["--start", str(clip["start"]), "--end", str(clip["end"])]
    if transparent.value:
        export_parts += ["--transparent"]
    export_parts += ["--output", f"output/tunnels-{clip_choice.value}-{video_format.value}.{'mov' if transparent.value else 'mp4'}"]
    export_command = shlex.join(export_parts)
    return (export_command,)


@app.cell
def _(
    absolute_time,
    alignment,
    animation_time,
    cabinet_update,
    chapter,
    clip_choice,
    control_mode,
    disclosure,
    export_command,
    hierarchy,
    knowledge,
    mo,
    modern,
    preview_height,
    preview_width,
    question,
    request,
    scene_svg,
    surprise,
    transparent,
    video_format,
    withheld,
):
    preview = mo.Html(
        '<div style="background:repeating-conic-gradient(#e8ebef 0% 25%,white 0% 50%) 0 / 24px 24px;'
        f'border:1px solid #dbe0e6;border-radius:12px;overflow:hidden;line-height:0;'
        f'max-width:{min(1200, 740*preview_width/preview_height):g}px;margin:auto">{scene_svg}</div>'
    )
    manual_controls = mo.vstack([
        hierarchy, knowledge, withheld, question, request, disclosure,
        surprise, cabinet_update, modern, alignment,
    ])
    controls = mo.vstack([
        clip_choice, control_mode, video_format, transparent,
        chapter, animation_time,
        mo.md(f"Animation time: **{absolute_time:.2f}s**"),
        mo.accordion({"Manual controls": manual_controls}),
    ])
    mo.vstack([
        mo.md("## Tunnels · 2014 → 2026\nBennett stays on the right throughout."),
        mo.hstack([preview, controls], widths=[3, 1], align="start", gap=2),
        mo.md(
            "Export the selected **timeline clip**:\n\n```sh\n" + export_command + "\n```\n"
            "Manual controls change the frame preview; edit `timeline_tunnels.json` to change the animation. "
            "Timeline edits reload automatically.\n\n"
            "Playback with speed controls: `uv run python animation_preview.py --scene tunnels`"
        ),
    ])
    return


@app.cell
def _(
    json,
    mo,
    preview_height,
    preview_width,
    render_scene,
    scene_state,
    timeline,
    transparent,
):
    # Downloads embed portraits; the live preview continues using served URLs.
    def portable_svg():
        return render_scene(
            scene_state, width=preview_width, height=preview_height, transparent=transparent.value,
        ).encode()
    mo.hstack([
        mo.download(portable_svg, filename="tunnels-frame.svg", mimetype="image/svg+xml", label="Download this frame"),
        mo.download(json.dumps(timeline, ensure_ascii=False, indent=2).encode(), filename="timeline_tunnels.json", mimetype="application/json", label="Download timeline"),
    ], justify="start")
    return


@app.cell
def _(mo, timeline):
    production_notes = "\n\n".join(timeline.get("notes", []))
    mo.accordion({
        "Timing and source notes": mo.md(
            production_notes + "\n\n"
            "[Cabinet minutes and comptroller findings](https://www.ynetnews.com/articles/0,7340,L-4928735,00.html)"
        ),
    })
    return


@app.cell
def _(
    alignment,
    animation_time,
    args,
    cabinet_update,
    chapter,
    clip_choice,
    control_mode,
    disclosure,
    hierarchy,
    knowledge,
    modern,
    question,
    request,
    surprise,
    transparent,
    video_format,
    withheld,
):
    interface = args.interface(
        clip_choice, control_mode, video_format, transparent, chapter, animation_time,
        hierarchy, knowledge, withheld, question, request, disclosure, surprise,
        cabinet_update, modern, alignment,
    )
    interface
    return


if __name__ == "__main__":
    app.run()
