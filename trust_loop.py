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

    return (
        ACTOR_FILES,
        ASSET_FILES,
        Path,
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
    timeline_path = Path(__file__).with_name("timeline_trust_loop.json")
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
    ### Trust loop · he vouches for them, they call him a liar
    Follows the quote chain, so the partners' quotes aren't repeated. An arrow
    down from Netanyahu tells us to trust his partners, an arrow back up says
    he's a liar, and a pulse chases around the loop. The diagram then shrinks
    to make room for the two ways out, which end at the same verdict. Text,
    partners, and timing are in `timeline_trust_loop.json`, which reloads
    automatically.
    """)
    return


@app.cell
def _(args):
    output = args.text(
        option="--output",
        label="Output video",
        help_text="Output path (default: output/trust-loop.mp4); a .mov exports ProRes 422 HQ for editing",
    )
    interface = args.interface(output)
    interface
    return interface, output


@app.cell
def _(mo, timeline):
    chapter = mo.ui.dropdown(
        {f"{c['time']:.1f}s · {c['label']}": c["time"] for c in timeline["chapters"]},
        value=f"{timeline['chapters'][-1]['time']:.1f}s · {timeline['chapters'][-1]['label']}",
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
        value=chapter.value + .5,
        label="Time (seconds)",
        show_value=True,
        full_width=True,
    )
    time
    return (time,)


@app.cell
def _(
    mo,
    preview_assets,
    render_scene,
    state_at,
    time,
    timeline,
):
    frame_state = state_at(timeline, time.value)
    scene_svg = render_scene(frame_state, assets=preview_assets, width=1080, height=1920)
    mo.Html(
        '<div style="width:432px;max-width:100%;line-height:0;border:1px solid #dbe0e6">'
        + scene_svg.replace('width="1080" height="1920"', 'width="432" height="768"', 1)
        + "</div>"
    )
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
    mo,
    output,
    render_scene,
    state_at,
    timeline,
):
    mo.stop(not export_button.value)
    exported = Path(output.value or "output/trust-loop.mp4")
    frames = encode_video(
        lambda t: render_scene(
            state_at(timeline, t),
            width=timeline["width"],
            height=timeline["height"],
        ),
        output=exported,
        fps=timeline["fps"],
        start=0,
        end=timeline["duration"],
        overwrite=True,
        progress=lambda indices: mo.status.progress_bar(indices, title="Exporting video"),
    )
    print(f"Saved {exported.resolve()} ({frames} frames)")
    return


if __name__ == "__main__":
    app.run()
