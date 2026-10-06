"""Deterministic, seekable animation state. Times in timeline.json are seconds."""
import json
import math
from pathlib import Path

DEFAULT_TIMELINE = Path(__file__).with_name("timeline.json")
METER_SCENE_LABELS = {"Meter introduction": "intro", "Blocked partnership": "blocked", "Escalation": "escalation", "Full sequence": "full"}
SCENE_LABELS = METER_SCENE_LABELS | {"Tunnels · 2014 → 2026": "tunnels", "Phone · notification dismissed": "phone"}
SCENE_FILES = {"intro": "timeline_intro.json", "blocked": "timeline_blocked.json", "escalation": "timeline.json", "tunnels": "timeline_tunnels.json", "phone": "timeline_phone.json"}
PHONE_TRACKS = {"notification_in", "dismiss", "touch"}
TUNNEL_TRACKS = {"hierarchy", "knowledge", "withheld", "question", "request", "disclosure", "surprise", "cabinet_update", "modern", "alignment"}
REVEAL_TRACKS = {"left_reveal", "right_reveal", "arc_reveal", "needle_reveal", "logos_reveal", "zones_reveal"}
BLOCKED_TRACKS = {"potential_position", "potential_opacity", "netanyahu", "abbas", "smotrich", "partnership", "block"}
TRACKS = {"israeli_position", "palestinian_position", "israeli_y", "palestinian_y",
          "portrait", "translation", "outcome"}


def ease(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def sample(keys, time):
    if time <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if time <= t1:
            return v0 + (v1 - v0) * ease((time - t0) / (t1 - t0))
    return keys[-1][1]


def load_timeline(path=DEFAULT_TIMELINE):
    data = json.loads(Path(path).read_text())
    for name in ("duration", "fps", "width", "height"):
        value = data[name]
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a finite positive number")
    for name in ("width", "height"):
        if not isinstance(data[name], int) or data[name] % 2:
            raise ValueError(f"{name} must be an even integer")
    scene = data.get("scene", "escalation")
    if scene not in SCENE_FILES:
        raise ValueError(f"Unknown scene: {scene}")
    required = PHONE_TRACKS if scene == "phone" else TUNNEL_TRACKS if scene == "tunnels" else TRACKS | (BLOCKED_TRACKS if scene == "blocked" else REVEAL_TRACKS if scene == "intro" else set())
    optional = set() if scene in {"tunnels", "phone"} else REVEAL_TRACKS
    if not required <= set(data["tracks"]) or set(data["tracks"]) - required - optional:
        raise ValueError(f"Timeline must define these tracks: {sorted(required)}")
    for name, keys in data["tracks"].items():
        if not keys or keys[0][0] != 0:
            raise ValueError(f"{name}: first keyframe must be at time 0")
        previous = -1
        for time, value in keys:
            if not all(math.isfinite(v) for v in (time, value)) or not previous < time <= data["duration"]:
                raise ValueError(f"{name}: keyframe times must increase and fit within duration")
            if name not in {"israeli_y", "palestinian_y"} and not 0 <= value <= 1:
                raise ValueError(f"{name}: values must be between 0 and 1")
            previous = time
    for event in data["events"]:
        if event["kind"] not in {"cash", "knife", "push"}:
            raise ValueError(f"Unknown event kind: {event['kind']}")
        if not (math.isfinite(event["start"]) and math.isfinite(event["duration"]) and
                event["start"] >= 0 and event["duration"] > 0 and
                event["start"] + event["duration"] <= data["duration"]):
            raise ValueError("Events must have positive durations and fit within the timeline")
    for chapter in data["chapters"]:
        if not (math.isfinite(chapter["time"]) and 0 <= chapter["time"] <= data["duration"]
                and isinstance(chapter["label"], str)):
            raise ValueError("Chapters need a label and a time within the timeline")
    for clip in data.get("clips", {}).values():
        start, end = clip["start"], clip["end"]
        if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end <= data["duration"]):
            raise ValueError("Clips must fit within the timeline")
    return data


def state_at(timeline, time):
    if not math.isfinite(time):
        raise ValueError("Animation time must be finite")
    time = max(0, min(timeline["duration"], time))
    if "segments" in timeline:
        for index, segment in enumerate(timeline["segments"]):
            end = segment["start"] + segment["duration"]
            if time < end or index == len(timeline["segments"]) - 1:
                local = time - segment["start"]
                if segment.get("scene") == "transition":
                    return {"scene": "transition", "title": segment["title"],
                            "scene_opacity": min(ease(local / .4), ease((segment["duration"] - local) / .4))}
                state = state_at(segment["timeline"], local)
                # Fade only at joins, preserving each standalone scene's timing.
                state["scene_opacity"] = min(
                    ease(local / .4) if index and timeline["segments"][index-1].get("scene") == "transition" else 1,
                    ease((segment["duration"] - local) / .4) if index + 1 < len(timeline["segments"]) and timeline["segments"][index+1].get("scene") == "transition" else 1,
                )
                return state
    state = {name: sample(keys, time) for name, keys in timeline["tracks"].items()}
    state["scene"] = timeline.get("scene", "escalation")
    if state["scene"] in {"tunnels", "phone"}:
        state["labels"] = timeline.get("labels", {})
    if state["scene"] == "phone":
        state["notification_scale"] = timeline.get("notification_scale", 1)
    state["events"] = [dict(event, progress=(time - event["start"]) / event["duration"])
                       for event in timeline["events"]
                       if event["start"] <= time < event["start"] + event["duration"]]
    return state


def load_scene(scene="escalation", timeline_path=None):
    """Load a standalone scene or resolve the ordered sequence into a portable snapshot."""
    if timeline_path is not None:
        return load_timeline(timeline_path)
    if scene in SCENE_FILES:
        return load_timeline(Path(__file__).with_name(SCENE_FILES[scene]))
    if scene != "full":
        raise ValueError(f"Unknown scene: {scene}")
    manifest = json.loads(Path(__file__).with_name("sequence.json").read_text())
    segments, chapters, offset = [], [], 0
    for entry_index, entry in enumerate(manifest["scenes"]):
        continuous = entry_index > 0 and [manifest["scenes"][entry_index-1], entry] in manifest.get("continuous_joins", [])
        if segments and not continuous:
            duration = manifest["transition"]["duration"]
            if not math.isfinite(duration) or duration <= 0:
                raise ValueError("Transition duration must be positive and finite")
            segments.append(dict(scene="transition", start=offset, duration=duration,
                                 title=manifest["transition"]["title"]))
            chapters.append(dict(time=offset, label="The other side"))
            offset += duration
        if entry not in SCENE_FILES:
            raise ValueError(f"Unknown sequence scene: {entry}")
        timeline = load_scene(entry)
        label = next(label for label, value in SCENE_LABELS.items() if value == entry)
        segments.append(dict(start=offset, duration=timeline["duration"], timeline=timeline))
        chapters.extend(dict(time=offset+c["time"], label=f"{label} · {c['label']}") for c in timeline["chapters"])
        offset += timeline["duration"]
    if not segments:
        raise ValueError("Sequence must contain at least one scene")
    first = segments[0]["timeline"]
    return dict(duration=offset, fps=first["fps"], width=first["width"], height=first["height"],
                chapters=chapters, segments=segments, scene="full")
