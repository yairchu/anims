import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import moops
    from pathlib import Path
    from animation_scene import render_scene
    from animation_timeline import load_timeline, state_at
    from export_video import encode_video

    return Path, encode_video, load_timeline, mo, moops, render_scene, state_at


@app.cell
def _(Path):
    timeline_path = Path(__file__).with_name("timeline_crew_list.json")
    return (timeline_path,)


@app.cell
def _(moops):
    args = moops.Group()
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
    ### FlyDubai · crew list binned
    The airline sends the crew list, with one flagged crew member, to the
    aviation authority, which throws it in the bin. The bin is a metaphor for
    unused information; say so in the narration.
    """)
    return


@app.cell
def _(args, mo, timeline):
    def label(key, option, name):
        return args.text(value=timeline["labels"][key], option=option, label=name, help_text=name)

    airline = label("airline", "--airline", "Airline")
    airline_role = label("airline_role", "--airline-role", "Airline caption")
    crew_list_title = label("list", "--list-title", "Crew list title")
    agency = label("agency", "--agency", "Receiving authority")
    agency_role = label("agency_role", "--agency-role", "Authority caption")
    transparent = args.checkbox(
        flag="--transparent",
        label="Transparent background",
        help_text="Export a ProRes 4444 MOV with alpha instead of an MP4",
    )
    output = args.text(
        option="--output",
        label="Output video",
        help_text="Output path (default: output/flydubai-crew-list.mp4, or .mov when transparent)",
    )
    mo.hstack(
        [airline, airline_role, crew_list_title, agency, agency_role, transparent, output],
        wrap=True,
    )
    return (
        agency,
        agency_role,
        airline,
        airline_role,
        crew_list_title,
        output,
        transparent,
    )


@app.cell
def _(
    agency,
    agency_role,
    airline,
    airline_role,
    args,
    crew_list_title,
    output,
    transparent,
):
    interface = args.interface(
        airline, airline_role, crew_list_title, agency, agency_role, transparent, output,
    )
    interface
    return (interface,)


@app.cell
def _(agency, agency_role, airline, airline_role, crew_list_title):
    live_labels = {
        "airline": airline.value,
        "airline_role": airline_role.value,
        "list": crew_list_title.value,
        "agency": agency.value,
        "agency_role": agency_role.value,
    }
    return (live_labels,)


@app.cell
def _(mo, timeline):
    chapter = mo.ui.dropdown(
        {f"{c['time']:g}s · {c['label']}": c["time"] for c in timeline["chapters"]},
        value=f"{timeline['chapters'][3]['time']:g}s · {timeline['chapters'][3]['label']}",
        label="Jump to chapter",
    )
    chapter
    return (chapter,)


@app.cell
def _(chapter, mo, timeline):
    time = mo.ui.slider(
        start=0,
        stop=timeline["duration"],
        step=1 / 30,
        value=chapter.value,
        label="Time (seconds)",
        show_value=True,
        full_width=True,
    )
    time
    return (time,)


@app.cell
def _(live_labels, mo, render_scene, state_at, time, timeline, transparent):
    frame_state = state_at(timeline, time.value) | {"labels": live_labels}
    scene_svg = render_scene(frame_state, width=1080, height=1920, transparent=transparent.value)
    mo.Html(
        '<div style="width:432px;max-width:100%;line-height:0;border:1px solid #dbe0e6;'
        'background:repeating-conic-gradient(#e8ebef 0% 25%,white 0% 50%) 0 0/24px 24px">'
        + scene_svg.replace('width="1080" height="1920"', 'width="432" height="768"', 1)
        + "</div>"
    )
    return


@app.cell
def _(mo):
    mo.md("""
    **Export:** click **Export video** below, or run the command under
    **Notebook CLI info** above. Edit timing in `timeline_crew_list.json`; it
    reloads automatically. The bottom ~500 px of the 1080×1920 frame stay clear
    for captions.
    """)
    return


@app.cell
def _(interface):
    export_button = interface.run_button(label="Export video")
    export_button
    return (export_button,)


@app.cell
def _(
    Path,
    encode_video,
    export_button,
    live_labels,
    mo,
    output,
    render_scene,
    state_at,
    timeline,
    transparent,
):
    mo.stop(not export_button.value)
    exported = Path(output.value or f"output/flydubai-crew-list.{'mov' if transparent.value else 'mp4'}")
    with mo.status.spinner("Exporting video..."):
        frames = encode_video(
            lambda t: render_scene(
                state_at(timeline, t) | {"labels": live_labels},
                width=timeline["width"],
                height=timeline["height"],
                transparent=transparent.value,
            ),
            output=exported,
            fps=timeline["fps"],
            start=0,
            end=timeline["duration"],
            transparent=transparent.value,
            overwrite=True,
        )
    print(f"Saved {exported.resolve()} ({frames} frames)")
    return


if __name__ == "__main__":
    app.run()
