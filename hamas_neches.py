import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    <svg height="400" viewBox="0 0 1 1">
    <line x1="0.2" y1="0.5" x2="0.8" y2="0.5" stroke="blue" stroke-width="0.02" />
    <text x="0.1" y="0.5" font-size="0.07" text-anchor="middle" alignment-baseline="middle" fill="black">
      שמאל
    </text>
    <text x="0.87" y="0.5" font-size="0.07" text-anchor="middle" alignment-baseline="middle" fill="black">
      ימין
    </text>
    </svg>
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
