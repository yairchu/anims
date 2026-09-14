import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full")


@app.cell
def _():
    import base64
    import marimo as mo
    import pathlib

    return base64, mo, pathlib


@app.cell
def _(mo):
    isr_y_slider = mo.ui.slider(0, 1, 0.001, 0.5, label="Israel political axis y", full_width=True)
    isr_y_slider
    return (isr_y_slider,)


@app.cell
def _(isr_y_slider):
    isr_y = isr_y_slider.value
    return (isr_y,)


@app.cell
def _():
    line_y = 0.08
    return (line_y,)


@app.cell
def _():
    label_x = 0.12
    return (label_x,)


@app.cell
def _():
    label_common = 'font-size="0.07" text-anchor="middle" alignment-baseline="middle" fill="black"'
    return (label_common,)


@app.cell
def _(base64, pathlib):
    vegan_logo_path = pathlib.Path(__file__).with_name("vegan-friendly.png")
    vegan_logo_uri = "data:image/png;base64," + base64.b64encode(vegan_logo_path.read_bytes()).decode("ascii")
    return (vegan_logo_uri,)


@app.cell
def _(base64, pathlib):
    kach_logo_path = pathlib.Path(__file__).with_name("Kach.svg")
    kach_logo_uri = "data:image/svg+xml;base64," + base64.b64encode(kach_logo_path.read_bytes()).decode("ascii")
    return (kach_logo_uri,)


@app.cell
def _(isr_y, kach_logo_uri, label_common, label_x, line_y, mo, vegan_logo_uri):
    mo.md(f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 1 1" style="max-width: 100%; height: auto;" role="img">
    <line x1="0.23" y1="{isr_y}" x2="0.75" y2="{isr_y}" stroke="blue" stroke-width="0.02" />
    <text x="{label_x}" y="{isr_y - line_y}" {label_common}> לכולם </text>
    <text x="{label_x}" y="{isr_y}" {label_common}> מגיע </text>
    <text x="{label_x}" y="{isr_y + line_y}" {label_common}> זכויות </text>
    <image href="{vegan_logo_uri}" x="0.02" y="{isr_y + 0.14}" width="0.15" height="0.15" />
    <text x="{1 - label_x}" y="{isr_y - line_y}" {label_common}> ישראל </text>
    <text x="{1 - label_x}" y="{isr_y}" {label_common}> ליהודים </text>
    <text x="{1 - label_x}" y="{isr_y + line_y}" {label_common}> בלבד </text>
    <image href="{kach_logo_uri}" x="0.83" y="{isr_y + 0.14}" width="0.15" height="0.15">
      <title>כך</title>
    </image>
    </svg>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <g fill="#b45309" stroke="#b45309">
      <line x1="0.32" y1="0.36" x2="0.64" y2="0.36" stroke-width="0.018" stroke-linecap="round" />
      <polygon points="0.69,0.36 0.63,0.325 0.63,0.395" stroke="none" />
    </g>
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
