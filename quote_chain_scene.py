"""A chain of quotes: each speaker appears above the one they talk about.

The camera scrolls up a vertical strip of portraits, so each quote sits between
its speaker and its target. When a quote's target isn't the previous speaker,
the chain breaks: the camera pans left instead, to a new strip that starts with
that target below its speaker. A speaker or target shared across the break
stays in place during the pan. Each quote's
duration is the length of its audio clip, so the text reveal lines up with the
recordings placed under the animation in the video editor.
"""

import html
import math
import textwrap

from animation_timeline import ease
from tunnels_scene import INK, MUTED, BLUE, clamp, text

# One speaker per STEP of strip, each above the previous one, with the quote in
# between. The quotes are the captions here, so the whole frame is used. A
# chain break starts a new strip one frame width to the left.
STEP, PAN = 700, 720
FACE_Y, FACE_R = 220, 120
QUOTE_SIZE, QUOTE_CHARS, QUOTE_LINES = 52, 22, 3
# Right-to-left marks keep leading and trailing punctuation ("...", "?!") on
# the correct side of each Hebrew line.
RLM = "\u200f"
TIMING = {"intro": .6, "pause": .3, "hold": .5, "scroll": .9, "outro": 2}
# The background is a soft gradient through each face's party colour, mixed
# with white this much, laid out with the faces so it moves with the camera.
# Each strip's background fades into the previous one over BLEND, just
# outside the frame once the pan is done.
TINT, BLEND = .25, 240
# By default the colour bands rise this many degrees toward the left, the way
# the chain moves; the timeline's background_tilt overrides it.
TILT = 15


def build_timeline(data):
    """Validate a quote chain and derive its schedule, duration, and chapters."""
    timing = TIMING | data.get("timing", {})
    if not all(isinstance(v, (int, float)) and math.isfinite(v) and v >= 0 for v in timing.values()):
        raise ValueError("Timing values must be finite and non-negative")
    speakers, quotes = data["speakers"], data["quotes"]
    if not quotes:
        raise ValueError("A quote chain needs at least one quote")
    closing = data.get("closing_speaker")
    for name in [q[key] for q in quotes for key in ("speaker", "about")] + ([closing] if closing else []):
        if name not in speakers:
            raise ValueError(f"Unknown speaker: {name}")
    parties = data.get("parties", {})
    for name, speaker in speakers.items():
        if speaker.get("party") and speaker["party"] not in parties:
            raise ValueError(f"{name}: unknown party {speaker['party']}")
    schedule, chapters, cursor = [], [], timing["intro"]
    for index, quote in enumerate(quotes):
        duration = quote["duration"]
        if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
            raise ValueError(f"Quote {index + 1}: duration must be positive")
        start = cursor + timing["pause"]
        end = start + duration
        scroll = end + timing["hold"]
        schedule.append(dict(start=start, end=end, scroll=scroll, scroll_end=scroll + timing["scroll"]))
        chapters.append(dict(time=start, label=f"{speakers[quote['speaker']]['name']} על {speakers[quote['about']]['name']}"))
        cursor = scroll + timing["scroll"]
    # The closing speaker needs one more scroll; without one, the chain ends on the last quote.
    if closing:
        chapters.append(dict(time=schedule[-1]["scroll"], label=f"{speakers[closing]['name']} · closing"))
        duration = schedule[-1]["scroll_end"] + timing["outro"]
    else:
        duration = schedule[-1]["end"] + timing["outro"]
    chapters.insert(0, dict(time=0, label=speakers[quotes[0]["speaker"]]["name"]))
    return dict(data, timing=timing, schedule=schedule, chapters=chapters, duration=duration,
                tracks={}, events=[])


def chain_state(timeline, time):
    keys = ("speakers", "parties", "quotes", "closing_speaker", "schedule", "timing")
    return {key: timeline.get(key) for key in keys} | {
        "scene": "quote_chain", "time": time,
        "quote_text_scale": timeline.get("quote_text_scale", 1),
        "background_tilt": timeline.get("background_tilt", TILT),
    }


