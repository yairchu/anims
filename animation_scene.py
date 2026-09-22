"""Shared SVG artwork for the notebook, timeline preview, and video exporter."""
import base64
import html
import math
from functools import lru_cache
from pathlib import Path
from scene_defaults import (RECONCILIATION_END, RIGHT_ZONE_START,
                            ISRAELI_COLOR, PALESTINIAN_COLOR, NEEDLE_COLOR)

def meter_point(position, radius=240):
    angle = math.radians(-50 + 100 * position)
    return 300 + radius * math.sin(angle), 340 - radius * math.cos(angle)


def zone_wedge(start, end):
    x0, y0 = meter_point(start)
    x1, y1 = meter_point(end)
    return f"M300 340 L{x0:.3f} {y0:.3f} A240 240 0 0 1 {x1:.3f} {y1:.3f} Z"


def zone_emphasis(position, reconciliation_end=RECONCILIATION_END, right_zone_start=RIGHT_ZONE_START):
    """Continuous emphasis, zero at a boundary and full at the end of the arc."""
    def smooth(value):
        value = max(0, min(1, value))
        return value * value * (3 - 2 * value)

    return (smooth((reconciliation_end-position)/reconciliation_end),
            smooth((position-right_zone_start)/(1-right_zone_start)))


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
    reconciliation_end=RECONCILIATION_END,
    right_zone_start=RIGHT_ZONE_START,
    mutual_reconciliation=False,
    reconciliation_strength=0,
    zone_labels=(("פתח", "לפיוס"), ("חלון", "לסיפוח")),
    translated_zone_labels=None,
    reveal=None,
):
    reveal = reveal or {}
    left_reveal = reveal.get("left_reveal", 1)
    right_reveal = reveal.get("right_reveal", 1)
    arc_reveal = reveal.get("arc_reveal", 1)
    needle_reveal = reveal.get("needle_reveal", 1)
    logos_reveal = reveal.get("logos_reveal", 1)
    zones_reveal = reveal.get("zones_reveal", 1)
    arc_x, arc_y = meter_point(1 - arc_reveal)
    # Mirror only the geometry so the labels and logos stay upright.
    geometry_transform = (
        "translate(0 400) scale(1 -1)" if upside_down else ""
    )
    # Vertical reflection preserves the left-to-right needle sweep.
    needle_angle = -50 + 100 * position
    label_y = 166 if upside_down else 194

    def render_labels(texts, opacity, blur=0, layer="original"):
        text_svg = "".join(
            f'<text opacity="{visibility}" x="{x}" y="{label_y + 15 * (3 - len(lines)) + 30 * line}">'
            f"{html.escape(text)}</text>"
            for x, lines, visibility in zip((60, 540), texts, (left_reveal, right_reveal))
            for line, text in enumerate(lines)
        )
        return render_text_layer(text_svg, opacity, blur, layer)

    def render_text_layer(text_svg, opacity, blur=0, layer="original"):
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
    # Wedges share the needle's pivot and exact 100-degree sweep.
    left_active = position <= reconciliation_end
    right_depth = max(0, min(1, (position-right_zone_start)/(1-right_zone_start)))
    left_opacity = .32 if mutual_reconciliation else (.23 if left_active else .10)
    right_opacity = .10 + .25 * right_depth
    zones_svg = (
        f'<path data-zone="reconciliation" d="{zone_wedge(0, reconciliation_end)}" '
        f'fill="#55b98b" fill-opacity="{left_opacity*zones_reveal}"/>'
        f'<path data-zone="right" d="{zone_wedge(right_zone_start, 1)}" '
        f'fill="#e5a044" fill-opacity="{right_opacity*zones_reveal}"/>'
    )

    def render_zone_labels(texts):
        parts = []
        for center, lines, color in zip(
            (reconciliation_end/2, (right_zone_start+1)/2), texts, ("#277351", "#955c18")
        ):
            x, y = meter_point(center, radius=178)
            # Follow the arc tangent; reflection reverses the tilt, not the text.
            angle = -50 + 100 * center
            if upside_down:
                y = 400-y
                angle = -angle
            text_svg = "".join(
                f'<text x="{x:.3f}" y="{y + 17*(line-(len(lines)-1)/2):.3f}" fill="{color}">{html.escape(text)}</text>'
                for line, text in enumerate(lines)
            )
            parts.append(f'<g transform="rotate({angle:.3f} {x:.3f} {y:.3f})">{text_svg}</g>')
        return "".join(parts)

    zone_text = render_text_layer(render_zone_labels(zone_labels), 1)
    if translated_zone_labels is not None:
        zone_text = render_text_layer(render_zone_labels(zone_labels), 1-blend, 8*blend, "zones-original")
        zone_text += render_text_layer(render_zone_labels(translated_zone_labels), blend, 8*(1-blend), "zones-translation")

    logo_y = 46 if upside_down else 274
    left_emphasis, right_emphasis = zone_emphasis(position, reconciliation_end, right_zone_start)

    def render_logo(index, uri):
        center_x, center_y = (60, 540)[index], logo_y+40
        emphasis = (left_emphasis, right_emphasis)[index]
        color = ("#55b98b", "#e5a044")[index]
        scale = 1 + .25*emphasis
        # Both left icons receive the same extra glow as the shared opportunity grows.
        glow = .55*emphasis + (.30*reconciliation_strength if index == 0 else 0)
        filter_id = f"{meter_id}-logo-{index}-zone-glow"
        return f'''<defs>
          <filter id="{filter_id}" x="-50%" y="-50%" width="200%" height="200%"
                  color-interpolation-filters="sRGB">
            <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="{color}" flood-opacity="{glow:.6f}"/>
          </filter>
        </defs>
        <g data-icon-zone="{'reconciliation' if index == 0 else 'right'}" data-scale="{scale:.6f}" opacity="{logos_reveal * (left_reveal, right_reveal)[index]}"
           transform="translate({center_x} {center_y}) scale({scale:.6f}) translate({-center_x} {-center_y})">
          <image href="{html.escape(uri, quote=True)}" x="{center_x-40}" y="{logo_y}"
                 width="80" height="80" filter="url(#{filter_id})"/>
        </g>'''

    logo_svg = "".join(render_logo(index, uri) for index, uri in enumerate(logos))
    return f'''<g id="{meter_id}" transform="translate(0 {y_offset})"
                   role="img" aria-label="{html.escape(title, quote=True)}">
      <g transform="{geometry_transform}">
        {zones_svg}
        <path id="{meter_id}-arc" d="M 483.851 185.731 A 240 240 0 0 0 {arc_x:.3f} {arc_y:.3f}"
              opacity="{1 if arc_reveal > 0 else 0}" fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round" />
        <g id="{meter_id}-needle" opacity="{needle_reveal}">
        <g transform="rotate({needle_angle} 300 340)">
          <path d="M 294 340 L 300 112 L 306 340 Z" fill="{needle_color}" />
        </g>
        <circle cx="300" cy="340" r="12" fill="{needle_color}" />
        <circle cx="300" cy="340" r="4" fill="white" />
        </g>
      </g>
      <g fill="black" font-size="26" font-family="Arial, sans-serif"
         text-anchor="middle" direction="rtl">{label_svg}</g>
      <g opacity="{zones_reveal}" font-size="16" font-family="Arial, sans-serif" text-anchor="middle" direction="rtl"
         stroke="white" stroke-width="2" stroke-opacity=".8" paint-order="stroke">{zone_text}</g>
      {logo_svg}
    </g>'''


