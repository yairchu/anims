import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full")


@app.cell
def _():
    import base64
    import html
    import marimo as mo
    import pathlib
    import wigglystuff

    return base64, html, mo, pathlib, wigglystuff


@app.cell
def _(mo):
    political_position = mo.ui.slider(
        0,
        1,
        0.001,
        0.5,
        label="Israeli political position (left → right)",
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
def _(mo):
    pal_meter_y_offset = mo.ui.slider(
        -400,
        300,
        1,
        -400,
        label="Palestinian meter vertical offset (positive → down)",
        show_value=True,
        full_width=True,
    )
    pal_meter_y_offset
    return (pal_meter_y_offset,)


@app.cell
def _(mo):
    pal_political_position = mo.ui.slider(
        0,
        1,
        0.001,
        0.5,
        label="Palestinian political position (left → right)",
        show_value=False,
        full_width=True,
    )
    pal_political_position
    return (pal_political_position,)


@app.cell
def _(mo):
    pal_translation_progress = mo.ui.slider(
        0,
        1,
        0.01,
        0,
        label="Palestinian labels: Arabic → Hebrew (blur)",
        show_value=True,
        full_width=True,
    )
    pal_translation_progress
    return (pal_translation_progress,)


@app.cell
def _(mo):
    far_right_peek_progress = mo.ui.slider(
        0,
        1,
        0.01,
        1,
        label="Smotrich and Bibi: in frame ← → offscreen",
        show_value=True,
        full_width=True,
    )
    far_right_peek_progress
    return (far_right_peek_progress,)


@app.cell
def _(base64, pathlib):
    def image(name):
        mime = name.rsplit(".", 1)[-1]
        if mime == "svg":
            mime = "svg+xml"
        return f"data:image/{mime};base64," + base64.b64encode(
            pathlib.Path(__file__).with_name(name).read_bytes()
        ).decode("ascii")

    return (image,)


@app.cell
def _(image):
    vegan_friendly_logo = image("vegan-friendly.png")
    return (vegan_friendly_logo,)


@app.cell
def _(image):
    cfp_logo = image("cfp_logo.png")
    return (cfp_logo,)


@app.cell
def _(image):
    kach_logo = image("Kach.svg")
    return (kach_logo,)


@app.cell
def _(image):
    hamas_logo = image("Emblem_of_Hamas.svg")
    return (hamas_logo,)


@app.cell
def _(image):
    smotrich_and_bibi_image = image("smotrich_and_bibi.png")
    return (smotrich_and_bibi_image,)


@app.cell
def _(far_right_peek_progress, isr_meter_y_offset, smotrich_and_bibi_image):
    # Dragging left brings the image fully inside, with a small edge margin.
    peek_progress = 1 - far_right_peek_progress.value
    peek_eased = peek_progress * peek_progress * (3 - 2 * peek_progress)
    peek_x = 600 - 170 * peek_eased
    peek_y = 300 + isr_meter_y_offset.value + 20
    far_right_peek_svg = f'''
      <image href="{smotrich_and_bibi_image}" x="{peek_x}" y="{peek_y}"
             width="140" height="140" preserveAspectRatio="xMidYMid meet">
        <title>Smotrich and Bibi peeking above the Israeli far-right label</title>
      </image>
    '''
    return (far_right_peek_svg,)


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
        [mo.md("Palestinian meter color:"), pal_meter_color_picker],
        justify="start",
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
def _(html):
    def render_meter(
        *,
        meter_id,
        title,
        color,
        needle_color,
        position,
        labels,
        y_offset=0,
        upside_down=False,
        logos=(),
        translated_labels=None,
        translation_progress=0,
    ):
        # Mirror only the geometry so the labels and logos stay upright.
        geometry_transform = (
            "translate(0 400) scale(1 -1)" if upside_down else ""
        )
        # Vertical reflection preserves the left-to-right needle sweep.
        needle_angle = -50 + 100 * position
        label_y = 166 if upside_down else 194

        def render_labels(texts, opacity, blur=0, layer="original"):
            text_svg = "".join(
                f'<text x="{x}" y="{label_y + 15 * (3 - len(lines)) + 30 * line}">'
                f"{html.escape(text)}</text>"
                for x, lines in zip((60, 540), texts)
                for line, text in enumerate(lines)
            )
            if blur == 0:
                return f'<g opacity="{opacity}">{text_svg}</g>'
            filter_id = f"{meter_id}-{layer}-blur"
            return f'''<defs>
              <filter id="{filter_id}" x="-20%" y="-50%" width="140%" height="200%">
                <feGaussianBlur stdDeviation="{blur}" />
              </filter>
            </defs>
            <g opacity="{opacity}" filter="url(#{filter_id})">{text_svg}</g>'''

        # Smoothstep eases the reveal while keeping it fully scrubbable.
        progress = max(0, min(1, translation_progress))
        blend = progress * progress * (3 - 2 * progress)
        label_svg = render_labels(labels, 1)
        if translated_labels is not None:
            # At the midpoint both languages are softly defocused; endpoints are crisp.
            label_svg = render_labels(labels, 1 - blend, blur=8 * blend)
            label_svg += render_labels(
                translated_labels,
                blend,
                blur=8 * (1 - blend),
                layer="translation",
            )
        logo_y = 46 if upside_down else 274
        logo_svg = "".join(
            f'<image href="{html.escape(uri, quote=True)}" x="{x}" y="{logo_y}" '
            f'width="80" height="80"></image>'
            for x, uri in zip((20, 500), logos)
        )
        return f'''<g id="{meter_id}" transform="translate(0 {y_offset})"
                       role="img" aria-label="{html.escape(title, quote=True)}">
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
    cfp_logo,
    far_right_peek_svg,
    hamas_logo,
    isr_meter_color,
    isr_meter_y_offset,
    kach_logo,
    mo,
    needle_color,
    pal_meter_color,
    pal_meter_y_offset,
    pal_political_position,
    pal_translation_progress,
    political_position,
    render_meter,
    vegan_friendly_logo,
):
    meters_svg = "".join(
        render_meter(
            **config,
            needle_color=needle_color,
        )
        for config in (
            dict(
                meter_id="palestinian-political-meter",
                title="Palestinian political meter",
                color=pal_meter_color,
                y_offset=pal_meter_y_offset.value,
                position=pal_political_position.value,
                upside_down=True,
                labels=(("الحقوق", "للجميع"), ("فلسطين", "للمسلمين", "فقط")),
                translated_labels=(
                    ("לכולם", "מגיע", "זכויות"),
                    ("פלסטין", "למוסלמים", "בלבד"),
                ),
                translation_progress=pal_translation_progress.value,
                logos=(
                    cfp_logo,
                    hamas_logo,
                ),
            ),
            dict(
                meter_id="israeli-political-meter",
                title="Israeli political meter",
                color=isr_meter_color,
                position=political_position.value,
                y_offset=300 + isr_meter_y_offset.value,
                labels=(
                    ("לכולם", "מגיע", "זכויות"),
                    ("ישראל", "ליהודים", "בלבד"),
                ),
                logos=(vegan_friendly_logo, kach_logo),
            ),
        )
    )
    mo.Html(f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="1000" viewBox="0 0 600 1000"
         style="max-width: 100%; height: auto; background: white; overflow: hidden;" role="img"
         aria-labelledby="political-meter-title">
      <title id="political-meter-title">מדדים פוליטיים — פלסטינים וישראלים</title>
      {far_right_peek_svg}
      {meters_svg}
      <rect width="600" height="1000" fill="none" stroke="black" />
    </svg>
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