def cue_sheet(timeline):
    """When each quote's audio should start, for placing the clips in the editor."""
    return [dict(start=round(s["start"], 2), speaker=timeline["speakers"][q["speaker"]]["name"],
                 about=timeline["speakers"][q["about"]]["name"], quote=q["text"], duration=q["duration"])
            for q, s in zip(timeline["quotes"], timeline["schedule"])]


def face(name, speaker, y, appear, speaking, time, assets, x=360):
    """Portrait, name and role; a pulsing ring and sound bars while speaking."""
    if appear <= 0:
        return ""
    portrait = (
        f'<image href="{assets[name]}" x="{-FACE_R}" y="{-FACE_R}" width="{2*FACE_R}" height="{2*FACE_R}" '
        f'preserveAspectRatio="xMidYMid slice" clip-path="url(#face-clip)"/>'
        if name in assets else
        f'<circle r="{FACE_R}" fill="#f5ecdc"/><circle cy="-20" r="28" fill="#c0b8ac"/>'
        '<path d="M-52 66 Q-52 14 0 14 Q52 14 52 66" fill="#c0b8ac"/>'
    )
    bars = "".join(
        f'<rect x="{i*15 - 34}" y="{-h/2:g}" width="8" height="{h:g}" rx="4" fill="{BLUE}"/>'
        for i, h in ((i, 8 + 34 * speaking * abs(math.sin(time * 9 + i * 1.7))) for i in range(5)))
    role = speaker.get("role")
    return (f'<g id="face-{name}" transform="translate({x:g} {y:g}) scale({.7 + .3*appear:g})" opacity="{appear:g}">'
            f'<circle r="{FACE_R + 4 + 8*speaking:g}" fill="none" stroke="{BLUE}" stroke-width="5" opacity="{.5*speaking:g}"/>'
            f'<circle r="{FACE_R + 3}" fill="white" stroke="#e4e6e9" stroke-width="2"/>'
            + portrait
            + f'<g transform="translate({FACE_R + 70} 0)" opacity="{speaking:g}">{bars}</g>'
            + text(0, FACE_R + 54, speaker["name"], 42, INK, "700")
            + (text(0, FACE_R + 90, role, 27, MUTED) if role else "")
            + '</g>')


def quote_block(block_id, quote, x, y, reveal, tag, scale, opacity=1):
    """The quote, revealed right to left at speaking pace, and its source."""
    # Long quotes shrink to fit QUOTE_LINES, so the next face still has room.
    while True:
        size = QUOTE_SIZE * scale
        lines = textwrap.wrap(quote["text"], round(QUOTE_CHARS * QUOTE_SIZE / size),
                              break_long_words=False, break_on_hyphens=False)
        if len(lines) <= QUOTE_LINES or scale < .6:
            break
        scale *= .9
    parts = []
    total = sum(map(len, lines))
    done = 0
    for line_index, line in enumerate(lines):
        baseline = y + 32 + line_index * size * 1.3
        progress = clamp((reveal * total - done) / len(line))
        done += len(line)
        if progress <= 0:
            continue
        if progress < 1:
            # The unspoken rest is laid out but transparent, so the line keeps its
            # final, centered position. A clip path would need an id reference,
            # which browsers briefly fail to resolve while the notebook patches it.
            shown = round(len(line) * progress)
            parts.append(
                f'<text x="{x:g}" y="{baseline:g}" text-anchor="middle" direction="rtl" font-size="{size:g}" '
                f'font-weight="700" fill="{INK}"><tspan>{html.escape(RLM + line[:shown])}</tspan>'
                f'<tspan fill-opacity="0">{html.escape(line[shown:] + RLM)}</tspan></text>')
        else:
            parts.append(text(x, baseline, RLM + line + RLM, size, INK, "700"))
    source_y = y + 32 + (len(lines) - 1) * size * 1.3 + 54
    parts.append(text(x, source_y, quote["source"], 25, MUTED, opacity=f"{tag:g}"))
    return f'<g id="quote-{block_id}" opacity="{opacity:g}">{"".join(parts)}</g>'


def rgb(color):
    return [int(color[i:i + 2], 16) for i in (1, 3, 5)]


def mix(a, b, amount):
    return [x + (y - x) * amount for x, y in zip(a, b)]


def hex_color(channels):
    return "#" + "".join(f"{round(c):02x}" for c in channels)


