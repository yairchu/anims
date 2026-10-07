"""FlyDubai crew list: sent by the airline, received by the aviation authority, binned.

Editorial illustration: the bin is a metaphor for unused information.
"""

from tunnels_scene import INK, MUTED, BLUE, clamp, cubic, partial_curve, path, text

RED = "#c0392b"
PAPER = "#fffdf7"
CARD_WIDTH, CARD_HEIGHT = 460, 130
AIRLINE = (360, 150)
AGENCY = (360, 650)
BIN, BIN_SCALE = (360, 860), 1.3
# The list slides out from behind the airline card, and is filed behind the
# authority's card like a letter in an inbox.
ISSUED, FILED = (360, 320), (360, 590)
LIST_SCALE, LIST_HALF_HEIGHT = .9, 90
# Enlarged mid-screen so the roster can be read.
ZOOM_CENTER, ZOOM_SCALE = (360, 470), 2.6
SEND_ROUTE = (ISSUED, (170, 380), (170, 500), FILED)
# Rises out of the authority's card first, then arcs around into the bin.
DISCARD_ROUTE = (FILED, (370, 380), (660, 560), (BIN[0], BIN[1] + 2))
FLAGGED_ROW = 2
ROWS = (-34, -6, 22, 50, 78)
PLANE = ("M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 "
         "3.5 1v-1.5L13 19v-5.5l8 2.5z")
BUILDING = "M2 9 12 3l10 6v1H2zm2 2h2v7H4zm5 0h2v7H9zm4 0h2v7h-2zm5 0h2v7h-2zM2 19h20v2H2z"


def mix(a, b, amount):
    return tuple(x + (y - x) * amount for x, y in zip(a, b))


def discard_scale(discard):
    return LIST_SCALE * (1 - .45*discard)


# On its way to the bin, the list comes to the front once it clears the card.
CLEARS_CARD = next(
    t / 100 for t in range(101)
    if cubic(DISCARD_ROUTE, t / 100)[1] + LIST_HALF_HEIGHT * discard_scale(t / 100)
    < AGENCY[1] - CARD_HEIGHT / 2
)


def avatar(masked):
    if not masked:
        return ('<circle r="11" fill="#eef1f4"/><circle cy="-3" r="4.5" fill="#c3cad3"/>'
                '<path d="M-8 9 Q-8 2 0 2 Q8 2 8 9Z" fill="#c3cad3"/>')
    # A generic balaclava silhouette: dark head and shoulders, an eye slit.
    return ('<circle r="11" fill="#fde8e6"/>'
            '<ellipse cy="-3" rx="5.5" ry="6.5" fill="#1d1f24"/>'
            '<path d="M-9 10 Q-9 2 0 2 Q9 2 9 10Z" fill="#1d1f24"/>'
            '<rect x="-4.5" y="-6" width="9" height="3" rx="1.5" fill="#d9a77f"/>'
            '<circle cx="-2" cy="-4.5" r=".9" fill="#1d1f24"/><circle cx="2" cy="-4.5" r=".9" fill="#1d1f24"/>')


def crew_list(title, flag):
    """A crew roster in a 140 × 180 box centered on the origin."""
    parts = [f'<rect x="-70" y="-90" width="140" height="180" rx="10" fill="{PAPER}" '
             'stroke="#d5d9df" stroke-width="2"/>',
             text(0, -62, title, 15, INK, "700"),
             path("M-56 -52 H56", "#e3e6ea", 1.5)]
    for index, y in enumerate(ROWS):
        masked = index == FLAGGED_ROW
        if masked:
            parts.append(f'<rect x="-64" y="{y-12}" width="128" height="24" rx="6" fill="{RED}" '
                         f'opacity="{.08 + .17*flag:g}"/>')
        parts.append(f'<g transform="translate(50 {y})">{avatar(masked)}</g>')
        parts.append(f'<rect x="-50" y="{y-7}" width="84" height="5" rx="2.5" fill="#c9ced6"/>')
        parts.append(f'<rect x="-22" y="{y+3}" width="56" height="4" rx="2" fill="#e0e3e8"/>')
    if flag > 0:
        parts.append(f'<circle cx="50" cy="{ROWS[FLAGGED_ROW]}" r="{12 + 4*flag:g}" fill="none" '
                     f'stroke="{RED}" stroke-width="2.5" opacity="{flag:g}"/>')
    return "".join(parts)


