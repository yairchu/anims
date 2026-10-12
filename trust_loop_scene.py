"""The trust loop: Netanyahu vouches for his partners, who say he's a liar.

It follows the quote chain, so their quotes are fresh and aren't repeated:
an arrow down from Netanyahu to his partners says "trust them", an arrow back
up says "he's a liar", a pulse chases around the loop, and the diagram then
shrinks to make room for the two ways out of it, which end in the same place.
"""

import html
import math

from animation_timeline import ease
from quote_chain_scene import RLM, TINT, hex_color, mix, rgb
from tunnels_scene import BLUE, INK, MUTED, RED, clamp, text

# Each beat follows the previous one; "loop" also sets how long the pulse runs.
TIMING = {"intro": .6, "partners": 1.2, "trust": 1, "trust_hold": .8, "liar": 1, "liar_hold": .8,
          "loop": 3, "settle": .8, "if_him": 1.8, "if_them": 1.8, "verdict": 1, "outro": 2.5}
BEATS = ("intro", "partners", "trust", "trust_hold", "liar", "liar_hold", "loop", "settle",
         "if_him", "if_them", "verdict", "outro")
LABELS = {"partners": "השותפים שהוא מציע שיובילו אותנו", "trust": "סמכו עליהם", "liar": "הוא שקרן",
          "if_him": "מאמינים לו? אז גם להם, והם אומרים שהוא שקרן", "if_them": "מאמינים להם? אז הוא שקרן",
          "verdict": "כך או כך, אי אפשר להאמין לו"}
LEADER = (360, 230, 110)
PARTNER_Y, PARTNER_R = 790, 78
# The pulse laps the loop this many times, speeding up.
LAPS = 2.5
# Once the loop has run, the diagram shrinks toward the top by this much.
SETTLED = .58
# Down the right side, from the leader to the partners, then back up the left.
TRUST_ARC = ((480, 290), (690, 340), (700, 560), (600, 660))
LIAR_ARC = ((120, 660), (20, 560), (30, 340), (240, 290))


def build_timeline(data):
    """Validate the loop and derive when each beat starts, the duration, and chapters."""
    timing = TIMING | data.get("timing", {})
    if not all(isinstance(timing.get(b), (int, float)) and math.isfinite(timing[b]) and timing[b] >= 0
               for b in BEATS):
        raise ValueError("Timing values must be finite and non-negative")
    speakers = data["speakers"]
    for name in [data["leader"], *data["partners"]]:
        if name not in speakers:
            raise ValueError(f"Unknown speaker: {name}")
    if not 1 <= len(data["partners"]) <= 4:
        raise ValueError("The loop needs one to four partners")
    starts, cursor = {}, 0
    for beat in BEATS:
        starts[beat] = cursor
        cursor += timing[beat]
    labels = LABELS | data.get("labels", {})
    chapters = [dict(time=starts[beat], label=label) for beat, label in (
        ("intro", "נתניהו והשותפים"), ("trust", labels["trust"]), ("liar", labels["liar"]),
        ("loop", "הלולאה"), ("if_him", "שתי הדרכים החוצה"), ("verdict", labels["verdict"]))]
    return dict(data, timing=timing, starts=starts, labels=labels, chapters=chapters, duration=cursor,
                tracks={}, events=[])


def loop_state(timeline, time):
    keys = ("speakers", "parties", "leader", "partners", "timing", "starts", "labels")
    return {key: timeline.get(key) for key in keys} | {"scene": "trust_loop", "time": time}


