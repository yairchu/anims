import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import moops
    from pathlib import Path
    from animation_scene import ACTOR_FILES, ASSET_FILES, notebook_asset_urls, render_scene
    from animation_timeline import load_timeline, state_at
    from export_video import encode_video
    from quote_chain_scene import cue_sheet

    return (
        ACTOR_FILES,
        ASSET_FILES,
        Path,
        cue_sheet,
        encode_video,
        load_timeline,
        mo,
        moops,
        notebook_asset_urls,
        render_scene,
        state_at,
    )


@app.cell
def _(Path):
    timeline_path = Path(__file__).with_name("timeline_quote_chain.json")
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
    get_asset_mtimes, set_asset_mtimes = mo.state(None)
    return get_asset_mtimes, set_asset_mtimes


@app.cell
def _(ACTOR_FILES, ASSET_FILES, Path, mo, set_asset_mtimes):
    # Poll the portraits and icons, including ones that don't exist yet, so
    # adding or replacing one (ben_gvir.png, saar.png, ...) refreshes the preview.
    def watch_assets():
        from time import sleep

        paths = [Path(__file__).with_name(f) for f in (ASSET_FILES | ACTOR_FILES).values()]

        def mtimes():
            return {p.name: p.stat().st_mtime_ns if p.exists() else None for p in paths}

        last = mtimes()
        thread = mo.current_thread()
        while not thread.should_exit:
            sleep(1)
            if (current := mtimes()) != last:
                last = current
                set_asset_mtimes(current)

    mo.Thread(target=watch_assets, daemon=True).start()
    return


@app.cell
def _(get_asset_mtimes, notebook_asset_urls):
    get_asset_mtimes()
    preview_assets = notebook_asset_urls()
    return (preview_assets,)


@app.cell
def _(mo):
    mo.md(r"""
    ### Quote chain · who said what about whom
    Each speaker appears with their quote, revealed at speaking pace, while the
    next speaker appears below; then the camera scrolls to them. Quotes,
    speakers, and timing are in `timeline_quote_chain.json`, which reloads
    automatically. Set each quote's `duration` to the length of its audio clip.
    Speakers without a portrait PNG (named by speaker id) show a silhouette.
    """)
    return


@app.cell
def _(args, mo, timeline):
    quote_text_scale = args.slider(
        start=.7,
        stop=1.3,
        step=.05,
        value=timeline.get("quote_text_scale", 1),
        option="--quote-text-size",
        label="Quote text size",
        help_text="Scale of the quote text; long quotes still shrink to fit three lines",
        show_value=True,
    )
    background_tilt = args.slider(
        start=-45,
        stop=45,
        step=1,
        value=timeline.get("background_tilt", 15),
        option="--background-tilt",
        label="Background tilt",
        help_text="Degrees the background's colour bands rise toward the left; negative rises to the right",
        show_value=True,
    )
    output = args.text(
        option="--output",
        label="Output video",
        help_text="Output path (default: output/quote-chain.mp4); a .mov exports ProRes 422 HQ for editing",
    )
    mo.hstack([quote_text_scale, background_tilt, output], wrap=True)
    return background_tilt, output, quote_text_scale


@app.cell
def _(args, background_tilt, output, quote_text_scale):
    interface = args.interface(quote_text_scale, background_tilt, output)
    interface
    return (interface,)


@app.cell
def _(background_tilt, quote_text_scale):
    live_overrides = {"quote_text_scale": quote_text_scale.value, "background_tilt": background_tilt.value}
    return (live_overrides,)


@app.cell
def _(mo, timeline):
    chapter = mo.ui.dropdown(
        {f"{c['time']:.1f}s · {c['label']}": c["time"] for c in timeline["chapters"]},
        value=f"{timeline['chapters'][1]['time']:.1f}s · {timeline['chapters'][1]['label']}",
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
        value=chapter.value + 1,
        label="Time (seconds)",
        show_value=True,
        full_width=True,
    )
    time
    return (time,)


@app.cell
def _(
    live_overrides,
    mo,
    preview_assets,
    render_scene,
    state_at,
    time,
    timeline,
):
    frame_state = state_at(timeline, time.value) | live_overrides
    scene_svg = render_scene(frame_state, assets=preview_assets, width=1080, height=1920)
    mo.Html(
        '<div style="width:432px;max-width:100%;line-height:0;border:1px solid #dbe0e6">'
        + scene_svg.replace('width="1080" height="1920"', 'width="432" height="768"', 1)
        + "</div>"
    )
    return


@app.cell
def _(cue_sheet, mo, timeline):
    mo.vstack([
        mo.md(f"**Audio cue sheet** · place each clip at its start time · total {timeline['duration']:.1f}s"),
        mo.ui.table(cue_sheet(timeline), selection=None),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    **Export:** click **Export video** below, or run the command under
    **Notebook CLI info** above.
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
    live_overrides,
    mo,
    output,
    render_scene,
    state_at,
    timeline,
):
    mo.stop(not export_button.value)
    exported = Path(output.value or "output/quote-chain.mp4")
    with mo.status.spinner("Exporting video..."):
        frames = encode_video(
            lambda t: render_scene(
                state_at(timeline, t) | live_overrides,
                width=timeline["width"],
                height=timeline["height"],
            ),
            output=exported,
            fps=timeline["fps"],
            start=0,
            end=timeline["duration"],
            overwrite=True,
        )
    print(f"Saved {exported.resolve()} ({frames} frames)")
    return


if __name__ == "__main__":
    app.run()
