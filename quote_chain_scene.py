"""A chain of quotes: a speaker says something, and the next speaker appears beneath.

The camera scrolls down a vertical strip of portraits and quotes. Each quote's
duration is the length of its audio clip, so the text reveal lines up with the
recordings placed under the animation in the video editor.
"""

import math
import textwrap

from animation_timeline import ease
from tunnels_scene import INK, MUTED, BLUE, clamp, text

# One speaker per STEP of strip; the next speaker waits below the quote. The
# quotes are the captions here, so the whole frame is used.
STEP = 700
FACE_Y, FACE_R = 220, 120
QUOTE_SIZE, QUOTE_CHARS, QUOTE_LINES = 52, 22, 3
# Right-to-left marks keep leading and trailing punctuation ("...", "?!") on
# the correct side of each Hebrew line.
RLM = "\u200f"
POP = .5
TIMING = {"intro": .6, "pause": .3, "next_lead": .8, "hold": .5, "scroll": .9, "outro": 2}


def build_timeline(data):
    """Validate a quote chain and derive its schedule, duration, and chapters."""
    timing = TIMING | data.get("timing", {})
    if not all(isinstance(v, (int, float)) and math.isfinite(v) and v >= 0 for v in timing.values()):
        raise ValueError("Timing values must be finite and non-negative")
    speakers, quotes = data["speakers"], data["quotes"]
    if not quotes:
        raise ValueError("A quote chain needs at least one quote")
    closing = data.get("closing_speaker")
    for name in [q["speaker"] for q in quotes] + ([closing] if closing else []):
        if name not in speakers:
            raise ValueError(f"Unknown speaker: {name}")
    schedule, chapters, cursor = [], [], timing["intro"]
    for index, quote in enumerate(quotes):
        duration = quote["duration"]
        if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
            raise ValueError(f"Quote {index + 1}: duration must be positive")
        start = cursor + timing["pause"]
        end = start + duration
        scroll = end + timing["hold"]
        schedule.append(dict(start=start, end=end, next_in=max(start, end - timing["next_lead"]),
                             scroll=scroll, scroll_end=scroll + timing["scroll"]))
        chapters.append(dict(time=start, label=f"{speakers[quote['speaker']]['name']} על {quote['about']}"))
        cursor = scroll + timing["scroll"]
    duration = schedule[-1]["end"] + timing["outro"]
    chapters.insert(0, dict(time=0, label=speakers[quotes[0]["speaker"]]["name"]))
    return dict(data, timing=timing, schedule=schedule, chapters=chapters, duration=duration,
                tracks={}, events=[])


def chain_state(timeline, time):
    keys = ("speakers", "quotes", "closing_speaker", "schedule", "timing")
    return {key: timeline.get(key) for key in keys} | {
        "scene": "quote_chain", "time": time,
        "quote_text_scale": timeline.get("quote_text_scale", 1),
    }


def cue_sheet(timeline):
    """When each quote's audio should start, for placing the clips in the editor."""
    return [dict(start=round(s["start"], 2), speaker=timeline["speakers"][q["speaker"]]["name"],
                 about=q["about"], quote=q["text"], duration=q["duration"])
            for q, s in zip(timeline["quotes"], timeline["schedule"])]


def face(name, speaker, y, appear, speaking, time, assets):
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
    return (f'<g id="face-{name}" transform="translate(360 {y:g}) scale({.7 + .3*appear:g})" opacity="{appear:g}">'
            f'<circle r="{FACE_R + 4 + 8*speaking:g}" fill="none" stroke="{BLUE}" stroke-width="5" opacity="{.5*speaking:g}"/>'
            f'<circle r="{FACE_R + 3}" fill="white" stroke="#e4e6e9" stroke-width="2"/>'
            + portrait
            + f'<g transform="translate({FACE_R + 70} 0)" opacity="{speaking:g}">{bars}</g>'
            + text(0, FACE_R + 54, speaker["name"], 42, INK, "700")
            + (text(0, FACE_R + 90, role, 27, MUTED) if role else "")
            + '</g>')


