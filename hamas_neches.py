import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full")


@app.cell
def _():
    import base64
    import marimo as mo
    import pathlib
    import wigglystuff

    return base64, mo, pathlib, wigglystuff


@app.cell
def _(mo):
    political_position = mo.ui.slider(
        0,
        1,
        0.001,
        0.5,
        label="Political position (left → right)",
        show_value=False,
        full_width=True,
    )
    political_position
    return (political_position,)


@app.cell
def _(mo):
    isr_meter_y_offset = mo.ui.slider(
        0,
        300,
        1,
        150,
        label="Israel meter vertical offset (positive → down)",
        show_value=True,
        full_width=True,
    )
    isr_meter_y_offset
    return (isr_meter_y_offset,)


@app.cell
def _(base64, pathlib):
    vegan_logo_path = pathlib.Path(__file__).with_name("vegan-friendly.png")
    vegan_logo_uri = "data:image/png;base64," + base64.b64encode(
        vegan_logo_path.read_bytes()
    ).decode("ascii")
    return (vegan_logo_uri,)


@app.cell
def _(base64, pathlib):
    kach_logo_path = pathlib.Path(__file__).with_name("Kach.svg")
    kach_logo_uri = "data:image/svg+xml;base64," + base64.b64encode(
        kach_logo_path.read_bytes()
    ).decode("ascii")
    return (kach_logo_uri,)


@app.cell
def _(mo, wigglystuff):
    isr_meter_color_picker = mo.ui.anywidget(
        wigglystuff.ColorPicker(color="#0056d6")
    )
    mo.hstack(
        [mo.md("Israel meter color:"), isr_meter_color_picker], justify="start"
    )
    return (isr_meter_color_picker,)


@app.cell
def _(isr_meter_color_picker):
    isr_meter_color = isr_meter_color_picker.value["color"]
    return (isr_meter_color,)


@app.cell
def _(mo, wigglystuff):
    needle_color_picker = mo.ui.anywidget(
        wigglystuff.ColorPicker(color="#7a7a7a")
    )
    mo.hstack([mo.md("Needle color:"), needle_color_picker], justify="start")
    return (needle_color_picker,)


@app.cell
def _(needle_color_picker):
    needle_color = needle_color_picker.value["color"]
    return (needle_color,)


@app.cell
def _(
    isr_meter_color,
    isr_meter_y_offset,
    kach_logo_uri,
    mo,
    needle_color,
    political_position,
    vegan_logo_uri,
):
    # The needle sweeps 100 degrees along a circle centered on its pivot.
    needle_angle = -50 + 100 * political_position.value
    mo.Html(f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="700" viewBox="0 0 600 700"
         style="max-width: 100%; height: auto; background: white;" role="img"
         aria-labelledby="political-meter-title">
      <title id="political-meter-title">מד פוליטי משמאל לימין — המחשה</title>
      <rect width="600" height="700" fill="none" stroke="black" />
      <g id="israeli-political-meter" transform="translate(0 {isr_meter_y_offset.value})">
        <path d="M 116.149 185.731 A 240 240 0 0 1 483.851 185.731"
              fill="none" stroke="{isr_meter_color}" stroke-width="10" stroke-linecap="round" />
        <g fill="black" font-size="26" font-family="Arial, sans-serif"
           text-anchor="middle" direction="rtl">
          <text x="60" y="194">לכולם</text>
          <text x="60" y="224">מגיע</text>
          <text x="60" y="254">זכויות</text>
          <text x="540" y="194">ישראל</text>
          <text x="540" y="224">ליהודים</text>
          <text x="540" y="254">בלבד</text>
        </g>
        <image href="{vegan_logo_uri}" x="20" y="274" width="80" height="80">
          <title>Vegan Friendly</title>
        </image>
        <image href="{kach_logo_uri}" x="500" y="274" width="80" height="80">
          <title>כך</title>
        </image>
        <g transform="rotate({needle_angle} 300 340)">
          <path d="M 294 340 L 300 112 L 306 340 Z" fill="{needle_color}" />
        </g>
        <circle cx="300" cy="340" r="12" fill="{needle_color}" />
        <circle cx="300" cy="340" r="4" fill="white" />
      </g>
    </svg>
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