ASSET_FILES = {
    "vegan": "vegan-friendly.png", "cfp": "cfp_logo.png", "kach": "Kach.svg",
    "hamas": "Emblem_of_Hamas.svg", "portrait": "smotrich_and_bibi.png",
}


ACTOR_FILES = {"netanyahu": "netanyahu.png", "abbas": "mansur_abbas.png", "smotrich": "smotrich.png"}


def available_asset_files():
    return ASSET_FILES | {name: filename for name, filename in ACTOR_FILES.items()
                          if Path(__file__).with_name(filename).is_file()}


def notebook_asset_urls():
    """Serve assets through marimo's file endpoint, once per asset-loading cell.

    This is the same virtual-file helper used by mo.image. In script/static
    export contexts marimo falls back to data URLs, keeping those portable.
    """
    from marimo._output.data import data as mo_data

    return {name: mo_data.image(Path(__file__).with_name(filename).read_bytes(),
                                ext=Path(filename).suffix).url
            for name, filename in available_asset_files().items()}


def embedded_assets():
    return {
        name: "data:image/" + ("svg+xml" if filename.endswith(".svg") else "png")
        + ";base64," + encoded_asset(filename, Path(__file__).with_name(filename).stat().st_mtime_ns)
        for name, filename in available_asset_files().items()
    }


