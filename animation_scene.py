"""Shared SVG artwork for the notebook, timeline preview, and video exporter."""
import base64
import html
import math
from functools import lru_cache
from pathlib import Path

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


ASSET_FILES = {
    "vegan": "vegan-friendly.png", "cfp": "cfp_logo.png", "kach": "Kach.svg",
    "hamas": "Emblem_of_Hamas.svg", "portrait": "smotrich_and_bibi.png",
}


@lru_cache
def embedded_assets():
    return {
        name: "data:image/" + ("svg+xml" if filename.endswith(".svg") else "png")
        + ";base64," + base64.b64encode(Path(__file__).with_name(filename).read_bytes()).decode()
        for name, filename in ASSET_FILES.items()
    }


def bezier(start, control, end, progress):
    p = progress
    point = tuple((1-p)**2*a + 2*(1-p)*p*b + p*p*c for a, b, c in zip(start, control, end))
    tangent = tuple(2*(1-p)*(b-a) + 2*p*(c-b) for a, b, c in zip(start, control, end))
    return *point, math.degrees(math.atan2(tangent[1], tangent[0]))


def render_events(state):
    parts = []
    for event in state["events"]:
        p = event["progress"]
        if event["kind"] == "cash":
            x, y, angle = bezier((500, state["israeli_y"]+85), (710, 270),
                                (540, state["palestinian_y"]+86), p)
            parts.append(f'''<g transform="translate({x} {y}) rotate({angle + 90})">
              <rect x="-22" y="-13" width="44" height="26" rx="3" fill="#a8ce8d" stroke="#375a32" stroke-width="2"/>
              <rect x="-17" y="-9" width="34" height="18" rx="2" fill="none" stroke="#547746"/>
              <text text-anchor="middle" y="6" font-size="18" fill="#254627">$</text>
            </g>''')
        elif event["kind"] == "knife":
            # The projectile starts at Hamas's emblem, not at the Palestinian population.
            x, y, angle = bezier((540, state["palestinian_y"]+86), (100, 280),
                                (345, state["israeli_y"]+230), min(1, p / .8))
            if p < .8:
                parts.append(f'''<g transform="translate({x} {y}) rotate({angle})">
                  <path d="M-18,-4 H8 L31,0 L8,7 H-18 Z" fill="#cbd3dc" stroke="#4b5563" stroke-width="1.5"/>
                  <rect x="-37" y="-5" width="19" height="11" rx="2" fill="#734d38"/>
                  <path d="M-18,-8 V10" stroke="#333" stroke-width="3"/>
                </g>''')
            else:
                burst = (p-.8)/.2
                parts.append(f'<circle cx="{x}" cy="{y}" r="{8+26*burst}" fill="none" stroke="#c45145" stroke-width="3" opacity="{1-burst}"/>')
        else:
            # Unsuccessful direct nudges: the corresponding needle track springs back.
            x = 375 + 20 * math.sin(math.pi*p)
            y = state["israeli_y"] + 190
            parts.append(f'''<g transform="translate({x} {y})" opacity="{math.sin(math.pi*p)}">
              <path d="M-30,0 H20 M7,-12 L20,0 L7,12" fill="none" stroke="#b77b2c" stroke-width="6" stroke-linecap="round"/>
            </g>''')
    return "".join(parts)


def render_scene(state, *, assets=None, width=1920, height=1080, transparent=False,
                 israeli_color="#0056d6", palestinian_color="#149149", needle_color="#7a7a7a"):
    assets = embedded_assets() if assets is None else assets
    # The drawing has a stable coordinate space; changing output size never changes motion.
    view_height = 720
    view_width = max(640, view_height * width / height)
    view_x = (600-view_width)/2
    background = "" if transparent else f'<rect x="{view_x}" width="{view_width}" height="720" fill="white"/>'
    portrait_start_x = view_x + view_width + 20
    portrait_x = portrait_start_x + (430 - portrait_start_x) * state["portrait"]
    portrait_y = state["israeli_y"] + 20
    portrait = f'''<g>
      <image href="{html.escape(assets['portrait'], quote=True)}" x="{portrait_x}" y="{portrait_y}" width="140" height="140"/>
    </g>'''
    pal = render_meter(meter_id="palestinian", title="Palestinian political meter",
        color=palestinian_color, needle_color=needle_color, position=state["palestinian_position"],
        y_offset=state["palestinian_y"], upside_down=True,
        labels=(("الحقوق", "للجميع"), ("فلسطين", "للمسلمين", "فقط")),
        translated_labels=(("לכולם", "מגיע", "זכויות"), ("פלסטין", "למוסלמים", "בלבד")),
        translation_progress=state["translation"], logos=(assets["cfp"], assets["hamas"]))
    isr = render_meter(meter_id="israeli", title="Israeli political meter", color=israeli_color,
        needle_color=needle_color, position=state["israeli_position"], y_offset=state["israeli_y"],
        labels=(("לכולם", "מגיע", "זכויות"), ("ישראל", "ליהודים", "בלבד")),
        logos=(assets["vegan"], assets["kach"]))
    # A neutral visual highlight of the outcome, without inventing dialogue or motive.
    outcome = f'''<g opacity="{state['outcome']}" fill="none" stroke="{israeli_color}" stroke-width="3">
      <circle cx="300" cy="{state['israeli_y']+340}" r="20"/>
    </g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
        viewBox="{view_x} 0 {view_width} {view_height}" style="max-width:100%;height:auto;overflow:hidden"
        role="img" aria-label="Political spectrum animation">
      {background}{portrait}{pal}{isr}{render_events(state)}{outcome}
    </svg>'''