def quote_block(index, quote, y, reveal, tag, scale):
    """The 'about' tag, then the quote revealed right to left at speaking pace."""
    # Long quotes shrink to fit QUOTE_LINES, so the next face still has room.
    while True:
        size = QUOTE_SIZE * scale
        lines = textwrap.wrap(quote["text"], round(QUOTE_CHARS * QUOTE_SIZE / size),
                              break_long_words=False, break_on_hyphens=False)
        if len(lines) <= QUOTE_LINES or scale < .6:
            break
        scale *= .9
    parts = [text(360, y, f'על {quote["about"]}', 30, BLUE, "700", opacity=f"{tag:g}")]
    total = sum(map(len, lines))
    done = 0
    for line_index, line in enumerate(lines):
        baseline = y + 72 + line_index * size * 1.3
        progress = clamp((reveal * total - done) / len(line))
        done += len(line)
        if progress <= 0:
            continue
        if progress < 1:
            # Hebrew reads right to left; uncover each line from its right edge.
            width = min(680, len(line) * size * .5 + 20)
            clip_id = f"reveal-{index}-{line_index}"
            parts.append(f'<clipPath id="{clip_id}"><rect x="{360 + width/2 - width*progress:g}" '
                         f'y="{baseline - size*1.1:g}" width="{width*progress:g}" height="{size*1.5:g}"/></clipPath>')
            parts.append(text(360, baseline, RLM + line + RLM, size, INK, "700", clip_path=f"url(#{clip_id})"))
        else:
            parts.append(text(360, baseline, RLM + line + RLM, size, INK, "700"))
    source_y = y + 72 + (len(lines) - 1) * size * 1.3 + 54
    parts.append(text(360, source_y, quote["source"], 25, MUTED, opacity=f"{tag:g}"))
    return f'<g id="quote-{index}">{"".join(parts)}</g>'


def render_quote_chain(state, *, assets, width=1080, height=1920, transparent=False):
    time, timing, schedule = state["time"], state["timing"], state["schedule"]
    speakers, quotes = state["speakers"], state["quotes"]
    camera = STEP * sum(ease((time - s["scroll"]) / timing["scroll"]) if timing["scroll"] else time >= s["scroll"]
                        for s in schedule[:-1])
    faces = [q["speaker"] for q in quotes] + ([state["closing_speaker"]] if state.get("closing_speaker") else [])
    parts = []
    for index, name in enumerate(faces):
        y = index * STEP + FACE_Y
        appear_at = 0 if index == 0 else schedule[index - 1]["next_in"]
        pop = timing["intro"] if index == 0 else POP
        appear = ease((time - appear_at) / pop) if pop else 1
        speaking = 0
        if index < len(quotes):
            s = schedule[index]
            speaking = min(ease((time - s["start"] + .2) / .2), ease((s["end"] + .2 - time) / .2))
        parts.append(face(name, speakers[name], y, appear, speaking, time, assets))
    for index, (quote, s) in enumerate(zip(quotes, schedule)):
        tag = ease((time - s["start"] + timing["pause"]) / .3)
        if tag > 0:
            reveal = clamp((time - s["start"]) / quote["duration"])
            y = index * STEP + FACE_Y + FACE_R + (140 if speakers[quote["speaker"]].get("role") else 110)
            parts.append(quote_block(index, quote, y, reveal, tag, state.get("quote_text_scale", 1)))
    background = "" if transparent else '<rect width="720" height="1280" fill="white"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 720 1280" '
            f'role="img" aria-label="Who said what about whom">{background}'
            f'<defs><clipPath id="face-clip"><circle r="{FACE_R}"/></clipPath></defs>'
            f'<g font-family="Arial, sans-serif" transform="translate(0 {-camera:g})">{"".join(parts)}</g></svg>')