def cubic(points, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = points
    u = 1 - t
    return (u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3,
            u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3)


def cubic_start(points, t):
    """The part of the curve up to t, as its own cubic (de Casteljau)."""
    a, b, c, d = points
    lerp = lambda p, q: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    ab, bc, cd = lerp(a, b), lerp(b, c), lerp(c, d)
    abc, bcd = lerp(ab, bc), lerp(bc, cd)
    return a, ab, abc, lerp(abc, bcd)


def arrow(arrow_id, points, drawn, color, glow=0):
    """An arc drawn from its start up to `drawn`, with its head at the tip."""
    if drawn <= 0:
        return ""
    part = cubic_start(points, min(drawn, 1))
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = part
    # Back off from the tip along the curve, so the head points along it.
    bx, by = cubic(part, .9) if drawn > .05 else (x2, y2)
    angle = math.degrees(math.atan2(y3 - by, x3 - bx))
    path = f"M{x0:g} {y0:g} C{x1:g} {y1:g} {x2:g} {y2:g} {x3:g} {y3:g}"
    return (f'<g id="{arrow_id}">'
            + (f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{18 + 10 * glow:g}" '
               f'stroke-linecap="round" opacity="{.25 * glow:g}"/>' if glow > 0 else "")
            + f'<path d="{path}" fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round"/>'
            f'<path transform="translate({x3:g} {y3:g}) rotate({angle:g})" d="M6 0 L-22 -16 L-16 0 L-22 16 Z" '
            f'fill="{color}" stroke="{color}" stroke-width="4" stroke-linejoin="round"/></g>')


def pill(pill_id, x, y, label, color, appear, size=36):
    """A label on a white rounded card, popping in."""
    if appear <= 0:
        return ""
    width = len(label) * size * .55 + 44
    return (f'<g id="{pill_id}" transform="translate({x:g} {y:g}) scale({.6 + .4 * appear:g})" opacity="{appear:g}">'
            f'<rect x="{-width / 2:g}" y="{-size * .95:g}" width="{width:g}" height="{size * 1.75:g}" '
            f'rx="{size * .875:g}" fill="white" stroke="{color}" stroke-width="4"/>'
            + text(0, size * .35, RLM + label + RLM, size, color, "700") + '</g>')


def face(name, speaker, x, y, radius, appear, assets, highlight=0, color=BLUE):
    """Portrait and name, with a ring that lights up when the pulse passes."""
    if appear <= 0:
        return ""
    portrait = (
        f'<image href="{html.escape(assets[name], quote=True)}" x="{-radius}" y="{-radius}" width="{2 * radius}" '
        f'height="{2 * radius}" preserveAspectRatio="xMidYMid slice" clip-path="url(#clip-{name})"/>'
        if name in assets else
        f'<circle r="{radius}" fill="#f5ecdc"/><circle cy="{-radius * .17:g}" r="{radius * .23:g}" fill="#c0b8ac"/>'
        f'<path d="M{-radius * .43:g} {radius * .55:g} Q{-radius * .43:g} {radius * .12:g} 0 {radius * .12:g} '
        f'Q{radius * .43:g} {radius * .12:g} {radius * .43:g} {radius * .55:g}" fill="#c0b8ac"/>'
    )
    return (f'<g id="face-{name}" transform="translate({x:g} {y:g}) scale({.7 + .3 * appear:g})" opacity="{appear:g}">'
            f'<clipPath id="clip-{name}"><circle r="{radius}"/></clipPath>'
            f'<circle r="{radius + 6 + 8 * highlight:g}" fill="none" stroke="{color}" stroke-width="6" '
            f'opacity="{highlight:g}"/>'
            f'<circle r="{radius + 3}" fill="white" stroke="#e4e6e9" stroke-width="2"/>'
            + portrait + text(0, radius + 44, speaker["name"], round(radius * .36), INK, "700") + '</g>')


def render_trust_loop(state, *, assets, width=1080, height=1920, transparent=False):
    time, timing, starts, labels = state["time"], state["timing"], state["starts"], state["labels"]
    speakers, parties = state["speakers"], state.get("parties", {})
    leader, partners = state["leader"], state["partners"]

    def ramp(beat, offset=0, duration=None):
        duration = timing[beat] if duration is None else duration
        start = starts[beat] + offset
        return ease((time - start) / duration) if duration else float(time >= start)

    def color_of(name):
        party = speakers[name].get("party")
        return rgb(parties.get(party, {}).get("color", "#ffffff") if party else "#ffffff")

    white = [255] * 3
    lx, ly, lr = LEADER
    spacing = 600 / len(partners)
    partner_x = [60 + spacing * (i + .5) for i in range(len(partners))]

    # The pulse laps the loop, speeding up, then the arrows rest lit.
    loop = clamp((time - starts["loop"]) / timing["loop"]) if timing["loop"] else float(time >= starts["loop"])
    laps = LAPS * loop * loop
    lap = laps % 1 if loop < 1 else 0
    pulse = loop > 0 and loop < 1
    # Which half of the loop the pulse is on, and how recently it reached each end.
    on_trust = pulse and lap < .5

    def flash(arrival):
        """Brightest as the pulse arrives, fading over the next quarter lap."""
        if not pulse:
            return 0
        since = (lap - arrival) % 1
        return clamp(1 - since * 4) if laps >= arrival else 0

    parts = []
    trust_drawn, liar_drawn = ramp("trust"), ramp("liar")
    parts.append(arrow("trust-arrow", TRUST_ARC, trust_drawn, BLUE, glow=float(pulse and on_trust)))
    parts.append(arrow("liar-arrow", LIAR_ARC, liar_drawn, RED, glow=float(pulse and not on_trust)))
    parts.append(pill("trust-label", 560, 470, labels["trust"], BLUE, ramp("trust", .5, .4)))
    parts.append(pill("liar-label", 160, 470, labels["liar"], RED, ramp("liar", .5, .4)))

    # The partners' group: a card with its caption, drawn under their faces.
    group = ramp("partners", 0, .5)
    if group > 0:
        parts.append(f'<g id="partners" opacity="{group:g}"><rect x="40" y="672" width="640" height="{PARTNER_R * 2 + 120}" '
                     f'rx="34" fill="white" fill-opacity=".55" stroke="{MUTED}" stroke-width="3" '
                     f'stroke-dasharray="14 10"/>'
                     + text(360, 672 + PARTNER_R * 2 + 172, labels["partners"], 32, MUTED, "700") + '</g>')
    parts.append(face(leader, speakers[leader], lx, ly, lr, ramp("intro"), assets, flash(0), RED))
    stagger = timing["partners"] / (len(partners) + 1)
    for i, name in enumerate(partners):
        parts.append(face(name, speakers[name], partner_x[i], PARTNER_Y, PARTNER_R,
                          ramp("partners", stagger * (i + 1), stagger * 1.5), assets, flash(.5), BLUE))
    if pulse:
        x, y = cubic(TRUST_ARC, lap * 2) if on_trust else cubic(LIAR_ARC, lap * 2 - 1)
        color = BLUE if on_trust else RED
        parts.append(f'<g id="pulse"><circle cx="{x:g}" cy="{y:g}" r="26" fill="{color}" opacity=".25"/>'
                     f'<circle cx="{x:g}" cy="{y:g}" r="14" fill="{color}" stroke="white" stroke-width="4"/></g>')

    # Centred on the frame at first, the diagram then shrinks toward the top,
    # making room for the ways out.
    settle = ramp("settle")
    scale = 1 - (1 - SETTLED) * settle
    diagram = (f'<g id="diagram" transform="translate({360 * (1 - scale):g} {90 - 130 * settle:g}) scale({scale:g})">'
               + "".join(parts) + '</g>')

    reasoning = []
    for beat, color, y in (("if_him", BLUE, 720), ("if_them", RED, 880)):
        appear = ramp(beat, 0, .5)
        if appear > 0:
            reasoning.append(
                f'<g id="{beat}" opacity="{appear:g}" transform="translate(0 {30 * (1 - appear):g})">'
                f'<rect x="60" y="{y - 62}" width="600" height="112" rx="26" fill="white" fill-opacity=".8" '
                f'stroke="{color}" stroke-width="4"/>'
                + wrapped_lines(360, y - 14, labels[beat], 34, INK) + '</g>')
    verdict = ramp("verdict", 0, .6)
    if verdict > 0:
        reasoning.append(f'<g id="verdict" opacity="{verdict:g}" transform="translate(360 1060) scale({.8 + .2 * verdict:g})">'
                         f'<rect x="-310" y="-58" width="620" height="116" rx="30" fill="{INK}"/>'
                         + text(0, 16, RLM + labels["verdict"] + RLM, 44, "white", "800") + '</g>')

    background = "" if transparent else (
        '<defs><linearGradient id="loop-background" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset=".1" stop-color="{hex_color(mix(white, color_of(leader), TINT))}"/>'
        '<stop offset=".7" stop-color="#ffffff"/></linearGradient></defs>'
        '<rect width="720" height="1280" fill="url(#loop-background)"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 720 1280" '
            f'role="img" aria-label="Trust loop"><g font-family="Arial, sans-serif">'
            f'{background}{diagram}{"".join(reasoning)}</g></svg>')


def wrapped_lines(x, y, value, size, color):
    """Up to two centred lines, split at the comma or the middle word."""
    if len(value) <= 26:
        return text(x, y + size * .65, RLM + value + RLM, size, color, "700")
    split = value.find(", ") + 1 or len(value) // 2
    if not value.find(", ") + 1:
        split = value.rfind(" ", 0, split) + 1 or split
    lines = (value[:split].strip(), value[split:].strip())
    return "".join(text(x, y + index * size * 1.25, RLM + line + RLM, size, color, "700")
                   for index, line in enumerate(lines))
