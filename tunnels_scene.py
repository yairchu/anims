"""Seekable hierarchy artwork. Bennett stays on the right in both eras."""

import html
import textwrap


INK = "#25364b"
MUTED = "#6d7988"
LINE = "#adb7c2"
AMBER = "#b77924"
RED = "#b75351"
BLUE = "#356a9a"
HISTORICAL = {
    "netanyahu": (440, 190),
    "gantz": (235, 410),
    "winter": (235, 660),
    "bennett": (790, 430),
}
CONTEMPORARY = {
    "netanyahu": (325, 220),
    "gantz": (180, 550),
    "winter": (470, 550),
    "bennett": (790, 220),
}
ACTOR_LABELS = {
    "netanyahu": ("בנימין נתניהו", "ראש הממשלה", "הליכוד"),
    "gantz": ("בני גנץ", "הרמטכ״ל", "ראש מפלגה"),
    "winter": ("עופר וינטר", "מפקד חטיבת גבעתי", "ראש מפלגה"),
    "bennett": ("נפתלי בנט", "חבר הקבינט", "ראש מפלגה"),
}


def clamp(value):
    return max(0, min(1, value))


PORTRAIT_HISTORICAL = {"netanyahu": (270, 275), "gantz": (190, 560),
                       "winter": (190, 920), "bennett": (525, 590)}
PORTRAIT_CONTEMPORARY = {"netanyahu": (220, 300), "gantz": (220, 620),
                         "winter": (220, 915), "bennett": (525, 300)}


def actor_positions(modern, portrait=False):
    blend = clamp(modern)
    historical = PORTRAIT_HISTORICAL if portrait else HISTORICAL
    contemporary = PORTRAIT_CONTEMPORARY if portrait else CONTEMPORARY
    return {
        name: tuple(a + (b - a) * blend for a, b in zip(position, contemporary[name]))
        for name, position in historical.items()
    }


def text(x, y, value, size=23, color=INK, weight="400", **attributes):
    attrs = " ".join(f'{key.replace("_", "-")}="{html.escape(str(value), quote=True)}"'
                     for key, value in attributes.items())
    return (f'<text x="{x:g}" y="{y:g}" text-anchor="middle" direction="rtl" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" {attrs}>'
            f'{html.escape(value)}</text>')


def wrapped_text(x, y, value, size=25, color=INK, max_chars=32, **attributes):
    return "".join(text(x, y + index * (size + 9), line, size, color, **attributes)
                   for index, line in enumerate(textwrap.wrap(value, max_chars,
                                                              break_long_words=False, break_on_hyphens=False)))


def path(d, color=LINE, width=3, **attributes):
    attrs = " ".join(f'{key.replace("_", "-")}="{html.escape(str(value), quote=True)}"'
                     for key, value in attributes.items())
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round" {attrs}/>')


def cubic(points, progress):
    p = clamp(progress)
    return tuple((1-p)**3*a + 3*(1-p)**2*p*b + 3*(1-p)*p*p*c + p**3*d
                 for a, b, c, d in zip(*points))


def partial_curve(points, progress):
    """De Casteljau subdivision works identically in browsers and resvg.

    resvg does not implement SVG pathLength-based dash normalization.
    """
    p = clamp(progress)
    a, b, c, d = points
    mix = lambda start, end: tuple(x + (y-x)*p for x, y in zip(start, end))
    ab, bc, cd = mix(a, b), mix(b, c), mix(c, d)
    abc, bcd = mix(ab, bc), mix(bc, cd)
    end = mix(abc, bcd)
    return f'M{a[0]:g} {a[1]:g} C{ab[0]:g} {ab[1]:g} {abc[0]:g} {abc[1]:g} {end[0]:g} {end[1]:g}'


def document(x, y, opacity=1, scale=1):
    return f'''<g transform="translate({x:g} {y:g}) scale({scale:g})" opacity="{opacity:g}">
      <rect x="-19" y="-25" width="38" height="50" rx="5" fill="#fff8e9" stroke="{AMBER}" stroke-width="2.5"/>
      <path d="M-10-12 H10 M-10-3 H10 M-10 7 H4" fill="none" stroke="{AMBER}" stroke-width="2.5" stroke-linecap="round"/>
    </g>'''


