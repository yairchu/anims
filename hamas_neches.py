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
    political_position = mo.ui.slider(
        0, 1, 0.001, 0.5, label="Political position (left → right)",
        show_value=False, full_width=True,
    )
    political_position
    return (political_position,)


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
def _(kach_logo_uri, mo, political_position, vegan_logo_uri):
    # The needle sweeps 100 degrees along a circle centered on its pivot.
    needle_angle = -50 + 100 * political_position.value
    mo.Html(f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400"
         style="max-width: 100%; height: auto; background: white;" role="img"
         aria-labelledby="political-meter-title">
      <title id="political-meter-title">מד פוליטי משמאל לימין — המחשה</title>
      <path d="M 116.149 185.731 A 240 240 0 0 1 483.851 185.731"
            fill="none" stroke="blue" stroke-width="10" stroke-linecap="round" />
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
        <path d="M 294 340 L 300 112 L 306 340 Z" fill="#b45309" />
      </g>
      <circle cx="300" cy="340" r="12" fill="#b45309" />
      <circle cx="300" cy="340" r="4" fill="white" />
    </svg>
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