@lru_cache(maxsize=32)
def encoded_asset(filename, modified):
    return base64.b64encode(Path(__file__).with_name(filename).read_bytes()).decode()


def render_actor(name, label, x, y, opacity, assets):
    if opacity <= 0:
        return ""
    portrait = (f'<image href="{html.escape(assets[name], quote=True)}" x="-55" y="-105" width="110" height="110" preserveAspectRatio="xMidYMax meet"/>'
                if name in assets else '<circle cy="-43" r="22" fill="#dce4ee"/><path d="M-36 0 Q-36-25 0-25 Q36-25 36 0" fill="#dce4ee"/>')
    return f'''<g id="actor-{name}" transform="translate({x} {y})" opacity="{opacity}">
      {portrait}
      <rect x="-65" y="5" width="130" height="35" rx="10" fill="white" stroke="#d1d9e2"/>
      <text y="29" text-anchor="middle" direction="rtl" font-size="19" font-family="Arial, sans-serif" fill="#27364b">{label}</text>
    </g>'''


def render_blocked(state, assets):
    """A hypothetical needle never changes the actual political-position track."""
    y = state["israeli_y"]
    left_x = 140 + 30 * state["netanyahu"]
    right_x = 460 - 30 * state["abbas"]
    actor_y = y + 10
    partnership = f'''<g id="partnership" opacity="{state['partnership']}">
      <path d="M{left_x+65} {actor_y-18} H{right_x-65}" stroke="#55a986" stroke-width="4" stroke-dasharray="8 6"/>
      <text x="300" y="{actor_y-36}" direction="rtl" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#277351">שותפות אפשרית</text>
    </g>'''
    potential = f'''<g id="potential-needle" opacity="{state['potential_opacity']}" transform="translate(0 {y})">
      <g transform="rotate({-50+100*state['potential_position']} 300 340)">
        <path d="M300 330 V112" fill="none" stroke="#379970" stroke-width="5" stroke-dasharray="9 7"/>
        <path d="M292 126 L300 112 L308 126" fill="none" stroke="#379970" stroke-width="4"/>
      </g>
      <text x="200" y="382" text-anchor="middle" direction="rtl" font-family="Arial, sans-serif" font-size="19" fill="#277351">אפשרות ליותר דו־קיום</text>
    </g>'''
    block = f'''<g id="partnership-block" opacity="{state['block']}" stroke="#ac5151" stroke-width="5" stroke-linecap="round">
      <path d="M288 {actor_y-30} L312 {actor_y-6} M312 {actor_y-30} L288 {actor_y-6}"/>
    </g>'''
    # The blocker enters from above, leaving the meter and its actual needle readable.
    actors = render_actor("netanyahu", "נתניהו", left_x, actor_y, state["netanyahu"], assets)
    actors += render_actor("abbas", "מנסור עבאס", right_x, actor_y, state["abbas"], assets)
    actors += render_actor("smotrich", "סמוטריץ׳", 300, actor_y-120-35*(1-state["smotrich"]), state["smotrich"], assets)
    caption = f'''<text id="blocked-outcome" x="300" y="{y+382}" opacity="{state['outcome']}"
      text-anchor="middle" direction="rtl" font-family="Arial, sans-serif" font-size="19" fill="#5c6674">האפשרות נחסמה</text>'''
    return partnership + potential + actors + block + caption


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


