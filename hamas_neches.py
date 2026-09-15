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
    pal_meter_color_picker = mo.ui.anywidget(
        wigglystuff.ColorPicker(color="#149149")
    )
    mo.hstack(
        [mo.md("Palestinian meter color:"), pal_meter_color_picker], justify="start"
    )
    return (pal_meter_color_picker,)


@app.cell
def _(pal_meter_color_picker):
    pal_meter_color = pal_meter_color_picker.value["color"]
    return (pal_meter_color,)


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
def _():
    from html import escape

    def render_meter(
        *, meter_id, title, color, needle_color, position, labels,
        y_offset=0, upside_down=False, logos=(),
    ):
        # Mirror only the geometry so the labels and logos stay upright.
        geometry_transform = "translate(0 400) scale(1 -1)" if upside_down else ""
        # Vertical reflection preserves the left-to-right needle sweep.
        needle_angle = -50 + 100 * position
        label_y = 166 if upside_down else 194
        label_svg = "".join(
            f'<text x="{x}" y="{label_y + 30 * line}">{escape(text)}</text>'
            for x, lines in zip((60, 540), labels)
            for line, text in enumerate(lines)
        )
        logo_y = 46 if upside_down else 274
        logo_svg = "".join(
            f'<image href="{escape(uri, quote=True)}" x="{x}" y="{logo_y}" '
            f'width="80" height="80"><title>{escape(name)}</title></image>'
            for x, (uri, name) in zip((20, 500), logos)
        )
        return f'''<g id="{meter_id}" transform="translate(0 {y_offset})"
                       role="img" aria-label="{escape(title, quote=True)}">
          <g transform="{geometry_transform}">
            <path d="M 116.149 185.731 A 240 240 0 0 1 483.851 185.731"
                  fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round" />
            <g transform="rotate({needle_angle} 300 340)">
              <path d="M 294 340 L 300 112 L 306 340 Z" fill="{needle_color}" />
            </g>
            <circle cx="300" cy="340" r="12" fill="{needle_color}" />
            <circle cx="300" cy="340" r="4" fill="white" />
          </g>
          <g fill="black" font-size="26" font-family="Arial, sans-serif"
             text-anchor="middle" direction="rtl">{label_svg}</g>
          {logo_svg}
        </g>'''

    return (render_meter,)


@app.cell
def _(
    isr_meter_color,
    isr_meter_y_offset,
    kach_logo_uri,
    mo,
    needle_color,
    pal_meter_color,
    political_position,
    render_meter,
    vegan_logo_uri,
):
    meters_svg = "".join(
        render_meter(
            **config,
            needle_color=needle_color,
            position=political_position.value,
        )
        for config in (
            dict(
                meter_id="palestinian-political-meter",
                title="Palestinian political meter",
                color=pal_meter_color,
                upside_down=True,
                labels=(("טקסט", "שמאל", "זמני"), ("טקסט", "ימין", "זמני")),
            ),
            dict(
                meter_id="israeli-political-meter",
                title="Israeli political meter",
                color=isr_meter_color,
                y_offset=300 + isr_meter_y_offset.value,
                labels=(("לכולם", "מגיע", "זכויות"), ("ישראל", "ליהודים", "בלבד")),
                logos=((vegan_logo_uri, "Vegan Friendly"), (kach_logo_uri, "כך")),
            ),
        )
    )
    mo.Html(f'''
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="1000" viewBox="0 0 600 1000"
         style="max-width: 100%; height: auto; background: white;" role="img"
         aria-labelledby="political-meter-title">
      <title id="political-meter-title">מדדים פוליטיים — פלסטינים וישראלים</title>
      <rect width="600" height="1000" fill="none" stroke="black" />
      {meters_svg}
    </svg>
    ''')
    return


if __name__ == "__main__":
    app.run()