def party_color(state, name):
    """A speaker's party colour, or white for speakers without a party."""
    party = state["speakers"][name].get("party")
    return rgb(state.get("parties", {}).get(party, {}).get("color", "#ffffff") if party else "#ffffff")


def strip_backgrounds(state, layout, shown, camera_x):
    """One background per strip, a vertical gradient through its faces' party colours.

    The gradients depend only on the layout, never on time, so the notebook
    preview never patches the definitions the frame references. Only the shown
    strips are drawn: a strip's edge fades over the previous strip, which would
    otherwise show while the camera is still there.

    A pan to a new strip slides the backgrounds along the tilt of their bands
    rather than straight sideways, so the bands hold still on screen while the
    new strip's edge sweeps in; once the pan is done they line up with the faces."""
    white = [255] * 3
    tilt = math.radians(state.get("background_tilt", TILT))
    parts = []
    for column in range(max(c for c, _, _ in layout) + 1):
        stops = sorted((FACE_Y - row * STEP, name) for c, row, name in layout if c == column)
        top, bottom = stops[0][0], stops[-1][0]
        left = 360 - column * PAN - PAN / 2
        gradient = "".join(
            f'<stop offset="{(y - top) / ((bottom - top) or 1):g}" '
            f'stop-color="{hex_color(mix(white, party_color(state, name), TINT))}"/>' for y, name in stops)
        # Tilted down and to the left, and shortened to match, the gradient still
        # puts each face's colour exactly at its face, in the middle of the strip.
        center, length = left + PAN / 2, (bottom - top) * math.cos(tilt)
        parts.append(f'<linearGradient id="strip-{column}" gradientUnits="userSpaceOnUse" '
                     f'x1="{center:g}" y1="{top}" x2="{center - length * math.sin(tilt):g}" '
                     f'y2="{top + length * math.cos(tilt):g}">{gradient}</linearGradient>')
        # Strips go leftward, so each one fades out to the right, over the previous strip.
        mask = ""
        if column:
            parts.append(f'<linearGradient id="strip-{column}-edge" gradientUnits="userSpaceOnUse" '
                         f'x1="{left + PAN:g}" y1="0" x2="{left + PAN + BLEND:g}" y2="0">'
                         '<stop offset="0" stop-color="white"/><stop offset="1" stop-color="black"/></linearGradient>'
                         f'<mask id="strip-{column}-mask"><rect x="{left:g}" y="{top - 1280}" '
                         f'width="{PAN + BLEND}" height="{bottom - top + 2560}" fill="url(#strip-{column}-edge)"/></mask>')
            mask = f' mask="url(#strip-{column}-mask)"'
        if column in shown:
            slide = math.tan(tilt) * (camera_x - column * PAN)
            parts.append(f'<rect transform="translate(0 {slide:g})" x="{left:g}" y="{top - 1280}" width="{PAN + (BLEND if column else 0)}" '
                         f'height="{bottom - top + 2560}" fill="url(#strip-{column})"{mask}/>')
    definitions = "".join(part for part in parts if not part.startswith("<rect"))
    return f'<defs>{definitions}</defs>' + "".join(part for part in parts if part.startswith("<rect"))