def render_scene(state, *, assets=None, width=1080, height=1920, transparent=False,
                 israeli_color=ISRAELI_COLOR, palestinian_color=PALESTINIAN_COLOR, needle_color=NEEDLE_COLOR,
                 reconciliation_end=RECONCILIATION_END, right_zone_start=RIGHT_ZONE_START):
    if not 0 < reconciliation_end < right_zone_start < 1:
        raise ValueError("Zone boundaries must satisfy 0 < left < right < 1")
    assets = embedded_assets() if assets is None else assets
    # Transition cards use the same canvas/background and work with alpha export.
    if state.get("scene") == "transition":
        background = "" if transparent else '<rect width="100%" height="100%" fill="white"/>'
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
          {background}<text x="{width/2}" y="{height/2}" text-anchor="middle" direction="rtl"
          font-family="Arial, sans-serif" font-size="{min(width,height)*.045}" fill="{israeli_color}"
          opacity="{state.get('scene_opacity',1)}">{html.escape(state['title'])}</text></svg>'''
    blocked = state.get("scene") == "blocked"
    intro = state.get("scene") == "intro"
    mutual = (state["israeli_position"] <= reconciliation_end
              and state["palestinian_position"] <= reconciliation_end
              and state["palestinian_y"] >= 0)
    shared_strength = min(
        zone_emphasis(state["israeli_position"], reconciliation_end, right_zone_start)[0],
        zone_emphasis(state["palestinian_position"], reconciliation_end, right_zone_start)[0],
    ) if mutual else 0
    zone_options = dict(reconciliation_strength=shared_strength, reconciliation_end=reconciliation_end, right_zone_start=right_zone_start,
                        mutual_reconciliation=mutual)
    # The drawing has a stable coordinate space; changing output size never changes motion.
    view_width = max(720, 720 * width / height)
    view_height = view_width * height / width
    view_x = (600-view_width)/2
    view_y = (720-view_height)/2
    background = "" if transparent else f'<rect x="{view_x}" y="{view_y}" width="{view_width}" height="{view_height}" fill="white"/>'
    # Keep the hidden neighbour above the actual frame in both aspect ratios.
    pal_y = state["palestinian_y"] + view_y * max(0, min(1, -state["palestinian_y"] / 400))
    portrait_start_x = view_x + view_width + 20
    portrait_x = portrait_start_x + (430 - portrait_start_x) * state["portrait"]
    portrait_y = state["israeli_y"] + 20
    portrait = f'''<g>
      <image href="{html.escape(assets['portrait'], quote=True)}" x="{portrait_x}" y="{portrait_y}" width="140" height="140"/>
    </g>'''
    pal = render_meter(meter_id="palestinian", title="Palestinian political meter",
        color=palestinian_color, needle_color=needle_color, position=state["palestinian_position"],
        y_offset=pal_y, upside_down=True,
        labels=(("الحقوق", "للجميع"), ("فلسطين", "للمسلمين", "فقط")),
        translated_labels=(("לכולם", "מגיע", "זכויות"), ("פלסטין", "למוסלמים", "בלבד")),
        translation_progress=state["translation"], logos=(assets["cfp"], assets["hamas"]),
        zone_labels=(("فرصة", "للمصالحة"), ("خطر", "التصعيد")),
        translated_zone_labels=(("פתח", "לפיוס"), ("סכנת", "הסלמה")), **zone_options)
    isr = render_meter(meter_id="israeli", title="Israeli political meter", color=israeli_color,
        needle_color=needle_color, position=state["israeli_position"], y_offset=state["israeli_y"],
        labels=(("לכולם", "מגיע", "זכויות"), ("ישראל", "ליהודים", "בלבד")),
        logos=(assets["vegan"], assets["kach"]), reveal=state, **zone_options)
    connection = ""
    if mutual:
        x0, y0 = meter_point(reconciliation_end/2)
        y_top = pal_y + 400-y0
        y_bottom = state["israeli_y"] + y0
        connection = f'''<path id="reconciliation-connection"
          d="M{x0:.3f} {y_top:.3f} C{x0-55:.3f} {y_top+40:.3f}, {x0-55:.3f} {y_bottom-40:.3f}, {x0:.3f} {y_bottom:.3f}"
          fill="none" stroke="#55b98b" stroke-width="12" stroke-opacity=".25" stroke-linecap="round"/>'''
    if blocked or intro:
        portrait, pal, connection = "", "", ""
    scene_art = "" if intro else render_blocked(state, assets) if blocked else render_events(state)
    # A neutral visual highlight of the outcome, without inventing dialogue or motive.
    outcome = f'''<g opacity="{state['outcome']}" fill="none" stroke="{israeli_color}" stroke-width="3">
      <circle cx="300" cy="{state['israeli_y']+340}" r="20"/>
    </g>'''
    if blocked or intro:
        outcome = ""
    artwork = f"{portrait}{connection}{pal}{isr}{scene_art}{outcome}"
    if "scene_opacity" in state:
        artwork = f'<g opacity="{state["scene_opacity"]}">{artwork}</g>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
        viewBox="{view_x} {view_y} {view_width} {view_height}" style="max-width:100%;height:auto;overflow:hidden"
        role="img" aria-label="Political spectrum animation">
      {background}{artwork}
    </svg>'''