def card(name, position, icon, title, subtitle, opacity, highlight=0):
    x, y = position
    w, h = CARD_WIDTH, CARD_HEIGHT
    frame = f'x="{-w/2:g}" y="{-h/2:g}" width="{w}" height="{h}" rx="28"'
    return (f'<g id="{name}" transform="translate({x} {y})" opacity="{opacity:g}">'
            f'<rect {frame} fill="white" stroke="#e4e6e9" stroke-width="2"/>'
            f'<rect {frame} fill="none" stroke="{BLUE}" stroke-width="4" opacity="{highlight:g}"/>'
            f'<g transform="translate({w/2 - 100:g} -31) scale(2.6)"><path d="{icon}" fill="{BLUE}"/></g>'
            + text(-45, -4, title, 32, INK, "700")
            + text(-45, 34, subtitle, 22, MUTED)
            + '</g>')


def wastebasket_back():
    return '<ellipse cx="0" cy="-58" rx="50" ry="11" fill="#5d6874"/>'


def wastebasket_front():
    ribs = "".join(path(f"M{x} -44 L{x*.85:g} 52", "#7b8794", 3) for x in (-26, -9, 9, 26))
    return ('<path d="M-50 -58 A50 11 0 0 0 50 -58 L42 54 Q42 62 34 62 H-34 Q-42 62 -42 54 Z" fill="#8d99a6"/>'
            + ribs
            + '<path d="M-50 -58 A50 11 0 0 0 50 -58" fill="none" stroke="#b3bcc6" stroke-width="4"/>')


def render_crew_list(state, *, width=1080, height=1920, transparent=False):
    labels = state.get("labels", {})
    cards, list_in, zoom, flag = (clamp(state[name]) for name in ("cards", "list_in", "zoom", "flag"))
    send, bin_in, discard = (clamp(state[name]) for name in ("send", "bin_in", "discard"))

    if discard > 0:
        position = cubic(DISCARD_ROUTE, discard)
    elif send > 0:
        position = cubic(SEND_ROUTE, send)
    else:
        position = mix(AIRLINE, ISSUED, list_in)
    x, y = mix(position, ZOOM_CENTER, zoom)
    scale = LIST_SCALE + (ZOOM_SCALE - LIST_SCALE) * zoom if zoom else discard_scale(discard)
    roster = (f'<g id="crew-list" transform="translate({x:g} {y:g}) rotate({200*discard:g}) scale({scale:g})" '
              f'opacity="{clamp(3*list_in):g}">{crew_list(labels.get("list", "רשימת אנשי צוות"), flag)}</g>')
    in_front = zoom > 0 or (discard > 0 and discard >= CLEARS_CARD)

    background = "" if transparent else '<rect width="720" height="1280" fill="white"/>'
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 720 1280"
      role="img" aria-label="Crew list sent to the aviation authority and binned">{background}
      <g font-family="Arial, sans-serif">''']
    bin_transform = f'translate({BIN[0]} {BIN[1]}) scale({BIN_SCALE * (.6 + .4*bin_in):g})'
    if bin_in > 0:
        parts.append(f'<g id="bin-back" transform="{bin_transform}" opacity="{bin_in:g}">{wastebasket_back()}</g>')
    if send > 0:
        parts.append(path(partial_curve(SEND_ROUTE, send), BLUE, 3, stroke_dasharray="7 9", opacity=.7))
    if not in_front:
        parts.append(roster)
    # Fade the cards behind the zoomed list so the roster reads clearly.
    backdrop = cards * (1 - .8*zoom)
    parts.append(card("airline", AIRLINE, PLANE, labels.get("airline", "flydubai"),
                      labels.get("airline_role", "חברת התעופה"), backdrop))
    received = clamp((send - .9) / .1) * (1 - clamp(4*discard))
    parts.append(card("agency", AGENCY, BUILDING, labels.get("agency", "רשות התעופה האזרחית"),
                      labels.get("agency_role", "משרד התחבורה"), backdrop, received))
    if in_front:
        parts.append(roster)
    if bin_in > 0:
        parts.append(f'<g id="bin" transform="{bin_transform}" opacity="{bin_in:g}">{wastebasket_front()}</g>')
    parts.append('</g></svg>')
    return "".join(parts)