def actor(name, position, opacity, modern, assets, labels):
    x, y = position
    title, role_2014, role_2026 = ACTOR_LABELS[name]
    title = labels.get(name, title)
    role_2026 = labels.get(name + "_2026", role_2026)
    portrait = (
        f'<image href="{html.escape(assets[name], quote=True)}" x="-64" y="-64" '
        f'width="128" height="128" preserveAspectRatio="xMidYMid slice" clip-path="url(#portrait-clip)"/>'
        if name in assets else
        '<circle r="64" fill="#f5ecdc"/><circle cy="-15" r="22" fill="#c0b8ac"/>'
        '<path d="M-41 53 Q-41 10 0 10 Q41 10 41 53" fill="#c0b8ac"/>'
    )
    return (f'<g id="actor-{name}" transform="translate({x:g} {y:g})" opacity="{opacity:g}">'
            '<circle r="68" fill="white" stroke="#e4e6e9" stroke-width="2"/>'
            + portrait
            + text(0, 96, title, 25, weight="700")
            + text(0, 124, role_2014, 19, MUTED, opacity=clamp(1-3*modern))
            + text(0, 124, role_2026, 19, MUTED, opacity=clamp(3*modern-2))
            + '</g>')


def render_tunnels(state, *, assets, width=1080, height=1920, transparent=False):
    modern = clamp(state["modern"])
    history = clamp(1 - 3*modern)
    hierarchy = clamp(state["hierarchy"])
    labels = state.get("labels", {})
    portrait = width / height < .75
    positions = actor_positions(modern, portrait)
    historical = PORTRAIT_HISTORICAL if portrait else HISTORICAL
    base_width, base_height = (720, 1280) if portrait else (1000, 870)
    view_width = max(base_width, base_height * width / height)
    view_height = view_width * height / width
    view_x, view_y = (base_width-view_width)/2, (base_height-view_height)/2
    cabinet = (410, 420, 250, 395) if portrait else (650, 300, 285, 325)
    request_points = (((453, 638), (360, 740), (405, 915), (262, 920)) if portrait
                      else ((721, 478), (610, 520), (450, 663), (307, 660)))
    reply_points = (((262, 885), (340, 845), (365, 590), (434, 590)) if portrait
                    else ((307, 625), (475, 588), (608, 430), (699, 430)))
    # Reserve the bottom ~27% of portrait exports for captions added in the editor.
    content_y = -140 if portrait else 0
    background = "" if transparent else (
        f'<rect x="{view_x:g}" y="{view_y:g}" width="{view_width:g}" height="{view_height:g}" fill="white"/>'
    )
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
      viewBox="{view_x:g} {view_y:g} {view_width:g} {view_height:g}"
      style="max-width:100%;height:auto" role="img" aria-label="2014 tunnel briefing and 2026 political alignment">
      <defs>
        <clipPath id="portrait-clip"><circle r="64"/></clipPath>
      </defs>{background}<g id="diagram" transform="translate(0 {content_y})" font-family="Arial, sans-serif">''']
    # Cabinet membership and military command are separate branches.
    cabinet_glow = clamp(state["cabinet_update"])
    parts.append(f'<g id="historical-structure" opacity="{history*hierarchy:g}">')
    cx, cy, cw, ch = cabinet
    parts.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="22" fill="#f5f7fa" stroke="#dfe4ea" stroke-width="2"/>')
    parts.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="22" fill="#fff8e9" stroke="{AMBER}" stroke-width="3" opacity="{cabinet_glow:g}"/>')
    parts.append(wrapped_text(cx+cw/2, cy+36, "הקבינט המדיני־ביטחוני", 23 if portrait else 22, MUTED, max_chars=16 if portrait else 40))
    parts.extend([
        path("M270 407 V450 H190 V491" if portrait else "M440 322 V338 H235 V341"),
        path("M340 275 H390 V395 H535 V420" if portrait else "M510 190 H600 V275 H790 V300"),
        path("M190 692 V847" if portrait else "M235 542 V587", stroke_dasharray="3 10"),
        ('<rect x="115" y="760" width="150" height="30" rx="8" fill="white"/>' if portrait
         else '<rect x="160" y="550" width="150" height="24" rx="8" fill="white"/>'),
        text(190 if portrait else 235, 782 if portrait else 568, "דרגי ביניים", 20 if portrait else 17, MUTED),
    ])
    for x in ((465, 510, 565, 610) if portrait else (705, 750, 835, 880)):
        parts.append(f'<g transform="translate({x} {775 if portrait else 585})" fill="#cbd3dd"><circle cy="-8" r="8"/><path d="M-13 13 Q-13 2 0 2 Q13 2 13 13"/></g>')
    parts.append('</g>')

    # Modern grouping is editorial political alignment, with dashed connectors.
    align = modern * clamp(state["alignment"])
    parts.append(f'<g id="political-alignment" opacity="{align:g}">')
    parts.extend([
        ('<rect x="65" y="210" width="310" height="865" rx="26" fill="#f5f7fa"/>' if portrait
         else '<rect x="70" y="140" width="530" height="586" rx="26" fill="#f5f7fa"/>'),
        path("M397 215 V1075" if portrait else "M635 145 V730", "#d8dee5", 2),
        path("M220 435 V458 H110 V915 H148 M110 620 H148" if portrait else "M325 355 V418 M180 418 H470 M180 418 V478 M470 418 V478", MUTED, 3, stroke_dasharray="8 9"),
        text(220 if portrait else 325, 490 if portrait else 700, labels.get("camp_2026", "מחנה נתניהו"), 25, weight="700",
             style="paint-order:stroke;stroke:#f5f7fa;stroke-width:12px;stroke-linejoin:round"),
        text(525 if portrait else 790, 490 if portrait else 415, labels.get("opposition_2026", "מול נתניהו"), 25 if portrait else 24, BLUE, weight="700"),
    ])
    parts.append('</g>')

    # Expose missing briefing before revealing the direct contact.
    withheld = clamp(state["withheld"])
    parts.append(f'<g id="missing-briefing" opacity="{history*withheld:g}">')
    parts.extend([
        ('<rect x="373" y="315" width="34" height="40" rx="8" fill="white"/>' if portrait
         else '<rect x="583" y="222" width="34" height="40" rx="8" fill="white"/>'),
        path("M383 328 H397 M383 341 H397" if portrait else "M593 235 H607 M593 248 H607", RED, 4),
        wrapped_text(535 if portrait else 758, 326 if portrait else 251,
                     labels.get("withheld", "הקבינט לא עודכן בהיקף האיום"), 23 if portrait else 20, RED,
                     max_chars=16 if portrait else 60),
    ])
    parts.append('</g>')

    request = clamp(state["request"])
    disclosure = clamp(state["disclosure"])
    parts.append(f'<g id="direct-contact" opacity="{history:g}">')
    if request > 0:
        parts.append(path(partial_curve(request_points, request), BLUE, 3,
                          opacity=.8 * (1-.55*disclosure)))
        rx, ry = cubic(request_points, request)
        parts.append(f'<circle cx="{rx:g}" cy="{ry:g}" r="5" fill="{BLUE}" opacity="{1-disclosure:g}"/>')
        parts.append(wrapped_text(525 if portrait else 500, 885 if portrait else 657, "פנייה ישירה לחבר", 23 if portrait else 20, BLUE, max_chars=14 if portrait else 40, opacity=request*clamp(1-4*disclosure)))
    if disclosure > 0:
        parts.append(path(partial_curve(reply_points, disclosure), AMBER, 4))
        dx, dy = cubic(reply_points, disclosure)
        parts.append(document(dx, dy))
        parts.append(wrapped_text(525 if portrait else 496, 885 if portrait else 464, "מנהרות חוצות־גבול", 24 if portrait else 21, AMBER, max_chars=13 if portrait else 40, opacity=clamp(4*disclosure-1)))
    else:
        parts.append(document(*reply_points[0], clamp(state["knowledge"])))
    parts.append('</g>')

    for index, name in enumerate(("netanyahu", "gantz", "bennett", "winter")):
        reveal = clamp(hierarchy * 4 - index)
        parts.append(actor(name, positions[name], reveal, modern, assets, labels))
    parts.append(f'<g id="known-information" opacity="{history*clamp(state["knowledge"]):g}" fill="{AMBER}">')
    for name in ("netanyahu", "gantz"):
        x, y = historical[name]
        parts.append(f'<circle cx="{x+52}" cy="{y-49}" r="9" stroke="white" stroke-width="3"/>')
    parts.append('</g>')
    parts.append(text(620 if portrait else 878, 568 if portrait else 408, "?", 39, BLUE, weight="700", opacity=history*state["question"]))
    parts.append(text(620 if portrait else 875, 568 if portrait else 412, "!", 43, AMBER, weight="700", opacity=history*state["surprise"]))

    parts.append('</g></svg>')
    return "".join(parts)