def render_quote_chain(state, *, assets, width=1080, height=1920, transparent=False):
    time, timing, schedule = state["time"], state["timing"], state["schedule"]
    speakers, quotes = state["speakers"], state["quotes"]
    closing = state.get("closing_speaker")
    faces = [q["speaker"] for q in quotes] + ([closing] if closing else [])
    reprise = closing and closing == quotes[0]["speaker"]
    # Who each face's quote is about; the reprise repeats the first quote's target,
    # and any other closing speaker just goes above the last one.
    targets = [q["about"] for q in quotes] + ([quotes[0]["about"] if reprise else quotes[-1]["speaker"]]
                                              if closing else [])

    def scrolled(s):
        return ease((time - s["scroll"]) / timing["scroll"]) if timing["scroll"] else float(time >= s["scroll"])

    def ramp(start, duration):
        return ease((time - start) / duration) if duration else float(time >= start)

    # Each face's strip (counted leftward) and row (counted upward). A face whose
    # quote is about the previous speaker goes above them; otherwise it starts a
    # new strip, level with the previous speaker, above its own target.
    breaks = [k > 0 and targets[k] != faces[k - 1] for k in range(len(faces))]
    columns, rows = [0], [0]
    for k in range(1, len(faces)):
        columns.append(columns[-1] + breaks[k])
        rows.append(rows[-1] + (not breaks[k]))

    # Every face's place, for the backgrounds, which follow the faces.
    layout = [(0, -1, targets[0])] + [(columns[k], rows[k], name) for k, name in enumerate(faces)] + [
        (columns[k], rows[k] - 1, targets[k]) for k in range(1, len(faces)) if breaks[k]]

    def position(column, row):
        return 360 - column * PAN, FACE_Y - row * STEP

    moves = [scrolled(s) for s in schedule[:len(faces) - 1]]
    camera_x = PAN * sum(m for m, b in zip(moves, breaks[1:]) if b)
    camera_y = STEP * sum(m for m, b in zip(moves, breaks[1:]) if not b)
    faces_drawn = []

    def add_face(name, column, row, appear, speaking=0):
        x, y = position(column, row)
        faces_drawn.append(dict(name=name, x=x, y=y, appear=appear, speaking=speaking))
        return faces_drawn[-1]

    # The chain opens with the first quote's target below its speaker.
    intro = ramp(0, timing["intro"])
    below = [add_face(targets[0], 0, -1, intro)]
    above = []
    for index, name in enumerate(faces):
        if index and breaks[index]:
            # The new strip's target is already there once the pan starts, sliding in with it.
            below.append(add_face(targets[index], columns[index], rows[index] - 1, float(moves[index - 1] > 0)))
        elif index:
            below.append(above[-1])
        speaking = 0
        if index < len(quotes):
            s = schedule[index]
            speaking = min(ease((time - s["start"] + .2) / .2), ease((s["end"] + .2 - time) / .2))
        # Each new speaker fades in as the camera moves to them.
        above.append(add_face(name, columns[index], rows[index], intro if index == 0 else moves[index - 1], speaking))
    # Whoever a chain break shares with the previous quote, its speaker or its
    # target, holds still on screen while the rest pans, then hands over to
    # their copy in the new strip, so a series by or about one person reads as such.
    for index in range(1, len(faces)):
        if breaks[index]:
            move = moves[index - 1]
            for side in (above, below):
                old, new = side[index - 1], side[index]
                if old["name"] == new["name"]:
                    old["x"] -= PAN * move
                    old["appear"] *= move < 1
                    new["appear"] = float(move >= 1)
    parts = [face(f["name"], speakers[f["name"]], f["y"], f["appear"], f["speaking"], time, assets, f["x"])
             for f in faces_drawn]
    def quote_at(index, speaker):
        """Below the face at this index, by how much room its name and role take."""
        x, y = position(columns[index], rows[index])
        return x, y + FACE_R + (140 if speakers[speaker].get("role") else 110)

    scale = state.get("quote_text_scale", 1)
    for index, (quote, s) in enumerate(zip(quotes, schedule)):
        # A spoken quote fades as the camera moves on.
        tag = ease((time - s["start"] + timing["pause"]) / .3)
        fade = 1 - scrolled(s) if index < len(faces) - 1 else 1
        if tag > 0 and fade > 0:
            reveal = clamp((time - s["start"]) / quote["duration"])
            parts.append(quote_block(index, quote, *quote_at(index, quote["speaker"]), reveal, tag, scale, fade))
    # Back where it began: the first quote returns above the face it was about.
    if reprise and (appear := scrolled(schedule[-1])) > 0:
        parts.append(quote_block("reprise", quotes[0], *quote_at(len(quotes), closing), 1, appear, scale))
    # A strip's background shows from when the camera starts panning to it.
    shown = {0} | {columns[k] for k in range(1, len(faces)) if breaks[k] and moves[k - 1] > 0}
    background = "" if transparent else strip_backgrounds(state, layout, shown, camera_x)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 720 1280" '
            f'role="img" aria-label="Who said what about whom">'
            f'<defs><clipPath id="face-clip"><circle r="{FACE_R}"/></clipPath></defs>'
            f'<g font-family="Arial, sans-serif" transform="translate({camera_x:g} {camera_y:g})">'
            f'{background}{"".join(parts)}</g></svg>')
